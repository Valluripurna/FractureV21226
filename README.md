# Todo Application

A full-stack Todo application built with Spring Boot backend and React frontend.

## Tech Stack

- **Backend**: Spring Boot, Java 11+, Maven, H2 Database
- **Frontend**: React, JavaScript, Axios
- **Database**: In-memory H2 Database

## Project Structure

```
project-root/
├── backend/                 # Spring Boot application
│   ├── src/main/java/com/todo/
│   │   ├── controller/     # REST controllers
│   │   ├── service/        # Business logic
│   │   ├── repository/     # Data access layer
│   │   ├── model/          # Entity/models
│   │   └── TodoApplication.java
│   ├── pom.xml             # Maven configuration
│   └── application.properties
├── frontend/               # React application
│   ├── public/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API service calls
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── README.md
├── README.md              # Main project documentation
├── architecture.md        # System architecture overview
└── api.md                 # API documentation
```

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Run the Spring Boot application:
```bash
mvn spring-boot:run
```

The backend will be available at `http://localhost:8080`.

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the React application:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`.

## API Endpoints

The backend provides the following REST API endpoints:

- `GET /api/todos` - Get all todos (optional: ?completed=true/false)
- `POST /api/todos` - Create a new todo
- `PUT /api/todos/{id}` - Update an existing todo
- `DELETE /api/todos/{id}` - Delete a todo

## Features

- Create, read, update, and delete todos
- Mark todos as complete/incomplete
- Filter todos by completion status
- Inline editing of todos
- Responsive design

## Running Both Applications

For development, run both applications separately:

1. Start the backend first (port 8080)
2. Then start the frontend (port 3000)

The proxy configuration in the frontend will forward API requests to the backend.