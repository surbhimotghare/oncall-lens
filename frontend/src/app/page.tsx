'use client';

import { useState } from 'react';
import FileUploader from '@/components/FileUploader';
import AnalysisResult from '@/components/AnalysisResult';
import { analyzeIncident, getAnalysisResults, subscribeToProgress, ProgressUpdate, ApiError } from '@/services/api';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function Home() {
  const [files, setFiles] = useState<File[]>([]);
  const [analysisResult, setAnalysisResult] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<number | undefined>(undefined);
  const [isLeftPanelCollapsed, setIsLeftPanelCollapsed] = useState(false);
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (files.length === 0) return;

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);
    setConfidence(undefined);
    setProgress(null);

    try {
      // Start the analysis and get task_id immediately
      console.log('🚀 Starting analysis...');
      const { task_id } = await analyzeIncident(files);
      console.log('🎯 Got task_id immediately:', task_id);
      
      setCurrentTaskId(task_id);
      
      // Start progress tracking immediately
      const unsubscribe = subscribeToProgress(task_id, async (update) => {
        console.log('📊 Progress update received in component:', update);
        setProgress(update);
        
        if (update.completed) {
          console.log('✅ Analysis completed, fetching results');
          
          try {
            // Fetch the final results
            const results = await getAnalysisResults(task_id);
            setAnalysisResult(results.summary);
            setConfidence(results.confidence_score);
          } catch (err) {
            console.error('❌ Failed to fetch results:', err);
            setError('Failed to retrieve analysis results');
          }
          
          setProgress(null);
          setCurrentTaskId(null);
          setIsAnalyzing(false);
          unsubscribe();
        }
      });
      
    } catch (err) {
      const errorMessage = err instanceof ApiError ? err.message : 'An unexpected error occurred';
      console.error('❌ Analysis failed:', errorMessage);
      setError(errorMessage);
      setIsAnalyzing(false);
    }
  };

  const handleFilesChange = (newFiles: File[]) => {
    setFiles(newFiles);
    // Reset analysis when files change
    if (analysisResult) {
      setAnalysisResult(null);
      setError(null);
      setConfidence(undefined);
      setProgress(null);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-8 h-8 bg-accent rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-zap w-5 h-5 text-white" aria-hidden="true">
                  <path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"></path>
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">🔍 Oncall Lens</h1>
                <p className="text-xs text-muted">Incident Analyzer</p>
              </div>
            </div>
            <div className="text-sm text-muted">AI-powered incident analysis</div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8 h-[calc(100vh-12rem)]">
          {/* Left Column - Controls */}
          <div className={`transition-all duration-300 ${isLeftPanelCollapsed ? 'w-12' : 'w-96'}`}>
            <div className="space-y-6">
              <div className="bg-card border border-border rounded-lg shadow-soft p-6 relative">
                {/* Collapse Button - Only show after analysis */}
                {analysisResult && (
                  <button
                    onClick={() => setIsLeftPanelCollapsed(!isLeftPanelCollapsed)}
                    className="absolute -right-3 top-6 bg-blue-600 hover:bg-blue-700 text-white border-2 border-white rounded-full p-2 shadow-lg hover:shadow-xl transition-all duration-200 z-10"
                    title={isLeftPanelCollapsed ? "Expand panel" : "Collapse panel"}
                  >
                    {isLeftPanelCollapsed ? (
                      <ChevronRight className="w-5 h-5" />
                    ) : (
                      <ChevronLeft className="w-5 h-5" />
                    )}
                  </button>
                )}

                {!isLeftPanelCollapsed && (
                  <>
                    <div className="flex items-center space-x-2 mb-4 pr-8">
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-files w-5 h-5 text-accent" aria-hidden="true">
                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
                        <polyline points="14,2 14,8 20,8"></polyline>
                        <path d="M16 13H8"></path>
                        <path d="M16 17H8"></path>
                        <path d="M10 9H8"></path>
                      </svg>
                      <h2 className="text-lg font-semibold text-foreground">Upload Incident Files</h2>
                    </div>
                    
                    <p className="text-muted text-sm mb-6">
                      Upload logs, stack traces, git diffs, or dashboard screenshots. 
                      The AI will analyze them to provide insights and suggest next steps.
                    </p>
                    
                    <FileUploader 
                      files={files} 
                      onFilesChange={handleFilesChange}
                    />
                    
                    <div className="flex justify-center mt-6">
                      <button
                        onClick={handleAnalyze}
                        disabled={files.length === 0 || isAnalyzing}
                        className={`
                          px-6 py-2.5 rounded-lg font-medium transition-all duration-200 inline-flex items-center justify-center
                          ${files.length === 0 || isAnalyzing
                            ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700 text-white shadow-soft hover:shadow-medium'
                          }
                        `}
                      >
                        {isAnalyzing ? (
                          <>
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Analyzing...
                          </>
                        ) : (
                          'Analyze'
                        )}
                      </button>
                    </div>
                    
                    <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <h3 className="text-sm font-medium text-blue-900 mb-2">💡Quick Tips</h3>
                      <ul className="text-xs text-blue-800 space-y-1">
                        <li>• Include error logs and stack traces for better analysis</li>
                        <li>• Upload git diffs to see what changed</li>
                        <li>• Add dashboard screenshots for context</li>
                        <li>• The AI will search for similar past incidents</li>
                      </ul>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Analysis Results */}
          <div className="flex-1">
            <AnalysisResult 
              result={analysisResult}
              isLoading={isAnalyzing}
              error={error}
              confidence={confidence}
              progress={progress}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
