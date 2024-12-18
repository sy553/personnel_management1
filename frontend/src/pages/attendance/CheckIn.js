// CheckIn.js - 考勤打卡页面

import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  message,
  Space,
  Modal,
  Form,
  Input,
  Select,
  Upload,
  Spin,
  Typography,
  Row,
  Col,
  Statistic,
  DatePicker
} from 'antd';
import {
  CheckCircleOutlined,
  CameraOutlined,
  EnvironmentOutlined,
  ClockCircleOutlined,
  UploadOutlined,
  CloseCircleOutlined,
  CompassOutlined
} from '@ant-design/icons';
import {
  createAttendanceRecord,
  createFieldWorkRecord,
  createMakeupRecord,
  getCheckInLocations,
  getAttendanceRecords
} from '../../services/attendance';
import { getUserInfo } from '../../utils/auth';
import dayjs from 'dayjs';
import axios from 'axios';
import moment from 'moment';

const { Title, Text } = Typography;
const { Option } = Select;

/**
 * 考勤打卡组件
 */
const CheckIn = () => {
  // 状态定义
  const [loading, setLoading] = useState(false);
  const [locations, setLocations] = useState([]);
  const [currentPosition, setCurrentPosition] = useState(null);
  const [makeupVisible, setMakeupVisible] = useState(false);
  const [fieldWorkVisible, setFieldWorkVisible] = useState(false);
  const [form] = Form.useForm();
  const [currentTime, setCurrentTime] = useState(dayjs());
  const [todayRecord, setTodayRecord] = useState(null);
  const [userInfo, setUserInfo] = useState(null);

  // 外勤打卡弹窗
  const [fieldWorkModalVisible, setFieldWorkModalVisible] = useState(false);
  const [fieldWorkLocation, setFieldWorkLocation] = useState('');
  const [fieldWorkReason, setFieldWorkReason] = useState('');

  // 补卡申请弹窗
  const [makeupModalVisible, setMakeupModalVisible] = useState(false);
  const [makeupDate, setMakeupDate] = useState(moment());
  const [makeupType, setMakeupType] = useState('签到');
  const [makeupReason, setMakeupReason] = useState('');

  // 初始化时获取用户信息
  useEffect(() => {
    // 尝试从localStorage获取用户信息
    const userStr = localStorage.getItem('auth');
    if (userStr) {
      try {
        const parsedUser = JSON.parse(userStr);
        console.log('获取到的用户信息:', parsedUser); // 添加日志
        if (!parsedUser.employeeId) {
          console.warn('用户信息中缺少employeeId:', parsedUser); // 添加警告日志
          message.error('未找到员工信息，请联系管理员');
        }
        setUserInfo(parsedUser);
      } catch (error) {
        console.error('解析用户信息失败:', error);
        message.error('获取用户信息失败，请重新登录');
      }
    } else {
      console.warn('localStorage中未找到auth信息'); // 添加警告日志
      message.error('未找到用户信息，请重新登录');
    }
  }, []);

  // 更新当前时间
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(dayjs());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // 获取打卡地点列表
  useEffect(() => {
    fetchLocations();
  }, []);

  // 获取当前位置
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        position => {
          setCurrentPosition({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          });
        },
        error => {
          console.error('获取位置失败:', error);
          message.error('获取位置信息失败');
        }
      );
    }
  }, []);

  // 获取今天的考勤记录
  const fetchTodayRecord = async () => {
    try {
      const today = dayjs().format('YYYY-MM-DD');
      const response = await getAttendanceRecords({
        date: today
      });
      if (response?.code === 200 && response.data?.length > 0) {
        setTodayRecord(response.data[0]);
      }
    } catch (error) {
      console.error('获取考勤记录失败:', error);
      message.error('获取考勤记录失败');
    }
  };

  // 获取今日考勤记录
  useEffect(() => {
    if (userInfo?.id) {
      fetchTodayRecord();
    }
  }, [userInfo]);

  /**
   * 获取打卡地点列表
   */
  const fetchLocations = async () => {
    try {
      const response = await getCheckInLocations();
      if (response?.code === 200) {
        setLocations(response.data || []);
      }
    } catch (error) {
      console.error('获取打卡地点失败:', error);
      message.error('获取打卡地点失败');
    }
  };

  /**
   * 普通打卡
   */
  const handleCheckIn = async (type) => {
    try {
      setLoading(true);
      const userInfo = getUserInfo();
      if (!userInfo?.employeeId) {
        message.error('未找到员工信息');
        return;
      }

      const data = {
        employee_id: userInfo.employeeId,
        type: type === 'in' ? 'check_in' : 'check_out',
        timestamp: new Date().toISOString()
      };

      const response = await createAttendanceRecord(data);
      if (response?.code === 200) {
        message.success(type === 'in' ? '签到成功' : '签退成功');
        fetchTodayRecord(); // 刷新考勤记录
      }
    } catch (error) {
      console.error('打卡失败:', error);
      message.error(error.message || '打卡失败');
    } finally {
      setLoading(false);
    }
  };

  /**
   * 外勤打卡
   */
  const handleFieldWork = async () => {
    try {
      if (!fieldWorkLocation.trim()) {
        message.error('请输入外勤地点');
        return;
      }
      if (!fieldWorkReason.trim()) {
        message.error('请输入外勤原因');
        return;
      }

      // 从状态中获取用户信息
      if (!userInfo || !userInfo.employeeId) {
        message.error('未找到员工信息，请重新登录');
        return;
      }

      const response = await axios.post(`${process.env.REACT_APP_API_URL}/api/attendance/field-work`, {
        employee_id: userInfo.employeeId,
        location: fieldWorkLocation,
        reason: fieldWorkReason
      });

      if (response.data.code === 200) {
        message.success('外勤打卡成功');
        setFieldWorkModalVisible(false);
        setFieldWorkLocation('');
        setFieldWorkReason('');
        fetchTodayRecord(); // 刷新考勤记录
      } else {
        message.error(response.data.message || '外勤打卡失败');
      }
    } catch (error) {
      console.error('外勤打卡错误:', error);
      message.error(error.response?.data?.message || '外勤打卡失败，请稍后重试');
    }
  };

  /**
   * 补卡申请
   */
  const handleMakeup = async () => {
    try {
      if (!makeupReason.trim()) {
        message.error('请输入补卡原因');
        return;
      }

      // 从状态中获取用户信息
      if (!userInfo || !userInfo.employeeId) {
        message.error('未找到员工信息，请重新登录');
        return;
      }

      const response = await axios.post(`${process.env.REACT_APP_API_URL}/api/attendance/makeup`, {
        employee_id: userInfo.employeeId,
        date: makeupDate.format('YYYY-MM-DD'),
        type: makeupType,
        reason: makeupReason
      });

      if (response.data.code === 200) {
        message.success('补卡申请提交成功');
        setMakeupModalVisible(false);
        setMakeupDate(moment());
        setMakeupType('签到');
        setMakeupReason('');
        fetchTodayRecord(); // 刷新考勤记录
      } else {
        message.error(response.data.message || '补卡申请失败');
      }
    } catch (error) {
      console.error('补卡申请错误:', error);
      message.error(error.response?.data?.message || '补卡申请失败，请稍后重试');
    }
  };

  return (
    <Spin spinning={loading}>
      <div className="attendance-container">
        <Card className="check-in-card">
          <Title level={2} style={{ textAlign: 'center', marginBottom: 30 }}>
            <ClockCircleOutlined /> 员工考勤打卡
          </Title>

          {/* 时间显示 */}
          <div className="time-display" style={{ textAlign: 'center', marginBottom: 30 }}>
            <Title level={3}>{currentTime.format('HH:mm:ss')}</Title>
            <Text>{currentTime.format('YYYY年MM月DD日 dddd')}</Text>
          </div>

          {/* 考勤状态 */}
          <Row gutter={16} style={{ marginBottom: 30 }}>
            <Col span={12}>
              <Card>
                <Statistic
                  title="签到状态"
                  value={todayRecord?.check_in ? '已签到' : '未签到'}
                  valueStyle={{ color: todayRecord?.check_in ? '#52c41a' : '#999' }}
                  prefix={todayRecord?.check_in ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                />
                {todayRecord?.check_in && (
                  <Text type="secondary">
                    签到时间：{dayjs(todayRecord.check_in).format('HH:mm:ss')}
                  </Text>
                )}
              </Card>
            </Col>
            <Col span={12}>
              <Card>
                <Statistic
                  title="签退状态"
                  value={todayRecord?.check_out ? '已签退' : '未签退'}
                  valueStyle={{ color: todayRecord?.check_out ? '#52c41a' : '#999' }}
                  prefix={todayRecord?.check_out ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                />
                {todayRecord?.check_out && (
                  <Text type="secondary">
                    签退时间：{dayjs(todayRecord.check_out).format('HH:mm:ss')}
                  </Text>
                )}
              </Card>
            </Col>
          </Row>

          {/* 打卡按钮 */}
          <Row gutter={16} justify="center" style={{ marginBottom: 30 }}>
            <Col>
              <Button
                type="primary"
                size="large"
                icon={<CheckCircleOutlined />}
                onClick={() => handleCheckIn('in')}
                disabled={todayRecord?.check_in}
              >
                签到打卡
              </Button>
            </Col>
            <Col>
              <Button
                type="primary"
                size="large"
                icon={<CheckCircleOutlined />}
                onClick={() => handleCheckIn('out')}
                disabled={!todayRecord?.check_in || todayRecord?.check_out}
              >
                签退打卡
              </Button>
            </Col>
          </Row>

          {/* 功能按钮组 */}
          <Space size="middle" style={{ width: '100%', justifyContent: 'center' }}>
            <Button
              icon={<CompassOutlined />}
              onClick={() => setFieldWorkModalVisible(true)}
            >
              外勤打卡
            </Button>
            <Button
              icon={<ClockCircleOutlined />}
              onClick={() => setMakeupModalVisible(true)}
            >
              补卡申请
            </Button>
          </Space>

          {/* 位置信息显示 */}
          {currentPosition && (
            <div className="location-info">
              <EnvironmentOutlined /> 当前位置已获取
            </div>
          )}
        </Card>

        {/* 外勤打卡弹窗 */}
        <Modal
          title="外勤打卡"
          visible={fieldWorkModalVisible}
          onOk={handleFieldWork}
          onCancel={() => {
            setFieldWorkModalVisible(false);
            setFieldWorkLocation('');
            setFieldWorkReason('');
          }}
          okText="确认打卡"
          cancelText="取消"
        >
          <Form layout="vertical">
            <Form.Item label="外勤地点" required>
              <Input
                placeholder="请输入外勤地点"
                value={fieldWorkLocation}
                onChange={e => setFieldWorkLocation(e.target.value)}
              />
            </Form.Item>
            <Form.Item label="外勤原因" required>
              <Input.TextArea
                placeholder="请输入外勤原因"
                value={fieldWorkReason}
                onChange={e => setFieldWorkReason(e.target.value)}
                rows={4}
              />
            </Form.Item>
          </Form>
        </Modal>

        {/* 补卡申请弹窗 */}
        <Modal
          title="补卡申请"
          visible={makeupModalVisible}
          onOk={handleMakeup}
          onCancel={() => {
            setMakeupModalVisible(false);
            setMakeupDate(moment());
            setMakeupType('签到');
            setMakeupReason('');
          }}
          okText="提交申请"
          cancelText="取消"
        >
          <Form layout="vertical">
            <Form.Item label="补卡日期" required>
              <DatePicker
                value={makeupDate}
                onChange={setMakeupDate}
                style={{ width: '100%' }}
              />
            </Form.Item>
            <Form.Item label="补卡类型" required>
              <Select
                value={makeupType}
                onChange={setMakeupType}
                style={{ width: '100%' }}
              >
                <Select.Option value="签到">签到</Select.Option>
                <Select.Option value="签退">签退</Select.Option>
              </Select>
            </Form.Item>
            <Form.Item label="补卡原因" required>
              <Input.TextArea
                placeholder="请输入补卡原因"
                value={makeupReason}
                onChange={e => setMakeupReason(e.target.value)}
                rows={4}
              />
            </Form.Item>
          </Form>
        </Modal>
      </div>
    </Spin>
  );
};

export default CheckIn;
