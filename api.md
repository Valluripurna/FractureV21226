# API Documentation

## Base URL

`http://localhost:8080/api/todos`

## Authentication

No authentication required for this application.

## Common Headers

- `Content-Type: application/json`
- `Accept: application/json`

## API Endpoints

### Get All Todos

**GET** `/api/todos`

#### Query Parameters

| Parameter | Type    | Required | Description |
|-----------|---------|----------|-------------|
| completed | boolean | No       | Filter todos by completion status |

#### Responses

**Success Response (200 OK)**

```json
[
  {
    "id": 1,
    "title": "Sample Todo",
    "description": "Sample description",
    "completed": false,
    "createdAt": "2023-01-01T10:00:00"
  }
]
```

### Create Todo

**POST** `/api/todos`

#### Request Body

| Field       | Type    | Required | Description |
|-------------|---------|----------|-------------|
| title       | string  | Yes      | Todo title (min 1 character) |
| description | string  | No       | Todo description |
| completed   | boolean | No       | Completion status (default: false) |

#### Example Request

```json
{
  "title": "New Todo Item",
  "description": "Description for the new todo item",
  "completed": false
}
```

#### Responses

**Success Response (201 Created)**

```json
{
  "id": 2,
  "title": "New Todo Item",
  "description": "Description for the new todo item",
  "completed": false,
  "createdAt": "2023-01-01T10:00:00"
}
```

**Validation Error Response (400 Bad Request)**

```json
{
  "timestamp": "2023-01-01T10:00:00",
  "status": 400,
  "error": "Bad Request",
  "path": "/api/todos"
}
```

### Get Todo by ID

**GET** `/api/todos/{id}`

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id        | long | Yes      | Unique identifier of the todo |

#### Responses

**Success Response (200 OK)**

```json
{
  "id": 1,
  "title": "Sample Todo",
  "description": "Sample description",
  "completed": false,
  "createdAt": "2023-01-01T10:00:00"
}
```

**Not Found Response (404 Not Found)**

```json
{
  "timestamp": "2023-01-01T10:00:00",
  "status": 404,
  "error": "Not Found",
  "message": "Todo not found with id: 1",
  "path": "/api/todos/1"
}
```

### Update Todo

**PUT** `/api/todos/{id}`

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id        | long | Yes      | Unique identifier of the todo to update |

#### Request Body

| Field       | Type    | Required | Description |
|-------------|---------|----------|-------------|
| title       | string  | Yes      | Todo title (min 1 character) |
| description | string  | No       | Todo description |
| completed   | boolean | No       | Completion status |

#### Example Request

```json
{
  "title": "Updated Todo Title",
  "description": "Updated description",
  "completed": true
}
```

#### Responses

**Success Response (200 OK)**

```json
{
  "id": 1,
  "title": "Updated Todo Title",
  "description": "Updated description",
  "completed": true,
  "createdAt": "2023-01-01T10:00:00"
}
```

### Delete Todo

**DELETE** `/api/todos/{id}`

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id        | long | Yes      | Unique identifier of the todo to delete |

#### Responses

**Success Response (204 No Content)**

No response body.

**Not Found Response (404 Not Found)**

```json
{
  "timestamp": "2023-01-01T10:00:00",
  "status": 404,
  "error": "Not Found",
  "message": "Todo not found with id: 1",
  "path": "/api/todos/1"
}
```

## Error Responses

All error responses follow the standard Spring Boot error format:

```json
{
  "timestamp": "2023-01-01T10:00:00",
  "status": 400,
  "error": "Bad Request",
  "message": "Detailed error message",
  "path": "/api/todos"
}
```

## Model Definitions

### Todo

| Field       | Type      | Description |
|-------------|-----------|-------------|
| id          | long      | Unique identifier |
| title       | string    | Todo title (required) |
| description | string    | Todo description (optional) |
| completed   | boolean   | Completion status |
| createdAt   | datetime  | Creation timestamp |

## Common HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `204 No Content` - Request successful, no content to return
- `400 Bad Request` - Invalid request format or validation error
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error