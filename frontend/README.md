# Nigerian Tax Reform Bills 2024 Q&A Assistant (Frontend)

A modern, responsive React application that provides an intuitive interface for Nigerians to understand the 2024 Tax Reform Bills with clear, source-backed answers.

## Project Overview

This frontend application provides a user-friendly Q&A interface where users can ask questions about the new tax laws and receive accurate, citation-backed responses. The system helps fight misinformation by providing verifiable information from official sources.

## Key Features

· AI-Powered Q&A Interface: Clean, modern chat interface for asking tax-related questions
· Source Citations: All responses include references to official documents
· Conversation History: Save and revisit previous conversations via sidebar
· Mobile-First Design: Fully responsive interface that works on all devices
· Quick Questions: Pre-defined common questions for easy access
· No Personal Data: Session-based tracking without personal information collection

## Tech Stack

· Framework: React 19
· Build Tool: Vite
· Styling: Tailwind CSS
· HTTP Client: Fetch API
· Icons: React Icons

## Quick Start

Prerequisites

· Node.js 18+
· npm 

Installation

Clone and navigate to frontend directory

```bash
git clone <repository-url>
cd nigerian-tax-reform-assistant/frontend
```

Install dependencies

```bash
npm install
npm install tailwindcss @tailwindcss/vite 

env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME="Taxify I assistant"
```

Run the development server

```bash
npm run dev
```

The application will start at http://localhost:3000

### Project Structure



The frontend communicates with the backend API at VITE_API_URL (default: http://localhost:8000).

API Endpoints Used

Method Endpoint Description
POST /api/chat Send message and get AI response
GET /api/history/{session_id} Get conversation history
POST /api/new-session Create new chat session


### Key Features Implementation

Conversation Management

· Automatic session ID generation and storage
· Local storage for conversation history
· Real-time message updates

Responsive Design

· Mobile-first approach
· Breakpoints for tablet and desktop
· Collapsible sidebar on mobile

User Experience

· Loading states and indicators
· Error handling with user feedback
· Smooth animations and transitions
· Keyboard shortcuts (Enter to send)

· Mobile: < 640px (Full-width, collapsible sidebar)
· Tablet: 640px - 1024px (Adaptive layout)
· Desktop: > 1024px (Full sidebar, spacious chat)

### Development Scripts

```bash
# Development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

```

### Configuration

Vite Configuration

The project uses Vite with React plugin and Tailwind CSS. Key configurations in vite.config.js:

· React plugin for Fast Refresh
· Proxy setup for API (if needed)
· Build optimization settings

Tailwind CSS

Custom configuration in tailwind.config.js:

· Custom color palette
· Extended spacing scale
· Custom animation utilities

### Troubleshooting

Common Issues

Frontend not connecting to backend
   ```bash
   # Check backend is running
   curl http://localhost:8000/
   
   # Verify CORS settings
   # Check browser console for errors (F12)
   ```
Build errors
   ```bash
   # Clear node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   
   # Check Node.js version
   node --version  # Should be 18+
   ```
Style not loading
   ```bash
   # Rebuild Tailwind
   npm run build:css
   
   # Check Tailwind configuration
   ```




