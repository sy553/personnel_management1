import React, { useState, useEffect } from 'react';
import { Table, Card, Form, Select, Button, DatePicker, Space, Popconfirm, message } from 'antd';
import { 
  getSalaryStructureAssignments, 
  deleteSalaryStructureAssignment,
  updateSalaryStructureAssignment
} from '../../../services/salary';
import { getEmployees } from '../../../services/employee';
import { getDepartments } from '../../../services/department';
import moment from 'moment';

const { Option } = Select;

/**
 * 工资结构分配记录列表组件
 * @returns {React.ReactNode}
 */
const SalaryStructureAssignments = () => {
  // 状态定义
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [assignments, setAssignments] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  });

  // 获取员工和部门列表
  useEffect(() => {
    // 获取员工列表
    getEmployees().then(response => {
      if (response.code === 200) {
        const employeeList = Array.isArray(response.data?.items) ? response.data.items : [];
        setEmployees(employeeList);
      } else {
        message.error('获取员工列表失败：' + (response.msg || '未知错误'));
      }
    });

    // 获取部门列表
    getDepartments().then(response => {
      if (response.code === 200) {
        const departmentList = Array.isArray(response.data) ? response.data : [];
        setDepartments(departmentList);
      } else {
        message.error('获取部门列表失败：' + (response.msg || '未知错误'));
      }
    });
  }, []);

  // 加载分配记录数据
  const loadData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await getSalaryStructureAssignments(params);
      if (response.code === 200) {
        setAssignments(response.data || []);
      } else {
        message.error(response.msg || '获取分配记录失败');
      }
    } catch (error) {
      console.error('加载分配记录失败:', error);
      message.error('加载分配记录失败');
    }
    setLoading(false);
  };

  // 处理表单查询
  const handleSearch = async () => {
    const values = await form.validateFields();
    loadData(values);
  };

  // 处理表单重置
  const handleReset = () => {
    form.resetFields();
    loadData();
  };

  // 处理删除分配记录
  const handleDelete = async (id) => {
    try {
      const response = await deleteSalaryStructureAssignment(id);
      if (response.code === 200) {
        message.success('删除成功');
        loadData(form.getFieldsValue());
      } else {
        message.error(response.msg || '删除失败');
      }
    } catch (error) {
      console.error('删除分配记录失败:', error);
      message.error('删除失败');
    }
  };

  // 处理修改生效日期
  const handleUpdateEffectiveDate = async (id, date) => {
    try {
      const response = await updateSalaryStructureAssignment(id, {
        effective_date: date.format('YYYY-MM-DD')
      });
      if (response.code === 200) {
        message.success('更新成功');
        loadData(form.getFieldsValue());
      } else {
        message.error(response.msg || '更新失败');
      }
    } catch (error) {
      console.error('更新生效日期失败:', error);
      message.error('更新失败');
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '分配类型',
      key: 'assignment_type',
      render: (_, record) => {
        if (record.employee_id) {
          return <span style={{ color: '#1890ff' }}>员工专属</span>;
        } else if (record.department_id) {
          return <span style={{ color: '#52c41a' }}>部门默认</span>;
        } else if (record.is_default) {
          return <span style={{ color: '#faad14' }}>全局默认</span>;
        }
        return '-';
      }
    },
    {
      title: '员工/部门',
      key: 'target',
      render: (_, record) => {
        if (record.employee_id && record.employee) {
          return `${record.employee.name}（员工）`;
        } else if (record.department_id && record.department) {
          return `${record.department.name}（部门）`;
        } else if (record.is_default) {
          return '全局默认';
        }
        return '-';
      }
    },
    {
      title: '工资结构',
      dataIndex: ['salary_structure', 'name'],
      key: 'structure_name'
    },
    {
      title: '基本工资',
      dataIndex: ['salary_structure', 'basic_salary'],
      key: 'basic_salary',
      render: (text) => `¥${text}`
    },
    {
      title: '住房补贴',
      dataIndex: ['salary_structure', 'housing_allowance'],
      key: 'housing_allowance',
      render: (text) => `¥${text}`
    },
    {
      title: '交通补贴',
      dataIndex: ['salary_structure', 'transport_allowance'],
      key: 'transport_allowance',
      render: (text) => `¥${text}`
    },
    {
      title: '餐饮补贴',
      dataIndex: ['salary_structure', 'meal_allowance'],
      key: 'meal_allowance',
      render: (text) => `¥${text}`
    },
    {
      title: '生效日期',
      dataIndex: 'effective_date',
      key: 'effective_date',
      render: (text, record) => (
        <DatePicker
          defaultValue={moment(text)}
          onChange={(date) => handleUpdateEffectiveDate(record.id, date)}
        />
      )
    },
    {
      title: '状态',
      key: 'status',
      render: (_, record) => (
        <span style={{ color: record.is_active ? '#52c41a' : '#ff4d4f' }}>
          {record.is_active ? '生效中' : '已失效'}
        </span>
      )
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Popconfirm
            title="确定要删除这条分配记录吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger>删除</Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  // 初始加载数据
  useEffect(() => {
    loadData();
  }, []);

  return (
    <Card title="工资结构分配记录">
      {/* 查询表单 */}
      <Form
        form={form}
        layout="inline"
        style={{ marginBottom: 24 }}
      >
        <Form.Item name="employee_id" label="员工">
          <Select
            allowClear
            placeholder="请选择员工"
            style={{ width: 200 }}
            showSearch
            optionFilterProp="children"
          >
            {employees.map(emp => (
              <Option key={emp.id} value={emp.id}>{emp.name}</Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item name="department_id" label="部门">
          <Select
            allowClear
            placeholder="请选择部门"
            style={{ width: 200 }}
            showSearch
            optionFilterProp="children"
          >
            {departments.map(dept => (
              <Option key={dept.id} value={dept.id}>{dept.name}</Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item name="is_default" label="类型">
          <Select
            allowClear
            placeholder="请选择类型"
            style={{ width: 200 }}
          >
            <Option value={false}>员工专属</Option>
            <Option value={true}>默认结构</Option>
          </Select>
        </Form.Item>

        <Form.Item>
          <Space>
            <Button type="primary" onClick={handleSearch}>查询</Button>
            <Button onClick={handleReset}>重置</Button>
          </Space>
        </Form.Item>
      </Form>

      {/* 数据表格 */}
      <Table
        columns={columns}
        dataSource={assignments}
        rowKey="id"
        loading={loading}
        pagination={pagination}
        onChange={(newPagination) => setPagination(newPagination)}
      />
    </Card>
  );
};

export default SalaryStructureAssignments;
