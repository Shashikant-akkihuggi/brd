import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor for error handling and token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // If 401 and we haven't tried to refresh yet
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refreshToken');

                if (!refreshToken) {
                    throw new Error('No refresh token available');
                }

                // Try to refresh the access token
                const response = await axios.post(`${API_BASE_URL}/auth/refresh-token`, {
                    refresh_token: refreshToken
                });

                const { access_token } = response.data;

                // Store new access token
                localStorage.setItem('token', access_token);

                // Retry original request with new token
                originalRequest.headers.Authorization = `Bearer ${access_token}`;
                return api(originalRequest);
            } catch (refreshError) {
                // Refresh failed, logout user
                localStorage.removeItem('token');
                localStorage.removeItem('refreshToken');
                localStorage.removeItem('user');
                window.location.href = '/login';
                toast.error('Session expired. Please login again.');
                return Promise.reject(refreshError);
            }
        }

        // Handle other errors
        if (error.response?.data?.detail) {
            toast.error(error.response.data.detail);
        } else if (error.message) {
            toast.error(error.message);
        } else {
            toast.error('An error occurred. Please try again.');
        }

        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    register: (data) => api.post('/api/auth/register', data),
    login: (data) => api.post('/api/auth/login', data),
    refreshToken: (refreshToken) => api.post('/api/auth/refresh-token', { refresh_token: refreshToken }),
    logout: (refreshToken) => api.post('/api/auth/logout', { refresh_token: refreshToken }),
    logoutAll: () => api.post('/api/auth/logout-all'),
    getMe: () => api.get('/api/auth/me'),
};

// Projects API
export const projectsAPI = {
    list: () => api.get('/api/projects'),
    get: (id) => api.get(`/api/projects/${id}`),
    create: (data) => api.post('/api/projects', data),
    delete: (id) => api.delete(`/api/projects/${id}`),
};

// Documents API
export const documentsAPI = {
    generate: (projectId) => api.post(`/api/documents/${projectId}/generate`),
    list: (projectId) => api.get(`/api/documents/${projectId}/documents`),
    get: (documentId) => api.get(`/api/documents/document/${documentId}`),
    exportPdf: (projectId) => api.get(`/api/documents/${projectId}/export/pdf`, { responseType: 'blob' }),
    exportWord: (projectId) => api.get(`/api/documents/${projectId}/export/word`, { responseType: 'blob' }),
    exportExcel: (projectId) => api.get(`/api/documents/${projectId}/export/excel`, { responseType: 'blob' }),
    traceability: (projectId) => api.get(`/api/documents/${projectId}/traceability`),
};

// Requirements API (using root endpoints)
export const requirementsAPI = {
    list: (projectId) => api.get(`/requirements/${projectId}`),
};

// Ingestion API (using root endpoints)
export const ingestionAPI = {
    uploadFile: (projectId, file) => {
        const formData = new FormData();
        formData.append('file', file);
        return api.post(`/upload-file/${projectId}`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },
    extractRequirements: (projectId) => api.post(`/extract-requirements/${projectId}`),
};

// Editing API
export const editingAPI = {
    edit: (documentId, instruction, section) => api.post(`/editing/${documentId}/edit`, { instruction, section }),
};

export default api;
