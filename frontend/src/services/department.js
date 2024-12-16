import request from '../utils/request';

/**
 * 获取部门列表
 * @returns {Promise} 返回部门列表
 */
export async function getDepartments() {
  return request.get('/api/departments');
}

/**
 * 获取单个部门信息
 * @param {number} id - 部门ID
 * @returns {Promise} 返回部门信息
 */
export async function getDepartment(id) {
  return request.get(`/api/departments/${id}`);
}

/**
 * 创建新部门
 * @param {Object} data - 部门信息
 * @returns {Promise} 返回创建结果
 */
export async function createDepartment(data) {
  return request.post('/api/departments', data);
}

/**
 * 更新部门信息
 * @param {number} id - 部门ID
 * @param {Object} data - 更新的部门信息
 * @returns {Promise} 返回更新结果
 */
export async function updateDepartment(id, data) {
  return request.put(`/api/departments/${id}`, data);
}

/**
 * 删除部门
 * @param {number} id - 部门ID
 * @returns {Promise} 返回删除结果
 */
export async function deleteDepartment(id) {
  return request.delete(`/api/departments/${id}`);
}
