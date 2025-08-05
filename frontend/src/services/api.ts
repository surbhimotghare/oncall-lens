const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface AnalysisResponse {
  summary: string;
  confidence_score?: number;
  sources?: string[];
  error?: string;
  task_id?: string;
}

export interface ProgressUpdate {
  task_id: string;
  stage: string;
  message: string;
  percentage: number;
  completed: boolean;
  timestamp: number;
}

export interface ApiKeys {
  openaiApiKey: string;
  cohereApiKey: string;
}

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

// Helper function to get API keys from localStorage
function getApiKeys(): ApiKeys {
  // Check if we're in a browser environment
  if (typeof window === 'undefined') {
    return { openaiApiKey: '', cohereApiKey: '' };
  }
  
  return {
    openaiApiKey: localStorage.getItem('oncall_openai_api_key') || '',
    cohereApiKey: localStorage.getItem('oncall_cohere_api_key') || ''
  };
}

// Helper function to check if frontend API keys are configured
function hasFrontendApiKeys(): boolean {
  const apiKeys = getApiKeys();
  return apiKeys.openaiApiKey.trim().length > 0;
}

export async function analyzeIncident(files: File[]): Promise<{task_id: string}> {
  const formData = new FormData();
  
  files.forEach((file) => {
    formData.append('files', file);
  });

  // Add API keys from frontend if available
  const apiKeys = getApiKeys();
  if (apiKeys.openaiApiKey.trim()) {
    formData.append('openai_api_key', apiKeys.openaiApiKey);
  }
  if (apiKeys.cohereApiKey.trim()) {
    formData.append('cohere_api_key', apiKeys.cohereApiKey);
  }

  try {
    const response = await fetch(`${API_BASE_URL}/summarize`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      
      try {
        const errorJson = JSON.parse(errorText);
        errorMessage = errorJson.detail || errorJson.message || errorMessage;
      } catch {
        // If parsing fails, use the raw text or default message
        errorMessage = errorText || errorMessage;
      }
      
      throw new ApiError(errorMessage, response.status);
    }

    const result = await response.json();
    
    if (result.error) {
      throw new ApiError(result.error);
    }
    
    return result; // Returns {task_id: string, status: "started"}
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Handle network errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ApiError('Unable to connect to the analysis service. Please check if the backend is running.');
    }
    
    throw new ApiError('An unexpected error occurred during analysis.');
  }
}

export async function getAnalysisResults(taskId: string): Promise<AnalysisResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/results/${taskId}`);
    
    if (!response.ok) {
      throw new ApiError(`Failed to get results: ${response.statusText}`, response.status);
    }
    
    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('Failed to retrieve analysis results');
  }
}

export function subscribeToProgress(taskId: string, onProgress: (update: ProgressUpdate) => void): () => void {
  console.log('🔗 Subscribing to progress for task:', taskId);
  
  const eventSource = new EventSource(`${API_BASE_URL}/progress/${taskId}`);
  
  eventSource.onopen = () => {
    console.log('✅ Progress stream opened');
  };
  
  eventSource.onmessage = (event) => {
    console.log('📨 Progress message received:', event.data);
    try {
      const update: ProgressUpdate = JSON.parse(event.data);
      console.log('📊 Progress update:', update);
      onProgress(update);
      
      if (update.completed) {
        console.log('✅ Progress completed, closing stream');
        eventSource.close();
      }
    } catch (error) {
      console.error('❌ Error parsing progress update:', error);
    }
  };
  
  eventSource.onerror = (error) => {
    console.error('❌ Progress stream error:', error);
    eventSource.close();
  };
  
  // Return cleanup function
  return () => {
    console.log('🧹 Cleaning up progress stream');
    eventSource.close();
  };
}

// Helper function to check if API keys are configured (either frontend or backend)
export function areApiKeysConfigured(): boolean {
  // If frontend has API keys, we're good
  if (hasFrontendApiKeys()) {
    return true;
  }
  
  // Otherwise, assume backend might have them configured
  // We'll let the backend handle the validation
  return true;
}

// Helper function to check if frontend API keys are available
export function hasFrontendApiKeysConfigured(): boolean {
  return hasFrontendApiKeys();
} 