/*
 * SentinelBERT Social Media Ingestion Service - Main Entry Point
 * 
 * This is the main entry point for the high-performance Rust-based data ingestion service.
 * It handles concurrent data collection from multiple social media platforms with
 * rate limiting, error handling, and graceful shutdown capabilities.
 * 
 * Key Features:
 * - Asynchronous processing using Tokio runtime
 * - Structured logging with tracing
 * - Configuration management
 * - Graceful shutdown handling
 * - Multi-platform data ingestion
 * 
 * Author: SentinelBERT Team
 * License: MIT
 */

// External crate imports for error handling, CLI parsing, and async operations
use anyhow::Result;           // Simplified error handling with context
use clap::Parser;             // Command-line argument parsing
use std::sync::Arc;           // Thread-safe reference counting for shared data
use tokio::signal;            // Async signal handling for graceful shutdown
use tracing::{info, warn};    // Structured logging for observability

// Internal module declarations - each handles specific functionality
mod config;        // Configuration management and validation
mod ingestion;     // Core ingestion service logic
mod models;        // Data models and structures
mod platforms;     // Platform-specific API connectors
mod rate_limiter;  // Rate limiting to respect API quotas
mod storage;       // Database and cache storage operations

// Import main configuration and service types
use config::Config;
use ingestion::IngestionService;

/**
 * Command Line Interface structure
 * 
 * Defines the CLI arguments that can be passed to the ingestion service.
 * Uses clap derive macros for automatic argument parsing.
 */
#[derive(Parser)]
#[command(name = "sentinel-ingestion")]
#[command(about = "SentinelBERT Social Media Ingestion Service")]
struct Cli {
    /// Path to configuration file (TOML format)
    /// Default: config.toml in current directory
    #[arg(short, long, default_value = "config.toml")]
    config: String,
}

/**
 * Main application entry point
 * 
 * This function initializes the ingestion service with the following steps:
 * 1. Set up structured logging with tracing
 * 2. Parse command line arguments
 * 3. Load configuration from file
 * 4. Initialize the ingestion service
 * 5. Start background workers
 * 6. Wait for shutdown signal
 * 7. Perform graceful shutdown
 * 
 * Returns: Result<()> - Ok on successful shutdown, Err on critical failures
 */
#[tokio::main]
async fn main() -> Result<()> {
    // Initialize structured logging with environment-based filtering
    // This allows runtime log level control via RUST_LOG environment variable
    // Example: RUST_LOG=debug cargo run
    tracing_subscriber::fmt()
        .with_env_filter(tracing_subscriber::EnvFilter::from_default_env())
        .init();

    // Parse command line arguments using clap
    let cli = Cli::parse();
    
    // Load configuration from specified TOML file
    // This includes API keys, database connections, rate limits, etc.
    let config = Config::from_file(&cli.config)?;
    info!("Configuration loaded from {}", cli.config);

    // Initialize the main ingestion service with loaded configuration
    // Arc (Atomically Reference Counted) allows safe sharing across async tasks
    let ingestion_service = Arc::new(IngestionService::new(config).await?);
    info!("Ingestion service initialized");

    // Start ingestion workers in a separate async task
    // This allows the main thread to handle shutdown signals
    let service_clone = Arc::clone(&ingestion_service);
    let ingestion_handle = tokio::spawn(async move {
        // Start the ingestion service - this runs until shutdown
        if let Err(e) = service_clone.start().await {
            warn!("Ingestion service error: {}", e);
        }
    });

    // Wait for shutdown signal (Ctrl+C)
    // This blocks the main thread until SIGINT is received
    info!("SentinelBERT Ingestion Service started. Press Ctrl+C to shutdown.");
    signal::ctrl_c().await?;
    info!("Shutdown signal received");

    // Perform graceful shutdown
    // 1. Stop accepting new ingestion jobs
    // 2. Complete in-flight requests
    // 3. Close database connections
    // 4. Clean up resources
    ingestion_service.shutdown().await?;
    ingestion_handle.abort();

    info!("SentinelBERT Ingestion Service stopped");
    Ok(())
}