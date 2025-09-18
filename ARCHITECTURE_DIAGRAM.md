# SentinelBERT System Architecture Diagrams

## High-Level System Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        X[X.com API]
        IG[Instagram API]
        RD[Reddit API]
        FB[Facebook API]
        TG[Telegram API]
    end

    subgraph "Ingestion Layer (Rust)"
        API_SCRAPER[API Scrapers]
        RATE_LIMITER[Rate Limiter]
        DATA_VALIDATOR[Data Validator]
        ETL_PIPELINE[ETL Pipeline]
    end

    subgraph "Message Queue"
        KAFKA[Apache Kafka]
        REDIS_QUEUE[Redis Queue]
    end

    subgraph "Processing Layer (Python)"
        NLP_SERVICE[NLP Service]
        BERT_MODEL[BERT Model]
        SENTIMENT_ANALYZER[Sentiment Analyzer]
        BEHAVIOR_DETECTOR[Behavior Pattern Detector]
        INFLUENCE_CALCULATOR[Influence Calculator]
    end

    subgraph "Storage Layer"
        POSTGRES[(PostgreSQL)]
        ELASTICSEARCH[(ElasticSearch)]
        REDIS_CACHE[(Redis Cache)]
        OBJECT_STORAGE[(Object Storage)]
    end

    subgraph "Backend Services (Spring Boot)"
        API_GATEWAY[API Gateway]
        AUTH_SERVICE[Auth Service]
        QUERY_SERVICE[Query Service]
        ANALYTICS_SERVICE[Analytics Service]
        USER_SERVICE[User Service]
        NOTIFICATION_SERVICE[Notification Service]
    end

    subgraph "Frontend (React)"
        DASHBOARD[Dashboard]
        TIMELINE_VIEW[Timeline View]
        ANALYTICS_PANEL[Analytics Panel]
        SEARCH_INTERFACE[Search Interface]
        ADMIN_PANEL[Admin Panel]
    end

    subgraph "Security & Monitoring"
        AUDIT_LOGGER[Audit Logger]
        PROMETHEUS[Prometheus]
        GRAFANA[Grafana]
        ALERTMANAGER[AlertManager]
    end

    %% Data Flow
    X --> API_SCRAPER
    IG --> API_SCRAPER
    RD --> API_SCRAPER
    FB --> API_SCRAPER
    TG --> API_SCRAPER

    API_SCRAPER --> RATE_LIMITER
    RATE_LIMITER --> DATA_VALIDATOR
    DATA_VALIDATOR --> ETL_PIPELINE
    ETL_PIPELINE --> KAFKA

    KAFKA --> NLP_SERVICE
    NLP_SERVICE --> BERT_MODEL
    BERT_MODEL --> SENTIMENT_ANALYZER
    BERT_MODEL --> BEHAVIOR_DETECTOR
    BERT_MODEL --> INFLUENCE_CALCULATOR

    SENTIMENT_ANALYZER --> POSTGRES
    BEHAVIOR_DETECTOR --> POSTGRES
    INFLUENCE_CALCULATOR --> POSTGRES
    
    ETL_PIPELINE --> ELASTICSEARCH
    NLP_SERVICE --> REDIS_CACHE

    POSTGRES --> QUERY_SERVICE
    ELASTICSEARCH --> QUERY_SERVICE
    REDIS_CACHE --> QUERY_SERVICE

    API_GATEWAY --> AUTH_SERVICE
    API_GATEWAY --> QUERY_SERVICE
    API_GATEWAY --> ANALYTICS_SERVICE
    API_GATEWAY --> USER_SERVICE

    QUERY_SERVICE --> DASHBOARD
    ANALYTICS_SERVICE --> ANALYTICS_PANEL
    QUERY_SERVICE --> TIMELINE_VIEW
    AUTH_SERVICE --> SEARCH_INTERFACE

    %% Monitoring
    API_GATEWAY --> AUDIT_LOGGER
    NLP_SERVICE --> PROMETHEUS
    QUERY_SERVICE --> PROMETHEUS
    PROMETHEUS --> GRAFANA
    PROMETHEUS --> ALERTMANAGER

    classDef rustService fill:#dea584
    classDef pythonService fill:#3776ab
    classDef javaService fill:#ed8b00
    classDef reactService fill:#61dafb
    classDef database fill:#336791
    classDef queue fill:#ff6b6b

    class API_SCRAPER,RATE_LIMITER,DATA_VALIDATOR,ETL_PIPELINE rustService
    class NLP_SERVICE,BERT_MODEL,SENTIMENT_ANALYZER,BEHAVIOR_DETECTOR,INFLUENCE_CALCULATOR pythonService
    class API_GATEWAY,AUTH_SERVICE,QUERY_SERVICE,ANALYTICS_SERVICE,USER_SERVICE,NOTIFICATION_SERVICE javaService
    class DASHBOARD,TIMELINE_VIEW,ANALYTICS_PANEL,SEARCH_INTERFACE,ADMIN_PANEL reactService
    class POSTGRES,ELASTICSEARCH,REDIS_CACHE,OBJECT_STORAGE database
    class KAFKA,REDIS_QUEUE queue
