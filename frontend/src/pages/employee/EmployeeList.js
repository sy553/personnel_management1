import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Button, 
  Space, 
  Select, 
  Row, 
  Col, 
  message, 
  Modal, 
  Form, 
  Radio, 
  Tag, 
  Input, 
  Upload, 
  Avatar, 
  Dropdown,
  Card,
  Statistic
} from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  PlusOutlined,
  UploadOutlined,
  DownloadOutlined,
  DownOutlined,
  EditOutlined,
  DeleteOutlined,
  ExclamationCircleOutlined,
  EyeOutlined,
  PrinterOutlined
} from '@ant-design/icons';
import axios from '../../utils/axios';
import EmployeeForm from './EmployeeForm';
import { 
  exportEmployees, 
  importEmployees, 
  getImportTemplate 
} from '../../services/employee';
import { useNavigate } from 'react-router-dom';
import './styles/employee.css';
import '../../styles/common.css';

const { Option } = Select;

// 处理头像URL的函数
const getImageUrl = (avatar) => {
  if (!avatar) return '';
  // 如果avatar已经是完整的URL，直接返回
  if (avatar.startsWith('http://') || avatar.startsWith('https://')) {
    return avatar;
  }
  // 使用static路径
  if (avatar.startsWith('/static/')) {
    return `${process.env.REACT_APP_API_BASE_URL}${avatar}`;
  }
  // 如果没有/static/前缀，添加它
  return `${process.env.REACT_APP_API_BASE_URL}/static/uploads/photos/${avatar}`;
};

