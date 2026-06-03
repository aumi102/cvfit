import axios from 'axios';
import { API_BASE_URL } from '@/utils/constants';
import { clearAuthSession, getStoredAuthToken } from './authStorage';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = getStoredAuthToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status } = error.response;
      if (status === 401 && typeof window !== 'undefined') {
        const authPage = ['/login', '/register'].includes(window.location.pathname);
        if (!authPage) {
          clearAuthSession();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
