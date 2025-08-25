'use client';

import { useState, useEffect } from 'react';
import FileUploader from '@/components/FileUploader';
import AnalysisResult from '@/components/AnalysisResult';
import Settings from '@/components/Settings';
import { analyzeIncident, getAnalysisResults, subscribeToProgress, ProgressUpdate, ApiError, ApiKeys, hasFrontendApiKeysConfigured } from '@/services/api';
import { ChevronLeft, ChevronRight, Settings as SettingsIcon } from 'lucide-react';

export default function Home() {
  const [files, setFiles] = useState<File[]>([]);
  const [analysisResult, setAnalysisResult] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confidence, setConfidence] = useState<number | undefined>(undefined);
  const [isLeftPanelCollapsed, setIsLeftPanelCollapsed] = useState(false);
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const handleAnalyze = async () => {
    // Validate that we have valid files
    const validFiles = files.filter(file => {
      const extension = file.name.split('.').pop()?.toLowerCase() || '';
      const supportedExtensions = ['log', 'txt', 'diff', 'patch', 'png', 'jpg', 'jpeg', 'json', 'js', 'ts', 'py', 'java', 'cpp', 'yaml', 'yml', 'md', 'csv', 'xml'];
      return supportedExtensions.includes(extension) && file.size <= 50 * 1024 * 1024; // 50MB max
    });

    if (validFiles.length === 0) {
      setError('Please upload at least one valid file (logs, code, images, or config files)');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);
    setConfidence(undefined);
    setProgress(null);

    try {
      // Start the analysis with only valid files
      console.log('🚀 Starting analysis with', validFiles.length, 'valid files...');
      const { task_id } = await analyzeIncident(validFiles);
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

  const handleSettingsSave = (apiKeys: ApiKeys) => {
    // Clear any previous API key related errors
    if (error && error.includes('API key')) {
      setError(null);
    }
  };

  const [hasApiKeys, setHasApiKeys] = useState(false);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    setHasApiKeys(hasFrontendApiKeysConfigured());
  }, []);

  const validFilesCount = files.filter(file => {
    const extension = file.name.split('.').pop()?.toLowerCase() || '';
    const supportedExtensions = ['log', 'txt', 'diff', 'patch', 'png', 'jpg', 'jpeg', 'json', 'js', 'ts', 'py', 'java', 'cpp', 'yaml', 'yml', 'md', 'csv', 'xml'];
    return supportedExtensions.includes(extension) && file.size <= 50 * 1024 * 1024;
  }).length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 transition-colors duration-300">
      {/* Enhanced Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-gray-200 dark:border-slate-700 shadow-sm sticky top-0 z-40 transition-colors duration-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl shadow-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-6 h-6 text-white">
                  <path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"></path>
                </svg>
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  Oncall Lens
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-300">AI-Powered Incident Analysis</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-6">
                            {/* Status indicator */}
              {isClient && (
                <div className="hidden md:flex items-center space-x-4">
                  <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-300">
                    <div className={`w-2 h-2 rounded-full ${hasApiKeys ? 'bg-green-500' : 'bg-amber-500'}`}></div>
                    <span>{hasApiKeys ? 'API Connected' : 'Setup Required'}</span>
                  </div>
                
                  {files.length > 0 && (
                    <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-300">
                      <span className="font-medium text-blue-600 dark:text-blue-400">{validFilesCount}</span>
                      <span>files ready</span>
                    </div>
                  )}
                </div>
              )}
              
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setIsSettingsOpen(true)}
                  className={`p-3 rounded-xl transition-all duration-200 ${
                    hasApiKeys 
                      ? 'text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-slate-700' 
                      : 'text-white bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 shadow-lg hover:shadow-xl animate-pulse hover:animate-none'
                  }`}
                  title="API Settings"
                >
                  <SettingsIcon className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* API Key Warning Banner */}
      {isClient && !hasApiKeys && (
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 border-b border-amber-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
                    <SettingsIcon className="w-5 h-5 text-amber-600" />
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-medium text-amber-900">API Configuration Required</h3>
                  <p className="text-sm text-amber-800">
                    Please configure your OpenAI API key to enable AI-powered incident analysis.
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsSettingsOpen(true)}
                className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
              >
                Configure Now
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex gap-8 min-h-[calc(100vh-12rem)]">
          {/* Left Column - Controls */}
          <div className={`transition-all duration-300 ${isLeftPanelCollapsed ? 'w-16' : 'w-96 lg:w-[28rem]'}`}>
            <div className="space-y-6 sticky top-24">
              <div className="bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-2xl shadow-lg overflow-hidden relative transition-colors duration-300">
                {/* Collapse Button - Only show after analysis */}
                {analysisResult && (
                  <button
                    onClick={() => setIsLeftPanelCollapsed(!isLeftPanelCollapsed)}
                    className="absolute -right-4 top-8 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white border-4 border-white rounded-full p-3 shadow-lg hover:shadow-xl transition-all duration-200 z-20"
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
                    {/* Header */}
                    <div className="px-6 py-5 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-slate-700 dark:to-slate-600 border-b border-gray-200 dark:border-slate-600 transition-colors duration-300">
                      <div className="flex items-center space-x-3 pr-8">
                        <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
                          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-5 h-5 text-blue-600 dark:text-blue-400">
                            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
                            <polyline points="14,2 14,8 20,8"></polyline>
                            <path d="M16 13H8"></path>
                            <path d="M16 17H8"></path>
                            <path d="M10 9H8"></path>
                          </svg>
                        </div>
                        <div>
                          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Upload Incident Files</h2>
                          <p className="text-sm text-gray-600 dark:text-gray-300">Upload files for AI analysis</p>
                        </div>
                      </div>
                    </div>
                    
                    {/* Content */}
                    <div className="p-6">
                      <div className="mb-6">
                        <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed">
                          Upload logs, stack traces, git diffs, or dashboard screenshots. 
                          Our multi-agent AI system will analyze them to provide comprehensive insights and actionable recommendations.
                        </p>
                      </div>
                      
                      <FileUploader 
                        files={files} 
                        onFilesChange={handleFilesChange}
                      />
                      
                      {/* Analyze Button */}
                      <div className="mt-8">
                        <button
                          onClick={handleAnalyze}
                          disabled={validFilesCount === 0 || isAnalyzing || !hasApiKeys}
                          className={`
                            w-full px-6 py-4 rounded-xl font-semibold transition-all duration-200 inline-flex items-center justify-center text-lg
                            ${validFilesCount === 0 || isAnalyzing || !hasApiKeys
                              ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                              : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transform hover:scale-105'
                            }
                          `}
                        >
                          {isAnalyzing ? (
                            <>
                              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                              </svg>
                              Analyzing Incident...
                            </>
                          ) : !hasApiKeys ? (
                            'Configure API Keys First'
                          ) : validFilesCount === 0 ? (
                            'Upload Files to Analyze'
                          ) : (
                            `🚀 Analyze ${validFilesCount} File${validFilesCount !== 1 ? 's' : ''}`
                          )}
                        </button>
                      </div>
                      
                      {/* Tips Section */}
                      <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl">
                        <h3 className="text-sm font-semibold text-blue-900 mb-3 flex items-center space-x-2">
                          <span>💡</span>
                          <span>Pro Tips for Better Analysis</span>
                        </h3>
                        <ul className="text-xs text-blue-800 space-y-2">
                          <li className="flex items-start space-x-2">
                            <span className="text-blue-500 mt-0.5">•</span>
                            <span>Include error logs and stack traces for precise root cause analysis</span>
                          </li>
                          <li className="flex items-start space-x-2">
                            <span className="text-blue-500 mt-0.5">•</span>
                            <span>Upload git diffs to understand what code changes triggered the issue</span>
                          </li>
                          <li className="flex items-start space-x-2">
                            <span className="text-blue-500 mt-0.5">•</span>
                            <span>Add dashboard screenshots for visual context and metrics</span>
                          </li>
                          <li className="flex items-start space-x-2">
                            <span className="text-blue-500 mt-0.5">•</span>
                            <span>The AI searches historical incidents for similar patterns</span>
                          </li>
                        </ul>
                      </div>
                    </div>
                  </>
                )}

                {/* Collapsed state indicator */}
                {isLeftPanelCollapsed && (
                  <div className="p-4 text-center">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg mx-auto flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="w-4 h-4 text-blue-600">
                        <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path>
                      </svg>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Column - Analysis Results */}
          <div className="flex-1 min-w-0">
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

      {/* Settings Modal */}
      <Settings
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSave={handleSettingsSave}
      />
    </div>
  );
}
