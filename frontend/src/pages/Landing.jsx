// src/pages/Landing.jsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';   // اگر .env داری: import.meta.env.VITE_API_URL

function Landing() {
  const navigate = useNavigate();

  // وضعیت کاربر
  const [currentUser, setCurrentUser] = useState(null);

  // مودال
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('login'); // 'login' یا 'signup'

  // فرم لاگین
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [loginLoading, setLoginLoading] = useState(false);

  // فرم ثبت‌نام
  const [signupEmail, setSignupEmail] = useState('');
  const [signupUsername, setSignupUsername] = useState('');
  const [signupPassword, setSignupPassword] = useState('');
  const [signupError, setSignupError] = useState('');
  const [signupLoading, setSignupLoading] = useState(false);

  // ====================== لاگین ======================
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError('');
    setLoginLoading(true);

    try {
      const res = await axios.post(`${API_BASE}/accounts/login/`, {
        email: loginEmail,
        password: loginPassword,
      });

      const { access } = res.data;

      localStorage.setItem('access_token', access);
      setCurrentUser({ email: loginEmail });

      setIsModalOpen(false);
      setLoginEmail('');
      setLoginPassword('');

      // بعد از لاگین موفق مستقیم بره به لیست اتاق‌ها
      navigate('/rooms');

    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.non_field_errors?.[0] ||
        'ایمیل یا رمز عبور اشتباه است';
      setLoginError(msg);
    } finally {
      setLoginLoading(false);
    }
  };

  // ====================== ثبت‌نام ======================
  const handleSignup = async (e) => {
    e.preventDefault();
    setSignupError('');
    setSignupLoading(true);

    try {
      await axios.post(`${API_BASE}/accounts/register/`, {
        email: signupEmail,
        username: signupUsername,
        password: signupPassword,
      });

      alert('ثبت‌نام با موفقیت انجام شد! حالا وارد شوید.');
      setActiveTab('login'); // بعد از ثبت‌نام بره به تب ورود
      setSignupEmail('');
      setSignupUsername('');
      setSignupPassword('');

    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.email?.[0] ||
        err.response?.data?.username?.[0] ||
        err.response?.data?.password?.[0] ||
        'خطا در ثبت‌نام';
      setSignupError(msg);
    } finally {
      setSignupLoading(false);
    }
  };

  // ====================== خروج ======================
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setCurrentUser(null);
    navigate('/');
  };

  return (
    <div
      style={{
        background: '#111',
        color: '#f0f0f0',
        minHeight: '100vh',
        fontFamily: "'Inter', 'Segoe UI', sans-serif",
        direction: 'rtl',
      }}
    >
      {/* هدر */}
      <header
        style={{
          padding: '20px 40px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          borderBottom: '1px solid #222',
        }}
      >
        <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#667eea' }}>
          Nexus
        </div>

        {currentUser ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
            <span style={{ color: '#ccc' }}>
              خوش آمدید، <strong>{currentUser.email}</strong>
            </span>
            <button
              onClick={handleLogout}
              style={{
                background: '#764ba2',
                color: 'white',
                border: 'none',
                padding: '10px 20px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: 600,
              }}
            >
              خروج
            </button>
          </div>
        ) : (
          <button
            onClick={() => setIsModalOpen(true)}
            style={{
              background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              padding: '12px 28px',
              borderRadius: '8px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            ورود / ثبت‌نام
          </button>
        )}
      </header>

      {/* محتوای اصلی */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '60px 20px' }}>
        <div style={{ textAlign: 'center', marginBottom: '80px' }}>
          <h1
            style={{
              fontSize: '4.8rem',
              fontWeight: 800,
              letterSpacing: '-2px',
              background: 'linear-gradient(90deg, #fff, #ccc)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              marginBottom: '20px',
            }}
          >
            Nexus
          </h1>
          <p
            style={{
              fontSize: '1.35rem',
              maxWidth: '720px',
              margin: '0 auto 50px',
              color: '#ccc',
              lineHeight: 1.6,
            }}
          >
            شبکه اجتماعی آینده. جایی که لحظات و ایده‌ها می‌توانند حرکت کنند.
          </p>

          <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', flexWrap: 'wrap' }}>
            <button
              onClick={() => navigate('/rooms')}
              style={{
                background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                padding: '18px 40px',
                borderRadius: '10px',
                fontSize: '1.15rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              ایجاد چت روم جدید
            </button>

            <button
              onClick={() => navigate('/join')}
              style={{
                background: 'transparent',
                color: '#667eea',
                border: '2px solid #667eea',
                padding: '18px 40px',
                borderRadius: '10px',
                fontSize: '1.15rem',
                fontWeight: 600,
                cursor: 'pointer',
              }}
            >
              ورود به چت روم
            </button>
          </div>
        </div>

        {/* ویژگی‌ها */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '30px',
          }}
        >
          {[
            { title: 'ارتباط سریع', desc: 'با یک کلیک، لحظات خود را به اشتراک بگذارید. سریع و بدون تأخیر.' },
            { title: 'ایمنی مطلق', desc: 'داده‌های شما کاملاً محفوظ است. هیچ‌کس دسترسی ندارد.' },
            { title: 'سازگاری کامل', desc: 'در همه دستگاه‌ها و مرورگرها بدون مشکل کار می‌کند.' },
          ].map((item, i) => (
            <div
              key={i}
              style={{
                background: '#1a1a1a',
                border: '1px solid #222',
                borderRadius: '12px',
                padding: '35px 25px',
                textAlign: 'center',
              }}
            >
              <h3 style={{ fontSize: '1.5rem', marginBottom: '15px' }}>{item.title}</h3>
              <p style={{ color: '#aaa', lineHeight: 1.7 }}>{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ====================== مودال ====================== */}
      {isModalOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.85)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2000,
          }}
          onClick={() => setIsModalOpen(false)}
        >
          <div
            style={{
              background: '#1a1a1a',
              width: '100%',
              maxWidth: '440px',
              borderRadius: '16px',
              padding: '40px 35px',
              position: 'relative',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setIsModalOpen(false)}
              style={{
                position: 'absolute',
                top: '15px',
                right: '20px',
                background: 'none',
                border: 'none',
                fontSize: '28px',
                color: '#777',
                cursor: 'pointer',
              }}
            >
              ×
            </button>

            {/* تب‌ها */}
            <div style={{ display: 'flex', marginBottom: '30px', borderBottom: '1px solid #333' }}>
              <button
                onClick={() => setActiveTab('login')}
                style={{
                  flex: 1,
                  padding: '14px',
                  background: 'none',
                  border: 'none',
                  color: activeTab === 'login' ? '#fff' : '#888',
                  fontWeight: activeTab === 'login' ? 'bold' : 'normal',
                  borderBottom: activeTab === 'login' ? '3px solid #667eea' : 'none',
                }}
              >
                ورود
              </button>
              <button
                onClick={() => setActiveTab('signup')}
                style={{
                  flex: 1,
                  padding: '14px',
                  background: 'none',
                  border: 'none',
                  color: activeTab === 'signup' ? '#fff' : '#888',
                  fontWeight: activeTab === 'signup' ? 'bold' : 'normal',
                  borderBottom: activeTab === 'signup' ? '3px solid #667eea' : 'none',
                }}
              >
                ثبت‌نام
              </button>
            </div>

            {/* فرم لاگین */}
            {activeTab === 'login' && (
              <form onSubmit={handleLogin}>
                <input
                  type="email"
                  placeholder="ایمیل"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  required
                  style={inputStyle}
                />
                <input
                  type="password"
                  placeholder="رمز عبور"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  required
                  style={inputStyle}
                />

                {loginError && <p style={{ color: '#ff6b6b', margin: '10px 0' }}>{loginError}</p>}

                <button type="submit" disabled={loginLoading} style={buttonStyle(loginLoading)}>
                  {loginLoading ? 'در حال ورود...' : 'ورود به حساب'}
                </button>
              </form>
            )}

            {/* فرم ثبت‌نام */}
            {activeTab === 'signup' && (
              <form onSubmit={handleSignup}>
                <input type="email" placeholder="ایمیل" value={signupEmail} onChange={(e) => setSignupEmail(e.target.value)} required style={inputStyle} />
                <input type="text" placeholder="نام کاربری" value={signupUsername} onChange={(e) => setSignupUsername(e.target.value)} required style={inputStyle} />
                <input type="password" placeholder="رمز عبور" value={signupPassword} onChange={(e) => setSignupPassword(e.target.value)} required style={inputStyle} />

                {signupError && <p style={{ color: '#ff6b6b', margin: '10px 0' }}>{signupError}</p>}

                <button type="submit" disabled={signupLoading} style={buttonStyle(signupLoading)}>
                  {signupLoading ? 'در حال ثبت‌نام...' : 'ثبت‌نام'}
                </button>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// استایل‌های مشترک
const inputStyle = {
  width: '100%',
  padding: '14px 16px',
  marginBottom: '16px',
  background: '#222',
  border: '1px solid #444',
  borderRadius: '8px',
  color: '#fff',
  fontSize: '1rem',
};

const buttonStyle = (loading) => ({
  width: '100%',
  padding: '15px',
  background: loading ? '#555' : 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
  color: 'white',
  border: 'none',
  borderRadius: '8px',
  fontSize: '1.1rem',
  fontWeight: 600,
  cursor: loading ? 'not-allowed' : 'pointer',
  opacity: loading ? 0.8 : 1,
});

export default Landing;