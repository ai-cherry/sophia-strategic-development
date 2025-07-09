# Outdated Model References Report

Total files with outdated references: 14


## Summary by Model

- **claude-3-opus**: 53 references → replace with `claude-3-5-sonnet-20241022`
- **gemini-1.5-pro**: 41 references → replace with `gemini-2.0-flash-exp`
- **gpt-4-turbo**: 31 references → replace with `gpt-4o`
- **anthropic/claude-3-opus**: 16 references → replace with `anthropic/claude-3.5-sonnet`
- **openai/gpt-4-turbo**: 14 references → replace with `openai/gpt-4o`
- **gpt-4-turbo-preview**: 14 references → replace with `gpt-4o`
- **claude-3-opus-20240229**: 12 references → replace with `claude-3-5-sonnet-20241022`
- **openai/gpt-4-turbo-preview**: 8 references → replace with `openai/gpt-4o`
- **gemini-1.5-pro-latest**: 6 references → replace with `gemini-2.0-flash-exp`
- **google/gemini-1.5-pro**: 4 references → replace with `google/gemini-2.0-flash-exp`

## Detailed Findings


### .json Files (4 files)


#### /Users/lynnmusil/sophia-main/.cursor-settings.json

- Line 3: `gpt-4-turbo` → `gpt-4o`
  ```
  "pulumi.ai.model": "gpt-4-turbo",
  ```
- Line 3: `gpt-4-turbo` → `gpt-4o`
  ```
  "pulumi.ai.model": "gpt-4-turbo",
  ```

#### /Users/lynnmusil/sophia-main/config/llm_router.json

- Line 39: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus": {
  ```
- Line 87: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "architecture_design": ["claude-3-5-sonnet", "gpt-4o", "claude-3-opus"],
  ```
- Line 96: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "creative_writing": ["claude-3-5-sonnet", "claude-3-opus", "gpt-4o"],
  ```
- Line 106: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "architecture": ["claude-3-5-sonnet", "claude-3-opus", "gpt-4o"]
  ```
- Line 111: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "premium": ["claude-3-5-sonnet", "claude-3-opus", "gpt-4o", "gpt-4"]
  ```
- Line 39: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus": {
  ```
- Line 40: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "name": "claude-3-opus-20240229",
  ```
- Line 87: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "architecture_design": ["claude-3-5-sonnet", "gpt-4o", "claude-3-opus"],
  ```
- Line 96: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "creative_writing": ["claude-3-5-sonnet", "claude-3-opus", "gpt-4o"],
  ```
- Line 106: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "architecture": ["claude-3-5-sonnet", "claude-3-opus", "gpt-4o"]
  ```
- Line 111: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "premium": ["claude-3-5-sonnet", "claude-3-opus", "gpt-4o", "gpt-4"]
  ```
- Line 40: `claude-3-opus-20240229` → `claude-3-5-sonnet-20241022`
  ```
  "name": "claude-3-opus-20240229",
  ```
- Line 40: `claude-3-opus-20240229` → `claude-3-5-sonnet-20241022`
  ```
  "name": "claude-3-opus-20240229",
  ```

#### /Users/lynnmusil/sophia-main/config/portkey/sophia-ai-config.json

- Line 18: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus",
  ```
- Line 18: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus",
  ```
- Line 10: `gpt-4-turbo` → `gpt-4o`
  ```
  "gpt-4-turbo"
  ```
- Line 10: `gpt-4-turbo` → `gpt-4o`
  ```
  "gpt-4-turbo"
  ```

#### /Users/lynnmusil/sophia-main/config/services/portkey.json

- Line 12: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "route_to": "claude-3-opus"
  ```
- Line 16: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "route_to": "claude-3-opus"
  ```
- Line 24: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "route_to": "claude-3-opus"
  ```
- Line 28: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "route_to": "claude-3-opus"
  ```
- Line 35: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "fallback_providers": ["claude-3-opus", "gpt-4", "openrouter/mixtral"]
  ```
