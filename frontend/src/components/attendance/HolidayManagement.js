// HolidayManagement.js - 节假日管理组件

import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Modal, Form, Input, DatePicker, Select, message, Space, Popconfirm } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { getHolidays, createHoliday, deleteHoliday } from '../../services/attendance';
import dayjs from 'dayjs';

const { Option } = Select;

const HolidayManagement = () => {
  // 状态定义
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [selectedYear, setSelectedYear] = useState(dayjs().year());
  const [selectedMonth, setSelectedMonth] = useState(dayjs().month() + 1);

  // 表格列定义
  const columns = [
    {
      title: '节假日名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      width: 120,
      render: (date) => dayjs(date).format('YYYY-MM-DD'),
    },
    {
      title: '类型',
      dataIndex: 'holiday_type',
      key: 'holiday_type',
      width: 120,
      render: (type) => ({
        holiday: '节假日',
        workday: '调休工作日',
      }[type] || type),
    },
    {
      title: '说明',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Popconfirm
          title="确定要删除这个节假日吗？"
          onConfirm={() => handleDelete(record.id)}
          okText="确定"
          cancelText="取消"
        >
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
          >
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ];

  // 加载节假日数据
  const loadData = async () => {
    try {
      setLoading(true);
      const response = await getHolidays({
        year: selectedYear,
        month: selectedMonth,
      });
      if (response.code === 200) {
        setData(response.data);
      } else {
        message.error(response.msg || '获取节假日列表失败');
      }
    } catch (error) {
      console.error('获取节假日列表失败:', error);
      message.error('获取节假日列表失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载数据
  useEffect(() => {
    loadData();
  }, [selectedYear, selectedMonth]);

  // 处理添加
  const handleAdd = async (values) => {
    try {
      const formattedValues = {
        ...values,
        date: values.date.format('YYYY-MM-DD'),
      };

      const response = await createHoliday(formattedValues);
      if (response.code === 200) {
        message.success('创建节假日成功');
        setModalVisible(false);
        loadData();
      } else {
        message.error(response.msg || '创建节假日失败');
      }
    } catch (error) {
      console.error('创建节假日失败:', error);
      message.error('创建节假日失败，请重试');
    }
  };

  // 处理删除
  const handleDelete = async (id) => {
    try {
      const response = await deleteHoliday(id);
      if (response.code === 200) {
        message.success('删除节假日成功');
        loadData();
      } else {
        message.error(response.msg || '删除节假日失败');
      }
    } catch (error) {
      console.error('删除节假日失败:', error);
      message.error('删除节假日失败，请重试');
    }
  };

  // 生成年份选项
  const yearOptions = [];
  const currentYear = dayjs().year();
  for (let i = currentYear - 5; i <= currentYear + 5; i++) {
    yearOptions.push(
      <Option key={i} value={i}>{i}年</Option>
    );
  }

  // 生成月份选项
  const monthOptions = [];
  for (let i = 1; i <= 12; i++) {
    monthOptions.push(
      <Option key={i} value={i}>{i}月</Option>
    );
  }

  return (
    <Card
      title="节假日管理"
      extra={
        <Space>
          <Select
            value={selectedYear}
            onChange={setSelectedYear}
            style={{ width: 100 }}
          >
            {yearOptions}
          </Select>
          <Select
            value={selectedMonth}
            onChange={setSelectedMonth}
            style={{ width: 80 }}
          >
            {monthOptions}
          </Select>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              form.resetFields();
              setModalVisible(true);
            }}
          >
            添加节假日
          </Button>
        </Space>
      }
    >
      <Table
        columns={columns}
        dataSource={data}
        loading={loading}
        rowKey="id"
        pagination={false}
      />

      <Modal
        title="添加节假日"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleAdd}
        >
          <Form.Item
            name="name"
            label="节假日名称"
            rules={[{ required: true, message: '请输入节假日名称' }]}
          >
            <Input placeholder="请输入节假日名称" />
          </Form.Item>

          <Form.Item
            name="date"
            label="日期"
            rules={[{ required: true, message: '请选择日期' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="holiday_type"
            label="类型"
            rules={[{ required: true, message: '请选择类型' }]}
          >
            <Select placeholder="请选择类型">
              <Option value="holiday">节假日</Option>
              <Option value="workday">调休工作日</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="description"
            label="说明"
          >
            <Input.TextArea rows={4} placeholder="请输入说明" />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default HolidayManagement;
