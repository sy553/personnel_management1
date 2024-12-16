import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Button, 
  Space, 
  Modal, 
  Form, 
  Input, 
  Select, 
  message,
  Row,
  Col,
  Card,
  Statistic,
  Input as AntInput
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined,
  TeamOutlined,
  BankOutlined,
  ApartmentOutlined,
  SearchOutlined
} from '@ant-design/icons';
import { getDepartments, createDepartment, updateDepartment, deleteDepartment } from '../../services/department';
import { getEmployees } from '../../services/employee';
import './styles/department.css';

const { Option } = Select;

const DepartmentList = () => {
  const [departments, setDepartments] = useState([]);
  const [employees, setEmployees] = useState([]); 
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [editingId, setEditingId] = useState(null);

  const fetchDepartments = async () => {
    try {
      setLoading(true);
      const response = await getDepartments();
      if (response.code === 200 && response.data) {
        const departmentData = response.data.map(dept => ({
          ...dept,
          key: dept.id,
          parentName: dept.parent_name || '无',
          managerName: dept.manager_name || '未指定'
        }));
        setDepartments(departmentData);
        console.log('获取到部门列表:', departmentData);
      } else {
        message.error(response.msg || '获取部门列表失败，请稍后重试');
      }
    } catch (error) {
      console.error('获取部门列表错误:', error);
      message.error('获取部门列表失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 获取员工列表
  const fetchEmployees = async () => {
    try {
      const response = await getEmployees({ employment_status: 'active' });
      if (response.code === 200 && response.data) {
        setEmployees(response.data.items || []);
      }
    } catch (error) {
      console.error('获取员工列表失败:', error);
    }
  };

  useEffect(() => {
    fetchDepartments();
    fetchEmployees(); 
  }, []);

  const handleAdd = () => {
    setEditingId(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingId(record.id);
    form.setFieldsValue(record);
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个部门吗？',
      onOk: async () => {
        try {
          const response = await deleteDepartment(id);
          if (response.code === 200) {
            message.success(response.msg || '删除成功');
            fetchDepartments();
          } else {
            message.error(response.msg || '删除失败');
          }
        } catch (error) {
          console.error('删除部门错误:', error);
          message.error('删除失败，请稍后重试');
        }
      },
    });
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      if (editingId) {
        const response = await updateDepartment(editingId, values);
        if (response.code === 200) {
          message.success(response.msg || '更新成功');
          setModalVisible(false);
          fetchDepartments();
        } else {
          message.error(response.msg || '更新失败');
        }
      } else {
        const response = await createDepartment(values);
        if (response.code === 200) {
          message.success(response.msg || '创建成功');
          setModalVisible(false);
          fetchDepartments();
        } else {
          message.error(response.msg || '创建失败');
        }
      }
    } catch (error) {
      console.error('操作失败:', error);
      if (error.response?.data?.msg) {
        message.error(error.response.data.msg);
      } else {
        message.error('操作失败，请稍后重试');
      }
    }
  };

  const columns = [
    {
      title: '部门名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '上级部门',
      dataIndex: 'parentName',
      key: 'parentName',
    },
    {
      title: '负责人',
      dataIndex: 'managerName',
      key: 'managerName',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space size="middle">
          <Button type="link" icon={<EditOutlined />} onClick={() => handleEdit(record)}>
            编辑
          </Button>
          <Button type="link" danger icon={<DeleteOutlined />} onClick={() => handleDelete(record.id)}>
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="department-container">
      {/* 页面标题 */}
      <div className="page-header">
        <h1 className="page-title">部门管理</h1>
      </div>

      {/* 统计卡片区域 */}
      <Row gutter={[16, 16]} className="department-stats">
        <Col xs={24} sm={8}>
          <Card className="stat-card">
            <Statistic
              title="部门总数"
              value={departments.length}
              prefix={<BankOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 搜索区域 */}
      <div className="search-area">
        <Row gutter={[16, 16]} className="search-form">
          <Col xs={24} sm={12} md={8}>
            <AntInput.Search
              placeholder="搜索部门名称"
              allowClear
              onSearch={(value) => {
                const filtered = departments.filter(dept => 
                  dept.name.toLowerCase().includes(value.toLowerCase())
                );
                setDepartments(filtered);
              }}
            />
          </Col>
        </Row>
      </div>

      {/* 操作按钮区 */}
      <div className="action-area">
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          添加部门
        </Button>
      </div>

      {/* 部门列表表格 */}
      <Card className="department-table">
        <Table
          columns={columns}
          dataSource={departments}
          rowKey="key"
          loading={loading}
        />
      </Card>

      {/* 添加/编辑部门弹窗 */}
      <Modal
        title={editingId ? "编辑部门" : "添加部门"}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name="name"
            label="部门名称"
            rules={[{ required: true, message: '请输入部门名称' }]}
          >
            <Input placeholder="请输入部门名称" />
          </Form.Item>

          <Form.Item
            name="parent_id"
            label="上级部门"
          >
            <Select
              placeholder="请选择上级部门"
              allowClear
            >
              {departments.map(dept => (
                <Option key={dept.id} value={dept.id}>{dept.name}</Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="manager_id"
            label="部门负责人"
          >
            <Select
              placeholder="请选择部门负责人"
              allowClear
            >
              {employees.map(emp => (
                <Option key={emp.id} value={emp.id}>{emp.name}</Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="description"
            label="部门描述"
          >
            <Input.TextArea placeholder="请输入部门描述" rows={4} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default DepartmentList;
