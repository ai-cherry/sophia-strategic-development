# 🌐 DNS Configuration Guide for sophia-intel.ai

## Required DNS Records

To fix the SSL certificate mismatch, configure these DNS records:

### A Records
- `sophia-intel.ai` → `192.222.58.232`
- `api.sophia-intel.ai` → `192.222.58.232`
- `app.sophia-intel.ai` → `192.222.58.232`
- `ws.sophia-intel.ai` → `192.222.58.232`

### CNAME Records (Alternative)
- `api.sophia-intel.ai` → `sophia-intel.ai`
- `app.sophia-intel.ai` → `sophia-intel.ai`
- `ws.sophia-intel.ai` → `sophia-intel.ai`

## Manual DNS Configuration Steps

### Option 1: Namecheap Dashboard
1. Log into Namecheap account
2. Go to Domain List → sophia-intel.ai → Manage
3. Navigate to Advanced DNS
4. Add/Update these records:

```
Type    Host    Value                   TTL
A       @       192.222.58.232         300
A       api     192.222.58.232         300
A       app     192.222.58.232         300
A       ws      192.222.58.232         300
```

### Option 2: Pulumi DNS Management
Run the DNS infrastructure deployment:

```bash
cd infrastructure/dns
pulumi up
```

### Option 3: GitHub Actions DNS Deployment
Trigger the DNS workflow:

```bash
gh workflow run dns-infrastructure.yml
```

## Verification Commands

After DNS configuration, verify with:

```bash
# Check DNS resolution
nslookup api.sophia-intel.ai
dig api.sophia-intel.ai

# Test SSL certificate
curl -I https://api.sophia-intel.ai/health
openssl s_client -connect api.sophia-intel.ai:443 -servername api.sophia-intel.ai
```

## Expected Results

After DNS configuration and SSL certificate provisioning (5-10 minutes):

- ✅ `https://api.sophia-intel.ai/health` returns 200 OK
- ✅ `https://sophia-intel.ai` loads frontend  
- ✅ No SSL certificate errors
- ✅ Real business data displays (no more mock data)

## Troubleshooting

### DNS Propagation
- DNS changes can take 5-60 minutes to propagate
- Use `dig +trace api.sophia-intel.ai` to check propagation

### SSL Certificate Issues  
- Certificates are auto-provisioned by cert-manager
- Check with: `kubectl get certificate -n sophia-ai-prod`
- Allow 5-10 minutes for Let's Encrypt issuance

### Application Issues
- Verify backend pods are running: `kubectl get pods -n sophia-ai-prod`
- Check ingress status: `kubectl get ingress -n sophia-ai-prod`
- Review logs: `kubectl logs -n sophia-ai-prod deployment/sophia-backend`

---
*Generated on 2025-07-16 15:54:57*
