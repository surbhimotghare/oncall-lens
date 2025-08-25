'use client';

import React from 'react';
import { Loader2, FileText, Search, Target, Database, CheckCircle2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  stage?: string;
  percentage?: number;
}

interface AnalysisStage {
  id: string;
  name: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  description: string;
}

const ANALYSIS_STAGES: AnalysisStage[] = [
  {
    id: 'data_triage',
    name: 'Data Triage',
    icon: FileText,
    color: 'text-blue-600',
    description: 'Processing and extracting key information from uploaded files'
  },
  {
    id: 'historical_search',
    name: 'Historical Search',
    icon: Search,
    color: 'text-green-600',
    description: 'Searching for similar incidents in historical data'
  },
  {
    id: 'root_cause',
    name: 'Root Cause Analysis',
    icon: Target,
    color: 'text-orange-600',
    description: 'Analyzing patterns and identifying potential root causes'
  },
  {
    id: 'synthesis',
    name: 'Synthesis',
    icon: Database,
    color: 'text-purple-600',
    description: 'Generating comprehensive analysis and recommendations'
  }
];

export default function LoadingSpinner({ 
  size = 'md', 
  message, 
  stage, 
  percentage 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  const currentStage = ANALYSIS_STAGES.find(s => s.id === stage);

  if (stage && percentage !== undefined) {
    return (
      <div className="space-y-6 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-xl shadow-sm">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">🔍 AI Analysis in Progress</h3>
          <p className="text-sm text-gray-600">
            Our multi-agent system is analyzing your incident files
          </p>
        </div>

        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Overall Progress</span>
            <span>{percentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div 
              className="bg-gradient-to-r from-blue-500 to-indigo-600 h-3 rounded-full transition-all duration-700 ease-out relative"
              style={{ width: `${percentage}%` }}
            >
              <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
            </div>
          </div>
        </div>

        {/* Current Stage */}
        {currentStage && (
          <div className="flex items-center space-x-4 p-4 bg-white/70 rounded-lg border border-blue-100">
            <div className={`p-3 rounded-full bg-blue-100 ${currentStage.color}`}>
              <currentStage.icon className="w-6 h-6" />
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                <h4 className={`font-medium ${currentStage.color}`}>
                  {currentStage.name}
                </h4>
                <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
              </div>
              <p className="text-sm text-gray-600">
                {message || currentStage.description}
              </p>
            </div>
          </div>
        )}

        {/* Stage Progress Indicators */}
        <div className="grid grid-cols-4 gap-2">
          {ANALYSIS_STAGES.map((stageInfo, index) => {
            const isCompleted = stage && ANALYSIS_STAGES.findIndex(s => s.id === stage) > index;
            const isCurrent = stageInfo.id === stage;
            const isPending = !isCompleted && !isCurrent;

            return (
              <div
                key={stageInfo.id}
                className={`flex flex-col items-center p-3 rounded-lg border transition-all duration-300 ${
                  isCompleted
                    ? 'bg-green-50 border-green-200'
                    : isCurrent
                    ? 'bg-blue-50 border-blue-200 ring-2 ring-blue-300'
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className={`p-2 rounded-full mb-2 ${
                  isCompleted
                    ? 'bg-green-100 text-green-600'
                    : isCurrent
                    ? 'bg-blue-100 text-blue-600'
                    : 'bg-gray-100 text-gray-400'
                }`}>
                  {isCompleted ? (
                    <CheckCircle2 className="w-4 h-4" />
                  ) : (
                    <stageInfo.icon className="w-4 h-4" />
                  )}
                </div>
                <span className={`text-xs font-medium text-center ${
                  isCompleted
                    ? 'text-green-700'
                    : isCurrent
                    ? 'text-blue-700'
                    : 'text-gray-500'
                }`}>
                  {stageInfo.name}
                </span>
              </div>
            );
          })}
        </div>

        {/* Estimated Time */}
        <div className="text-center">
          <p className="text-xs text-gray-500">
            ⏱️ Estimated completion: {Math.max(1, Math.ceil((100 - percentage) / 20))} minute{Math.ceil((100 - percentage) / 20) !== 1 ? 's' : ''}
          </p>
        </div>
      </div>
    );
  }

  // Simple spinner for basic loading states
  return (
    <div className="flex items-center justify-center space-x-3 p-4">
      <Loader2 className={`${sizeClasses[size]} animate-spin text-blue-600`} />
      {message && (
        <span className="text-sm text-gray-600">{message}</span>
      )}
    </div>
  );
}

// Enhanced skeleton loader for better UX
export function AnalysisSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      {/* Header skeleton */}
      <div className="space-y-3">
        <div className="flex items-center space-x-3">
          <div className="w-6 h-6 bg-gray-300 rounded-full"></div>
          <div className="h-6 bg-gray-300 rounded w-64"></div>
        </div>
        <div className="h-4 bg-gray-200 rounded w-full"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
      </div>

      {/* Content blocks skeleton */}
      <div className="space-y-4">
        <div className="h-5 bg-gray-300 rounded w-48"></div>
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded w-full"></div>
          <div className="h-4 bg-gray-200 rounded w-4/5"></div>
          <div className="h-4 bg-gray-200 rounded w-3/5"></div>
        </div>
      </div>

      {/* Code block skeleton */}
      <div className="space-y-2">
        <div className="h-4 bg-gray-300 rounded w-32"></div>
        <div className="h-24 bg-gray-100 border border-gray-200 rounded-lg p-4 space-y-2">
          <div className="h-3 bg-gray-200 rounded w-3/4"></div>
          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
          <div className="h-3 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>

      {/* Recommendations skeleton */}
      <div className="space-y-3">
        <div className="h-5 bg-gray-300 rounded w-40"></div>
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-6 h-6 bg-gray-300 rounded-full flex-shrink-0"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-300 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-full"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
