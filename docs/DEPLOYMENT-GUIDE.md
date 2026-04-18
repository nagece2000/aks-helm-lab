AKS HELM LAB - Complete Deployment Guide
Flask + PostgreSQL on Azure Kubernetes Service  
Deployed with Helm Charts and Terraform
---
Table of Contents
Overview
Phase 1: Infrastructure Setup
Phase 2: Application Development
Phase 3: Helm Chart Development
Phase 4: Ingress Configuration
Phase 5: Advanced Helm Features
Grafana Monitoring
Issues and Troubleshooting
Command Reference
Teardown Instructions
---
Overview
This guide provides complete step-by-step instructions to deploy a Flask web application with PostgreSQL database on Azure Kubernetes Service (AKS) using Helm charts and Terraform.
What You'll Build
Flask web application with visitor counter
PostgreSQL database for data persistence
AKS cluster with 2 nodes
Azure Container Registry for custom images
Nginx Ingress controller for routing
Grafana monitoring dashboards
Helm charts for deployment management
Technologies Used
Technology	Purpose
Azure AKS	Kubernetes cluster platform
Terraform	Infrastructure as Code
Helm	Kubernetes package manager
Flask	Python web framework
PostgreSQL	Relational database
Nginx Ingress	Ingress controller for routing
Grafana	Monitoring and visualization
---
Phase 1: Infrastructure Setup
Set up Azure infrastructure using Terraform with remote state storage.
Prerequisites
Azure subscription
Azure CLI installed
Terraform installed
Git installed
Step 1: Create GitHub Repository
Create a new repository at https://github.com/YOUR_USERNAME
Repository name: `aks-helm-lab`
Clone and initialize:
```bash
git clone https://github.com/YOUR_USERNAME/aks-helm-lab.git
cd aks-helm-lab
mkdir terraform helm-charts docs
git add .
git commit -m "Initial structure"
git push
```
Step 2: Create Terraform State Storage
Create Azure Storage Account for Terraform remote state (run in PowerShell):
```powershell
$STORAGE_RG = "rg-tfstate-aks-helm"
$STORAGE_ACCOUNT = "sttfstate" + (Get-Date -Format "yyyyMMddHHmmss")
$CONTAINER_NAME = "tfstate"
$LOCATION = "eastus"

az group create --name $STORAGE_RG --location $LOCATION

az storage account create `
  --name $STORAGE_ACCOUNT `
  --resource-group $STORAGE_RG `
  --location $LOCATION `
  --sku Standard_LRS

az storage container create `
  --name $CONTAINER_NAME `
  --account-name $STORAGE_ACCOUNT

# Note the storage account name
Write-Host "Storage Account Name: $STORAGE_ACCOUNT"
```
Step 3: Create Terraform Configuration Files
File: `terraform/backend.tf`
```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-tfstate-aks-helm"
    storage_account_name = "YOUR_STORAGE_ACCOUNT_NAME"
    container_name       = "tfstate"
    key                  = "aks-helm-lab.tfstate"
  }
}
```
File: `terraform/providers.tf`
```hcl
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}
```
File: `terraform/variables.tf`
```hcl
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-aks-helm-lab"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "aks_cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
  default     = "aks-helm-lab"
}

variable "aks_node_count" {
  description = "Number of nodes"
  type        = number
  default     = 2
}

variable "aks_node_size" {
  description = "VM size for nodes"
  type        = string
  default     = "Standard_D2s_v3"
}

variable "acr_name" {
  description = "Name of ACR"
  type        = string
  default     = "acrhelmlab"
}

variable "acr_sku" {
  description = "SKU for ACR"
  type        = string
  default     = "Basic"
}
```
File: `terraform/main.tf`
```hcl
# Resource Group
resource "azurerm_resource_group" "aks" {
  name     = var.resource_group_name
  location = var.location
  
  tags = {
    Environment = "Learning"
    Project     = "AKS-Helm-Lab"
  }
}

# Azure Container Registry
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.aks.name
  location            = azurerm_resource_group.aks.location
  sku                 = var.acr_sku
  admin_enabled       = true
  
  tags = {
    Environment = "Learning"
    Project     = "AKS-Helm-Lab"
  }
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.aks_cluster_name
  location            = azurerm_resource_group.aks.location
  resource_group_name = azurerm_resource_group.aks.name
  dns_prefix          = var.aks_cluster_name
  
  default_node_pool {
    name       = "default"
    node_count = var.aks_node_count
    vm_size    = var.aks_node_size
  }
  
  identity {
    type = "SystemAssigned"
  }
  
  tags = {
    Environment = "Learning"
    Project     = "AKS-Helm-Lab"
  }
}

# Attach ACR to AKS
resource "azurerm_role_assignment" "aks_acr" {
  principal_id                     = azurerm_kubernetes_cluster.aks.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.acr.id
  skip_service_principal_aad_check = true
}
```
File: `terraform/outputs.tf`
```hcl
output "resource_group_name" {
  value = azurerm_resource_group.aks.name
}

output "aks_cluster_name" {
  value = azurerm_kubernetes_cluster.aks.name
}

output "acr_name" {
  value = azurerm_container_registry.acr.name
}

output "acr_login_server" {
  value = azurerm_container_registry.acr.login_server
}

output "kube_config_command" {
  value = "az aks get-credentials --resource-group ${azurerm_resource_group.aks.name} --name ${azurerm_kubernetes_cluster.aks.name}"
}
```
Step 4: Deploy Infrastructure
```bash
cd terraform
terraform init
terraform plan
terraform apply
```
Type `yes` when prompted.
Step 5: Configure kubectl
```bash
az aks get-credentials --resource-group rg-aks-helm-lab --name aks-helm-lab
kubectl get nodes
```
You should see 2 nodes in Ready status.
---
Phase 2: Application Development
Create Flask application, containerize it, and push to Azure Container Registry.
Step 1: Create Application Structure
```bash
cd ..
mkdir -p app/templates app/static
```
Step 2: Create Flask Application
File: `app/app.py`
```python
from flask import Flask, render_template, request
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'helmdb')
DB_USER = os.getenv('DB_USER', 'helmuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'helmpass')

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS visitors (
                    id SERIAL PRIMARY KEY,
                    visit_time TIMESTAMP,
                    ip_address VARCHAR(50)
                )
            ''')
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Database initialization failed: {e}")

# Initialize database on startup
init_db()

@app.route('/')
def home():
    db_status = "Connected"
    visitor_count = 0
    
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            
            ip_address = request.remote_addr
            cur.execute(
                "INSERT INTO visitors (visit_time, ip_address) VALUES (%s, %s)",
                (datetime.now(), ip_address)
            )
            conn.commit()
            
            cur.execute("SELECT COUNT(*) FROM visitors")
            visitor_count = cur.fetchone()[0]
            
            cur.close()
            conn.close()
        except Exception as e:
            db_status = f"Error: {e}"
    else:
        db_status = "Disconnected"
    
    return render_template('index.html', 
                         db_status=db_status, 
                         visitor_count=visitor_count)

@app.route('/health')
def health():
    return {'status': 'healthy', 'service': 'flask-app'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```
