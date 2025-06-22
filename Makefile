# DocIA - Makefile para facilitar gerenciamento
# Version: 2.3.0

.PHONY: help build deploy clean status logs scale delete update health

# Default target
help: ## Mostrar ajuda
	@echo "DocIA - Kubernetes Management"
	@echo "============================="
	@echo "Comandos disponíveis:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Construir imagem Docker
	docker build -t doc-ia:latest -f Dockerfile.smart .

deploy: ## Deploy completo no Kubernetes
	@echo "Iniciando deploy..."
	@if [ -f deploy/deploy.sh ]; then \
		bash deploy/deploy.sh; \
	else \
		deploy/deploy.bat; \
	fi

quick-deploy: ## Deploy rápido (sem build)
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/serviceaccount.yaml
	kubectl apply -f k8s/secrets.yaml
	kubectl apply -f k8s/configmap.yaml
	kubectl apply -f k8s/pvc.yaml
	kubectl apply -f k8s/deployment.yaml
	kubectl apply -f k8s/service.yaml
	kubectl apply -f k8s/ingress.yaml || true
	kubectl apply -f k8s/hpa.yaml || true

status: ## Verificar status do deployment
	@echo "Status do DocIA:"
	@echo "================"
	kubectl get all -n doc-ia
	@echo ""
	@echo "Volumes:"
	kubectl get pvc -n doc-ia
	@echo ""
	@echo "Ingress:"
	kubectl get ingress -n doc-ia || true

logs: ## Ver logs da aplicação
	kubectl logs -n doc-ia deployment/doc-ia-deployment -f

logs-tail: ## Ver últimas 100 linhas dos logs
	kubectl logs -n doc-ia deployment/doc-ia-deployment --tail=100

scale: ## Escalar aplicação (use REPLICAS=N)
	@if [ -z "$(REPLICAS)" ]; then \
		echo "Uso: make scale REPLICAS=3"; \
		exit 1; \
	fi
	kubectl scale deployment doc-ia-deployment --replicas=$(REPLICAS) -n doc-ia

delete: ## Deletar aplicação completa
	@echo "⚠️  Deletando DocIA..."
	@read -p "Tem certeza? (y/N): " confirm && [ "$$confirm" = "y" ]
	kubectl delete namespace doc-ia

clean: ## Limpar recursos temporários
	docker system prune -f
	kubectl delete pods --field-selector=status.phase=Succeeded -n doc-ia || true
	kubectl delete pods --field-selector=status.phase=Failed -n doc-ia || true

update: ## Atualizar aplicação (restart)
	kubectl rollout restart deployment/doc-ia-deployment -n doc-ia
	kubectl rollout status deployment/doc-ia-deployment -n doc-ia

health: ## Verificar saúde da aplicação
	@echo "Health Check:"
	@echo "============="
	@echo "Pods:"
	kubectl get pods -n doc-ia
	@echo ""
	@echo "Services:"
	kubectl get svc -n doc-ia
	@echo ""
	@echo "Endpoints:"
	kubectl get endpoints -n doc-ia
	@echo ""
	@echo "Events:"
	kubectl get events -n doc-ia --sort-by='.lastTimestamp' | tail -10

port-forward: ## Port forward para acesso local (porta 5000)
	@echo "Acessível em: http://localhost:5000"
	kubectl port-forward -n doc-ia svc/doc-ia-service 5000:5000

debug: ## Conectar ao pod para debug
	kubectl exec -it -n doc-ia deployment/doc-ia-deployment -- /bin/bash

test: ## Teste básico da aplicação
	@echo "Testando DocIA..."
	@if kubectl get svc doc-ia-nodeport -n doc-ia > /dev/null 2>&1; then \
		NODE_PORT=$$(kubectl get svc doc-ia-nodeport -n doc-ia -o jsonpath='{.spec.ports[0].nodePort}'); \
		echo "Testando NodePort: http://localhost:$$NODE_PORT"; \
		curl -s -o /dev/null -w "%{http_code}" http://localhost:$$NODE_PORT || echo "Serviço indisponível"; \
	else \
		echo "NodePort não configurado"; \
	fi

backup: ## Fazer backup dos dados
	@echo "Fazendo backup dos dados..."
	@mkdir -p backup
	kubectl get all -n doc-ia -o yaml > backup/doc-ia-resources-$$(date +%Y%m%d-%H%M%S).yaml
	@echo "Backup salvo em backup/"

restore: ## Restaurar dados do backup (use BACKUP_FILE=nome)
	@if [ -z "$(BACKUP_FILE)" ]; then \
		echo "Uso: make restore BACKUP_FILE=backup/doc-ia-resources-YYYYMMDD-HHMMSS.yaml"; \
		exit 1; \
	fi
	kubectl apply -f $(BACKUP_FILE)

# Comandos para desenvolvimento
dev-setup: ## Configurar ambiente de desenvolvimento
	@echo "Configurando ambiente de desenvolvimento..."
	kubectl config set-context --current --namespace=doc-ia

dev-logs: ## Logs em tempo real para desenvolvimento
	kubectl logs -n doc-ia deployment/doc-ia-deployment -f --tail=0

dev-shell: ## Shell interativo no container
	kubectl exec -it -n doc-ia deployment/doc-ia-deployment -- /bin/bash

# Comandos para monitoramento
monitor: ## Monitorar recursos
	watch kubectl top pods -n doc-ia

events: ## Mostrar eventos recentes
	kubectl get events -n doc-ia --sort-by='.lastTimestamp'

describe: ## Descrever deployment
	kubectl describe deployment doc-ia-deployment -n doc-ia

# Comandos para rede
network-test: ## Testar conectividade de rede
	kubectl run test-pod --image=busybox --rm -it --restart=Never -n doc-ia -- /bin/sh

network-policy: ## Aplicar políticas de rede
	kubectl apply -f k8s/networkpolicy.yaml 