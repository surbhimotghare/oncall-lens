'use client';

import React, { useState } from 'react';
import { Search, Zap } from 'lucide-react';
import FileUploader from '@/components/FileUploader';
import AnalysisResult from '@/components/AnalysisResult';
import { analyzeIncident, ApiError } from '@/services/api';

export default function Home() {
  const [files, setFiles] = useState<File[]>([]);
  const [analysisResult, setAnalysisResult] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<number | undefined>(undefined);

  const handleAnalyze = async () => {
    if (files.length === 0) {
      setError('Please upload at least one file before analyzing.');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);
    setConfidence(undefined);

    try {
      const result = await analyzeIncident(files);
      setAnalysisResult(result.summary);
      setConfidence(result.confidence_score);
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsAnalyzing(false);
    }
  };

  const canAnalyze = files.length > 0 && !isAnalyzing;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-8 h-8 bg-accent rounded-lg">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">🔍 Oncall Lens</h1>
                <p className="text-xs text-muted">Incident Analyzer</p>
              </div>
            </div>
            <div className="text-sm text-muted">
              AI-powered incident analysis
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[calc(100vh-12rem)]">
          {/* Left Column - Controls */}
          <div className="space-y-6">
            <div className="bg-card border border-border rounded-lg shadow-soft p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Search className="w-5 h-5 text-accent" />
                <h2 className="text-lg font-semibold text-foreground">
                  Upload Incident Files
                </h2>
              </div>
              <p className="text-muted text-sm mb-6">
                Upload logs, stack traces, git diffs, or dashboard screenshots. 
                The AI will analyze them to provide insights and suggest next steps.
              </p>
              
              <FileUploader files={files} onFilesChange={setFiles} />
            </div>

            {/* Analyze Button */}
            <button
              onClick={handleAnalyze}
              disabled={!canAnalyze}
              className={`
                w-full px-6 py-3 rounded-lg font-medium text-white transition-all duration-200
                ${canAnalyze 
                  ? 'bg-accent hover:bg-accent-hover shadow-medium hover:shadow-lg' 
                  : 'bg-muted-foreground cursor-not-allowed'
                }
                ${isAnalyzing ? 'animate-pulse' : ''}
              `}
            >
              {isAnalyzing ? (
                <span className="flex items-center justify-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Analyzing...</span>
                </span>
              ) : (
                `Analyze ${files.length > 0 ? `${files.length} file${files.length === 1 ? '' : 's'}` : 'Incident'}`
              )}
            </button>

            {/* Quick Tips */}
            <div className="bg-accent/5 border border-accent/20 rounded-lg p-4">
              <h3 className="text-sm font-medium text-foreground mb-2">
                💡 Quick Tips
              </h3>
              <ul className="text-xs text-muted space-y-1">
                <li>• Upload error logs, stack traces, or git diffs</li>
                <li>• Include dashboard screenshots for context</li>
                <li>• Multiple files provide better analysis</li>
                <li>• Supported formats: .log, .txt, .diff, .png, .jpg</li>
              </ul>
            </div>
          </div>

          {/* Right Column - Results */}
          <div className="bg-card border border-border rounded-lg shadow-soft p-6 overflow-hidden">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-2 h-2 bg-accent rounded-full"></div>
              <h2 className="text-lg font-semibold text-foreground">
                Analysis Results
              </h2>
            </div>
            
            <div className="h-full overflow-y-auto pr-2">
              <AnalysisResult
                result={analysisResult}
                isLoading={isAnalyzing}
                error={error}
                confidence={confidence}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
