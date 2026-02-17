import React, { useState } from 'react';
import TodoService from '../services/TodoService';

const TodoForm = ({ onAddTodo }) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!title.trim()) return;

        try {
            const newTodo = {
                title: title.trim(),
                description: description.trim(),
                completed: false,
            };

            const response = await TodoService.createTodo(newTodo);
            onAddTodo(response.data);

            // Reset form
            setTitle('');
            setDescription('');
        } catch (error) {
            console.error('Error creating todo:', error);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="todo-form">
            <div className="form-group">
                <input
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="Enter todo title..."
                    required
                />
            </div>
            <div className="form-group">
                <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Enter description (optional)"
                />
            </div>
            <button type="submit">Add Todo</button>
        </form>
    );
};

export default TodoForm;