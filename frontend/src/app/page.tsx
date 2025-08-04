'use client';

import React, { useState } from 'react';
import { Search, Zap, ChevronLeft, ChevronRight } from 'lucide-react';
import FileUploader from '@/components/FileUploader';
import AnalysisResult from '@/components/AnalysisResult';
import { analyzeIncident, ApiError } from '@/services/api';

export default function Home() {
  const [files, setFiles] = useState<File[]>([]);
  const [analysisResult, setAnalysisResult] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<number | undefined>(undefined);
  const [isLeftPanelCollapsed, setIsLeftPanelCollapsed] = useState(false);

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
        <div className="flex gap-8 h-[calc(100vh-12rem)]">
          {/* Left Column - Controls */}
          <div className={`transition-all duration-300 ${isLeftPanelCollapsed ? 'w-12' : 'w-96'}`}>
            {isLeftPanelCollapsed ? (
              /* Collapsed State - Show expand button */
              <div className="h-full flex flex-col items-center">
                <button
                  onClick={() => setIsLeftPanelCollapsed(false)}
                  className="p-3 bg-card border border-border rounded-lg shadow-soft hover:shadow-medium transition-all"
                  title="Expand controls panel"
                >
                  <ChevronRight className="w-5 h-5 text-muted" />
                </button>
              </div>
            ) : (
              /* Expanded State - Show full controls */
              <div className="space-y-6">
                <div className="bg-card border border-border rounded-lg shadow-soft p-6 relative">
                  {/* Collapse button - Only show when analysis is complete */}
                  {analysisResult && (
                    <button
                      onClick={() => setIsLeftPanelCollapsed(true)}
                      className="absolute -right-3 top-6 p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all border-2 border-white"
                      title="Hide panel to focus on results"
                    >
                      <ChevronLeft className="w-5 h-5" />
                    </button>
                  )}

                  <div className="flex items-center space-x-2 mb-4 pr-8">
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
                <div className="flex justify-center">
                  <button
                    onClick={handleAnalyze}
                    disabled={!canAnalyze}
                    className={`
                      px-6 py-2.5 rounded-lg font-medium transition-all duration-200 inline-flex items-center justify-center
                      ${canAnalyze 
                        ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-md hover:shadow-lg' 
                        : 'bg-gray-300 text-gray-600 cursor-not-allowed'
                      }
                      ${isAnalyzing ? 'animate-pulse' : ''}
                    `}
                  >
                    {isAnalyzing ? (
                      <span className="flex items-center justify-center space-x-2">
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span className="text-white">Analyzing...</span>
                      </span>
                    ) : (
                      <span>
                        Analyze {files.length > 0 ? `${files.length} file${files.length === 1 ? '' : 's'}` : 'Incident'}
                      </span>
                    )}
                  </button>
                </div>

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
            )}
          </div>

          {/* Right Column - Results */}
          <div className="flex-1 bg-card border border-border rounded-lg shadow-soft p-6 overflow-hidden">
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
