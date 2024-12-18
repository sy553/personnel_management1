import React from 'react';
import { Form, Input, TimePicker, InputNumber, Switch, Select, DatePicker, Space } from 'antd';
import dayjs from 'dayjs';

/**
 * 考勤规则表单组件
 * @param {Object} props - 组件属性
 * @param {Object} props.form - 表单实例
 * @param {Object} props.initialValues - 初始值
 * @param {boolean} props.loading - 加载状态
 */
const RuleForm = ({ form, initialValues, loading }) => {
  // 规则类型选项
  const ruleTypeOptions = [
    { label: '常规规则', value: 'regular' },
    { label: '特殊规则', value: 'special' },
    { label: '临时规则', value: 'temporary' }
  ];

  return (
    <Form
      form={form}
      layout="vertical"
      initialValues={{
        priority: 0,
        rule_type: 'regular',
        late_threshold: 15,
        early_leave_threshold: 15,
        overtime_minimum: 60,
        flexible_time: 30,
        overtime_rate: 1.5,
        weekend_overtime_rate: 2.0,
        holiday_overtime_rate: 3.0,
        ...initialValues,
        work_start_time: initialValues?.work_start_time ? dayjs(initialValues.work_start_time, 'HH:mm') : null,
        work_end_time: initialValues?.work_end_time ? dayjs(initialValues.work_end_time, 'HH:mm') : null,
        break_start_time: initialValues?.break_start_time ? dayjs(initialValues.break_start_time, 'HH:mm') : null,
        break_end_time: initialValues?.break_end_time ? dayjs(initialValues.break_end_time, 'HH:mm') : null,
        effective_start_date: initialValues?.effective_start_date ? dayjs(initialValues.effective_start_date) : dayjs(),
        effective_end_date: initialValues?.effective_end_date ? dayjs(initialValues.effective_end_date) : null
      }}
    >
      <Form.Item
        name="name"
        label="规则名称"
        rules={[{ required: true, message: '请输入规则名称' }]}
      >
        <Input placeholder="请输入规则名称" disabled={loading} />
      </Form.Item>

      <Space style={{ width: '100%' }} direction="vertical" size="middle">
        <Form.Item
          name="rule_type"
          label="规则类型"
          rules={[{ required: true, message: '请选择规则类型' }]}
        >
          <Select options={ruleTypeOptions} disabled={loading} />
        </Form.Item>

        <Form.Item
          name="priority"
          label="优先级"
          tooltip="数字越大优先级越高"
          rules={[{ required: true, message: '请设置优先级' }]}
        >
          <InputNumber min={0} style={{ width: '100%' }} disabled={loading} />
        </Form.Item>

        <Form.Item
          name="effective_start_date"
          label="生效开始日期"
          rules={[{ required: true, message: '请选择生效开始日期' }]}
        >
          <DatePicker style={{ width: '100%' }} disabled={loading} />
        </Form.Item>

        <Form.Item
          name="effective_end_date"
          label="生效结束日期"
          tooltip="不设置则永久有效"
        >
          <DatePicker style={{ width: '100%' }} disabled={loading} />
        </Form.Item>
      </Space>

      <Form.Item label="工作时间">
        <Space style={{ width: '100%' }} direction="vertical">
          <Form.Item
            name="work_start_time"
            rules={[{ required: true, message: '请选择上班时间' }]}
          >
            <TimePicker
              format="HH:mm"
              placeholder="上班时间"
              style={{ width: '100%' }}
              disabled={loading}
            />
          </Form.Item>

          <Form.Item
            name="work_end_time"
            rules={[{ required: true, message: '请选择下班时间' }]}
          >
            <TimePicker
              format="HH:mm"
              placeholder="下班时间"
              style={{ width: '100%' }}
              disabled={loading}
            />
          </Form.Item>
        </Space>
      </Form.Item>

      <Form.Item label="休息时间">
        <Space style={{ width: '100%' }} direction="vertical">
          <Form.Item name="break_start_time">
            <TimePicker
              format="HH:mm"
              placeholder="休息开始时间"
              style={{ width: '100%' }}
              disabled={loading}
            />
          </Form.Item>

          <Form.Item name="break_end_time">
            <TimePicker
              format="HH:mm"
              placeholder="休息结束时间"
              style={{ width: '100%' }}
              disabled={loading}
            />
          </Form.Item>
        </Space>
      </Form.Item>

      <Form.Item label="考勤设置">
        <Space style={{ width: '100%' }} direction="vertical">
          <Form.Item
            name="late_threshold"
            label="迟到阈值(分钟)"
            rules={[{ required: true, message: '请设置迟到阈值' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} disabled={loading} />
          </Form.Item>

          <Form.Item
            name="early_leave_threshold"
            label="早退阈值(分钟)"
            rules={[{ required: true, message: '请设置早退阈值' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} disabled={loading} />
          </Form.Item>

          <Form.Item
            name="overtime_minimum"
            label="最小加班时长(分钟)"
            rules={[{ required: true, message: '请设置最小加班时长' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} disabled={loading} />
          </Form.Item>

          <Form.Item
            name="flexible_time"
            label="弹性工作时间(分钟)"
            rules={[{ required: true, message: '请设置弹性工作时间' }]}
          >
            <InputNumber min={0} style={{ width: '100%' }} disabled={loading} />
          </Form.Item>
        </Space>
      </Form.Item>

      <Form.Item label="加班费率设置">
        <Space style={{ width: '100%' }} direction="vertical">
          <Form.Item
            name="overtime_rate"
            label="普通加班费率"
            rules={[{ required: true, message: '请设置加班费率' }]}
          >
            <InputNumber min={1} step={0.1} style={{ width: '100%' }} disabled={loading} />
          </Form.Item>

          <Form.Item
            name="weekend_overtime_rate"
            label="周末加班费率"
            rules={[{ required: true, message: '请设置周末加班费率' }]}
          >
            <InputNumber min={1} step={0.1} style={{ width: '100%' }} disabled={loading} />
          </Form.Item>

          <Form.Item
            name="holiday_overtime_rate"
            label="节假日加班费率"
            rules={[{ required: true, message: '请设置节假日加班费率' }]}
          >
            <InputNumber min={1} step={0.1} style={{ width: '100%' }} disabled={loading} />
          </Form.Item>
        </Space>
      </Form.Item>

      <Form.Item
        name="is_default"
        label="是否默认规则"
        valuePropName="checked"
      >
        <Switch disabled={loading} />
      </Form.Item>

      <Form.Item
        name="description"
        label="规则说明"
      >
        <Input.TextArea
          rows={4}
          placeholder="请输入规则说明"
          disabled={loading}
        />
      </Form.Item>
    </Form>
  );
};

export default RuleForm;
