'use client';

import { useState } from 'react';
import { ChevronDown, ChevronRight, Brain, FileSearch, History, Target, Zap, CheckCircle2, Clock } from 'lucide-react';

interface ReasoningStep {
  agent: string;
  action: string;
  reasoning: string;
  result: string;
  confidence: number;
  timestamp: number;
}

interface AgentReasoningProps {
  steps?: ReasoningStep[];
  currentStep?: string;
  isVisible?: boolean;
}

const AGENT_CONFIGS = {
  'data_triage': {
    name: 'Data Triage Agent',
    icon: FileSearch,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    description: 'Analyzing and extracting key information from uploaded files'
  },
  'historical_search': {
    name: 'Historical Analyst',
    icon: History,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    description: 'Searching for similar incidents in historical data'
  },
  'root_cause': {
    name: 'Root Cause Analyzer',
    icon: Target,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
    borderColor: 'border-orange-200',
    description: 'Identifying potential root causes and failure patterns'
  },
  'synthesis': {
    name: 'Synthesis Agent',
    icon: Brain,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200',
    description: 'Generating comprehensive analysis and recommendations'
  }
};

export default function AgentReasoning({ steps = [], currentStep, isVisible = true }: AgentReasoningProps) {
  const [expandedSteps, setExpandedSteps] = useState<Set<number>>(new Set());
  const [showReasoning, setShowReasoning] = useState(false);

  if (!isVisible) return null;

  const toggleStep = (index: number) => {
    const newExpanded = new Set(expandedSteps);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedSteps(newExpanded);
  };

  // Mock reasoning steps if none provided
  const mockSteps: ReasoningStep[] = steps.length > 0 ? steps : [
    {
      agent: 'data_triage',
      action: 'File Analysis',
      reasoning: 'Analyzing uploaded files to extract error patterns, stack traces, and system metrics',
      result: 'Found 3 error patterns, 1 stack trace, and performance degradation signals',
      confidence: 0.85,
      timestamp: Date.now() - 3000
    },
    {
      agent: 'historical_search',
      action: 'Pattern Matching',
      reasoning: 'Searching vector database for similar incident patterns and error signatures',
      result: 'Found 2 similar incidents from the past 6 months with 78% similarity',
      confidence: 0.72,
      timestamp: Date.now() - 2000
    },
    {
      agent: 'root_cause',
      action: 'Causal Analysis',
      reasoning: 'Correlating error patterns with code changes and system metrics to identify root cause',
      result: 'Database connection pool exhaustion likely caused by recent connection leak',
      confidence: 0.90,
      timestamp: Date.now() - 1000
    }
  ];

  const displaySteps = mockSteps;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden mb-6">
      <div className="px-6 py-4 bg-gradient-to-r from-gray-50 to-blue-50 border-b border-gray-200">
        <button
          onClick={() => setShowReasoning(!showReasoning)}
          className="flex items-center justify-between w-full text-left"
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Brain className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">AI Agent Reasoning</h3>
              <p className="text-sm text-gray-600">See how our multi-agent system analyzed your incident</p>
            </div>
          </div>
          {showReasoning ? (
            <ChevronDown className="w-5 h-5 text-gray-500" />
          ) : (
            <ChevronRight className="w-5 h-5 text-gray-500" />
          )}
        </button>
      </div>

      {showReasoning && (
        <div className="p-6">
          <div className="space-y-4">
            {displaySteps.map((step, index) => {
              const config = AGENT_CONFIGS[step.agent as keyof typeof AGENT_CONFIGS];
              const isExpanded = expandedSteps.has(index);
              const isActive = currentStep === step.agent;
              const isComplete = !currentStep || displaySteps.findIndex(s => s.agent === currentStep) > index;

              return (
                <div
                  key={index}
                  className={`border rounded-lg overflow-hidden transition-all duration-200 ${
                    isActive ? 'ring-2 ring-blue-300 border-blue-200' : config.borderColor
                  }`}
                >
                  <button
                    onClick={() => toggleStep(index)}
                    className={`w-full p-4 text-left transition-colors ${
                      isActive ? 'bg-blue-50' : config.bgColor
                    } hover:bg-opacity-80`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`p-2 rounded-lg ${isActive ? 'bg-blue-100' : 'bg-white'}`}>
                          {isComplete ? (
                            <CheckCircle2 className={`w-5 h-5 text-green-600`} />
                          ) : isActive ? (
                            <Clock className={`w-5 h-5 text-blue-600 animate-spin`} />
                          ) : (
                            <config.icon className={`w-5 h-5 ${config.color}`} />
                          )}
                        </div>
                        <div>
                          <h4 className={`font-medium ${isActive ? 'text-blue-900' : 'text-gray-900'}`}>
                            {config.name}
                          </h4>
                          <p className={`text-sm ${isActive ? 'text-blue-700' : 'text-gray-600'}`}>
                            {step.action}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        {isComplete && (
                          <div className="flex items-center space-x-1 text-sm text-green-600">
                            <span className="font-medium">{Math.round(step.confidence * 100)}%</span>
                          </div>
                        )}
                        {isExpanded ? (
                          <ChevronDown className="w-4 h-4 text-gray-500" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-gray-500" />
                        )}
                      </div>
                    </div>
                  </button>

                  {isExpanded && (
                    <div className="px-4 pb-4 bg-white border-t border-gray-100">
                      <div className="space-y-3 pt-3">
                        <div>
                          <h5 className="text-sm font-medium text-gray-900 mb-1">Reasoning:</h5>
                          <p className="text-sm text-gray-700">{step.reasoning}</p>
                        </div>
                        {isComplete && (
                          <div>
                            <h5 className="text-sm font-medium text-gray-900 mb-1">Result:</h5>
                            <p className="text-sm text-gray-700">{step.result}</p>
                          </div>
                        )}
                        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                          <span className="text-xs text-gray-500">
                            {new Date(step.timestamp).toLocaleTimeString()}
                          </span>
                          {isComplete && (
                            <div className="flex items-center space-x-1">
                              <Zap className="w-3 h-3 text-yellow-500" />
                              <span className="text-xs text-gray-500">
                                Confidence: {Math.round(step.confidence * 100)}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
