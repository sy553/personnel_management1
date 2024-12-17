// CheckInCard.js - 考勤打卡组件

import React, { useState, useEffect } from 'react';
import { Card, Button, Typography, Space, message } from 'antd';
import { ClockCircleOutlined } from '@ant-design/icons';
import { createAttendanceRecord } from '../../services/attendance';
import dayjs from 'dayjs';

const { Title, Text } = Typography;

const CheckInCard = () => {
  // 当前时间状态
  const [currentTime, setCurrentTime] = useState(dayjs());
  // 打卡状态
  const [checkInStatus, setCheckInStatus] = useState({
    checkedIn: false,
    checkedOut: false,
  });

  // 更新当前时间
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(dayjs());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // 处理打卡
  const handleCheckIn = async (type) => {
    try {
      const response = await createAttendanceRecord({
        date: currentTime.format('YYYY-MM-DD'),
        [type === 'in' ? 'check_in' : 'check_out']: currentTime.format('HH:mm:ss'),
      });

      if (response.code === 200) {
        message.success(type === 'in' ? '签到成功' : '签退成功');
        setCheckInStatus(prev => ({
          ...prev,
          [type === 'in' ? 'checkedIn' : 'checkedOut']: true,
        }));
      } else {
        message.error(response.msg || '操作失败');
      }
    } catch (error) {
      message.error('操作失败，请重试');
      console.error('打卡失败:', error);
    }
  };

  return (
    <Card className="check-in-card">
      <Space direction="vertical" size="large" style={{ width: '100%', textAlign: 'center' }}>
        <Title level={2}>
          <ClockCircleOutlined /> 考勤打卡
        </Title>
        
        <div className="current-time">
          <Title level={3}>{currentTime.format('HH:mm:ss')}</Title>
          <Text>{currentTime.format('YYYY年MM月DD日 dddd')}</Text>
        </div>

        <Space size="large">
          <Button
            type="primary"
            size="large"
            onClick={() => handleCheckIn('in')}
            disabled={checkInStatus.checkedIn}
          >
            签到打卡
          </Button>
          <Button
            type="primary"
            size="large"
            onClick={() => handleCheckIn('out')}
            disabled={!checkInStatus.checkedIn || checkInStatus.checkedOut}
          >
            签退打卡
          </Button>
        </Space>

        <div className="check-in-status">
          <Space direction="vertical">
            <Text>
              签到状态：
              <Text type={checkInStatus.checkedIn ? "success" : "warning"}>
                {checkInStatus.checkedIn ? '已签到' : '未签到'}
              </Text>
            </Text>
            <Text>
              签退状态：
              <Text type={checkInStatus.checkedOut ? "success" : "warning"}>
                {checkInStatus.checkedOut ? '已签退' : '未签退'}
              </Text>
            </Text>
          </Space>
        </div>
      </Space>

      <style jsx>{`
        .check-in-card {
          max-width: 600px;
          margin: 20px auto;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .current-time {
          background: #f5f5f5;
          padding: 20px;
          border-radius: 8px;
        }
        .check-in-status {
          margin-top: 20px;
          padding: 15px;
          background: #fafafa;
          border-radius: 8px;
        }
      `}</style>
    </Card>
  );
};

export default CheckInCard;
