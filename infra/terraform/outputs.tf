output "storage_bucket" {
  value = google_storage_bucket.weather_bucket.name
}
output "cloud_run_service_url" {
  value = google_cloud_run_service.weather_service.status[0].url
  description = "URL for Cloud Run service (may be empty until deployed)."
}
output "artifact_registry_repo" {
  value = google_artifact_registry_repository.repo.name
}
