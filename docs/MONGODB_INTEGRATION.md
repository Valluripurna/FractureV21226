# MongoDB Integration Documentation

## Overview

This document describes the MongoDB integration implementation for the FractureDetect AI system. The integration provides persistent storage for user data, fracture detection reports, and X-ray images.

## Implementation Details

### Database Structure

#### Collections

1. **users** - Stores user account information
2. **reports** - Stores fracture detection reports
3. **fs.files** - GridFS metadata for image storage
4. **fs.chunks** - GridFS binary data for image storage

### Connection Configuration

The MongoDB connection is configured through environment variables in the `.env` file:

```env
MONGO_URI=mongodb+srv://valluripurna:Purnavalluri03@@event.xwrdr.mongodb.net/?appName=event
```

### Database Module

The `database.py` module handles all MongoDB operations:

#### User Management
- `register_user()` - Creates new user accounts
- `authenticate_user()` - Validates user credentials
- `get_user_details()` - Retrieves user information

#### Report Management
- `save_report()` - Stores detection reports with associated images
- `get_user_reports()` - Retrieves all reports for a user
- `get_report_by_id()` - Retrieves a specific report
- `get_image_by_id()` - Retrieves stored X-ray images

## Data Models

### User Document
```javascript
{
  "_id": ObjectId,
  "name": String,
  "email": String,
  "password": String, // SHA-256 hashed
  "phone": String,
  "age": String,
  "created_at": DateTime
}
```

### Report Document
```javascript
{
  "_id": ObjectId,
  "user_email": String,
  "report_data": {
    "fracture_detected": Boolean,
    "confidence": Number,
    "probability": Number,
    "body_region": String,
    "model_version": String,
    "model_accuracy": String,
    "user_data": Object
  },
  "image_id": ObjectId, // GridFS reference
  "created_at": DateTime
}
```

## Features Implemented

### 1. Persistent User Accounts
- User registration and authentication
- Secure password storage with hashing
- User profile management

### 2. Report History
- Complete history of all fracture detections
- Timestamped records for audit trails
- Easy retrieval of past analyses

### 3. Image Storage
- Permanent storage of X-ray images
- Binary data stored in GridFS
- Association with detection reports

### 4. Data Retrieval
- Efficient querying by user email
- Sorting by creation date
- Report and image retrieval by ID

## API Endpoints

### Authentication
- `/signup` - User registration
- `/login` - User authentication
- `/user-details` - User information retrieval

### Reports
- `/user-reports` - Get all user reports
- `/report/{id}` - Get specific report
- `/report-image/{id}` - Get stored image

## Security Considerations

### Data Protection
- Passwords hashed with SHA-256
- No sensitive data in frontend code
- MongoDB Atlas encryption at rest

### Access Control
- JWT token authentication
- User-scoped data retrieval
- Secure API endpoints

## Performance Optimizations

### Indexing
- Email field indexed for fast user lookup
- Creation date indexed for sorting
- Report ID indexed for quick retrieval

### Memory Management
- Images stored externally in GridFS
- Automatic cleanup of temporary data
- Efficient connection pooling

## Error Handling

### Common Issues
- Connection failures
- Document validation errors
- GridFS storage failures
- Query timeouts

### Recovery Strategies
- Retry mechanisms for transient failures
- Graceful degradation for non-critical features
- Detailed error logging for debugging

## Maintenance

### Backup Strategy
- MongoDB Atlas automatic backups
- Point-in-time recovery
- Regular export procedures

### Monitoring
- Database performance metrics
- Connection pool monitoring
- Storage capacity tracking

## Future Enhancements

### Planned Improvements
1. **Aggregation Pipelines** - Advanced reporting analytics
2. **Data Archiving** - Automated old data archiving
3. **Replication** - High availability setup
4. **Sharding** - Horizontal scaling for large datasets

### Scalability Features
1. **Caching Layer** - Redis integration for frequent queries
2. **Read Replicas** - Load distribution for read operations
3. **Index Optimization** - Query performance improvements