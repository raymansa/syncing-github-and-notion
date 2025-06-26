import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import { logout } from './services/apiService';
import './App.css';

function App() {
    const [token, setToken] = useState(null);
    const [activeView, setActiveView] = useState('dashboard');
    const [flashMessage, setFlashMessage] = useState('');

    useEffect(() => {
        const storedToken = localStorage.getItem('jwt_token');
        if (storedToken) {
            setToken(storedToken);
        }
    }, []);

    const handleLoginSuccess = (newToken) => {
        localStorage.setItem('jwt_token', newToken);
        setToken(newToken);
        setFlashMessage(''); // Clear any previous messages on successful login
    };

    const handleLogout = (message = '') => {
        logout(); // Clears token from localStorage
        setToken(null);
        if (message) {
            setFlashMessage(message);
        }
    };

    const handleNavigation = (e, view) => {
        e.preventDefault();
        setActiveView(view);
    };

    return (
        <div className="App">
            {!token ? (
                <Login onLoginSuccess={handleLoginSuccess} flashMessage={flashMessage} />
            ) : (
                <Dashboard
                    activeView={activeView}
                    onLogout={handleLogout}
                    onNavigate={handleNavigation}
                    setFlashMessage={setFlashMessage}
                />
            )}
        </div>
    );
}

export default App;