import request from '../utils/request';

/**
 * 获取实习状态列表
 * @param {Object} params - 查询参数
 * @returns {Promise} 返回请求结果
 */
export async function getInternStatusList(params) {
  return request({
    url: '/api/intern/status',
    method: 'GET',
    params,
  });
}

/**
 * 获取实习状态详情
 * @param {string} id - 实习状态ID
 * @returns {Promise} 返回请求结果
 */
export async function getInternStatus(id) {
  return request({
    url: `/api/intern/status/${id}`,
    method: 'GET',
  });
}

/**
 * 创建实习状态
 * @param {Object} data - 实习状态数据
 * @returns {Promise} 返回请求结果
 */
export async function createInternStatus(data) {
  return request({
    url: '/api/intern/status',
    method: 'POST',
    data,
  });
}

/**
 * 更新实习状态
 * @param {string} id - 实习状态ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 返回请求结果
 */
export async function updateInternStatus(id, data) {
  return request({
    url: `/api/intern/status/${id}`,
    method: 'PUT',
    data,
  });
}

/**
 * 创建实习评估
 * @param {Object} data - 评估数据
 * @returns {Promise} 返回请求结果
 */
export async function createInternEvaluation(data) {
  return request({
    url: '/api/intern/evaluations',
    method: 'POST',
    data,
  });
}

/**
 * 获取评估详情
 * @param {string} id - 评估ID
 * @returns {Promise} 返回请求结果
 */
export async function getInternEvaluation(id) {
  return request({
    url: `/api/intern/evaluations/${id}`,
    method: 'GET',
  });
}

/**
 * 获取实习状态的所有评估
 * @param {string} statusId - 实习状态ID
 * @returns {Promise} 返回评估列表
 */
export async function getStatusEvaluations(statusId) {
  return request({
    url: `/api/intern/status/${statusId}/evaluations`,
    method: 'GET',
  });
}
