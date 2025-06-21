"""Defines the production hosting infrastructure for the Sophia Dashboard.

This includes an S3 bucket for static website hosting and a CloudFront
distribution for global delivery and HTTPS.
"""

import pulumi
import pulumi_aws as aws

# The S3 bucket where our GitHub Action uploads the built artifacts.
build_artifacts_bucket_name = "sophia-dashboard-build-artifacts"

# --- 1. S3 Bucket for Hosting ---
# This bucket will be configured to serve a static website.
hosting_bucket = aws.s3.Bucket(
    "sophia-dashboard-hosting-bucket",
    website=aws.s3.BucketWebsiteArgs(
        index_document="index.html",
    ),
)

# --- 2. Public Access Block ---
# We need to allow public read access for the website to be visible.
public_access_block = aws.s3.BucketPublicAccessBlock(
    "hosting-public-access-block",
    bucket=hosting_bucket.id,
    block_public_acls=False,
    block_public_policy=False,
    ignore_public_acls=False,
    restrict_public_buckets=False,
)

# --- 3. Bucket Policy ---
# This policy grants public read access to the objects in the bucket.
bucket_policy = aws.s3.BucketPolicy(
    "hosting-bucket-policy",
    bucket=hosting_bucket.id,
    policy=hosting_bucket.id.apply(
        lambda id: f"""{{
        "Version": "2012-10-17",
        "Statement": [{{
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::{id}/*"
        }}]
    }}"""
    ),
    opts=pulumi.ResourceOptions(depends_on=[public_access_block]),
)

# --- 4. CloudFront Distribution ---
# This provides a CDN, HTTPS, and a nice URL for our dashboard.
cdn = aws.cloudfront.Distribution(
    "sophia-dashboard-cdn",
    origins=[
        aws.cloudfront.DistributionOriginArgs(
            domain_name=hosting_bucket.website_endpoint,
            origin_id="S3-sophia-dashboard",
            custom_origin_config=aws.cloudfront.DistributionOriginCustomOriginConfigArgs(
                http_port=80,
                https_port=443,
                origin_protocol_policy="http-only",
                origin_ssl_protocols=["TLSv1.2"],
            ),
        )
    ],
    enabled=True,
    is_ipv6_enabled=True,
    default_root_object="index.html",
    default_cache_behavior=aws.cloudfront.DistributionDefaultCacheBehaviorArgs(
        allowed_methods=["GET", "HEAD"],
        cached_methods=["GET", "HEAD"],
        target_origin_id="S3-sophia-dashboard",
        forwarded_values=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
            query_string=False,
            cookies=aws.cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                forward="none"
            ),
        ),
        viewer_protocol_policy="redirect-to-https",
        min_ttl=0,
        default_ttl=3600,
        max_ttl=86400,
    ),
    restrictions=aws.cloudfront.DistributionRestrictionsArgs(
        geo_restriction=aws.cloudfront.DistributionRestrictionsGeoRestrictionArgs(
            restriction_type="none",
        ),
    ),
    viewer_certificate=aws.cloudfront.DistributionViewerCertificateArgs(
        cloudfront_default_certificate=True,
    ),
)

# --- 5. Pulumi Stack Output ---
# This will be the public URL for our dashboard.
pulumi.export("dashboard_url", cdn.domain_name)
# This command tells the deployment agent how to sync files.
pulumi.export(
    "deployment_sync_command",
    pulumi.Output.concat(
        "aws s3 sync s3://",
        build_artifacts_bucket_name,
        "/ ",
        hosting_bucket.id.apply(lambda id: f"s3://{id}/"),
    ),
)
