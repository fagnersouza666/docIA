# DocIA - Enterprise Kubernetes Architecture

## 🏗️ Visão Geral da Arquitetura

O DocIA v2.3.0 Enterprise Edition implementa uma arquitetura Kubernetes robusta seguindo as melhores práticas da indústria para aplicações empresariais.

## 🔒 Segurança Enterprise

### RBAC (Role-Based Access Control)

```yaml
# Service Account com permissions mínimas
apiVersion: v1
kind: ServiceAccount
metadata:
  name: doc-ia-service-account
  namespace: doc-ia
automountServiceAccountToken: false
```

### Security Context

- **Execução não-root**: UID 1000
- **Read-only filesystem**: Parcial (Ollama requer write)
- **Capabilities**: DROP ALL + NET_BIND_SERVICE
- **Seccomp Profile**: RuntimeDefault

### Network Policies

- **Default Deny All**: Política padrão de negação
- **Selective Allow**: Apenas tráfego necessário
- **Ingress/Egress Control**: Controle granular de rede

## 📊 Observabilidade

### Health Checks Avançados

#### Liveness Probe

- **Endpoint**: `/health`
- **Frequência**: 30s
- **Timeout**: 10s
- **Verifica**: Indexador funcionando, Ollama status

#### Readiness Probe

- **Endpoint**: `/ready`
- **Frequência**: 10s
- **Timeout**: 5s
- **Verifica**: Documentos indexados, pronto para tráfego

#### Startup Probe

- **Endpoint**: `/startup`
- **Frequência**: 10s
- **Timeout**: 5s
- **Verifica**: Inicialização completa

### Prometheus Integration

```yaml
# ServiceMonitor para coleta de métricas
spec:
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### Grafana Dashboard

- **Request Rate**: Taxa de requisições
- **Response Time**: Tempo de resposta (P95)
- **Error Rate**: Taxa de erros
- **Document Count**: Número de documentos indexados

## ⚡ Escalabilidade

### Horizontal Pod Autoscaler (HPA)

```yaml
spec:
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        averageUtilization: 80
```

### Resource Management

| Ambiente | CPU Request | CPU Limit | Memory Request | Memory Limit |
|----------|-------------|-----------|----------------|--------------|
| Dev      | 500m        | 1000m     | 1Gi           | 2Gi          |
| Staging  | 1000m       | 2000m     | 2Gi           | 4Gi          |
| Prod     | 2000m       | 4000m     | 4Gi           | 8Gi          |

### Pod Anti-Affinity

```yaml
affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        topologyKey: kubernetes.io/hostname
```

## 💾 Storage Strategy

### Persistent Volumes

1. **Documents Volume**: 20Gi (fast-ssd)
   - Backup: Diário às 2h
   - Retenção: 30 dias

2. **Cache Volume**: 10Gi (standard)
   - Backup: Não (pode ser regenerado)
   - Retenção: N/A

3. **Logs Volume**: 5Gi (standard)
   - Backup: Semanal
   - Retenção: 30 dias

### Storage Classes

- **fast-ssd**: Para produção (documents)
- **standard**: Para desenvolvimento/cache

## 🌐 Rede

### Services

1. **ClusterIP**: Comunicação interna
2. **NodePort**: Acesso externo (30500)
3. **Headless**: Service discovery

### Ingress

```yaml
annotations:
  nginx.ingress.kubernetes.io/ssl-redirect: "true"
  nginx.ingress.kubernetes.io/rate-limit-connections: "10"
  nginx.ingress.kubernetes.io/rate-limit-rps: "20"
```

### TLS/SSL

- **cert-manager**: Certificados automáticos
- **Let's Encrypt**: CA de produção
- **HTTPS Redirect**: Forçado

## 🛠️ DevOps Tooling

### Makefile Commands

```bash
# Deployment
make deploy          # Deploy completo
make quick-deploy    # Deploy rápido
make update         # Rolling update

# Monitoring
make status         # Status do sistema
make health         # Health check
make logs           # Ver logs

# Scaling
make scale REPLICAS=5  # Escalar aplicação

# Maintenance
make backup         # Backup de dados
make clean          # Limpeza
make delete         # Deletar tudo
```

### Interactive Deploy Scripts

#### Windows (deploy.bat)

- Interface interativa
- Seleção de ambiente
- Configuração automática de recursos
- Verificação de pré-requisitos

#### Linux/Mac (deploy.sh)

- Cores e emojis
- Log estruturado
- Validação de cluster
- Cleanup automático

## 🔄 Multi-Environment

### Environment Configuration

```bash
# Development
REPLICAS=1
RESOURCES_REQUEST_CPU=500m
RESOURCES_REQUEST_MEM=1Gi
STORAGE_CLASS=standard

# Staging
REPLICAS=2
RESOURCES_REQUEST_CPU=1000m
RESOURCES_REQUEST_MEM=2Gi
STORAGE_CLASS=fast-ssd

# Production
REPLICAS=3
RESOURCES_REQUEST_CPU=2000m
RESOURCES_REQUEST_MEM=4Gi
STORAGE_CLASS=fast-ssd
```

## 📈 Monitoring & Alerting

### Key Metrics

- **Application Metrics**: Request rate, response time, errors
- **System Metrics**: CPU, memory, disk usage
- **Business Metrics**: Documents indexed, search queries
- **Infrastructure Metrics**: Pod restarts, network traffic

### Alerting Rules

- **High Error Rate**: > 5% por 5 minutos
- **High Response Time**: P95 > 2s por 5 minutos
- **Pod Restart**: > 3 restarts em 10 minutos
- **Resource Usage**: CPU > 80% ou Memory > 90%

## 🔧 Troubleshooting

### Common Issues

#### Pod Not Starting

```bash
# Check events
make events

# Describe pod
make describe

# Check logs
make logs-tail
```

#### Network Issues

```bash
# Test connectivity
make network-test

# Check network policies
kubectl get networkpolicy -n doc-ia
```

#### Storage Issues

```bash
# Check PVC status
kubectl get pvc -n doc-ia

# Check storage class
kubectl get storageclass
```

### Debug Commands

```bash
# Shell into pod
make dev-shell

# Port forward for local access
make port-forward

# Monitor resources
make monitor
```

## 🚀 Future Roadmap

### Planejado para v2.4.0

- **Service Mesh**: Istio integration
- **Distributed Tracing**: Jaeger implementation
- **Advanced Monitoring**: Custom metrics
- **Blue/Green Deployments**: Zero-downtime strategy

### Planejado para v2.5.0

- **Multi-cluster**: Deploy em múltiplos clusters
- **GitOps**: ArgoCD integration
- **Policy as Code**: OPA Gatekeeper
- **Cost Optimization**: Resource recommendations

## 📋 Compliance & Standards

### Security Standards

- **CIS Kubernetes Benchmark**: Conformidade
- **NSA/CISA Hardening Guide**: Implementado
- **Pod Security Standards**: Restricted profile

### Observability Standards

- **OpenTelemetry**: Ready for implementation
- **Prometheus Best Practices**: Seguido
- **SLI/SLO Framework**: Definido

---

Esta arquitetura enterprise fornece uma base sólida para aplicações de produção, garantindo segurança, observabilidade, escalabilidade e facilidade de manutenção.
