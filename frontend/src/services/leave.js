// leave.js - 请假管理相关的API服务

import request from '../utils/request';

/**
 * 获取请假记录列表
 * @param {Object} params - 请求参数
 * @param {number} [params.employee_id] - 员工ID（可选）
 * @param {string} [params.start_date] - 开始日期 (YYYY-MM-DD)
 * @param {string} [params.end_date] - 结束日期 (YYYY-MM-DD)
 * @param {string} [params.status] - 状态（pending-待审批, approved-已批准, rejected-已拒绝）
 * @returns {Promise} 返回请假记录列表
 */
export async function getLeaveRecords(params) {
  return request('/api/leave', {
    method: 'GET',
    params,
  });
}

/**
 * 创建请假申请
 * @param {Object} data - 请假申请数据
 * @param {string} data.leave_type - 请假类型（sick-病假, personal-事假, annual-年假）
 * @param {string} data.start_date - 开始日期 (YYYY-MM-DD)
 * @param {string} data.end_date - 结束日期 (YYYY-MM-DD)
 * @param {string} [data.reason] - 请假原因（可选）
 * @returns {Promise} 返回创建结果
 */
export async function createLeaveRequest(data) {
  return request('/api/leave', {
    method: 'POST',
    data,
  });
}

/**
 * 审批请假申请
 * @param {number} id - 请假记录ID
 * @param {Object} data - 审批数据
 * @param {string} data.status - 审批状态（approved-批准, rejected-拒绝）
 * @param {string} [data.comment] - 审批意见（可选）
 * @returns {Promise} 返回审批结果
 */
export async function approveLeaveRequest(id, data) {
  return request(`/api/leave/${id}/approve`, {
    method: 'POST',
    data,
  });
}
