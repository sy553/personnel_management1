import React, { useState } from 'react';
import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import authService from '../../services/auth';
import { validatePasswordStrength, getPasswordStrength } from '../../utils/passwordValidator';
import './index.css';

/**
 * 注册表单组件
 * @param {Function} onSuccess - 注册成功的回调函数
 * @param {Function} onCancel - 取消注册的回调函数
 */
const RegisterForm = ({ onSuccess, onCancel }) => {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  /**
   * 处理表单提交
   * @param {Object} values - 表单值
   */
  const onFinish = async (values) => {
    try {
      setLoading(true);
      // 确认两次密码输入一致
      if (values.password !== values.confirmPassword) {
        message.error('两次输入的密码不一致');
        return;
      }

      // 调用注册接口
      const response = await authService.register({
        username: values.username,
        password: values.password,
        email: values.email
      });

      // 注册成功处理（兼容200和201状态码）
      if (response?.code === 200 || response?.code === undefined) {
        message.success('注册成功，请登录');
        form.resetFields(); // 清空表单
        onSuccess(); // 调用成功回调
      } else {
        // 注册失败处理
        throw new Error(response?.message || '注册失败');
      }
    } catch (error) {
      console.error('注册失败:', error);
      // 显示具体的错误信息
      message.error(error.response?.data?.message || error.message || '注册失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="注册新用户" className="login-card">
      <Form
        form={form}
        name="register"
        onFinish={onFinish}
        size="large"
        autoComplete="off"
      >
        <Form.Item
          name="username"
          rules={[
            { required: true, message: '请输入用户名' },
            { min: 3, message: '用户名至少3个字符' },
            { max: 20, message: '用户名最多20个字符' }
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
            { required: true, message: '请输入邮箱' },
            { type: 'email', message: '请输入有效的邮箱地址' }
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
            { required: true, message: '请输入密码' },
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
              placeholder="密码"
              onChange={(e) => {
                const strength = getPasswordStrength(e.target.value);
                // 可以在这里添加密码强度提示UI
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
            { required: true, message: '请确认密码' },
            ({ getFieldValue }) => ({
              validator(_, value) {
                if (!value || getFieldValue('password') === value) {
                  return Promise.resolve();
                }
                return Promise.reject(new Error('两次输入的密码不一致'));
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
          <Button
            type="primary"
            htmlType="submit"
            loading={loading}
            block
            size="large"
          >
            注册
          </Button>
        </Form.Item>
        <Form.Item>
          <Button
            type="link"
            block
            onClick={onCancel}
          >
            返回登录
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default RegisterForm;
