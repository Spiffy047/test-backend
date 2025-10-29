# Configuration System Documentation

## Overview

The IT ServiceDesk system has been updated to remove hardcoded values and implement a dynamic, database-driven configuration system. This allows for flexible system management without code changes.

## Key Changes

### Before (Hardcoded)
```python
# Hardcoded SLA targets
sla_targets = {
    'Critical': 4,
    'High': 8, 
    'Medium': 24,
    'Low': 72
}

# Hardcoded user roles
role = db.Column(db.String(50), default='Normal User')

# Hardcoded status checks
if ticket.status == 'Closed':
    # ...
```

### After (ORM-based)
```python
# Dynamic SLA targets from database
target_hours = ticket.priority.sla_hours

# Foreign key relationships
role_id = db.Column(db.Integer, db.ForeignKey('user_roles.id'))
role = db.relationship('UserRole', backref='users')

# Dynamic status checks
if ticket.status.is_closed_status:
    # ...
```

## Configuration Tables

### 1. UserRole
Manages user roles and permissions:
- `name`: Role name (e.g., "Normal User", "Technical User")
- `description`: Role description
- `permissions`: JSON array of permissions
- `is_active`: Enable/disable role

### 2. TicketStatus
Manages ticket statuses:
- `name`: Status name (e.g., "New", "Open", "Closed")
- `description`: Status description
- `is_closed_status`: Whether this status indicates closure
- `sort_order`: Display order
- `is_active`: Enable/disable status

### 3. TicketPriority
Manages priorities with SLA targets:
- `name`: Priority name (e.g., "Critical", "High")
- `description`: Priority description
- `sla_hours`: SLA target in hours
- `escalation_hours`: Escalation threshold
- `color_code`: UI color (hex)
- `sort_order`: Display order
- `is_active`: Enable/disable priority

### 4. TicketCategory
Manages ticket categories:
- `name`: Category name (e.g., "Hardware", "Software")
- `description`: Category description
- `default_priority_id`: Default priority for this category
- `is_active`: Enable/disable category

### 5. AlertType
Manages alert types and templates:
- `name`: Alert type name (e.g., "assignment", "sla_violation")
- `description`: Alert description
- `template`: Message template with placeholders
- `is_active`: Enable/disable alert type

### 6. SystemSetting
Manages system-wide settings:
- `key`: Setting key (e.g., "auto_assign_tickets")
- `value`: Setting value (stored as string)
- `data_type`: Value type (string, integer, boolean, json)
- `description`: Setting description
- `is_editable`: Whether setting can be modified

## API Endpoints

### Configuration Management
- `GET /api/config/roles` - Get all user roles
- `GET /api/config/statuses` - Get all ticket statuses
- `GET /api/config/priorities` - Get all ticket priorities
- `GET /api/config/categories` - Get all ticket categories
- `GET /api/config/alert-types` - Get all alert types
- `GET /api/config/settings` - Get all system settings
- `PUT /api/config/settings/<key>` - Update system setting

### Initialization
- `POST /api/config/initialize` - Initialize default configuration

## Usage Examples

### 1. Getting SLA Target
```python
from app.services.configuration_service import ConfigurationService

# Get priority by name
priority = ConfigurationService.get_priority_by_name('Critical')
sla_hours = priority.sla_hours  # Returns 4

# Or directly from ticket
ticket = Ticket.query.first()
sla_hours = ticket.priority.sla_hours
```

### 2. Checking Closed Status
```python
# Check if ticket is closed
if ticket.status.is_closed_status:
    # Handle closed ticket
    pass

# Get all closed statuses
closed_statuses = [s.id for s in ConfigurationService.get_ticket_statuses() 
                   if s.is_closed_status]
```

