/**
 * Authentication service for interacting with the Express server
 * These functions demonstrate how to use credentials: 'include'
 * to send and receive cookies with cross-origin requests
 */

const API_URL = "http://localhost:5000";

/**
 * Login to the server
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<{ok: boolean}>}
 */
export const login = async (email: string, password: string) => {
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include", // This allows cookies to be sent and received
            body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
            throw new Error(`Login failed with status ${response.status}`);
        }

        const data = await response.json();
        console.log("Login successful:", data);
        return data;
    } catch (error) {
        console.error("Login error:", error);
        throw error;
    }
};

/**
 * Check if user is authenticated
 * @returns {Promise<{authenticated: boolean}>}
 */
export const checkAuthentication = async () => {
    try {
        const response = await fetch(`${API_URL}/me`, {
            method: "GET",
            credentials: "include", // This allows the session cookie to be sent
        });

        if (!response.ok) {
            throw new Error(`Auth check failed with status ${response.status}`);
        }

        const data = await response.json();
        console.log("Auth check result:", data);
        return data;
    } catch (error) {
        console.error("Auth check error:", error);
        throw error;
    }
};

/**
 * Example usage in a React component:
 *
 * import { login, checkAuthentication } from './authService';
 *
 * // In a component or event handler:
 * const handleLogin = async () => {
 *   try {
 *     const result = await login('user@example.com', 'password123');
 *     if (result.ok) {
 *       console.log('Logged in successfully');
 *       // Redirect or update state
 *     }
 *   } catch (error) {
 *     console.error('Failed to login:', error);
 *   }
 * };
 *
 * const handleCheckAuth = async () => {
 *   try {
 *     const result = await checkAuthentication();
 *     console.log('Is authenticated:', result.authenticated);
 *   } catch (error) {
 *     console.error('Failed to check auth:', error);
 *   }
 * };
 */
