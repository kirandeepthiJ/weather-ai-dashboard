resource "google_cloud_run_service" "weather_service" {
  name     = "weather-api"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.cloud_run_sa.email

      containers {
        image = var.cloud_run_image

        env {
          name  = "BUCKET_NAME"
          value = var.bucket_name
        }

        # Needed by your Gemini client
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }

        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
      }

      container_concurrency = 80
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  autogenerate_revision_name = true
}

# Scheduler → Cloud Run invocation
resource "google_cloud_run_service_iam_member" "invoker_binding" {
  service  = google_cloud_run_service.weather_service.name
  location = google_cloud_run_service.weather_service.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.scheduler_sa.email}"
}

# Cloud Run → Vertex AI access (REQUIRED for Gemini)
resource "google_project_iam_member" "cloudrun_vertex_ai" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}
