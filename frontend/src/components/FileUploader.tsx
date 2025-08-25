'use client';

import React, { useCallback, useState } from 'react';
import { Upload, File, Image, Code, X, AlertTriangle, CheckCircle2, FileText, Database, GitBranch, BarChart3, FileImage } from 'lucide-react';

interface FileWithPreview {
  file: File;
  id: string;
  isValid: boolean;
  validationMessage?: string;
  fileType: 'log' | 'code' | 'image' | 'data' | 'other';
  preview?: string;
}

interface FileUploaderProps {
  onFilesChange: (files: File[]) => void;
  files: File[];
}

// Enhanced file type detection with validation
const getFileInfo = (file: File) => {
  const extension = file.name.split('.').pop()?.toLowerCase() || '';
  const maxSize = 50 * 1024 * 1024; // 50MB max
  
  let fileType: FileWithPreview['fileType'] = 'other';
  let icon = <File className="w-4 h-4" />;
  let isValid = true;
  let validationMessage = '';

  // Size validation
  if (file.size > maxSize) {
    isValid = false;
    validationMessage = 'File size exceeds 50MB limit';
  }

  // Type detection and validation
  switch (extension) {
    case 'png':
    case 'jpg':
    case 'jpeg':
    case 'gif':
    case 'webp':
    case 'svg':
      fileType = 'image';
      icon = <FileImage className="w-4 h-4 text-green-600" />;
      if (file.size > 10 * 1024 * 1024) { // 10MB for images
        isValid = false;
        validationMessage = 'Image files should be under 10MB';
      }
      break;
      
    case 'log':
    case 'txt':
      fileType = 'log';
      icon = <FileText className="w-4 h-4 text-blue-600" />;
      break;
      
    case 'diff':
    case 'patch':
      fileType = 'code';
      icon = <GitBranch className="w-4 h-4 text-purple-600" />;
      break;
      
    case 'js':
    case 'ts':
    case 'py':
    case 'java':
    case 'cpp':
    case 'c':
    case 'go':
    case 'rs':
    case 'php':
    case 'rb':
      fileType = 'code';
      icon = <Code className="w-4 h-4 text-indigo-600" />;
      break;
      
    case 'json':
    case 'yaml':
    case 'yml':
    case 'xml':
    case 'csv':
      fileType = 'data';
      icon = <Database className="w-4 h-4 text-orange-600" />;
      break;
      
    case 'md':
    case 'markdown':
      fileType = 'log';
      icon = <FileText className="w-4 h-4 text-gray-600" />;
      break;
      
    default:
      if (!isValid) break; // Keep existing validation message
      isValid = false;
      validationMessage = `Unsupported file type: .${extension}. Supported: .log, .txt, .diff, .png, .jpg, .json, .js, .py, etc.`;
  }

  return { fileType, icon, isValid, validationMessage };
};

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const getFileTypeLabel = (fileType: FileWithPreview['fileType']): string => {
  switch (fileType) {
    case 'log': return 'Log File';
    case 'code': return 'Code/Diff';
    case 'image': return 'Image';
    case 'data': return 'Data File';
    default: return 'Document';
  }
};

