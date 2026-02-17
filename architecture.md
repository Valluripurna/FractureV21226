# Architecture Overview

## System Architecture

The Todo application follows a client-server architecture with a clear separation between the frontend and backend layers.

```
┌─────────────────┐    HTTP/JSON    ┌──────────────────┐
│   Frontend      │◄───────────────►│    Backend       │
│   (React)       │                │  (Spring Boot)   │
│                 │                │                  │
│ - Components    │                │ - Controllers    │
│ - Services      │                │ - Services       │
│ - State Mgmt    │                │ - Repositories   │
│                 │                │ - Models         │
└─────────────────┘                └──────────────────┘
                                           │
                                           │ JDBC
                                           ▼
                                    ┌─────────────────┐
                                    │   Database      │
                                    │   (H2 In-Mem)   │
                                    └─────────────────┘
```

## Frontend Architecture

The frontend is built with React using a component-based architecture:

- **App.js**: Main application component
- **TodoList.js**: Container component managing state and orchestrating child components
- **TodoForm.js**: Component for adding new todos
- **TodoItem.js**: Component representing a single todo with actions
- **TodoService.js**: Service layer handling API calls

## Backend Architecture

The backend follows the standard Spring Boot layered architecture:

- **Controllers**: Handle HTTP requests and responses (TodoController)
- **Services**: Contain business logic (TodoService)
- **Repositories**: Handle data persistence (TodoRepository)
- **Models**: Represent data structures (Todo entity)

## Data Flow

1. **Creating a Todo**: 
   - User fills form in TodoForm component
   - TodoService makes POST request to `/api/todos`
   - TodoController receives request and delegates to TodoService
   - TodoService saves to TodoRepository
   - Response sent back to frontend

2. **Reading Todos**:
   - TodoList component makes GET request to `/api/todos`
   - Optional `completed` parameter for filtering
   - Data returned and rendered in TodoItem components

3. **Updating a Todo**:
   - User interacts with TodoItem component
   - PUT request sent to `/api/todos/{id}`
   - TodoController handles request and updates via TodoService

4. **Deleting a Todo**:
   - User clicks delete button in TodoItem
   - DELETE request sent to `/api/todos/{id}`
   - TodoController handles deletion via TodoService

## Technology Choices

- **Spring Boot**: Rapid development, embedded server, extensive ecosystem
- **JPA/Hibernate**: Object-relational mapping, database abstraction
- **H2 Database**: In-memory database for development, no setup required
- **React**: Component-based UI, virtual DOM, rich ecosystem
- **Axios**: Promise-based HTTP client with interceptors and error handling
- **Maven**: Dependency management and build automation

## Security Considerations

- CORS configured to allow requests from frontend origin
- Input validation using Bean Validation annotations
- SQL injection prevention through JPA parameter binding

## Scalability Considerations

- Stateless REST API allows horizontal scaling
- Separation of concerns enables independent scaling of frontend/backend
- Potential for caching layer addition
- Database abstraction allows for migration to external DB