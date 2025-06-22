#!/bin/bash
# DocIA - Enterprise Kubernetes Deployment Script
# Version: 2.3.0
# Description: Production-ready deployment with best practices

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Log functions
log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

# Cleanup function
cleanup() {
    rm -f k8s/deployment-temp.yaml k8s/pvc-temp.yaml
}
trap cleanup EXIT

echo "========================================="
echo "   DocIA - Enterprise K8s Deployment"
echo "========================================="
echo "Version: 2.3.0"
echo "Namespace: doc-ia"
echo "========================================="
echo

# Check prerequisites
log_info "[1/8] Checking prerequisites..."

if ! command -v kubectl &> /dev/null; then
    log_error "kubectl not found. Install: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    log_error "Docker not found. Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! kubectl cluster-info &> /dev/null; then
    log_error "No Kubernetes cluster available"
    log_info "Run: ./setup-remote.sh"
    exit 1
fi

CURRENT_CONTEXT=$(kubectl config current-context)
log_success "Connected to cluster: $CURRENT_CONTEXT"
echo

# Image configuration
log_info "[2/8] Image configuration..."
echo "Choose image option:"
echo "1) Local build"
echo "2) Remote registry"
echo "3) Skip (use existing)"
read -p "Enter choice [1-3]: " IMAGE_CHOICE

case $IMAGE_CHOICE in
    1)
        log_info "Building Docker image..."
        if docker build -t doc-ia:v2.3.0 -f Dockerfile.smart .; then
            IMAGE_NAME="doc-ia:v2.3.0"
        else
            log_error "Failed to build Docker image"
            exit 1
        fi
        ;;
    2)
        read -p "Enter full image name (registry/repo:tag): " IMAGE_NAME
        ;;
    *)
        IMAGE_NAME="doc-ia:latest"
        ;;
esac

log_success "Using image: $IMAGE_NAME"
echo

# Environment configuration
log_info "[3/8] Environment configuration..."
echo "Environment type:"
echo "1) Development"
echo "2) Staging"
echo "3) Production"
read -p "Enter choice [1-3]: " ENV_TYPE

case $ENV_TYPE in
    1)
        REPLICAS=1
        RESOURCES_REQUEST_CPU="500m"
        RESOURCES_REQUEST_MEM="1Gi"
        RESOURCES_LIMIT_CPU="1000m"
        RESOURCES_LIMIT_MEM="2Gi"
        STORAGE_CLASS="standard"
        log_success "Development configuration applied"
        ;;
    2)
        REPLICAS=2
        RESOURCES_REQUEST_CPU="1000m"
        RESOURCES_REQUEST_MEM="2Gi"
        RESOURCES_LIMIT_CPU="2000m"
        RESOURCES_LIMIT_MEM="4Gi"
        STORAGE_CLASS="fast-ssd"
        log_success "Staging configuration applied"
        ;;
    *)
        REPLICAS=3
        RESOURCES_REQUEST_CPU="2000m"
        RESOURCES_REQUEST_MEM="4Gi"
        RESOURCES_LIMIT_CPU="4000m"
        RESOURCES_LIMIT_MEM="8Gi"
        STORAGE_CLASS="fast-ssd"
        log_success "Production configuration applied"
        ;;
esac
echo

# Update manifests with configuration
log_info "[4/8] Updating manifests..."
sed "s|image: doc-ia:latest|image: $IMAGE_NAME|g; s|replicas: 2|replicas: $REPLICAS|g; s|cpu: \"1000m\"|cpu: \"$RESOURCES_REQUEST_CPU\"|g; s|memory: \"2Gi\"|memory: \"$RESOURCES_REQUEST_MEM\"|g; s|cpu: \"2000m\"|cpu: \"$RESOURCES_LIMIT_CPU\"|g; s|memory: \"4Gi\"|memory: \"$RESOURCES_LIMIT_MEM\"|g" k8s/deployment.yaml > k8s/deployment-temp.yaml

sed "s|storageClassName: fast-ssd|storageClassName: $STORAGE_CLASS|g; s|storageClassName: standard|storageClassName: $STORAGE_CLASS|g" k8s/pvc.yaml > k8s/pvc-temp.yaml