const getFileTypeColor = (fileType: FileWithPreview['fileType']): string => {
  switch (fileType) {
    case 'log': return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'code': return 'bg-purple-100 text-purple-800 border-purple-200';
    case 'image': return 'bg-green-100 text-green-800 border-green-200';
    case 'data': return 'bg-orange-100 text-orange-800 border-orange-200';
    default: return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

export default function FileUploader({ onFilesChange, files }: FileUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [filesWithId, setFilesWithId] = useState<FileWithPreview[]>([]);

  // Update filesWithId when files prop changes
  React.useEffect(() => {
    const newFilesWithId = files.map(file => {
      const fileInfo = getFileInfo(file);
      return {
        file,
        id: `${file.name}-${file.size}-${file.lastModified}`,
        isValid: fileInfo.isValid,
        validationMessage: fileInfo.validationMessage,
        fileType: fileInfo.fileType
      };
    });
    setFilesWithId(newFilesWithId);
  }, [files]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    // Filter out duplicates by name and size
    const existingFileKeys = files.map(f => `${f.name}-${f.size}`);
    const uniqueNewFiles = droppedFiles.filter(file => 
      !existingFileKeys.includes(`${file.name}-${file.size}`)
    );
    
    const newFiles = [...files, ...uniqueNewFiles];
    onFilesChange(newFiles);
  }, [files, onFilesChange]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      // Filter out duplicates by name and size
      const existingFileKeys = files.map(f => `${f.name}-${f.size}`);
      const uniqueNewFiles = selectedFiles.filter(file => 
        !existingFileKeys.includes(`${file.name}-${file.size}`)
      );
      
      const newFiles = [...files, ...uniqueNewFiles];
      onFilesChange(newFiles);
    }
    // Reset input value to allow re-uploading the same file
    e.target.value = '';
  }, [files, onFilesChange]);

  const removeFile = useCallback((fileId: string) => {
    const updatedFiles = filesWithId
      .filter(f => f.id !== fileId)
      .map(f => f.file);
    onFilesChange(updatedFiles);
  }, [filesWithId, onFilesChange]);

  const validFiles = filesWithId.filter(f => f.isValid);
  const invalidFiles = filesWithId.filter(f => !f.isValid);

  return (
    <div className="space-y-6">
      {/* Enhanced Drag & Drop Area */}
      <div
        className={`
          relative border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300
          ${isDragOver 
            ? 'border-blue-400 bg-blue-50 shadow-lg scale-105' 
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          multiple
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          accept=".log,.txt,.diff,.png,.jpg,.jpeg,.json,.js,.ts,.py,.java,.cpp,.yaml,.yml,.md,.csv,.xml"
        />
        
        <div className="space-y-4">
          <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 ${
            isDragOver ? 'bg-blue-100' : 'bg-gray-100'
          }`}>
            <Upload className={`w-8 h-8 transition-colors duration-300 ${
              isDragOver ? 'text-blue-600' : 'text-gray-500'
            }`} />
          </div>
          
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {isDragOver ? 'Drop files here!' : 'Upload Incident Files'}
            </h3>
            <p className="text-gray-600 text-sm">
              Drag and drop files here, or <span className="text-blue-600 font-medium">click to browse</span>
            </p>
            <p className="text-xs text-gray-500 mt-2">
              Supports: logs, code, diffs, images, config files (max 50MB each)
            </p>
          </div>
        </div>
      </div>

      {/* File Type Guide */}
      {filesWithId.length === 0 && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="flex flex-col items-center p-3 bg-blue-50 rounded-lg border border-blue-200">
            <FileText className="w-6 h-6 text-blue-600 mb-2" />
            <span className="text-xs font-medium text-blue-800">Log Files</span>
            <span className="text-xs text-blue-600">.log, .txt</span>
          </div>
          <div className="flex flex-col items-center p-3 bg-purple-50 rounded-lg border border-purple-200">
            <GitBranch className="w-6 h-6 text-purple-600 mb-2" />
            <span className="text-xs font-medium text-purple-800">Code Diffs</span>
            <span className="text-xs text-purple-600">.diff, .patch</span>
          </div>
          <div className="flex flex-col items-center p-3 bg-green-50 rounded-lg border border-green-200">
            <FileImage className="w-6 h-6 text-green-600 mb-2" />
            <span className="text-xs font-medium text-green-800">Screenshots</span>
            <span className="text-xs text-green-600">.png, .jpg</span>
          </div>
          <div className="flex flex-col items-center p-3 bg-orange-50 rounded-lg border border-orange-200">
            <Database className="w-6 h-6 text-orange-600 mb-2" />
            <span className="text-xs font-medium text-orange-800">Config Files</span>
            <span className="text-xs text-orange-600">.json, .yaml</span>
          </div>
        </div>
      )}

      {/* Valid Files List */}
      {validFiles.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-gray-900 flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-green-600" />
              <span>Ready for Analysis ({validFiles.length})</span>
            </h3>
            {validFiles.length > 3 && (
              <button
                onClick={() => onFilesChange([])}
                className="text-xs text-gray-500 hover:text-gray-700 font-medium"
              >
                Clear All
              </button>
            )}
          </div>
          
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {validFiles.map((fileWithId) => {
              const fileInfo = getFileInfo(fileWithId.file);
              return (
                <div
                  key={fileWithId.id}
                  className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-all duration-200"
                >
                  <div className="flex items-center space-x-4 flex-1 min-w-0">
                    <div className="flex-shrink-0">
                      {fileInfo.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {fileWithId.file.name}
                        </p>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getFileTypeColor(fileWithId.fileType)}`}>
                          {getFileTypeLabel(fileWithId.fileType)}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(fileWithId.file.size)} • Modified {new Date(fileWithId.file.lastModified).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(fileWithId.id)}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200"
                    title="Remove file"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Invalid Files List */}
      {invalidFiles.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-red-900 flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-red-600" />
            <span>Issues Found ({invalidFiles.length})</span>
          </h3>
          
          <div className="space-y-2">
            {invalidFiles.map((fileWithId) => (
              <div
                key={fileWithId.id}
                className="flex items-center justify-between p-4 bg-red-50 border border-red-200 rounded-lg"
              >
                <div className="flex items-center space-x-4 flex-1 min-w-0">
                  <AlertTriangle className="w-5 h-5 text-red-500 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-red-900 truncate">
                      {fileWithId.file.name}
                    </p>
                    <p className="text-xs text-red-700">
                      {fileWithId.validationMessage}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(fileWithId.id)}
                  className="p-2 text-red-400 hover:text-red-600 hover:bg-red-100 rounded-lg transition-colors"
                  title="Remove file"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Upload Summary */}
      {filesWithId.length > 0 && (
        <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600">
            <span className="font-medium">{validFiles.length}</span> files ready
            {invalidFiles.length > 0 && (
              <span>, <span className="text-red-600 font-medium">{invalidFiles.length}</span> with issues</span>
            )}
          </div>
          {validFiles.length > 0 && (
            <div className="text-xs text-green-600 font-medium flex items-center space-x-1">
              <CheckCircle2 className="w-3 h-3" />
              <span>Ready to analyze</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
} 