# Serverless Weather AI Microservice on GCP

This project implements an end-to-end *serverless, event-driven microservice* on Google Cloud Platform that:

- Periodically ingests live *weather data* for 5 cities
- Stores it in *Google Cloud Storage*
- Uses *Vertex AI Gemini 2.0 Flash* to generate:
  - a short *summary* of the weather
  - a *mood tag* (e.g., Calm, Chilly, Pleasant)
- Exposes a simple *REST API* via Cloud Run
- Visualizes the data in a *React UI* deployed on *GKE*

---

## 1. Architecture Overview

*Data flow:*

1. *Cloud Scheduler* calls the /ingest endpoint on a *Cloud Run* service (weather-api) every N minutes.
2. Cloud Run:
   - Calls *Open-Meteo* APIs to fetch current weather for 5 cities.
   - Calls *Vertex AI (Gemini 2.0 Flash)* to derive:
     - summary (natural language)
     - mood (short label)
   - Stores the final JSON (raw + AI fields) into *GCS bucket* weather-data-<something>.
3. The *React UI* (Weather AI Dashboard) running on *GKE*:
   - Calls the Cloud Run API
   - Renders a table of all cities
   - Shows mood as colored tags and summary as text
   - Allows clicking a city to view full JSON details.

*Tech stack:*

- Backend: Python, Flask, Cloud Run, Vertex AI, Cloud Storage, Cloud Scheduler  
- Frontend: React, Axios, CSS, GKE (Deployment + Service)  
- IaC: Terraform (Cloud Run, GKE, Scheduler, Storage, Artifact Registry, IAM)  
- Logging: JSON logs to *Cloud Logging*

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
