# Cloud Run service account (used by the ingestion service)
resource "google_service_account" "cloud_run_sa" {
  account_id   = "weather-cloudrun-sa"
  display_name = "Service account for Cloud Run weather ingestion"
}

# Scheduler service account (used by Cloud Scheduler to invoke Cloud Run)
resource "google_service_account" "scheduler_sa" {
  account_id   = "weather-scheduler-sa"
  display_name = "Service account for Cloud Scheduler"
}

# IAM bindings: give Cloud Run SA access to Storage and Vertex AI
resource "google_project_iam_member" "cloudrun_storage" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloudrun_aiplatform" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Scheduler needs permission to invoke Cloud Run via OIDC token; we will bind run.invoker later to target service.
# Also allow scheduler SA to generate identity tokens (if required)
resource "google_project_iam_member" "scheduler_iam_token_creator" {
  project = var.project_id
  role    = "roles/iam.serviceAccountTokenCreator"
  member  = "serviceAccount:${google_service_account.scheduler_sa.email}"
}

resource "google_project_iam_member" "cloudrun_aiplatform_serviceagent" {
  project = var.project_id
  role    = "roles/aiplatform.serviceAgent"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "cloudrun_aiplatform_viewer" {
  project = var.project_id
  role    = "roles/aiplatform.viewer"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}
