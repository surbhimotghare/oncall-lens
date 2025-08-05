'use client';

import { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Eye, EyeOff, Save, X } from 'lucide-react';

interface ApiKeys {
  openaiApiKey: string;
  cohereApiKey: string;
}

interface SettingsProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (apiKeys: ApiKeys) => void;
}

export default function Settings({ isOpen, onClose, onSave }: SettingsProps) {
  const [apiKeys, setApiKeys] = useState<ApiKeys>({
    openaiApiKey: '',
    cohereApiKey: ''
  });
  const [showOpenAIKey, setShowOpenAIKey] = useState(false);
  const [showCohereKey, setShowCohereKey] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Load saved API keys from localStorage on component mount
  useEffect(() => {
    if (isOpen) {
      const savedOpenAIKey = localStorage.getItem('oncall_openai_api_key') || '';
      const savedCohereKey = localStorage.getItem('oncall_cohere_api_key') || '';
      setApiKeys({
        openaiApiKey: savedOpenAIKey,
        cohereApiKey: savedCohereKey
      });
    }
  }, [isOpen]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Save to localStorage
      localStorage.setItem('oncall_openai_api_key', apiKeys.openaiApiKey);
      localStorage.setItem('oncall_cohere_api_key', apiKeys.cohereApiKey);
      
      // Call parent save function
      onSave(apiKeys);
      
      // Close the modal
      onClose();
    } catch (error) {
      console.error('Failed to save API keys:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleKeyChange = (key: keyof ApiKeys, value: string) => {
    setApiKeys(prev => ({
      ...prev,
      [key]: value
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-2xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-t-xl">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <SettingsIcon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">API Settings</h2>
              <p className="text-sm text-gray-500 dark:text-gray-400">Configure your API keys for analysis</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* OpenAI API Key */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-900 dark:text-white">
              OpenAI API Key *
            </label>
            <div className="relative">
              <input
                type={showOpenAIKey ? 'text' : 'password'}
                value={apiKeys.openaiApiKey}
                onChange={(e) => handleKeyChange('openaiApiKey', e.target.value)}
                placeholder="sk-proj-..."
                className="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              <button
                type="button"
                onClick={() => setShowOpenAIKey(!showOpenAIKey)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                {showOpenAIKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Required for AI analysis. Get your key from{' '}
              <a
                href="https://platform.openai.com/api-keys"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 underline"
              >
                OpenAI Platform
              </a>
            </p>
          </div>

          {/* Cohere API Key */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-900 dark:text-white">
              Cohere API Key (Optional)
            </label>
            <div className="relative">
              <input
                type={showCohereKey ? 'text' : 'password'}
                value={apiKeys.cohereApiKey}
                onChange={(e) => handleKeyChange('cohereApiKey', e.target.value)}
                placeholder="sk-..."
                className="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
              />
              <button
                type="button"
                onClick={() => setShowCohereKey(!showCohereKey)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                {showCohereKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-xs text-gray-600 dark:text-gray-400">
              Optional. Used for advanced retrieval features. Get your key from{' '}
              <a
                href="https://console.cohere.ai/api-keys"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 underline"
              >
                Cohere Console
              </a>
            </p>
          </div>

          {/* Security Note */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="w-6 h-6 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 dark:text-blue-400 text-sm font-medium">🔒</span>
                </div>
              </div>
              <div>
                <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">Security & Privacy</h4>
                <p className="text-xs text-blue-800 dark:text-blue-200">
                  Your API keys are stored securely in your browser's localStorage and are sent directly to OpenAI/Cohere. 
                  They are never stored on our servers.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-b-xl">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!apiKeys.openaiApiKey.trim() || isSaving}
            className="px-6 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center space-x-2 shadow-sm"
          >
            <Save className="w-4 h-4" />
            <span>{isSaving ? 'Saving...' : 'Save Settings'}</span>
          </button>
        </div>
      </div>
    </div>
  );
} 