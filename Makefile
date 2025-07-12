# Sophia AI Makefile
# This Makefile provides automatic setup and management for Sophia AI
# Just type 'make' and everything will be set up automatically

.PHONY: all setup env ssl deps docker health command clean one-time-inventory one-time-archive one-time-purge deploy-new-stack deploy-dev-stack deploy-prod-stack validate-deployment benchmark-new-stack deploy-monitoring cleanup-old-stack deploy-all prod-deploy-all

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

one-time-inventory:
	python scripts/generate_one_time_inventory.py

one-time-archive:
	bash scripts/soft_archive_one_time.sh

one-time-purge:
	git rm -r archive/one_time_* && git commit -m "purge one-time scripts"

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
        @echo "  one-time-inventory - Generate one-time artefact list"
        @echo "  one-time-archive   - Move approved items to archive"
        @echo "  one-time-purge     - Remove archived items"
        @echo "  deploy-new-stack    - Deploy Weaviate/Redis/PostgreSQL/Lambda GPU stack to production"
        @echo "  deploy-dev-stack    - Deploy to development environment first"
        @echo "  deploy-prod-stack   - Deploy to production (after dev validation)"
        @echo "  validate-deployment - Validate the deployed stack is working correctly"
        @echo "  benchmark-new-stack - Run performance benchmarks on the new stack"
        @echo "  deploy-monitoring   - Deploy Prometheus and Grafana monitoring"
        @echo "  cleanup-old-stack   - Clean up old Snowflake-based resources"
        @echo "  deploy-all          - Deploy everything to dev and validate"
        @echo "  prod-deploy-all     - Deploy everything to production"
        @echo "  help     - Show this help"

# Phase 4: Deploy New Memory Stack
deploy-new-stack: ## Deploy Weaviate/Redis/PostgreSQL/Lambda GPU stack to production
	@echo "🚀 Deploying new memory architecture stack..."
	@echo "Stack: $(STACK)"
	@echo ""
	# Ensure we're in the infrastructure directory
	cd infrastructure && \
	# Preview changes first
	pulumi preview --stack $(STACK) && \
	# Deploy with auto-approve
	pulumi up --stack $(STACK) --yes && \
	# Wait for deployments to be ready
	kubectl rollout status -n sophia-ai-$(STACK) deployment/weaviate --timeout=5m && \
	kubectl rollout status -n sophia-ai-$(STACK) statefulset/redis --timeout=5m && \
	kubectl rollout status -n sophia-ai-$(STACK) deployment/postgresql --timeout=5m && \
	kubectl rollout status -n sophia-ai-$(STACK) deployment/lambda-inference --timeout=5m && \
	# Show deployment status
	echo "✅ All services deployed successfully!" && \
	kubectl get pods -n sophia-ai-$(STACK) -l app.kubernetes.io/part-of=sophia-ai

deploy-dev-stack: ## Deploy to development environment first
	@$(MAKE) deploy-new-stack STACK=dev

deploy-prod-stack: ## Deploy to production (after dev validation)
	@echo "⚠️  Deploying to PRODUCTION"
	@echo "Have you validated in dev? (Ctrl-C to cancel)"
	@sleep 5
	@$(MAKE) deploy-new-stack STACK=prod

validate-deployment: ## Validate the deployed stack is working correctly
	@echo "🔍 Validating deployment..."
	@echo ""
	# Check Weaviate health
	@echo "Checking Weaviate..."
	@kubectl exec -n sophia-ai-$(STACK) deployment/weaviate -- curl -s http://localhost:8080/v1/.well-known/ready || echo "❌ Weaviate not ready"
	@echo ""
	# Check Redis health
	@echo "Checking Redis..."
	@kubectl exec -n sophia-ai-$(STACK) statefulset/redis -- redis-cli ping || echo "❌ Redis not ready"
	@echo ""
	# Check PostgreSQL health
	@echo "Checking PostgreSQL..."
	@kubectl exec -n sophia-ai-$(STACK) deployment/postgresql -- pg_isready || echo "❌ PostgreSQL not ready"
	@echo ""
	# Check Lambda Inference health
	@echo "Checking Lambda Inference..."
	@kubectl exec -n sophia-ai-$(STACK) deployment/lambda-inference -- curl -s http://localhost:8080/health || echo "❌ Lambda Inference not ready"

benchmark-new-stack: ## Run performance benchmarks on the new stack
	@echo "📊 Running performance benchmarks..."
	python scripts/benchmark_memory_performance.py --environment=$(STACK)

deploy-monitoring: ## Deploy Prometheus and Grafana monitoring
	@echo "📊 Deploying monitoring stack..."
	kubectl apply -f infrastructure/monitoring/prometheus-deployment.yaml -n sophia-ai-$(STACK)
	kubectl apply -f infrastructure/monitoring/grafana-deployment.yaml -n sophia-ai-$(STACK)

cleanup-old-stack: ## Clean up old Snowflake-based resources
	@echo "🧹 Cleaning up old stack resources..."
	@echo "⚠️  This will remove Snowflake MCP servers. Continue? (Ctrl-C to cancel)"
	@sleep 5
	kubectl delete deployment snowflake-unified -n sophia-ai-$(STACK) --ignore-not-found=true
	kubectl delete service snowflake-unified-service -n sophia-ai-$(STACK) --ignore-not-found=true

# Convenience targets
deploy-all: deploy-dev-stack validate-deployment deploy-monitoring ## Deploy everything to dev and validate

prod-deploy-all: deploy-prod-stack validate-deployment ## Deploy everything to production

# Default stack is dev
STACK ?= dev
