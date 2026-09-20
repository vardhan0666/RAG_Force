import axios from 'axios';

const API_BASE_URL = '/api/v1';

export const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('ragforge_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});