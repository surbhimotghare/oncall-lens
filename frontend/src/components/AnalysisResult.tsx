'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { AlertCircle, CheckCircle, Clock, TrendingUp, Shield, Zap, Brain, History, Target, FileSearch } from 'lucide-react';
import { ProgressUpdate } from '@/services/api';
import LoadingSpinner, { AnalysisSkeleton } from './LoadingSpinner';

interface AnalysisResultProps {
  result: string | null;
  isLoading: boolean;
  error: string | null;
  confidence?: number;
  progress?: ProgressUpdate | null;
}

// Enhanced empty state with actionable tips
const EmptyState = () => (
  <div className="flex flex-col items-center justify-center py-16 text-center">
    <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mb-6">
      <Brain className="w-10 h-10 text-blue-600" />
    </div>
    <div className="max-w-md">
      <h3 className="text-xl font-semibold text-gray-900 mb-3">
        Ready to Analyze Your Incident
      </h3>
      <p className="text-gray-600 mb-6">
        Upload your incident files and our AI-powered multi-agent system will provide comprehensive analysis with root cause identification and actionable recommendations.
      </p>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="flex items-center space-x-2 text-gray-500">
          <FileSearch className="w-4 h-4 text-blue-500" />
          <span>Data Triage</span>
        </div>
        <div className="flex items-center space-x-2 text-gray-500">
          <History className="w-4 h-4 text-green-500" />
          <span>Historical Context</span>
        </div>
        <div className="flex items-center space-x-2 text-gray-500">
          <Target className="w-4 h-4 text-orange-500" />
          <span>Root Cause Analysis</span>
        </div>
        <div className="flex items-center space-x-2 text-gray-500">
          <Shield className="w-4 h-4 text-purple-500" />
          <span>Recommendations</span>
        </div>
      </div>
    </div>
  </div>
);

// Enhanced confidence indicator with visual improvements
const ConfidenceIndicator = ({ confidence }: { confidence: number }) => {
  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return { text: 'text-green-700', bg: 'bg-green-100', border: 'border-green-300', icon: 'text-green-600' };
    if (score >= 0.6) return { text: 'text-yellow-700', bg: 'bg-yellow-100', border: 'border-yellow-300', icon: 'text-yellow-600' };
    return { text: 'text-red-700', bg: 'bg-red-100', border: 'border-red-300', icon: 'text-red-600' };
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return 'High Confidence';
    if (score >= 0.6) return 'Medium Confidence';
    return 'Low Confidence';
  };

  const colors = getConfidenceColor(confidence);
  const percentage = Math.round(confidence * 100);

  return (
    <div className={`flex items-center justify-between p-4 rounded-lg border ${colors.bg} ${colors.border}`}>
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2">
          <CheckCircle className={`w-5 h-5 ${colors.icon}`} />
          <span className={`font-semibold ${colors.text}`}>
            {getConfidenceLabel(confidence)}
          </span>
        </div>
        <span className={`text-sm ${colors.text}`}>
          {percentage}% accuracy
        </span>
      </div>
      
      {/* Progress bar visualization */}
      <div className="flex items-center space-x-2">
        <div className="w-24 bg-white rounded-full h-2 border">
          <div 
            className={`h-2 rounded-full transition-all duration-1000 ${
              confidence >= 0.8 ? 'bg-green-500' : confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
            }`}
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        <TrendingUp className={`w-4 h-4 ${colors.icon}`} />
      </div>
    </div>
  );
};

export default function AnalysisResult({ result, isLoading, error, confidence, progress }: AnalysisResultProps) {
  console.log('🔍 AnalysisResult render:', { isLoading, progress, result: !!result });
  
  // Enhanced error display
  if (error) {
    return (
      <div className="space-y-4">
        <div className="flex items-start space-x-4 p-6 bg-gradient-to-r from-red-50 to-pink-50 border border-red-200 rounded-xl shadow-sm">
          <div className="p-2 bg-red-100 rounded-full">
            <AlertCircle className="w-6 h-6 text-red-600" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-red-900 mb-2">Analysis Failed</h3>
            <p className="text-red-800 mb-4">{error}</p>
            <div className="flex items-center space-x-4 text-sm">
              <div className="flex items-center space-x-2 text-red-700">
                <Zap className="w-4 h-4" />
                <span>Try uploading different files</span>
              </div>
              <div className="flex items-center space-x-2 text-red-700">
                <Shield className="w-4 h-4" />
                <span>Check API key configuration</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Enhanced progress display */}
      {progress && (
        <LoadingSpinner 
          stage={progress.stage}
          percentage={progress.percentage}
          message={progress.message}
        />
      )}
      
      {/* Loading state without progress */}
      {isLoading && !progress && <AnalysisSkeleton />}
      
      {/* Results display */}
      {!isLoading && result && (
        <div className="space-y-6">
          {/* Confidence indicator */}
          {confidence !== undefined && (
            <ConfidenceIndicator confidence={confidence} />
          )}
          
          {/* Analysis content */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-gray-200">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Brain className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">AI Analysis Results</h2>
                  <p className="text-sm text-gray-600">Comprehensive incident analysis with recommendations</p>
                </div>
              </div>
            </div>
            
            <div className="p-6">
              <div className="prose prose-sm max-w-none prose-headings:text-gray-900 prose-p:text-gray-700">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ className, children, ...props }: any) {
                  const match = /language-(\w+)/.exec(className || '');
                  const language = match ? match[1] : '';
                  
                  if (language) {
                    return (
                      <SyntaxHighlighter
                        style={oneLight}
                        language={language}
                        PreTag="div"
                        className="rounded-md border border-border text-sm leading-relaxed p-4"
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    );
                  }
                  
                  return (
                    <code
                      className="px-1.5 py-0.5 text-sm bg-border/50 text-foreground rounded font-mono"
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },
                h1: ({ children }) => (
                  <h1 className="text-2xl font-bold text-gray-900 mb-6 pb-3 border-b border-gray-200 flex items-center space-x-3">
                    <Target className="w-6 h-6 text-blue-600" />
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-xl font-semibold text-gray-800 mb-4 mt-8 flex items-center space-x-2">
                    <div className="w-2 h-6 bg-blue-500 rounded-full"></div>
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-lg font-medium text-gray-800 mb-3 mt-6">
                    {children}
                  </h3>
                ),
                p: ({ children }) => (
                  <p className="text-gray-700 mb-4 leading-relaxed">
                    {children}
                  </p>
                ),
                ul: ({ children }) => (
                  <ul className="list-none space-y-2 mb-4">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-inside space-y-2 mb-4 text-gray-700">
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li className="text-gray-700 flex items-start space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>{children}</span>
                  </li>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-blue-400 pl-6 py-3 bg-blue-50 rounded-r-lg mb-4 italic">
                    {children}
                  </blockquote>
                ),
                table: ({ children }) => (
                  <div className="overflow-x-auto mb-6">
                    <table className="min-w-full border border-gray-200 rounded-lg shadow-sm">
                      {children}
                    </table>
                  </div>
                ),
                th: ({ children }) => (
                  <th className="px-4 py-3 bg-gray-50 border-b border-gray-200 text-left font-semibold text-gray-900">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="px-4 py-3 border-b border-gray-200 text-gray-700">
                    {children}
                  </td>
                ),
              }}
            >
              {result}
            </ReactMarkdown>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Empty state */}
      {!isLoading && !result && !progress && <EmptyState />}
    </div>
  );
} 