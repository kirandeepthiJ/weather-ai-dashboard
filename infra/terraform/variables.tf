variable "project_id" {
  type    = string
  default = "weather-ai-dashboard"
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "zone" {
  type    = string
  default = "us-central1-a"
}

variable "bucket_name" {
  type    = string
  default = "weather-data-deepthi-2025"
}

variable "cloud_run_image" {
  default = "us-central1-docker.pkg.dev/weather-ai-dashboard/weather-repo/weather-api:latest"
}



variable "gke_cluster_name" {
  type    = string
  default = "weather-ui-cluster"
}

variable "scheduler_cron" {
  type    = string
  default = "*/30 * * * *"
}
