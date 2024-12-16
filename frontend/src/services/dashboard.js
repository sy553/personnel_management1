import request from '../utils/request';

/**
 * 获取仪表盘统计数据
 * @returns {Promise} 返回统计数据
 */
export async function getDashboardStats() {
  return request.get('/api/dashboard/stats');
}