File: `app/requirements.txt`
```
Flask==3.0.0
psycopg2-binary==2.9.9
gunicorn==21.2.0
```
File: `app/Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
```
File: `app/templates/index.html`
Create a simple HTML template (see GitHub repository for complete code).
Step 3: Build and Push to ACR
```bash
cd app
az acr build --registry acrhelmlab --image flask-webapp:v2 .
```
Verify:
```bash
az acr repository list --name acrhelmlab
az acr repository show-tags --name acrhelmlab --repository flask-webapp
```
---
Phase 3: Helm Chart Development
Create Helm charts to deploy Flask application and PostgreSQL.
Step 1: Install Helm
Check if Helm is installed:
```bash
helm version
```
Step 2: Create Helm Chart
```bash
cd ..
helm create helm-charts/webapp
```
Step 3: Customize Chart Files
File: `helm-charts/webapp/Chart.yaml`
```yaml
apiVersion: v2
name: webapp
description: Flask web application with PostgreSQL backend
type: application
version: 0.1.0
appVersion: "v1"
```
File: `helm-charts/webapp/values.yaml`
```yaml
replicaCount: 2

image:
  repository: acrhelmlab.azurecr.io/flask-webapp
  pullPolicy: IfNotPresent
  tag: "v2"

serviceAccount:
  create: true

service:
  type: ClusterIP
  port: 80
  targetPort: 5000

env:
  - name: DB_HOST
    value: "webapp-postgresql"
  - name: DB_PORT
    value: "5432"
  - name: DB_NAME
    value: "helmdb"
  - name: DB_USER
    value: "helmuser"
  - name: DB_PASSWORD
    value: "helmpass"

livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 5
  periodSeconds: 5

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

ingress:
  enabled: false
```
Step 4: Create PostgreSQL Deployment Template
File: `helm-charts/webapp/templates/postgres-deployment.yaml`
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "webapp.fullname" . }}-postgresql
  labels:
    {{- include "webapp.labels" . | nindent 4 }}
    app: postgresql
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgresql
  template:
    metadata:
      labels:
        app: postgresql
    spec:
      containers:
      - name: postgresql
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: helmdb
        - name: POSTGRES_USER
          value: helmuser
        - name: POSTGRES_PASSWORD
          value: helmpass
