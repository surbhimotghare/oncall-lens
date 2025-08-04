'use client';

import React, { useCallback, useState } from 'react';
import { Upload, File, Image, Code, X } from 'lucide-react';

interface FileWithPreview {
  file: File;
  id: string;
}

interface FileUploaderProps {
  onFilesChange: (files: File[]) => void;
  files: File[];
}

const getFileIcon = (fileName: string) => {
  const extension = fileName.split('.').pop()?.toLowerCase();
  
  switch (extension) {
    case 'png':
    case 'jpg':
    case 'jpeg':
    case 'gif':
    case 'webp':
      return <Image className="w-4 h-4 text-muted" />;
    case 'log':
    case 'txt':
    case 'diff':
    case 'js':
    case 'ts':
    case 'py':
    case 'json':
      return <Code className="w-4 h-4 text-muted" />;
    default:
      return <File className="w-4 h-4 text-muted" />;
  }
};

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export default function FileUploader({ onFilesChange, files }: FileUploaderProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [filesWithId, setFilesWithId] = useState<FileWithPreview[]>([]);

  // Update filesWithId when files prop changes
  React.useEffect(() => {
    setFilesWithId(files.map(file => ({
      file,
      id: `${file.name}-${file.size}-${file.lastModified}`
    })));
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
    const newFiles = [...files, ...droppedFiles];
    onFilesChange(newFiles);
  }, [files, onFilesChange]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      const newFiles = [...files, ...selectedFiles];
      onFilesChange(newFiles);
    }
  }, [files, onFilesChange]);

  const removeFile = useCallback((fileId: string) => {
    const updatedFiles = filesWithId
      .filter(f => f.id !== fileId)
      .map(f => f.file);
    onFilesChange(updatedFiles);
  }, [filesWithId, onFilesChange]);

  return (
    <div className="space-y-4">
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${isDragOver 
            ? 'border-accent bg-accent/5' 
            : 'border-border hover:border-accent/50'
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
          accept=".log,.txt,.diff,.png,.jpg,.jpeg,.json,.js,.ts,.py"
        />
        
        <div className="space-y-3">
          <Upload className="w-12 h-12 text-muted mx-auto" />
          <div>
            <p className="text-foreground font-medium">
              Drop your incident files here
            </p>
            <p className="text-muted text-sm mt-1">
              or click to browse (.log, .txt, .diff, .png, .jpg, etc.)
            </p>
          </div>
        </div>
      </div>

      {filesWithId.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-foreground">
            Uploaded Files ({filesWithId.length})
          </h3>
          <div className="space-y-2 max-h-48 overflow-y-auto">
            {filesWithId.map((fileWithId) => (
              <div
                key={fileWithId.id}
                className="flex items-center justify-between p-3 bg-card border border-border rounded-lg shadow-soft"
              >
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  {getFileIcon(fileWithId.file.name)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">
                      {fileWithId.file.name}
                    </p>
                    <p className="text-xs text-muted">
                      {formatFileSize(fileWithId.file.size)}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(fileWithId.id)}
                  className="p-1 text-muted hover:text-foreground hover:bg-border rounded transition-colors"
                  title="Remove file"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
} 