- Line 12: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "route_to": "claude-3-opus"
  ```
- Line 16: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "route_to": "claude-3-opus"
  ```
- Line 24: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "route_to": "claude-3-opus"
  ```
- Line 28: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "route_to": "claude-3-opus"
  ```
- Line 35: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "fallback_providers": ["claude-3-opus", "gpt-4", "openrouter/mixtral"]
  ```

### .md Files (2 files)


#### /Users/lynnmusil/sophia-main/docs/ai-context/sophia-brain.md

- Line 66: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "business_intelligence": ["gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro"],
  ```
- Line 67: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "research": ["gemini-1.5-pro", "claude-3-5-sonnet", "gpt-4o"],
  ```
- Line 72: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "premium_mode": ["claude-3-5-sonnet", "gpt-4o", "gemini-1.5-pro"]
  ```
- Line 66: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "business_intelligence": ["gpt-4o", "claude-3-5-sonnet", "gemini-1.5-pro"],
  ```
- Line 67: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "research": ["gemini-1.5-pro", "claude-3-5-sonnet", "gpt-4o"],
  ```
- Line 72: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "premium_mode": ["claude-3-5-sonnet", "gpt-4o", "gemini-1.5-pro"]
  ```

#### /Users/lynnmusil/sophia-main/docs/implementation/LLM_ROUTER_MIGRATION_GUIDE.md

- Line 139: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  model="claude-3-opus",
  ```
- Line 148: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  model_override="claude-3-opus"  # Optional override
  ```
- Line 139: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  model="claude-3-opus",
  ```
- Line 148: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  model_override="claude-3-opus"  # Optional override
  ```

### .py Files (7 files)


#### /Users/lynnmusil/sophia-main/infrastructure/services/enhanced_portkey_llm_gateway.py

- Line 157: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro": ModelTarget(
  ```
- Line 158: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  name="gemini-1.5-pro",
  ```
- Line 193: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro",
  ```
- Line 195: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "research": ["gemini-1.5-pro", "claude-3-5-sonnet", "gpt-4o"],
  ```
- Line 197: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "document_analysis": ["gemini-1.5-pro", "claude-3-5-sonnet"],
  ```
- Line 207: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro",
  ```
- Line 212: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro",
  ```
- Line 219: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "large": ["gemini-1.5-pro", "claude-3-5-sonnet"],
  ```
- Line 220: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "extra_large": ["gemini-1.5-pro"],
  ```
- Line 226: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "premium_mode": ["claude-3-5-sonnet", "gpt-4o", "gemini-1.5-pro"],
  ```
- Line 157: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro": ModelTarget(
  ```
- Line 158: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  name="gemini-1.5-pro",
  ```
- Line 160: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  model="gemini-1.5-pro-latest",
  ```
- Line 193: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro",
  ```
- Line 195: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "research": ["gemini-1.5-pro", "claude-3-5-sonnet", "gpt-4o"],
  ```
- Line 197: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "document_analysis": ["gemini-1.5-pro", "claude-3-5-sonnet"],
  ```
- Line 207: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro",
  ```
- Line 212: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro",
  ```
- Line 219: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "large": ["gemini-1.5-pro", "claude-3-5-sonnet"],
  ```
- Line 220: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "extra_large": ["gemini-1.5-pro"],
  ```
- Line 226: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "premium_mode": ["claude-3-5-sonnet", "gpt-4o", "gemini-1.5-pro"],
  ```
- Line 160: `gemini-1.5-pro-latest` → `gemini-2.0-flash-exp`
  ```
  model="gemini-1.5-pro-latest",
  ```
- Line 160: `gemini-1.5-pro-latest` → `gemini-2.0-flash-exp`
  ```
  model="gemini-1.5-pro-latest",
  ```

#### /Users/lynnmusil/sophia-main/infrastructure/services/llm_gateway/openrouter_integration.py

