// Records.js - 考勤记录页面

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Table, 
  DatePicker, 
  Select, 
  Space, 
  message,
  Row,
  Col,
  Statistic
} from 'antd';
import { 
  ClockCircleOutlined, 
  CheckCircleOutlined, 
  CloseCircleOutlined,
  FieldTimeOutlined
} from '@ant-design/icons';
import { getAttendanceRecords } from '../../services/attendance';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;

/**
 * 考勤记录页面组件
 * 显示员工的考勤记录，支持按日期和状态筛选
 */
const RecordsPage = () => {
  // 状态管理
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    dateRange: [dayjs().startOf('month'), dayjs()],
    status: undefined,
  });
  const [statistics, setStatistics] = useState({
    total: 0,
    normal: 0,
    late: 0,
    early: 0,
    absent: 0,
  });

  // 获取考勤记录
  const fetchRecords = async () => {
    try {
      setLoading(true);
      const params = {
        start_date: filters.dateRange[0].format('YYYY-MM-DD'),
        end_date: filters.dateRange[1].format('YYYY-MM-DD'),
        status: filters.status,
      };

      const response = await getAttendanceRecords(params);
      
      if (response.code === 200) {
        // 添加key属性
        const formattedRecords = response.data.map(record => ({
          ...record,
          key: record.id,
        }));
        setRecords(formattedRecords);

        // 统计各状态数量
        const stats = formattedRecords.reduce((acc, curr) => {
          acc.total++;
          acc[curr.status] = (acc[curr.status] || 0) + 1;
          return acc;
        }, { total: 0, normal: 0, late: 0, early: 0, absent: 0 });

        setStatistics(stats);
      } else {
        message.error(response.msg || '获取考勤记录失败');
      }
    } catch (error) {
      console.error('获取考勤记录失败:', error);
      message.error('获取考勤记录失败');
    } finally {
      setLoading(false);
    }
  };

  // 监听筛选条件变化
  useEffect(() => {
    fetchRecords();
  }, [filters]);

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
      render: (text) => text ? dayjs(text).format('HH:mm:ss') : '-',
    },
    {
      title: '签退时间',
      dataIndex: 'check_out',
      key: 'check_out',
      width: 180,
      render: (text) => text ? dayjs(text).format('HH:mm:ss') : '-',
    },
    {
      title: '考勤状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => {
        const statusMap = {
          normal: { text: '正常', color: '#52c41a' },
          late: { text: '迟到', color: '#faad14' },
          early: { text: '早退', color: '#faad14' },
          absent: { text: '缺勤', color: '#f5222d' },
        };
        const { text, color } = statusMap[status] || { text: '未知', color: '#999' };
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

  return (
    <div className="records-container">
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={4}>
          <Card>
            <Statistic
              title="总记录"
              value={statistics.total}
              prefix={<FieldTimeOutlined />}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card>
            <Statistic
              title="正常考勤"
              value={statistics.normal}
              valueStyle={{ color: '#52c41a' }}
              prefix={<CheckCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card>
            <Statistic
              title="迟到"
              value={statistics.late}
              valueStyle={{ color: '#faad14' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card>
            <Statistic
              title="早退"
              value={statistics.early}
              valueStyle={{ color: '#faad14' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={5}>
          <Card>
            <Statistic
              title="缺勤"
              value={statistics.absent}
              valueStyle={{ color: '#f5222d' }}
              prefix={<CloseCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 筛选区域 */}
      <Card style={{ marginBottom: 24 }}>
        <Space size="large">
          <RangePicker
            value={filters.dateRange}
            onChange={(dates) => setFilters(prev => ({ ...prev, dateRange: dates }))}
            allowClear={false}
          />
          <Select
            style={{ width: 120 }}
            placeholder="考勤状态"
            allowClear
            value={filters.status}
            onChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
          >
            <Select.Option value="normal">正常</Select.Option>
            <Select.Option value="late">迟到</Select.Option>
            <Select.Option value="early">早退</Select.Option>
            <Select.Option value="absent">缺勤</Select.Option>
          </Select>
        </Space>
      </Card>

      {/* 考勤记录表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={records}
          loading={loading}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      <style jsx>{`
        .records-container {
          padding: 24px;
        }
      `}</style>
    </div>
  );
};

export default RecordsPage;