const EmployeeList = () => {
  // 状态定义
  const [employees, setEmployees] = useState([]); // 员工列表数据
  const [employeeStats, setEmployeeStats] = useState({
    active: 0,
    suspended: 0,
    resigned: 0,
    total: 0
  }); // 员工统计数据
  const [departments, setDepartments] = useState([]); // 部门列表
  const [positions, setPositions] = useState([]); // 职位列表
  const [selectedDepartment, setSelectedDepartment] = useState(undefined); // 选中的部门
  const [selectedPosition, setSelectedPosition] = useState(undefined); // 选中的职位
  const [selectedGender, setSelectedGender] = useState(undefined); // 选中的性别
  const [selectedEducation, setSelectedEducation] = useState(undefined); // 选中的学历
  const [selectedStatus, setSelectedStatus] = useState('active'); // 选中的在职状态，默认在职
  const [currentPage, setCurrentPage] = useState(1); // 当前页码
  const [total, setTotal] = useState(0); // 总记录数
  const [open, setOpen] = useState(false); // 控制表单弹窗显示
  const [currentEmployee, setCurrentEmployee] = useState(null); // 当前编辑的员工
  const [searchKeyword, setSearchKeyword] = useState(''); // 添加搜索关键词状态
  const [loading, setLoading] = useState(false); // 表格加载状态
  const [detailOpen, setDetailOpen] = useState(false); // 控制详情弹窗显示
  const [detailEmployee, setDetailEmployee] = useState(null); // 当前查看的员工
  const [importModalVisible, setImportModalVisible] = useState(false); // 控制导入模态框显示

  const navigate = useNavigate();

  // 渲染状态标签
  const renderStatusTag = (status) => {
    const statusConfig = {
      active: { color: 'success', text: '在职' },
      suspended: { color: 'warning', text: '休假' },  // 将"停职"改为"休假"
      resigned: { color: 'error', text: '离职' }
    };
    const config = statusConfig[status] || { color: 'default', text: '未知' };
    return (
      <Tag color={config.color} className={`status-tag ${status}`}>
        {config.text}
      </Tag>
    );
  };

  // 获取员工列表数据
  const fetchEmployees = React.useCallback(async (page = 1) => {
    setLoading(true);
    try {
      const params = {
        page,
        per_page: 10,
        department_id: selectedDepartment,
        position_id: selectedPosition,
        search: searchKeyword,
        gender: selectedGender,
        education: selectedEducation,
        employment_status: selectedStatus
      };

      console.log('获取员工列表，请求参数:', params);

      const response = await axios.get('/api/employees', { params });
      console.log('获取员工列表响应:', response.data);

      if (response.data.code === 200) {
        // 为每个数据项添加唯一的 key
        const processedData = response.data.data.items.map(item => ({
          ...item,
          key: `employee-${item.id}`
        }));
        setEmployees(processedData);
        setTotal(response.data.data.total);
      } else {
        message.error(response.data.msg || '获取员工列表失败');
      }
    } catch (error) {
      console.error('获取员工列表失败:', error);
      if (error.response) {
        console.error('错误响应:', error.response.data);
      }
      message.error('获取员工列表失败');
    } finally {
      setLoading(false);
    }
  }, [selectedDepartment, selectedPosition, searchKeyword, selectedGender, selectedEducation, selectedStatus]);

  // 获取员工统计数据
  const fetchEmployeeStats = async () => {
    try {
      const response = await axios.get('/api/employees/stats');
      if (response.data.code === 200) {
        setEmployeeStats(response.data.data);
      }
    } catch (error) {
      console.error('获取员工统计数据失败:', error);
    }
  };

  // 获取部门和职位列表
  const fetchDepartmentsAndPositions = async () => {
    try {
      const [deptRes, posRes] = await Promise.all([
        axios.get('/api/departments'),
        axios.get('/api/positions')
      ]);
      
      console.log('获取部门列表响应:', deptRes.data);
      console.log('获取职位列表响应:', posRes.data);
      
      if (deptRes.data.code === 200) {
        setDepartments(deptRes.data.data || []);
      }
      
      if (posRes.data.code === 200) {
        setPositions(posRes.data.data || []);
      }
    } catch (error) {
      console.error('获取部门和职位列表失败:', error);
      message.error('获取部门和职位列表失败');
    }
  };

  // 组件加载时获取数据
  React.useEffect(() => {
    fetchEmployeeStats();
  }, []);

  React.useEffect(() => {
    fetchEmployees(currentPage);
  }, [fetchEmployees, currentPage]);

  React.useEffect(() => {
    fetchDepartmentsAndPositions();
  }, []);

  // 处理部门筛选
  const handleDepartmentChange = (value) => {
    setSelectedDepartment(value);
    fetchEmployees(1);
  };

  // 处理职位筛选
  const handlePositionChange = (value) => {
    setSelectedPosition(value);
    fetchEmployees(1);
  };

  // 处理性别筛选
  const handleGenderChange = (value) => {
    setSelectedGender(value);
    fetchEmployees(1);
  };

  // 处理学历筛选
  const handleEducationChange = (value) => {
    setSelectedEducation(value);
    fetchEmployees(1);
  };

  // 处理状态筛选变化
  const handleStatusChange = (value) => {
    console.log('状态变更为:', value);
    setSelectedStatus(value);
    setCurrentPage(1);
    fetchEmployees(1);
  };

  // 处理分页变化
  const handleTableChange = (pagination) => {
    setCurrentPage(pagination.current);
    fetchEmployees(pagination.current);
  };

  // 处理删除
  const handleDelete = (id) => {
    Modal.confirm({
      title: '确认删除',
      icon: <ExclamationCircleOutlined />,
      content: '确定要删除这名员工吗？此操作不可恢复。',
      okText: '确定',
      cancelText: '取消',
      styles: { body: { padding: '24px' } },
      onOk: async () => {
        try {
          await axios.delete(`/api/employees/${id}`);
          message.success('删除成功');
          fetchEmployees();
          // 删除员工后刷新统计数据
          fetchEmployeeStats();
        } catch (error) {
          console.error('删除失败:', error);
          message.error('删除失败');
        }
      },
    });
  };

  // 处理编辑
  const handleEdit = (record) => {
    setCurrentEmployee(record);
    setOpen(true);
  };

  // 处理表单成功提交
  const handleFormSuccess = (needRefreshStats = false) => {
    setOpen(false);
    setCurrentEmployee(null);
    fetchEmployees(currentPage);
    // 如果需要刷新统计数据（状态变更或新增员工时）
    if (needRefreshStats) {
      fetchEmployeeStats();
    }
  };

  // 处理取消编辑
  const handleCancel = () => {
    setOpen(false);
    setCurrentEmployee(null);
    // 关闭弹窗时也刷新列表
    fetchEmployees(currentPage);
  };

  // 处理搜索
  const handleSearch = (value) => {
    setSearchKeyword(value);
    fetchEmployees(1);
  };

  // 处理导出
  const handleExport = async (status) => {
    try {
      message.loading({ content: '正在导出...', key: 'export' });
      const response = await exportEmployees(status);
      const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const statusText = {
        'active': '在职',
        'resigned': '离职',
        'suspended': '休假'
      }[status] || '全部';
      link.download = `employees_${statusText}_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      message.success({ content: '导出成功', key: 'export' });
    } catch (error) {
      console.error('导出失败:', error);
      message.error({ content: '导出失败', key: 'export' });
    }
  };

  // 处理导入
  const handleImport = async (file) => {
    try {
      message.loading({ content: '正在导入...', key: 'import' });
      
      // 检查文件类型
      const fileType = file.name.split('.').pop().toLowerCase();
      if (fileType !== 'xlsx') {
        message.error({ content: '请上传Excel文件(.xlsx)', key: 'import' });
        return;
      }
      
      // 检查文件大小（限制为10MB）
      const maxSize = 10 * 1024 * 1024; // 10MB
      if (file.size > maxSize) {
        message.error({ content: '文件大小不能超过10MB', key: 'import' });
        return;
      }
      
      const response = await importEmployees(file);
      console.log('Import response:', response);
      
      if (response.code === 200) {
        const { success_count, error_count, errors } = response.data;
        
        if (error_count > 0) {
          Modal.error({
            title: '导入完成，但存在错误',
            content: (
              <div>
                <p>成功导入: {success_count} 条</p>
                <p>失败: {error_count} 条</p>
                <div style={{ maxHeight: '200px', overflow: 'auto' }}>
                  {errors.map((error, index) => (
                    <p key={index} style={{ color: 'red' }}>{error}</p>
                  ))}
                </div>
              </div>
            ),
            width: 500
          });
        } else {
          message.success({ content: `成功导入 ${success_count} 条记录`, key: 'import' });
        }
        
        // 刷新列表
        fetchEmployees(1);
      } else {
        throw new Error(response.msg || '导入失败');
      }
    } catch (error) {
      console.error('导入失败:', error);
      message.error({ 
        content: error.response?.data?.msg || error.message || '导入失败', 
        key: 'import' 
      });
    }
  };

  // 处理下载模板
  const handleDownloadTemplate = async () => {
    try {
      message.loading({ content: '正在下载模板...', key: 'template' });
      const response = await getImportTemplate();
      const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'employee_import_template.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      message.success({ content: '模板下载成功', key: 'template' });
    } catch (error) {
      console.error('模板下载失败:', error);
      message.error({ content: '模板下载失败', key: 'template' });
    }
  };

  // 处理查看详情
  const handleViewDetail = async (record) => {
    try {
      // 获取教育经历
      const educationRes = await axios.get(`/api/employees/${record.id}/education`);
      const workRes = await axios.get(`/api/employees/${record.id}/work`);
      
      setDetailEmployee({
        ...record,
        educationHistory: educationRes.data.data || [],
        workHistory: workRes.data.data || []
      });
      setDetailOpen(true);
    } catch (error) {
      console.error('获取详情失败:', error);
      message.error('获取详情失败');
      // 如果获取额外信息失败，仍然显示基本信息
      setDetailEmployee(record);
      setDetailOpen(true);
    }
  };

  // 处理关闭详情
  const handleDetailClose = () => {
    setDetailOpen(false);
    setDetailEmployee(null);
  };

  return (
    <div className="employee-list">
      {/* 统计卡片区域 */}
      <Row gutter={16} className="stats-row">
        <Col span={6}>
          <Card>
            <Statistic
              title="在职员工"
              value={employeeStats.active}
              prefix={<TeamOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="休假员工"  // 将"停职员工"改为"休假员工"
              value={employeeStats.suspended}
              prefix={<UserOutlined style={{ color: '#faad14' }} />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="离职员工"
              value={employeeStats.resigned}
              prefix={<UserOutlined style={{ color: '#ff4d4f' }} />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="总人数"
              value={employeeStats.total}
              prefix={<TeamOutlined style={{ color: '#1890ff' }} />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 搜索和过滤区域 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          <Col span={6}>
            <Input.Search
              placeholder="搜索员工姓名/工号"
              onSearch={handleSearch}
              style={{ width: '100%' }}
              allowClear
            />
          </Col>
          <Col span={4}>
            <Select
              placeholder="选择部门"
              onChange={handleDepartmentChange}
              style={{ width: '100%' }}
              allowClear
            >
              {departments.map(dept => (
                <Option key={dept.id} value={dept.id}>{dept.name}</Option>
              ))}
            </Select>
          </Col>
          <Col span={4}>
            <Select
              placeholder="选择职位"
              onChange={handlePositionChange}
              style={{ width: '100%' }}
              allowClear
            >
              {positions.map(pos => (
                <Option key={pos.id} value={pos.id}>{pos.name}</Option>
              ))}
            </Select>
          </Col>
          <Col span={4}>
            <Select
              placeholder="选择性别"
              onChange={handleGenderChange}
              style={{ width: '100%' }}
              allowClear
            >
              <Option value="男">男</Option>
              <Option value="女">女</Option>
            </Select>
          </Col>
          <Col span={4}>
            <Select
              placeholder="在职状态"
              onChange={handleStatusChange}
              style={{ width: '100%' }}
              defaultValue="active"
            >
              <Option value="active">在职</Option>
              <Option value="suspended">休假</Option>
              <Option value="resigned">离职</Option>
            </Select>
          </Col>
        </Row>
      </Card>

      {/* 操作按钮区域 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space size="middle">
              <Button type="primary" icon={<PlusOutlined />} onClick={() => setOpen(true)}>
                新增员工
              </Button>
              <Button icon={<UploadOutlined />} onClick={() => setImportModalVisible(true)}>
                导入员工
              </Button>
              <Button icon={<DownloadOutlined />} onClick={handleDownloadTemplate}>
                下载模板
              </Button>
            </Space>
          </Col>
          <Col>
            <Dropdown
              menu={{
                items: [
                  { key: 'all', label: '导出全部' },
                  { key: 'active', label: '导出在职' },
                  { key: 'suspended', label: '导出休假' },
                  { key: 'resigned', label: '导出离职' }
                ],
                onClick: ({ key }) => handleExport(key)
              }}
            >
              <Button>
                导出 <DownOutlined />
              </Button>
            </Dropdown>
          </Col>
        </Row>
      </Card>

      {/* 员工列表表格 */}
      <Card>
        <Table
          columns={[
            {
              title: '员工信息',
              dataIndex: 'name',
              key: 'employeeInfo',
              fixed: 'left',
              width: 250,
              render: (_, record) => (
                <Space>
                  <Avatar
                    src={getImageUrl(record.photo_url)}
                    icon={<UserOutlined />}
                  />
                  <div>
                    <div style={{ fontWeight: 'bold' }}>{record.name}</div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      工号: {record.employee_id}
                    </div>
                  </div>
                </Space>
              ),
            },
            {
              title: '部门',
              dataIndex: 'department',
              key: 'department',
              width: 120,
            },
            {
              title: '职位',
              dataIndex: 'position',
              key: 'position',
              width: 120,
            },
            {
              title: '联系方式',
              key: 'contact',
              width: 200,
              render: (_, record) => (
                <div>
                  <div>{record.phone}</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>{record.email}</div>
                </div>
              ),
            },
            {
              title: '入职日期',
              dataIndex: 'hire_date',
              key: 'hire_date',
              width: 120,
            },
            {
              title: '状态',
              dataIndex: 'employment_status',
              key: 'status',
              width: 100,
              render: (status) => renderStatusTag(status),
            },
            {
              title: '操作',
              key: 'action',
              fixed: 'right',
              width: 200,
              render: (_, record) => (
                <Space size="middle">
                  <Button
                    type="link"
                    icon={<EyeOutlined />}
                    onClick={() => handleViewDetail(record)}
                  >
                    详情
                  </Button>
                  <Button
                    type="link"
                    icon={<EditOutlined />}
                    onClick={() => handleEdit(record)}
                  >
                    编辑
                  </Button>
                  <Button
                    type="link"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => handleDelete(record.id)}
                  >
                    删除
                  </Button>
                </Space>
              ),
            },
          ]}
          dataSource={employees}
          rowKey="id"
          pagination={{
            total: total,
            current: currentPage,
            pageSize: 10,
            showSizeChanger: false,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`
          }}
          onChange={handleTableChange}
          scroll={{ x: 1300 }}
          loading={loading}
        />
      </Card>

      {/* 员工表单弹窗 */}
      <EmployeeForm
        open={open}
        employee={currentEmployee}
        departments={departments}
        positions={positions}
        onSuccess={handleFormSuccess}
        onCancel={handleCancel}
      />

      {/* 员工详情弹窗 */}
      <Modal
        title={
          <Space>
            <span>员工档案</span>
            <Button 
              type="primary" 
              icon={<PrinterOutlined />}
              onClick={() => window.print()}
            >
              打印
            </Button>
          </Space>
        }
        open={detailOpen}
        onCancel={handleDetailClose}
        width={800}
        footer={null}
        className="employee-detail-modal"
      >
        {detailEmployee && (
          <div className="archive-content">
            <div className="archive-header">
              <h2>员工个人档案</h2>
            </div>
            <div className="archive-body">
              <table className="archive-table">
                <tbody>
                  <tr>
                    <td className="label">工号：</td>
                    <td className="value">{detailEmployee.employee_id}</td>
                    <td className="label">姓名：</td>
                    <td className="value">{detailEmployee.name}</td>
                    <td className="label">性别：</td>
                    <td className="value">{detailEmployee.gender === 'male' ? '男' : '女'}</td>
                    <td className="photo" rowSpan="4">
                      <div className="photo-container">
                        <Avatar
                          size={120}
                          src={detailEmployee.photo_url ? getImageUrl(detailEmployee.photo_url) : null}
                          icon={<UserOutlined />}
                        />
                      </div>
                    </td>
                  </tr>
                  <tr>
                    <td className="label">出生日期：</td>
                    <td className="value">{detailEmployee.birth_date}</td>
                    <td className="label">学历：</td>
                    <td className="value" colSpan="3">{detailEmployee.education}</td>
                  </tr>
                  <tr>
                    <td className="label">身份证号：</td>
                    <td className="value" colSpan="5">{detailEmployee.id_card}</td>
                  </tr>
                  <tr>
                    <td className="label">户籍所在地：</td>
                    <td className="value" colSpan="5">{detailEmployee.address}</td>
                  </tr>
                  <tr>
                    <td className="label">家庭电话：</td>
                    <td className="value">{detailEmployee.phone}</td>
                    <td className="label">手机：</td>
                    <td className="value">{detailEmployee.phone}</td>
                    <td className="label">E-mail：</td>
                    <td className="value" colSpan="2">{detailEmployee.email}</td>
                  </tr>
                  <tr>
                    <td className="label">家庭住址：</td>
                    <td className="value" colSpan="6">{detailEmployee.address}</td>
                  </tr>
                  <tr>
                    <td className="label">部门：</td>
                    <td className="value">{detailEmployee.department}</td>
                    <td className="label">职位：</td>
                    <td className="value">{detailEmployee.position}</td>
                    <td className="label">入职日期：</td>
                    <td className="value" colSpan="2">{detailEmployee.hire_date}</td>
                  </tr>
                  <tr>
                    <td className="label">在职状态：</td>
                    <td className="value" colSpan="6">
                      {renderStatusTag(detailEmployee.employment_status)}
                    </td>
                  </tr>
                </tbody>
              </table>

              {/* 教育经历 */}
              {detailEmployee.educationHistory && detailEmployee.educationHistory.length > 0 && (
                <div className="archive-section">
                  <div className="section-header">教育经历</div>
                  <table className="archive-table">
                    <thead>
                      <tr>
                        <th>时间</th>
                        <th>学校</th>
                        <th>专业</th>
                        <th>学历</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detailEmployee.educationHistory.map((edu, index) => (
                        <tr key={index}>
                          <td>{edu.start_date} 至 {edu.end_date || '至今'}</td>
                          <td>{edu.school || '-'}</td>
                          <td>{edu.major || '-'}</td>
                          <td>{edu.degree || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* 工作经历 */}
              {detailEmployee.workHistory && detailEmployee.workHistory.length > 0 && (
                <div className="archive-section">
                  <div className="section-header">工作经历</div>
                  <table className="archive-table">
                    <thead>
                      <tr>
                        <th>时间</th>
                        <th>公司</th>
                        <th>职位</th>
                        <th>工作描述</th>
                      </tr>
                    </thead>
                    <tbody>
                      {detailEmployee.workHistory.map((work, index) => (
                        <tr key={index}>
                          <td>{work.start_date} 至 {work.end_date || '至今'}</td>
                          <td>{work.company || '-'}</td>
                          <td>{work.position || '-'}</td>
                          <td>{work.description || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}
      </Modal>

      {/* 导入模态框 */}
      <Modal
        title="导入员工数据"
        open={importModalVisible}
        onCancel={() => setImportModalVisible(false)}
        footer={[
          <Button key="template" onClick={handleDownloadTemplate}>
            下载模板
          </Button>,
          <Button key="cancel" onClick={() => setImportModalVisible(false)}>
            取消
          </Button>
        ]}
      >
        <Upload.Dragger
          name="file"
          accept=".xlsx"
          showUploadList={false}
          customRequest={({ file }) => {
            handleImport(file);
            setImportModalVisible(false);
          }}
        >
          <p className="ant-upload-drag-icon">
            <UploadOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持 .xlsx 格式的 Excel 文件，文件大小不超过 10MB
          </p>
        </Upload.Dragger>
      </Modal>
    </div>
  );
};

export default EmployeeList;
