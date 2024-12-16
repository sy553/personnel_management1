import React, { useState } from 'react';
import { Form, Input, Button, message, Card, Space, Typography, Divider } from 'antd';
import { MailOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import authService from '../../services/auth';
import './ForgotPasswordForm.css';

const { Title, Text } = Typography;

const ForgotPasswordForm = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      await authService.resetPassword(values);
      message.success('重置密码邮件已发送，请查收邮箱');
      navigate('/login');
    } catch (error) {
      console.error('重置密码失败:', error);
      if (error.response) {
        message.error(error.response.data?.msg || '重置密码失败，请稍后重试');
      } else if (error.request) {
        message.error('无法连接到服务器，请检查网络连接');
      } else {
        message.error('重置密码请求失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forgot-password-container">
      <Card className="forgot-password-card">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Title level={2} className="forgot-password-title">重置密码</Title>
          <Form
            form={form}
            name="forgot-password"
            onFinish={handleSubmit}
            layout="vertical"
            size="large"
          >
            <Form.Item
              name="email"
              rules={[
                { required: true, message: '请输入邮箱！' },
                { type: 'email', message: '请输入有效的邮箱地址！' }
              ]}
            >
              <Input
                prefix={<MailOutlined />}
                placeholder="请输入注册时使用的邮箱"
              />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" block loading={loading}>
                发送重置密码邮件
              </Button>
            </Form.Item>
          </Form>

          <Divider>
            <Text type="secondary">或者</Text>
          </Divider>

          <Button type="default" block onClick={() => navigate('/login')}>
            返回登录
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default ForgotPasswordForm;
