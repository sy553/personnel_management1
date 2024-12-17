// CheckIn.js - 考勤打卡页面

import React, { useState, useEffect } from 'react';
import { Card, Typography, Row, Col, Statistic, message } from 'antd';
import { ClockCircleOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { createAttendanceRecord, getAttendanceRecords } from '../../services/attendance';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

/**
 * 考勤打卡页面组件
 * 提供员工打卡功能，包括签到和签退
 */
const CheckInPage = () => {
  // 状态管理
  const [currentTime, setCurrentTime] = useState(dayjs());
  const [todayRecord, setTodayRecord] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userInfo, setUserInfo] = useState(null);

  // 初始化时获取用户信息
  useEffect(() => {
    // 尝试从localStorage获取用户信息
    const user = localStorage.getItem('user');
    if (user) {
      try {
        const parsedUser = JSON.parse(user);
        setUserInfo(parsedUser);
      } catch (error) {
        console.error('解析用户信息失败:', error);
      }
    }
  }, []);

  // 获取今天的考勤记录
  const fetchTodayRecord = async () => {
    try {
      const today = dayjs().format('YYYY-MM-DD');
      const response = await getAttendanceRecords({
        employee_id: userInfo?.id, // 添加员工ID
        start_date: today,
        end_date: today,
      });
      
      if (response.code === 200 && response.data.length > 0) {
        setTodayRecord(response.data[0]);
      }
    } catch (error) {
      console.error('获取今日考勤记录失败:', error);
      message.error('获取考勤记录失败');
    } finally {
      setLoading(false);
    }
  };

  // 处理打卡
  const handleCheckIn = async (type) => {
    if (!userInfo?.id) {
      message.error('获取用户信息失败，请重新登录');
      return;
    }

    try {
      const now = dayjs();
      const response = await createAttendanceRecord({
        employee_id: userInfo.id, // 添加员工ID
        date: now.format('YYYY-MM-DD'),
        [type === 'in' ? 'check_in' : 'check_out']: now.format('HH:mm'),  // 只发送时间部分
      });

      if (response.code === 200) {
        message.success(type === 'in' ? '签到成功' : '签退成功');
        fetchTodayRecord();
      } else {
        message.error(response.msg || '操作失败');
      }
    } catch (error) {
      console.error('打卡失败:', error);
      message.error('操作失败，请重试');
    }
  };

  // 更新当前时间
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(dayjs());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // 获取今日考勤记录
  useEffect(() => {
    if (userInfo?.id) {
      fetchTodayRecord();
    }
  }, [userInfo]);

  // 如果没有用户信息，显示提示
  if (!userInfo?.id) {
    return (
      <div className="attendance-container">
        <Card>
          <Title level={3} style={{ textAlign: 'center' }}>
            获取用户信息失败，请重新登录
          </Title>
        </Card>
      </div>
    );
  }

  return (
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
        <Row gutter={16} justify="center">
          <Col>
            <button
              className={`check-button ${todayRecord?.check_in ? 'disabled' : ''}`}
              onClick={() => handleCheckIn('in')}
              disabled={todayRecord?.check_in}
            >
              签到打卡
            </button>
          </Col>
          <Col>
            <button
              className={`check-button ${!todayRecord?.check_in || todayRecord?.check_out ? 'disabled' : ''}`}
              onClick={() => handleCheckIn('out')}
              disabled={!todayRecord?.check_in || todayRecord?.check_out}
            >
              签退打卡
            </button>
          </Col>
        </Row>
      </Card>

      <style jsx>{`
        .attendance-container {
          padding: 24px;
          max-width: 800px;
          margin: 0 auto;
        }
        .check-in-card {
          background: #fff;
          border-radius: 8px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .time-display {
          background: #f5f5f5;
          padding: 20px;
          border-radius: 8px;
          margin-bottom: 24px;
        }
        .check-button {
          padding: 12px 24px;
          font-size: 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          background: #1890ff;
          color: white;
          transition: all 0.3s;
        }
        .check-button:hover {
          background: #40a9ff;
        }
        .check-button.disabled {
          background: #d9d9d9;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
};

export default CheckInPage;
