import React from 'react';
import { Card, Typography, Space, Divider } from 'antd';
import { useNavigate } from 'react-router-dom';
import RegisterForm from '../../components/auth/RegisterForm';
import './Auth.css';

const { Title, Text } = Typography;

const Register = () => {
  const navigate = useNavigate();

  // 注册成功后的处理
  const handleRegisterSuccess = () => {
    navigate('/login');
  };

  return (
    <div className="auth-container">
      <Card className="auth-card">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2}>人员管理系统</Title>
            <Text type="secondary">创建新账号</Text>
          </div>

          <RegisterForm onSuccess={handleRegisterSuccess} />

          <Divider />

          <div style={{ textAlign: 'center' }}>
            <Space>
              <Text type="secondary">已有账号？</Text>
              <a href="#" onClick={(e) => { e.preventDefault(); navigate('/login'); }}>
                立即登录
              </a>
            </Space>
          </div>
        </Space>
      </Card>
    </div>
  );
};

export default Register;