```

## Data Processing Pipeline

```mermaid
sequenceDiagram
    participant DS as Data Sources
    participant RS as Rust Ingestion
    participant K as Kafka
    participant PS as Python NLP
    participant DB as Database
    participant SB as Spring Boot
    participant FE as Frontend

    DS->>RS: Raw social media data
    RS->>RS: Rate limiting & validation
    RS->>K: Publish to queue
    K->>PS: Consume messages
    PS->>PS: BERT analysis
    PS->>DB: Store results
    
    FE->>SB: User search query
    SB->>DB: Query data
    DB->>SB: Return results
    SB->>PS: Request analysis
    PS->>SB: Analysis results
    SB->>FE: Formatted response
    
    Note over PS,DB: Real-time processing
    Note over SB,FE: Interactive dashboard
```

## Microservices Architecture

```mermaid
graph LR
    subgraph "API Gateway Layer"
        GATEWAY[Spring Cloud Gateway]
        LB[Load Balancer]
    end

    subgraph "Authentication"
        AUTH[Auth Service]
        JWT[JWT Service]
        RBAC[RBAC Service]
    end

    subgraph "Core Services"
        QUERY[Query Service]
        ANALYTICS[Analytics Service]
        USER[User Service]
        EXPORT[Export Service]
    end

    subgraph "Processing Services"
        INGESTION[Ingestion Service]
        NLP[NLP Service]
        NOTIFICATION[Notification Service]
    end

    subgraph "Data Layer"
        POSTGRES[(PostgreSQL)]
        ELASTIC[(ElasticSearch)]
        REDIS[(Redis)]
    end

    LB --> GATEWAY
    GATEWAY --> AUTH
    GATEWAY --> QUERY
    GATEWAY --> ANALYTICS
    GATEWAY --> USER
    GATEWAY --> EXPORT

    AUTH --> JWT
    AUTH --> RBAC
    
    QUERY --> POSTGRES
    QUERY --> ELASTIC
    QUERY --> REDIS
    
    ANALYTICS --> POSTGRES
    ANALYTICS --> ELASTIC
    
    INGESTION --> NLP
    NLP --> POSTGRES
    NLP --> REDIS

    classDef gateway fill:#ff9999
    classDef auth fill:#99ccff
    classDef core fill:#99ff99
    classDef processing fill:#ffcc99
    classDef data fill:#cc99ff

    class GATEWAY,LB gateway
    class AUTH,JWT,RBAC auth
    class QUERY,ANALYTICS,USER,EXPORT core
    class INGESTION,NLP,NOTIFICATION processing
    class POSTGRES,ELASTIC,REDIS data
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Ingress"
            NGINX[NGINX Ingress]
            CERT[Cert Manager]
        end

        subgraph "Application Pods"
            subgraph "Frontend Tier"
                REACT1[React Pod 1]
                REACT2[React Pod 2]
                REACT3[React Pod 3]
            end

            subgraph "Backend Tier"
                SPRING1[Spring Boot Pod 1]
                SPRING2[Spring Boot Pod 2]
                SPRING3[Spring Boot Pod 3]
            end

            subgraph "Processing Tier"
                RUST1[Rust Pod 1]
                RUST2[Rust Pod 2]
                PYTHON1[Python Pod 1]
                PYTHON2[Python Pod 2]
            end
        end

        subgraph "Data Tier"
            POSTGRES_MASTER[(PostgreSQL Master)]
            POSTGRES_REPLICA[(PostgreSQL Replica)]
            ELASTIC_CLUSTER[(ElasticSearch Cluster)]
            REDIS_CLUSTER[(Redis Cluster)]
        end

        subgraph "Monitoring"
            PROMETHEUS[Prometheus]
            GRAFANA[Grafana]
            JAEGER[Jaeger Tracing]
        end
    end

    subgraph "External Services"
        SOCIAL_APIS[Social Media APIs]
        OBJECT_STORE[Object Storage]
        EMAIL_SERVICE[Email Service]
    end

    NGINX --> REACT1
    NGINX --> REACT2
    NGINX --> REACT3

    REACT1 --> SPRING1
    REACT2 --> SPRING2
    REACT3 --> SPRING3

    SPRING1 --> POSTGRES_MASTER
    SPRING2 --> POSTGRES_REPLICA
    SPRING3 --> POSTGRES_MASTER

    RUST1 --> SOCIAL_APIS
    RUST2 --> SOCIAL_APIS
    RUST1 --> PYTHON1
    RUST2 --> PYTHON2

    PYTHON1 --> POSTGRES_MASTER
    PYTHON2 --> POSTGRES_MASTER

    SPRING1 --> ELASTIC_CLUSTER
    SPRING2 --> ELASTIC_CLUSTER
    SPRING3 --> ELASTIC_CLUSTER

    SPRING1 --> REDIS_CLUSTER
    SPRING2 --> REDIS_CLUSTER
    SPRING3 --> REDIS_CLUSTER

    classDef frontend fill:#61dafb
    classDef backend fill:#ed8b00
    classDef processing fill:#dea584,color:#000
    classDef database fill:#336791
    classDef monitoring fill:#ff6b6b

    class REACT1,REACT2,REACT3 frontend
    class SPRING1,SPRING2,SPRING3 backend
    class RUST1,RUST2,PYTHON1,PYTHON2 processing
    class POSTGRES_MASTER,POSTGRES_REPLICA,ELASTIC_CLUSTER,REDIS_CLUSTER database
    class PROMETHEUS,GRAFANA,JAEGER monitoring
