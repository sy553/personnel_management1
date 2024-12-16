import React, { useState, useEffect } from 'react';
import { Card, Table, Button, message, Row, Col, Statistic, Form, DatePicker, Popconfirm, Modal, Space } from 'antd';
import { MailOutlined, FileAddOutlined, DownloadOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import moment from 'moment';
import '../../../styles/salary.css';
import { getSalaryRecords, batchCreateSalaryRecords, batchSendSalarySlips, exportSalaryRecords, deleteSalaryRecord, updateSalaryRecord } from '../../../services/salary';
import { getEmployees } from '../../../services/employee';
import AssignSalaryStructure from '../AssignSalaryStructure';
import SalaryRecordForm from './components/SalaryRecordForm';

/**
 * 月度工资发放页面
 * 用于管理和发放员工月度工资
 */
const SalaryRecords = () => {
  // 状态定义
  const [loading, setLoading] = useState(false);
  const [records, setRecords] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [selectedMonth, setSelectedMonth] = useState(moment());
  const [assignModalVisible, setAssignModalVisible] = useState(false);
  const [editModalVisible, setEditModalVisible] = useState(false);
  const [currentRecord, setCurrentRecord] = useState(null);

  // 获取工资记录
  const fetchRecords = async () => {
    setLoading(true);
    try {
      // 使用封装的API函数替代直接的axios调用
      const response = await getSalaryRecords({
        year: selectedMonth.year(),
        month: selectedMonth.month() + 1
      });
      
      if (response.code === 200) {
        setRecords(response.data.records);
        setStatistics(response.data.statistics);
      } else {
        message.error(response.msg || '获取工资记录失败');
      }
    } catch (error) {
      console.error('获取工资记录失败:', error);
      message.error(error.message || '获取工资记录失败');
    } finally {
      setLoading(false);
    }
  };

  // 监听月份变化
  useEffect(() => {
    fetchRecords();
  }, [selectedMonth]);

  // 处理月份选择变化
  const handleMonthChange = (date) => {
    if (date) {
      // 确保不会意外改变年份
      const newDate = moment(date).set({
        year: selectedMonth ? selectedMonth.year() : moment().year(),
        month: date.month()
      });
      setSelectedMonth(newDate);
    }
  };

  // 批量生成工资记录
  const handleBatchCreate = async () => {
    try {
      setLoading(true);
      // 获取所有在职员工列表
      const employeesResponse = await getEmployees({
        page: 1,
        per_page: 1000,  // 设置较大的数值以获取所有员工
        employment_status: 'active'  // 只获取在职员工
      });
      
      if (!employeesResponse || !employeesResponse.data || !employeesResponse.data.items) {
        message.error('获取员工列表失败');
        return;
      }
      
      const employeeIds = employeesResponse.data.items.map(emp => emp.id);
      if (employeeIds.length === 0) {
        message.warning('没有可用的员工记录');
        return;
      }

      // 使用封装的API函数
      const response = await batchCreateSalaryRecords({
        year: selectedMonth.year(),
        month: selectedMonth.month() + 1,
        employee_ids: employeeIds
      });
      
      if (response.code === 200) {
        // 处理成功、失败和跳过的记录
        const { success = [], failed = [], skipped = [] } = response.data;
        
        // 构建提示信息
        const successCount = success.length;
        const failedCount = failed.length;
        const skippedCount = skipped.length;
        
        let resultMessage = [];
        if (successCount > 0) {
          resultMessage.push(`成功生成${successCount}条工资记录`);
        }
        if (skippedCount > 0) {
          resultMessage.push(`${skippedCount}名员工已有工资记录，已跳过`);
        }
        if (failedCount > 0) {
          // 收集失败原因
          const failureReasons = failed.reduce((acc, curr) => {
            const reason = curr.reason || '未知原因';
            acc[reason] = (acc[reason] || 0) + 1;
            return acc;
          }, {});
          
          // 格式化失败原因
          const failureMessages = Object.entries(failureReasons).map(
            ([reason, count]) => `${count}名员工因${reason}`
          );
          
          resultMessage.push(`${failedCount}条记录生成失败：${failureMessages.join('；')}`);
        }
        
        // 显示操作结果
        if (successCount > 0) {
          message.success(resultMessage.join('；'));
        } else if (skippedCount > 0 && failedCount === 0) {
          message.info(resultMessage.join('；'));
        } else {
          message.error(resultMessage.join('；'));
        }
        
        // 刷新记录列表
        await fetchRecords();
      } else {
        // 处理错误响应
        message.error(response.message || '生成工资记录失败');
      }
    } catch (error) {
      console.error('批量生成工资记录失败:', error);
      // 显示详细的错误信息
      if (error.response?.data?.message) {
        message.error(error.response.data.message);
      } else {
        message.error('生成工资记录失败，请检查网络连接');
      }
    } finally {
      setLoading(false);
    }
  };

  // 批量发送工资条
  const handleBatchSend = async () => {
    try {
      // 使用封装的API函数
      const response = await batchSendSalarySlips({
        year: selectedMonth.year(),
        month: selectedMonth.month() + 1
      });
      
      if (response.code === 200) {
        message.success('批量发送工资条成功');
        fetchRecords();
      } else {
        message.error(response.msg || '批量发送工资条失败');
      }
    } catch (error) {
      console.error('批量发送工资条失败:', error);
      message.error(error.message || '批量发送工资条失败');
    }
  };

  // 导出工资记录
  const handleExport = () => {
    message.info('导出功能开发中');
  };

  // 处理编辑
  const handleEdit = (record) => {
    setCurrentRecord(record);
    setEditModalVisible(true);
  };

  // 处理删除
  const handleDelete = async (id) => {
    try {
      const response = await deleteSalaryRecord(id);
      if (response.code === 200) {
        message.success('删除工资记录成功');
        fetchRecords();
      } else {
        message.error(response.msg || '删除工资记录失败');
      }
    } catch (error) {
      console.error('删除工资记录失败:', error);
      message.error(error.message || '删除工资记录失败');
    }
  };

  // 处理更新
  const handleUpdate = async (values) => {
    try {
      const response = await updateSalaryRecord(currentRecord.id, values);
      if (response.code === 200) {
        message.success('更新工资记录成功');
        setEditModalVisible(false);
        setCurrentRecord(null);
        fetchRecords();
      } else {
        message.error(response.msg || '更新工资记录失败');
      }
    } catch (error) {
      console.error('更新工资记录失败:', error);
      message.error(error.message || '更新工资记录失败');
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '员工姓名',
      dataIndex: 'employee_name',  // 使用直接提供的员工姓名字段
      key: 'employee_name',
    },
    {
      title: '部门',
      dataIndex: 'department_name',  // 使用直接提供的部门名称字段
      key: 'department_name',
    },
    {
      title: '基本工资',
      dataIndex: 'basic_salary',
      key: 'basic_salary',
      render: (value) => `¥${value.toFixed(2)}`,
    },
    {
      title: '补贴',
      dataIndex: 'allowances',
      key: 'allowances',
      render: (value) => `¥${value.toFixed(2)}`,
    },
    {
      title: '加班费',
      dataIndex: 'overtime_pay',
      key: 'overtime_pay',
      render: (value) => `¥${value.toFixed(2)}`,
    },
    {
      title: '奖金',
      dataIndex: 'bonus',
      key: 'bonus',
      render: (value) => `¥${value.toFixed(2)}`,
    },
    {
      title: '个税',
      dataIndex: 'tax',
      key: 'tax',
      render: (value) => `¥${value.toFixed(2)}`,
    },
    {
      title: '实发工资',
      dataIndex: 'net_salary',
      key: 'net_salary',
      render: (value) => `¥${value.toFixed(2)}`,
    },
    {
      title: '发放状态',
      dataIndex: 'payment_status',
      key: 'payment_status',
      render: (status) => ({
        'pending': '待发放',
        'paid': '已发放',
        'cancelled': '已取消'
      }[status] || status),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<MailOutlined />}
            onClick={() => handleSendSalarySlip(record.id)}
            disabled={record.payment_status === 'paid'}
          >
            发送工资条
          </Button>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
            disabled={record.payment_status === 'paid'}
          >
            修改
          </Button>
          <Popconfirm
            title="确定要删除这条工资记录吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
            disabled={record.payment_status === 'paid'}
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
              disabled={record.payment_status === 'paid'}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 发送单个工资条
  const handleSendSalarySlip = async (id) => {
    try {
      // TODO: 使用封装的API函数发送工资条
      // const response = await sendSalarySlip(id);
      // if (response.code === 200) {
      //   message.success('发送工资条成功');
      //   fetchRecords();
      // } else {
      //   message.error(response.msg || '发送工资条失败');
      // }
      message.error('发送工资条功能开发中');
    } catch (error) {
      console.error('发送工资条失败:', error);
      message.error(error.message || '发送工资条失败');
    }
  };

  // 工具栏渲染函数
  const toolBarRender = () => [
    <Button
      key="assign"
      type="primary"
      onClick={() => setAssignModalVisible(true)}
    >
      分配工资结构
    </Button>,
    <Button
      key="batch"
      type="primary"
      onClick={handleBatchCreate}
      icon={<FileAddOutlined />}
    >
      批量生成
    </Button>,
    <Popconfirm
      title="确定要批量发送工资条吗？"
      onConfirm={handleBatchSend}
    >
      <Button
        icon={<MailOutlined />}
      >
        批量发送
      </Button>
    </Popconfirm>,
    <Button
      icon={<DownloadOutlined />}
      onClick={handleExport}
    >
      导出Excel
    </Button>,
  ];

  return (
    <div className="salary-page">
      <Card title="月度工资发放" className="salary-card">
        <div className="salary-header">
          <Row gutter={24}>
            <Col span={6}>
              <Form.Item label="选择月份">
                <DatePicker
                  value={selectedMonth}
                  onChange={handleMonthChange}
                  picker="month"
                />
              </Form.Item>
            </Col>
            <Col span={18} style={{ textAlign: 'right' }}>
              {toolBarRender()}
            </Col>
          </Row>
        </div>

        <div className="salary-statistics">
          <Row gutter={24}>
            <Col span={6}>
              <Statistic
                title="本月应发总额"
                value={statistics.total?.total_gross || 0}
                precision={2}
                prefix="¥"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="本月实发总额"
                value={statistics.total?.total_net || 0}
                precision={2}
                prefix="¥"
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="本月记录数"
                value={statistics.total?.total_count || 0}
              />
            </Col>
            <Col span={6}>
              <Statistic
                title="已发放记录数"
                value={statistics.total?.paid_count || 0}
              />
            </Col>
          </Row>
        </div>

        <Table
          className="salary-table"
          columns={columns}
          dataSource={records}
          rowKey="id"
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
          }}
        />
      </Card>

      {/* 工资结构分配模态框 */}
      <AssignSalaryStructure
        visible={assignModalVisible}
        onCancel={() => setAssignModalVisible(false)}
        onSuccess={() => {
          setAssignModalVisible(false);
          fetchRecords(selectedMonth);  // 刷新数据
        }}
      />

      {/* 工资记录编辑模态框 */}
      <SalaryRecordForm
        visible={editModalVisible}
        record={currentRecord}
        onCancel={() => {
          setEditModalVisible(false);
          setCurrentRecord(null);
        }}
        onSuccess={(values) => handleUpdate(values)}
      />
    </div>
  );
};

export default SalaryRecords;
