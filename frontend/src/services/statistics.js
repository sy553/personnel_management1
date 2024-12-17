// statistics.js - 考勤统计相关的API服务

import request from '../utils/request';

/**
 * 获取考勤统计数据
 * @param {Object} params - 请求参数
 * @param {string} params.start_date - 开始日期 (YYYY-MM-DD)
 * @param {string} params.end_date - 结束日期 (YYYY-MM-DD)
 * @param {number} [params.department_id] - 部门ID（可选）
 * @returns {Promise} 返回统计数据
 */
export async function getAttendanceStatistics(params) {
  return request('/api/attendance/statistics', {
    method: 'GET',
    params,
  });
}

/**
 * 获取部门考勤统计数据
 * @param {Object} params - 请求参数
 * @param {string} params.start_date - 开始日期 (YYYY-MM-DD)
 * @param {string} params.end_date - 结束日期 (YYYY-MM-DD)
 * @param {number} params.department_id - 部门ID
 * @returns {Promise} 返回部门统计数据
 */
export async function getDepartmentStatistics(params) {
  return request('/api/attendance/department-statistics', {
    method: 'GET',
    params,
  });
}

/**
 * 导出考勤统计数据
 * @param {Object} params - 请求参数
 * @param {string} params.start_date - 开始日期 (YYYY-MM-DD)
 * @param {string} params.end_date - 结束日期 (YYYY-MM-DD)
 * @param {number} [params.department_id] - 部门ID（可选）
 * @returns {Promise} 返回导出文件URL
 */
export async function exportStatistics(params) {
  return request('/api/attendance/export-statistics', {
    method: 'GET',
    params,
    responseType: 'blob',
  });
}
