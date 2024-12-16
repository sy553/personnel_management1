import React, { useState } from 'react';
import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import authService from '../../services/auth';
import './index.css';
import { validatePasswordStrength, getPasswordStrength } from '../../utils/passwordValidator';

const ResetPasswordForm = ({ onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1); // 1: 输入邮箱, 2: 输入验证码和新密码
  const [form] = Form.useForm();
  const [email, setEmail] = useState('');

  // 发送验证码
  const handleSendCode = async () => {
    try {
      const emailValue = form.getFieldValue('email');
      if (!emailValue) {
        message.error('请输入邮箱地址');
        return;
      }

      setLoading(true);
      const response = await authService.sendResetCode({ email: emailValue });
      
      if (response?.code === 200) {
        message.success('验证码已发送到您的邮箱');
        setEmail(emailValue);
        setStep(2);
      } else {
        throw new Error(response?.message || '发送验证码失败');
      }
    } catch (error) {
      console.error('发送验证码失败:', error);
      message.error(error.message || '发送验证码失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 重置密码
  const handleResetPassword = async (values) => {
    try {
      setLoading(true);
      const response = await authService.resetPassword({
        email: email,
        code: values.code,
        new_password: values.newPassword
      });

      // 检查响应格式
      if (response && response.code === 200) {
        message.success(response.message || '密码重置成功，请使用新密码登录');
        onSuccess();
      } else {
        throw new Error(response?.message || '重置密码失败，请重试');
      }
    } catch (error) {
      console.error('重置密码失败:', error);
      message.error(error.message || '重置密码失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 第一步：输入邮箱
  const renderStep1 = () => (
    <Form
      form={form}
      name="resetPassword_step1"
      onFinish={handleSendCode}
    >
      <Form.Item
        name="email"
        rules={[
          { required: true, message: '请输入邮箱' },
          { type: 'email', message: '请输入有效的邮箱地址' }
        ]}
      >
        <Input
          prefix={<MailOutlined />}
          placeholder="请输入注册时使用的邮箱"
          size="large"
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
          发送验证码
        </Button>
      </Form.Item>
    </Form>
  );

  // 第二步：输入验证码和新密码
  const renderStep2 = () => (
    <Form
      form={form}
      name="resetPassword_step2"
      onFinish={handleResetPassword}
    >
      <Form.Item
        name="code"
        rules={[
          { required: true, message: '请输入验证码' },
          { len: 6, message: '验证码为6位数字' }
        ]}
      >
        <Input
          placeholder="请输入验证码"
          size="large"
        />
      </Form.Item>

      <Form.Item
        name="newPassword"
        rules={[
          { required: true, message: '请输入新密码' },
          {
            validator: async (_, value) => {
              if (!value) return Promise.resolve();
              
              const { isValid, errors } = validatePasswordStrength(value);
              if (!isValid) {
                return Promise.reject(new Error(errors.join('\n')));
              }
              return Promise.resolve();
            }
          }
        ]}
      >
        <div>
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="新密码"
            size="large"
            onChange={(e) => {
              const strength = getPasswordStrength(e.target.value);
              form.setFields([{
                name: 'passwordStrength',
                value: strength
              }]);
            }}
          />
          <Form.Item
            name="passwordStrength"
            noStyle
          >
            <div style={{ marginTop: 4 }}>
              <div style={{ display: 'flex', gap: 4 }}>
                {[1, 2, 3, 4].map((level) => (
                  <div
                    key={level}
                    style={{
                      height: 4,
                      flex: 1,
                      backgroundColor: form.getFieldValue('passwordStrength') >= level
                        ? level === 4 ? '#52c41a' : level === 3 ? '#1890ff' : level === 2 ? '#faad14' : '#ff4d4f'
                        : '#f0f0f0'
                    }}
                  />
                ))}
              </div>
              <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                密码强度：
                {form.getFieldValue('passwordStrength') === 4 ? '强' :
                  form.getFieldValue('passwordStrength') === 3 ? '中等' :
                  form.getFieldValue('passwordStrength') === 2 ? '一般' :
                  form.getFieldValue('passwordStrength') === 1 ? '弱' : '非常弱'}
              </div>
            </div>
          </Form.Item>
        </div>
      </Form.Item>

      <Form.Item
        name="confirmPassword"
        rules={[
          { required: true, message: '请确认新密码' },
          ({ getFieldValue }) => ({
            validator(_, value) {
              if (!value || getFieldValue('newPassword') === value) {
                return Promise.resolve();
              }
              return Promise.reject(new Error('两次输入的密码不一致'));
            },
          }),
        ]}
      >
        <Input.Password
          prefix={<LockOutlined />}
          placeholder="确认新密码"
          size="large"
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
          重置密码
        </Button>
      </Form.Item>
    </Form>
  );

  return (
    <Card title="重置密码" className="login-card">
      {step === 1 ? renderStep1() : renderStep2()}
      <Button
        type="link"
        block
        onClick={onCancel}
      >
        返回登录
      </Button>
    </Card>
  );
};

export default ResetPasswordForm;
