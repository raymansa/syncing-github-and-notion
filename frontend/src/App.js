import React, { useState, useEffect, useRef } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import { logout } from './services/apiService';
import './App.css';
import { jwtDecode } from "jwt-decode";

const INACTIVITY_LIMIT = 5 * 60 * 1000; // 5 minutes
const WARNING_BEFORE = 2 * 60 * 1000; // 2 minutes before logout

function App() {
    const [token, setToken] = useState(null);
    const [activeView, setActiveView] = useState('dashboard');
    const [flashMessage, setFlashMessage] = useState('');
    const logoutTimerRef = useRef(null);
    const warnTimerRef = useRef(null);

    useEffect(() => {
        const storedToken = localStorage.getItem('jwt_token');
        if (storedToken) {
            setToken(storedToken);
        }
    }, []);

    // Handle token expiry and warning
    useEffect(() => {
        if (!token) return;

        const resetTimers = () => {
            // Clear previous timers
            if (logoutTimerRef.current) clearTimeout(logoutTimerRef.current);
            if (warnTimerRef.current) clearTimeout(warnTimerRef.current);

            // Remove warning flash message if present
            setFlashMessage(prev =>
                prev === "You will be logged out in 2 minutes due to inactivity." ? "" : prev
            );

            // Set warning timer
            warnTimerRef.current = setTimeout(() => {
                setFlashMessage("You will be logged out in 2 minutes due to inactivity.");
            }, INACTIVITY_LIMIT - WARNING_BEFORE);

            // Set logout timer
            logoutTimerRef.current = setTimeout(() => {
                setFlashMessage("You have been logged out due to inactivity.");
                handleLogout();
            }, INACTIVITY_LIMIT);
        };

        // List of events that count as activity
        const activityEvents = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll'];
        activityEvents.forEach(event =>
            window.addEventListener(event, resetTimers)
        );

        // Start timers initially
        resetTimers();

        // Cleanup
        return () => {
            activityEvents.forEach(event =>
                window.removeEventListener(event, resetTimers)
            );
            if (logoutTimerRef.current) clearTimeout(logoutTimerRef.current);
            if (warnTimerRef.current) clearTimeout(warnTimerRef.current);
        };
        // eslint-disable-next-line
    }, [token]);

    const handleLoginSuccess = (newToken) => {
        localStorage.setItem('jwt_token', newToken);
        setToken(newToken);
        setFlashMessage('');
    };

    const handleLogout = (message) => {
        logout();
        setToken(null);
        if (message) setFlashMessage(message);
    };

    const handleNavigation = (e, view) => {
        e.preventDefault();
        setActiveView(view);
    };

    return (
        <div className="App">
            {flashMessage && (
                <div className="flash-message">
                    {flashMessage}
                </div>
            )}
            {!token ? (
                <Login onLoginSuccess={handleLoginSuccess} setFlashMessage={setFlashMessage} />
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