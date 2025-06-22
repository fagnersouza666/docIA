@echo off
REM Script para configurar cluster Kubernetes remoto

echo =========================================
echo   DocIA - Configurar Cluster Remoto
echo =========================================
echo.

echo Escolha o tipo de cluster remoto:
echo.
echo 1. Google Cloud (GKE)
echo 2. Amazon EKS
echo 3. Azure AKS
echo 4. DigitalOcean
echo 5. Configuracao manual (kubeconfig)
echo.
set /p CHOICE="Digite sua opcao (1-5): "

if "%CHOICE%"=="1" goto GKE
if "%CHOICE%"=="2" goto EKS
if "%CHOICE%"=="3" goto AKS
if "%CHOICE%"=="4" goto DIGITALOCEAN
if "%CHOICE%"=="5" goto MANUAL
echo Opcao invalida!
pause
exit /b 1

:GKE
echo.
echo === GOOGLE CLOUD (GKE) ===
echo.
echo Comandos para configurar GKE:
echo.
echo 1. Instale gcloud CLI: https://cloud.google.com/sdk/docs/install
echo 2. Faca login: gcloud auth login
echo 3. Configure projeto: gcloud config set project SEU-PROJETO
echo 4. Obtenha credenciais: gcloud container clusters get-credentials NOME-CLUSTER --zone=ZONA
echo.
echo Exemplo:
echo gcloud container clusters get-credentials my-cluster --zone=us-central1-a
echo.
goto END

:EKS
echo.
echo === AMAZON EKS ===
echo.
echo Comandos para configurar EKS:
echo.
echo 1. Instale AWS CLI: https://aws.amazon.com/cli/
echo 2. Configure credenciais: aws configure
echo 3. Obtenha credenciais: aws eks update-kubeconfig --region REGIAO --name NOME-CLUSTER
echo.
echo Exemplo:
echo aws eks update-kubeconfig --region us-west-2 --name my-cluster
echo.
goto END

:AKS
echo.
echo === AZURE AKS ===
echo.
echo Comandos para configurar AKS:
echo.
echo 1. Instale Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
echo 2. Faca login: az login
echo 3. Obtenha credenciais: az aks get-credentials --resource-group GRUPO --name NOME-CLUSTER
echo.
echo Exemplo:
echo az aks get-credentials --resource-group myResourceGroup --name myAKSCluster
echo.
goto END

:DIGITALOCEAN
echo.
echo === DIGITALOCEAN ===
echo.
echo Comandos para configurar DigitalOcean:
echo.
echo 1. Instale doctl: https://docs.digitalocean.com/reference/doctl/how-to/install/
echo 2. Autentique: doctl auth init
echo 3. Obtenha credenciais: doctl kubernetes cluster kubeconfig save NOME-CLUSTER
echo.
echo Exemplo:
echo doctl kubernetes cluster kubeconfig save my-cluster
echo.
goto END

:MANUAL
echo.
echo === CONFIGURACAO MANUAL ===
echo.
echo Se voce tem um arquivo kubeconfig:
echo.
echo 1. Copie o arquivo kubeconfig para: %USERPROFILE%\.kube\config
echo 2. Ou defina variavel: set KUBECONFIG=C:\caminho\para\seu\kubeconfig
echo 3. Teste: kubectl cluster-info
echo.
echo Se voce tem as credenciais:
echo.
set /p CLUSTER_URL="URL do cluster (https://...): "
set /p CLUSTER_TOKEN="Token de acesso: "
set /p CLUSTER_NAME="Nome do cluster: "
echo.
echo Configurando cluster...
kubectl config set-cluster %CLUSTER_NAME% --server=%CLUSTER_URL% --insecure-skip-tls-verify=true
kubectl config set-credentials %CLUSTER_NAME%-user --token=%CLUSTER_TOKEN%
kubectl config set-context %CLUSTER_NAME% --cluster=%CLUSTER_NAME% --user=%CLUSTER_NAME%-user
kubectl config use-context %CLUSTER_NAME%
echo.
echo Testando conexao...
kubectl cluster-info
if %errorlevel% equ 0 (
    echo ✅ Cluster configurado com sucesso!
    echo.
    echo Agora execute: deploy-k8s.bat
) else (
    echo ❌ Erro na configuracao. Verifique as credenciais.
)
goto END

:END
echo.
echo Apos configurar, execute: deploy-k8s.bat
echo.
pause 