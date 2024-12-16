import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Space, Modal, message, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import moment from 'moment';
import '../../../styles/salary.css';
import {
  getSalaryStructures,
  createSalaryStructure,
  updateSalaryStructure,
  deleteSalaryStructure,
} from '../../../services/salary';
import SalaryStructureForm from './components/SalaryStructureForm';

/**
 * 工资结构管理页面
 * 用于管理员工的工资结构信息
 */
const SalaryStructure = () => {
  // 状态定义
  const [loading, setLoading] = useState(false);
  const [structures, setStructures] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [currentStructure, setCurrentStructure] = useState(null);

  // 获取工资结构列表
  const fetchStructures = async () => {
    setLoading(true);
    try {
      const response = await getSalaryStructures();
      if (response.code === 200) {
        // 确保数据是数组
        const structuresData = Array.isArray(response.data) ? response.data : [];
        setStructures(structuresData);
      } else {
        message.error('获取工资结构列表失败：' + (response.msg || '未知错误'));
      }
    } catch (error) {
      console.error('获取工资结构列表失败:', error);
      message.error('获取工资结构列表失败：' + (error.message || '未知错误'));
    } finally {
      setLoading(false);
    }
  };

  // 初始化加载数据
  useEffect(() => {
    fetchStructures();
  }, []);

  // 表格列定义
  const columns = [
    {
      title: '薪资结构名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '基本工资',
      dataIndex: 'basic_salary',
      key: 'basic_salary',
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '住房补贴',
      dataIndex: 'housing_allowance',
      key: 'housing_allowance',
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '交通补贴',
      dataIndex: 'transport_allowance',
      key: 'transport_allowance',
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '餐饮补贴',
      dataIndex: 'meal_allowance',
      key: 'meal_allowance',
      render: (value) => `¥${(value || 0).toFixed(2)}`,
    },
    {
      title: '生效日期',
      dataIndex: 'effective_date',
      key: 'effective_date',
      render: (date) => moment(date).format('YYYY-MM-DD'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除该工资结构吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 处理编辑
  const handleEdit = (record) => {
    setCurrentStructure({
      ...record,
      effective_date: moment(record.effective_date),
    });
    setModalVisible(true);
  };

  // 处理删除
  const handleDelete = async (id) => {
    try {
      const response = await deleteSalaryStructure(id);
      if (response.code === 200) {
        message.success('删除工资结构成功');
        fetchStructures();
      } else {
        message.error('删除失败：' + (response.msg || '未知错误'));
      }
    } catch (error) {
      console.error('删除工资结构失败:', error);
      message.error('删除失败：' + (error.message || '未知错误'));
    }
  };

  // 处理表单保存
  const handleSaveForm = async (values) => {
    try {
      let response;
      if (currentStructure) {
        // 更新
        response = await updateSalaryStructure(currentStructure.id, values);
      } else {
        // 创建
        response = await createSalaryStructure(values);
      }

      if (response.code === 200) {
        message.success(currentStructure ? '更新工资结构成功' : '创建工资结构成功');
        setModalVisible(false);
        setCurrentStructure(null);
        fetchStructures();
      } else {
        message.error((currentStructure ? '更新' : '创建') + '失败：' + (response.msg || '未知错误'));
      }
    } catch (error) {
      console.error(currentStructure ? '更新工资结构失败:' : '创建工资结构失败:', error);
      message.error((currentStructure ? '更新' : '创建') + '失败：' + (error.message || '未知错误'));
    }
  };

  // 处理模态框关闭
  const handleModalClose = () => {
    setModalVisible(false);
    setCurrentStructure(null);
  };

  return (
    <Card title="工资结构管理">
      <div className="table-operations">
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setModalVisible(true)}
        >
          新增工资结构
        </Button>
      </div>

      <Table
        loading={loading}
        columns={columns}
        dataSource={structures}
        rowKey="id"
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total) => `共 ${total} 条记录`,
        }}
      />

      <Modal
        title={currentStructure ? '编辑工资结构' : '新增工资结构'}
        open={modalVisible}
        onCancel={handleModalClose}
        footer={null}
        destroyOnClose
        width={600}
      >
        <SalaryStructureForm
          initialValues={currentStructure}
          onSave={handleSaveForm}
          onCancel={handleModalClose}
        />
      </Modal>
    </Card>
  );
};

export default SalaryStructure;