log_success "Manifests updated with environment configuration"
echo

# Deploy core resources
log_info "[5/8] Deploying core resources..."

log_info "Applying namespace..."
kubectl apply -f k8s/namespace.yaml

log_info "Applying RBAC..."
kubectl apply -f k8s/serviceaccount.yaml

log_info "Applying secrets..."
kubectl apply -f k8s/secrets.yaml

log_info "Applying configuration..."
kubectl apply -f k8s/configmap.yaml

log_info "Applying storage..."
kubectl apply -f k8s/pvc-temp.yaml

log_success "Core resources deployed"
echo

# Deploy application
log_info "[6/8] Deploying application..."

log_info "Deploying application..."
kubectl apply -f k8s/deployment-temp.yaml

log_info "Creating services..."
kubectl apply -f k8s/service.yaml

log_success "Application deployed"
echo

# Deploy optional resources
log_info "[7/8] Deploying optional resources..."

log_info "Configuring autoscaler..."
if kubectl apply -f k8s/hpa.yaml &> /dev/null; then
    log_success "HPA configured"
else
    log_warning "HPA not available (metrics server required)"
fi

log_info "Configuring ingress..."
if kubectl apply -f k8s/ingress.yaml &> /dev/null; then
    log_success "Ingress configured"
else
    log_warning "Ingress not available (ingress controller required)"
fi

log_info "Configuring network policies..."
if kubectl apply -f k8s/networkpolicy.yaml &> /dev/null; then
    log_success "Network policies configured"
else
    log_warning "Network policies not available (CNI support required)"
fi

log_info "Configuring monitoring..."
if kubectl apply -f k8s/monitoring.yaml &> /dev/null; then
    log_success "Monitoring configured"
else
    log_warning "Monitoring not available (Prometheus operator required)"
fi
echo

# Wait for deployment
log_info "[8/8] Waiting for deployment to be ready..."
log_info "This may take a few minutes..."

if kubectl wait --for=condition=available --timeout=600s deployment/doc-ia-deployment -n doc-ia; then
    log_success "Deployment ready!"
else
    log_warning "Deployment timeout. Checking status..."
    kubectl get pods -n doc-ia
    echo
    log_info "Check logs with: kubectl logs -n doc-ia deployment/doc-ia-deployment"
fi
echo

# Show deployment information
echo "========================================="
log_success "DEPLOYMENT SUCCESSFUL!"
echo "========================================="
echo

echo "📊 Deployment Information:"
echo "• Namespace: doc-ia"
echo "• Image: $IMAGE_NAME"
echo "• Replicas: $REPLICAS"
echo "• Environment: $ENV_TYPE"
echo "• Cluster: $CURRENT_CONTEXT"
echo

echo "📋 Access Information:"
if kubectl get service doc-ia-nodeport -n doc-ia &> /dev/null; then
    NODE_PORT=$(kubectl get service doc-ia-nodeport -n doc-ia -o jsonpath='{.spec.ports[0].nodePort}')
    echo "• NodePort: http://localhost:$NODE_PORT"
    
    # Get node IPs
    NODE_IPS=$(kubectl get nodes -o jsonpath='{.items[*].status.addresses[?(@.type=="InternalIP")].address}' | head -3)
    for ip in $NODE_IPS; do
        echo "• Node Access: http://$ip:$NODE_PORT"
    done
fi

if kubectl get ingress doc-ia-ingress -n doc-ia &> /dev/null; then
    echo "• Ingress Hosts:"
    kubectl get ingress doc-ia-ingress -n doc-ia -o jsonpath='{.spec.rules[*].host}' | tr ' ' '\n' | while read host; do
        echo "  - https://$host"
    done
fi

echo
echo "🔧 Management Commands:"
echo "• View pods:      kubectl get pods -n doc-ia"
echo "• View logs:      kubectl logs -n doc-ia deployment/doc-ia-deployment -f"
echo "• Scale app:      kubectl scale deployment doc-ia-deployment --replicas=N -n doc-ia"
echo "• Delete app:     kubectl delete namespace doc-ia"
echo "• Update app:     kubectl rollout restart deployment/doc-ia-deployment -n doc-ia"
echo

log_success "Deploy completed successfully!" 