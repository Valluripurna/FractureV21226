import React, { useState } from 'react';
import TodoService from '../services/TodoService';

const TodoItem = ({ todo, onUpdate, onDelete }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [editTitle, setEditTitle] = useState(todo.title);
    const [editDescription, setEditDescription] = useState(todo.description);

    const handleUpdate = async (e) => {
        e.preventDefault();
        try {
            const updatedTodo = {
                ...todo,
                title: editTitle,
                description: editDescription,
            };
            await TodoService.updateTodo(todo.id, updatedTodo);
            onUpdate({
                ...todo,
                title: editTitle,
                description: editDescription,
            });
            setIsEditing(false);
        } catch (error) {
            console.error('Error updating todo:', error);
        }
    };

    const toggleComplete = async () => {
        try {
            const updatedTodo = {
                ...todo,
                completed: !todo.completed,
            };
            await TodoService.updateTodo(todo.id, updatedTodo);
            onUpdate(updatedTodo);
        } catch (error) {
            console.error('Error updating todo status:', error);
        }
    };

    return (
        <div className={`todo-item ${todo.completed ? 'completed' : ''}`}>
            {isEditing ? (
                <form onSubmit={handleUpdate} className="edit-form">
                    <input
                        type="text"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        placeholder="Title"
                        required
                    />
                    <textarea
                        value={editDescription}
                        onChange={(e) => setEditDescription(e.target.value)}
                        placeholder="Description"
                    />
                    <div className="edit-actions">
                        <button type="submit">Save</button>
                        <button type="button" onClick={() => setIsEditing(false)}>Cancel</button>
                    </div>
                </form>
            ) : (
                <div className="todo-content">
                    <div className="todo-header">
                        <input
                            type="checkbox"
                            checked={todo.completed}
                            onChange={toggleComplete}
                        />
                        <h3 className={todo.completed ? 'completed-title' : ''}>{todo.title}</h3>
                    </div>
                    {todo.description && <p>{todo.description}</p>}
                    <div className="todo-footer">
                        <span className="date">{new Date(todo.createdAt).toLocaleString()}</span>
                        <div className="actions">
                            <button onClick={() => setIsEditing(true)}>Edit</button>
                            <button onClick={() => onDelete(todo.id)}>Delete</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TodoItem;