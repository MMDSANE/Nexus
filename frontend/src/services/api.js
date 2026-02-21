// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor برای اضافه کردن توکن به هر درخواست
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor برای هندل کردن 401 (token منقضی) → بعداً می‌تونیم refresh token اضافه کنیم
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // اینجا بعداً می‌تونی لاگ‌اوت کنی یا refresh token بزنی
      console.warn('Unauthorized - شاید نیاز به لاگین دوباره باشه');
      // localStorage.removeItem('access_token');
      // window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// حالا helper functions برای هر endpoint مهم
export const register = (data) => api.post('/accounts/register/', data);

export const login = (data) => api.post('/accounts/login/', data);

export const getMyRooms = () => api.get('/chat/rooms/'); // MyRoomsView

export const createRoom = (name) => api.post('/chat/rooms/', { name });

export const joinRoom = (room_code) => api.post('/chat/rooms/join/', { room_code });

export const leaveRoom = (room_id) => api.post(`/chat/rooms/${room_id}/leave/`);

export const getRoomMessages = (room_id, params = {}) =>
  api.get(`/chat/rooms/${room_id}/messages/`, { params }); // pagination اگر خواستی

export const sendMessageREST = (room_id, content) =>
  api.post(`/chat/rooms/${room_id}/messages/`, { content }); // اگر بعداً نیاز شد

export default api;