```

## Security Architecture

```mermaid
graph TB
    subgraph "External Access"
        USER[Investigators]
        ADMIN[System Admins]
    end

    subgraph "Security Perimeter"
        WAF[Web Application Firewall]
        DDoS[DDoS Protection]
        RATE_LIMIT[Rate Limiting]
    end

    subgraph "Authentication Layer"
        SSO[Single Sign-On]
        MFA[Multi-Factor Auth]
        JWT_SERVICE[JWT Service]
    end

    subgraph "Authorization Layer"
        RBAC_SERVICE[RBAC Service]
        POLICY_ENGINE[Policy Engine]
        AUDIT_SERVICE[Audit Service]
    end

    subgraph "Application Security"
        INPUT_VALIDATION[Input Validation]
        OUTPUT_ENCODING[Output Encoding]
        CSRF_PROTECTION[CSRF Protection]
        XSS_PROTECTION[XSS Protection]
    end

    subgraph "Data Security"
        ENCRYPTION_AT_REST[Encryption at Rest]
        ENCRYPTION_IN_TRANSIT[Encryption in Transit]
        DATA_MASKING[Data Masking]
        KEY_MANAGEMENT[Key Management]
    end

    subgraph "Network Security"
        VPC[Virtual Private Cloud]
        NETWORK_SEGMENTATION[Network Segmentation]
        FIREWALL_RULES[Firewall Rules]
        VPN[VPN Access]
    end

    subgraph "Monitoring & Compliance"
        SIEM[SIEM System]
        LOG_AGGREGATION[Log Aggregation]
        COMPLIANCE_REPORTING[Compliance Reporting]
        THREAT_DETECTION[Threat Detection]
    end

    USER --> WAF
    ADMIN --> WAF
    WAF --> DDoS
    DDoS --> RATE_LIMIT
    RATE_LIMIT --> SSO
    SSO --> MFA
    MFA --> JWT_SERVICE
    JWT_SERVICE --> RBAC_SERVICE
    RBAC_SERVICE --> POLICY_ENGINE
    POLICY_ENGINE --> AUDIT_SERVICE

    AUDIT_SERVICE --> INPUT_VALIDATION
    INPUT_VALIDATION --> OUTPUT_ENCODING
    OUTPUT_ENCODING --> CSRF_PROTECTION
    CSRF_PROTECTION --> XSS_PROTECTION

    XSS_PROTECTION --> ENCRYPTION_AT_REST
    ENCRYPTION_AT_REST --> ENCRYPTION_IN_TRANSIT
    ENCRYPTION_IN_TRANSIT --> DATA_MASKING
    DATA_MASKING --> KEY_MANAGEMENT

    KEY_MANAGEMENT --> VPC
    VPC --> NETWORK_SEGMENTATION
    NETWORK_SEGMENTATION --> FIREWALL_RULES
    FIREWALL_RULES --> VPN

    VPN --> SIEM
    SIEM --> LOG_AGGREGATION
    LOG_AGGREGATION --> COMPLIANCE_REPORTING
    COMPLIANCE_REPORTING --> THREAT_DETECTION

    classDef security fill:#ff6b6b
    classDef auth fill:#4ecdc4
    classDef data fill:#45b7d1
    classDef network fill:#96ceb4
    classDef monitoring fill:#feca57

    class WAF,DDoS,RATE_LIMIT security
    class SSO,MFA,JWT_SERVICE,RBAC_SERVICE,POLICY_ENGINE auth
    class ENCRYPTION_AT_REST,ENCRYPTION_IN_TRANSIT,DATA_MASKING,KEY_MANAGEMENT data
    class VPC,NETWORK_SEGMENTATION,FIREWALL_RULES,VPN network
    class SIEM,LOG_AGGREGATION,COMPLIANCE_REPORTING,THREAT_DETECTION monitoring
