import axios from 'axios';

// Create axios instance with custom config
const instance = axios.create({
  baseURL: 'http://localhost:5000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add request interceptor
instance.interceptors.request.use(
  config => {
    // Get token from localStorage
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Add response interceptor
instance.interceptors.response.use(
  response => response,
  error => {
    if (error.response) {
      // Handle different error status
      switch (error.response.status) {
        case 401:
          // Handle unauthorized error (e.g., redirect to login)
          localStorage.removeItem('token');
          window.location.href = '/login';
          break;
        case 403:
          // Handle forbidden error
          console.error('没有权限访问此资源');
          break;
        default:
          console.error('请求失败:', error.response.data);
      }
    }
    return Promise.reject(error);
  }
);

export default instance;
