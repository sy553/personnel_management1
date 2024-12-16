import React, { useEffect } from 'react';
import { Form, Input, InputNumber, Select, DatePicker, Button, Row, Col, Divider, Modal, Space } from 'antd';
import moment from 'moment';

const { Option } = Select;

/**
 * 工资记录表单组件
 * @param {Object} props - 组件属性
 * @param {boolean} props.visible - 是否显示模态框
 * @param {Object} props.record - 工资记录数据（编辑时传入）
 * @param {Function} props.onCancel - 取消回调函数
 * @param {Function} props.onSuccess - 成功回调函数
 */
const SalaryRecordForm = ({ visible, record, onCancel, onSuccess }) => {
  const [form] = Form.useForm();

  // 初始化表单数据
  useEffect(() => {
    if (record) {
      form.setFieldsValue({
        ...record,
        payment_date: record.payment_date ? moment(record.payment_date) : null,
      });
    }
  }, [record, form]);

  // 处理表单提交
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      // 格式化日期
      if (values.payment_date) {
        values.payment_date = values.payment_date.format('YYYY-MM-DD');
      }
      
      // 调用成功回调
      await onSuccess(values);
      
      // 重置表单
      form.resetFields();
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  // 处理取消
  const handleCancel = () => {
    form.resetFields();
    onCancel();
  };

  return (
    <Modal
      title="编辑工资记录"
      open={visible}
      onCancel={handleCancel}
      onOk={handleSubmit}
      width={800}
      maskClosable={false}
    >
      <Form
        form={form}
        layout="vertical"
      >
        <Row gutter={24}>
          <Col span={12}>
            <Form.Item
              name="employee_name"
              label="员工姓名"
            >
              <Input disabled />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="payment_status"
              label="发放状态"
            >
              <Select>
                <Option value="pending">待发放</Option>
                <Option value="paid">已发放</Option>
                <Option value="cancelled">已取消</Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={24}>
          <Col span={12}>
            <Form.Item
              name="year"
              label="年份"
            >
              <InputNumber style={{ width: '100%' }} disabled />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="month"
              label="月份"
            >
              <InputNumber style={{ width: '100%' }} min={1} max={12} disabled />
            </Form.Item>
          </Col>
        </Row>

        <Divider>工资组成</Divider>

        <Row gutter={24}>
          <Col span={12}>
            <Form.Item
              name="basic_salary"
              label="基本工资"
              rules={[
                { required: true, message: '请输入基本工资' },
                { type: 'number', min: 0, message: '工资不能为负数' }
              ]}
            >
              <InputNumber
                style={{ width: '100%' }}
                precision={2}
                prefix="¥"
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="allowances"
              label="补贴总额"
              rules={[
                { required: true, message: '请输入补贴总额' },
                { type: 'number', min: 0, message: '补贴不能为负数' }
              ]}
            >
              <InputNumber
                style={{ width: '100%' }}
                precision={2}
                prefix="¥"
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={24}>
          <Col span={12}>
            <Form.Item
              name="overtime_pay"
              label="加班费"
              rules={[
                { type: 'number', min: 0, message: '加班费不能为负数' }
              ]}
            >
              <InputNumber
                style={{ width: '100%' }}
                precision={2}
                prefix="¥"
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="bonus"
              label="奖金"
              rules={[
                { type: 'number', min: 0, message: '奖金不能为负数' }
              ]}
            >
              <InputNumber
                style={{ width: '100%' }}
                precision={2}
                prefix="¥"
              />
            </Form.Item>
          </Col>
        </Row>

        <Divider>扣除项目</Divider>

        <Row gutter={24}>
          <Col span={12}>
            <Form.Item
              name="deductions"
              label="扣除项(请假等)"
              rules={[
                { type: 'number', min: 0, message: '扣除金额不能为负数' }
              ]}
            >
              <InputNumber
                style={{ width: '100%' }}
                precision={2}
                prefix="¥"
              />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="tax"
              label="个人所得税"
            >
              <InputNumber
                style={{ width: '100%' }}
                precision={2}
                prefix="¥"
                disabled
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={24}>
          <Col span={24}>
            <Form.Item
              name="net_salary"
              label="实发工资"
            >
              <InputNumber
                style={{ width: '100%' }}
                precision={2}
                prefix="¥"
                disabled
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={24}>
          <Col span={24}>
            <Form.Item
              name="remark"
              label="备注"
            >
              <Input.TextArea rows={4} />
            </Form.Item>
          </Col>
        </Row>
      </Form>
    </Modal>
  );
};

export default SalaryRecordForm;
