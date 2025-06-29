# 🚨 Snowflake 404 Error Troubleshooting Guide - Sophia AI

## **CRITICAL ERROR DETAILS**

### **Current Error Pattern:**
```
ERROR: 250003 (08001): None: 404 Not Found: 
post https://scoobyjava-vw02766.snowflakecomputing.com:443/session/v1/login-request
```

### **Key Issue Indicators:**
- **Error Code:** `250003 (08001)` - Network connectivity/authentication failure
- **HTTP Status:** `404 Not Found` - Account locator not found
- **Endpoint:** `scoobyjava-vw02766.snowflakecomputing.com` - Invalid account identifier
- **Expected Account:** `ZNB04675` (correct account)
- **Current Problem:** System still using old account `scoobyjava-vw02766`

---

## 🔍 **SOPHIA-MAIN REPOSITORY INVESTIGATION**

### **1. Configuration Files to Check:**

#### **A. Primary Configuration Sources:**
```bash
# Check these files for old account references:
grep -r "scoobyjava-vw02766" backend/
grep -r "scoobyjava-vw02766" config/
grep -r "scoobyjava-vw02766" infrastructure/
```

#### **B. Critical Files Already Updated (but verify):**
- `backend/core/security_config.py` ✅ (Fixed to ZNB04675)
- `snowflake_advanced_features_implementation.py` ✅ (Fixed to ZNB04675)
- `pulumi/esc/sophia-ai-production.yaml` ✅ (Fixed to ZNB04675)

#### **C. Potential Hidden Configuration Sources:**
```bash
# Check environment variables
env | grep -i snowflake

# Check for cached Python bytecode
find . -name "*.pyc" -exec grep -l "scoobyjava-vw02766" {} \; 2>/dev/null

# Check for hidden config files
find . -name ".*" -type f -exec grep -l "scoobyjava-vw02766" {} \; 2>/dev/null
```

### **2. Connection Manager Investigation:**

#### **A. OptimizedConnectionManager Analysis:**
File: `backend/core/optimized_connection_manager.py`

**Key Investigation Points:**
1. **Connection String Construction:** How is the Snowflake URL built?
2. **Configuration Priority:** Which config source takes precedence?
3. **Caching Issues:** Are old connection parameters cached?

#### **B. Configuration Loading Chain:**
```python
# Trace this chain:
1. auto_esc_config.py → get_config_value()
2. security_config.py → NON_SECRET_CONFIG
3. snowflake_config_override.py → Override values
4. Environment variables → Fallback values
```

### **3. Pulumi ESC Integration Check:**

#### **A. ESC Configuration Verification:**
```bash
# Check if Pulumi ESC is loading correct values
pulumi config get snowflake_account --stack sophia-ai-production
pulumi config list --stack sophia-ai-production | grep snowflake
```

#### **B. ESC Secret Synchronization:**
File: `pulumi/esc/sophia-ai-production.yaml`
- Verify `snowflake_account: "ZNB04675"` is set correctly
- Check if ESC sync is working: GitHub Secrets → Pulumi ESC → Backend

### **4. Runtime Configuration Debug:**

#### **A. Add Debug Logging:**
```python
# Add to backend/core/optimized_connection_manager.py
import logging
logger = logging.getLogger(__name__)

# Before connection attempt:
logger.info(f"🔍 Snowflake Account: {account}")
logger.info(f"🔍 Snowflake User: {user}")
logger.info(f"🔍 Snowflake Database: {database}")
logger.info(f"🔍 Connection URL: {connection_url}")
```

#### **B. Configuration Source Tracing:**
```python
# Add to auto_esc_config.py
def get_config_value(key, default=None):
    value = # ... existing logic
    logger.info(f"🔍 Config {key} = {value} (source: {source})")
    return value
```

---

## 🔍 **SNOWFLAKE ACCOUNT INVESTIGATION**

### **1. Account Locator Verification:**

#### **A. Correct Account Information:**
- **Account Locator:** `ZNB04675`
- **Region:** (Need to verify - likely US-WEST-2 or US-EAST-1)
- **Cloud Provider:** (Need to verify - likely AWS)
- **Full Account URL:** `https://ZNB04675.snowflakecomputing.com`

#### **B. Account Locator Formats to Test:**
```
# Try these variations:
1. ZNB04675
2. ZNB04675.us-west-2
3. ZNB04675.us-east-1
4. ZNB04675.aws
5. ZNB04675.us-west-2.aws
```

### **2. Snowflake Console Verification:**

#### **A. Login to Snowflake Web UI:**
1. Go to `https://app.snowflake.com`
2. Use account locator: `ZNB04675`
3. Verify successful login with user: `SCOOBYJAVA15`
4. Note the exact URL after login (this shows correct format)

#### **B. Account Information Query:**
```sql
-- Run in Snowflake console:
SELECT CURRENT_ACCOUNT();
SELECT CURRENT_REGION();
SELECT CURRENT_CLOUD();

-- Check account URL:
SHOW PARAMETERS LIKE 'ACCOUNT_LOCATOR';
```

### **3. Network Connectivity Test:**

#### **A. DNS Resolution Check:**
```bash
# Test DNS resolution:
nslookup ZNB04675.snowflakecomputing.com
nslookup scoobyjava-vw02766.snowflakecomputing.com

# Expected: ZNB04675 resolves, scoobyjava-vw02766 fails
```

