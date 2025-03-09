variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}


variable "cluster_name" {
  type = string
  description = "Cluster Name"
  default = "my-gke-cluster"
}

variable "node_pool_name" {
  type = string
  description = "Node Pool Name"
  default = "my-node-pool"
}

variable "machine_type" {
  type = string
  description = "Node Pool Name"
  default = "my-node-pool"
}


variable "clusters" {
  type = map(object({
    location    = string
    machine_type = string
    node_count  = number
  }))
  default = {}
}