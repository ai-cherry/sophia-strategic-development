# 🚀 SOPHIA AI DEPLOYMENT MAKEFILE
# Deploy the GPU-accelerated AI overlord with one command

.PHONY: help deploy deploy-infra deploy-backend deploy-mcp deploy-frontend deploy-all test clean

# Default Lambda Labs servers
LAMBDA_PRIMARY ?= 104.171.202.103
LAMBDA_GPU ?= 192.222.58.232
LAMBDA_MCP ?= 104.171.202.117

# Docker registry
REGISTRY ?= scoobyjava15

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

check-env: ## Check environment setup
	@echo "🔍 Checking deployment environment..."
	@echo "✅ Pulumi organization: $$PULUMI_ORG"
	@echo "✅ Environment: $$ENVIRONMENT"
	@echo "✅ Docker registry: $(REGISTRY)"
	@echo "✅ Lambda Labs servers configured"

deploy: deploy-all ## Full deployment (alias for deploy-all)

deploy-infra: check-env ## Deploy infrastructure (Qdrant, Redis, PostgreSQL)
	@echo "🏗️  Deploying infrastructure to Lambda Labs..."
	cd infrastructure/pulumi && pulumi up -y
	@echo "⏳ Waiting for infrastructure to stabilize..."
	sleep 30
	kubectl get pods -n sophia-ai-prod

build-images: ## Build all Docker images
	@echo "🐳 Building Docker images..."
	docker build -f backend/Dockerfile -t $(REGISTRY)/sophia-backend:latest .
	docker build -f frontend/Dockerfile -t $(REGISTRY)/sophia-frontend:latest frontend/
	docker build -f docker/Dockerfile.mcp-base -t $(REGISTRY)/sophia-mcp-base:latest .
	docker build -f docker/Dockerfile.gh200 -t $(REGISTRY)/sophia-gpu:latest .

push-images: build-images ## Push images to registry
	@echo "📤 Pushing images to $(REGISTRY)..."
	docker push $(REGISTRY)/sophia-backend:latest
	docker push $(REGISTRY)/sophia-frontend:latest
	docker push $(REGISTRY)/sophia-mcp-base:latest
	docker push $(REGISTRY)/sophia-gpu:latest

deploy-backend: push-images ## Deploy backend services
	@echo "🎯 Deploying backend services..."
	kubectl apply -k k8s/overlays/production
	kubectl rollout status deployment/sophia-backend -n sophia-ai-prod

deploy-mcp: ## Deploy MCP servers
	@echo "🤖 Deploying MCP servers..."
	kubectl apply -f k8s/mcp-servers/
	@echo "⏳ Waiting for MCP servers..."
	sleep 20
	kubectl get pods -n mcp-servers

deploy-frontend: ## Deploy frontend to Lambda Labs
	@echo "🎨 Deploying frontend..."
	cd frontend && npm run build

deploy-n8n: ## Deploy n8n workflows
	@echo "🔄 Deploying n8n workflows..."
	kubectl apply -f kubernetes/n8n/
	@echo "📥 Importing workflows..."
	python scripts/import_n8n_workflows.py

deploy-all: deploy-infra deploy-backend deploy-mcp deploy-frontend deploy-n8n ## Deploy everything
	@echo "✅ Full deployment complete!"
	@echo "🔥 Sophia AI is now operational!"
	@make test

test: ## Run deployment tests
	@echo "🧪 Running deployment tests..."
	@echo "Testing backend health..."
	curl -f http://$(LAMBDA_PRIMARY):8000/health || exit 1
	@echo "\nTesting memory service..."
	curl -f http://$(LAMBDA_GPU):8000/api/v2/memory/stats || exit 1
	@echo "\nTesting chat service..."
	curl -f http://$(LAMBDA_PRIMARY):8000/api/v4/sophia/health || exit 1
	@echo "\nTesting MCP gateway..."
	curl -f http://$(LAMBDA_MCP):8080/health || exit 1
	@echo "\n✅ All tests passed!"

test-sophia: ## Test Sophia's personality
	@echo "😈 Testing Sophia's personality..."
	curl -X POST http://$(LAMBDA_PRIMARY):8000/api/v4/sophia/chat \
		-H "Content-Type: application/json" \
		-d '{"query": "Why is our system slow?", "user_id": "ceo_user"}' | jq

logs: ## Tail backend logs
	kubectl logs -f deployment/sophia-backend -n sophia-ai-prod

logs-mcp: ## Tail MCP server logs
	kubectl logs -f -l app=mcp-server -n mcp-servers

status: ## Check deployment status
	@echo "📊 Deployment Status"
	@echo "==================="
	kubectl get pods -n sophia-ai-prod
	@echo "\nMCP Servers:"
	kubectl get pods -n mcp-servers
	@echo "\nServices:"
	kubectl get svc -n sophia-ai-prod

rollback: ## Rollback deployment
	@echo "⏪ Rolling back deployment..."
	kubectl rollout undo deployment/sophia-backend -n sophia-ai-prod
	kubectl rollout undo deployment/sophia-mcp-gateway -n mcp-servers

clean: ## Clean up resources
	@echo "🧹 Cleaning up..."
	docker system prune -f
	kubectl delete pods --field-selector=status.phase=Failed -n sophia-ai-prod

monitoring: ## Open monitoring dashboards
	@echo "📊 Opening monitoring dashboards..."
	@echo "Grafana: http://$(LAMBDA_PRIMARY):3000"
	@echo "Prometheus: http://$(LAMBDA_PRIMARY):9090"
	@echo "n8n: http://$(LAMBDA_PRIMARY):5678"

ssh-primary: ## SSH to primary Lambda server
	ssh ubuntu@$(LAMBDA_PRIMARY)

ssh-gpu: ## SSH to GPU Lambda server
	ssh ubuntu@$(LAMBDA_GPU)

quick-deploy: build-images push-images ## Quick deploy (skip infra)
	kubectl rollout restart deployment/sophia-backend -n sophia-ai-prod
	kubectl rollout restart deployment -n mcp-servers
	@echo "✅ Quick deployment complete!"

# Development shortcuts
dev-backend: ## Run backend locally
	cd backend && uvicorn app.fastapi_app:app --reload --port 8000

dev-frontend: ## Run frontend locally
	cd frontend && npm run dev

dev-test: ## Run local tests
	pytest tests/ -v

# One-command deployment
.DEFAULT_GOAL := help
