import React from 'react';
import { Form, Input, Button, message, Card, Space, Typography, Divider } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/auth';
import './RegisterForm.css';

const { Title, Text } = Typography;

const RegisterForm = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = React.useState(false);
  const navigate = useNavigate();

  // 处理注册
  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      await authService.register(values);
      message.success('注册成功！');
      // 注册成功后跳转到登录页
      navigate('/login');
    } catch (error) {
      console.error('注册失败:', error);
      if (error.response) {
        message.error(error.response.data?.msg || '注册失败，请稍后重试');
      } else if (error.request) {
        message.error('无法连接到服务器，请检查网络连接');
      } else {
        message.error('注册请求失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-container">
      <Card className="register-card">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Title level={2} className="register-title">用户注册</Title>
          <Form
            form={form}
            name="register"
            onFinish={handleSubmit}
            autoComplete="off"
            layout="vertical"
            size="large"
          >
            <Form.Item
              name="username"
              rules={[
                { required: true, message: '请输入用户名！' },
                { min: 3, message: '用户名至少3个字符！' }
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="用户名"
              />
            </Form.Item>

            <Form.Item
              name="email"
              rules={[
                { required: true, message: '请输入邮箱！' },
                { type: 'email', message: '请输入有效的邮箱地址！' }
              ]}
            >
              <Input
                prefix={<MailOutlined />}
                placeholder="邮箱"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[
                { required: true, message: '请输入密码！' },
                { min: 6, message: '密码至少6个字符！' }
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="密码"
              />
            </Form.Item>

            <Form.Item
              name="confirm"
              dependencies={['password']}
              rules={[
                { required: true, message: '请确认密码！' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('两次输入的密码不一致！'));
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="确认密码"
              />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" block loading={loading}>
                注册
              </Button>
            </Form.Item>
          </Form>

          <Divider>
            <Text type="secondary">已有账号？</Text>
          </Divider>

          <Button type="default" block onClick={() => navigate('/login')}>
            返回登录
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default RegisterForm;
