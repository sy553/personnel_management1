// 考勤规则管理页面
import React, { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Space,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  DatePicker,
  Popconfirm,
  message,
  TimePicker,
  Card,
  Switch,
  Transfer,
  Radio,
  List,
  Empty,
} from 'antd';
import { EditOutlined, DeleteOutlined, PlusOutlined, ReloadOutlined, ShareAltOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import {
  getAttendanceRules,
  createAttendanceRule,
  updateAttendanceRule,
  deleteAttendanceRule,
  assignRuleToDepartment,
  assignRuleToEmployees,
  getRuleAssignments,
  unassignRuleFromDepartment,
  unassignRuleFromEmployee,
} from '../../services/attendance';
import { getDepartments } from '../../services/department';
import { getEmployees } from '../../services/employee';

/**
 * 考勤规则管理组件
 * @returns {JSX.Element}
 */
const Rules = () => {
  // 状态定义
  const [rules, setRules] = useState([]); // 考勤规则列表
  const [loading, setLoading] = useState(false); // 页面加载状态
  const [modalVisible, setModalVisible] = useState(false); // 模态框显示状态
  const [modalTitle, setModalTitle] = useState('新增考勤规则'); // 模态框标题
  const [form] = Form.useForm(); // 表单实例
  const [assignForm] = Form.useForm(); // 分配表单实例
  const [currentRule, setCurrentRule] = useState(null); // 当前编辑的规则
  const [submitting, setSubmitting] = useState(false); // 表单提交状态
  const [departments, setDepartments] = useState([]); // 部门列表
  const [employees, setEmployees] = useState([]); // 员工列表
  const [selectedEmployees, setSelectedEmployees] = useState([]); // 选中的员工
  const [assignModalVisible, setAssignModalVisible] = useState(false); // 分配规则模态框
  const [currentAssignRule, setCurrentAssignRule] = useState(null); // 当前分配的规则
  const [assignmentsModalVisible, setAssignmentsModalVisible] = useState(false); // 分配详情模态框显示状态
  const [currentAssignments, setCurrentAssignments] = useState(null); // 当前规则的分配信息

  /**
   * 获取考勤规则列表
   */
  const fetchRules = async () => {
    try {
      setLoading(true);
      const response = await getAttendanceRules();
      // 检查响应状态
      if (response && response.code === 200 && Array.isArray(response.data)) {
        // 处理日期和时间格式
        const formattedRules = response.data.map(rule => ({
          ...rule,
          // 使用原始的字符串值，不进行转换
          effective_start_date: rule.effective_start_date || '',
          effective_end_date: rule.effective_end_date || '',
          work_start_time: rule.work_start_time || '',
          work_end_time: rule.work_end_time || '',
          break_start_time: rule.break_start_time || '',
          break_end_time: rule.break_end_time || ''
        }));
        setRules(formattedRules);
      } else {
        console.error('获取考勤规则列表失败:', response);
        message.error('获取考勤规则列表失败');
      }
    } catch (error) {
      console.error('获取考勤规则列表失败:', error);
      message.error('获取考勤规则列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 获取部门列表
  const fetchDepartments = async () => {
    try {
      const response = await getDepartments();
      if (response?.code === 200) {
        setDepartments(response.data || []);
      }
    } catch (error) {
      console.error('获取部门列表失败:', error);
      message.error('获取部门列表失败');
    }
  };

  // 获取员工列表
  const fetchEmployees = async () => {
    try {
      const response = await getEmployees();
      if (response?.code === 200) {
        // 确保我们使用正确的数据结构
        const employeeList = response.data?.items || [];
        setEmployees(employeeList);
      }
    } catch (error) {
      console.error('获取员工列表失败:', error);
      message.error('获取员工列表失败');
    }
  };

  // 获取规则分配信息
  const fetchRuleAssignments = async (ruleId) => {
    try {
      const response = await getRuleAssignments(ruleId);
      if (response?.code === 200) {
        setCurrentAssignments(response.data);
      } else {
        message.error('获取规则分配信息失败');
      }
    } catch (error) {
      console.error('获取规则分配信息失败:', error);
      message.error('获取规则分配信息失败');
    }
  };

  // 组件加载时获取数据
  useEffect(() => {
    fetchRules();
    fetchDepartments();
    fetchEmployees();
  }, []);

  /**
   * 处理表单提交
   * @param {Object} values - 表单值
   */
  const handleSubmit = async (values) => {
    try {
      // 确保所有日期字段都是正确的格式
      const formattedValues = {
        ...values,
        effective_start_date: values.effective_start_date ? dayjs(values.effective_start_date).format('YYYY-MM-DD') : null,
        effective_end_date: values.effective_end_date ? dayjs(values.effective_end_date).format('YYYY-MM-DD') : null,
        work_start_time: values.work_start_time ? dayjs(values.work_start_time).format('HH:mm') : null,
        work_end_time: values.work_end_time ? dayjs(values.work_end_time).format('HH:mm') : null,
        break_start_time: values.break_start_time ? dayjs(values.break_start_time).format('HH:mm') : null,
        break_end_time: values.break_end_time ? dayjs(values.break_end_time).format('HH:mm') : null,
      };

      if (currentRule) {
        // 更新规则
        await updateAttendanceRule(currentRule.id, formattedValues);
        message.success('考勤规则更新成功');
      } else {
        // 创建新规则
        await createAttendanceRule(formattedValues);
        message.success('考勤规则创建成功');
      }
      
      // 刷新列表并关闭对话框
      fetchRules();
      setModalVisible(false);
      form.resetFields();
    } catch (error) {
      console.error('提交表单失败:', error);
      message.error('操作失败: ' + (error.message || '未知错误'));
    }
  };

  /**
   * 处理删除规则
   * @param {string} id - 规则ID
   */
  const handleDelete = async (id) => {
    try {
      const response = await deleteAttendanceRule(id);
      if (response?.code === 200) {
        message.success('删除规则成功');
        fetchRules(); // 刷新列表
      } else {
        throw new Error(response?.msg || '删除规则失败');
      }
    } catch (error) {
      console.error('删除规则失败:', error);
      message.error(error.message);
    }
  };

  // 处理规则分配
  const handleAssign = (rule) => {
    setCurrentAssignRule(rule);
    assignForm.resetFields(); // 重置分配表单
    setAssignModalVisible(true);
  };

  // 处理分配表单提交
  const handleAssignSubmit = async (values) => {
    try {
      const { assignType, department_ids, employee_ids } = values;

      if (assignType === 'department' && department_ids?.length > 0) {
        // 分配给部门
        await assignRuleToDepartment(currentAssignRule.id, department_ids);
        message.success('规则分配成功');
      } else if (assignType === 'employee' && employee_ids?.length > 0) {
        // 分配给员工
        await assignRuleToEmployees(currentAssignRule.id, employee_ids);
        message.success('规则分配成功');
      } else {
        message.error('请选择分配对象');
        return;
      }

      // 关闭模态框并重置状态
      setAssignModalVisible(false);
      setCurrentAssignRule(null);
      assignForm.resetFields(); // 重置分配表单
      // 刷新规则列表
      fetchRules();
    } catch (error) {
      console.error('分配规则失败:', error);
      message.error('分配失败: ' + (error.message || '未知错误'));
    }
  };

  // 查看规则分配
  const handleViewAssignments = async (rule) => {
    setCurrentAssignRule(rule);
    await fetchRuleAssignments(rule.id);
    setAssignmentsModalVisible(true);
  };

  // 取消部门分配
  const handleUnassignDepartment = async (departmentId) => {
    try {
      await unassignRuleFromDepartment(currentAssignRule.id, departmentId);
      message.success('取消部门分配成功');
      // 只刷新分配信息
      await fetchRuleAssignments(currentAssignRule.id);
    } catch (error) {
      console.error('取消部门分配失败:', error);
      message.error('取消部门分配失败');
    }
  };

  // 取消员工分配
  const handleUnassignEmployee = async (employeeId) => {
    try {
      await unassignRuleFromEmployee(currentAssignRule.id, employeeId);
      message.success('取消员工分配成功');
      // 只刷新分配信息
      await fetchRuleAssignments(currentAssignRule.id);
    } catch (error) {
      console.error('取消员工分配失败:', error);
      message.error('取消员工分配失败');
    }
  };

  // 表格列定义
  const columns = [
    {
      title: '规则名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: '规则类型',
      dataIndex: 'rule_type',
      key: 'rule_type',
      width: 100,
      render: (type) => {
        const typeMap = {
          regular: '常规规则',
          special: '特殊规则',
          temporary: '临时规则'
        };
        return typeMap[type] || type;
      }
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      align: 'center',
      sorter: (a, b) => a.priority - b.priority
    },
    {
      title: '生效时间',
      key: 'effective_time',
      width: 200,
      render: (text, record) => {
        // 直接使用字符串拼接，不使用format方法
        let result = record.effective_start_date || '';
        if (record.effective_end_date) {
          result += ' 至 ' + record.effective_end_date;
        } else {
          result += ' 起';
        }
        return result;
      }
    },
    {
      title: '适用范围',
      key: 'scope',
      width: 180,
      render: (_, record) => (
        <span>
          {record.department_name ? '部门: ' + record.department_name : ''}
          {record.employee_count ? ', ' + record.employee_count + '名员工' : ''}
          {!record.department_name && !record.employee_count && '全局'}
        </span>
      )
    },
    {
      title: '工作时间',
      key: 'work_time',
      width: 180,
      render: (_, record) => (
        <span>
          {record.work_start_time} - {record.work_end_time}
          {record.break_start_time && record.break_end_time && 
            <div style={{ fontSize: '12px', color: '#666' }}>
              {'休息: ' + record.break_start_time + ' - ' + record.break_end_time}
            </div>
          }
        </span>
      )
    },
    {
      title: '考勤设置',
      key: 'attendance_settings',
      width: 200,
      render: (_, record) => (
        <div>
          <div>{'迟到: ' + record.late_threshold + '分钟'}</div>
          <div>{'早退: ' + record.early_leave_threshold + '分钟'}</div>
          <div>{'弹性: ' + record.flexible_time + '分钟'}</div>
        </div>
      )
    },
    {
      title: '加班设置',
      key: 'overtime_settings',
      width: 200,
      render: (_, record) => (
        <div>
          <div>{'最短时长: ' + record.overtime_minimum + '分钟'}</div>
          <div>{'工作日: ' + record.overtime_rate + '倍'}</div>
          <div>{'周末: ' + record.weekend_overtime_rate + '倍'}</div>
          <div>{'节假日: ' + record.holiday_overtime_rate + '倍'}</div>
        </div>
      )
    },
    {
      title: '是否默认',
      dataIndex: 'is_default',
      key: 'is_default',
      width: 80,
      align: 'center',
      render: (text) => text ? '是' : '否',
    },
    {
      title: '操作',
      key: 'action',
      fixed: 'right',
      width: 220,
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="primary"
            icon={<EditOutlined />}
            onClick={() => {
              setCurrentRule(record);
              setModalTitle('编辑考勤规则');

              // 设置表单值，不进行日期转换，让Form.Item的getValueProps处理转换
              form.setFieldsValue({
                ...record,
                work_start_time: record.work_start_time ? dayjs(record.work_start_time, 'HH:mm') : null,
                work_end_time: record.work_end_time ? dayjs(record.work_end_time, 'HH:mm') : null,
                break_start_time: record.break_start_time ? dayjs(record.break_start_time, 'HH:mm') : null,
                break_end_time: record.break_end_time ? dayjs(record.break_end_time, 'HH:mm') : null,
              });
              setModalVisible(true);
            }}
          >
            编辑
          </Button>
          <Button
            type="primary"
            icon={<ShareAltOutlined />}
            onClick={() => handleAssign(record)}
          >
            分配
          </Button>
          <Button
            onClick={() => handleViewAssignments(record)}
          >
            查看分配
          </Button>
          <Popconfirm
            title="确定要删除这条规则吗？"
            description="删除后将无法恢复"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="primary" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 分配模态框组件
  const AssignModal = () => (
    <Modal
      title="分配考勤规则"
      open={assignModalVisible}
      onCancel={() => {
        setAssignModalVisible(false);
        setCurrentAssignRule(null);
        assignForm.resetFields(); // 重置分配表单
      }}
      onOk={() => {
        assignForm.validateFields().then(handleAssignSubmit);
      }}
    >
      <Form 
        form={assignForm} 
        layout="vertical"
        initialValues={{
          assignType: 'department' // 设置默认分配类型
        }}
      >
        <Form.Item
          name="assignType"
          label="分配类型"
          rules={[{ required: true, message: '请选择分配类型' }]}
        >
          <Radio.Group>
            <Radio value="department">分配给部门</Radio>
            <Radio value="employee">分配给员工</Radio>
          </Radio.Group>
        </Form.Item>

        <Form.Item
          noStyle
          shouldUpdate={(prevValues, currentValues) => prevValues.assignType !== currentValues.assignType}
        >
          {({ getFieldValue }) =>
            getFieldValue('assignType') === 'department' ? (
              <Form.Item
                name="department_ids"
                label="选择部门"
                rules={[{ required: true, message: '请选择部门' }]}
              >
                <Select 
                  mode="multiple"
                  placeholder="请选择部门"
                  style={{ width: '100%' }}
                  optionFilterProp="children"
                >
                  {departments.map(dept => (
                    <Select.Option key={dept.id} value={dept.id}>
                      {dept.name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            ) : (
              <Form.Item
                name="employee_ids"
                label="选择员工"
                rules={[{ required: true, message: '请选择员工' }]}
              >
                <Select
                  mode="multiple"
                  placeholder="请选择员工"
                  style={{ width: '100%' }}
                  optionFilterProp="children"
                >
                  {employees.map(emp => (
                    <Select.Option key={emp.id} value={emp.id}>
                      {emp.name}
                    </Select.Option>
                  ))}
                </Select>
              </Form.Item>
            )
          }
        </Form.Item>
      </Form>
    </Modal>
  );

  // 分配详情模态框组件
  const AssignmentsModal = () => (
    <Modal
      title="考勤规则分配详情"
      open={assignmentsModalVisible}
      onCancel={() => {
        setAssignmentsModalVisible(false);
        // 关闭模态框时刷新规则列表
        fetchRules();
      }}
      footer={[
        <Button key="close" onClick={() => {
          setAssignmentsModalVisible(false);
          // 关闭模态框时刷新规则列表
          fetchRules();
        }}>
          关闭
        </Button>
      ]}
      afterClose={() => {
        // 清理状态
        setCurrentAssignRule(null);
        setCurrentAssignments(null);
      }}
    >
      {currentAssignments && (
        <div>
          <div style={{ marginBottom: 16 }}>
            <h3>部门分配</h3>
            {currentAssignments.departments.length > 0 ? (
              <List
                dataSource={currentAssignments.departments}
                renderItem={item => (
                  <List.Item
                    actions={[
                      <Popconfirm
                        title="确定要取消此部门的规则分配吗？"
                        onConfirm={() => handleUnassignDepartment(item.id)}
                      >
                        <Button type="link" danger>取消分配</Button>
                      </Popconfirm>
                    ]}
                  >
                    {item.name}
                  </List.Item>
                )}
              />
            ) : (
              <Empty description="暂无部门分配" />
            )}
          </div>
          <div>
            <h3>员工分配</h3>
            {currentAssignments.employees.length > 0 ? (
              <List
                dataSource={currentAssignments.employees}
                renderItem={item => (
                  <List.Item
                    actions={[
                      <Popconfirm
                        title="确定要取消此员工的规则分配吗？"
                        onConfirm={() => handleUnassignEmployee(item.id)}
                      >
                        <Button type="link" danger>取消分配</Button>
                      </Popconfirm>
                    ]}
                  >
                    <div>{item.name}</div>
                    <div style={{ color: '#999', fontSize: '12px' }}>{item.department_name}</div>
                  </List.Item>
                )}
              />
            ) : (
              <Empty description="暂无员工分配" />
            )}
          </div>
        </div>
      )}
    </Modal>
  );

  return (
    <div className="rules-container">
      <Card>
        <div style={{ marginBottom: 16 }}>
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => {
                setCurrentRule(null);
                setModalTitle('新增考勤规则');
                form.resetFields();
                setModalVisible(true);
              }}
            >
              新增规则
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={fetchRules}
            >
              刷新
            </Button>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={rules}
          loading={loading}
          rowKey="id"
          scroll={{ x: 1800 }}
          pagination={{
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => '共 ' + total + ' 条'
          }}
        />
      </Card>

      {/* 规则表单模态框 */}
      <Modal
        title={modalTitle}
        open={modalVisible}
        onOk={() => form.submit()}
        onCancel={() => {
          setModalVisible(false);
          form.resetFields();
        }}
        confirmLoading={submitting}
        width={800}
      >
        <Form
          form={form}
          onFinish={handleSubmit}
          layout="vertical"
        >
          <Form.Item
            name="name"
            label="规则名称"
            rules={[{ required: true, message: '请输入规则名称' }]}
          >
            <Input placeholder="请输入规则名称" />
          </Form.Item>

          <Form.Item
            name="rule_type"
            label="规则类型"
            rules={[{ required: true, message: '请选择规则类型' }]}
          >
            <Select>
              <Select.Option value="regular">常规规则</Select.Option>
              <Select.Option value="special">特殊规则</Select.Option>
              <Select.Option value="temporary">临时规则</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="priority"
            label="优先级"
            rules={[{ required: true, message: '请输入优先级' }]}
          >
            <InputNumber min={1} max={100} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="effective_start_date"
            label="生效开始日期"
            rules={[{ required: true, message: '请选择生效开始日期' }]}
            getValueProps={(value) => {
              // 如果value是字符串，转换为dayjs对象
              if (value && typeof value === 'string') {
                return { value: dayjs(value) };
              }
              return { value };
            }}
          >
            <DatePicker format="YYYY-MM-DD" placeholder="请选择生效开始日期" style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="effective_end_date"
            label="生效结束日期"
            getValueProps={(value) => {
              // 如果value是字符串，转换为dayjs对象
              if (value && typeof value === 'string') {
                return { value: dayjs(value) };
              }
              return { value };
            }}
          >
            <DatePicker format="YYYY-MM-DD" placeholder="请选择生效结束日期" style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="work_start_time"
            label="上班时间"
            rules={[{ required: true, message: '请选择上班时间' }]}
          >
            <TimePicker format="HH:mm" placeholder="请选择上班时间" style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="work_end_time"
            label="下班时间"
            rules={[{ required: true, message: '请选择下班时间' }]}
          >
            <TimePicker format="HH:mm" placeholder="请选择下班时间" style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="late_threshold"
            label="迟到阈值(分钟)"
            rules={[
              { required: true, message: '请输入迟到阈值' },
              { type: 'number', min: 0, message: '迟到阈值不能小于0' }
            ]}
          >
            <InputNumber min={0} placeholder="请输入迟到阈值" style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="early_leave_threshold"
            label="早退阈值(分钟)"
            rules={[
              { required: true, message: '请输入早退阈值' },
              { type: 'number', min: 0, message: '早退阈值不能小于0' }
            ]}
          >
            <InputNumber min={0} placeholder="请输入早退阈值" style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="flexible_time"
            label="弹性时间(分钟)"
            rules={[
              { required: true, message: '请输入弹性时间' },
              { type: 'number', min: 0, message: '弹性时间不能小于0' }
            ]}
          >
            <InputNumber min={0} placeholder="请输入弹性时间" style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="is_default"
            label="是否默认规则"
            valuePropName="checked"
            extra="每个部门只能设置一个默认规则"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="description"
            label="规则说明"
            rules={[
              { max: 200, message: '规则说明不能超过200个字符' }
            ]}
          >
            <Input.TextArea rows={4} placeholder="请输入规则说明" maxLength={200} showCount />
          </Form.Item>
        </Form>
      </Modal>

      <AssignModal />
      <AssignmentsModal />
    </div>
  );
};

export default Rules;
