locals {
  workload_pool = "${var.project_id}.svc.id.goog"
}

resource "google_service_account" "gke_workload_sa" {
  account_id   = "weather-gke-workload-sa"
  display_name = "GKE workload identity service account"
  project      = var.project_id
}

resource "google_container_cluster" "gke_cluster" {
  name                     = var.gke_cluster_name
  location                 = var.zone  
  project                  = var.project_id
  remove_default_node_pool = true
  initial_node_count       = 1

  workload_identity_config {
    workload_pool = local.workload_pool
  }

  network    = "default"
  subnetwork = "default"

  addons_config {
    horizontal_pod_autoscaling {
      disabled = false
    }
  }

  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }
}

resource "google_container_node_pool" "primary_nodes" {
  name     = "${var.gke_cluster_name}-node-pool"
  location = google_container_cluster.gke_cluster.location
  cluster  = google_container_cluster.gke_cluster.name
  project  = var.project_id

  node_config {
    machine_type  = "e2-medium"
    disk_type     = "pd-standard"
    disk_size_gb  = 20

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }

  initial_node_count = 1

  autoscaling {
    min_node_count = 1
    max_node_count = 2
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

output "gke_cluster_name" {
  value = google_container_cluster.gke_cluster.name
}

output "gke_cluster_endpoint" {
  value = google_container_cluster.gke_cluster.endpoint
}

output "gke_workload_pool" {
  value = local.workload_pool
}

output "gke_workload_sa" {
  value = google_service_account.gke_workload_sa.email
}
