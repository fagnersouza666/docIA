@echo off
REM Script para verificar e configurar pré-requisitos do Kubernetes

echo =========================================
echo     DocIA - Setup Kubernetes
echo =========================================
echo.

REM Verificar se Docker está rodando
echo [1/5] Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker não está instalado ou não está rodando
    echo    Instale o Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
    pause
    exit /b 1
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Desktop não está rodando
    echo    Inicie o Docker Desktop e tente novamente
    pause
    exit /b 1
)
echo ✅ Docker está funcionando

REM Verificar se kubectl está instalado
echo [2/5] Verificando kubectl...
kubectl version --client >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ kubectl não está instalado
    echo    Instale via: winget install -e --id Kubernetes.kubectl
    pause
    exit /b 1
)
echo ✅ kubectl está instalado

REM Verificar se há cluster disponível
echo [3/5] Verificando cluster Kubernetes...
kubectl cluster-info >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Nenhum cluster Kubernetes detectado
    echo.
    echo    OPÇÕES PARA CONFIGURAR KUBERNETES:
    echo.
    echo    📋 OPÇÃO 1: Docker Desktop (Recomendado)
    echo       1. Abra o Docker Desktop
    echo       2. Vá em Settings / Settings
    echo       3. Clique em "Kubernetes" no menu lateral
    echo       4. Marque "Enable Kubernetes"
    echo       5. Clique "Apply & Restart"
    echo       6. Aguarde alguns minutos para inicializar
    echo.
    echo    📋 OPÇÃO 2: minikube
    echo       1. Instale: winget install minikube
    echo       2. Execute: minikube start
    echo.
    echo    📋 OPÇÃO 3: kind
    echo       1. Instale: winget install Kubernetes.kind
    echo       2. Execute: kind create cluster
    echo.
    echo    Após configurar, execute novamente este script
    pause
    exit /b 1
)
echo ✅ Cluster Kubernetes detectado

REM Verificar contexto atual
echo [4/5] Verificando contexto...
kubectl config current-context >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Nenhum contexto ativo
    echo    Configure um contexto válido
    pause
    exit /b 1
)

set CURRENT_CONTEXT=
for /f "delims=" %%i in ('kubectl config current-context') do set CURRENT_CONTEXT=%%i
echo ✅ Contexto ativo: %CURRENT_CONTEXT%

REM Verificar se pode criar recursos
echo [5/5] Testando permissões...
kubectl auth can-i create namespaces >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Sem permissões para criar recursos
    echo    Verifique as permissões do cluster
    pause
    exit /b 1
)
echo ✅ Permissões OK

echo.
echo =========================================
echo ✅ Tudo pronto para o deploy!
echo =========================================
echo.
echo Cluster: %CURRENT_CONTEXT%
echo.
echo Próximos passos:
echo 1. Execute: deploy-k8s.bat
echo 2. Ou execute comandos individuais:
echo    kubectl apply -f k8s-namespace.yaml
echo    kubectl apply -f k8s-configmap.yaml
echo    kubectl apply -f k8s-pvc.yaml
echo    kubectl apply -f k8s-deployment.yaml
echo    kubectl apply -f k8s-service.yaml
echo.
pause 