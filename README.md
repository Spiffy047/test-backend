# IT ServiceDesk Backend

Flask REST API backend for the IT ServiceDesk platform with intelligent auto-assignment, advanced file handling, and comprehensive analytics.

## Features

### Intelligent Auto-Assignment System
- **Workload-based assignment** - Automatically assigns tickets to agents with least active workload
- **Live database integration** - Uses real agent data from PostgreSQL
- **Role-based filtering** - Only assigns to Technical Users and Technical Supervisors
- **Smart notifications** - Creates alerts for assigned agents and supervisors

### Advanced File Upload System
- **Multi-endpoint support** - `/api/files/upload` and `/api/upload/image`
- **Cloudinary integration** - Secure cloud storage with automatic optimization
- **Timeline integration** - File uploads appear immediately in ticket timeline
- **Enhanced field detection** - Automatically detects files in multiple form field names

### Authentication & Security
- **JWT token-based authentication** - Secure API access
- **Role-based access control** - Different permissions per user role
- **CORS configuration** - Secure cross-origin requests
- **Input validation** - Comprehensive data validation

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://user:pass@host:port/dbname
export CLOUDINARY_CLOUD_NAME=your_cloud_name
export CLOUDINARY_API_KEY=your_api_key
export CLOUDINARY_API_SECRET=your_api_secret

# Run development server
python app.py
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Tickets
- `GET /api/tickets` - List tickets with pagination
- `POST /api/tickets` - Create ticket with auto-assignment
- `GET /api/tickets/{id}` - Get ticket details
- `PUT /api/tickets/{id}` - Update ticket

### File Uploads
- `POST /api/files/upload` - Upload files to timeline
- `POST /api/upload/image` - Upload images with Cloudinary

### Agents & Assignment
- `GET /api/agents/assignable` - Get available agents
- `GET /api/analytics/agent-workload` - Agent workload data
- `GET /api/analytics/agent-performance` - Performance metrics

### Messages & Timeline
- `POST /api/messages` - Send message to ticket
- `GET /api/messages/ticket/{id}/timeline` - Get ticket timeline

## Database Schema

### Core Tables
- `users` - User accounts with roles
- `tickets` - Support tickets with auto-assignment
- `messages` - Ticket timeline messages
- `alerts` - Notification system

### Configuration Tables
- `priorities` - Priority levels with SLA targets
- `categories` - Ticket categories
- `statuses` - Ticket status definitions

## Environment Variables

```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
JWT_SECRET_KEY=your_jwt_secret
```

## Deployment

The backend is deployed on Render with automatic deployments from the main branch.

- **Production URL**: https://hotfix.onrender.com/api
- **Health Check**: https://hotfix.onrender.com/health
- **API Documentation**: Contact system administrator

## Recent Updates

- [FIXED] Fixed auto-assignment to use live database agents
- [FIXED] Enhanced file upload with dual endpoint support
- [FIXED] Added agent name resolution in ticket responses
- [FIXED] Improved error handling and debugging
- [FIXED] Fixed Content-Type headers for multipart uploads