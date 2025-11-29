resource "google_storage_bucket" "weather_bucket" {
  name     = var.bucket_name
  location = var.region
  uniform_bucket_level_access = true

  versioning {
    enabled = false
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 365
    }
  }
}
