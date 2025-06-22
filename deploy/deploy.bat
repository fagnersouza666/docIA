@echo off
REM DocIA - Enterprise Kubernetes Deployment Script
REM Version: 2.3.0
REM Description: Production-ready deployment with best practices

setlocal EnableDelayedExpansion

echo =========================================
echo    DocIA - Enterprise K8s Deployment
echo =========================================
echo Version: 2.3.0
echo Namespace: doc-ia
echo =========================================
echo.

REM Check prerequisites
echo [1/8] Checking prerequisites...
kubectl version --client >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ kubectl not found. Install: winget install Kubernetes.kubectl
    pause
    exit /b 1
)

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker not found. Install Docker Desktop
    pause
    exit /b 1
)

kubectl cluster-info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ No Kubernetes cluster available
    echo    Run: setup-remote-k8s.bat
    pause
    exit /b 1
)

for /f "delims=" %%i in ('kubectl config current-context') do set CURRENT_CONTEXT=%%i
echo ✅ Connected to cluster: %CURRENT_CONTEXT%
echo.

REM Image configuration
echo [2/8] Image configuration...
set /p IMAGE_CHOICE="Choose image option (1=Local build, 2=Remote registry, 3=Skip): "

if "%IMAGE_CHOICE%"=="1" (
    echo Building Docker image...
    docker build -t doc-ia:v2.3.0 -f Dockerfile.smart .
    if !errorlevel! neq 0 (
        echo ❌ Failed to build Docker image
        pause
        exit /b 1
    )
    set IMAGE_NAME=doc-ia:v2.3.0
) else if "%IMAGE_CHOICE%"=="2" (
    set /p IMAGE_NAME="Enter full image name (registry/repo:tag): "
) else (
    set IMAGE_NAME=doc-ia:latest
)

echo ✅ Using image: %IMAGE_NAME%
echo.

REM Environment configuration
echo [3/8] Environment configuration...
set /p ENV_TYPE="Environment type (1=Development, 2=Staging, 3=Production): "

if "%ENV_TYPE%"=="1" (
    set REPLICAS=1
    set RESOURCES_REQUEST_CPU=500m
    set RESOURCES_REQUEST_MEM=1Gi
    set RESOURCES_LIMIT_CPU=1000m
    set RESOURCES_LIMIT_MEM=2Gi
    set STORAGE_CLASS=standard
    echo 🔧 Development configuration applied
) else if "%ENV_TYPE%"=="2" (
    set REPLICAS=2
    set RESOURCES_REQUEST_CPU=1000m
    set RESOURCES_REQUEST_MEM=2Gi
    set RESOURCES_LIMIT_CPU=2000m
    set RESOURCES_LIMIT_MEM=4Gi
    set STORAGE_CLASS=fast-ssd
    echo 🔧 Staging configuration applied
) else (
    set REPLICAS=3
    set RESOURCES_REQUEST_CPU=2000m
    set RESOURCES_REQUEST_MEM=4Gi
    set RESOURCES_LIMIT_CPU=4000m
    set RESOURCES_LIMIT_MEM=8Gi
    set STORAGE_CLASS=fast-ssd
    echo 🔧 Production configuration applied
)
echo.

REM Update manifests with configuration
echo [4/8] Updating manifests...
powershell -Command "(Get-Content k8s/deployment.yaml) -replace 'image: doc-ia:latest', 'image: %IMAGE_NAME%' -replace 'replicas: 2', 'replicas: %REPLICAS%' -replace 'cpu: \"1000m\"', 'cpu: \"%RESOURCES_REQUEST_CPU%\"' -replace 'memory: \"2Gi\"', 'memory: \"%RESOURCES_REQUEST_MEM%\"' -replace 'cpu: \"2000m\"', 'cpu: \"%RESOURCES_LIMIT_CPU%\"' -replace 'memory: \"4Gi\"', 'memory: \"%RESOURCES_LIMIT_MEM%\"' | Set-Content k8s/deployment-temp.yaml"
powershell -Command "(Get-Content k8s/pvc.yaml) -replace 'storageClassName: fast-ssd', 'storageClassName: %STORAGE_CLASS%' -replace 'storageClassName: standard', 'storageClassName: %STORAGE_CLASS%' | Set-Content k8s/pvc-temp.yaml"
echo ✅ Manifests updated with environment configuration
echo.

REM Deploy core resources
echo [5/8] Deploying core resources...

echo Applying namespace...
kubectl apply -f k8s/namespace.yaml
if %errorlevel% neq 0 goto :deploy_error

echo Applying RBAC...
kubectl apply -f k8s/serviceaccount.yaml
if %errorlevel% neq 0 goto :deploy_error

