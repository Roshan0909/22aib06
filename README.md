
# 22aib06 Project

This repository contains implementations for backend development with FastAPI and logging middleware functionality.

## Project Structure

### 1. Backend Test Submission
A FastAPI application with URL shortening functionality that includes:
- RESTful API endpoints for creating and managing short URLs
- Built-in logging middleware for request/response tracking
- Authentication token integration for external logging service
- Automatic expiration handling for shortened URLs

### 2. Logging Middleware
A standalone logging middleware implementation featuring:
- Custom logging function for remote log posting
- FastAPI middleware integration
- Request/response logging with timestamps
- Error handling and fallback logging

## Features
- **URL Shortening Service**: Create, manage, and redirect shortened URLs
- **Request Logging**: Comprehensive logging of all HTTP requests and responses
- **Remote Logging**: Integration with external logging service
- **Error Handling**: Robust error handling with appropriate HTTP status codes
- **Authentication**: JWT token-based authentication for logging service

## Setup Instructions

1. **Create Virtual Environment**:
   ```powershell
   python -m venv env
   .\env\Scripts\activate
   ```

2. **Install Dependencies**:
   ```powershell
   cd "Backend Test Submission"
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```powershell
   uvicorn main:app --reload
   ```

## API Endpoints
- `POST /shortUrls` - Create a new short URL
- `GET /{shortcode}` - Redirect to original URL
- `GET /shortUrls/{shortcode}` - Get URL details
- `DELETE /shortUrls/{shortcode}` - Delete a short URL

## Logging
All requests are automatically logged with:
- Timestamp
- HTTP method and path
- Response status code
- Remote logging service integration

## Output

<img width="1915" height="1023" alt="image" src="https://github.com/user-attachments/assets/2eb9f64d-694c-41c7-b350-1faeb079828d" />
