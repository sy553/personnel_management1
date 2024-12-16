import request from '../utils/request';

/**
 * 获取职位列表
 * @returns {Promise} 返回职位列表
 */
export async function getPositions() {
  return request.get('/api/positions');
}

/**
 * 获取单个职位信息
 * @param {number} id - 职位ID
 * @returns {Promise} 返回职位信息
 */
export async function getPosition(id) {
  return request.get(`/api/positions/${id}`);
}

/**
 * 创建新职位
 * @param {Object} data - 职位信息
 * @returns {Promise} 返回创建结果
 */
export async function createPosition(data) {
  return request.post('/api/positions', data);
}

/**
 * 更新职位信息
 * @param {number} id - 职位ID
 * @param {Object} data - 更新的职位信息
 * @returns {Promise} 返回更新结果
 */
export async function updatePosition(id, data) {
  return request.put(`/api/positions/${id}`, data);
}

/**
 * 删除职位
 * @param {number} id - 职位ID
 * @returns {Promise} 返回删除结果
 */
export async function deletePosition(id) {
  return request.delete(`/api/positions/${id}`);
}
