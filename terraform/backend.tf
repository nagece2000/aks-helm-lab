terraform {
  backend "azurerm" {
    resource_group_name  = "rg-tfstate-aks-helm"
    storage_account_name = "sttfstate20260403071034"
    container_name       = "tfstate"
    key                  = "aks-helm-lab.tfstate"
  }
}