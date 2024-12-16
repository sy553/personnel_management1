import React, { useState, useEffect } from 'react';
import { Card, Table, Form, Select, DatePicker, Button, Row, Col, Statistic } from 'antd';
import moment from 'moment';
import request from '../../../utils/request';  // 导入封装的request实例
import { getDepartments } from '../../../services/department';  // 导入部门服务

const { Option } = Select;

/**
 * 薪资统计报表页面
 * 用于展示和分析薪资数据
 */
const SalaryStatistics = () => {
  // 状态定义
  const [loading, setLoading] = useState(false);
  const [statistics, setStatistics] = useState(null);
  const [departmentStats, setDepartmentStats] = useState([]); // 添加部门统计数据状态
  const [departments, setDepartments] = useState([]);
  const [form] = Form.useForm();

  // 获取部门列表
  useEffect(() => {
    const fetchDepartments = async () => {
      try {
        const response = await getDepartments();
        if (response.code === 200) {
          setDepartments(response.data || []);
        }
      } catch (error) {
        console.error('获取部门列表失败:', error);
      }
    };
    fetchDepartments();
  }, []);

  // 获取统计数据
  const fetchStatistics = async (values) => {
    setLoading(true);
    try {
      const { year, month, department_id } = values;
      // 获取总体统计数据
      const totalResponse = await request.get('/api/salary/statistics', {
        params: {
          year,
          month: month ? month.month() + 1 : undefined,
          department_id
        }
      });

      if (totalResponse.code === 200) {
        // 如果选择了部门，只显示该部门的统计数据
        if (department_id) {
          const department = departments.find(d => d.id === department_id);
          const statsData = {
            ...totalResponse.data,
            department_name: department ? department.name : '未知部门'
          };
          setStatistics(statsData);
          setDepartmentStats([statsData]); // 只显示选中部门的数据
        } else {
          // 未选择部门时，需要获取所有部门的统计数据
          setStatistics({
            ...totalResponse.data,
            department_name: '全部部门'
          });

          // 获取各部门的统计数据
          const departmentStatsPromises = departments.map(dept =>
            request.get('/api/salary/statistics', {
              params: {
                year,
                month: month ? month.month() + 1 : undefined,
                department_id: dept.id
              }
            })
          );

          const departmentResponses = await Promise.all(departmentStatsPromises);
          const deptStats = departmentResponses
            .map((response, index) => {
              if (response.code === 200) {
                return {
                  ...response.data,
                  department_name: departments[index].name,
                  key: departments[index].id // 添加key以避免警告
                };
              }
              return null;
            })
            .filter(Boolean); // 过滤掉null值

          setDepartmentStats(deptStats);
        }
      }
    } catch (error) {
      console.error('获取统计数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 表单提交处理
  const handleSubmit = (values) => {
    fetchStatistics(values);
  };

  // 重置表单
  const handleReset = () => {
    form.resetFields();
    setStatistics(null);
    setDepartmentStats([]); // 清空部门统计数据
  };

  // 表格列定义
  const columns = [
    {
      title: '部门',
      dataIndex: 'department_name',
      key: 'department_name',
      // 添加中文注释：显示部门名称
    },
    {
      title: '员工数',
      dataIndex: 'total_count',  // 修改为后端返回的字段名
      key: 'total_count',
      // 添加中文注释：显示部门员工总数
      render: (value) => `${value || 0}人`  // 添加"人"单位
    },
    {
      title: '基本工资总额',
      dataIndex: 'total_basic',
      key: 'total_basic',
      // 添加中文注释：显示基本工资总额
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '补贴总额',
      dataIndex: 'total_allowances',
      key: 'total_allowances',
      // 添加中文注释：显示补贴总额
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '加班费总额',
      dataIndex: 'total_overtime',
      key: 'total_overtime',
      // 添加中文注释：显示加班费总额
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '奖金总额',
      dataIndex: 'total_bonus',
      key: 'total_bonus',
      // 添加中文注释：显示奖金总额
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '个税总额',
      dataIndex: 'total_tax',
      key: 'total_tax',
      // 添加中文注释：显示个人所得税总额
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '实发工资总额',
      dataIndex: 'total_net',
      key: 'total_net',
      // 添加中文注释：显示实发工资总额
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
  ];

  return (
    <div className="salary-statistics">
      <Card title="薪资统计报表" className="statistics-card">
        {/* 查询表单 */}
        <Form
          form={form}
          layout="inline"
          onFinish={handleSubmit}
          style={{ marginBottom: 24 }}
        >
          <Form.Item
            name="year"
            label="年份"
            initialValue={moment()}
            rules={[{ required: true, message: '请选择年份' }]}
          >
            <DatePicker picker="year" />
          </Form.Item>
          <Form.Item
            name="month"
            label="月份"
            initialValue={moment()}
            rules={[{ required: true, message: '请选择月份' }]}
          >
            <DatePicker picker="month" />
          </Form.Item>
          <Form.Item name="department_id" label="部门">
            <Select
              allowClear
              placeholder="请选择部门"
              style={{ width: 200 }}
            >
              {departments.map(dept => (
                <Option key={dept.id} value={dept.id}>{dept.name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading}>
              查询
            </Button>
            <Button style={{ marginLeft: 8 }} onClick={handleReset}>
              重置
            </Button>
          </Form.Item>
        </Form>

        {/* 统计概览 */}
        {statistics && (
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={6}>
              <Statistic
                title="部门"
                value={statistics.department_name || '全部部门'}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="员工人数"
                value={statistics.total_count || 0}
                suffix="人"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="本期工资总额"
                value={statistics.total_gross || 0}
                prefix="¥"
                precision={2}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="人均工资"
                value={statistics.total_count ? (statistics.total_gross / statistics.total_count).toFixed(2) : 0}
                prefix="¥"
                precision={2}
              />
            </Col>
          </Row>
        )}

        {/* 详细数据表格 */}
        <Table
          columns={columns}
          dataSource={departmentStats.length > 0 ? departmentStats : (statistics ? [statistics] : [])}
          loading={loading}
          rowKey={record => record.key || 'total'}
          pagination={false}
          scroll={{ x: true }}
        />
      </Card>
    </div>
  );
};

export default SalaryStatistics;
