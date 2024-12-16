import React, { useState } from 'react';
import { Form, Input, Button, message, Card, Space, Typography, Divider, Row, Col } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../../services/auth';
import './LoginForm.css';

const { Title, Text } = Typography;

const LoginForm = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const response = await authService.login(values);
      if (response.code === 200) {
        message.success('登录成功');
        // 获取之前保存的路径（如果有）
        const redirectPath = localStorage.getItem('redirectPath');
        // 清除保存的路径
        localStorage.removeItem('redirectPath');
        // 跳转到之前的页面或默认页面
        navigate(redirectPath || '/dashboard');
      } else {
        message.error(response.msg || '登录失败');
      }
    } catch (error) {
      console.error('登录错误:', error);
      if (error.response) {
        message.error(error.response.data?.msg || '登录失败，请稍后重试');
      } else if (error.request) {
        message.error('无法连接到服务器，请检查网络连接');
      } else {
        message.error('登录请求失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <Card className="login-card">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Title level={2} className="login-title">人员管理系统</Title>
          <Form
            name="login"
            onFinish={handleSubmit}
            size="large"
            layout="vertical"
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: '请输入用户名' }]}
            >
              <Input 
                prefix={<UserOutlined />}
                placeholder="用户名"
              />
            </Form.Item>
            
            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="密码"
              />
            </Form.Item>

            <Form.Item>
              <Row justify="end">
                <Col>
                  <Link to="/forgot-password" className="login-form-link">
                    忘记密码？
                  </Link>
                </Col>
              </Row>
            </Form.Item>
            
            <Form.Item>
              <Button 
                type="primary" 
                htmlType="submit" 
                block 
                loading={loading}
              >
                登录
              </Button>
            </Form.Item>
          </Form>

          <Divider>
            <Text type="secondary">还没有账号？</Text>
          </Divider>

          <Button type="default" block onClick={() => navigate('/register')}>
            立即注册
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default LoginForm;
