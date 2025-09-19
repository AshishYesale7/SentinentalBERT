# GCP Infrastructure for SentinentalBERT
# This Terraform configuration sets up the complete GCP infrastructure

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Enable required APIs
resource "google_project_service" "apis" {
  for_each = toset([
    "compute.googleapis.com",
    "container.googleapis.com",
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "pubsub.googleapis.com",
    "dataflow.googleapis.com",
    "bigquery.googleapis.com",
    "storage.googleapis.com",
    "firestore.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudscheduler.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "secretmanager.googleapis.com",
    "iam.googleapis.com",
    "firebase.googleapis.com"
  ])

  service = each.value
  project = var.project_id

  disable_dependent_services = true
}

# Cloud Storage buckets
resource "google_storage_bucket" "raw_data" {
  name     = "${var.project_id}-sentinelbert-raw-data-${var.environment}"
  location = var.region

  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.apis]
}

resource "google_storage_bucket" "processed_data" {
  name     = "${var.project_id}-sentinelbert-processed-data-${var.environment}"
  location = var.region

  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }

  depends_on = [google_project_service.apis]
}

resource "google_storage_bucket" "models" {
  name     = "${var.project_id}-sentinelbert-models-${var.environment}"
  location = var.region

  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }

  depends_on = [google_project_service.apis]
}

resource "google_storage_bucket" "cloud_build" {
  name     = "${var.project_id}-sentinelbert-cloudbuild-${var.environment}"
  location = var.region

  uniform_bucket_level_access = true

  depends_on = [google_project_service.apis]
}

# BigQuery dataset
resource "google_bigquery_dataset" "sentinelbert" {
  dataset_id  = "sentinelbert_${var.environment}"
  description = "SentinentalBERT analytics dataset"
  location    = var.region

  delete_contents_on_destroy = var.environment != "prod"

  depends_on = [google_project_service.apis]
}

# Pub/Sub topics
resource "google_pubsub_topic" "social_media_raw" {
  name = "social-media-raw-${var.environment}"

  message_retention_duration = "604800s" # 7 days

  depends_on = [google_project_service.apis]
}

resource "google_pubsub_topic" "social_media_processed" {
  name = "social-media-processed-${var.environment}"

  message_retention_duration = "604800s" # 7 days

  depends_on = [google_project_service.apis]
}

resource "google_pubsub_topic" "nlp_analysis" {
  name = "nlp-analysis-${var.environment}"

  message_retention_duration = "604800s" # 7 days

  depends_on = [google_project_service.apis]
}

# Dead letter topic
resource "google_pubsub_topic" "dead_letter" {
  name = "dead-letter-${var.environment}"

  message_retention_duration = "2592000s" # 30 days

  depends_on = [google_project_service.apis]
}

# Pub/Sub subscriptions
resource "google_pubsub_subscription" "social_media_raw_sub" {
  name  = "social-media-raw-sub-${var.environment}"
  topic = google_pubsub_topic.social_media_raw.name

  ack_deadline_seconds = 300

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 5
  }
}

resource "google_pubsub_subscription" "social_media_processed_sub" {
  name  = "social-media-processed-sub-${var.environment}"
  topic = google_pubsub_topic.social_media_processed.name

  ack_deadline_seconds = 300

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 5
  }
}

resource "google_pubsub_subscription" "nlp_analysis_sub" {
  name  = "nlp-analysis-sub-${var.environment}"
  topic = google_pubsub_topic.nlp_analysis.name

  ack_deadline_seconds = 600 # Longer for ML processing

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 3
  }
}

# Firestore database
resource "google_firestore_database" "sentinelbert" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"

  depends_on = [google_project_service.apis]
}

# Service accounts
resource "google_service_account" "ingestion_service" {
  account_id   = "sentinelbert-ingestion-${var.environment}"
  display_name = "SentinentalBERT Ingestion Service"
  description  = "Service account for data ingestion services"
}

resource "google_service_account" "nlp_service" {
  account_id   = "sentinelbert-nlp-${var.environment}"
  display_name = "SentinentalBERT NLP Service"
  description  = "Service account for NLP processing services"
}

resource "google_service_account" "backend_service" {
  account_id   = "sentinelbert-backend-${var.environment}"
  display_name = "SentinentalBERT Backend Service"
  description  = "Service account for backend API services"
}

resource "google_service_account" "dataflow_service" {
  account_id   = "sentinelbert-dataflow-${var.environment}"
  display_name = "SentinentalBERT Dataflow Service"
  description  = "Service account for Dataflow jobs"
}

resource "google_service_account" "cloud_functions" {
  account_id   = "sentinelbert-functions-${var.environment}"
  display_name = "SentinentalBERT Cloud Functions"
  description  = "Service account for Cloud Functions"
}

# IAM bindings for service accounts
resource "google_project_iam_member" "ingestion_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.ingestion_service.email}"
}

resource "google_project_iam_member" "ingestion_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.ingestion_service.email}"
}

resource "google_project_iam_member" "nlp_pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.nlp_service.email}"
}

resource "google_project_iam_member" "nlp_vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.nlp_service.email}"
}

resource "google_project_iam_member" "backend_bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.backend_service.email}"
}

resource "google_project_iam_member" "backend_firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.backend_service.email}"
}

resource "google_project_iam_member" "dataflow_worker" {
  project = var.project_id
  role    = "roles/dataflow.worker"
  member  = "serviceAccount:${google_service_account.dataflow_service.email}"
}

resource "google_project_iam_member" "dataflow_bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.dataflow_service.email}"
}

resource "google_project_iam_member" "functions_invoker" {
  project = var.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "serviceAccount:${google_service_account.cloud_functions.email}"
}

# Secret Manager secrets
resource "google_secret_manager_secret" "twitter_bearer_token" {
  secret_id = "twitter-bearer-token-${var.environment}"

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret" "reddit_client_id" {
  secret_id = "reddit-client-id-${var.environment}"

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret" "reddit_client_secret" {
  secret_id = "reddit-client-secret-${var.environment}"

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret" "instagram_access_token" {
  secret_id = "instagram-access-token-${var.environment}"

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "jwt-secret-${var.environment}"

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

# Cloud Scheduler jobs
resource "google_cloud_scheduler_job" "daily_ingestion" {
  name             = "daily-ingestion-${var.environment}"
  description      = "Daily social media data ingestion"
  schedule         = "0 2 * * *" # 2 AM daily
  time_zone        = "UTC"
  attempt_deadline = "320s"

  retry_config {
    retry_count = 3
  }

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-${var.project_id}.cloudfunctions.net/trigger-ingestion-${var.environment}"
  }

  depends_on = [google_project_service.apis]
}

# Outputs
output "project_id" {
  value = var.project_id
}

output "region" {
  value = var.region
}

output "raw_data_bucket" {
  value = google_storage_bucket.raw_data.name
}

output "processed_data_bucket" {
  value = google_storage_bucket.processed_data.name
}

output "models_bucket" {
  value = google_storage_bucket.models.name
}

output "bigquery_dataset" {
  value = google_bigquery_dataset.sentinelbert.dataset_id
}

output "pubsub_topics" {
  value = {
    raw       = google_pubsub_topic.social_media_raw.name
    processed = google_pubsub_topic.social_media_processed.name
    nlp       = google_pubsub_topic.nlp_analysis.name
  }
}

output "service_accounts" {
  value = {
    ingestion = google_service_account.ingestion_service.email
    nlp       = google_service_account.nlp_service.email
    backend   = google_service_account.backend_service.email
    dataflow  = google_service_account.dataflow_service.email
    functions = google_service_account.cloud_functions.email
  }
}