import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Space,
  Button,
  Input,
  Select,
  Form,
  message,
  Modal,
  DatePicker,
} from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { getInternStatusList, createInternStatus, updateInternStatus } from '../../services/intern';
import { getDepartments } from '../../services/department';
import { getPositions } from '../../services/position';
import { getEmployees } from '../../services/employee';
import moment from 'moment';

const { Option } = Select;
const { RangePicker } = DatePicker;

/**
 * 实习列表组件
 * 用于展示和管理实习生信息
 */
const InternList = () => {
  // 状态定义
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  const [departments, setDepartments] = useState([]);
  const [positions, setPositions] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [currentRecord, setCurrentRecord] = useState(null);
  const [form] = Form.useForm();
  const [searchForm] = Form.useForm();

  // 初始化数据
  useEffect(() => {
    fetchDepartments();
    fetchPositions();
    fetchEmployees();
    fetchInternList();
  }, []);

  // 获取部门列表
  const fetchDepartments = async () => {
    try {
      const res = await getDepartments();
      if (res.code === 200) {
        setDepartments(res.data);
      }
    } catch (error) {
      message.error('获取部门列表失败');
    }
  };

  // 获取职位列表
  const fetchPositions = async () => {
    try {
      const res = await getPositions();
      if (res.code === 200) {
        setPositions(res.data);
      }
    } catch (error) {
      message.error('获取职位列表失败');
    }
  };

  // 获取员工列表
  const fetchEmployees = async () => {
    try {
      const res = await getEmployees();
      if (res.code === 200) {
        setEmployees(res.data.items);
      }
    } catch (error) {
      message.error('获取员工列表失败');
    }
  };

  // 获取实习列表
  const fetchInternList = async (params = {}) => {
    setLoading(true);
    try {
      const res = await getInternStatusList({
        page: pagination.current,
        per_page: pagination.pageSize,
        ...params,
      });
      if (res.code === 200) {
        setData(res.data.items || []);
        setPagination({
          ...pagination,
          total: res.data.total || 0,
        });
      } else {
        message.error(res.message || '获取实习列表失败');
      }
    } catch (error) {
      console.error('获取实习列表失败:', error);
      message.error('获取实习列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 处理表格变化
  const handleTableChange = (newPagination, filters, sorter) => {
    setPagination(newPagination);
    fetchInternList({
      page: newPagination.current,
      per_page: newPagination.pageSize,
      ...filters,
      ...sorter,
    });
  };

  // 处理搜索
  const handleSearch = async (values) => {
    setPagination({
      ...pagination,
      current: 1,
    });
    await fetchInternList({
      ...values,
      page: 1,
    });
  };

  // 处理重置
  const handleReset = () => {
    searchForm.resetFields();
    setPagination({
      ...pagination,
      current: 1,
    });
    fetchInternList({
      page: 1,
    });
  };

  // 表格列定义
  const columns = [
    {
      title: '员工姓名',
      dataIndex: 'employee_name',
      key: 'employee_name',
    },
    {
      title: '部门',
      dataIndex: 'department_name',
      key: 'department_name',
    },
    {
      title: '职位',
      dataIndex: 'position_name',
      key: 'position_name',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusMap = {
          intern: '实习中',
          probation: '试用期',
          regular: '正式',
        };
        return statusMap[status] || status;
      },
    },
    {
      title: '开始日期',
      dataIndex: 'start_date',
      key: 'start_date',
    },
    {
      title: '计划结束日期',
      dataIndex: 'planned_end_date',
      key: 'planned_end_date',
    },
    {
      title: '实际结束日期',
      dataIndex: 'actual_end_date',
      key: 'actual_end_date',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button type="link" onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Button type="link" onClick={() => handleEvaluation(record)}>
            评估
          </Button>
        </Space>
      ),
    },
  ];

  // 处理编辑
  const handleEdit = (record) => {
    setCurrentRecord(record);
    form.setFieldsValue({
      ...record,
      start_date: moment(record.start_date),
      planned_end_date: moment(record.planned_end_date),
      actual_end_date: record.actual_end_date ? moment(record.actual_end_date) : undefined,
    });
    setModalVisible(true);
  };

  // 处理评估
  const handleEvaluation = (record) => {
    // 跳转到评估页面
    window.location.href = `/intern/evaluation/${record.id}`;
  };

  // 处理模态框确认
  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      const data = {
        ...values,
        start_date: values.start_date.format('YYYY-MM-DD'),
        planned_end_date: values.planned_end_date.format('YYYY-MM-DD'),
        actual_end_date: values.actual_end_date ? values.actual_end_date.format('YYYY-MM-DD') : undefined,
      };

      if (currentRecord) {
        await updateInternStatus(currentRecord.id, data);
        message.success('更新成功');
      } else {
        await createInternStatus(data);
        message.success('创建成功');
      }

      setModalVisible(false);
      form.resetFields();
      fetchInternList();
    } catch (error) {
      message.error('操作失败');
    }
  };

  return (
    <Card>
      {/* 搜索表单 */}
      <Form
        form={searchForm}
        layout="inline"
        onFinish={handleSearch}
        style={{ marginBottom: 24 }}
      >
        <Form.Item name="keyword">
          <Input placeholder="搜索员工姓名" />
        </Form.Item>
        <Form.Item name="department_id">
          <Select
            placeholder="选择部门"
            style={{ width: 200 }}
            allowClear
          >
            {departments.map((dept) => (
              <Option key={dept.id} value={dept.id}>
                {dept.name}
              </Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item name="status">
          <Select
            placeholder="选择状态"
            style={{ width: 200 }}
            allowClear
          >
            <Option value="intern">实习中</Option>
            <Option value="probation">试用期</Option>
            <Option value="regular">正式</Option>
          </Select>
        </Form.Item>
        <Form.Item name="date_range">
          <RangePicker />
        </Form.Item>
        <Form.Item>
          <Button type="primary" htmlType="submit">
            搜索
          </Button>
        </Form.Item>
        <Form.Item>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setCurrentRecord(null);
              form.resetFields();
              setModalVisible(true);
            }}
          >
            新建实习记录
          </Button>
        </Form.Item>
        <Form.Item>
          <Button type="primary" onClick={handleReset}>
            重置
          </Button>
        </Form.Item>
      </Form>

      {/* 数据表格 */}
      <Table
        columns={columns}
        dataSource={data}
        pagination={pagination}
        loading={loading}
        onChange={handleTableChange}
        rowKey="id"
      />

      {/* 编辑/创建模态框 */}
      <Modal
        title={currentRecord ? '编辑实习信息' : '新增实习信息'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
          setCurrentRecord(null);
        }}
        style={{
          body: { padding: '24px' }
        }}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="employee_id"
            label="员工"
            rules={[{ required: true, message: '请选择员工' }]}
          >
            <Select placeholder="选择员工">
              {employees.map((emp) => (
                <Option key={emp.id} value={emp.id}>
                  {emp.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="department_id"
            label="部门"
            rules={[{ required: true, message: '请选择部门' }]}
          >
            <Select placeholder="选择部门">
              {departments.map((dept) => (
                <Option key={dept.id} value={dept.id}>
                  {dept.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="position_id"
            label="职位"
            rules={[{ required: true, message: '请选择职位' }]}
          >
            <Select placeholder="选择职位">
              {positions.map((pos) => (
                <Option key={pos.id} value={pos.id}>
                  {pos.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="mentor_id"
            label="导师"
          >
            <Select placeholder="选择导师" allowClear>
              {employees.map((emp) => (
                <Option key={emp.id} value={emp.id}>
                  {emp.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="start_date"
            label="开始日期"
            rules={[{ required: true, message: '请选择开始日期' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="planned_end_date"
            label="计划结束日期"
            rules={[{ required: true, message: '请选择计划结束日期' }]}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="actual_end_date"
            label="实际结束日期"
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="comments"
            label="备注"
          >
            <Input.TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default InternList;