---
apiVersion: v1
kind: Service
metadata:
  name: {{ include "webapp.fullname" . }}-postgresql
  labels:
    {{- include "webapp.labels" . | nindent 4 }}
spec:
  ports:
  - port: 5432
    targetPort: 5432
  selector:
    app: postgresql
```
Step 5: Update Deployment Template
Edit `helm-charts/webapp/templates/deployment.yaml` to add environment variables.
Find the `ports:` section and add the `env:` section after it:
```yaml
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort }}
              protocol: TCP
          env:
          {{- range .Values.env }}
          - name: {{ .name }}
            {{- if .value }}
            value: {{ .value | quote }}
            {{- end }}
          {{- end }}
```
Step 6: Deploy with Helm
```bash
helm install webapp ./helm-charts/webapp
```
Verify:
```bash
kubectl get pods
kubectl get service
```
Wait for all pods to show `Running` status.
Get the LoadBalancer IP:
```bash
kubectl get service webapp
```
Access your application at the EXTERNAL-IP shown.
---
Phase 4: Ingress Configuration
Set up Nginx Ingress controller for better routing and cost savings.
Step 1: Install Nginx Ingress Controller
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install nginx-ingress ingress-nginx/ingress-nginx \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz
```
Verify:
```bash
kubectl get pods | findstr nginx
kubectl get service
```
Note the EXTERNAL-IP of the nginx-ingress controller.
Step 2: Update Webapp for Ingress
Edit `helm-charts/webapp/values.yaml`:
Change:
```yaml
service:
  type: LoadBalancer  # Change to ClusterIP
```
To:
```yaml
service:
  type: ClusterIP
```
Enable ingress:
```yaml
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: ""  # Accept any hostname/IP
      paths:
        - path: /
          pathType: Prefix
```
Step 3: Upgrade Helm Release
```bash
helm upgrade webapp ./helm-charts/webapp
```
Verify ingress:
```bash
kubectl get ingress
kubectl describe ingress webapp
```
Access your application using the nginx-ingress EXTERNAL-IP.
---
Phase 5: Advanced Helm Features
Learn Helm hooks, rollbacks, and multi-environment configurations.
Helm Hooks
Create a post-upgrade hook.
File: `helm-charts/webapp/templates/post-install-job.yaml`
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "webapp.fullname" . }}-post-upgrade
  labels:
    {{- include "webapp.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": post-upgrade
    "helm.sh/hook-weight": "0"
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: post-upgrade
        image: busybox:latest
        command: ['sh', '-c', 'echo "Upgrade completed at $(date)"']
```
Test the hook:
```bash
helm upgrade webapp ./helm-charts/webapp
kubectl get jobs
kubectl logs job/webapp-post-upgrade
```
Rollbacks
View revision history:
```bash
helm history webapp
```
Intentionally break the deployment:
```bash
# Edit values.yaml - change image tag to "v999" (doesn't exist)
helm upgrade webapp ./helm-charts/webapp
kubectl get pods  # See ImagePullBackOff
```
Rollback:
```bash
helm rollback webapp
kubectl get pods  # Fixed!
```
Multi-Environment Values
Create environment-specific values:
File: `helm-charts/webapp/values/dev.yaml`
```yaml
replicaCount: 1

resources:
  limits:
    cpu: 250m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi
```
File: `helm-charts/webapp/values/prod.yaml`
```yaml
replicaCount: 5

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi
```
Deploy different environments:
```bash
# Dev
helm upgrade webapp ./helm-charts/webapp -f ./helm-charts/webapp/values/dev.yaml

# Prod
helm upgrade webapp ./helm-charts/webapp -f ./helm-charts/webapp/values/prod.yaml

# Back to default
helm upgrade webapp ./helm-charts/webapp
```
---
Grafana Monitoring
Set up Prometheus and Grafana for cluster monitoring.
Install Monitoring Stack
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install monitoring prometheus-community/kube-prometheus-stack \
  --set grafana.service.type=LoadBalancer
```
Access Grafana
Get the LoadBalancer IP:
```bash
kubectl get service | findstr grafana
```
Get the password (PowerShell):
```powershell
$secret = kubectl get secrets monitoring-grafana -o jsonpath="{.data.admin-password}"
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($secret))
```
Access Grafana at `http://GRAFANA_IP`:
Username: `admin`
Password: (from above command)
Explore Dashboards
Click "Dashboards" in left sidebar
Open "Kubernetes / Compute Resources / Namespace (Pods)"
Select namespace: "default"
View:
CPU usage
Memory consumption
Network I/O
Pod status
---
Issues and Troubleshooting
Issue 1: Git Push Failed - Large Files
Problem: Terraform .terraform directory contains provider binaries over 100MB.
Root Cause: No .gitignore file, attempting to commit large binary files.
Solution:
Create `.gitignore` with `**/.terraform/*` pattern
Remove cached files: `git rm -r --cached terraform/.terraform`
Commit and push
Issue 2: Bitnami PostgreSQL Image Not Found
Problem: PostgreSQL pod stuck in ImagePullBackOff with 'image not found' error.
Root Cause: Bitnami chart references old image tag that no longer exists.
Solution: Switched to official `postgres:16-alpine` image with custom deployment template.
Issue 3: Service Selector Mismatch
Problem: Flask app couldn't connect to PostgreSQL despite both pods running.
Root Cause: Old Bitnami service had selector `app.kubernetes.io/name=postgresql` but new deployment had label `app=postgresql`.
Solution:
Delete old service: `kubectl delete service webapp-postgresql`
Upgrade Helm chart to recreate service with correct selectors
Issue 4: Database Table Not Created
Problem: Flask app showed 'relation visitors does not exist' error.
Root Cause: `init_db()` function was inside `if __name__ == '__main__'` block, doesn't execute with Gunicorn.
Solution:
Move `init_db()` call outside the if block to module level
Rebuild image as v2: `az acr build --registry acrhelmlab --image flask-webapp:v2 .`
Update Helm chart with new tag
Issue 5: Helm Template Errors - HTTPRoute
Problem: Helm install failed with 'nil pointer evaluating .Values.httpRoute.enabled'.
Root Cause: Template file exists but configuration missing from values.yaml.
Solution: Delete unused template files (`httproute.yaml`, `hpa.yaml`).
---
Command Reference
Git Commands
```bash
git clone https://github.com/USER/REPO.git
git add .
git commit -m "message"
git push
git status
git rm -r --cached PATH
```
Azure CLI Commands
```bash
# Resource Groups
az group create --name NAME --location LOCATION
az group delete --name NAME --yes
az group list --output table

# Storage
az storage account create --name NAME --resource-group RG --location LOC --sku STANDARD_LRS
az storage container create --name NAME --account-name ACCOUNT

# AKS
az aks get-credentials --resource-group RG --name CLUSTER

# ACR
az acr build --registry REGISTRY --image IMAGE:TAG .
az acr repository list --name REGISTRY
az acr repository show-tags --name REGISTRY --repository REPO
```
Terraform Commands
```bash
terraform init          # Initialize working directory
terraform plan          # Show execution plan
terraform apply         # Apply changes
terraform destroy       # Destroy infrastructure
terraform output        # Show output values
terraform fmt           # Format files
terraform validate      # Validate configuration
```
kubectl Commands
```bash
# Cluster Info
kubectl get nodes
kubectl cluster-info

# Pods
kubectl get pods
kubectl get pods -w                    # Watch mode
kubectl describe pod POD_NAME
kubectl logs POD_NAME
kubectl logs POD_NAME --follow        # Stream logs
kubectl exec POD_NAME -- COMMAND      # Execute command in pod
kubectl delete pod POD_NAME

# Services
kubectl get service
kubectl get svc                        # Short form
kubectl describe service SERVICE_NAME

# Ingress
kubectl get ingress
kubectl describe ingress INGRESS_NAME

# Jobs
kubectl get jobs
kubectl logs job/JOB_NAME

# General
kubectl get all                        # All resources
kubectl apply -f FILE.yaml            # Apply configuration
kubectl delete -f FILE.yaml           # Delete from file
```
Helm Commands
```bash
# Repository Management
helm repo add NAME URL
helm repo update
helm repo list

# Chart Management
helm create CHART_NAME
helm lint CHART_PATH

# Release Management
helm install RELEASE CHART_PATH
helm install RELEASE CHART_PATH -f VALUES.yaml
helm upgrade RELEASE CHART_PATH
helm upgrade RELEASE CHART_PATH -f VALUES.yaml
helm rollback RELEASE
helm rollback RELEASE REVISION
helm uninstall RELEASE

# Information
helm list
helm list --all-namespaces
helm history RELEASE
helm status RELEASE
helm get values RELEASE
helm get manifest RELEASE

# Dependencies
helm dependency update CHART_PATH
```
---
Teardown Instructions
To stop Azure billing, destroy all resources in the correct order.
Step 1: Uninstall Helm Releases
```bash
helm uninstall webapp
helm uninstall nginx-ingress
helm uninstall monitoring
```
Verify all releases are gone:
```bash
helm list
```
Step 2: Verify Pods Are Deleted
```bash
kubectl get pods
```
Wait for all pods to be terminated.
Step 3: Destroy Terraform Infrastructure
```bash
cd terraform
terraform destroy
```
Type `yes` when prompted.
This will destroy:
AKS cluster
Azure Container Registry
Resource group rg-aks-helm-lab
All associated networking resources
Step 4: Delete Terraform State Storage (Optional)
If you want to completely remove everything including Terraform state:
```bash
az group delete --name rg-tfstate-aks-helm --yes
```
Warning: This deletes the Terraform state. Only do this if you're completely done with the project.
Verification
Confirm all resources are deleted:
```bash
az group list --output table
```
Expected result: Only remaining resource groups should be system-managed Azure groups.
Cost Verification
Check Azure portal:
Go to Cost Management
Verify no active resources are billing
AKS cluster should show as "Deleted"
---
Summary
What Was Built:
Complete AKS cluster with 2 nodes
Flask web application with visitor counter
PostgreSQL database with persistence
Nginx Ingress for routing
Grafana monitoring stack
Full Helm chart deployment
Skills Learned:
Terraform for infrastructure provisioning
Helm for application deployment
Kubernetes pod, service, and ingress management
Container registry integration
Monitoring setup
Rollback and recovery procedures
Time to Complete: Approximately 4 days (one phase per day)
Final Architecture:
```
Internet → Nginx Ingress → Flask Pods (2) → PostgreSQL Pod
                              ↓
                         ACR (Images)
                              ↓
                     AKS Cluster (2 nodes)
```
---
GitHub Repository: https://github.com/nagece2000/aks-helm-lab
End of Guide