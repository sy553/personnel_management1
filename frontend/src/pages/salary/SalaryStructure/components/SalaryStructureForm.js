import React, { useState, useEffect } from 'react';
import { Form, Input, Select, DatePicker, Button, Space, message } from 'antd';
import { getEmployees } from '../../../../services/employee';
import moment from 'moment';

/**
 * 工资结构表单组件
 * @param {Object} props - 组件属性
 * @param {Object} props.initialValues - 初始值，用于编辑模式
 * @param {Function} props.onSave - 保存回调函数
 * @param {Function} props.onCancel - 取消回调函数
 */
const SalaryStructureForm = ({ initialValues, onSave, onCancel }) => {
  const [form] = Form.useForm();
  const [employees, setEmployees] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // 获取员工列表
  useEffect(() => {
    const fetchEmployees = async () => {
      try {
        setLoading(true);
        const response = await getEmployees();
        if (response.code === 200 && response.data?.items) {
          setEmployees(response.data.items);
        } else {
          message.error('获取员工列表失败：' + (response.msg || '未知错误'));
        }
      } catch (error) {
        console.error('获取员工列表失败:', error);
        message.error('获取员工列表失败：' + (error.message || '未知错误'));
      } finally {
        setLoading(false);
      }
    };

    fetchEmployees();
  }, []);

  // 设置初始值
  useEffect(() => {
    if (initialValues) {
      form.setFieldsValue({
        ...initialValues,
        effective_date: moment(initialValues.effective_date),
      });
    }
  }, [initialValues, form]);

  // 自定义数值验证器
  const validatePositiveNumber = (rule, value) => {
    // 如果值为空且不是必填字段，则通过验证
    if (value === '' || value === undefined || value === null) {
      if (!rule.required) {
        return Promise.resolve();
      }
      return Promise.reject(new Error(rule.message || '请输入数值'));
    }

    // 转换为数字并验证
    const num = parseFloat(value);
    if (isNaN(num)) {
      return Promise.reject(new Error('请输入有效的数字'));
    }
    if (num < (rule.min || 0)) {
      return Promise.reject(new Error(rule.message || '数值不能小于' + (rule.min || 0)));
    }
    return Promise.resolve();
  };

  // 提交表单
  const handleSubmit = async (values) => {
    try {
      setSubmitting(true);
      // 转换表单数据
      const formattedValues = {
        ...values,
        // 将所有数值字段转换为数字类型
        basic_salary: parseFloat(values.basic_salary || 0),
        housing_allowance: parseFloat(values.housing_allowance || 0),
        transport_allowance: parseFloat(values.transport_allowance || 0),
        meal_allowance: parseFloat(values.meal_allowance || 0),
        // 添加生效日期，如果没有选择则使用当前日期
        effective_date: (values.effective_date || moment()).format('YYYY-MM-DD')
      };

      await onSave(formattedValues);
      message.success('保存成功');
    } catch (error) {
      console.error('保存工资结构失败:', error);
      message.error('保存失败：' + (error.message || '未知错误'));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
      initialValues={{
        housing_allowance: 0,
        transport_allowance: 0,
        meal_allowance: 0,
        effective_date: moment(),
      }}
    >
      <Form.Item
        name="name"
        label="薪资结构名称"
        rules={[{ required: true, message: '请输入薪资结构名称' }]}
      >
        <Input
          placeholder="请输入薪资结构名称"
          disabled={submitting}
        />
      </Form.Item>

      <Form.Item
        name="description"
        label="描述"
      >
        <Input.TextArea
          placeholder="请输入描述信息"
          disabled={submitting}
          rows={4}
        />
      </Form.Item>

      <Form.Item
        name="basic_salary"
        label="基本工资"
        rules={[
          { required: true, message: '请输入基本工资' },
          { validator: validatePositiveNumber, min: 0, message: '工资不能为负数' }
        ]}
      >
        <Input
          type="number"
          step="0.01"
          min="0"
          prefix="¥"
          placeholder="请输入基本工资"
          disabled={submitting}
        />
      </Form.Item>

      <Form.Item
        name="housing_allowance"
        label="住房补贴"
        rules={[{ validator: validatePositiveNumber, min: 0, message: '补贴不能为负数' }]}
      >
        <Input
          type="number"
          step="0.01"
          min="0"
          prefix="¥"
          placeholder="请输入住房补贴"
          disabled={submitting}
        />
      </Form.Item>

      <Form.Item
        name="transport_allowance"
        label="交通补贴"
        rules={[{ validator: validatePositiveNumber, min: 0, message: '补贴不能为负数' }]}
      >
        <Input
          type="number"
          step="0.01"
          min="0"
          prefix="¥"
          placeholder="请输入交通补贴"
          disabled={submitting}
        />
      </Form.Item>

      <Form.Item
        name="meal_allowance"
        label="餐饮补贴"
        rules={[{ validator: validatePositiveNumber, min: 0, message: '补贴不能为负数' }]}
      >
        <Input
          type="number"
          step="0.01"
          min="0"
          prefix="¥"
          placeholder="请输入餐饮补贴"
          disabled={submitting}
        />
      </Form.Item>

      <Form.Item
        name="effective_date"
        label="生效日期"
        rules={[{ required: true, message: '请选择生效日期' }]}
      >
        <DatePicker
          style={{ width: '100%' }}
          placeholder="请选择生效日期"
          disabled={submitting}
        />
      </Form.Item>

      <Form.Item>
        <Space>
          <Button type="primary" htmlType="submit" loading={submitting}>
            保存
          </Button>
          <Button onClick={onCancel} disabled={submitting}>
            取消
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );
};

export default SalaryStructureForm;
