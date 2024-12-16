import request from '../utils/request';

/**
 * 获取当前登录用户信息
 * @returns {Promise} 返回包含用户信息的Promise对象
 */
export const getCurrentUser = () => {
  return request.get('/api/users/current');
};

/**
 * 更新用户信息
 * @param {Object} data - 要更新的用户数据
 * @returns {Promise} 返回更新结果的Promise对象
 */
export const updateUserProfile = (data) => {
  return request.put('/api/users/profile', data);
};

/**
 * 修改密码
 * @param {Object} data - 包含旧密码和新密码的对象
 * @returns {Promise} 返回修改结果的Promise对象
 */
export const changePassword = (data) => {
  return request.put('/api/users/password', data);
};
