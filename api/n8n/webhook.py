"""
Sophia AI n8n Webhook Handler
Optimized for Vercel serverless deployment with focus on performance and reliability.
Handles webhooks from n8n workflows for Salesforce to HubSpot/Intercom migration.
"""

import logging
import os
from datetime import datetime
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Environment configuration
SOPHIA_ENV = os.getenv("SOPHIA_ENV", "production")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class N8NWebhookProcessor:
    """Lightweight processor for n8n webhook data transformations."""

    def __init__(self):
        self.supported_workflows = {
            "salesforce_to_hubspot": self.process_salesforce_to_hubspot,
            "salesforce_to_intercom": self.process_salesforce_to_intercom,
            "data_sync": self.process_data_sync,
            "lead_enrichment": self.process_lead_enrichment,
        }

    def process_salesforce_to_hubspot(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform Salesforce data for HubSpot integration."""
        try:
            # Extract Salesforce fields
            sf_data = data.get("salesforce_data", {})

            # Transform to HubSpot format
            hubspot_data = {
                "properties": {
                    "company": sf_data.get("AccountName", ""),
                    "industry": sf_data.get("Industry", ""),
                    "website": sf_data.get("Website", ""),
                    "phone": sf_data.get("Phone", ""),
                    "city": sf_data.get("BillingCity", ""),
                    "state": sf_data.get("BillingState", ""),
                    "country": sf_data.get("BillingCountry", ""),
                    "annual_revenue": sf_data.get("AnnualRevenue", 0),
                    "number_of_employees": sf_data.get("NumberOfEmployees", 0),
                    "description": sf_data.get("Description", ""),
                    "salesforce_id": sf_data.get("Id", ""),
                    "last_modified_date": sf_data.get("LastModifiedDate", ""),
                    "created_date": sf_data.get("CreatedDate", ""),
                }
            }

            # Add contact information if available
            if "contacts" in sf_data:
                hubspot_data["contacts"] = []
                for contact in sf_data["contacts"]:
                    hubspot_contact = {
                        "properties": {
                            "firstname": contact.get("FirstName", ""),
                            "lastname": contact.get("LastName", ""),
                            "email": contact.get("Email", ""),
                            "phone": contact.get("Phone", ""),
                            "jobtitle": contact.get("Title", ""),
                            "salesforce_contact_id": contact.get("Id", ""),
                        }
                    }
                    hubspot_data["contacts"].append(hubspot_contact)

            return {
                "status": "success",
                "transformed_data": hubspot_data,
                "transformation_type": "salesforce_to_hubspot",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error transforming Salesforce to HubSpot data: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "transformation_type": "salesforce_to_hubspot",
                "timestamp": datetime.utcnow().isoformat(),
            }

    def process_salesforce_to_intercom(self, data: dict[str, Any]) -> dict[str, Any]:
        """Transform Salesforce data for Intercom integration."""
        try:
            sf_data = data.get("salesforce_data", {})

            # Transform to Intercom format
            intercom_data = {
                "company": {
                    "name": sf_data.get("AccountName", ""),
                    "website": sf_data.get("Website", ""),
                    "industry": sf_data.get("Industry", ""),
                    "size": sf_data.get("NumberOfEmployees", 0),
                    "custom_attributes": {
                        "salesforce_id": sf_data.get("Id", ""),
                        "annual_revenue": sf_data.get("AnnualRevenue", 0),
                        "billing_city": sf_data.get("BillingCity", ""),
                        "billing_state": sf_data.get("BillingState", ""),
                        "billing_country": sf_data.get("BillingCountry", ""),
                        "description": sf_data.get("Description", ""),
                        "last_modified_date": sf_data.get("LastModifiedDate", ""),
                        "created_date": sf_data.get("CreatedDate", ""),
                    },
                }
            }

            # Add contacts if available
            if "contacts" in sf_data:
                intercom_data["contacts"] = []
                for contact in sf_data["contacts"]:
                    intercom_contact = {
                        "email": contact.get("Email", ""),
                        "name": f"{contact.get('FirstName', '')} {contact.get('LastName', '')}".strip(),
                        "phone": contact.get("Phone", ""),
                        "custom_attributes": {
                            "job_title": contact.get("Title", ""),
                            "salesforce_contact_id": contact.get("Id", ""),
                            "lead_source": contact.get("LeadSource", ""),
                            "department": contact.get("Department", ""),
                        },
                    }
                    intercom_data["contacts"].append(intercom_contact)

            return {
                "status": "success",
                "transformed_data": intercom_data,
                "transformation_type": "salesforce_to_intercom",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error transforming Salesforce to Intercom data: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "transformation_type": "salesforce_to_intercom",
                "timestamp": datetime.utcnow().isoformat(),
            }

    def process_data_sync(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process general data synchronization requests."""
        try:
            sync_type = data.get("sync_type", "unknown")
            source_data = data.get("source_data", {})
            target_format = data.get("target_format", "json")

            # Basic data validation and cleaning
            cleaned_data = self._clean_data(source_data)

            return {
                "status": "success",
                "sync_type": sync_type,
                "target_format": target_format,
                "processed_data": cleaned_data,
                "record_count": (
                    len(cleaned_data) if isinstance(cleaned_data, list) else 1
                ),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error processing data sync: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "transformation_type": "data_sync",
                "timestamp": datetime.utcnow().isoformat(),
            }

    def process_lead_enrichment(self, data: dict[str, Any]) -> dict[str, Any]:
        """Process lead enrichment requests."""
        try:
            lead_data = data.get("lead_data", {})
            enrichment_sources = data.get("enrichment_sources", ["basic"])

            # Basic lead enrichment (can be extended with external APIs)
            enriched_lead = {
                **lead_data,
                "enrichment_timestamp": datetime.utcnow().isoformat(),
                "enrichment_sources": enrichment_sources,
                "enrichment_status": "completed",
            }

            # Add computed fields
            if "email" in lead_data:
                enriched_lead["email_domain"] = (
                    lead_data["email"].split("@")[-1]
                    if "@" in lead_data["email"]
                    else ""
                )

            if "company" in lead_data and "title" in lead_data:
                enriched_lead["seniority_level"] = self._determine_seniority(
                    lead_data["title"]
                )

            return {
                "status": "success",
                "enriched_lead": enriched_lead,
                "transformation_type": "lead_enrichment",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error processing lead enrichment: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "transformation_type": "lead_enrichment",
                "timestamp": datetime.utcnow().isoformat(),
            }

    def _clean_data(self, data: Any) -> Any:
        """Clean and validate data."""
        if isinstance(data, dict):
            return {k: self._clean_data(v) for k, v in data.items() if v is not None}
        elif isinstance(data, list):
            return [self._clean_data(item) for item in data if item is not None]
        elif isinstance(data, str):
            return data.strip()
        else:
            return data

    def _determine_seniority(self, title: str) -> str:
        """Determine seniority level from job title."""
        title_lower = title.lower()
        if any(
            word in title_lower
            for word in ["ceo", "cto", "cfo", "president", "founder"]
        ):
            return "executive"
        elif any(
            word in title_lower
            for word in ["director", "vp", "vice president", "head of"]
        ):
            return "senior"
        elif any(word in title_lower for word in ["manager", "lead", "senior"]):
            return "mid"
        else:
            return "junior"


# Initialize processor
processor = N8NWebhookProcessor()


@app.route("/api/n8n/webhook", methods=["POST", "GET"])
@app.route("/api/n8n/webhook/<path:workflow_type>", methods=["POST", "GET"])
def handle_webhook(workflow_type: str | None = None):
    """Handle incoming n8n webhooks."""
    try:
        # Log request details
        logger.info(f"Received {request.method} request for workflow: {workflow_type}")

        if request.method == "GET":
            return jsonify(
                {
                    "status": "ready",
                    "service": "sophia-ai-n8n-webhook",
                    "version": "2.1.0",
                    "supported_workflows": list(processor.supported_workflows.keys()),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        # Parse request data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        if not data:
            return (
                jsonify(
                    {
                        "status": "error",
                        "error": "No data provided",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ),
                400,
            )

        # Determine workflow type
        if not workflow_type:
            workflow_type = data.get("workflow_type", "data_sync")

        # Process the webhook
        if workflow_type in processor.supported_workflows:
            result = processor.supported_workflows[workflow_type](data)
        else:
            result = {
                "status": "error",
                "error": f"Unsupported workflow type: {workflow_type}",
                "supported_workflows": list(processor.supported_workflows.keys()),
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Return appropriate status code
        status_code = 200 if result.get("status") == "success" else 400

        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        return (
            jsonify(
                {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            500,
        )


@app.route("/api/n8n/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "service": "sophia-ai-n8n-webhook",
            "version": "2.1.0",
            "environment": SOPHIA_ENV,
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


# Vercel serverless function handler
def handler(request):
    """Vercel serverless function handler."""
    with app.test_request_context(
        path=request.url.path,
        method=request.method,
        headers=dict(request.headers),
        data=request.body,
        query_string=request.url.query,
    ):
        return app.full_dispatch_request()


# For local development
if __name__ == "__main__":
    app.run(debug=DEBUG, host="0.0.0.0", port=5001)
