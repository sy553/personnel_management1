// attendance.js - 考勤相关的API服务

import request from '../utils/request';

/**
 * 考勤打卡相关API
 */

// 获取考勤记录列表
export async function getAttendanceRecords(params) {
  return request('/api/attendance', {
    method: 'GET',
    params,
  });
}

// 创建考勤记录
export async function createAttendanceRecord(data) {
  return request('/api/attendance', {
    method: 'POST',
    data,
  });
}

/**
 * 考勤统计相关API
 */

// 获取考勤统计数据
export async function getAttendanceStatistics(params) {
  return request('/api/attendance/statistics', {
    method: 'GET',
    params,
  });
}

/**
 * 请假相关API
 */

// 获取请假记录列表
export async function getLeaveRecords(params) {
  return request('/api/leave', {
    method: 'GET',
    params,
  });
}

// 创建请假申请
export async function createLeaveRequest(data) {
  return request('/api/leave', {
    method: 'POST',
    data,
  });
}

// 审批请假申请
export async function approveLeaveRequest(id, data) {
  return request(`/api/leave/${id}/approve`, {
    method: 'POST',
    data,
  });
}

/**
 * 加班相关API
 */

// 获取加班记录列表
export async function getOvertimeRecords(params) {
  return request('/api/overtime', {
    method: 'GET',
    params,
  });
}

// 创建加班申请
export async function createOvertimeRequest(data) {
  return request('/api/overtime', {
    method: 'POST',
    data,
  });
}

// 审批加班申请
export async function approveOvertimeRequest(id, data) {
  return request(`/api/overtime/${id}/approve`, {
    method: 'POST',
    data,
  });
}
