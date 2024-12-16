import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Card, 
  Descriptions, 
  Button, 
  Space, 
  message, 
  Skeleton,
  Tabs,
  Timeline,
  Upload,
  Table,
  Form,
  Input,
  DatePicker,
  Modal,
  Select,
  Row,
  Col,
  Statistic,
  Rate,
  Switch,
  InputNumber
} from 'antd';
import { 
  ArrowLeftOutlined,
  EditOutlined,
  UserOutlined,
  SolutionOutlined,
  TeamOutlined,
  UploadOutlined,
  PlusOutlined,
  ReadOutlined,
  BriefcaseOutlined,
  SwapOutlined,
  PrinterOutlined
} from '@ant-design/icons';
import moment from 'moment';
import { 
  getEmployee, 
  getDepartments, 
  getPositions,
  getEducationHistory,
  getWorkHistory,
  getPositionChanges,
  addEducationHistory,
  addWorkHistory,
  addPositionChange
} from '../../services/employee';
import { getAttachments } from '../../services/upload';
import EmployeeForm from './EmployeeForm';
import ContractList from './components/ContractList';
// 样式导入
import './Employee.css';
import './styles/employee-detail.css';  // 添加详情页专用样式
import './styles/print.css';  // 打印样式

const { TabPane } = Tabs;
const { TextArea } = Input;
const { Option } = Select;

const EmployeeDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  
  // 状态定义
  const [employee, setEmployee] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [educationHistory, setEducationHistory] = useState([]);
  const [workHistory, setWorkHistory] = useState([]);
  const [positionChanges, setPositionChanges] = useState([]);
  const [attachments, setAttachments] = useState([]);
  const [addEducationModalVisible, setAddEducationModalVisible] = useState(false);
  const [addWorkModalVisible, setAddWorkModalVisible] = useState(false);
  const [addPositionChangeModalVisible, setAddPositionChangeModalVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('1'); // 新增：当前激活的标签页
  const [photoLoading, setPhotoLoading] = useState(false); // 新增：照片上传loading状态
  const [internEvaluationModalVisible, setInternEvaluationModalVisible] = useState(false);
  const [evaluationForm] = Form.useForm();
  const [evaluationHistory, setEvaluationHistory] = useState([]);

  // 获取所有数据
  const fetchAllData = useCallback(async () => {
    try {
      // 检查认证状态
      const token = localStorage.getItem('token');
      if (!token) {
        message.error('登录已过期，请重新登录');
        navigate('/login');
        return;
      }

      setLoading(true);
      const [
        employeeRes,
        educationRes,
        workRes,
        positionChangesRes,
        attachmentsRes,
        departmentsRes,
        positionsRes
      ] = await Promise.all([
        getEmployee(id),
        getEducationHistory(id),
        getWorkHistory(id),
        getPositionChanges(id),
        getAttachments(id),
        getDepartments(),
        getPositions()
      ]);

      if (employeeRes.code === 200 && employeeRes.data) {
        setEmployee(employeeRes.data);
      } else {
        message.error(employeeRes.msg || '获取员工信息失败');
        return;
      }

      // 处理其他响应数据
      if (educationRes.code === 200) setEducationHistory(educationRes.data || []);
      if (workRes.code === 200) setWorkHistory(workRes.data || []);
      if (positionChangesRes.code === 200) setPositionChanges(positionChangesRes.data || []);
      if (attachmentsRes.code === 200) setAttachments(attachmentsRes.data || []);
      if (departmentsRes.code === 200) setDepartments(departmentsRes.data || []);
      if (positionsRes.code === 200) setPositions(positionsRes.data || []);
      
    } catch (error) {
      console.error('获取数据失败:', error);
      if (error.response?.status === 401) {
        message.error('登录已过期，请重新登录');
        navigate('/login');
      } else {
        message.error('获取数据失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // 处理照片上传
  const handlePhotoUpload = async (file) => {
    try {
      setPhotoLoading(true);
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/employees/upload/photo/${id}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      const result = await response.json();
      if (response.ok && result.code === 200) {
        message.success('照片上传成功');
        await checkAndUpdatePhoto();
      } else {
        message.error(result.msg || '上传失败');
      }
    } catch (error) {
      console.error('Error uploading photo:', error);
      message.error('上传失败，请稍后重试');
    } finally {
      setPhotoLoading(false);
    }
    return false;
  };

  const checkAndUpdatePhoto = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/employees/check_photo/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      const result = await response.json();
      if (response.ok && result.code === 200) {
        // 照片存在，更新员工信息
        fetchEmployeeData();
      } else {
        // 照片不存在，显示默认头像
        setEmployee(prev => ({
          ...prev,
          photo_url: null
        }));
        message.warning('照片文件不存在，将显示默认头像');
      }
    } catch (error) {
      console.error('Error checking photo:', error);
      message.error('检查照片失败');
    }
  };

  // 在组件加载时检查照片
  useEffect(() => {
    if (employee?.photo_url) {
      checkAndUpdatePhoto();
    }
  }, [employee?.photo_url]);

  // 处理合同附件上传
  const handleContractUpload = {
    name: 'file',
    action: `/api/upload/contract?employee_id=${id}`,
    headers: {
      authorization: 'authorization-text',
    },
    onChange(info) {
      if (info.file.status === 'done') {
        message.success(`${info.file.name} 上传成功`);
        fetchAllData(); // 刷新数据
      } else if (info.file.status === 'error') {
        message.error(`${info.file.name} 上传失败`);
      }
    },
  };

  // 添加教育经历
  const handleAddEducation = async (values) => {
    try {
      await addEducationHistory(id, {
        ...values,
        start_date: values.start_date.format('YYYY-MM-DD'),
        end_date: values.end_date?.format('YYYY-MM-DD')
      });
      message.success('添加教育经历成功');
      setAddEducationModalVisible(false);
      form.resetFields();
      fetchAllData();
    } catch (error) {
      message.error('添加教育经历失败');
    }
  };

  // 添加工作经历
  const handleAddWork = async (values) => {
    try {
      await addWorkHistory(id, {
        ...values,
        start_date: values.start_date.format('YYYY-MM-DD'),
        end_date: values.end_date?.format('YYYY-MM-DD')
      });
      message.success('添加工作经历成功');
      setAddWorkModalVisible(false);
      form.resetFields();
      fetchAllData();
    } catch (error) {
      message.error('添加工作经历失败');
    }
  };

  // 添加调岗记录
  const handleAddPositionChange = async (values) => {
    try {
      await addPositionChange(id, {
        ...values,
        change_date: values.change_date.format('YYYY-MM-DD')
      });
      message.success('添加调岗记录成功');
      setAddPositionChangeModalVisible(false);
      form.resetFields();
      fetchAllData();
    } catch (error) {
      message.error('添加调岗记录失败');
    }
  };

  // 渲染照片上传
  const renderPhotoUpload = () => (
    <div className="photo-upload">
      <Upload 
        beforeUpload={file => {
          const isImage = file.type.startsWith('image/');
          if (!isImage) {
            message.error('只能上传图片文件!');
            return false;
          }
          const isLt2M = file.size / 1024 / 1024 < 2;
          if (!isLt2M) {
            message.error('图片大小不能超过2MB!');
            return false;
          }
          return true;
        }}
        customRequest={handlePhotoUpload}
        onChange={info => {
          if (info.file.status === 'uploading') {
            // 可以在这里添加上传中的状态处理
          }
        }}
      >
        <Button icon={<UploadOutlined />}>上传照片</Button>
      </Upload>
      {employee?.photo_url && (
        <img 
          src={`http://localhost:5000${employee.photo_url}`}
          alt="员工照片" 
          style={{ maxWidth: 200, marginTop: 16 }} 
        />
      )}
    </div>
  );

  // 渲染教育经历表格
  const renderEducationHistory = () => {
    const columns = [
      { title: '学校', dataIndex: 'school', key: 'school' },
      { title: '专业', dataIndex: 'major', key: 'major' },
      { title: '学历', dataIndex: 'degree', key: 'degree' },
      { 
        title: '起止时间', 
        key: 'time',
        render: (_, record) => (
          `${record.start_date} ~ ${record.end_date || '至今'}`
        )
      }
    ];

    return (
      <div>
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={() => setAddEducationModalVisible(true)}
          style={{ marginBottom: 16 }}
        >
          添加教育经历
        </Button>
        <Table 
          columns={columns} 
          dataSource={educationHistory} 
          rowKey="id"
        />
      </div>
    );
  };

  // 渲染工作经历表格
  const renderWorkHistory = () => {
    const columns = [
      { title: '公司', dataIndex: 'company', key: 'company' },
      { title: '职位', dataIndex: 'position', key: 'position' },
      { 
        title: '起止时间', 
        key: 'time',
        render: (_, record) => (
          `${record.start_date} ~ ${record.end_date || '至今'}`
        )
      },
      { title: '工作描述', dataIndex: 'description', key: 'description' }
    ];

    return (
      <div>
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={() => setAddWorkModalVisible(true)}
          style={{ marginBottom: 16 }}
        >
          添加工作经历
        </Button>
        <Table 
          columns={columns} 
          dataSource={workHistory} 
          rowKey="id"
        />
      </div>
    );
  };

  // 渲染调岗历史表格
  const renderPositionChanges = () => {
    const columns = [
      { 
        title: '原部门', 
        key: 'old_department',
        render: (_, record) => record.old_department_name || '-'
      },
      { 
        title: '新部门', 
        key: 'new_department',
        render: (_, record) => record.new_department_name
      },
      { 
        title: '原职位', 
        key: 'old_position',
        render: (_, record) => record.old_position_name || '-'
      },
      { 
        title: '新职位', 
        key: 'new_position',
        render: (_, record) => record.new_position_name
      },
      { title: '调岗日期', dataIndex: 'change_date', key: 'change_date' },
      { title: '调岗原因', dataIndex: 'change_reason', key: 'change_reason' }
    ];

    return (
      <div>
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={() => setAddPositionChangeModalVisible(true)}
          style={{ marginBottom: 16 }}
        >
          添加调岗记录
        </Button>
        <Table 
          columns={columns} 
          dataSource={positionChanges} 
          rowKey="id"
        />
      </div>
    );
  };

  // 渲染合同附件表格
  const renderAttachments = () => {
    const columns = [
      { title: '文件名', dataIndex: 'file_name', key: 'file_name' },
      { title: '文件类型', dataIndex: 'file_type', key: 'file_type' },
      { 
        title: '上传时间', 
        dataIndex: 'upload_time', 
        key: 'upload_time',
        render: (text) => moment(text).format('YYYY-MM-DD HH:mm:ss')
      },
      {
        title: '操作',
        key: 'action',
        render: (_, record) => (
          <a href={record.file_url} target="_blank" rel="noopener noreferrer">
            下载
          </a>
        )
      }
    ];

    return (
      <div>
        <Upload
          name="file"
          action={`http://localhost:5000/api/employees/upload/contract/${id}`}
          headers={{
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }}
          beforeUpload={file => {
            const isValidType = ['.pdf', '.doc', '.docx'].some(ext => 
              file.name.toLowerCase().endsWith(ext)
            );
            if (!isValidType) {
              message.error('只能上传 PDF、DOC、DOCX 格式的文件！');
              return false;
            }
            return true;
          }}
          onChange={info => {
            if (info.file.status === 'done') {
              message.success(`${info.file.name} 上传成功`);
              // 刷新合同列表
              fetchAllData();
            } else if (info.file.status === 'error') {
              message.error(`${info.file.name} 上传失败: ${info.file.response?.msg || '未知错误'}`);
            }
          }}
          accept=".pdf,.doc,.docx"
        >
          <Button icon={<UploadOutlined />} style={{ marginBottom: 16 }}>
            上传合同
          </Button>
        </Upload>
        <ContractList employeeId={id} />
      </div>
    );
  };

  // 渲染基本信息标签页内容
  const renderBasicInfo = () => (
    <div>
      {renderPhotoUpload()}
      <Descriptions bordered column={2} style={{ marginTop: 24 }}>
        <Descriptions.Item label="员工编号">{employee.employee_id}</Descriptions.Item>
        <Descriptions.Item label="姓名">{employee.name}</Descriptions.Item>
        <Descriptions.Item label="性别">{employee.gender}</Descriptions.Item>
        <Descriptions.Item label="学历">{employee.education}</Descriptions.Item>
        <Descriptions.Item label="出生日期">
          {employee.birth_date ? moment(employee.birth_date).format('YYYY-MM-DD') : '-'}
        </Descriptions.Item>
        <Descriptions.Item label="身份证号">{employee.id_card || '-'}</Descriptions.Item>
        <Descriptions.Item label="联系电话">{employee.phone || '-'}</Descriptions.Item>
        <Descriptions.Item label="邮箱">{employee.email || '-'}</Descriptions.Item>
        <Descriptions.Item label="住址" span={2}>{employee.address || '-'}</Descriptions.Item>
      </Descriptions>
    </div>
  );

  // 获取实习评估历史
  const fetchEvaluationHistory = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/intern/status/${id}/evaluations`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const result = await response.json();
      if (response.ok && result.code === 200) {
        setEvaluationHistory(result.data);
      }
    } catch (error) {
      console.error('Error fetching evaluation history:', error);
    }
  };

  // 提交实习评估
  const handleEvaluationSubmit = async () => {
    try {
      const values = await evaluationForm.validateFields();
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/intern/evaluations`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...values,
          intern_status_id: employee.intern_status_id
        })
      });
      
      const result = await response.json();
      if (response.ok && result.code === 200) {
        message.success('评估提交成功');
        setInternEvaluationModalVisible(false);
        evaluationForm.resetFields();
        fetchEvaluationHistory();
        fetchAllData(); // 刷新员工信息
      } else {
        message.error(result.msg || '提交失败');
      }
    } catch (error) {
      console.error('Error submitting evaluation:', error);
      message.error('提交失败，请稍后重试');
    }
  };

  // 渲染实习评估历史
  const renderEvaluationHistory = () => {
    const columns = [
      { 
        title: '评估日期', 
        dataIndex: 'evaluation_date', 
        key: 'evaluation_date' 
      },
      { 
        title: '评估类型', 
        dataIndex: 'evaluation_type', 
        key: 'evaluation_type',
        render: type => type === 'monthly' ? '月度评估' : '转正评估'
      },
      { 
        title: '总分', 
        dataIndex: 'total_score', 
        key: 'total_score' 
      },
      { 
        title: '评估结果', 
        key: 'result',
        render: record => record.conversion_recommended ? '建议转正' : '继续观察'
      },
      { 
        title: '评估人', 
        dataIndex: 'evaluator_name', 
        key: 'evaluator_name' 
      }
    ];

    return (
      <div>
        <Space style={{ marginBottom: 16 }}>
          <Button
            type="primary"
            onClick={() => setInternEvaluationModalVisible(true)}
            disabled={employee?.employee_type !== 'intern'}
          >
            新增评估
          </Button>
        </Space>
        <Table
          columns={columns}
          dataSource={evaluationHistory}
          rowKey="id"
        />
      </div>
    );
  };

  // 渲染实习评估表单
  const renderEvaluationForm = () => (
    <Modal
      title="实习评估"
      visible={internEvaluationModalVisible}
      onOk={handleEvaluationSubmit}
      onCancel={() => {
        setInternEvaluationModalVisible(false);
        evaluationForm.resetFields();
      }}
      width={800}
    >
      <Form
        form={evaluationForm}
        layout="vertical"
      >
        <Form.Item
          name="evaluation_date"
          label="评估日期"
          rules={[{ required: true }]}
        >
          <DatePicker style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item
          name="evaluation_type"
          label="评估类型"
          rules={[{ required: true }]}
        >
          <Select>
            <Option value="monthly">月度评估</Option>
            <Option value="final">转正评估</Option>
          </Select>
        </Form.Item>
        <Form.Item
          name="work_performance"
          label="工作表现"
          rules={[{ required: true }]}
        >
          <Rate count={5} />
        </Form.Item>
        <Form.Item
          name="learning_ability"
          label="学习能力"
          rules={[{ required: true }]}
        >
          <Rate count={5} />
        </Form.Item>
        <Form.Item
          name="communication_skill"
          label="沟通能力"
          rules={[{ required: true }]}
        >
          <Rate count={5} />
        </Form.Item>
        <Form.Item
          name="professional_skill"
          label="专业技能"
          rules={[{ required: true }]}
        >
          <Rate count={5} />
        </Form.Item>
        <Form.Item
          name="attendance"
          label="出勤情况"
          rules={[{ required: true }]}
        >
          <Rate count={5} />
        </Form.Item>
        <Form.Item
          name="evaluation_content"
          label="评估内容"
          rules={[{ required: true }]}
        >
          <Input.TextArea rows={4} />
        </Form.Item>
        <Form.Item
          name="improvement_suggestions"
          label="改进建议"
        >
          <Input.TextArea rows={4} />
        </Form.Item>
        <Form.Item
          name="conversion_recommended"
          label="是否推荐转正"
          valuePropName="checked"
        >
          <Switch />
        </Form.Item>
        <Form.Item
          noStyle
          shouldUpdate={(prevValues, currentValues) =>
            prevValues.conversion_recommended !== currentValues.conversion_recommended
          }
        >
          {({ getFieldValue }) =>
            getFieldValue('conversion_recommended') ? (
              <>
                <Form.Item
                  name="recommended_position_id"
                  label="建议转正职位"
                >
                  <Select>
                    {positions.map(pos => (
                      <Option key={pos.id} value={pos.id}>{pos.name}</Option>
                    ))}
                  </Select>
                </Form.Item>
                <Form.Item
                  name="recommended_salary"
                  label="建议转正工资"
                >
                  <InputNumber
                    style={{ width: '100%' }}
                    formatter={value => `¥ ${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                    parser={value => value.replace(/\¥\s?|(,*)/g, '')}
                  />
                </Form.Item>
                <Form.Item
                  name="conversion_comments"
                  label="转正意见"
                >
                  <Input.TextArea rows={4} />
                </Form.Item>
              </>
            ) : null
          }
        </Form.Item>
      </Form>
    </Modal>
  );

  if (loading) {
    return (
      <div className="employee-detail">
        <Card>
          <Skeleton active />
        </Card>
      </div>
    );
  }

  if (!employee) {
    return (
      <div className="employee-detail">
        <Card>
          <div className="error-message">员工不存在或已被删除</div>
          <Button type="primary" onClick={() => navigate('/employees')}>返回列表</Button>
        </Card>
      </div>
    );
  }

  // 处理打印功能
  const handlePrint = () => {
    window.print();
  };

  // 修改标签页配置
  const tabItems = [
    {
      key: 'basic',
      label: '基本信息',
      icon: <UserOutlined />,
      children: renderBasicInfo()
    },
    {
      key: 'education',
      label: '教育经历',
      icon: <ReadOutlined />,
      children: renderEducationHistory()
    },
    {
      key: 'work',
      label: '工作经历',
      icon: <BriefcaseOutlined />,
      children: renderWorkHistory()
    },
    {
      key: 'position',
      label: '调岗记录',
      icon: <SwapOutlined />,
      children: renderPositionChanges()
    },
    {
      key: 'contract',
      label: '合同记录',
      icon: <SolutionOutlined />,
      children: <ContractList employeeId={id} />
    },
    // 只有实习生显示评估记录标签
    ...(employee?.employee_type === 'intern' ? [{
      key: 'evaluation',
      label: '实习评估',
      icon: <SolutionOutlined />,
      children: renderEvaluationHistory()
    }] : [])
  ];

  return (
    // 使用正确的类名组合
    <div className="employee-detail employee-detail-container">
      {/* 页面头部 */}
      <div className="detail-header page-header">
        <div className="left">
          <Space>
            <Button 
              icon={<ArrowLeftOutlined />} 
              onClick={() => navigate('/employees')}
            >
              返回
            </Button>
            <h2 className="page-title">员工详情</h2>
          </Space>
        </div>
        <div className="right">
          <Button 
            icon={<PrinterOutlined />} 
            onClick={handlePrint}
            className="action-button"
          >
            打印
          </Button>
        </div>
      </div>

      {/* 统计卡片区域 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={8}>
          <Card className="detail-card">
            <Statistic
              title="教育经历"
              value={educationHistory.length}
              prefix={<ReadOutlined />}
              suffix="条"
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card className="detail-card">
            <Statistic
              title="工作经历"
              value={workHistory.length}
              prefix={<BriefcaseOutlined />}
              suffix="条"
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card className="detail-card">
            <Statistic
              title="调岗记录"
              value={positionChanges.length}
              prefix={<SwapOutlined />}
              suffix="次"
            />
          </Card>
        </Col>
      </Row>

      {loading ? (
        <Skeleton active />
      ) : (
        <>
          {/* 基本信息卡片 */}
          <Card 
            title="基本信息" 
            className="detail-card"
            extra={
              <Button 
                type="primary" 
                icon={<EditOutlined />}
                onClick={() => setIsModalVisible(true)}
              >
                编辑
              </Button>
            }
          >
            {/* 照片上传区域 */}
            <div className="photo-upload">
              <Upload
                name="photo"
                listType="picture-card"
                showUploadList={false}
                beforeUpload={handlePhotoUpload}
                disabled={photoLoading}
              >
                {employee?.photo_url ? (
                  <img 
                    src={`${process.env.REACT_APP_API_URL}${employee.photo_url}`}
                    alt="员工照片"
                  />
                ) : (
                  <div>
                    {photoLoading ? '上传中...' : '上传照片'}
                    <UserOutlined />
                  </div>
                )}
              </Upload>
            </div>

            <Descriptions bordered>
              {/* 基本信息描述列表 */}
              <Descriptions.Item label="员工编号">{employee?.employee_id}</Descriptions.Item>
              <Descriptions.Item label="姓名">{employee?.name}</Descriptions.Item>
              <Descriptions.Item label="性别">{employee?.gender}</Descriptions.Item>
              <Descriptions.Item label="学历">{employee?.education}</Descriptions.Item>
              <Descriptions.Item label="出生日期">
                {employee?.birth_date ? moment(employee.birth_date).format('YYYY-MM-DD') : '-'}
              </Descriptions.Item>
              <Descriptions.Item label="身份证号">{employee?.id_card || '-'}</Descriptions.Item>
              <Descriptions.Item label="联系电话">{employee?.phone || '-'}</Descriptions.Item>
              <Descriptions.Item label="邮箱">{employee?.email || '-'}</Descriptions.Item>
              <Descriptions.Item label="住址" span={2}>{employee?.address || '-'}</Descriptions.Item>
            </Descriptions>
          </Card>

          {/* 标签页区域 */}
          <Card className="detail-card">
            <Tabs activeKey={activeTab} onChange={setActiveTab}>
              {tabItems.map(item => (
                <TabPane 
                  tab={
                    <span>
                      {item.icon}
                      {item.label}
                    </span>
                  } 
                  key={item.key}
                >
                  <div className="history-list">
                    {item.children}
                  </div>
                </TabPane>
              ))}
            </Tabs>
          </Card>
        </>
      )}

      {/* 编辑表单模态框 */}
      <Modal
        title="编辑员工信息"
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        footer={null}
        width={800}
        destroyOnClose
      >
        <EmployeeForm
          employee={employee}
          departments={departments}
          positions={positions}
          onSuccess={() => {
            setIsModalVisible(false);
            fetchAllData();
          }}
          onCancel={() => setIsModalVisible(false)}
        />
      </Modal>

      {/* 添加教育经历模态框 */}
      <Modal
        title="添加教育经历"
        open={addEducationModalVisible}
        onOk={() => form.submit()}
        onCancel={() => {
          setAddEducationModalVisible(false);
          form.resetFields();
        }}
      >
        <Form form={form} onFinish={handleAddEducation}>
          <Form.Item
            name="school"
            label="学校"
            rules={[{ required: true, message: '请输入学校名称' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="major"
            label="专业"
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="degree"
            label="学历"
            rules={[{ required: true, message: '请选择学历' }]}
          >
            <Select>
              <Option value="高中">高中</Option>
              <Option value="专科">专科</Option>
              <Option value="本科">本科</Option>
              <Option value="硕士">硕士</Option>
              <Option value="博士">博士</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="start_date"
            label="开始时间"
            rules={[{ required: true, message: '请选择开始时间' }]}
          >
            <DatePicker />
          </Form.Item>
          <Form.Item
            name="end_date"
            label="结束时间"
          >
            <DatePicker />
          </Form.Item>
        </Form>
      </Modal>

      {/* 添加工作经历模态框 */}
      <Modal
        title="添加工作经历"
        open={addWorkModalVisible}
        onOk={() => form.submit()}
        onCancel={() => {
          setAddWorkModalVisible(false);
          form.resetFields();
        }}
      >
        <Form form={form} onFinish={handleAddWork}>
          <Form.Item
            name="company"
            label="公司"
            rules={[{ required: true, message: '请输入公司名称' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="position"
            label="职位"
            rules={[{ required: true, message: '请输入职位名称' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item
            name="start_date"
            label="开始时间"
            rules={[{ required: true, message: '请选择开始时间' }]}
          >
            <DatePicker />
          </Form.Item>
          <Form.Item
            name="end_date"
            label="结束时间"
          >
            <DatePicker />
          </Form.Item>
          <Form.Item
            name="description"
            label="工作描述"
          >
            <TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 添加调岗记录模态框 */}
      <Modal
        title="添加调岗记录"
        open={addPositionChangeModalVisible}
        onOk={() => form.submit()}
        onCancel={() => {
          setAddPositionChangeModalVisible(false);
          form.resetFields();
        }}
      >
        <Form form={form} onFinish={handleAddPositionChange}>
          <Form.Item
            name="new_department_id"
            label="新部门"
            rules={[{ required: true, message: '请选择新部门' }]}
          >
            <Select>
              {departments.map(dept => (
                <Option key={dept.id} value={dept.id}>{dept.name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="new_position_id"
            label="新职位"
            rules={[{ required: true, message: '请选择新职位' }]}
          >
            <Select>
              {positions.map(pos => (
                <Option key={pos.id} value={pos.id}>{pos.name}</Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="change_date"
            label="调岗日期"
            rules={[{ required: true, message: '请选择调岗日期' }]}
          >
            <DatePicker />
          </Form.Item>
          <Form.Item
            name="change_reason"
            label="调岗原因"
          >
            <TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>

      {renderEvaluationForm()}
    </div>
  );
};

export default EmployeeDetail;
