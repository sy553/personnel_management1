import React, { useState, useEffect, useCallback } from 'react';
import { Form, Input, Select, Button, Row, Col, Modal, message, DatePicker, List, Space, Radio, Divider, Card, Badge, Tag, Upload } from 'antd';
import { UploadOutlined, DeleteOutlined, UserOutlined, PlusOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import {
  createEmployee,
  updateEmployee,
  uploadPhoto,
  uploadContract,
  getEducationHistory,
  getWorkHistory,
  createEducationHistory,
  createWorkHistory,
  deleteEducationHistory,
  deleteWorkHistory,
  getEmployeeContracts
} from '../../services/employee';
import FileUpload from './components/FileUpload';
import ContractUpload from './components/ContractUpload';
import './EmployeeForm.less';

const { Option } = Select;

const EmployeeForm = ({ open, onCancel, onSuccess, employee, departments, positions }) => {
  // 创建表单实例
  const [mainForm] = Form.useForm();
  const [educationForm] = Form.useForm();
  const [workForm] = Form.useForm();
  
  // 组件状态
  const [loading, setLoading] = useState(false);
  const [educationVisible, setEducationVisible] = useState(false);
  const [workVisible, setWorkVisible] = useState(false);
  const [educationHistory, setEducationHistory] = useState([]);
  const [workHistory, setWorkHistory] = useState([]);
  const [photoUrl, setPhotoUrl] = useState('');
  const [contractInfo, setContractInfo] = useState(null);
  const isEdit = !!employee;

  // 处理日期格式化
  const formatDate = useCallback((dateStr) => {
    if (!dateStr) return null;
    const date = dayjs(dateStr);
    return date.$d instanceof Date && !isNaN(date.$d) ? date : null;
  }, []);

  // 格式化日期为字符串
  const formatDateToString = useCallback((date) => {
    if (!date) return null;
    const parsedDate = dayjs.isDayjs(date) ? date : dayjs(date);
    return parsedDate.$d instanceof Date && !isNaN(parsedDate.$d) 
      ? parsedDate.format('YYYY-MM-DD') 
      : null;
  }, []);

  // 加载教育经历
  const loadEducationHistory = useCallback(async (employeeId) => {
    try {
      const response = await getEducationHistory(employeeId);
      if (response.code === 200) {
        const historyData = response.data || [];
        setEducationHistory(historyData.map(item => ({
          ...item,
          start_date: formatDate(item.start_date),
          end_date: formatDate(item.end_date)
        })));
      } else {
        setEducationHistory([]);
      }
    } catch (error) {
      console.error('加载教育经历失败:', error);
      message.error('加载教育经历失败');
      setEducationHistory([]);
    }
  }, [formatDate]);

  // 加载工作经历
  const loadWorkHistory = useCallback(async (employeeId) => {
    try {
      const response = await getWorkHistory(employeeId);
      if (response.code === 200) {
        const historyData = response.data || [];
        setWorkHistory(historyData.map(item => ({
          ...item,
          start_date: formatDate(item.start_date),
          end_date: formatDate(item.end_date)
        })));
      } else {
        setWorkHistory([]);
      }
    } catch (error) {
      console.error('加载工作经历失败:', error);
      message.error('加载工作经历失败');
      setWorkHistory([]);
    }
  }, [formatDate]);

  // 加载合同信息
  const loadContractInfo = useCallback(async (employeeId) => {
    try {
      const response = await getEmployeeContracts(employeeId);
      if (response.code === 200 && response.data && response.data.length > 0) {
        const latestContract = response.data[0];
        setContractInfo(latestContract);
        mainForm.setFieldValue('contract_info', latestContract);
      }
    } catch (error) {
      console.error('加载合同信息失败:', error);
    }
  }, [mainForm]);

  // 在组件挂载时初始化表单
  useEffect(() => {
    const initializeForm = () => {
      if (!open) {
        if (mainForm && educationForm && workForm) {
          try {
            mainForm.resetFields();
            educationForm.resetFields();
            workForm.resetFields();
            setPhotoUrl('');
            setEducationHistory([]);
            setWorkHistory([]);
            setContractInfo(null);
          } catch (error) {
            console.error('重置表单失败:', error);
          }
        }
      } else if (employee) {
        const formData = {
          ...employee,
          birth_date: employee.birth_date ? dayjs(employee.birth_date) : null,
          hire_date: employee.hire_date ? dayjs(employee.hire_date) : null,
          resignation_date: employee.resignation_date ? dayjs(employee.resignation_date) : null,
          department_id: employee.department_id?.toString(),
          position_id: employee.position_id?.toString(),
        };

        if (mainForm) {
          try {
            mainForm.setFieldsValue(formData);
          } catch (error) {
            console.error('设置表单值失败:', error);
          }
        }

        if (employee.photo_url) {
          setPhotoUrl(employee.photo_url.startsWith('http') 
            ? employee.photo_url 
            : `${process.env.REACT_APP_API_BASE_URL}${employee.photo_url}`);
        }

        if (employee.id) {
          loadEducationHistory(employee.id);
          loadWorkHistory(employee.id);
          loadContractInfo(employee.id);
        }
      }
    };

    const frameId = requestAnimationFrame(initializeForm);
    return () => cancelAnimationFrame(frameId);
  }, [open, employee, mainForm, educationForm, workForm, loadEducationHistory, loadWorkHistory, loadContractInfo]);

  // 处理照片上传
  const handlePhotoUpload = async (formData) => {
    try {
      const response = await uploadPhoto(formData, employee?.id);
      console.log('Upload photo response:', response);

      if (response?.code === 200 && response.data?.photo_url) {
        mainForm.setFieldValue('photo_url', response.data.photo_url);
        
        return {
          photo_url: response.data.photo_url
        };
      }
      
      const errorMsg = response?.message || '上传失败';
      console.error('Upload failed:', errorMsg);
      throw new Error(errorMsg);
    } catch (error) {
      console.error('上传照片失败:', error);
      message.error(error.message || '上传照片失败');
      throw error;
    }
  };

  // 处理表单提交
  const handleSubmit = async (values) => {
    try {
      setLoading(true);
      const formData = {
        ...values,
        birth_date: values.birth_date ? dayjs(values.birth_date).format('YYYY-MM-DD') : null,
        hire_date: values.hire_date ? dayjs(values.hire_date).format('YYYY-MM-DD') : null,
        resignation_date: values.resignation_date ? dayjs(values.resignation_date).format('YYYY-MM-DD') : null,
        department_id: values.department_id ? parseInt(values.department_id) : null,
        position_id: values.position_id ? parseInt(values.position_id) : null,
        photo_url: values.photo_url || null  
      };

      console.log('提交的表单数据:', formData);

      if (isEdit) {
        const response = await updateEmployee(employee.id, formData);
        if (response.code === 200) {
          message.success('员工信息更新成功');
          if (employee.employment_status !== formData.employment_status) {
            onSuccess(true); 
          } else {
            onSuccess(false); 
          }
          onCancel();
        } else {
          message.error(response.msg || '更新失败');
        }
      } else {
        const response = await createEmployee(formData);
        if (response.code === 200) {
          message.success('员工添加成功');
          onSuccess(true); 
          onCancel();
        } else {
          message.error(response.msg || '添加失败');
        }
      }
    } catch (error) {
      console.error('提交表单失败:', error);
      message.error('操作失败');
    } finally {
      setLoading(false);
    }
  };

  // 处理合同上传
  const handleContractUpload = async (formData) => {
    try {
      const employeeId = employee?.id;
      const response = await uploadContract(formData, employeeId);
      
      if (response.code === 200 && response.data) {
        setContractInfo(response.data);
        mainForm.setFieldValue('contract_info', response.data);
        message.success('合同上传成功');
      }
      
      return response;
    } catch (error) {
      console.error('合同上传错误:', error);
      throw error;
    }
  };

  // 添加教育经历
  const handleAddEducation = async () => {
    try {
      const values = await educationForm.validateFields();
      const [startDate, endDate] = values.date_range;
      
      if (isEdit) {
        const educationData = {
          school: values.school,
          major: values.major,
          degree: values.degree,
          start_date: startDate.format('YYYY-MM'),
          end_date: endDate.format('YYYY-MM')
        };
        
        await createEducationHistory(employee.id, educationData);
        message.success('添加教育经历成功');
        loadEducationHistory(employee.id);
      } else {
        setEducationHistory(prev => [...prev, {
          id: `temp_${Date.now()}`,
          school: values.school,
          major: values.major,
          degree: values.degree,
          start_date: startDate,
          end_date: endDate
        }]);
        message.success('添加教育经历成功');
      }
      
      setEducationVisible(false);
      educationForm.resetFields();
    } catch (error) {
      console.error('添加教育经历失败:', error);
      message.error('添加教育经历失败');
    }
  };

  // 添加工作经历
  const handleAddWork = async () => {
    try {
      const values = await workForm.validateFields();
      const [startDate, endDate] = values.date_range;
      
      if (isEdit) {
        const workData = {
          company: values.company,
          position: values.position,
          start_date: startDate.format('YYYY-MM'),
          end_date: endDate.format('YYYY-MM')
        };
        
        await createWorkHistory(employee.id, workData);
        message.success('添加工作经历成功');
        loadWorkHistory(employee.id);
      } else {
        setWorkHistory(prev => [...prev, {
          id: `temp_${Date.now()}`,
          company: values.company,
          position: values.position,
          start_date: startDate,
          end_date: endDate
        }]);
        message.success('添加工作经历成功');
      }
      
      setWorkVisible(false);
      workForm.resetFields();
    } catch (error) {
      console.error('添加工作经历失败:', error);
      message.error('添加工作经历失败');
    }
  };

  // 删除教育经历
  const handleDeleteEducation = async (id) => {
    try {
      if (isEdit) {
        await deleteEducationHistory(id);
        message.success('删除教育经历成功');
        loadEducationHistory(employee.id);
      } else {
        setEducationHistory(prev => prev.filter(item => item.id !== id));
        message.success('删除教育经历成功');
      }
    } catch (error) {
      console.error('删除教育经历失败:', error);
      message.error('删除教育经历失败');
    }
  };

  // 删除工作经历
  const handleDeleteWork = async (id) => {
    try {
      if (isEdit) {
        await deleteWorkHistory(id);
        message.success('删除工作经历成功');
        loadWorkHistory(employee.id);
      } else {
        setWorkHistory(prev => prev.filter(item => item.id !== id));
        message.success('删除工作经历成功');
      }
    } catch (error) {
      console.error('删除工作经历失败:', error);
      message.error('删除工作经历失败');
    }
  };

  const renderMainForm = () => (
    <Form
      form={mainForm}
      layout="vertical"
      onFinish={handleSubmit}
      initialValues={{
        employment_status: 'active',
        gender: 'male'
      }}
      preserve={false}
    >
      <div className="form-section">
        <div className="section-title">基本信息</div>
        <Row gutter={24}>
          <Col span={18}>
            <Row gutter={16}>
              <Col span={12}>
                <Form.Item
                  name="employee_id"
                  label="工号"
                  rules={[{ required: true, message: '请输入工号' }]}
                >
                  <Input placeholder="请输入工号" />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item
                  name="name"
                  label="姓名"
                  rules={[{ required: true, message: '请输入姓名' }]}
                >
                  <Input placeholder="请输入姓名" />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={16}>
              <Col span={8}>
                <Form.Item
                  name="gender"
                  label="性别"
                  rules={[{ required: true, message: '请选择性别' }]}
                >
                  <Radio.Group>
                    <Radio value="male">男</Radio>
                    <Radio value="female">女</Radio>
                  </Radio.Group>
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="birth_date"
                  label="出生日期"
                  getValueProps={(i) => ({
                    value: i ? dayjs(i) : null
                  })}
                >
                  <DatePicker 
                    style={{ width: '100%' }} 
                    format="YYYY-MM-DD"
                  />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item
                  name="education"
                  label="学历"
                >
                  <Select placeholder="请选择学历">
                    <Option value="高中">高中</Option>
                    <Option value="专科">专科</Option>
                    <Option value="本科">本科</Option>
                    <Option value="硕士">硕士</Option>
                    <Option value="博士">博士</Option>
                  </Select>
                </Form.Item>
              </Col>
            </Row>
          </Col>
          <Col span={6}>
            <Form.Item label="照片">
              <FileUpload
                accept="image/*"
                imageMode={true}
                value={photoUrl}
                uploadAction={handlePhotoUpload}
                maxSize={5}
                tip="点击或拖拽上传照片"
                defaultIcon={<UserOutlined />}
              />
            </Form.Item>
          </Col>
        </Row>
      </div>

      <div className="form-section">
        <div className="section-title">联系方式</div>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="phone"
              label="手机号码"
              rules={[
                { required: true, message: '请输入手机号码' },
                { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码' }
              ]}
            >
              <Input placeholder="请输入手机号码" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="id_card"
              label="身份证号"
              rules={[
                { required: true, message: '请输入身份证号' },
                { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号' }
              ]}
            >
              <Input placeholder="请输入身份证号" />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item
          name="address"
          label="住址"
        >
          <Input.TextArea placeholder="请输入住址" rows={2} />
        </Form.Item>
      </div>

      <div className="form-section">
        <div className="section-title">工作信息</div>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="department"
              label="所属部门"
              rules={[{ required: true, message: '请选择部门' }]}
            >
              <Select placeholder="请选择部门">
                {departments.map(dept => (
                  <Option key={dept.id} value={dept.id}>{dept.name}</Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="position"
              label="职位"
              rules={[{ required: true, message: '请选择职位' }]}
            >
              <Select placeholder="请选择职位">
                {positions.map(pos => (
                  <Option key={pos.id} value={pos.id}>{pos.name}</Option>
                ))}
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="hire_date"
              label="入职日期"
              getValueProps={(i) => ({
                value: i ? dayjs(i) : null
              })}
            >
              <DatePicker 
                style={{ width: '100%' }} 
                format="YYYY-MM-DD"
              />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="employment_status"
              label="在职状态"
              rules={[{ required: true, message: '请选择在职状态' }]}
            >
              <Select>
                <Option value="active">在职</Option>
                <Option value="suspended">休假</Option>
                <Option value="resigned">离职</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item
              name="resignation_date"
              label="离职日期"
              getValueProps={(i) => ({
                value: i ? dayjs(i) : null
              })}
            >
              <DatePicker 
                style={{ width: '100%' }} 
                format="YYYY-MM-DD"
              />
            </Form.Item>
          </Col>
        </Row>
      </div>

      <Card title="教育经历" className="info-card">
        <List
          size="small"
          dataSource={educationHistory}
          renderItem={item => (
            <List.Item
              actions={[
                <Button
                  type="link"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => handleDeleteEducation(item.id)}
                >
                  删除
                </Button>
              ]}
            >
              <List.Item.Meta
                title={
                  <Space>
                    <span>{item.school}</span>
                    <Divider type="vertical" />
                    <span>{item.major}</span>
                    <Tag color="blue">{item.degree}</Tag>
                  </Space>
                }
                description={`${dayjs(item.start_date).format('YYYY-MM')} 至 ${dayjs(item.end_date).format('YYYY-MM')}`}
              />
            </List.Item>
          )}
          footer={
            <Button type="dashed" icon={<PlusOutlined />} onClick={() => setEducationVisible(true)} block>
              添加教育经历
            </Button>
          }
        />
      </Card>

      <Card title="工作经历" className="info-card">
        <List
          size="small"
          dataSource={workHistory}
          renderItem={item => (
            <List.Item
              actions={[
                <Button
                  type="link"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => handleDeleteWork(item.id)}
                >
                  删除
                </Button>
              ]}
            >
              <List.Item.Meta
                title={
                  <Space>
                    <span>{item.company}</span>
                    <Divider type="vertical" />
                    <span>{item.position}</span>
                  </Space>
                }
                description={`${dayjs(item.start_date).format('YYYY-MM')} 至 ${dayjs(item.end_date).format('YYYY-MM')}`}
              />
            </List.Item>
          )}
          footer={
            <Button type="dashed" icon={<PlusOutlined />} onClick={() => setWorkVisible(true)} block>
              添加工作经历
            </Button>
          }
        />
      </Card>

      <Card title="合同附件" className="info-card">
        <ContractUpload
          value={contractInfo}
          onChange={(info) => {
            setContractInfo(info);
            mainForm.setFieldValue('contract_info', info);
          }}
          uploadAction={handleContractUpload}
        />
      </Card>
    </Form>
  );

  const renderEducationForm = () => (
    <Modal
      open={educationVisible}
      title="添加教育经历"
      onCancel={() => {
        setEducationVisible(false);
        if (educationForm) {
          try {
            educationForm.resetFields();
          } catch (error) {
            console.error('重置教育经历表单失败:', error);
          }
        }
      }}
      footer={null}
      styles={{ 
        body: { padding: '20px' },
        mask: { backgroundColor: 'rgba(0, 0, 0, 0.45)' },
        content: { borderRadius: '8px' }
      }}
      destroyOnClose
    >
      <Form
        form={educationForm}
        layout="vertical"
        onFinish={handleAddEducation}
        preserve={false}
      >
        <Form.Item
          name="school"
          label="学校"
          rules={[{ required: true, message: '请输入学校名称' }]}
        >
          <Input placeholder="请输入学校名称" />
        </Form.Item>
        <Form.Item
          name="major"
          label="专业"
          rules={[{ required: true, message: '请输入专业' }]}
        >
          <Input placeholder="请输入专业" />
        </Form.Item>
        <Form.Item
          name="degree"
          label="学位"
          rules={[{ required: true, message: '请选择学位' }]}
        >
          <Select placeholder="请选择学位">
            <Option value="高中">高中</Option>
            <Option value="专科">专科</Option>
            <Option value="本科">本科</Option>
            <Option value="硕士">硕士</Option>
            <Option value="博士">博士</Option>
          </Select>
        </Form.Item>
        <Form.Item
          name="date_range"
          label="起止时间"
          rules={[{ required: true, message: '请选择起止时间' }]}
        >
          <DatePicker.RangePicker style={{ width: '100%' }} picker="month" />
        </Form.Item>
      </Form>
    </Modal>
  );

  const renderWorkForm = () => (
    <Modal
      open={workVisible}
      title="添加工作经历"
      onCancel={() => {
        setWorkVisible(false);
        if (workForm) {
          try {
            workForm.resetFields();
          } catch (error) {
            console.error('重置工作经历表单失败:', error);
          }
        }
      }}
      footer={null}
      styles={{ 
        body: { padding: '20px' },
        mask: { backgroundColor: 'rgba(0, 0, 0, 0.45)' },
        content: { borderRadius: '8px' }
      }}
      destroyOnClose
    >
      <Form
        form={workForm}
        layout="vertical"
        onFinish={handleAddWork}
        preserve={false}
      >
        <Form.Item
          name="company"
          label="公司"
          rules={[{ required: true, message: '请输入公司名称' }]}
        >
          <Input placeholder="请输入公司名称" />
        </Form.Item>
        <Form.Item
          name="position"
          label="职位"
          rules={[{ required: true, message: '请输入职位' }]}
        >
          <Input placeholder="请输入职位" />
        </Form.Item>
        <Form.Item
          name="date_range"
          label="起止时间"
          rules={[{ required: true, message: '请选择起止时间' }]}
        >
          <DatePicker.RangePicker style={{ width: '100%' }} picker="month" />
        </Form.Item>
      </Form>
    </Modal>
  );

  return (
    <Modal
      title={isEdit ? '编辑员工' : '添加员工'}
      open={open}
      onCancel={onCancel}
      footer={[
        <Button key="back" onClick={onCancel}>
          取消
        </Button>,
        <Button
          key="submit"
          type="primary"
          loading={loading}
          onClick={() => mainForm.submit()}
        >
          {isEdit ? '更新' : '添加'}
        </Button>
      ]}
      width={1000}
      destroyOnClose
      styles={{
        body: { maxHeight: '70vh', overflow: 'auto' }
      }}
    >
      <React.Fragment>
        {renderMainForm()}
        {renderEducationForm()}
        {renderWorkForm()}
      </React.Fragment>
    </Modal>
  );
};

export default EmployeeForm;
