import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import authService from '../../services/auth';
import { setToken } from '../../utils/auth';
import RegisterForm from './RegisterForm';
import ResetPasswordForm from './ResetPasswordForm';
import './index.css';

const LoginPage = () => {
  const [loading, setLoading] = useState(false);
  const [currentForm, setCurrentForm] = useState('login'); // 'login', 'register', 'reset'
  const navigate = useNavigate();
  const location = useLocation();

  // 检查是否已登录
  useEffect(() => {
    if (authService.isAuthenticated()) {
      const returnPath = sessionStorage.getItem('returnPath');
      if (returnPath) {
        sessionStorage.removeItem('returnPath');
        navigate(returnPath);
      } else {
        navigate('/dashboard');
      }
    }
  }, [navigate]);

  // 处理登录
  const handleLogin = async (values) => {
    try {
      setLoading(true);
      const response = await authService.login(values);

      // 登录成功
      if (response?.token && response?.user) {
        // 保存token
        setToken(response.token);
        message.success('登录成功');
        
        // 获取返回路径
        const returnPath = sessionStorage.getItem('returnPath');
        sessionStorage.removeItem('returnPath');
        
        // 导航到返回路径或默认页面
        navigate(returnPath || '/dashboard', { replace: true });
      } else {
        message.error('登录失败，请检查用户名和密码');
      }
    } catch (error) {
      console.error('登录失败:', error);
      message.error(error.message || '登录失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 处理注册或重置密码成功
  const handleSuccess = () => {
    setCurrentForm('login');
  };

  // 渲染登录表单
  const renderLoginForm = () => (
    <Card title="人员管理系统" className="login-card">
      <Form
        name="login"
        onFinish={handleLogin}
        size="large"
        autoComplete="off"
        initialValues={{ remember: true }}
      >
        <Form.Item
          name="username"
          rules={[
            { required: true, message: '请输入用户名' },
            { min: 3, message: '用户名至少3个字符' }
          ]}
        >
          <Input
            prefix={<UserOutlined className="site-form-item-icon" />}
            placeholder="请输入用户名"
            autoComplete="username"
            autoFocus
          />
        </Form.Item>

        <Form.Item
          name="password"
          rules={[
            { required: true, message: '请输入密码' },
            { min: 6, message: '密码至少6个字符' }
          ]}
        >
          <Input.Password
            prefix={<LockOutlined className="site-form-item-icon" />}
            placeholder="请输入密码"
            autoComplete="current-password"
          />
        </Form.Item>

        <Form.Item>
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            block
            size="large"
          >
            {loading ? '登录中...' : '登录'}
          </Button>
        </Form.Item>

        <Form.Item style={{ marginBottom: 0 }}>
          <Button
            type="link"
            onClick={() => setCurrentForm('register')}
            style={{ float: 'left' }}
          >
            注册新用户
          </Button>
          <Button
            type="link"
            onClick={() => setCurrentForm('reset')}
            style={{ float: 'right' }}
          >
            忘记密码？
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );

  // 根据当前表单状态渲染对应的组件
  const renderForm = () => {
    switch (currentForm) {
      case 'register':
        return (
          <RegisterForm
            onSuccess={handleSuccess}
            onCancel={() => setCurrentForm('login')}
          />
        );
      case 'reset':
        return (
          <ResetPasswordForm
            onSuccess={handleSuccess}
            onCancel={() => setCurrentForm('login')}
          />
        );
      default:
        return renderLoginForm();
    }
  };

  return (
    <div className="login-container">
      {renderForm()}
    </div>
  );
};

export default LoginPage;
