# Code Models (Codey) Setup Guide for SentinentalBERT

<div align="center">

![Codey](https://img.shields.io/badge/Codey-AI%20Models-FF6F00?style=for-the-badge&logo=google&logoColor=white)
![Generative AI](https://img.shields.io/badge/Generative%20AI-Code%20Generation-4285F4?style=for-the-badge&logo=openai&logoColor=white)

**Advanced Code Generation, Chat, and Completion with Google's Codey Models**

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🔧 Prerequisites](#-prerequisites)
- [🚀 Step-by-Step Setup](#-step-by-step-setup)
- [💻 Code Generation Setup](#-code-generation-setup)
- [💬 Code Chat Setup](#-code-chat-setup)
- [⚡ Code Completion Setup](#-code-completion-setup)
- [📊 Usage Optimization](#-usage-optimization)
- [🧪 Testing & Validation](#-testing--validation)
- [🔍 Monitoring](#-monitoring)
- [🆘 Troubleshooting](#-troubleshooting)

---

## 🎯 Overview

This guide configures Google's Codey models for SentinentalBERT, enabling advanced code generation, chat assistance, and intelligent code completion. Your configuration supports 1000 requests per day for each service type.

### 🌟 Codey Models Configuration

Based on your specifications:

| Model Type | Daily Requests | Peak RPM | Avg Input | Avg Output | Use Case |
|------------|----------------|----------|-----------|------------|----------|
| **Code Generation** | 1,000 | 10 | 500 chars | 8,000 chars | Generate complete functions/classes |
| **Code Chat** | 1,000 | 100 | 100 chars | 2,000 chars | Interactive coding assistance |
| **Code Completion** | 1,000 | 100 | 1,000 chars | 600 chars | Auto-complete code snippets |

### 💰 Cost Optimization Features

- **Batch Discounts**: Enabled for Code Generation
- **Request Pooling**: Optimize API calls
- **Caching**: Reduce redundant requests
- **Rate Limiting**: Stay within quotas

### ⏱️ Estimated Setup Time: 20-25 minutes

---

## 🔧 Prerequisites

### ✅ Required Setup

1. **GCP Project**: With Vertex AI API enabled
2. **Service Account**: With appropriate permissions
3. **Python Environment**: Python 3.8+ with required packages
4. **Authentication**: Service account key configured

### 📦 Install Required Packages

```bash
# Install Google Cloud AI Platform SDK
pip install google-cloud-aiplatform

# Install additional dependencies
pip install google-auth google-auth-oauthlib google-auth-httplib2
pip install requests python-dotenv

# For advanced features
pip install asyncio aiohttp tenacity
```

### 🔑 Verify Prerequisites

```bash
# Check authentication
gcloud auth list

# Verify project
gcloud config get-value project

# Check Vertex AI API
gcloud services list --enabled --filter="name:aiplatform.googleapis.com"
```

---

## 🚀 Step-by-Step Setup

### Step 1: Enable Vertex AI Generative AI APIs

```bash
# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable ml.googleapis.com
gcloud services enable compute.googleapis.com

# Verify API enablement
gcloud services list --enabled --filter="name:aiplatform.googleapis.com"
```

### Step 2: Set Up Authentication

```bash
# Set environment variables
export PROJECT_ID="your-sentinelbert-project"
export LOCATION="us-central1"  # Codey models region
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Verify authentication
gcloud auth application-default print-access-token
```

### Step 3: Create Codey Configuration

```python
# config/codey_config.py
"""
Codey Models Configuration for SentinentalBERT
Optimized for your 1000 requests/day per model configuration
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class CodeyConfig:
    """Configuration class for Codey models"""
    
    # Project configuration
    project_id: str = os.getenv("GCP_PROJECT_ID", "your-sentinelbert-project")
    location: str = os.getenv("CODEY_LOCATION", "us-central1")
    
    # Model configurations
    generation_model: str = "code-bison@001"
    chat_model: str = "codechat-bison@001"
    completion_model: str = "code-gecko@001"
    
    # Rate limiting (based on your configuration)
    generation_requests_per_day: int = 1000
    generation_peak_rpm: int = 10
    chat_requests_per_day: int = 1000
    chat_peak_rpm: int = 100
    completion_requests_per_day: int = 1000
    completion_peak_rpm: int = 100
    
    # Request characteristics
    generation_avg_input_chars: int = 500
    generation_avg_output_chars: int = 8000
    chat_avg_input_chars: int = 100
    chat_avg_output_chars: int = 2000
    completion_avg_input_chars: int = 1000
    completion_avg_output_chars: int = 600
    
    # API parameters
    temperature: float = 0.2
    max_output_tokens: int = 2048
    top_p: float = 0.8
    top_k: int = 40
    
    # Optimization settings
    batch_discounts: bool = True
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600
    
    # Monitoring
    enable_metrics: bool = True
    log_requests: bool = True

# Global configuration instance
CODEY_CONFIG = CodeyConfig()
```

---

## 💻 Code Generation Setup

### Step 4: Implement Code Generation Service

```python
# services/codey/code_generation.py
"""
Code Generation Service using Codey models
Handles automated code generation with optimization and caching
"""

import asyncio
import hashlib
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CodeGenerationRequest:
    """Request structure for code generation"""
    prompt: str
    language: str = "python"
    max_tokens: int = 2048
    temperature: float = 0.2
    context: Optional[str] = None
    requirements: Optional[List[str]] = None

@dataclass
class CodeGenerationResponse:
    """Response structure for code generation"""
    generated_code: str
    language: str
    confidence: float
    execution_time_ms: float
    tokens_used: int
    cached: bool = False

class CodeGenerationService:
    """
    Service for generating code using Codey models
    Optimized for 1000 requests/day with batch processing
    """
    
    def __init__(self, config: CodeyConfig):
        self.config = config
        self.client = None
        self.cache = {}  # Simple in-memory cache
        self.request_count = 0
        self.daily_limit = config.generation_requests_per_day
        
        # Initialize Vertex AI
        aiplatform.init(
            project=config.project_id,
            location=config.location
        )
        
        logger.info(f"Code Generation Service initialized for project: {config.project_id}")
    
    def _get_cache_key(self, request: CodeGenerationRequest) -> str:
        """Generate cache key for request"""
        content = f"{request.prompt}_{request.language}_{request.temperature}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _check_rate_limit(self) -> bool:
        """Check if within daily rate limit"""
        if self.request_count >= self.daily_limit:
            logger.warning(f"Daily rate limit reached: {self.request_count}/{self.daily_limit}")
            return False
        return True
    
    async def generate_code(self, request: CodeGenerationRequest) -> CodeGenerationResponse:
        """
        Generate code using Codey model
        
        Args:
            request: Code generation request
            
        Returns:
            CodeGenerationResponse with generated code
        """
        start_time = time.time()
        
        # Check rate limit
        if not self._check_rate_limit():
            raise Exception("Daily rate limit exceeded")
        
        # Check cache
        cache_key = self._get_cache_key(request)
        if self.config.enable_caching and cache_key in self.cache:
            cached_response = self.cache[cache_key]
            cached_response.cached = True
            logger.info("Returning cached response")
            return cached_response
        
        try:
            # Prepare prompt
            full_prompt = self._prepare_prompt(request)
            
            # Call Vertex AI
            response = await self._call_vertex_ai(full_prompt, request)
            
            # Process response
            generated_code = self._extract_code(response)
            
            # Create response object
            execution_time = (time.time() - start_time) * 1000
            result = CodeGenerationResponse(
                generated_code=generated_code,
                language=request.language,
                confidence=0.85,  # Placeholder - would be calculated from model response
                execution_time_ms=execution_time,
                tokens_used=len(generated_code.split()),
                cached=False
            )
            
            # Cache response
            if self.config.enable_caching:
                self.cache[cache_key] = result
            
            # Update metrics
            self.request_count += 1
            
            logger.info(f"Code generated successfully in {execution_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}")
            raise
    
    def _prepare_prompt(self, request: CodeGenerationRequest) -> str:
        """Prepare optimized prompt for code generation"""
        
        prompt_parts = []
        
        # Add context if provided
        if request.context:
            prompt_parts.append(f"Context: {request.context}")
        
        # Add requirements
        if request.requirements:
            requirements_text = "\n".join(f"- {req}" for req in request.requirements)
            prompt_parts.append(f"Requirements:\n{requirements_text}")
        
        # Add main prompt
        prompt_parts.append(f"Generate {request.language} code for the following:")
        prompt_parts.append(request.prompt)
        
        # Add formatting instructions
        prompt_parts.append(f"Please provide clean, well-commented {request.language} code.")
        
        return "\n\n".join(prompt_parts)
    
    async def _call_vertex_ai(self, prompt: str, request: CodeGenerationRequest) -> str:
        """Call Vertex AI Codey model"""
        
        # Initialize prediction client
        client_options = {"api_endpoint": f"{self.config.location}-aiplatform.googleapis.com"}
        client = aip.PredictionServiceClient(client_options=client_options)
        
        # Prepare request
        endpoint = f"projects/{self.config.project_id}/locations/{self.config.location}/publishers/google/models/{self.config.generation_model}"
        
        instance = {
            "prefix": prompt,
            "suffix": "",
            "temperature": request.temperature,
            "maxOutputTokens": request.max_tokens,
            "topP": self.config.top_p,
            "topK": self.config.top_k
        }
        
        instances = [instance]
        parameters = {}
        
        # Make prediction
        response = client.predict(
            endpoint=endpoint,
            instances=instances,
            parameters=parameters
        )
        
        return response.predictions[0]["content"]
    
    def _extract_code(self, response: str) -> str:
        """Extract and clean generated code"""
        
        # Remove markdown code blocks if present
        if "```" in response:
            parts = response.split("```")
            if len(parts) >= 3:
                # Extract code from markdown block
                code_block = parts[1]
                # Remove language identifier if present
                lines = code_block.strip().split('\n')
                if lines[0].strip() in ['python', 'javascript', 'java', 'cpp', 'c', 'go', 'rust']:
                    return '\n'.join(lines[1:])
                return code_block.strip()
        
        return response.strip()
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return {
            "requests_today": self.request_count,
            "daily_limit": self.daily_limit,
            "remaining_requests": self.daily_limit - self.request_count,
            "cache_size": len(self.cache),
            "utilization_percent": (self.request_count / self.daily_limit) * 100
        }

# Example usage
async def example_code_generation():
    """Example of using the code generation service"""
    
    config = CodeyConfig()
    service = CodeGenerationService(config)
    
    # Example request
    request = CodeGenerationRequest(
        prompt="Create a function to calculate sentiment score from text",
        language="python",
        context="This is for a sentiment analysis application",
        requirements=[
            "Use numpy for calculations",
            "Include error handling",
            "Add type hints",
            "Include docstring"
        ]
    )
    
    try:
        response = await service.generate_code(request)
        print(f"Generated Code:\n{response.generated_code}")
        print(f"Execution time: {response.execution_time_ms:.2f}ms")
        print(f"Tokens used: {response.tokens_used}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(example_code_generation())
```

### Step 5: Create Code Generation API Endpoint

```python
# api/endpoints/code_generation.py
"""
FastAPI endpoints for code generation
Integrates with SentinentalBERT backend
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import asyncio

from services.codey.code_generation import CodeGenerationService, CodeGenerationRequest
from config.codey_config import CODEY_CONFIG

router = APIRouter(prefix="/api/v1/codey", tags=["Code Generation"])

# Initialize service
code_gen_service = CodeGenerationService(CODEY_CONFIG)

class CodeGenerationAPIRequest(BaseModel):
    """API request model for code generation"""
    prompt: str
    language: str = "python"
    max_tokens: int = 2048
    temperature: float = 0.2
    context: Optional[str] = None
    requirements: Optional[List[str]] = None

class CodeGenerationAPIResponse(BaseModel):
    """API response model for code generation"""
    success: bool
    generated_code: str
    language: str
    confidence: float
    execution_time_ms: float
    tokens_used: int
    cached: bool
    usage_stats: dict

@router.post("/generate", response_model=CodeGenerationAPIResponse)
async def generate_code(request: CodeGenerationAPIRequest):
    """
    Generate code using Codey models
    
    This endpoint generates code based on natural language prompts
    using Google's Codey models optimized for your usage patterns.
    """
    
    try:
        # Convert API request to service request
        service_request = CodeGenerationRequest(
            prompt=request.prompt,
            language=request.language,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            context=request.context,
            requirements=request.requirements
        )
        
        # Generate code
        response = await code_gen_service.generate_code(service_request)
        
        # Get usage stats
        usage_stats = code_gen_service.get_usage_stats()
        
        return CodeGenerationAPIResponse(
            success=True,
            generated_code=response.generated_code,
            language=response.language,
            confidence=response.confidence,
            execution_time_ms=response.execution_time_ms,
            tokens_used=response.tokens_used,
            cached=response.cached,
            usage_stats=usage_stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage")
async def get_usage_stats():
    """Get current usage statistics for code generation"""
    return code_gen_service.get_usage_stats()
```

---

## 💬 Code Chat Setup

### Step 6: Implement Code Chat Service

```python
# services/codey/code_chat.py
"""
Code Chat Service using Codey models
Provides interactive coding assistance and Q&A
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip
import logging

logger = logging.getLogger(__name__)

@dataclass
class ChatMessage:
    """Individual chat message"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: float

@dataclass
class CodeChatRequest:
    """Request structure for code chat"""
    message: str
    conversation_history: List[ChatMessage]
    language: str = "python"
    context: Optional[str] = None

@dataclass
class CodeChatResponse:
    """Response structure for code chat"""
    response: str
    conversation_id: str
    confidence: float
    execution_time_ms: float
    tokens_used: int

class CodeChatService:
    """
    Service for interactive code chat using Codey models
    Optimized for 1000 requests/day with conversation management
    """
    
    def __init__(self, config: CodeyConfig):
        self.config = config
        self.conversations = {}  # Store conversation history
        self.request_count = 0
        self.daily_limit = config.chat_requests_per_day
        
        # Initialize Vertex AI
        aiplatform.init(
            project=config.project_id,
            location=config.location
        )
        
        logger.info(f"Code Chat Service initialized")
    
    async def chat(self, request: CodeChatRequest) -> CodeChatResponse:
        """
        Process chat message and generate response
        
        Args:
            request: Code chat request
            
        Returns:
            CodeChatResponse with assistant's reply
        """
        start_time = time.time()
        
        # Check rate limit
        if self.request_count >= self.daily_limit:
            raise Exception("Daily rate limit exceeded")
        
        try:
            # Prepare conversation context
            conversation_context = self._prepare_conversation_context(request)
            
            # Call Vertex AI
            response = await self._call_vertex_ai_chat(conversation_context, request)
            
            # Create response
            execution_time = (time.time() - start_time) * 1000
            result = CodeChatResponse(
                response=response,
                conversation_id="chat_" + str(int(time.time())),
                confidence=0.90,
                execution_time_ms=execution_time,
                tokens_used=len(response.split())
            )
            
            # Update metrics
            self.request_count += 1
            
            logger.info(f"Chat response generated in {execution_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Chat failed: {str(e)}")
            raise
    
    def _prepare_conversation_context(self, request: CodeChatRequest) -> str:
        """Prepare conversation context for the model"""
        
        context_parts = []
        
        # Add system context
        context_parts.append("You are a helpful coding assistant specialized in software development.")
        
        if request.context:
            context_parts.append(f"Context: {request.context}")
        
        # Add conversation history
        if request.conversation_history:
            context_parts.append("Conversation history:")
            for msg in request.conversation_history[-5:]:  # Last 5 messages
                role = "Human" if msg.role == "user" else "Assistant"
                context_parts.append(f"{role}: {msg.content}")
        
        # Add current message
        context_parts.append(f"Human: {request.message}")
        context_parts.append("Assistant:")
        
        return "\n".join(context_parts)
    
    async def _call_vertex_ai_chat(self, context: str, request: CodeChatRequest) -> str:
        """Call Vertex AI Codey chat model"""
        
        client_options = {"api_endpoint": f"{self.config.location}-aiplatform.googleapis.com"}
        client = aip.PredictionServiceClient(client_options=client_options)
        
        endpoint = f"projects/{self.config.project_id}/locations/{self.config.location}/publishers/google/models/{self.config.chat_model}"
        
        instance = {
            "messages": [{"content": context}],
            "temperature": self.config.temperature,
            "maxOutputTokens": self.config.max_output_tokens,
            "topP": self.config.top_p,
            "topK": self.config.top_k
        }
        
        response = client.predict(
            endpoint=endpoint,
            instances=[instance],
            parameters={}
        )
        
        return response.predictions[0]["candidates"][0]["content"]

# API endpoint for code chat
@router.post("/chat", response_model=CodeChatResponse)
async def code_chat(request: CodeChatAPIRequest):
    """Interactive code chat endpoint"""
    
    service_request = CodeChatRequest(
        message=request.message,
        conversation_history=request.conversation_history,
        language=request.language,
        context=request.context
    )
    
    response = await code_chat_service.chat(service_request)
    return response
```

---

## ⚡ Code Completion Setup

### Step 7: Implement Code Completion Service

```python
# services/codey/code_completion.py
"""
Code Completion Service using Codey models
Provides intelligent code completion and suggestions
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic as aip
import logging

logger = logging.getLogger(__name__)

@dataclass
class CodeCompletionRequest:
    """Request structure for code completion"""
    prefix: str  # Code before cursor
    suffix: str = ""  # Code after cursor (optional)
    language: str = "python"
    max_completions: int = 3
    context: Optional[str] = None

@dataclass
class CodeCompletionSuggestion:
    """Individual completion suggestion"""
    completion: str
    confidence: float
    type: str  # "function", "variable", "class", etc.

@dataclass
class CodeCompletionResponse:
    """Response structure for code completion"""
    suggestions: List[CodeCompletionSuggestion]
    execution_time_ms: float
    tokens_used: int

class CodeCompletionService:
    """
    Service for code completion using Codey models
    Optimized for 1000 requests/day with fast response times
    """
    
    def __init__(self, config: CodeyConfig):
        self.config = config
        self.request_count = 0
        self.daily_limit = config.completion_requests_per_day
        
        # Initialize Vertex AI
        aiplatform.init(
            project=config.project_id,
            location=config.location
        )
        
        logger.info(f"Code Completion Service initialized")
    
    async def complete_code(self, request: CodeCompletionRequest) -> CodeCompletionResponse:
        """
        Generate code completions
        
        Args:
            request: Code completion request
            
        Returns:
            CodeCompletionResponse with suggestions
        """
        start_time = time.time()
        
        # Check rate limit
        if self.request_count >= self.daily_limit:
            raise Exception("Daily rate limit exceeded")
        
        try:
            # Call Vertex AI
            completions = await self._call_vertex_ai_completion(request)
            
            # Process completions
            suggestions = self._process_completions(completions)
            
            # Create response
            execution_time = (time.time() - start_time) * 1000
            result = CodeCompletionResponse(
                suggestions=suggestions,
                execution_time_ms=execution_time,
                tokens_used=sum(len(s.completion.split()) for s in suggestions)
            )
            
            # Update metrics
            self.request_count += 1
            
            logger.info(f"Code completion generated in {execution_time:.2f}ms")
            return result
            
        except Exception as e:
            logger.error(f"Code completion failed: {str(e)}")
            raise
    
    async def _call_vertex_ai_completion(self, request: CodeCompletionRequest) -> List[str]:
        """Call Vertex AI Codey completion model"""
        
        client_options = {"api_endpoint": f"{self.config.location}-aiplatform.googleapis.com"}
        client = aip.PredictionServiceClient(client_options=client_options)
        
        endpoint = f"projects/{self.config.project_id}/locations/{self.config.location}/publishers/google/models/{self.config.completion_model}"
        
        instance = {
            "prefix": request.prefix,
            "suffix": request.suffix,
            "temperature": 0.1,  # Lower temperature for completion
            "maxOutputTokens": 200,  # Shorter completions
            "candidateCount": request.max_completions
        }
        
        response = client.predict(
            endpoint=endpoint,
            instances=[instance],
            parameters={}
        )
        
        return [pred["content"] for pred in response.predictions]
    
    def _process_completions(self, completions: List[str]) -> List[CodeCompletionSuggestion]:
        """Process raw completions into structured suggestions"""
        
        suggestions = []
        for i, completion in enumerate(completions):
            # Determine completion type (simplified)
            completion_type = "code"
            if "def " in completion:
                completion_type = "function"
            elif "class " in completion:
                completion_type = "class"
            elif "import " in completion:
                completion_type = "import"
            
            suggestion = CodeCompletionSuggestion(
                completion=completion.strip(),
                confidence=0.9 - (i * 0.1),  # Decreasing confidence
                type=completion_type
            )
            suggestions.append(suggestion)
        
        return suggestions

# API endpoint for code completion
@router.post("/complete", response_model=CodeCompletionResponse)
async def complete_code(request: CodeCompletionAPIRequest):
    """Code completion endpoint"""
    
    service_request = CodeCompletionRequest(
        prefix=request.prefix,
        suffix=request.suffix,
        language=request.language,
        max_completions=request.max_completions,
        context=request.context
    )
    
    response = await code_completion_service.complete_code(service_request)
    return response
```

---

## 📊 Usage Optimization

### Step 8: Implement Request Optimization

```python
# services/codey/optimization.py
"""
Optimization utilities for Codey models
Implements batching, caching, and rate limiting
"""

import asyncio
import time
from typing import List, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class RequestBatcher:
    """Batch requests for better efficiency"""
    
    def __init__(self, batch_size: int = 5, batch_timeout: float = 1.0):
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.pending_requests = []
        self.batch_timer = None
    
    async def add_request(self, request: Any) -> Any:
        """Add request to batch"""
        self.pending_requests.append(request)
        
        if len(self.pending_requests) >= self.batch_size:
            return await self._process_batch()
        
        if self.batch_timer is None:
            self.batch_timer = asyncio.create_task(self._wait_and_process())
        
        return await self.batch_timer
    
    async def _wait_and_process(self):
        """Wait for timeout and process batch"""
        await asyncio.sleep(self.batch_timeout)
        return await self._process_batch()
    
    async def _process_batch(self):
        """Process current batch"""
        if not self.pending_requests:
            return []
        
        batch = self.pending_requests.copy()
        self.pending_requests.clear()
        self.batch_timer = None
        
        # Process batch (implementation depends on specific use case)
        results = []
        for request in batch:
            # Process individual request
            result = await self._process_single_request(request)
            results.append(result)
        
        return results
    
    async def _process_single_request(self, request: Any) -> Any:
        """Process single request (placeholder)"""
        # This would be implemented based on specific request type
        pass

class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.requests = []
    
    async def acquire(self):
        """Acquire permission to make request"""
        now = time.time()
        
        # Remove old requests
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        # Check if we can make request
        if len(self.requests) >= self.requests_per_minute:
            # Calculate wait time
            oldest_request = min(self.requests)
            wait_time = 60 - (now - oldest_request)
            await asyncio.sleep(wait_time)
        
        # Record this request
        self.requests.append(now)

class UsageTracker:
    """Track usage across all Codey services"""
    
    def __init__(self):
        self.daily_usage = {
            "generation": 0,
            "chat": 0,
            "completion": 0
        }
        self.reset_time = time.time() + 86400  # 24 hours
    
    def record_request(self, service_type: str):
        """Record a request"""
        self._check_reset()
        self.daily_usage[service_type] += 1
    
    def get_usage(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        self._check_reset()
        return {
            "daily_usage": self.daily_usage.copy(),
            "time_until_reset": self.reset_time - time.time()
        }
    
    def _check_reset(self):
        """Check if we need to reset daily counters"""
        if time.time() >= self.reset_time:
            self.daily_usage = {k: 0 for k in self.daily_usage}
            self.reset_time = time.time() + 86400

# Global instances
usage_tracker = UsageTracker()
generation_rate_limiter = RateLimiter(10)  # 10 RPM for generation
chat_rate_limiter = RateLimiter(100)  # 100 RPM for chat
completion_rate_limiter = RateLimiter(100)  # 100 RPM for completion
```

---

## 🧪 Testing & Validation

### Step 9: Create Test Suite

```python
# tests/test_codey_integration.py
"""
Comprehensive test suite for Codey integration
Tests all three services with various scenarios
"""

import pytest
import asyncio
from services.codey.code_generation import CodeGenerationService, CodeGenerationRequest
from services.codey.code_chat import CodeChatService, CodeChatRequest
from services.codey.code_completion import CodeCompletionService, CodeCompletionRequest
from config.codey_config import CODEY_CONFIG

class TestCodeyIntegration:
    """Test suite for Codey services"""
    
    @pytest.fixture
    def generation_service(self):
        return CodeGenerationService(CODEY_CONFIG)
    
    @pytest.fixture
    def chat_service(self):
        return CodeChatService(CODEY_CONFIG)
    
    @pytest.fixture
    def completion_service(self):
        return CodeCompletionService(CODEY_CONFIG)
    
    @pytest.mark.asyncio
    async def test_code_generation(self, generation_service):
        """Test code generation functionality"""
        
        request = CodeGenerationRequest(
            prompt="Create a function to validate email addresses",
            language="python",
            requirements=["Use regex", "Include error handling"]
        )
        
        response = await generation_service.generate_code(request)
        
        assert response.generated_code is not None
        assert len(response.generated_code) > 0
        assert response.language == "python"
        assert response.execution_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_code_chat(self, chat_service):
        """Test code chat functionality"""
        
        request = CodeChatRequest(
            message="How do I implement a binary search in Python?",
            conversation_history=[],
            language="python"
        )
        
        response = await chat_service.chat(request)
        
        assert response.response is not None
        assert len(response.response) > 0
        assert response.confidence > 0
    
    @pytest.mark.asyncio
    async def test_code_completion(self, completion_service):
        """Test code completion functionality"""
        
        request = CodeCompletionRequest(
            prefix="def calculate_sentiment(",
            language="python",
            max_completions=3
        )
        
        response = await completion_service.complete_code(request)
        
        assert len(response.suggestions) > 0
        assert all(s.completion for s in response.suggestions)
        assert all(s.confidence > 0 for s in response.suggestions)
    
    def test_rate_limiting(self, generation_service):
        """Test rate limiting functionality"""
        
        # Test that rate limiting works
        initial_count = generation_service.request_count
        
        # Simulate reaching limit
        generation_service.request_count = generation_service.daily_limit
        
        assert not generation_service._check_rate_limit()
        
        # Reset for other tests
        generation_service.request_count = initial_count

# Run tests
if __name__ == "__main__":
    pytest.main([__file__])
```

### Step 10: Create Performance Benchmarks

```python
# benchmarks/codey_performance.py
"""
Performance benchmarks for Codey services
Measures response times and throughput
"""

import asyncio
import time
import statistics
from typing import List
import matplotlib.pyplot as plt

async def benchmark_code_generation():
    """Benchmark code generation performance"""
    
    service = CodeGenerationService(CODEY_CONFIG)
    
    test_prompts = [
        "Create a REST API endpoint for user authentication",
        "Implement a binary search tree in Python",
        "Write a function to parse JSON data",
        "Create a database connection pool",
        "Implement rate limiting middleware"
    ]
    
    response_times = []
    
    for prompt in test_prompts:
        request = CodeGenerationRequest(prompt=prompt)
        
        start_time = time.time()
        response = await service.generate_code(request)
        end_time = time.time()
        
        response_times.append((end_time - start_time) * 1000)
    
    # Calculate statistics
    avg_time = statistics.mean(response_times)
    median_time = statistics.median(response_times)
    min_time = min(response_times)
    max_time = max(response_times)
    
    print(f"Code Generation Benchmark Results:")
    print(f"  Average response time: {avg_time:.2f}ms")
    print(f"  Median response time: {median_time:.2f}ms")
    print(f"  Min response time: {min_time:.2f}ms")
    print(f"  Max response time: {max_time:.2f}ms")
    
    return response_times

async def run_all_benchmarks():
    """Run all performance benchmarks"""
    
    print("🚀 Running Codey Performance Benchmarks...")
    
    # Run benchmarks
    gen_times = await benchmark_code_generation()
    
    # Create visualization
    plt.figure(figsize=(10, 6))
    plt.hist(gen_times, bins=10, alpha=0.7)
    plt.xlabel('Response Time (ms)')
    plt.ylabel('Frequency')
    plt.title('Code Generation Response Time Distribution')
    plt.savefig('codey_performance.png')
    
    print("✅ Benchmarks completed. Results saved to codey_performance.png")

if __name__ == "__main__":
    asyncio.run(run_all_benchmarks())
```

---

## 🔍 Monitoring

### Step 11: Set Up Monitoring Dashboard

```python
# monitoring/codey_monitor.py
"""
Monitoring and metrics collection for Codey services
Tracks usage, performance, and costs
"""

import time
from typing import Dict, Any
from dataclasses import dataclass
from google.cloud import monitoring_v3
import logging

logger = logging.getLogger(__name__)

@dataclass
class CodeyMetrics:
    """Metrics for Codey services"""
    generation_requests: int = 0
    chat_requests: int = 0
    completion_requests: int = 0
    total_tokens_used: int = 0
    average_response_time: float = 0.0
    error_count: int = 0
    cache_hit_rate: float = 0.0

class CodeyMonitor:
    """Monitor Codey service usage and performance"""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"
        self.metrics = CodeyMetrics()
        
    def record_request(self, service_type: str, response_time: float, tokens_used: int):
        """Record a service request"""
        
        if service_type == "generation":
            self.metrics.generation_requests += 1
        elif service_type == "chat":
            self.metrics.chat_requests += 1
        elif service_type == "completion":
            self.metrics.completion_requests += 1
        
        self.metrics.total_tokens_used += tokens_used
        
        # Update average response time
        total_requests = (self.metrics.generation_requests + 
                         self.metrics.chat_requests + 
                         self.metrics.completion_requests)
        
        self.metrics.average_response_time = (
            (self.metrics.average_response_time * (total_requests - 1) + response_time) / 
            total_requests
        )
        
        # Send to Cloud Monitoring
        self._send_metrics_to_cloud_monitoring(service_type, response_time, tokens_used)
    
    def record_error(self, service_type: str, error: str):
        """Record an error"""
        self.metrics.error_count += 1
        logger.error(f"Codey {service_type} error: {error}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return {
            "generation_requests": self.metrics.generation_requests,
            "chat_requests": self.metrics.chat_requests,
            "completion_requests": self.metrics.completion_requests,
            "total_requests": (self.metrics.generation_requests + 
                             self.metrics.chat_requests + 
                             self.metrics.completion_requests),
            "total_tokens_used": self.metrics.total_tokens_used,
            "average_response_time_ms": self.metrics.average_response_time,
            "error_count": self.metrics.error_count,
            "error_rate": (self.metrics.error_count / max(1, 
                          self.metrics.generation_requests + 
                          self.metrics.chat_requests + 
                          self.metrics.completion_requests)),
            "cache_hit_rate": self.metrics.cache_hit_rate
        }
    
    def _send_metrics_to_cloud_monitoring(self, service_type: str, response_time: float, tokens_used: int):
        """Send metrics to Google Cloud Monitoring"""
        
        try:
            # Create time series data
            now = time.time()
            seconds = int(now)
            nanos = int((now - seconds) * 10 ** 9)
            interval = monitoring_v3.TimeInterval(
                {"end_time": {"seconds": seconds, "nanos": nanos}}
            )
            
            # Response time metric
            point = monitoring_v3.Point({
                "interval": interval,
                "value": {"double_value": response_time}
            })
            
            series = monitoring_v3.TimeSeries({
                "metric": {
                    "type": f"custom.googleapis.com/codey/{service_type}/response_time",
                    "labels": {"service": service_type}
                },
                "resource": {
                    "type": "global",
                    "labels": {"project_id": self.project_id}
                },
                "points": [point]
            })
            
            self.client.create_time_series(
                name=self.project_name,
                time_series=[series]
            )
            
        except Exception as e:
            logger.error(f"Failed to send metrics: {e}")

# Global monitor instance
codey_monitor = CodeyMonitor(CODEY_CONFIG.project_id)
```

---

## 🆘 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Authentication Errors

**Error**: `Permission denied` or `Authentication failed`

**Solution**:
```bash
# Check authentication
gcloud auth list

# Re-authenticate if needed
gcloud auth application-default login

# Verify service account permissions
gcloud projects get-iam-policy $PROJECT_ID
```

#### Issue 2: Rate Limit Exceeded

**Error**: `Quota exceeded` or `Rate limit exceeded`

**Solution**:
```python
# Implement exponential backoff
import time
import random

async def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if "rate limit" in str(e).lower():
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(wait_time)
            else:
                raise
    raise Exception("Max retries exceeded")
```

#### Issue 3: Model Not Available

**Error**: `Model not found` or `Endpoint not available`

**Solution**:
```bash
# Check available models
gcloud ai models list --region=us-central1

# Verify model names
# code-bison@001 (generation)
# codechat-bison@001 (chat)
# code-gecko@001 (completion)
```

#### Issue 4: High Latency

**Problem**: Slow response times

**Solution**:
```python
# Optimize requests
- Use smaller prompts
- Reduce max_output_tokens
- Implement caching
- Use batch processing
- Choose optimal region
```

---

## 📞 Important Links & References

### 🔗 Essential Links

- **Vertex AI Console**: https://console.cloud.google.com/vertex-ai
- **Model Garden**: https://console.cloud.google.com/vertex-ai/model-garden
- **Quotas Console**: https://console.cloud.google.com/iam-admin/quotas
- **API Documentation**: https://cloud.google.com/vertex-ai/docs/generative-ai/code/code-models-overview

### 📚 Documentation References

- **Codey Models Overview**: https://cloud.google.com/vertex-ai/docs/generative-ai/code/code-models-overview
- **Code Generation**: https://cloud.google.com/vertex-ai/docs/generative-ai/code/code-generation-prompts
- **Code Chat**: https://cloud.google.com/vertex-ai/docs/generative-ai/code/code-chat-prompts
- **Code Completion**: https://cloud.google.com/vertex-ai/docs/generative-ai/code/code-completion-prompts
- **Best Practices**: https://cloud.google.com/vertex-ai/docs/generative-ai/learn/responsible-ai
- **Pricing**: https://cloud.google.com/vertex-ai/pricing

### 🛠️ Tools & SDKs

- **Python SDK**: https://cloud.google.com/python/docs/reference/aiplatform/latest
- **REST API**: https://cloud.google.com/vertex-ai/docs/reference/rest
- **gcloud CLI**: https://cloud.google.com/sdk/gcloud/reference/ai

---

<div align="center">

**Next Steps**: Continue with [Cloud Run Setup](./04-cloud-run-setup.md) to deploy your containerized services.

*Your Codey models are now configured for intelligent code generation, chat, and completion within your daily quotas.*

</div>