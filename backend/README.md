# Taxify AI assistant - Backend

## 🚀 Features Implemented

### ✅ Core Features
- User authentication (JWT-based)
- Chat with AI about tax reforms
- Conversation history
- Document ingestion for RAG system

### ✅ Security Features
- Password hashing with bcrypt
- Rate limiting on all endpoints
- Account lockout after failed attempts
- Input validation and sanitization
- CORS protection

### ✅ User Management
- Registration with email validation
- Login with secure token issuance
- Profile update (full name)
- Password change with current password verification
- Password reset flow with tokens
- Account lockout protection

### ✅ Error Handling
- Consistent error responses
- User-friendly error messages
- Detailed logging for debugging
- Graceful degradation when services fail

### ✅ Monitoring & Logging
- Request logging middleware
- System logs for security events
- Rate limit tracking
- Health check endpoints

## 📁 Project Structure

```

backend/
├── main.py              # FastAPI app with error handlers
├── database.py          # Database connection & schema
├── auth.py              # Authentication endpoints
├── chat.py              # Chat endpoints with AI
├── ingest.py            # Document ingestion
├── errors.py            # Custom error handling
├── security.py          # Security utilities
├── rate_limiter.py      # Rate limiting middleware
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md           # This file

```

## 🔧 Setup Instructions

1. **Create database:**
   ```sql
   CREATE DATABASE tax_assistant_db;
```

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```
3. Run the server:
   ```bash
   cd ..
   uvicorn backend.main:app --reload --port 8000
   ```

🔐 Authentication Flow

1. Register: POST /api/auth/register
2. Login: POST /api/auth/login → Returns JWT token
3. Use token: Add Authorization: Bearer <token> header
4. Token expiry: 7 days (configurable in .env)

📊 Rate Limiting

· Login: 10 attempts per minute per IP
· Register: 5 attempts per minute per IP
· Chat: 50 messages per hour per user
· Password reset: 3 requests per hour per IP

🩺 Health Checks

· Basic: GET /health
· Detailed: GET /health/detailed (checks DB, AI engine)
· Metrics: GET /metrics (basic metrics)

🐛 Error Responses

All errors follow this format:

```json
{
  "error": "ERROR_CODE",
  "message": "User-friendly message",
  "detail": "Technical details (optional)",
  "code": "APP-1001",
  "timestamp": "2024-01-06T10:30:00Z",
  "request_id": "req_123456"
}
```

🎯 Demo Credentials

For testing:

· Email: user@example.com
· Password: user123
· Or register new account

🔗 API Documentation

Once running, visit:

· Swagger UI: http://localhost:8000/docs
· ReDoc: http://localhost:8000/redoc



During demo, if something fails:

1. Check http://localhost:8000/health
2. Look at server logs for errors
3. All endpoints have graceful fallbacks

```
