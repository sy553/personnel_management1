import React from 'react';
import { Card, Typography, Space, Divider } from 'antd';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../../components/auth/LoginForm';
import './Auth.css';

const { Title, Text } = Typography;

const Login = () => {
  const navigate = useNavigate();

  // 登录成功后的处理
  const handleLoginSuccess = () => {
    navigate('/');  // 导航到根路径，会自动匹配到默认的Dashboard页面
  };

  return (
    <div className="auth-container">
      <Card className="auth-card">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2}>人员管理系统</Title>
            <Text type="secondary">请登录您的账号</Text>
          </div>

          <LoginForm onSuccess={handleLoginSuccess} />

          <Divider />

          <div style={{ textAlign: 'center' }}>
            <Space>
              <Text type="secondary">还没有账号？</Text>
              <a href="#" onClick={(e) => { e.preventDefault(); navigate('/register'); }}>
                立即注册
              </a>
            </Space>
            <br />
            <a href="#" onClick={(e) => { e.preventDefault(); navigate('/reset-password'); }}>
              忘记密码？
            </a>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default Login;
