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
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-background border border-border rounded-lg shadow-lg w-full max-w-md mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <div className="flex items-center space-x-2">
            <SettingsIcon className="w-5 h-5 text-foreground" />
            <h2 className="text-lg font-semibold text-foreground">API Settings</h2>
          </div>
          <button
            onClick={onClose}
            className="text-muted hover:text-foreground transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* OpenAI API Key */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">
              OpenAI API Key *
            </label>
            <div className="relative">
              <input
                type={showOpenAIKey ? 'text' : 'password'}
                value={apiKeys.openaiApiKey}
                onChange={(e) => handleKeyChange('openaiApiKey', e.target.value)}
                placeholder="sk-..."
                className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground placeholder-muted focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
              />
              <button
                type="button"
                onClick={() => setShowOpenAIKey(!showOpenAIKey)}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-muted hover:text-foreground"
              >
                {showOpenAIKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-xs text-muted">
              Required for AI analysis. Get your key from{' '}
              <a
                href="https://platform.openai.com/api-keys"
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent hover:underline"
              >
                OpenAI Platform
              </a>
            </p>
          </div>

          {/* Cohere API Key */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">
              Cohere API Key (Optional)
            </label>
            <div className="relative">
              <input
                type={showCohereKey ? 'text' : 'password'}
                value={apiKeys.cohereApiKey}
                onChange={(e) => handleKeyChange('cohereApiKey', e.target.value)}
                placeholder="sk-..."
                className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground placeholder-muted focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
              />
              <button
                type="button"
                onClick={() => setShowCohereKey(!showCohereKey)}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 text-muted hover:text-foreground"
              >
                {showCohereKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-xs text-muted">
              Optional. Used for advanced retrieval features. Get your key from{' '}
              <a
                href="https://console.cohere.ai/api-keys"
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent hover:underline"
              >
                Cohere Console
              </a>
            </p>
          </div>

          {/* Security Note */}
          <div className="bg-muted/20 border border-border rounded-md p-4">
            <p className="text-xs text-muted">
              🔒 Your API keys are stored securely in your browser's localStorage and are sent directly to OpenAI/Cohere. 
              They are never stored on our servers.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-border">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-muted hover:text-foreground transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!apiKeys.openaiApiKey.trim() || isSaving}
            className="px-4 py-2 text-sm font-medium bg-accent text-accent-foreground rounded-md hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
          >
            <Save className="w-4 h-4" />
            <span>{isSaving ? 'Saving...' : 'Save Settings'}</span>
          </button>
        </div>
      </div>
    </div>
  );
} 