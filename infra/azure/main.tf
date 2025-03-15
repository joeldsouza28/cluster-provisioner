provider "azurerm" {
  features {}
  client_id       = var.client_id
  client_secret   = var.client_secret
  tenant_id       = var.tenant_id
  subscription_id = var.subscription_id
}

resource "azurerm_resource_group" "rg" {
  for_each = var.clusters

  name     = each.value.resource_group_name
  location = each.value.location
}

resource "azurerm_kubernetes_cluster" "aks" {
  for_each = var.clusters

  name                = each.value.name
  location            = each.value.location
  resource_group_name = azurerm_resource_group.rg[each.key].name
  dns_prefix          = each.value.dns_prefix

  default_node_pool {
    name       = "agentpool"
    node_count = each.value.node_count
    vm_size    = each.value.vm_size
  }

  service_principal {
    client_id     = var.client_id
    client_secret = var.client_secret
  }

#   identity {
#     type = "SystemAssigned"
#   }

  tags = var.tags
}

output "kubeconfigs" {
  value     = { for k, v in azurerm_kubernetes_cluster.aks : k => v.kube_config_raw }
  sensitive = true
}
