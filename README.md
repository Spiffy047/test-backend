# IT ServiceDesk Backend

A robust Flask-based REST API for the IT ServiceDesk platform with PostgreSQL database support, real-time messaging, and comprehensive analytics.

## Features

- **RESTful API**: Complete CRUD operations for tickets, users, and agents
- **Role-Based Access**: Support for multiple user roles and permissions
- **Real-Time Messaging**: Ticket chat system with timeline view
- **Analytics Endpoints**: SLA tracking, performance metrics, aging analysis
- **Database Migrations**: Flask-Migrate for schema management
- **CORS Support**: Cross-origin requests for frontend integration

## Tech Stack

- **Flask 3.0** - Web framework
- **SQLAlchemy** - ORM and database toolkit
- **PostgreSQL** - Primary database (SQLite for development)
- **Flask-Migrate** - Database migrations
- **Marshmallow** - Serialization/deserialization
- **Flask-CORS** - Cross-origin resource sharing
- **Flask-JWT-Extended** - JWT authentication (ready for implementation)

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL (for production) or SQLite (for development)
- pip

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd it-servicedesk-backend
```

2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize database
```bash
export INIT_DB=true
python app.py
```

6. Start the development server
```bash
python app.py
```

The API will be available at [http://localhost:5001](http://localhost:5001)

## Project Structure

```
app/
├── models/            # SQLAlchemy models
│   ├── ticket.py     # Ticket, Message, Activity models
│   └── user.py       # User and Agent models
├── routes/           # API route handlers
│   ├── tickets.py    # Ticket CRUD and analytics
│   ├── users.py      # User management
│   ├── agents.py     # Agent management and performance
│   └── messages.py   # Messaging and timeline
├── schemas/          # Marshmallow serialization schemas
└── __init__.py       # Flask app factory
```

## API Endpoints

### Tickets
- `GET /api/tickets` - List all tickets (with filtering)
- `POST /api/tickets` - Create new ticket
- `GET /api/tickets/{id}` - Get specific ticket
- `PUT /api/tickets/{id}` - Update ticket
- `DELETE /api/tickets/{id}` - Delete ticket
- `GET /api/tickets/analytics/sla-adherence` - SLA metrics
- `GET /api/tickets/analytics/aging` - Ticket aging analysis

### Users
- `GET /api/users` - List users
- `POST /api/users` - Create user
- `GET /api/users/{id}` - Get user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Agents
- `GET /api/agents` - List agents
- `POST /api/agents` - Create agent
- `GET /api/agents/{id}` - Get agent
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent
- `GET /api/agents/performance` - Performance metrics

### Messages
- `GET /api/messages/ticket/{id}` - Get ticket messages
- `GET /api/messages/ticket/{id}/timeline` - Get combined timeline
- `POST /api/messages` - Send message
- `PUT /api/messages/{id}` - Update message
- `DELETE /api/messages/{id}` - Delete message

## Database Schema

### Core Tables
- `users` - System users with roles
- `agents` - Technical support agents
- `tickets` - Support tickets with SLA tracking
- `ticket_messages` - Chat messages
- `ticket_activities` - Audit trail of changes

### Key Features
- **Automatic SLA Calculation**: Based on priority and creation time
- **Activity Logging**: Tracks all ticket changes
- **Performance Metrics**: Calculated agent statistics
- **Relationship Management**: Proper foreign keys and cascading

## Environment Configuration

```bash
# .env file
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=postgresql://username:password@localhost/servicedesk_db
JWT_SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=http://localhost:5173
```

## Database Migration

```bash
# Initialize migrations (first time only)
flask db init

# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade
```

## Sample Data

The application includes sample data initialization:

- 4 users with different roles
- 5 technical agents
- 3 sample tickets with various statuses
- Realistic performance metrics

## Production Deployment

### Using Docker (Recommended)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### Using Heroku

```bash
# Install Heroku CLI and login
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set FLASK_ENV=production
git push heroku main
```

### Environment Variables for Production

```bash
FLASK_ENV=production
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=secure-random-key
CORS_ORIGINS=https://your-frontend-domain.com
```

## Testing

```bash
# Run tests (when implemented)
python -m pytest

# Test API endpoints
curl http://localhost:5000/health
curl http://localhost:5000/api/tickets
```

## Performance Considerations

- **Database Indexing**: Key fields are indexed for performance
- **Query Optimization**: Efficient queries with proper joins
- **Pagination**: Large result sets should be paginated
- **Caching**: Consider Redis for frequently accessed data

## Security Features

- **Input Validation**: Marshmallow schema validation
- **SQL Injection Prevention**: SQLAlchemy ORM protection
- **CORS Configuration**: Controlled cross-origin access
- **JWT Ready**: Authentication framework prepared

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License