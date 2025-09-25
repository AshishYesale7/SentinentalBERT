import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

// Test JWT token for demo purposes
const TEST_JWT_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvZmZpY2VyX2lkIjoidGVzdF91c2VyIiwicm9sZSI6ImFkbWluIiwicGVybWlzc2lvbnMiOlsibmxwOmFuYWx5emUiLCJubHA6c2VudGltZW50Iiwidmlld19yZXBvcnRzIiwiYWRtaW4iXSwiZXhwIjoxNzU4Njg3Njk4fQ.foU1cbemulfazsFFmjwnzROcV9FBN-7pLE7PU3MRgX8';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${TEST_JWT_TOKEN}`,
  },
});

export interface SentimentResult {
  positive: number;
  negative: number;
  neutral: number;
  confidence: number;
}

export interface BehavioralPattern {
  pattern_type: string;
  score: number;
  confidence: number;
  indicators: string[];
}

export interface AnalysisResult {
  text_id: number;
  sentiment: SentimentResult;
  behavioral_patterns: BehavioralPattern[];
  influence_score: number;
  language: string;
  processing_time_ms: number;
}

export interface BatchAnalysisResponse {
  results: AnalysisResult[];
  total_processing_time_ms: number;
  model_version: string;
  cache_hits: number;
  cache_misses: number;
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  gpu_available: boolean;
  memory_usage_mb: number;
  active_requests: number;
}

export const apiService = {
  // Health check
  async getHealth(): Promise<HealthResponse> {
    const response = await api.get('/health');
    return response.data;
  },

  // Analyze texts with full analysis
  async analyzeTexts(texts: string[]): Promise<BatchAnalysisResponse> {
    const response = await api.post('/analyze', { texts });
    return response.data;
  },

  // Analyze sentiment only
  async analyzeSentiment(texts: string[]): Promise<{ results: SentimentResult[]; model_version: string }> {
    const response = await api.post('/analyze/sentiment', { texts });
    return response.data;
  },

  // Get model information
  async getModels(): Promise<any> {
    const response = await api.get('/models');
    return response.data;
  },

  // Get metrics
  async getMetrics(): Promise<any> {
    const response = await api.get('/metrics');
    return response.data;
  },
};

export default apiService;