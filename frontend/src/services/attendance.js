// attendance.js - 考勤相关的API服务

import request from '../utils/request';

const BASE_URL = '/api/attendance';

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

// 获取打卡地点列表
export async function getCheckInLocations() {
  return request('/api/attendance/locations', {
    method: 'GET',
  });
}

// 外勤打卡
export async function createFieldWorkRecord(data) {
  return request('/api/attendance/field-work', {
    method: 'POST',
    data,
  });
}

// 补卡申请
export async function createMakeupRecord(data) {
  return request('/api/attendance/makeup', {
    method: 'POST',
    data,
  });
}

// 获取补卡申请列表
export async function getMakeupRecords(params) {
  return request('/api/attendance/makeup', {
    method: 'GET',
    params,
  });
}

// 审批补卡申请
export async function approveMakeupRecord(id, data) {
  return request(`/api/attendance/makeup/${id}`, {
    method: 'PUT',
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

/**
 * 考勤规则相关API
 */

// 获取考勤规则列表
export const getAttendanceRules = () => {
  return request({
    url: `${BASE_URL}/rules`,
    method: 'get'
  });
};

// 创建考勤规则
export const createAttendanceRule = (data) => {
  // 直接使用传入的数据，因为已经在Rules.js中格式化过了
  return request({
    url: `${BASE_URL}/rules`,
    method: 'post',
    data: data
  });
};

// 更新考勤规则
export const updateAttendanceRule = (id, data) => {
  // 直接使用传入的数据，因为已经在Rules.js中格式化过了
  return request({
    url: `${BASE_URL}/rules/${id}`,
    method: 'put',
    data: data
  });
};

// 删除考勤规则
export const deleteAttendanceRule = (id) => {
  return request({
    url: `${BASE_URL}/rules/${id}`,
    method: 'delete'
  });
};

/**
 * 分配规则到部门
 * @param {number} ruleId - 规则ID
 * @param {number[]} departmentIds - 部门ID列表
 * @returns {Promise} 请求结果
 */
export async function assignRuleToDepartment(ruleId, departmentIds) {
  return request(`/api/attendance/rules/${ruleId}/assign/department`, {
    method: 'POST',
    data: {
      department_ids: departmentIds
    }
  });
}

/**
 * 分配规则到员工
 * @param {number} ruleId - 规则ID
 * @param {number[]} employeeIds - 员工ID列表
 * @returns {Promise} 请求结果
 */
export async function assignRuleToEmployees(ruleId, employeeIds) {
  return request(`/api/attendance/rules/${ruleId}/assign/employee`, {
    method: 'POST',
    data: {
      employee_ids: employeeIds
    }
  });
}

// 获取员工的考勤规则
export const getEmployeeRules = (employeeId) => {
  return request({
    url: `${BASE_URL}/rules/employee/${employeeId}`,
    method: 'get'
  });
};

// 获取员工在指定日期的有效考勤规则
export const getEmployeeActiveRule = (employeeId, date) => {
  return request({
    url: `${BASE_URL}/rules/employee/${employeeId}/active`,
    method: 'get',
    params: { date }
  });
};

// 获取特定日期的活动规则
export async function getActiveRule(date) {
  return request('/api/attendance-rules/active', {
    method: 'GET',
    params: { date },
  });
}

/**
 * 获取规则的分配信息
 * @param {number} ruleId - 规则ID
 * @returns {Promise} 请求结果
 */
export async function getRuleAssignments(ruleId) {
  return request(`/api/attendance/rules/${ruleId}/assignments`, {
    method: 'GET'
  });
}

/**
 * 取消部门的规则分配
 * @param {number} ruleId - 规则ID
 * @param {number} departmentId - 部门ID
 * @returns {Promise} 请求结果
 */
export async function unassignRuleFromDepartment(ruleId, departmentId) {
  return request(`/api/attendance/rules/${ruleId}/assignments/department/${departmentId}`, {
    method: 'DELETE'
  });
}

/**
 * 取消员工的规则分配
 * @param {number} ruleId - 规则ID
 * @param {number} employeeId - 员工ID
 * @returns {Promise} 请求结果
 */
export async function unassignRuleFromEmployee(ruleId, employeeId) {
  return request(`/api/attendance/rules/${ruleId}/assignments/employee/${employeeId}`, {
    method: 'DELETE'
  });
}
