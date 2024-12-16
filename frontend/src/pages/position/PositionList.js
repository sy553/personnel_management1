import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Button, 
  Space, 
  Modal, 
  Form, 
  Input, 
  message, 
  Select,
  Card,
  Row,
  Col,
  Statistic
} from 'antd';
import { 
  PlusOutlined, 
  EditOutlined, 
  DeleteOutlined,
  IdcardOutlined
} from '@ant-design/icons';
import { getPositions, createPosition, updatePosition, deletePosition } from '../../services/position';
import { getDepartments } from '../../services/department';
import './styles/position.css';  

const PositionList = () => {
  const [positions, setPositions] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();
  const [editingId, setEditingId] = useState(null);

  // 获取职位列表
  const fetchPositions = async () => {
    try {
      setLoading(true);
      const response = await getPositions();
      if (response.code === 200) {
        console.log('获取到的职位数据:', response.data);  
        setPositions(response.data);
      } else {
        message.error(response.msg || '获取职位列表失败');
      }
    } catch (error) {
      console.error('获取职位列表失败:', error);  
      message.error('获取职位列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取部门列表
  const fetchDepartments = async () => {
    try {
      const response = await getDepartments();
      if (response.code === 200) {
        console.log('获取到的部门数据:', response.data);
        setDepartments(response.data);
      } else {
        message.error(response.msg || '获取部门列表失败');
      }
    } catch (error) {
      console.error('获取部门列表失败:', error);
      message.error('获取部门列表失败');
    }
  };

  useEffect(() => {
    fetchPositions();
    fetchDepartments();
  }, []);

  const handleAdd = () => {
    setEditingId(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEdit = (record) => {
    setEditingId(record.id);
    form.setFieldsValue({
      ...record,
      department_id: record.department_id?.toString()
    });
    setModalVisible(true);
  };

  const handleDelete = async (id) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个职位吗？',
      onOk: async () => {
        try {
          const response = await deletePosition(id);
          if (response.code === 200) {
            message.success('删除成功');
            fetchPositions();
          } else {
            message.error(response.msg || '删除失败');
          }
        } catch (error) {
          console.error('删除失败:', error);
          message.error('删除失败');
        }
      },
    });
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      
      // 验证部门ID
      if (!values.department_id) {
        message.error('请选择部门');
        return;
      }

      setLoading(true);

      // 转换并验证数据
      const submitData = {
        ...values,
        department_id: parseInt(values.department_id, 10),
      };

      // 打印提交的数据
      console.log('提交的数据:', submitData);

      if (editingId) {
        const response = await updatePosition(editingId, submitData);
        console.log('更新职位响应:', response);
        if (response.code === 200) {
          message.success('更新成功');
          setModalVisible(false);
          await fetchPositions();
        } else {
          message.error(response.msg || '更新失败');
        }
      } else {
        const response = await createPosition(submitData);
        console.log('创建职位响应:', response);
        if (response.code === 200) {
          message.success('创建成功');
          setModalVisible(false);
          await fetchPositions();
        } else {
          message.error(response.msg || '创建失败');
        }
      }
    } catch (error) {
      console.error('操作失败:', error);
      if (error.response) {
        console.error('错误响应:', error.response.data);
        message.error(error.response.data.msg || '操作失败');
      } else {
        message.error('操作失败');
      }
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: '职位名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '所属部门',
      dataIndex: 'department_name',
      key: 'department_name',
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
          <Button
            type="primary"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="primary"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="position-container">
      {/* 页面标题 */}
      <div className="page-header">
        <h1 className="page-title">职位管理</h1>
      </div>

      {/* 统计卡片区域 */}
      <Row gutter={[16, 16]} className="position-stats">
        <Col xs={24} sm={8}>
          <Card className="stat-card">
            <Statistic
              title="职位总数"
              value={positions.length}
              prefix={<IdcardOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 操作按钮区 */}
      <div className="action-area">
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleAdd}
        >
          添加职位
        </Button>
      </div>

      {/* 职位列表表格 */}
      <Card className="position-table">
        <Table
          columns={columns}
          dataSource={positions}
          rowKey="id"
          loading={loading}
        />
      </Card>

      {/* 添加/编辑职位弹窗 */}
      <Modal
        title={editingId ? '编辑职位' : '新增职位'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        confirmLoading={loading}
        bodyStyle={{ padding: '24px' }}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            description: '',
          }}
        >
          <Form.Item
            name="name"
            label="职位名称"
            rules={[{ required: true, message: '请输入职位名称' }]}
          >
            <Input placeholder="请输入职位名称" />
          </Form.Item>
          <Form.Item
            name="department_id"
            label="所属部门"
            rules={[{ required: true, message: '请选择所属部门' }]}
          >
            <Select
              placeholder="请选择部门"
              options={departments.map(dept => ({
                label: dept.name,
                value: dept.id.toString()
              }))}
              showSearch
              optionFilterProp="label"
            />
          </Form.Item>
          <Form.Item
            name="description"
            label="描述"
          >
            <Input.TextArea placeholder="请输入职位描述" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PositionList;
