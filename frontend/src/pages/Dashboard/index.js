import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Table, message, Progress, Empty, List, Spin } from 'antd';
import { UserOutlined, BankOutlined, ApartmentOutlined } from '@ant-design/icons';
import request from '../../utils/request';
import './index.css';
import '../../styles/common.css';

const Dashboard = () => {
  // 状态管理
  const [employeeStats, setEmployeeStats] = useState(null);
  const [loading, setLoading] = useState(true);

  // 获取仪表盘数据
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await request.get('/api/dashboard/stats');
        console.log('Dashboard stats:', response);
        if (response && response.overview) {
          // 处理recent_employees数据，添加key属性
          if (response.recent_employees) {
            response.recent_employees = response.recent_employees.map((employee, index) => ({
              ...employee,
              key: employee.id || `employee-${index}`  // 使用员工ID或生成唯一key
            }));
          }
          // 处理department_stats数据，添加key属性
          if (response.department_stats) {
            response.department_stats = response.department_stats.map((dept, index) => ({
              ...dept,
              key: dept.id || `dept-${index}`  // 使用部门ID或生成唯一key
            }));
          }
          setEmployeeStats(response);
        } else {
          throw new Error(response.message || '获取统计数据失败');
        }
      } catch (error) {
        console.error('获取统计数据失败:', error);
        message.error(error.message || '获取统计数据失败');
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  // 加载状态显示
  if (loading) {
    return (
      <div className="page-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Spin size="large" />
      </div>
    );
  }

  // 数据为空时的显示
  if (!employeeStats) {
    return (
      <div className="page-container">
        <Empty description="暂无数据" />
      </div>
    );
  }

  return (
    <div className="page-container dashboard">
      <div className="page-header">
        <h1 className="page-title">仪表盘</h1>
      </div>
      
      {/* 统计卡片 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={8}>
          <Card className="stat-card">
            <Statistic
              title="员工总数"
              value={employeeStats.overview.total_employees}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card className="stat-card">
            <Statistic
              title="部门总数"
              value={employeeStats.overview.total_departments}
              prefix={<BankOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card className="stat-card">
            <Statistic
              title="职位总数"
              value={employeeStats.overview.total_positions}
              prefix={<ApartmentOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表和表格 */}
      <Row gutter={[16, 16]} style={{ marginTop: '20px' }}>
        <Col xs={24} md={12}>
          <Card title="部门人员分布" className="chart-card">
            {employeeStats.department_stats.length > 0 ? (
              <List
                className="department-list"
                dataSource={employeeStats.department_stats}
                renderItem={item => (
                  <List.Item key={item.key}>
                    <List.Item.Meta
                      title={item.name}
                      description={
                        <Progress 
                          percent={Math.round((item.count / employeeStats.overview.total_employees) * 100)} 
                          format={percent => `${item.count}人 (${percent}%)`}
                          strokeColor={{
                            '0%': '#1890ff',
                            '100%': '#36cfc9',
                          }}
                        />
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <Empty description="暂无部门数据" />
            )}
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="最近添加的员工" className="chart-card">
            {employeeStats.recent_employees.length > 0 ? (
              <Table
                className="recent-employees"
                dataSource={employeeStats.recent_employees}
                rowKey={record => record.key}
                columns={[
                  {
                    title: '姓名',
                    dataIndex: 'name',
                    key: 'name',
                  },
                  {
                    title: '部门',
                    dataIndex: 'department',
                    key: 'department',
                  },
                  {
                    title: '职位',
                    dataIndex: 'position',
                    key: 'position',
                  },
                  {
                    title: '添加时间',
                    dataIndex: 'created_at',
                    key: 'created_at',
                  },
                ]}
                pagination={false}
              />
            ) : (
              <Empty description="暂无员工数据" />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
