const API_URL = "http://127.0.0.1:5000/v1";

/**
 * Handles login request.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<string>} The JWT token.
 */
export const login = async (email, password) => {
    const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.description || 'Login failed');
    }

    const data = await response.json();
    return data.token;
};

/**
 * Fetches dashboard data using a JWT token for authentication.
 * @returns {Promise<object>} The dashboard data.
 */
export const getDashboardData = async () => {
    const token = localStorage.getItem('jwt_token');
    if (!token) {
        throw new Error('No authentication token found.');
    }

    const response = await fetch(`${API_URL}/dashboard`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });

    if (response.status === 401) {
        throw new Error('Unauthorized: Token expired or invalid');
    }

    if (!response.ok) {
        throw new Error('Failed to fetch dashboard data.');
    }
    return response.json();
};

/**
 * Removes the token from local storage.
 */
export const logout = () => {
    localStorage.removeItem('jwt_token');
};

/**
 * Fetches activity logs from the backend.
 * @returns {Promise<object>} The logs data and pagination info.
 */
export const getLogs = async () => {
    const token = localStorage.getItem('jwt_token');
    if (!token) {
        throw new Error('No authentication token found.');
    }

    const response = await fetch(`${API_URL}/logs`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    });

    if (!response.ok) {
        throw new Error('Failed to fetch logs.');
    }

    return response.json();
};