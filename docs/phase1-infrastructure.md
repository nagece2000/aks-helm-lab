# Phase 1: Infrastructure Setup

## Resources Created

- **Resource Group**: `rg-aks-helm-lab` (East US)
- **AKS Cluster**: `aks-helm-lab`
  - 2 nodes (Standard_D2s_v3)
  - Kubernetes version: v1.34.4
- **Azure Container Registry**: `acrhelmlab.azurecr.io`
- **Role Assignment**: AKS can pull from ACR

## Commands Used

### Connect to AKS
```bash
az aks get-credentials --resource-group rg-aks-helm-lab --name aks-helm-lab
```

### Verify Cluster
```bash
kubectl get nodes
```

## State Storage
- Terraform state stored in Azure Storage Account: `sttfstate20260403071034`
- Container: `tfstate`
- State file: `aks-helm-lab.tfstate`