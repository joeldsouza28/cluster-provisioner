provider "google" {
    project     = var.project_id
    region      = var.region
}


resource "google_container_cluster" "gke" {
  for_each = var.clusters

  name     = each.key
  location = each.value.location
  deletion_protection = false

  initial_node_count = each.value.node_count

  node_config {
    machine_type = each.value.machine_type
  }
}