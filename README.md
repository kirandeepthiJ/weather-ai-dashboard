# Serverless Weather AI Microservice on GCP

## Overview
This project implements an end-to-end serverless, event-driven microservice on Google Cloud Platform (GCP).

Features:
- Periodically ingests live weather data for 5 cities
- Stores structured data in Google Cloud Storage
- Uses Google Vertex AI (Gemini 2.0 Flash) to generate:
  - Weather summary
  - Mood label (Calm, Chilly, Pleasant, etc.)
- Exposes REST APIs using Cloud Run
- Displays data using a React UI deployed on GKE


## Architecture Flow

Cloud Scheduler  
→ Cloud Run (/ingest)  
→ Open-Meteo API  
→ Vertex AI (Gemini)  
→ Google Cloud Storage  
→ React UI on GKE  

React UI:
- Fetches data from Cloud Run
- Displays table view
- Shows mood tags
- Allows viewing raw JSON per city

Technologies:
Backend: Python, Flask, Cloud Run, Vertex AI, Cloud Storage, Cloud Scheduler  
Frontend: React, Axios, CSS  
Infrastructure: Terraform, Artifact Registry, GKE  
Logging: Cloud Logging  


## Repository Structure

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
- k8s  
  - deployment.yaml  
  - service.yaml  
- src  
- public  
- package.json  


## Deployment Instructions

### Step 1: Terraform Setup
Go to:
infra/terraform

Create:
terraform.tfvars

Example:
project_id = "your-project-id"
region = "us-central1"
zone = "us-central1-a"
bucket_name = "weather-data-yourname"
cloud_run_image = "image-path"
ui_image = "image-path"
gke_cluster_name = "weather-cluster"

Run:
terraform init  
terraform apply  


### Step 2: Backend Deployment (Cloud Run)

Build image:
docker build -t IMAGE .

Push:
docker push IMAGE


### Step 3: UI Deployment (GKE)

Build & push:
docker build -t UI_IMAGE .
docker push UI_IMAGE

Get cluster credentials:
gcloud container clusters get-credentials CLUSTER_NAME

Apply manifests:
kubectl apply -f k8s/deployment.yaml  
kubectl apply -f k8s/service.yaml  

Open LoadBalancer IP.


## API Documentation

Base URL:
Cloud Run service URL

Endpoints:

GET /  
Health check

GET /ingest  
Fetches weather + AI processing

GET /weather/all  
Returns all cities

GET /weather/{city}  
Returns one city data


## Logging

Logs are emitted in JSON format.
View logs in:
Google Cloud Console → Logs Explorer


## Security

- Least privilege service accounts
- Secrets removed from repository
- terraform.tfvars ignored
- .env files ignored
- IAM roles scoped properly


## Cost Optimization

- Autoscaling
- Lifecycle rules on storage
- Lightweight compute
- Artifact Registry used for images


## CI/CD

CI/CD is not implemented yet.
It is planned using GitHub Actions or Cloud Build.


## Demo

1. Trigger /ingest
2. View Cloud Storage bucket
3. Open UI dashboard
4. Click a city to inspect full JSON


## Author

Kiran Deepthi  
B.Tech CSE | Cloud & AI Engineering
