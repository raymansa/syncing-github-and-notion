import React, { useState } from 'react';
import { login } from '../services/apiService';

const Login = ({ onLoginSuccess }) => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        try {
            const token = await login(email, password);
            onLoginSuccess(token);
        } catch (err) {
            // If the error is a JSON parse error or contains HTML, show a friendly message
            if (
                err.message.includes("Unexpected token") ||
                err.message.includes("not valid JSON") ||
                err.message.includes("<!doctype")
            ) {
                setError("Your Login Details are incorrect");
            } else {
                setError(err.message || 'An unknown error occurred.');
            }
        }
    };

    return (
        <div className="login-container">
            <div className="login-card">
                <h1>Nueroflux Project Admin</h1>
                {error && <p className="error-message">{error}</p>}
                <form id="login-form" onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label htmlFor="email">Email</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="password">Password</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />
                    </div>
                    <button type="submit" className="btn btn-primary">Login</button>
                    <p className="forgot-password"><a href="#">Forgot Password?</a></p>
                </form>
            </div>
        </div>
    );
};

export default Login;