import React, { useState, useEffect } from 'react';
import TodoItem from './TodoItem';
import TodoForm from './TodoForm';
import TodoService from '../services/TodoService';

const TodoList = () => {
    const [todos, setTodos] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // 'all', 'active', 'completed'

    useEffect(() => {
        loadTodos();
    }, []);

    const loadTodos = async () => {
        try {
            let completedFilter = null;
            if (filter === 'active') {
                completedFilter = false;
            } else if (filter === 'completed') {
                completedFilter = true;
            }

            const response = await TodoService.getTodos(completedFilter);
            setTodos(response.data);
            setLoading(false);
        } catch (error) {
            console.error('Error loading todos:', error);
            setLoading(false);
        }
    };

    useEffect(() => {
        loadTodos();
    }, [filter]);

    const handleAddTodo = (newTodo) => {
        setTodos([newTodo, ...todos]);
    };

    const handleUpdateTodo = (updatedTodo) => {
        setTodos(todos.map(todo => 
            todo.id === updatedTodo.id ? updatedTodo : todo
        ));
    };

    const handleDeleteTodo = async (id) => {
        try {
            await TodoService.deleteTodo(id);
            setTodos(todos.filter(todo => todo.id !== id));
        } catch (error) {
            console.error('Error deleting todo:', error);
        }
    };

    const filteredTodos = todos.filter(todo => {
        if (filter === 'active') return !todo.completed;
        if (filter === 'completed') return todo.completed;
        return true;
    });

    if (loading) {
        return <div className="loading">Loading todos...</div>;
    }

    return (
        <div className="todo-list-container">
            <h1>Todo List</h1>
            
            <div className="filters">
                <button 
                    className={filter === 'all' ? 'active' : ''}
                    onClick={() => setFilter('all')}
                >
                    All
                </button>
                <button 
                    className={filter === 'active' ? 'active' : ''}
                    onClick={() => setFilter('active')}
                >
                    Active
                </button>
                <button 
                    className={filter === 'completed' ? 'active' : ''}
                    onClick={() => setFilter('completed')}
                >
                    Completed
                </button>
            </div>

            <TodoForm onAddTodo={handleAddTodo} />

            <div className="todo-list">
                {filteredTodos.length > 0 ? (
                    filteredTodos.map(todo => (
                        <TodoItem
                            key={todo.id}
                            todo={todo}
                            onUpdate={handleUpdateTodo}
                            onDelete={handleDeleteTodo}
                        />
                    ))
                ) : (
                    <div className="no-todos">No todos found</div>
                )}
            </div>
        </div>
    );
};

export default TodoList;