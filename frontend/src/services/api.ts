const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface AnalysisResponse {
  summary: string;
  confidence_score?: number;
  sources?: string[];
  error?: string;
}

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function analyzeIncident(files: File[]): Promise<AnalysisResponse> {
  const formData = new FormData();
  
  files.forEach((file) => {
    formData.append('files', file);
  });

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

    const result: AnalysisResponse = await response.json();
    
    if (result.error) {
      throw new ApiError(result.error);
    }
    
    return result;
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