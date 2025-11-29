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

### Data flow

1. **Cloud Scheduler** calls the `/ingest` endpoint on the **Cloud Run** service (`weather-api`) every N minutes.
2. Cloud Run:
   - Calls **Open-Meteo API** to get weather data.
   - Calls **Vertex AI (Gemini 2.0 Flash)** to generate:
     - weather summary
     - mood classification
   - Stores enriched results in **Google Cloud Storage (GCS)**.
3. The **React UI on GKE**:
   - Calls Cloud Run APIs
   - Displays weather in a table
   - Shows mood as colored tags
   - Lets user click a city to view full JSON data.

---

### Technology Stack

Backend:
- Python, Flask
- Cloud Run
- Vertex AI (Gemini)
- Google Cloud Storage
- Cloud Scheduler

Frontend:
- React
- Axios
- CSS
- Kubernetes (GKE)

Infrastructure:
- Terraform (IaC)
- Artifact Registry
- IAM & Service Accounts

Logging:
- Structured JSON logs to Cloud Logging

---

## 2. Repository Layout

cloudrun_api  
- Dockerfile  
- main.py  
- requirements.txt  

infra  
- lifecycle.json  
- terraform  
  - provider.tf  
  - cloudrun.tf  
  - scheduler.tf  
  - gke.tf  
  - storage.tf  
  - service_accounts.tf  
  - artifact_registry.tf  
  - variables.tf  
  - terraform.tfvars.example  

weather-ui  
- Dockerfile  
- .env.example  
- .dockerignore  
- k8s  
  - deployment.yaml  
  - service.yaml  
- src  
  - App.js  
  - api.js  
  - index.js  
  - index.css  
  - components  
    - WeatherTable.js  
    - CityDetail.js  
- public  
- package.json  

.gitignore  
README.md  

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

