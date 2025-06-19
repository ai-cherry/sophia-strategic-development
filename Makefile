# Sophia AI Makefile
# This Makefile provides automatic setup and management for Sophia AI
# Just type 'make' and everything will be set up automatically

.PHONY: all setup env ssl deps docker health command clean

# Default target - runs everything
all: setup

# Setup everything automatically
setup: env ssl deps docker health command
	@echo "\n✅ Sophia AI setup complete! The system is now ready to use."

# Set up environment variables
env:
	@echo "\n🔧 Setting up environment variables..."
	@chmod +x secrets_manager.py || true
	@./secrets_manager.py import-from-env || true
	@./secrets_manager.py export-to-env || true
	@./secrets_manager.py validate || true

# Fix SSL certificate issues
ssl:
	@echo "\n🔧 Fixing SSL certificate issues..."
	@chmod +x fix_ssl_certificates.py || true
	@./fix_ssl_certificates.py || true
	@chmod +x run_with_ssl_fix.py || true

# Fix Python package dependencies
deps:
	@echo "\n🔧 Fixing Python package dependencies..."
	@chmod +x fix_dependencies.py || true
	@./fix_dependencies.py || true

# Fix Docker Compose and start MCP servers
docker:
	@echo "\n🔧 Starting MCP servers..."
	@chmod +x start_mcp_servers.py || true
	@./start_mcp_servers.py || true

# Run health check
health:
	@echo "\n🔧 Running health check..."
	@if [ -f "automated_health_check_fixed.py" ] && [ ! -f "automated_health_check.py" ]; then \
		cp automated_health_check_fixed.py automated_health_check.py; \
	fi
	@if [ -f "automated_health_check.py" ]; then \
		./run_with_ssl_fix.py automated_health_check.py || true; \
	else \
		echo "⚠️ automated_health_check.py not found. Skipping health check."; \
	fi

# Run command interface
command:
	@echo "\n🔧 Running command interface..."
	@if [ -f "unified_command_interface_fixed.py" ] && [ ! -f "unified_command_interface.py" ]; then \
		cp unified_command_interface_fixed.py unified_command_interface.py; \
	fi
	@if [ -f "unified_command_interface.py" ]; then \
		./run_with_ssl_fix.py unified_command_interface.py "check system status" || true; \
	else \
		echo "⚠️ unified_command_interface.py not found. Skipping command interface."; \
	fi

# Clean up
clean:
	@echo "\n🧹 Cleaning up..."
	@docker-compose -f docker-compose.mcp.yml down || true
	@echo "✅ Cleanup complete"

# Help
help:
	@echo "Sophia AI Makefile"
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  all      - Set up everything (default)"
	@echo "  setup    - Set up everything"
	@echo "  env      - Set up environment variables"
	@echo "  ssl      - Fix SSL certificate issues"
	@echo "  deps     - Fix Python package dependencies"
	@echo "  docker   - Fix Docker Compose and start MCP servers"
	@echo "  health   - Run health check"
	@echo "  command  - Run command interface"
	@echo "  clean    - Clean up"
	@echo "  help     - Show this help"
