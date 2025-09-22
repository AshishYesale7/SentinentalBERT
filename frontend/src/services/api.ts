import axios from 'axios';
import authService from './auth';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(async (config) => {
  const token = await authService.getValidToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear invalid token
      authService.clearToken();
      console.error('Authentication failed. Please refresh the page.');
    }
    return Promise.reject(error);
  }
);

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