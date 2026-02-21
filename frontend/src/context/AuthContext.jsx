// src/contexts/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';
import { login } from '../services/api'; // فرض بر اینه که api.js در services وجود داره

// ساخت context
const AuthContext = createContext(null);

// Provider اصلی
export function AuthProvider({ children }) {
  // state ها
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(() => {
    // مقدار اولیه از localStorage خونده میشه
    return localStorage.getItem('access_token') || null;
  });
  const [loading, setLoading] = useState(true);

  // چک اولیه موقع لود اپلیکیشن
  useEffect(() => {
    const token = localStorage.getItem('access_token');

    if (token) {
      setAccessToken(token);
      // اگر بعداً بخوای اطلاعات کاربر رو از سرور بگیری می‌تونی اینجا درخواست بزنی
      // فعلاً فقط توکن رو نگه می‌داریم
    }

    setLoading(false);
  }, []);

  // تابع ورود (login)
  const signIn = async (email, password) => {
    try {
      const response = await login({ email, password });
      const { access } = response.data;

      // ذخیره توکن
      localStorage.setItem('access_token', access);

      // آپدیت state
      setAccessToken(access);

      // موقتاً کاربر رو با ایمیل ست می‌کنیم (بعداً می‌تونی کامل‌تر کنی)
      setUser({ email });

      return { success: true };
    } catch (error) {
      console.error('خطا در ورود:', error);

      let message = 'خطا در ورود. لطفاً دوباره تلاش کنید.';

      if (error.response?.data) {
        if (error.response.data.detail) {
          message = error.response.data.detail;
        } else if (error.response.data.non_field_errors) {
          message = error.response.data.non_field_errors[0];
        }
      }

      return { success: false, message };
    }
  };

  // تابع خروج
  const signOut = () => {
    localStorage.removeItem('access_token');
    setAccessToken(null);
    setUser(null);
  };

  // مقادیری که به همه کامپوننت‌ها می‌دم
  const value = {
    user,                // اطلاعات کاربر (فعلاً فقط email)
    accessToken,         // توکن دسترسی
    setAccessToken,      // setter توکن (حالا حتماً اینجا هست)
    isAuthenticated: !!accessToken,
    loading,             // آیا هنوز در حال چک اولیه هستیم؟
    signIn,              // تابع لاگین
    signOut,             // تابع لاگ‌اوت
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// هوک سفارشی برای استفاده راحت‌تر
export function useAuth() {
  const context = useContext(AuthContext);

  if (context === null) {
    throw new Error(
      'useAuth باید داخل AuthProvider استفاده شود. ' +
      'مطمئن شوید که کامپوننت شما داخل <AuthProvider> قرار گرفته است.'
    );
  }

  return context;
}