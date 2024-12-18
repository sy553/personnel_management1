// Leave.js - 请假申请页面

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
import { getLeaveRecords, createLeaveRequest, approveLeaveRequest } from '../../services/leave';
import { getUserInfo, hasEmployeeInfo } from '../../utils/auth';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { TextArea } = Input;

/**
 * 请假状态对应的标签颜色
 */
const statusColors = {
  pending: 'gold',
  approved: 'green',
  rejected: 'red'
};

/**
 * 请假状态对应的中文描述
 */
const statusText = {
  pending: '待审批',
  approved: '已批准',
  rejected: '已拒绝'
};

/**
 * 请假类型对应的中文描述
 */
const leaveTypeText = {
  sick: '病假',
  personal: '事假',
  annual: '年假'
};

/**
 * 请假管理页面组件
 */
const LeavePage = () => {
  // 路由钩子
  const navigate = useNavigate();

  // 状态定义
  const [loading, setLoading] = useState(false);
  const [records, setRecords] = useState([]);
  const [visible, setVisible] = useState(false);
  const [form] = Form.useForm();
  const [filters, setFilters] = useState({
    start_date: undefined,
    end_date: undefined,
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

  // 获取请假记录
  useEffect(() => {
    fetchRecords();
  }, [filters]);

  // 获取请假记录列表
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
      
      const response = await getLeaveRecords(params);
      if (response && response.code === 200) {
        setRecords(response.data || []);
      } else {
        message.error('获取请假记录失败');
      }
    } catch (error) {
      console.error('获取请假记录失败:', error);
      message.error(error.message || '获取请假记录失败');
    } finally {
      setLoading(false);
    }
  };

  // 提交请假申请
  const handleSubmit = async (values) => {
    try {
      const data = {
        leave_type: values.leave_type,
        start_date: values.date[0].format('YYYY-MM-DD'),
        end_date: values.date[1].format('YYYY-MM-DD'),
        reason: values.reason
      };

      const response = await createLeaveRequest(data);
      if (response && response.code === 200) {
        message.success('提交请假申请成功');
        setVisible(false);
        form.resetFields();
        fetchRecords();
      } else {
        message.error(response?.msg || '提交请假申请失败');
      }
    } catch (error) {
      console.error('提交请假申请失败:', error);
      message.error('提交请假申请失败');
    }
  };

  // 审批请假申请
  const handleApprove = async (record, status) => {
    try {
      const response = await approveLeaveRequest(record.id, { status });
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
      title: '请假类型',
      dataIndex: 'leave_type',
      key: 'leave_type',
      render: (text) => leaveTypeText[text] || text,
    },
    {
      title: '开始日期',
      dataIndex: 'start_date',
      key: 'start_date',
      render: (text) => dayjs(text).format('YYYY-MM-DD'),
    },
    {
      title: '结束日期',
      dataIndex: 'end_date',
      key: 'end_date',
      render: (text) => dayjs(text).format('YYYY-MM-DD'),
    },
    {
      title: '请假原因',
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
    <div className="leave-page">
      {/* 筛选条件 */}
      <Card style={{ marginBottom: 16 }}>
        <Form layout="inline">
          <Form.Item label="日期范围">
            <RangePicker
              value={filters.start_date && filters.end_date ? [
                dayjs(filters.start_date),
                dayjs(filters.end_date)
              ] : undefined}
              onChange={(dates) => {
                setFilters({
                  ...filters,
                  start_date: dates ? dates[0].format('YYYY-MM-DD') : undefined,
                  end_date: dates ? dates[1].format('YYYY-MM-DD') : undefined
                });
              }}
            />
          </Form.Item>
          <Form.Item label="状态">
            <Select
              value={filters.status}
              onChange={(value) => setFilters({ ...filters, status: value })}
              allowClear
              style={{ width: 120 }}
            >
              <Option value="pending">待审批</Option>
              <Option value="approved">已批准</Option>
              <Option value="rejected">已拒绝</Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setVisible(true)}
            >
              请假申请
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {/* 请假记录表格 */}
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

      {/* 请假申请表单弹窗 */}
      <Modal
        title="请假申请"
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
            name="leave_type"
            label="请假类型"
            rules={[{ required: true, message: '请选择请假类型' }]}
          >
            <Select>
              <Option value="sick">病假</Option>
              <Option value="personal">事假</Option>
              <Option value="annual">年假</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="date"
            label="请假日期"
            rules={[{ required: true, message: '请选择请假日期' }]}
          >
            <RangePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="reason"
            label="请假原因"
            rules={[{ required: true, message: '请输入请假原因' }]}
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

export default LeavePage;
