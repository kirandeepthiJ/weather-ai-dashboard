# Serverless Weather AI Microservice on GCP

This project implements an end-to-end **serverless, event-driven microservice** on Google Cloud Platform that:

- Periodically ingests live **weather data** for 5 cities
- Stores it in **Google Cloud Storage**
- Uses **Vertex AI Gemini 2.0 Flash** to generate:
  - a short **summary** of the weather
  - a **mood tag** (e.g., Calm, Chilly, Pleasant)
- Exposes a simple **REST API** via Cloud Run
- Visualizes the data in a **React UI** deployed on **GKE**

---

## 1. Architecture Overview

**Data flow:**

1. **Cloud Scheduler** calls the `/ingest` endpoint on a **Cloud Run** service (`weather-api`) every N minutes.
2. Cloud Run:
   - Calls **Open-Meteo** APIs to fetch current weather for 5 cities.
   - Calls **Vertex AI (Gemini 2.0 Flash)** to derive:
     - `summary` (natural language)
     - `mood` (short label)
   - Stores the final JSON (raw + AI fields) into **GCS bucket** `weather-data-<something>`.
3. The **React UI** (Weather AI Dashboard) running on **GKE**:
   - Calls the Cloud Run API
   - Renders a table of all cities
   - Shows mood as colored tags and summary as text
   - Allows clicking a city to view full JSON details.

**Tech stack:**

- Backend: Python, Flask, Cloud Run, Vertex AI, Cloud Storage, Cloud Scheduler  
- Frontend: React, Axios, CSS, GKE (Deployment + Service)  
- IaC: Terraform (Cloud Run, GKE, Scheduler, Storage, Artifact Registry, IAM)  
- Logging: JSON logs to **Cloud Logging**

---

## 2. Repository Layout

```text
cloudrun_api/
  Dockerfile              # Backend container image
  main.py                 # Flask API + Vertex AI + ingestion logic
  requirements.txt        # Python dependencies

infra/
  lifecycle.json          # Example GCS lifecycle rule (delete old objects)
  terraform/
    .terraform.lock.hcl   # Provider lock file
    artifact_registry.tf  # Artifact Registry repo for Docker images
    cloudrun.tf           # Cloud Run service + IAM
    gke.tf                # GKE cluster + node pool
    provider.tf           # Terraform provider configuration
    scheduler.tf          # Cloud Scheduler job
    service_accounts.tf   # IAM service accounts and roles
    storage.tf            # GCS bucket for weather JSON files
    variables.tf          # Input variable definitions
    terraform.tfvars.example  # Example values for variables

weather-ui/
  k8s/
    deployment.yaml       # GKE Deployment for React UI
    service.yaml          # LoadBalancer Service for UI
  public/
    index.html
  src/
    App.js                # Top-level React component
    api.js                # Axios calls to Cloud Run API
    index.js              # React entry point
    index.css             # Styling
    components/
      WeatherTable.js     # Main table with mood badges
      CityDetail.js       # Modal with full JSON
  Dockerfile              # UI Docker image
  .dockerignore
  .env.example            # Sample env file for REACT_APP_API_URL

.gitignore
README.md                 # This file
---

## 3. Deployment Instructions

### Prerequisites

Install:
- Terraform
- Docker
- Node.js
- gcloud CLI (authenticated)

---

### Step 1: Configure Terraform

Go to:
infra/terraform

Create actual variables file:
cp terraform.tfvars.example terraform.tfvars

Edit terraform.tfvars:

project_id = "your-gcp-project-id"
region = "us-central1"
zone = "us-central1-a"
bucket_name = "weather-data-yourname"
cloud_run_image = "us-central1-docker.pkg.dev/PROJECT/weather-repo/weather-api:v1"
ui_image = "us-central1-docker.pkg.dev/PROJECT/weather-repo/weather-ui:v1"
gke_cluster_name = "weather-gke-cluster"

Run:

terraform init
terraform apply

This provisions:
- Cloud Run
- Cloud Scheduler
- Cloud Storage
- GKE
- Artifact Registry
- IAM service accounts

---

### Step 2: Build & Push Cloud Run API

cd cloudrun_api
docker build -t IMAGE .
docker push IMAGE

---

### Step 3: Build & Push UI Image

cd weather-ui
docker build -t UI_IMAGE .
docker push UI_IMAGE

Update image in deployment.yaml then:

kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

Get UI URL:

kubectl get services

Open LoadBalancer IP.

---

## 4. API Documentation

Base URL:
Cloud Run URL

Endpoints:

GET /
Health check

GET /ingest
Fetches weather + runs AI processing

GET /weather/all
Returns all cities

GET /weather/{city}
Returns one city's data

Example response:

{
"city": "London",
"temperature": 6.4,
"wind_speed": 5.3,
"summary": "Partly cloudy and calm.",
"mood": "chilly"
}

---

## 5. Logging

Application outputs JSON logs:

{"service":"weather-api","severity":"INFO","message":"Stored London"}

Logs appear in:

GCP Console → Cloud Logging → Logs Explorer

---

## 6. Security & IAM

- Separate service accounts per workload
- Least privilege IAM roles
- No credentials in GitHub
- `.env` and terraform.tfvars ignored
- Secret values passed using:
  - Environment variables
  - Kubernetes Secrets

---

## 7. Cost Optimization

- Autoscaling for Cloud Run
- Autoscaling node pool for GKE
- GCS lifecycle rules
- Minimal Docker image sizes
- Artifact Registry for image storage

---

## 8. CI/CD (Future Scope)

CI/CD is not implemented yet.

Planned:
- GitHub Actions / Cloud Build
- Automatic Docker builds
- Auto deployment on commits

---

## 9. Demo Steps

1. Call `/ingest`
2. Check Cloud Storage bucket
3. Open UI
4. Click city → see AI output

---

## 10. Author

Kiran Deepthi  
B.Tech CSE | Cloud & AI Enthusiast

