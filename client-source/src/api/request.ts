import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000',
    timeout: 5000,
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
}, (error) => {
    return Promise.reject(error);
});

api.interceptors.response.use((response) => {
    return response;
}, (error) => {
    if (error.response && error.response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('token');
        window.location.reload();
    }
    return Promise.reject(error);
});

export default api;