echo Applying secrets...
kubectl apply -f k8s/secrets.yaml
if %errorlevel% neq 0 goto :deploy_error

echo Applying configuration...
kubectl apply -f k8s/configmap.yaml
if %errorlevel% neq 0 goto :deploy_error

echo Applying storage...
kubectl apply -f k8s/pvc-temp.yaml
if %errorlevel% neq 0 goto :deploy_error

echo ✅ Core resources deployed
echo.

REM Deploy application
echo [6/8] Deploying application...

echo Deploying application...
kubectl apply -f k8s/deployment-temp.yaml
if %errorlevel% neq 0 goto :deploy_error

echo Creating services...
kubectl apply -f k8s/service.yaml
if %errorlevel% neq 0 goto :deploy_error

echo ✅ Application deployed
echo.

REM Deploy optional resources
echo [7/8] Deploying optional resources...

echo Configuring autoscaler...
kubectl apply -f k8s/hpa.yaml >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ HPA configured
) else (
    echo ⚠️ HPA not available (metrics server required)
)

echo Configuring ingress...
kubectl apply -f k8s/ingress.yaml >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ingress configured
) else (
    echo ⚠️ Ingress not available (ingress controller required)
)

echo Configuring network policies...
kubectl apply -f k8s/networkpolicy.yaml >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Network policies configured
) else (
    echo ⚠️ Network policies not available (CNI support required)
)

echo Configuring monitoring...
kubectl apply -f k8s/monitoring.yaml >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Monitoring configured
) else (
    echo ⚠️ Monitoring not available (Prometheus operator required)
)
echo.

REM Wait for deployment
echo [8/8] Waiting for deployment to be ready...
echo This may take a few minutes...
kubectl wait --for=condition=available --timeout=600s deployment/doc-ia-deployment -n doc-ia
if %errorlevel% neq 0 (
    echo ⚠️ Deployment timeout. Checking status...
    kubectl get pods -n doc-ia
    echo.
    echo Check logs with: kubectl logs -n doc-ia deployment/doc-ia-deployment
    pause
)

echo ✅ Deployment ready!
echo.

REM Show deployment information
echo =========================================
echo ✅ DEPLOYMENT SUCCESSFUL!
echo =========================================
echo.
echo 📊 Deployment Information:
echo • Namespace: doc-ia
echo • Image: %IMAGE_NAME%
echo • Replicas: %REPLICAS%
echo • Environment: %ENV_TYPE%
echo • Cluster: %CURRENT_CONTEXT%
echo.

echo 📋 Access Information:
kubectl get service doc-ia-nodeport -n doc-ia -o custom-columns="TYPE:.spec.type,PORT:.spec.ports[0].nodePort" --no-headers 2>nul
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('kubectl get service doc-ia-nodeport -n doc-ia -o custom-columns="TYPE:.spec.type,PORT:.spec.ports[0].nodePort" --no-headers') do (
        echo • NodePort: http://localhost:%%i
        kubectl get nodes -o custom-columns="IP:.status.addresses[?(@.type==\"InternalIP\")].address" --no-headers | findstr /r "^[0-9]" | head -3 | for /f %%j in ('more') do (
            echo • Node Access: http://%%j:%%i
        )
    )
)

kubectl get ingress doc-ia-ingress -n doc-ia -o custom-columns="HOSTS:.spec.rules[*].host" --no-headers 2>nul | findstr /r "." >nul
if %errorlevel% equ 0 (
    echo • Ingress Hosts:
    for /f "delims=" %%i in ('kubectl get ingress doc-ia-ingress -n doc-ia -o custom-columns="HOSTS:.spec.rules[*].host" --no-headers') do (
        echo   - https://%%i
    )
)

echo.
echo 🔧 Management Commands:
echo • View pods:      kubectl get pods -n doc-ia
echo • View logs:      kubectl logs -n doc-ia deployment/doc-ia-deployment -f
echo • Scale app:      kubectl scale deployment doc-ia-deployment --replicas=N -n doc-ia
echo • Delete app:     kubectl delete namespace doc-ia
echo • Update app:     kubectl rollout restart deployment/doc-ia-deployment -n doc-ia
echo.

REM Cleanup temporary files
del k8s\deployment-temp.yaml >nul 2>&1
del k8s\pvc-temp.yaml >nul 2>&1

echo Deploy completed successfully!
echo.
pause
exit /b 0

:deploy_error
echo ❌ Deployment failed!
echo Check the error above and verify cluster connectivity.
del k8s\deployment-temp.yaml >nul 2>&1
del k8s\pvc-temp.yaml >nul 2>&1
pause
exit /b 1 