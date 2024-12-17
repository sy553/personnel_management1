// Statistics.js - 考勤统计页面

import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  DatePicker, 
  Table, 
  Select,
  Statistic,
  message,
  Spin,
  Button
} from 'antd';
import {
  UserOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  DownloadOutlined
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import { getAttendanceStatistics, exportStatistics } from '../../services/statistics';
import { getDepartments } from '../../services/department';
import dayjs from 'dayjs';

const { RangePicker } = DatePicker;
const { Option } = Select;

/**
 * 考勤统计页面组件
 * 显示考勤数据的统计信息，包括出勤率、迟到早退、缺勤等
 */
const StatisticsPage = () => {
  // 路由钩子
  const navigate = useNavigate();
  const location = useLocation();

  // 状态定义
  const [loading, setLoading] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [dateRange, setDateRange] = useState([dayjs().startOf('month'), dayjs()]);
  const [departmentId, setDepartmentId] = useState(undefined);
  const [departments, setDepartments] = useState([]);
  const [statistics, setStatistics] = useState({
    totalDays: 0,
    totalEmployees: 0,
    attendanceRate: 0,
    lateCount: 0,
    earlyCount: 0,
    absentCount: 0,
    details: []
  });

  // 检查认证状态
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      message.error('请先登录');
      navigate('/login', { state: { from: location } });
    }
  }, [navigate, location]);

  // 获取部门列表
  useEffect(() => {
    fetchDepartments();
  }, []);

  // 获取统计数据
  useEffect(() => {
    if (dateRange?.[0] && dateRange?.[1]) {
      fetchStatistics();
    }
  }, [dateRange, departmentId]);

  // 获取部门列表
  const fetchDepartments = async () => {
    try {
      const response = await getDepartments();
      if (response && response.code === 200) {
        setDepartments(response.data || []);
      } else {
        message.error(response?.msg || '获取部门列表失败');
      }
    } catch (error) {
      console.error('获取部门列表失败:', error);
      message.error('获取部门列表失败');
    }
  };

  // 获取统计数据
  const fetchStatistics = async () => {
    try {
      setLoading(true);
      const params = {
        start_date: dateRange[0].format('YYYY-MM-DD'),
        end_date: dateRange[1].format('YYYY-MM-DD'),
        department_id: departmentId
      };

      const response = await getAttendanceStatistics(params);
      
      if (response && response.code === 200) {
        setStatistics(response.data || {
          totalDays: 0,
          totalEmployees: 0,
          attendanceRate: 0,
          lateCount: 0,
          earlyCount: 0,
          absentCount: 0,
          details: []
        });
      } else {
        message.error(response?.msg || '获取统计数据失败');
      }
    } catch (error) {
      console.error('获取统计数据失败:', error);
      message.error('获取统计数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 导出统计数据
  const handleExport = async () => {
    try {
      setExportLoading(true);
      const params = {
        start_date: dateRange[0].format('YYYY-MM-DD'),
        end_date: dateRange[1].format('YYYY-MM-DD'),
        department_id: departmentId
      };

      const response = await exportStatistics(params);
      
      // 创建下载链接
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `考勤统计_${params.start_date}_${params.end_date}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      message.success('导出成功');
    } catch (error) {
      console.error('导出失败:', error);
      message.error('导出失败');
    } finally {
      setExportLoading(false);
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '部门',
      dataIndex: 'department_name',
      key: 'department',
    },
    {
      title: '员工姓名',
      dataIndex: 'employee_name',
      key: 'name',
    },
    {
      title: '应出勤天数',
      dataIndex: 'total_days',
      key: 'totalDays',
    },
    {
      title: '实际出勤天数',
      dataIndex: 'attended_days',
      key: 'actualDays',
    },
    {
      title: '出勤率',
      dataIndex: 'attendance_rate',
      key: 'attendanceRate',
      render: (text) => `${(text * 100).toFixed(2)}%`,
    },
    {
      title: '迟到次数',
      dataIndex: 'late_count',
      key: 'lateCount',
    },
    {
      title: '早退次数',
      dataIndex: 'early_count',
      key: 'earlyCount',
    },
    {
      title: '缺勤次数',
      dataIndex: 'absent_count',
      key: 'absentCount',
    },
  ];

  return (
    <Spin spinning={loading}>
      <div className="attendance-statistics">
        {/* 筛选条件 */}
        <Card style={{ marginBottom: 16 }}>
          <Row gutter={16} align="middle">
            <Col>
              <RangePicker
                value={dateRange}
                onChange={setDateRange}
                style={{ width: 280 }}
              />
            </Col>
            <Col>
              <Select
                placeholder="选择部门"
                value={departmentId}
                onChange={setDepartmentId}
                allowClear
                style={{ width: 200 }}
              >
                {departments.map(dept => (
                  <Option key={dept.id} value={dept.id}>{dept.name}</Option>
                ))}
              </Select>
            </Col>
            <Col>
              <Button
                type="primary"
                icon={<DownloadOutlined />}
                loading={exportLoading}
                onClick={handleExport}
              >
                导出统计
              </Button>
            </Col>
          </Row>
        </Card>

        {/* 统计概览 */}
        <Card style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col span={6}>
              <Statistic
                title="总员工数"
                value={statistics.totalEmployees}
                prefix={<UserOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="出勤率"
                value={statistics.attendanceRate * 100}
                precision={2}
                suffix="%"
                prefix={<CheckCircleOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="迟到/早退"
                value={statistics.lateCount + statistics.earlyCount}
                prefix={<WarningOutlined />}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="缺勤"
                value={statistics.absentCount}
                prefix={<CloseCircleOutlined />}
              />
            </Col>
          </Row>
        </Card>

        {/* 详细数据表格 */}
        <Card>
          <Table
            columns={columns}
            dataSource={statistics.details}
            rowKey={(record) => record.id}
            pagination={{
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: total => `共 ${total} 条记录`,
            }}
          />
        </Card>
      </div>
    </Spin>
  );
};

export default StatisticsPage;
