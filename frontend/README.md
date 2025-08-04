# Oncall Lens Frontend

A clean, functional Next.js frontend for the Oncall Lens incident analysis tool. Built with GitHub-inspired aesthetics and ChatGPT minimalism for on-call engineers who need fast, efficient incident analysis.

## Features

- **Two-Column Layout**: Input controls on the left, analysis results on the right
- **Drag & Drop File Upload**: Support for logs, diffs, screenshots, and more
- **Real-time Analysis**: Loading states and progress indicators
- **Markdown Rendering**: Rich formatting with syntax highlighting for code blocks
- **Light Theme**: Clean, high-contrast design optimized for readability
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Next.js 15** with App Router
- **TypeScript** for type safety
- **Tailwind CSS** for styling
- **Lucide React** for icons
- **React Markdown** with syntax highlighting
- **Custom color palette** inspired by GitHub/Linear aesthetics

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

### Environment Variables

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

### File Structure

```
src/
├── app/
│   ├── globals.css       # Global styles and CSS variables
│   ├── layout.tsx        # Root layout with metadata
│   └── page.tsx          # Main application page
├── components/
│   ├── FileUploader.tsx  # Drag & drop file upload component
│   └── AnalysisResult.tsx # Markdown result display component
└── services/
    └── api.ts            # API client for backend communication
```

### Key Components

- **FileUploader**: Handles drag & drop, file validation, and file list display
- **AnalysisResult**: Renders markdown with syntax highlighting and loading states
- **API Service**: Manages communication with the FastAPI backend

### Color Palette

The application uses a custom light theme:

- Background: `#F9FAFB` (Light gray)
- Cards: `#FFFFFF` (Pure white)
- Text: `#111827` (Dark charcoal)
- Accent: `#4F46E5` (Indigo)
- Borders: `#E5E7EB` (Subtle gray)

## Building for Production

```bash
# Build the application
npm run build

# Start production server
npm start
```

## Backend Integration

The frontend expects a FastAPI backend running on `http://localhost:8000` with the following endpoint:

- `POST /summarize` - Accepts multipart file uploads and returns analysis results

## Design Philosophy

This UI follows the principle of **Function Over Form**:

- Clean, uncluttered interface
- High contrast for readability
- Minimal animations and visual noise
- Information-dense design for busy engineers
- GitHub-inspired functionality with ChatGPT minimalism
