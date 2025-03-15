variable "client_id" {
  description = "Azure Service Principal Client ID"
  type        = string
}

variable "client_secret" {
  description = "Azure Service Principal Client Secret"
  type        = string
  sensitive   = true
}

variable "tenant_id" {
  description = "Azure Tenant ID"
  type        = string
}

variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}


variable "clusters" {
  description = "List of AKS clusters to create"
  type = map(object({
    name                = string
    location            = string
    resource_group_name = string
    dns_prefix          = string
    node_count          = number
    vm_size             = string
  }))
}

variable "tags" {
  description = "Tags to apply to all clusters"
  type        = map(string)
  default = {
    environment = "Dev"
    managed_by  = "Terraform"
  }
}
