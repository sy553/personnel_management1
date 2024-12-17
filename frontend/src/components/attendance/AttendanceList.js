// AttendanceList.js - 考勤记录列表组件

import React, { useState, useEffect } from 'react';
import { Table, Card, DatePicker, Select, Space, message } from 'antd';
import { getAttendanceRecords } from '../../services/attendance';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

const AttendanceList = () => {
  // 状态定义
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [filters, setFilters] = useState({
    status: undefined,
    dateRange: [],
  });

  // 表格列定义
  const columns = [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      width: 120,
    },
    {
      title: '员工姓名',
      dataIndex: 'employee_name',
      key: 'employee_name',
      width: 120,
    },
    {
      title: '签到时间',
      dataIndex: 'check_in',
      key: 'check_in',
      width: 180,
    },
    {
      title: '签退时间',
      dataIndex: 'check_out',
      key: 'check_out',
      width: 180,
    },
    {
      title: '考勤状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => {
        const statusMap = {
          normal: { text: '正常', color: 'green' },
          late: { text: '迟到', color: 'orange' },
          early: { text: '早退', color: 'orange' },
          absent: { text: '缺勤', color: 'red' },
        };
        const { text, color } = statusMap[status] || { text: '未知', color: 'default' };
        return <span style={{ color }}>{text}</span>;
      },
    },
    {
      title: '备注',
      dataIndex: 'remark',
      key: 'remark',
      ellipsis: true,
    },
  ];

  // 加载考勤记录数据
  const loadData = async () => {
    try {
      setLoading(true);
      const params = {
        status: filters.status,
        start_date: filters.dateRange[0]?.format('YYYY-MM-DD'),
        end_date: filters.dateRange[1]?.format('YYYY-MM-DD'),
      };
      const response = await getAttendanceRecords(params);
      if (response.code === 200) {
        setData(response.data);
      } else {
        message.error(response.msg || '获取考勤记录失败');
      }
    } catch (error) {
      console.error('获取考勤记录失败:', error);
      message.error('获取考勤记录失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 监听筛选条件变化
  useEffect(() => {
    loadData();
  }, [filters]);

  // 处理日期范围变化
  const handleDateRangeChange = (dates) => {
    setFilters(prev => ({ ...prev, dateRange: dates }));
  };

  // 处理状态筛选变化
  const handleStatusChange = (value) => {
    setFilters(prev => ({ ...prev, status: value }));
  };

  return (
    <Card>
      <Space style={{ marginBottom: 16 }}>
        <RangePicker
          onChange={handleDateRangeChange}
          value={filters.dateRange}
          allowClear
        />
        <Select
          placeholder="考勤状态"
          style={{ width: 120 }}
          onChange={handleStatusChange}
          value={filters.status}
          allowClear
        >
          <Select.Option value="normal">正常</Select.Option>
          <Select.Option value="late">迟到</Select.Option>
          <Select.Option value="early">早退</Select.Option>
          <Select.Option value="absent">缺勤</Select.Option>
        </Select>
      </Space>

      <Table
        columns={columns}
        dataSource={data}
        loading={loading}
        rowKey="id"
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条记录`,
        }}
      />
    </Card>
  );
};

export default AttendanceList;