```

## ML/NLP Pipeline Architecture

```mermaid
graph LR
    subgraph "Data Preprocessing"
        TEXT_CLEAN[Text Cleaning]
        TOKENIZATION[Tokenization]
        NORMALIZATION[Normalization]
    end

    subgraph "Feature Extraction"
        BERT_EMBEDDINGS[BERT Embeddings]
        USER_FEATURES[User Features]
        TEMPORAL_FEATURES[Temporal Features]
        NETWORK_FEATURES[Network Features]
    end

    subgraph "Model Ensemble"
        SENTIMENT_MODEL[Sentiment Model]
        BEHAVIOR_MODEL[Behavior Model]
        INFLUENCE_MODEL[Influence Model]
        TREND_MODEL[Trend Model]
    end

    subgraph "Post-Processing"
        SCORE_AGGREGATION[Score Aggregation]
        CONFIDENCE_CALCULATION[Confidence Calculation]
        RESULT_VALIDATION[Result Validation]
    end

    subgraph "Model Serving"
        MODEL_CACHE[Model Cache]
        BATCH_INFERENCE[Batch Inference]
        REAL_TIME_INFERENCE[Real-time Inference]
        A_B_TESTING[A/B Testing]
    end

    TEXT_CLEAN --> TOKENIZATION
    TOKENIZATION --> NORMALIZATION
    NORMALIZATION --> BERT_EMBEDDINGS

    BERT_EMBEDDINGS --> SENTIMENT_MODEL
    USER_FEATURES --> BEHAVIOR_MODEL
    TEMPORAL_FEATURES --> INFLUENCE_MODEL
    NETWORK_FEATURES --> TREND_MODEL

    SENTIMENT_MODEL --> SCORE_AGGREGATION
    BEHAVIOR_MODEL --> SCORE_AGGREGATION
    INFLUENCE_MODEL --> SCORE_AGGREGATION
    TREND_MODEL --> SCORE_AGGREGATION

    SCORE_AGGREGATION --> CONFIDENCE_CALCULATION
    CONFIDENCE_CALCULATION --> RESULT_VALIDATION

    RESULT_VALIDATION --> MODEL_CACHE
    MODEL_CACHE --> BATCH_INFERENCE
    MODEL_CACHE --> REAL_TIME_INFERENCE
    MODEL_CACHE --> A_B_TESTING

    classDef preprocessing fill:#ffd93d
    classDef features fill:#6bcf7f
    classDef models fill:#4d96ff
    classDef postprocessing fill:#ff6b6b
    classDef serving fill:#a8e6cf

    class TEXT_CLEAN,TOKENIZATION,NORMALIZATION preprocessing
    class BERT_EMBEDDINGS,USER_FEATURES,TEMPORAL_FEATURES,NETWORK_FEATURES features
    class SENTIMENT_MODEL,BEHAVIOR_MODEL,INFLUENCE_MODEL,TREND_MODEL models
    class SCORE_AGGREGATION,CONFIDENCE_CALCULATION,RESULT_VALIDATION postprocessing
    class MODEL_CACHE,BATCH_INFERENCE,REAL_TIME_INFERENCE,A_B_TESTING serving
```