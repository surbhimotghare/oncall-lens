'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { AlertCircle, CheckCircle, Clock, Loader2, Database, Search, Target, FileText } from 'lucide-react';
import { ProgressUpdate } from '@/services/api';

interface AnalysisResultProps {
  result: string | null;
  isLoading: boolean;
  error: string | null;
  confidence?: number;
  progress?: ProgressUpdate | null;
}

const LoadingSkeleton = () => (
  <div className="space-y-4 animate-pulse">
    <div className="flex items-center space-x-2">
      <Loader2 className="w-5 h-5 text-accent animate-spin" />
      <div className="h-6 bg-border rounded w-48"></div>
    </div>
    <div className="space-y-3">
      <div className="h-4 bg-border rounded w-full"></div>
      <div className="h-4 bg-border rounded w-5/6"></div>
      <div className="h-4 bg-border rounded w-4/6"></div>
    </div>
    <div className="space-y-2">
      <div className="h-4 bg-border rounded w-32"></div>
      <div className="h-20 bg-border rounded w-full"></div>
    </div>
    <div className="space-y-3">
      <div className="h-4 bg-border rounded w-full"></div>
      <div className="h-4 bg-border rounded w-3/4"></div>
    </div>
  </div>
);

const ProgressDisplay = ({ progress }: { progress: ProgressUpdate }) => {
  console.log('🎨 Rendering ProgressDisplay:', progress);
  
  const getStageIcon = (stage: string) => {
    switch (stage) {
      case 'data_triage':
        return <FileText className="w-4 h-4" />;
      case 'historical_search':
        return <Search className="w-4 h-4" />;
      case 'root_cause':
        return <Target className="w-4 h-4" />;
      case 'synthesis':
        return <Database className="w-4 h-4" />;
      default:
        return <Loader2 className="w-4 h-4 animate-spin" />;
    }
  };

  const getStageColor = (stage: string) => {
    switch (stage) {
      case 'data_triage':
        return 'text-blue-600';
      case 'historical_search':
        return 'text-green-600';
      case 'root_cause':
        return 'text-orange-600';
      case 'synthesis':
        return 'text-purple-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
      <h3 className="text-sm font-medium text-blue-900">Analysis Progress</h3>
      
      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-accent h-2 rounded-full transition-all duration-500"
          style={{ width: `${progress.percentage}%` }}
        ></div>
      </div>
      
      {/* Progress Details */}
      <div className="flex items-center space-x-3">
        {getStageIcon(progress.stage)}
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <span className={`font-medium ${getStageColor(progress.stage)}`}>
              {progress.message}
            </span>
            <span className="text-sm text-muted">
              {progress.percentage}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

const EmptyState = () => (
  <div className="flex flex-col items-center justify-center h-64 text-center space-y-4">
    <Clock className="w-12 h-12 text-muted" />
    <div>
      <h3 className="text-lg font-medium text-foreground">
        Ready for Analysis
      </h3>
      <p className="text-muted mt-1">
        Your incident analysis will appear here once you upload files and click "Analyze"
      </p>
    </div>
  </div>
);

const ConfidenceIndicator = ({ confidence }: { confidence: number }) => {
  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (score: number) => {
    if (score >= 0.8) return 'High';
    if (score >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <div className="flex items-center space-x-2 text-sm">
      <CheckCircle className={`w-4 h-4 ${getConfidenceColor(confidence)}`} />
      <span className="text-muted">
        Confidence: 
        <span className={`ml-1 font-medium ${getConfidenceColor(confidence)}`}>
          {getConfidenceLabel(confidence)} ({Math.round(confidence * 100)}%)
        </span>
      </span>
    </div>
  );
};

export default function AnalysisResult({ result, isLoading, error, confidence, progress }: AnalysisResultProps) {
  console.log('🔍 AnalysisResult render:', { isLoading, progress, result: !!result });
  
  if (error) {
    return (
      <div className="flex items-start space-x-3 p-4 bg-red-50 border border-red-200 rounded-lg">
        <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
        <div>
          <h3 className="text-sm font-medium text-red-800">Analysis Failed</h3>
          <p className="text-sm text-red-700 mt-1">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Always show progress if available */}
      {progress && <ProgressDisplay progress={progress} />}
      
      {isLoading && !progress && <LoadingSkeleton />}
      
      {!isLoading && result && (
        <div className="space-y-4">
          {confidence !== undefined && (
            <div className="pb-3 border-b border-border">
              <ConfidenceIndicator confidence={confidence} />
            </div>
          )}
          
          <div className="prose prose-sm max-w-none">
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
                  <h1 className="text-2xl font-bold text-foreground mb-4 pb-2 border-b border-border">
                    {children}
                  </h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-xl font-semibold text-foreground mb-3 mt-6">
                    {children}
                  </h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-lg font-medium text-foreground mb-2 mt-4">
                    {children}
                  </h3>
                ),
                p: ({ children }) => (
                  <p className="text-foreground mb-3 leading-relaxed">
                    {children}
                  </p>
                ),
                ul: ({ children }) => (
                  <ul className="list-disc list-inside space-y-1 mb-3 text-foreground">
                    {children}
                  </ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal list-inside space-y-1 mb-3 text-foreground">
                    {children}
                  </ol>
                ),
                li: ({ children }) => (
                  <li className="text-foreground">{children}</li>
                ),
                blockquote: ({ children }) => (
                  <blockquote className="border-l-4 border-accent pl-4 py-2 bg-accent/5 rounded-r-md mb-4">
                    {children}
                  </blockquote>
                ),
                table: ({ children }) => (
                  <div className="overflow-x-auto mb-4">
                    <table className="min-w-full border border-border rounded-lg">
                      {children}
                    </table>
                  </div>
                ),
                th: ({ children }) => (
                  <th className="px-4 py-2 bg-background border-b border-border text-left font-medium text-foreground">
                    {children}
                  </th>
                ),
                td: ({ children }) => (
                  <td className="px-4 py-2 border-b border-border text-foreground">
                    {children}
                  </td>
                ),
              }}
            >
              {result}
            </ReactMarkdown>
          </div>
        </div>
      )}
      
      {!isLoading && !result && !progress && <EmptyState />}
    </div>
  );
} 