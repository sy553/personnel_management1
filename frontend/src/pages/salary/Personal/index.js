import React, { useState, useEffect } from 'react';
import { Card, Table, Form, DatePicker, Row, Col, Statistic, Alert, Spin, message } from 'antd';
import axios from 'axios';
import moment from 'moment';

/**
 * 个人工资查询页面
 * 用于员工查询自己的工资记录
 */
const PersonalSalary = () => {
  // 状态定义
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [error, setError] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);
  const [statistics, setStatistics] = useState({});

  // 获取当前登录用户信息
  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          setError('请先登录');
          return;
        }

        const response = await axios.get('/api/users/current', {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (response.data.code === 200) {
          setCurrentUser(response.data.data);
          // 获取当前年份的工资记录
          fetchPersonalSalary(moment().year());
        } else {
          setError(response.data.message || '获取用户信息失败');
        }
      } catch (error) {
        console.error('获取当前用户信息失败:', error);
        setError('获取用户信息失败，请重新登录');
      }
    };

    fetchCurrentUser();
  }, []);

  // 获取个人工资记录
  const fetchPersonalSalary = async (year, month) => {
    if (!currentUser?.employee_id) {
      message.error('未找到员工信息');
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/salary/personal', {
        headers: { Authorization: `Bearer ${token}` },
        params: {
          employee_id: currentUser.employee_id,
          year,
          month: month ? month.month() + 1 : undefined
        }
      });

      if (response.data.code === 200) {
        setData(response.data.data.records || []);
        setStatistics(response.data.data.statistics || {});
      } else {
        setError(response.data.message || '获取工资记录失败');
      }
    } catch (error) {
      console.error('获取个人工资记录失败:', error);
      setError(error.response?.data?.message || '获取工资记录失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '年份',
      dataIndex: 'year',
      key: 'year',
      width: 80,
    },
    {
      title: '月份',
      dataIndex: 'month',
      key: 'month',
      width: 80,
    },
    {
      title: '基本工资',
      dataIndex: 'basic_salary',
      key: 'basic_salary',
      width: 120,
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '补贴',
      dataIndex: 'allowances',
      key: 'allowances',
      width: 120,
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '加班费',
      dataIndex: 'overtime_pay',
      key: 'overtime_pay',
      width: 120,
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '奖金',
      dataIndex: 'bonus',
      key: 'bonus',
      width: 120,
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '个税',
      dataIndex: 'tax',
      key: 'tax',
      width: 120,
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '实发工资',
      dataIndex: 'net_salary',
      key: 'net_salary',
      width: 120,
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '发放状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => {
        const statusMap = {
          pending: '待发放',
          paid: '已发放',
          cancelled: '已取消'
        };
        return statusMap[status] || status;
      }
    }
  ];

  // 处理年份选择
  const handleYearChange = (date) => {
    if (date) {
      fetchPersonalSalary(date.year());
    }
  };

  // 处理月份选择
  const handleMonthChange = (date) => {
    if (date) {
      fetchPersonalSalary(date.year(), date);
    }
  };

  return (
    <Spin spinning={loading}>
      <Card title="个人工资查询">
        {error ? (
          <Alert message={error} type="error" showIcon style={{ marginBottom: 16 }} />
        ) : (
          <>
            <Form layout="inline" style={{ marginBottom: 16 }}>
              <Form.Item label="选择年份">
                <DatePicker
                  picker="year"
                  onChange={handleYearChange}
                  defaultValue={moment()}
                />
              </Form.Item>
              <Form.Item label="选择月份">
                <DatePicker
                  picker="month"
                  onChange={handleMonthChange}
                  defaultValue={moment()}
                />
              </Form.Item>
            </Form>

            <Row gutter={16} style={{ marginBottom: 16 }}>
              <Col span={6}>
                <Statistic
                  title="本年累计收入"
                  value={statistics.yearly_total || 0}
                  precision={2}
                  prefix="¥"
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="平均月收入"
                  value={statistics.monthly_average || 0}
                  precision={2}
                  prefix="¥"
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="最高月收入"
                  value={statistics.highest_monthly || 0}
                  precision={2}
                  prefix="¥"
                />
              </Col>
              <Col span={6}>
                <Statistic
                  title="最低月收入"
                  value={statistics.lowest_monthly || 0}
                  precision={2}
                  prefix="¥"
                />
              </Col>
            </Row>

            <Table
              columns={columns}
              dataSource={data}
              rowKey={(record) => `${record.year}-${record.month}`}
              scroll={{ x: 1200 }}
              pagination={{
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total) => `共 ${total} 条记录`,
              }}
            />
          </>
        )}
      </Card>
    </Spin>
  );
};

export default PersonalSalary;
