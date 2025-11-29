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
```
3. Prerequisites

Google Cloud project (e.g., weather-ai-dashboard)

gcloud CLI installed and authenticated

Terraform installed

Docker installed

Node.js + npm (if you want to run the UI locally)
4. Infrastructure Deployment (Terraform)

All commands below are run from the repo root unless otherwise specified.
4.1 Set up Terraform variables
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars
Edit terraform.tfvars and fill in:
project_id   = "weather-ai-dashboard"   # your GCP project id
region       = "us-central1"
zone         = "us-central1-a"
bucket_name  = "weather-data-deepthi-2025"
gke_cluster_name = "weather-gke-cluster"
cloud_run_image  = "us-central1-docker.pkg.dev/weather-ai-dashboard/weather-repo/weather-api:vX"
ui_image         = "us-central1-docker.pkg.dev/weather-ai-dashboard/weather-repo/weather-ui:vY"
Note: cloud_run_image and ui_image refer to Docker images you’ll build & push in the next step.
4.2 Build & push backend (Cloud Run) image
cd cloudrun_api

# Build image
docker build -t us-central1-docker.pkg.dev/PROJECT_ID/weather-repo/weather-api:v1 .

# Push to Artifact Registry
docker push us-central1-docker.pkg.dev/PROJECT_ID/weather-repo/weather-api:v1
Update cloud_run_image in terraform.tfvars to this exact tag.
4.3 Build & push UI (GKE) image
cd weather-ui

npm install
# (optional) npm run build

docker build -t us-central1-docker.pkg.dev/PROJECT_ID/weather-repo/weather-ui:v1 .

docker push us-central1-docker.pkg.dev/PROJECT_ID/weather-repo/weather-ui:v1

Update ui_image in terraform.tfvars if you are referencing it from Terraform, or ensure k8s/deployment.yaml uses this image.

4.4 Run Terraform
cd infra/terraform

terraform init
terraform apply
Terraform will create:

Artifact Registry repo

GCS bucket

Service accounts + IAM roles

Cloud Run service weather-api

Cloud Scheduler job calling /ingest

GKE cluster + node pool
5. Deploy the React UI to GKE

After Terraform finishes, configure kubectl:
gcloud container clusters get-credentials <gke_cluster_name> --zone <zone> --project <project_id>
Check cluster access:
kubectl get nodes
Then deploy the UI:
cd weather-ui/k8s
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
Get the external IP:
kubectl get service weather-ui-service
Open the IP in the browser – you should see Weather AI Dashboard.
6. Running Ingestion & Viewing Data

Manually trigger ingestion once (for testing):
curl "https://<cloud-run-url>/ingest"
Or click the Cloud Run URL in GCP console and append /ingest.

Scheduler will then call this endpoint automatically based on its cron schedule.

The UI calls:

GET /weather/all to list all cities

GET /weather/<city> to fetch a single city
7. API Documentation

Base URL:
https://<cloud-run-host>
7.1 GET /

Description: Health message

Response:
{ "message": "Weather API running" }
7.2 GET /healthz

Description: Health check endpoint

Response:
{ "status": "ok" }
7.3 GET /ingest

Description:
Fetches weather for 5 cities, calls Vertex AI to generate summary and mood, and writes one JSON file per city in GCS.

Response (example):
{
  "Hyderabad": "✔ Stored",
  "London": "✔ Stored",
  "New York": "✔ Stored",
  "Tokyo": "✔ Stored",
  "Sydney": "✔ Stored"
}
7.4 GET /weather/all

Description: Returns all cities currently stored in the bucket.

Sample response:
[
  {
    "city": "Hyderabad",
    "temperature": 19.3,
    "wind_speed": 2.5,
    "mood": "Calm",
    "summary": "Hyderabad weather is mild with a gentle breeze."
  },
  ...
]
7.5 GET /weather/<city>

Description: Returns a single city record by name.

Example:
GET /weather/London
Response:
{
  "city": "London",
  "temperature": 5.6,
  "wind_speed": 8.4,
  "mood": "Chilly",
  "summary": "The weather in London is cool and breezy."
}
8. Local Development
Backend (Cloud Run API) locally
cd cloudrun_api
pip install -r requirements.txt
export BUCKET_NAME="your-test-bucket"
export GOOGLE_CLOUD_PROJECT="your-project-id"
python main.py
Visit http://localhost:8080/weather/all (if you have JSON in the bucket).
UI locally
cd weather-ui
npm install
npm start
Set REACT_APP_API_URL in .env to point to your local or Cloud Run backend.

9. Logging

Application outputs JSON logs:
{"service":"weather-api","severity":"INFO","message":"Stored London"}

Logs appear in:

GCP Console → Cloud Logging → Logs Explorer

10. Security & IAM

- Separate service accounts per workload
- Least privilege IAM roles
- No credentials in GitHub
- `.env` and terraform.tfvars ignored
- Secret values passed using:
  - Environment variables
  - Kubernetes Secrets

 11. Cost Optimization

- Autoscaling for Cloud Run
- Autoscaling node pool for GKE
- GCS lifecycle rules
- Minimal Docker image sizes
- Artifact Registry for image storage

 12. CI/CD (Future Scope)

CI/CD is not implemented yet.

Planned:
- GitHub Actions / Cloud Build
- Automatic Docker builds
- Auto deployment on commits
 13. Demo Steps

1. Call `/ingest`
2. Check Cloud Storage bucket
3. Open UI
4. Click city → see AI output
14. Author

Kiran Deepthi  
B.Tech CSE | Cloud & AI Enthusiast

