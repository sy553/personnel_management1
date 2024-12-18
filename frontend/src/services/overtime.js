// overtime.js - 加班管理相关的API服务

import request from '../utils/request';

/**
 * 获取加班记录列表
 * @param {Object} params - 请求参数
 * @param {number} [params.employee_id] - 员工ID（可选）
 * @param {string} [params.start_time] - 开始时间 (YYYY-MM-DD HH:mm:ss)
 * @param {string} [params.end_time] - 结束时间 (YYYY-MM-DD HH:mm:ss)
 * @param {string} [params.status] - 状态（pending-待审批, approved-已批准, rejected-已拒绝）
 * @returns {Promise} 返回加班记录列表
 */
export async function getOvertimeRecords(params) {
  return request('/api/overtime', {
    method: 'GET',
    params,
  });
}

/**
 * 创建加班申请
 * @param {Object} data - 加班申请数据
 * @param {string} data.start_time - 开始时间 (YYYY-MM-DD HH:mm:ss)
 * @param {string} data.end_time - 结束时间 (YYYY-MM-DD HH:mm:ss)
 * @param {string} [data.reason] - 加班原因（可选）
 * @returns {Promise} 返回创建结果
 */
export async function createOvertimeRequest(data) {
  return request('/api/overtime', {
    method: 'POST',
    data,
  });
}

/**
 * 审批加班申请
 * @param {number} id - 加班记录ID
 * @param {Object} data - 审批数据
 * @param {string} data.status - 审批状态（approved-批准, rejected-拒绝）
 * @param {string} [data.comment] - 审批意见（可选）
 * @returns {Promise} 返回审批结果
 */
export async function approveOvertimeRequest(id, data) {
  return request(`/api/overtime/${id}/approve`, {
    method: 'POST',
    data,
  });
}
