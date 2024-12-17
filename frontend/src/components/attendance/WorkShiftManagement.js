// WorkShiftManagement.js - 班次管理组件

import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Modal, Form, Input, TimePicker, InputNumber, Switch, message, Space, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { getWorkShifts, createWorkShift, updateWorkShift, deleteWorkShift } from '../../services/attendance';
import dayjs from 'dayjs';

const WorkShiftManagement = () => {
  // 状态定义
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingShift, setEditingShift] = useState(null);
  const [form] = Form.useForm();

  // 表格列定义
  const columns = [
    {
      title: '班次名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: '上班时间',
      dataIndex: 'start_time',
      key: 'start_time',
      width: 120,
      render: (time) => time ? dayjs(time, 'HH:mm:ss').format('HH:mm') : '-',
    },
    {
      title: '下班时间',
      dataIndex: 'end_time',
      key: 'end_time',
      width: 120,
      render: (time) => time ? dayjs(time, 'HH:mm:ss').format('HH:mm') : '-',
    },
    {
      title: '弹性时间(分钟)',
      dataIndex: 'flex_time',
      key: 'flex_time',
      width: 120,
    },
    {
      title: '休息时间',
      key: 'break_time',
      width: 180,
      render: (_, record) => {
        if (record.break_start && record.break_end) {
          return `${dayjs(record.break_start, 'HH:mm:ss').format('HH:mm')} - ${dayjs(record.break_end, 'HH:mm:ss').format('HH:mm')}`;
        }
        return '-';
      },
    },
    {
      title: '加班开始时间',
      dataIndex: 'overtime_start',
      key: 'overtime_start',
      width: 120,
      render: (time) => time ? dayjs(time, 'HH:mm:ss').format('HH:mm') : '-',
    },
    {
      title: '是否默认',
      dataIndex: 'is_default',
      key: 'is_default',
      width: 100,
      render: (isDefault) => isDefault ? '是' : '否',
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space>
          <Button
            type="text"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个班次吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              disabled={record.is_default}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 加载班次数据
  const loadData = async () => {
    try {
      setLoading(true);
      const response = await getWorkShifts();
      if (response.code === 200) {
        setData(response.data);
      } else {
        message.error(response.msg || '获取班次列表失败');
      }
    } catch (error) {
      console.error('获取班次列表失败:', error);
      message.error('获取班次列表失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载数据
  useEffect(() => {
    loadData();
  }, []);

  // 处理添加/编辑
  const handleAddOrEdit = async (values) => {
    try {
      const formattedValues = {
        ...values,
        start_time: values.start_time.format('HH:mm:ss'),
        end_time: values.end_time.format('HH:mm:ss'),
        break_start: values.break_start?.format('HH:mm:ss'),
        break_end: values.break_end?.format('HH:mm:ss'),
        overtime_start: values.overtime_start?.format('HH:mm:ss'),
      };

      if (editingShift) {
        const response = await updateWorkShift(editingShift.id, formattedValues);
        if (response.code === 200) {
          message.success('更新班次成功');
          setModalVisible(false);
          loadData();
        } else {
          message.error(response.msg || '更新班次失败');
        }
      } else {
        const response = await createWorkShift(formattedValues);
        if (response.code === 200) {
          message.success('创建班次成功');
          setModalVisible(false);
          loadData();
        } else {
          message.error(response.msg || '创建班次失败');
        }
      }
    } catch (error) {
      console.error('保存班次失败:', error);
      message.error('保存班次失败，请重试');
    }
  };

  // 处理编辑
  const handleEdit = (record) => {
    setEditingShift(record);
    form.setFieldsValue({
      ...record,
      start_time: dayjs(record.start_time, 'HH:mm:ss'),
      end_time: dayjs(record.end_time, 'HH:mm:ss'),
      break_start: record.break_start ? dayjs(record.break_start, 'HH:mm:ss') : null,
      break_end: record.break_end ? dayjs(record.break_end, 'HH:mm:ss') : null,
      overtime_start: record.overtime_start ? dayjs(record.overtime_start, 'HH:mm:ss') : null,
    });
    setModalVisible(true);
  };

  // 处理删除
  const handleDelete = async (id) => {
    try {
      const response = await deleteWorkShift(id);
      if (response.code === 200) {
        message.success('删除班次成功');
        loadData();
      } else {
        message.error(response.msg || '删除班次失败');
      }
    } catch (error) {
      console.error('删除班次失败:', error);
      message.error('删除班次失败，请重试');
    }
  };

  return (
    <Card
      title="班次管理"
      extra={
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setEditingShift(null);
            form.resetFields();
            setModalVisible(true);
          }}
        >
          添加班次
        </Button>
      }
    >
      <Table
        columns={columns}
        dataSource={data}
        loading={loading}
        rowKey="id"
        pagination={false}
        scroll={{ x: 1200 }}
      />

      <Modal
        title={editingShift ? '编辑班次' : '添加班次'}
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleAddOrEdit}
        >
          <Form.Item
            name="name"
            label="班次名称"
            rules={[{ required: true, message: '请输入班次名称' }]}
          >
            <Input placeholder="请输入班次名称" />
          </Form.Item>

          <Form.Item
            name="start_time"
            label="上班时间"
            rules={[{ required: true, message: '请选择上班时间' }]}
          >
            <TimePicker format="HH:mm" placeholder="请选择上班时间" />
          </Form.Item>

          <Form.Item
            name="end_time"
            label="下班时间"
            rules={[{ required: true, message: '请选择下班时间' }]}
          >
            <TimePicker format="HH:mm" placeholder="请选择下班时间" />
          </Form.Item>

          <Form.Item
            name="flex_time"
            label="弹性时间(分钟)"
            initialValue={0}
          >
            <InputNumber min={0} placeholder="请输入弹性时间" />
          </Form.Item>

          <Form.Item
            name="break_start"
            label="休息开始时间"
          >
            <TimePicker format="HH:mm" placeholder="请选择休息开始时间" />
          </Form.Item>

          <Form.Item
            name="break_end"
            label="休息结束时间"
          >
            <TimePicker format="HH:mm" placeholder="请选择休息结束时间" />
          </Form.Item>

          <Form.Item
            name="overtime_start"
            label="加班开始时间"
          >
            <TimePicker format="HH:mm" placeholder="请选择加班开始时间" />
          </Form.Item>

          <Form.Item
            name="description"
            label="班次说明"
          >
            <Input.TextArea rows={4} placeholder="请输入班次说明" />
          </Form.Item>

          <Form.Item
            name="is_default"
            label="是否默认班次"
            valuePropName="checked"
            initialValue={false}
          >
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default WorkShiftManagement;
