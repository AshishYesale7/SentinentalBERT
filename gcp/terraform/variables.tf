# Terraform variables for SentinentalBERT GCP deployment

variable "project_id" {
  description = "The GCP project ID where resources will be created"
  type        = string
  validation {
    condition     = length(var.project_id) > 0
    error_message = "Project ID must not be empty."
  }
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
  validation {
    condition = contains([
      "us-central1", "us-east1", "us-west1", "us-west2",
      "europe-west1", "europe-west2", "europe-west3",
      "asia-east1", "asia-southeast1", "asia-northeast1"
    ], var.region)
    error_message = "Region must be a valid GCP region."
  }
}

variable "zone" {
  description = "The GCP zone for resources"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "enable_apis" {
  description = "Whether to enable required GCP APIs"
  type        = bool
  default     = true
}

variable "bigquery_location" {
  description = "Location for BigQuery dataset"
  type        = string
  default     = "US"
}

variable "storage_class" {
  description = "Storage class for Cloud Storage buckets"
  type        = string
  default     = "STANDARD"
  validation {
    condition = contains([
      "STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE"
    ], var.storage_class)
    error_message = "Storage class must be one of: STANDARD, NEARLINE, COLDLINE, ARCHIVE."
  }
}

variable "pubsub_message_retention_duration" {
  description = "Message retention duration for Pub/Sub topics (in seconds)"
  type        = string
  default     = "604800" # 7 days
}

variable "enable_monitoring" {
  description = "Whether to enable monitoring and logging"
  type        = bool
  default     = true
}

variable "enable_security_features" {
  description = "Whether to enable additional security features"
  type        = bool
  default     = true
}

variable "dataflow_max_workers" {
  description = "Maximum number of workers for Dataflow jobs"
  type        = number
  default     = 10
}

variable "cloud_run_cpu_limit" {
  description = "CPU limit for Cloud Run services"
  type        = string
  default     = "2"
}

variable "cloud_run_memory_limit" {
  description = "Memory limit for Cloud Run services"
  type        = string
  default     = "4Gi"
}

variable "cloud_run_max_instances" {
  description = "Maximum instances for Cloud Run services"
  type        = number
  default     = 100
}

variable "cloud_run_min_instances" {
  description = "Minimum instances for Cloud Run services"
  type        = number
  default     = 0
}

variable "vertex_ai_region" {
  description = "Region for Vertex AI resources"
  type        = string
  default     = "us-central1"
}

variable "firestore_location" {
  description = "Location for Firestore database"
  type        = string
  default     = "us-central"
}

variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default = {
    project     = "sentinelbert"
    managed-by  = "terraform"
    team        = "data-engineering"
  }
}

variable "deletion_protection" {
  description = "Whether to enable deletion protection on critical resources"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Number of days to retain backups"
  type        = number
  default     = 30
}

variable "log_retention_days" {
  description = "Number of days to retain logs"
  type        = number
  default     = 30
}

variable "enable_vpc" {
  description = "Whether to create a custom VPC"
  type        = bool
  default     = false
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_nat_gateway" {
  description = "Whether to enable NAT gateway for private instances"
  type        = bool
  default     = false
}

variable "enable_cloud_armor" {
  description = "Whether to enable Cloud Armor for DDoS protection"
  type        = bool
  default     = false
}

variable "notification_email" {
  description = "Email address for notifications and alerts"
  type        = string
  default     = ""
}

variable "budget_amount" {
  description = "Budget amount in USD for cost monitoring"
  type        = number
  default     = 1000
}

variable "enable_budget_alerts" {
  description = "Whether to enable budget alerts"
  type        = bool
  default     = true
}