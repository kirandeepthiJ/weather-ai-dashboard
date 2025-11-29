resource "google_cloud_scheduler_job" "ingest_job" {
  name        = "weather-ingest-job"
  description = "Trigger Cloud Run ingestion every 30 minutes"
  schedule    = var.scheduler_cron
  time_zone   = "UTC"
  attempt_deadline = "600s"

  http_target {
    http_method = "GET"
    uri         = "${google_cloud_run_service.weather_service.status[0].url}/ingest"

    oidc_token {
      service_account_email = google_service_account.scheduler_sa.email
    }
  }
}
