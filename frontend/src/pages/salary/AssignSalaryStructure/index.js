import React, { useState, useEffect } from 'react';
import { Modal, Form, Input, InputNumber, Select, message, DatePicker, Radio } from 'antd';
import { assignSalaryStructure, getSalaryStructures } from '../../../services/salary';  
import { getEmployees } from '../../../services/employee';
import { getDepartments } from '../../../services/department';
import moment from 'moment';

const { Option } = Select;

/**
 * 工资结构分配组件
 * @param {Object} props - 组件属性
 * @param {boolean} props.visible - 是否显示模态框
 * @param {Function} props.onCancel - 取消回调函数
 * @param {Function} props.onSuccess - 成功回调函数
 */
const AssignSalaryStructure = ({ visible, onCancel, onSuccess }) => {
  const [form] = Form.useForm();
  const [employees, setEmployees] = useState([]); // 员工列表
  const [departments, setDepartments] = useState([]); // 部门列表
  const [structures, setStructures] = useState([]); // 工资结构列表
  const [assignType, setAssignType] = useState('employee'); // 分配类型：employee-员工, department-部门, default-默认
  const [selectedStructure, setSelectedStructure] = useState(null); // 选中的工资结构

  // 获取员工、部门和工资结构列表
  useEffect(() => {
    if (visible) {  
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

      // 获取工资结构列表
      getSalaryStructures().then(response => {
        if (response.code === 200) {
          const structureList = Array.isArray(response.data) ? response.data : [];
          setStructures(structureList);
        } else {
          message.error('获取工资结构列表失败：' + (response.msg || '未知错误'));
        }
      });
    }
  }, [visible]);

  // 处理工资结构选择
  const handleStructureSelect = (structureId) => {
    const structure = structures.find(s => s.id === structureId);
    if (structure) {
      setSelectedStructure(structure);
    }
  };

  // 处理分配类型变更
  const handleAssignTypeChange = (value) => {
    setAssignType(value);
    form.resetFields(['employee_id', 'department_id']);
  };

  // 处理表单提交
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      // 构建提交数据
      const submitData = {
        salary_structure_id: values.salary_structure_id,
        effective_date: values.effective_date.format('YYYY-MM-DD')
      };

      // 根据分配类型设置相应的字段
      if (values.assignType === 'employee') {
        submitData.employee_id = values.employee_id;
      } else if (values.assignType === 'department') {
        submitData.department_id = values.department_id;
      } else if (values.assignType === 'default') {
        submitData.is_default = true;
      }

      // 调用分配API
      const response = await assignSalaryStructure(submitData);
      if (response.code === 200) {
        message.success('工资结构分配成功');
        form.resetFields();
        onSuccess();
      } else {
        message.error(response.msg || '工资结构分配失败');
      }
    } catch (error) {
      console.error('表单验证失败:', error);
    }
  };

  // 模态框关闭时重置表单
  const handleCancel = () => {
    form.resetFields();
    setSelectedStructure(null);
    onCancel();
  };

  return (
    <Modal
      title="分配工资结构"
      open={visible}
      onCancel={handleCancel}
      onOk={handleSubmit}
      width={600}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          assignType: 'employee',
          effective_date: moment(),
        }}
      >
        {/* 选择工资结构 */}
        <Form.Item
          name="salary_structure_id"
          label="选择工资结构"
          rules={[{ required: true, message: '请选择工资结构' }]}
        >
          <Select
            placeholder="请选择工资结构"
            onChange={handleStructureSelect}
            showSearch
            optionFilterProp="children"
          >
            {structures.map(structure => (
              <Option key={structure.id} value={structure.id}>{structure.name}</Option>
            ))}
          </Select>
        </Form.Item>

        {/* 显示选中的工资结构信息 */}
        {selectedStructure && (
          <div style={{ marginBottom: 24 }}>
            <h4>工资结构详情：</h4>
            <p>名称：{selectedStructure.name}</p>
            <p>描述：{selectedStructure.description || '无'}</p>
            <p>基本工资：¥{selectedStructure.basic_salary}</p>
            <p>住房补贴：¥{selectedStructure.housing_allowance}</p>
            <p>交通补贴：¥{selectedStructure.transport_allowance}</p>
            <p>餐饮补贴：¥{selectedStructure.meal_allowance}</p>
          </div>
        )}

        {/* 分配类型 */}
        <Form.Item
          name="assignType"
          label="分配类型"
          rules={[{ required: true, message: '请选择分配类型' }]}
        >
          <Radio.Group onChange={e => handleAssignTypeChange(e.target.value)}>
            <Radio value="employee">分配给员工（优先级最高）</Radio>
            <Radio value="department">部门默认（优先级中等）</Radio>
            <Radio value="default">全局默认（优先级最低）</Radio>
          </Radio.Group>
        </Form.Item>

        {/* 分配类型说明 */}
        <div style={{ marginBottom: 16, color: '#666' }}>
          <p>工资结构分配优先级说明：</p>
          <ol>
            <li>员工专属工资结构：针对特定员工的个性化工资结构，优先级最高</li>
            <li>部门工资结构：适用于部门内所有未设置专属工资结构的员工</li>
            <li>全局默认工资结构：适用于未设置专属或部门工资结构的所有员工</li>
          </ol>
        </div>

        {/* 选择员工 */}
        {assignType === 'employee' && (
          <Form.Item
            name="employee_id"
            label="选择员工"
            rules={[{ required: true, message: '请选择员工' }]}
          >
            <Select
              placeholder="请选择员工"
              showSearch
              optionFilterProp="children"
            >
              {employees.map(employee => (
                <Option key={employee.id} value={employee.id}>
                  {employee.name} - {employee.department?.name || '未分配部门'}
                </Option>
              ))}
            </Select>
          </Form.Item>
        )}

        {/* 选择部门 */}
        {assignType === 'department' && (
          <Form.Item
            name="department_id"
            label="选择部门"
            rules={[{ required: true, message: '请选择部门' }]}
            help="将作为该部门的默认工资结构"
          >
            <Select
              placeholder="请选择部门"
              showSearch
              optionFilterProp="children"
            >
              {departments.map(department => (
                <Option key={department.id} value={department.id}>{department.name}</Option>
              ))}
            </Select>
          </Form.Item>
        )}

        {/* 生效日期 */}
        <Form.Item
          name="effective_date"
          label="生效日期"
          rules={[{ required: true, message: '请选择生效日期' }]}
        >
          <DatePicker style={{ width: '100%' }} />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default AssignSalaryStructure;
