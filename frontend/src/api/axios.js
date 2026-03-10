import axios from "axios";

// Create axios instance with proper configuration
const api = axios.create({
    baseURL: "http://127.0.0.1:8000",
    headers: {
        "Content-Type": "application/json"
    },
    timeout: 10000, // 10 second timeout
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        console.error('Request Error:', error);
        return Promise.reject(error);
    }
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        console.log('Full Error:', error);

        // Network error (backend not reachable)
        if (error.code === 'ECONNABORTED') {
            console.error('Request timeout');
            throw new Error('Request timeout. Please try again.');
        }

        if (error.request && !error.response) {
            console.error('Backend not reachable:', error.message);
            throw new Error('Backend not reachable. Is FastAPI running on http://127.0.0.1:8000?');
        }

        // Server responded with error
        if (error.response) {
            console.error('Server Error:', error.response.status, error.response.data);

            // Handle 401 Unauthorized
            if (error.response.status === 401) {
                const originalRequest = error.config;

                // Try to refresh token if not already retrying
                if (!originalRequest._retry) {
                    originalRequest._retry = true;

                    try {
                        const refreshToken = localStorage.getItem('refreshToken');
                        if (refreshToken) {
                            const response = await axios.post(
                                'http://127.0.0.1:8000/api/auth/refresh-token',
                                { refresh_token: refreshToken }
                            );

                            const { access_token } = response.data;
                            localStorage.setItem('token', access_token);

                            // Retry original request
                            originalRequest.headers.Authorization = `Bearer ${access_token}`;
                            return api(originalRequest);
                        }
                    } catch (refreshError) {
                        // Refresh failed, logout
                        localStorage.clear();
                        window.location.href = '/login';
                        throw new Error('Session expired. Please login again.');
                    }
                }
            }

            // Return error message from server
            const errorMessage = error.response.data?.detail ||
                error.response.data?.message ||
                `Server error: ${error.response.status}`;
            throw new Error(errorMessage);
        }

        // Unknown error
        throw new Error('Unexpected error occurred');
    }
);

export default api;
