import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080/api/todos';

class TodoService {
    // Get all todos
    getTodos(completed = null) {
        let url = API_BASE_URL;
        if (completed !== null) {
            url += `?completed=${completed}`;
        }
        return axios.get(url);
    }

    // Create a new todo
    createTodo(todo) {
        return axios.post(API_BASE_URL, todo);
    }

    // Update an existing todo
    updateTodo(id, todo) {
        return axios.put(`${API_BASE_URL}/${id}`, todo);
    }

    // Delete a todo
    deleteTodo(id) {
        return axios.delete(`${API_BASE_URL}/${id}`);
    }
}

export default new TodoService();