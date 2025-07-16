# uv.lock - Simple Up-to-Date Example

```toml
# This is a minimal example of a uv.lock file for dependency governance.
# It includes pinned versions and groups as per project standards.

[package."fastapi"]
version = "0.111.0"
source = "pypi"
hashes = ["sha256:examplehashfastapi1234567890abcdef"]

[package."redis"]
version = "5.0.4"
source = "pypi"
hashes = ["sha256:examplehashredis1234567890abcdef"]

[package."qdrant-client"]
version = "3.10.0"
source = "pypi"
hashes = ["sha256:examplehashqdrant1234567890abcdef"]

[package."anthropic-mcp-python-sdk"]
version = "1.2.4"
source = "pypi"
hashes = ["sha256:examplehashanthropic1234567890abcdef"]

[package."openai"]
version = "1.30.0"
source = "pypi"
hashes = ["sha256:examplehashopenai1234567890abcdef"]

[package."anthropic"]
version = "0.25.6"
source = "pypi"
hashes = ["sha256:examplehashanthropiclib1234567890abcdef"]

[package."langchain"]
version = "0.2.0"
source = "pypi"
hashes = ["sha256:examplehashlangchain1234567890abcdef"]

[package."n8n-python-client"]
version = "0.2.0"
source = "pypi"
hashes = ["sha256:examplen8nclient1234567890abcdef"]

[package."temporal-sdk"]
version = "1.5.0"
source = "pypi"
hashes = ["sha256:examplehashtemporal1234567890abcdef"]

[package."pytest"]
version = "8.2.2"
source = "pypi"
hashes = ["sha256:examplehashpytest1234567890abcdef"]

[package."ruff"]
version = "0.4.4"
source = "pypi"
hashes = ["sha256:exampleruff1234567890abcdef"]

[package."mypy"]
version = "1.10.0"
source = "pypi"
hashes = ["sha256:examplehashmypy1234567890abcdef"]

[package."black"]
version = "24.4.0"
source = "pypi"
hashes = ["sha256:examplehashblack1234567890abcdef"]

[tool.uv.dependency-groups]
core = ["fastapi", "redis", "qdrant-client"]
mcp-servers = ["anthropic-mcp-python-sdk"]
ai-enhanced = ["openai", "anthropic", "langchain"]
automation = ["n8n-python-client", "temporal-sdk"]
dev = ["pytest", "ruff", "mypy", "black"]
