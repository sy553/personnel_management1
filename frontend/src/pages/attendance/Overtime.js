// Overtime.js - 加班申请页面

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Table,
  Button,
  Form,
  Input,
  DatePicker,
  Select,
  message,
  Modal,
  Space,
  Tag
} from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { getOvertimeRecords, createOvertimeRequest, approveOvertimeRequest } from '../../services/overtime';
import { getUserInfo } from '../../utils/auth';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { TextArea } = Input;

/**
 * 加班状态对应的标签颜色
 */
const statusColors = {
  pending: 'gold',
  approved: 'green',
  rejected: 'red'
};

/**
 * 加班状态对应的中文描述
 */
const statusText = {
  pending: '待审批',
  approved: '已批准',
  rejected: '已拒绝'
};

/**
 * 加班管理页面组件
 */
const OvertimePage = () => {
  // 路由钩子
  const navigate = useNavigate();

  // 状态定义
  const [loading, setLoading] = useState(false);
  const [records, setRecords] = useState([]);
  const [visible, setVisible] = useState(false);
  const [form] = Form.useForm();
  const [filters, setFilters] = useState({
    start_time: undefined,
    end_time: undefined,
    status: undefined
  });

  // 检查认证状态
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      message.error('请先登录');
      navigate('/login');
      return;
    }
  }, [navigate]);

  // 获取加班记录
  useEffect(() => {
    fetchRecords();
  }, [filters]);

  // 获取加班记录列表
  const fetchRecords = async () => {
    try {
      setLoading(true);
      // 获取当前登录用户信息
      const userInfo = getUserInfo();
      if (!userInfo || !userInfo.employeeId) {
        throw new Error('未找到员工信息');
      }
      
      // 构建查询参数
      const params = {
        ...filters,
        employee_id: userInfo.employeeId
      };
      
      const response = await getOvertimeRecords(params);
      if (response && response.code === 200) {
        setRecords(response.data || []);
      } else {
        message.error('获取加班记录失败');
      }
    } catch (error) {
      console.error('获取加班记录失败:', error);
      message.error(error.message || '获取加班记录失败');
    } finally {
      setLoading(false);
    }
  };

  // 提交加班申请
  const handleSubmit = async (values) => {
    try {
      const data = {
        start_time: values.time[0].format('YYYY-MM-DD HH:mm:ss'),
        end_time: values.time[1].format('YYYY-MM-DD HH:mm:ss'),
        reason: values.reason
      };

      const response = await createOvertimeRequest(data);
      if (response && response.code === 200) {
        message.success('提交加班申请成功');
        setVisible(false);
        form.resetFields();
        fetchRecords();
      } else {
        message.error(response?.msg || '提交加班申请失败');
      }
    } catch (error) {
      console.error('提交加班申请失败:', error);
      message.error('提交加班申请失败');
    }
  };

  // 审批加班申请
  const handleApprove = async (record, status) => {
    try {
      const response = await approveOvertimeRequest(record.id, { status });
      if (response && response.code === 200) {
        message.success('审批成功');
        fetchRecords();
      } else {
        message.error(response?.msg || '审批失败');
      }
    } catch (error) {
      console.error('审批失败:', error);
      message.error('审批失败');
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '开始时间',
      dataIndex: 'start_time',
      key: 'start_time',
      render: (text) => dayjs(text).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '结束时间',
      dataIndex: 'end_time',
      key: 'end_time',
      render: (text) => dayjs(text).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '加班时长（小时）',
      key: 'duration',
      render: (_, record) => {
        const start = dayjs(record.start_time);
        const end = dayjs(record.end_time);
        const hours = end.diff(start, 'hour', true).toFixed(1);
        return hours;
      },
    },
    {
      title: '加班原因',
      dataIndex: 'reason',
      key: 'reason',
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (text) => (
        <Tag color={statusColors[text]}>
          {statusText[text] || text}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          {record.status === 'pending' && (
            <>
              <Button
                type="link"
                onClick={() => handleApprove(record, 'approved')}
              >
                批准
              </Button>
              <Button
                type="link"
                danger
                onClick={() => handleApprove(record, 'rejected')}
              >
                拒绝
              </Button>
            </>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div className="overtime-page">
      {/* 筛选条件 */}
      <Card style={{ marginBottom: 16 }}>
        <Form layout="inline">
          <Form.Item label="时间范围">
            <RangePicker
              value={filters.start_time && filters.end_time ? [
                dayjs(filters.start_time),
                dayjs(filters.end_time)
              ] : undefined}
              onChange={(dates) => {
                setFilters({
                  ...filters,
                  start_time: dates ? dates[0].format('YYYY-MM-DD HH:mm:ss') : undefined,
                  end_time: dates ? dates[1].format('YYYY-MM-DD HH:mm:ss') : undefined
                });
              }}
              showTime
            />
          </Form.Item>
          <Form.Item label="状态">
            <Select
              value={filters.status}
              onChange={(value) => setFilters({ ...filters, status: value })}
              allowClear
              style={{ width: 120 }}
            >
              <Select.Option value="pending">待审批</Select.Option>
              <Select.Option value="approved">已批准</Select.Option>
              <Select.Option value="rejected">已拒绝</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setVisible(true)}
            >
              加班申请
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {/* 加班记录表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={records}
          rowKey="id"
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: total => `共 ${total} 条记录`,
          }}
        />
      </Card>

      {/* 加班申请表单弹窗 */}
      <Modal
        title="加班申请"
        open={visible}
        onCancel={() => {
          setVisible(false);
          form.resetFields();
        }}
        footer={null}
        destroyOnClose
      >
        <Form
          form={form}
          onFinish={handleSubmit}
          layout="vertical"
        >
          <Form.Item
            name="time"
            label="加班时间"
            rules={[{ required: true, message: '请选择加班时间' }]}
          >
            <RangePicker
              showTime
              style={{ width: '100%' }}
              format="YYYY-MM-DD HH:mm"
            />
          </Form.Item>
          <Form.Item
            name="reason"
            label="加班原因"
            rules={[{ required: true, message: '请输入加班原因' }]}
          >
            <TextArea rows={4} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              提交申请
            </Button>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default OvertimePage;