### 3. Creating Tickets with Configuration
```python
# Get configuration objects
priority = ConfigurationService.get_priority_by_name('High')
category = ConfigurationService.get_category_by_name('Hardware')
status = ConfigurationService.get_default_status()

# Create ticket
ticket = Ticket(
    title="Server Issue",
    description="Server is down",
    priority_id=priority.id,
    category_id=category.id,
    status_id=status.id,
    created_by=user_id
)
```

### 4. System Settings
```python
# Get setting value
auto_assign = ConfigurationService.get_system_setting('auto_assign_tickets', True)

# Set setting value
ConfigurationService.set_system_setting(
    'max_file_size', 
    10485760, 
    'integer', 
    'Maximum file upload size in bytes'
)
```

## Migration Process

### 1. Run Migration Script
```bash
python migrate_to_orm.py
```

### 2. Update Database Schema
The migration script creates new tables and migrates data, but you may need to:
- Remove old string columns after verification
- Add proper indexes for performance
- Update any custom queries

### 3. Verify Configuration
```bash
# Check configuration via API
curl http://localhost:5001/api/config/priorities
curl http://localhost:5001/api/config/statuses
```

## Benefits

### 1. Flexibility
- Change SLA targets without code deployment
- Add new statuses, priorities, categories dynamically
- Modify system behavior through settings

### 2. Consistency
- Single source of truth for configuration
- Referential integrity through foreign keys
- Centralized configuration management

### 3. Maintainability
- No hardcoded values scattered in code
- Easy to audit and modify configuration
- Version control for configuration changes

### 4. Scalability
- Support for multiple environments
- Easy configuration replication
- Automated configuration deployment

## Default Configuration

The system initializes with these defaults:

### User Roles
- Normal User (create/view own tickets)
- Technical User (handle assigned tickets)
- Technical Supervisor (manage team, analytics)
- System Admin (full access)

### Ticket Priorities
- Critical: 4 hours SLA
- High: 8 hours SLA
- Medium: 24 hours SLA
- Low: 72 hours SLA

### Ticket Statuses
- New → Open → In Progress → Pending → Resolved/Closed

### Categories
- Hardware, Software, Network, Access, Email, Security

### System Settings
- Auto-assign tickets: enabled
- SLA check interval: 300 seconds
- Max file upload: 10MB
- Email notifications: enabled

## Best Practices

### 1. Configuration Changes
- Test configuration changes in development first
- Document configuration changes
- Use the API endpoints rather than direct database access
- Backup configuration before major changes

### 2. Performance
- Configuration is cached in memory where possible
- Use relationships efficiently (avoid N+1 queries)
- Index foreign key columns for performance

### 3. Security
- Restrict access to configuration endpoints
- Validate configuration values
- Audit configuration changes
- Use proper data types for settings

## Troubleshooting

### Common Issues

1. **Migration Errors**
   - Ensure all dependencies are installed
   - Check database connectivity
   - Verify table permissions

2. **Configuration Not Loading**
   - Check if initialization completed successfully
   - Verify foreign key relationships
   - Check for data type mismatches

3. **Performance Issues**
   - Add indexes on foreign key columns
   - Use eager loading for relationships
   - Cache frequently accessed configuration

### Debug Commands
```python
# Check configuration status
from app.services.configuration_service import ConfigurationService

# List all priorities
priorities = ConfigurationService.get_ticket_priorities()
for p in priorities:
    print(f"{p.name}: {p.sla_hours} hours")

# Check system settings
settings = SystemSetting.query.all()
for s in settings:
    print(f"{s.key}: {s.get_typed_value()}")
```

## Future Enhancements

1. **Configuration Versioning**
   - Track configuration changes over time
   - Rollback capability
   - Change approval workflow

2. **Environment-Specific Configuration**
   - Different settings per environment
   - Configuration inheritance
   - Environment promotion

3. **Advanced Permissions**
   - Granular permission system
   - Role-based configuration access
   - Audit logging

4. **Configuration UI**
   - Admin interface for configuration
   - Validation and testing tools
   - Configuration import/export