- Line 33: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  "anthropic/claude-3-opus",
  ```
- Line 44: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  "anthropic/claude-3-opus",
  ```
- Line 57: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  "anthropic/claude-3-opus",  # Strong context understanding
  ```
- Line 63: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  "anthropic/claude-3-opus",
  ```
- Line 84: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  "anthropic/claude-3-opus": {
  ```
- Line 33: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  "anthropic/claude-3-opus",
  ```
- Line 44: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  "anthropic/claude-3-opus",
  ```
- Line 57: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  "anthropic/claude-3-opus",  # Strong context understanding
  ```
- Line 63: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  "anthropic/claude-3-opus",
  ```
- Line 84: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  "anthropic/claude-3-opus": {
  ```
- Line 33: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "anthropic/claude-3-opus",
  ```
- Line 44: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "anthropic/claude-3-opus",
  ```
- Line 57: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "anthropic/claude-3-opus",  # Strong context understanding
  ```
- Line 63: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "anthropic/claude-3-opus",
  ```
- Line 84: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "anthropic/claude-3-opus": {
  ```
- Line 32: `gpt-4-turbo` → `gpt-4o`
  ```
  "openai/gpt-4-turbo-preview",
  ```
- Line 38: `gpt-4-turbo` → `gpt-4o`
  ```
  "openai/gpt-4-turbo",
  ```
- Line 56: `gpt-4-turbo` → `gpt-4o`
  ```
  "openai/gpt-4-turbo",  # Fine-tuned for business
  ```
- Line 62: `gpt-4-turbo` → `gpt-4o`
  ```
  "openai/gpt-4-turbo",
  ```
- Line 77: `gpt-4-turbo` → `gpt-4o`
  ```
  "openai/gpt-4-turbo-preview": {
  ```
- Line 38: `openai/gpt-4-turbo` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo",
  ```
- Line 56: `openai/gpt-4-turbo` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo",  # Fine-tuned for business
  ```
- Line 62: `openai/gpt-4-turbo` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo",
  ```
- Line 32: `openai/gpt-4-turbo` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo-preview",
  ```
- Line 38: `openai/gpt-4-turbo` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo",
  ```
- Line 56: `openai/gpt-4-turbo` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo",  # Fine-tuned for business
  ```
- Line 62: `openai/gpt-4-turbo` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo",
  ```
- Line 77: `openai/gpt-4-turbo` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo-preview": {
  ```
- Line 32: `gpt-4-turbo-preview` → `gpt-4o`
  ```
  "openai/gpt-4-turbo-preview",
  ```
- Line 77: `gpt-4-turbo-preview` → `gpt-4o`
  ```
  "openai/gpt-4-turbo-preview": {
  ```
- Line 32: `openai/gpt-4-turbo-preview` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo-preview",
  ```
- Line 77: `openai/gpt-4-turbo-preview` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo-preview": {
  ```
- Line 32: `openai/gpt-4-turbo-preview` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo-preview",
  ```
- Line 77: `openai/gpt-4-turbo-preview` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo-preview": {
  ```

#### /Users/lynnmusil/sophia-main/infrastructure/services/llm_gateway/portkey_integration.py

- Line 49: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus",
  ```
- Line 49: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus",
  ```
- Line 48: `gpt-4-turbo` → `gpt-4o`
  ```
  "gpt-4-turbo-preview",
  ```
- Line 157: `gpt-4-turbo` → `gpt-4o`
  ```
  "model": settings.get("model", "gpt-4-turbo-preview"),
  ```
- Line 48: `gpt-4-turbo-preview` → `gpt-4o`
  ```
  "gpt-4-turbo-preview",
  ```
- Line 157: `gpt-4-turbo-preview` → `gpt-4o`
  ```
  "model": settings.get("model", "gpt-4-turbo-preview"),
  ```
- Line 48: `gpt-4-turbo-preview` → `gpt-4o`
  ```
  "gpt-4-turbo-preview",
  ```
- Line 157: `gpt-4-turbo-preview` → `gpt-4o`
  ```
  "model": settings.get("model", "gpt-4-turbo-preview"),
  ```

#### /Users/lynnmusil/sophia-main/infrastructure/services/llm_router/fallback.py

- Line 342: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  TaskComplexity.ARCHITECTURE: "anthropic/claude-3-opus",
  ```
- Line 342: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  TaskComplexity.ARCHITECTURE: "anthropic/claude-3-opus",
  ```
- Line 336: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  TaskComplexity.ARCHITECTURE: "claude-3-opus-20240229",
  ```
- Line 342: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  TaskComplexity.ARCHITECTURE: "anthropic/claude-3-opus",
  ```
- Line 353: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  TaskComplexity.COMPLEX: "claude-3-opus-20240229",
  ```
- Line 354: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  TaskComplexity.ARCHITECTURE: "claude-3-opus-20240229",
  ```
- Line 336: `claude-3-opus-20240229` → `claude-3-5-sonnet-20241022`
  ```
  TaskComplexity.ARCHITECTURE: "claude-3-opus-20240229",
  ```
- Line 353: `claude-3-opus-20240229` → `claude-3-5-sonnet-20241022`
  ```
  TaskComplexity.COMPLEX: "claude-3-opus-20240229",
  ```
- Line 354: `claude-3-opus-20240229` → `claude-3-5-sonnet-20241022`
  ```
  TaskComplexity.ARCHITECTURE: "claude-3-opus-20240229",
  ```
- Line 336: `claude-3-opus-20240229` → `claude-3-5-sonnet-20241022`
  ```
  TaskComplexity.ARCHITECTURE: "claude-3-opus-20240229",
  ```
- Line 353: `claude-3-opus-20240229` → `claude-3-5-sonnet-20241022`
  ```
  TaskComplexity.COMPLEX: "claude-3-opus-20240229",
  ```
- Line 354: `claude-3-opus-20240229` → `claude-3-5-sonnet-20241022`
  ```
  TaskComplexity.ARCHITECTURE: "claude-3-opus-20240229",
  ```

#### /Users/lynnmusil/sophia-main/infrastructure/sophia_iac_orchestrator.py

- Line 136: `gpt-4-turbo` → `gpt-4o`
  ```
  model="gpt-4-turbo-preview",
  ```
- Line 136: `gpt-4-turbo-preview` → `gpt-4o`
  ```
  model="gpt-4-turbo-preview",
  ```
- Line 136: `gpt-4-turbo-preview` → `gpt-4o`
  ```
  model="gpt-4-turbo-preview",
  ```

#### /Users/lynnmusil/sophia-main/scripts/cleanup_outdated_models.py

- Line 16: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  "anthropic/claude-3-opus",
  ```
- Line 31: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  "anthropic/claude-3-opus": "anthropic/claude-3.5-sonnet",
  ```
- Line 16: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  "anthropic/claude-3-opus",
  ```
- Line 31: `anthropic/claude-3-opus` → `anthropic/claude-3.5-sonnet`
  ```
  "anthropic/claude-3-opus": "anthropic/claude-3.5-sonnet",
  ```
- Line 14: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus",
  ```
- Line 29: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus": "claude-3-5-sonnet-20241022",
  ```
- Line 14: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus",
  ```
- Line 15: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus-20240229",
  ```
- Line 16: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "anthropic/claude-3-opus",
  ```
- Line 29: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus": "claude-3-5-sonnet-20241022",
  ```
- Line 30: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus-20240229": "claude-3-5-sonnet-20241022",
  ```
- Line 31: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  "anthropic/claude-3-opus": "anthropic/claude-3.5-sonnet",
  ```
- Line 20: `gpt-4-turbo` → `gpt-4o`
  ```
  "gpt-4-turbo",
  ```
- Line 39: `gpt-4-turbo` → `gpt-4o`
  ```
  "gpt-4-turbo": "gpt-4o",
  ```
- Line 20: `gpt-4-turbo` → `gpt-4o`
  ```
  "gpt-4-turbo",
  ```
- Line 21: `gpt-4-turbo` → `gpt-4o`
  ```
  "gpt-4-turbo-preview",
  ```
- Line 22: `gpt-4-turbo` → `gpt-4o`
  ```
  "openai/gpt-4-turbo",
  ```
- Line 23: `gpt-4-turbo` → `gpt-4o`
  ```
  "openai/gpt-4-turbo-preview",
  ```
- Line 39: `gpt-4-turbo` → `gpt-4o`
  ```
  "gpt-4-turbo": "gpt-4o",
  ```
- Line 40: `gpt-4-turbo` → `gpt-4o`
  ```
  "gpt-4-turbo-preview": "gpt-4o",
  ```
- Line 41: `gpt-4-turbo` → `gpt-4o`
  ```
  "openai/gpt-4-turbo": "openai/gpt-4o",
  ```
- Line 42: `gpt-4-turbo` → `gpt-4o`
  ```
  "openai/gpt-4-turbo-preview": "openai/gpt-4o",
  ```
- Line 17: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro",
  ```
- Line 34: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro": "gemini-2.0-flash-exp",
  ```
- Line 17: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro",
  ```
- Line 18: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro-latest",
  ```
- Line 19: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "google/gemini-1.5-pro",
  ```
- Line 34: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro": "gemini-2.0-flash-exp",
  ```
- Line 35: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro-latest": "gemini-2.0-flash-exp",
  ```
- Line 36: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  "google/gemini-1.5-pro": "google/gemini-2.0-flash-exp",
  ```
- Line 15: `claude-3-opus-20240229` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus-20240229",
  ```
- Line 30: `claude-3-opus-20240229` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus-20240229": "claude-3-5-sonnet-20241022",
  ```
- Line 15: `claude-3-opus-20240229` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus-20240229",
  ```
- Line 30: `claude-3-opus-20240229` → `claude-3-5-sonnet-20241022`
  ```
  "claude-3-opus-20240229": "claude-3-5-sonnet-20241022",
  ```
- Line 19: `google/gemini-1.5-pro` → `google/gemini-2.0-flash-exp`
  ```
  "google/gemini-1.5-pro",
  ```
- Line 36: `google/gemini-1.5-pro` → `google/gemini-2.0-flash-exp`
  ```
  "google/gemini-1.5-pro": "google/gemini-2.0-flash-exp",
  ```
- Line 19: `google/gemini-1.5-pro` → `google/gemini-2.0-flash-exp`
  ```
  "google/gemini-1.5-pro",
  ```
- Line 36: `google/gemini-1.5-pro` → `google/gemini-2.0-flash-exp`
  ```
  "google/gemini-1.5-pro": "google/gemini-2.0-flash-exp",
  ```
- Line 22: `openai/gpt-4-turbo` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo",
  ```
- Line 41: `openai/gpt-4-turbo` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo": "openai/gpt-4o",
  ```
- Line 22: `openai/gpt-4-turbo` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo",
  ```
- Line 23: `openai/gpt-4-turbo` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo-preview",
  ```
- Line 41: `openai/gpt-4-turbo` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo": "openai/gpt-4o",
  ```
- Line 42: `openai/gpt-4-turbo` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo-preview": "openai/gpt-4o",
  ```
- Line 21: `gpt-4-turbo-preview` → `gpt-4o`
  ```
  "gpt-4-turbo-preview",
  ```
- Line 40: `gpt-4-turbo-preview` → `gpt-4o`
  ```
  "gpt-4-turbo-preview": "gpt-4o",
  ```
- Line 21: `gpt-4-turbo-preview` → `gpt-4o`
  ```
  "gpt-4-turbo-preview",
  ```
- Line 23: `gpt-4-turbo-preview` → `gpt-4o`
  ```
  "openai/gpt-4-turbo-preview",
  ```
- Line 40: `gpt-4-turbo-preview` → `gpt-4o`
  ```
  "gpt-4-turbo-preview": "gpt-4o",
  ```
- Line 42: `gpt-4-turbo-preview` → `gpt-4o`
  ```
  "openai/gpt-4-turbo-preview": "openai/gpt-4o",
  ```
- Line 18: `gemini-1.5-pro-latest` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro-latest",
  ```
- Line 35: `gemini-1.5-pro-latest` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro-latest": "gemini-2.0-flash-exp",
  ```
- Line 18: `gemini-1.5-pro-latest` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro-latest",
  ```
- Line 35: `gemini-1.5-pro-latest` → `gemini-2.0-flash-exp`
  ```
  "gemini-1.5-pro-latest": "gemini-2.0-flash-exp",
  ```
- Line 23: `openai/gpt-4-turbo-preview` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo-preview",
  ```
- Line 42: `openai/gpt-4-turbo-preview` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo-preview": "openai/gpt-4o",
  ```
- Line 23: `openai/gpt-4-turbo-preview` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo-preview",
  ```
- Line 42: `openai/gpt-4-turbo-preview` → `openai/gpt-4o`
  ```
  "openai/gpt-4-turbo-preview": "openai/gpt-4o",
  ```

#### /Users/lynnmusil/sophia-main/scripts/mcp_orchestration_optimizer.py

- Line 376: `gpt-4-turbo` → `gpt-4o`
  ```
  "fallback": "gpt-4-turbo",
  ```
- Line 432: `gpt-4-turbo` → `gpt-4o`
  ```
  "gpt-4-turbo": {
  ```
- Line 473: `gpt-4-turbo` → `gpt-4o`
  ```
  "gpt-4-turbo": 0.01,
  ```
- Line 376: `gpt-4-turbo` → `gpt-4o`
  ```
  "fallback": "gpt-4-turbo",
  ```
- Line 432: `gpt-4-turbo` → `gpt-4o`
  ```
  "gpt-4-turbo": {
  ```
- Line 473: `gpt-4-turbo` → `gpt-4o`
  ```
  "gpt-4-turbo": 0.01,
  ```

### .yaml Files (1 files)


#### /Users/lynnmusil/sophia-main/config/services/optimization.yaml

- Line 216: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  models: ["gpt-4o", "claude-3-opus", "gemini-1.5-pro"]
  ```
- Line 265: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  model: "claude-3-opus"
  ```
- Line 333: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  competitive_intelligence: "claude-3-opus"
  ```
- Line 37: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  - claude-3-opus
  ```
- Line 216: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  models: ["gpt-4o", "claude-3-opus", "gemini-1.5-pro"]
  ```
- Line 265: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  model: "claude-3-opus"
  ```
- Line 333: `claude-3-opus` → `claude-3-5-sonnet-20241022`
  ```
  competitive_intelligence: "claude-3-opus"
  ```
- Line 222: `gpt-4-turbo` → `gpt-4o`
  ```
  models: ["claude-3-haiku", "gpt-4-turbo", "deepseek-v3"]
  ```
- Line 36: `gpt-4-turbo` → `gpt-4o`
  ```
  - gpt-4-turbo
  ```
- Line 222: `gpt-4-turbo` → `gpt-4o`
  ```
  models: ["claude-3-haiku", "gpt-4-turbo", "deepseek-v3"]
  ```
- Line 216: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  models: ["gpt-4o", "claude-3-opus", "gemini-1.5-pro"]
  ```
- Line 277: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  model: "gemini-1.5-pro"
  ```
- Line 335: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  market_analysis: "gemini-1.5-pro"
  ```
- Line 216: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  models: ["gpt-4o", "claude-3-opus", "gemini-1.5-pro"]
  ```
- Line 277: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  model: "gemini-1.5-pro"
  ```
- Line 335: `gemini-1.5-pro` → `gemini-2.0-flash-exp`
  ```
  market_analysis: "gemini-1.5-pro"
  ```