#### **B. Connection Test:**
```bash
# Test HTTPS connectivity:
curl -I https://ZNB04675.snowflakecomputing.com
curl -I https://scoobyjava-vw02766.snowflakecomputing.com

# Expected: ZNB04675 returns 200/403, scoobyjava-vw02766 returns 404
```

### **4. Snowflake User and Permissions:**

#### **A. User Verification:**
```sql
-- Check user exists and is active:
SHOW USERS LIKE 'SCOOBYJAVA15';

-- Check user roles:
SHOW GRANTS TO USER SCOOBYJAVA15;
```

#### **B. Database and Warehouse Access:**
```sql
-- Verify database exists:
SHOW DATABASES LIKE 'SOPHIA_AI_PROD';

-- Verify warehouse exists:
SHOW WAREHOUSES LIKE 'SOPHIA_AI_WH';

-- Check permissions:
SHOW GRANTS ON DATABASE SOPHIA_AI_PROD;
SHOW GRANTS ON WAREHOUSE SOPHIA_AI_WH;
```

---

## 🔧 **TROUBLESHOOTING STEPS**

### **Priority 1: Configuration Source Investigation**

1. **Find Configuration Source:**
   ```bash
   # Run this in sophia-main:
   python -c "
   from backend.core.auto_esc_config import get_config_value
   print('Account:', get_config_value('snowflake_account'))
   print('User:', get_config_value('snowflake_user'))
   print('Database:', get_config_value('snowflake_database'))
   "
   ```

2. **Check All Config Files:**
   ```bash
   # Search entire codebase:
   find . -type f -name "*.py" -exec grep -l "scoobyjava-vw02766" {} \;
   find . -type f -name "*.yaml" -exec grep -l "scoobyjava-vw02766" {} \;
   find . -type f -name "*.json" -exec grep -l "scoobyjava-vw02766" {} \;
   ```

### **Priority 2: Snowflake Account Validation**

1. **Test Account Locator:**
   ```python
   # Test script:
   import snowflake.connector
   try:
       conn = snowflake.connector.connect(
           account='ZNB04675',
           user='SCOOBYJAVA15',
           password='[PASSWORD]',  # Use actual password
           database='SOPHIA_AI_PROD',
           warehouse='SOPHIA_AI_WH'
       )
       print("✅ Connection successful!")
       print("Account:", conn.account)
   except Exception as e:
       print("❌ Connection failed:", e)
   ```

2. **Verify in Snowflake Console:**
   - Login to Snowflake web interface
   - Confirm account locator format
   - Test database and warehouse access

### **Priority 3: Environment Reset**

1. **Clear Python Cache:**
   ```bash
   find . -name "__pycache__" -exec rm -rf {} \; 2>/dev/null || true
   find . -name "*.pyc" -delete 2>/dev/null || true
   ```

2. **Restart Services:**
   ```bash
   # Kill all Python processes
   pkill -f python
   
   # Restart FastAPI with debug logging
   PYTHONPATH=. python -c "
   import logging
   logging.basicConfig(level=logging.DEBUG)
   import uvicorn
   uvicorn.run('backend.app.fastapi_app:app', host='0.0.0.0', port=8000)
   "
   ```

---

## 🎯 **EXPECTED FIXES**

### **Root Cause Scenarios:**

1. **Hidden Configuration File:**
   - Old config file still loading `scoobyjava-vw02766`
   - Solution: Find and update all config sources

2. **Cached Connection Parameters:**
   - Connection manager caching old values
   - Solution: Clear cache and restart

3. **Environment Variable Override:**
   - System environment variable overriding config
   - Solution: Check and update environment

4. **Incorrect Account Format:**
   - Account locator needs region/cloud suffix
   - Solution: Use correct format (e.g., `ZNB04675.us-west-2.aws`)

### **Success Indicators:**

✅ **Connection Successful When:**
- No 404 errors in logs
- Snowflake connection pool shows >0 connections
- Health endpoint returns database connectivity status
- Logs show: `✅ ConnectionType.SNOWFLAKE pool initialized with X connections`

---

## 📋 **INVESTIGATION CHECKLIST**

### **Sophia-Main Repository:**
- [ ] Search entire codebase for `scoobyjava-vw02766`
- [ ] Verify all config files use `ZNB04675`
- [ ] Check environment variables
- [ ] Clear Python cache
- [ ] Test configuration loading chain
- [ ] Add debug logging to connection manager

### **Snowflake Account:**
- [ ] Login to Snowflake web console with `ZNB04675`
- [ ] Verify account locator format
- [ ] Test user `SCOOBYJAVA15` permissions
- [ ] Confirm database `SOPHIA_AI_PROD` exists
- [ ] Confirm warehouse `SOPHIA_AI_WH` exists
- [ ] Test direct Python connection

### **Network/DNS:**
- [ ] Test DNS resolution for both accounts
- [ ] Test HTTPS connectivity
- [ ] Verify no firewall blocking

---

**🎯 Once you identify the root cause, apply the fix and test with:**
```bash
uv run python -c "
from backend.core.optimized_connection_manager import OptimizedConnectionManager, ConnectionType
import asyncio

async def test():
    manager = OptimizedConnectionManager()
    conn = await manager.get_connection(ConnectionType.SNOWFLAKE)
    print('✅ Snowflake connection successful!')

asyncio.run(test())
"
```
