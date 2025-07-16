#!/usr/bin/env python3
"""
Specific fixes for Gong and Asana API integration issues
"""

# GONG API FIX - Add required fields
async def fetch_gong_data_fixed(self) -> Dict[str, Any]:
    """Fetch real data from Gong.io - FIXED with required fields"""
    if not self.credentials.get('gong_access_key'):
        return {'status': '❌ No credentials', 'data': [], 'calls': 0, 'has_credentials': False}
    
    try:
        await self.initialize_session()
        
        # FIX: Use correct Gong API endpoint for listing calls
        url = "https://us-70092.api.gong.io/v2/calls"
        
        # Proper Base64 encoding for Gong API
        access_key = self.credentials['gong_access_key']
        access_secret = self.credentials['gong_access_key_secret']
        
        auth_string = f"{access_key}:{access_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f"Basic {auth_b64}",
            'Content-Type': 'application/json'
        }
        
        # FIX: Use GET request for listing calls instead of POST
        # Add proper query parameters
        params = {
            'fromDateTime': (datetime.now() - timedelta(days=7)).isoformat(),
            'toDateTime': datetime.now().isoformat(),
            'limit': 10
        }
        
        logger.info(f"🔧 Gong API: Trying GET {url} with params: {params}")
        
        async with self.session.get(url, headers=headers, params=params) as response:
            response_text = await response.text()
            logger.info(f"Gong API Response: {response.status} - {response_text[:200]}")
            
            if response.status == 200:
                data = await response.json()
                calls = data.get('calls', [])
                
                logger.info(f"✅ Gong: Fetched {len(calls)} calls")
                
                return {
                    'status': '✅ Connected',
                    'data': calls[:10],
                    'total_calls': len(calls),
                    'last_updated': datetime.now().isoformat(),
                    'has_credentials': True
                }
            else:
                logger.error(f"❌ Gong API error: {response.status} - {response_text}")
                return {'status': f'❌ API Error {response.status}', 'data': [], 'calls': 0, 'has_credentials': True}
                
    except Exception as e:
        logger.error(f"❌ Gong connection error: {e}")
        return {'status': f'❌ Connection Error', 'data': [], 'calls': 0, 'has_credentials': True}

# ASANA API FIX - Get workspace first, then projects
async def fetch_asana_data_fixed(self) -> Dict[str, Any]:
    """Fetch real data from Asana - FIXED with workspace"""
    if not self.credentials.get('asana_api_token'):
        return {'status': '❌ No credentials', 'data': [], 'projects': 0, 'has_credentials': False}
    
    try:
        await self.initialize_session()
        
        headers = {
            'Authorization': f"Bearer {self.credentials['asana_api_token']}",
            'Content-Type': 'application/json'
        }
        
        # FIX: First get workspaces
        workspaces_url = "https://app.asana.com/api/1.0/workspaces"
        
        async with self.session.get(workspaces_url, headers=headers) as workspace_response:
            if workspace_response.status != 200:
                logger.error(f"❌ Asana workspace error: {workspace_response.status}")
                return {'status': f'❌ Workspace Error {workspace_response.status}', 'data': [], 'projects': 0, 'has_credentials': True}
            
            workspace_data = await workspace_response.json()
            workspaces = workspace_data.get('data', [])
            
            if not workspaces:
                logger.error("❌ No Asana workspaces found")
                return {'status': '❌ No Workspaces', 'data': [], 'projects': 0, 'has_credentials': True}
            
            # Use first workspace
            workspace_gid = workspaces[0]['gid']
            logger.info(f"🔧 Using Asana workspace: {workspace_gid}")
        
        # Now get projects for this workspace
        projects_url = "https://app.asana.com/api/1.0/projects"
        params = {
            'workspace': workspace_gid,
            'limit': 10,
            'opt_fields': 'name,created_at,modified_at,owner,team'
        }
        
        logger.info(f"🔧 Asana API: Trying {projects_url} with workspace {workspace_gid}")
        
        async with self.session.get(projects_url, headers=headers, params=params) as response:
            response_text = await response.text()
            logger.info(f"Asana API Response: {response.status} - {response_text[:200]}")
            
            if response.status == 200:
                data = await response.json()
                projects = data.get('data', [])
                
                logger.info(f"✅ Asana: Fetched {len(projects)} projects")
                
                return {
                    'status': '✅ Connected',
                    'data': projects,
                    'total_projects': len(projects),
                    'workspace_gid': workspace_gid,
                    'last_updated': datetime.now().isoformat(),
                    'has_credentials': True
                }
            else:
                logger.error(f"❌ Asana API error: {response.status} - {response_text}")
                return {'status': f'❌ API Error {response.status}', 'data': [], 'projects': 0, 'has_credentials': True}
                
    except Exception as e:
        logger.error(f"❌ Asana connection error: {e}")
        return {'status': f'❌ Connection Error', 'data': [], 'projects': 0, 'has_credentials': True}

# ALTERNATIVE GONG API APPROACH - Try different endpoint
async def fetch_gong_data_alternative(self) -> Dict[str, Any]:
    """Alternative Gong API approach - try users endpoint first"""
    if not self.credentials.get('gong_access_key'):
        return {'status': '❌ No credentials', 'data': [], 'calls': 0, 'has_credentials': False}
    
    try:
        await self.initialize_session()
        
        # Try users endpoint first to test auth
        access_key = self.credentials['gong_access_key']
        access_secret = self.credentials['gong_access_key_secret']
        
        auth_string = f"{access_key}:{access_secret}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            'Authorization': f"Basic {auth_b64}",
            'Content-Type': 'application/json'
        }
        
        # Test with users endpoint first
        users_url = "https://us-70092.api.gong.io/v2/users"
        
        async with self.session.get(users_url, headers=headers) as response:
            response_text = await response.text()
            logger.info(f"Gong Users API Response: {response.status} - {response_text[:200]}")
            
            if response.status == 200:
                users_data = await response.json()
                users = users_data.get('users', [])
                
                logger.info(f"✅ Gong: Auth successful, {len(users)} users found")
                
                return {
                    'status': '✅ Connected (Users)',
                    'data': users[:5],  # Show first 5 users as test data
                    'total_users': len(users),
                    'last_updated': datetime.now().isoformat(),
                    'has_credentials': True
                }
            else:
                logger.error(f"❌ Gong Users API error: {response.status} - {response_text}")
                return {'status': f'❌ API Error {response.status}', 'data': [], 'calls': 0, 'has_credentials': True}
                
    except Exception as e:
        logger.error(f"❌ Gong connection error: {e}")
        return {'status': f'❌ Connection Error', 'data': [], 'calls': 0, 'has_credentials': True}

