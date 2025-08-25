'use client';

import { useState } from 'react';
import { Copy, Share2, Download, CheckCircle2, ExternalLink } from 'lucide-react';

interface ActionButtonsProps {
  content: string;
  title?: string;
  confidence?: number;
}

export default function ActionButtons({ content, title = "Incident Analysis", confidence }: ActionButtonsProps) {
  const [copied, setCopied] = useState(false);
  const [shared, setShared] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: title,
          text: content.substring(0, 200) + '...',
          url: window.location.href,
        });
        setShared(true);
        setTimeout(() => setShared(false), 2000);
      } catch (err) {
        console.error('Failed to share:', err);
      }
    } else {
      // Fallback: copy URL to clipboard
      await navigator.clipboard.writeText(window.location.href);
      setShared(true);
      setTimeout(() => setShared(false), 2000);
    }
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([content], { type: 'text/markdown' });
    element.href = URL.createObjectURL(file);
    element.download = `incident-analysis-${new Date().toISOString().split('T')[0]}.md`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleOpenInNewTab = () => {
    const newWindow = window.open('', '_blank');
    if (newWindow) {
      newWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>${title}</title>
          <meta charset="utf-8">
          <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; }
            h1, h2, h3 { color: #1f2937; }
            code { background: #f3f4f6; padding: 2px 4px; border-radius: 4px; }
            pre { background: #f3f4f6; padding: 16px; border-radius: 8px; overflow-x: auto; }
            .confidence { background: #dbeafe; padding: 12px; border-radius: 8px; margin: 16px 0; }
          </style>
        </head>
        <body>
          ${confidence ? `<div class="confidence"><strong>Confidence: ${Math.round(confidence * 100)}%</strong></div>` : ''}
          <div>${content.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</div>
        </body>
        </html>
      `);
      newWindow.document.close();
    }
  };

  return (
    <div className="flex items-center space-x-2 p-3 bg-gray-50 border-t border-gray-200 rounded-b-xl">
      <button
        onClick={handleCopy}
        className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-white rounded-lg transition-all duration-200"
        title="Copy to clipboard"
      >
        {copied ? (
          <>
            <CheckCircle2 className="w-4 h-4 text-green-600" />
            <span className="text-green-600">Copied!</span>
          </>
        ) : (
          <>
            <Copy className="w-4 h-4" />
            <span>Copy</span>
          </>
        )}
      </button>

      <button
        onClick={handleShare}
        className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-white rounded-lg transition-all duration-200"
        title="Share analysis"
      >
        {shared ? (
          <>
            <CheckCircle2 className="w-4 h-4 text-green-600" />
            <span className="text-green-600">Shared!</span>
          </>
        ) : (
          <>
            <Share2 className="w-4 h-4" />
            <span>Share</span>
          </>
        )}
      </button>

      <button
        onClick={handleDownload}
        className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-white rounded-lg transition-all duration-200"
        title="Download as markdown"
      >
        <Download className="w-4 h-4" />
        <span>Download</span>
      </button>

      <button
        onClick={handleOpenInNewTab}
        className="flex items-center space-x-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-white rounded-lg transition-all duration-200"
        title="Open in new tab"
      >
        <ExternalLink className="w-4 h-4" />
        <span>Open</span>
      </button>
    </div>
  );
}
