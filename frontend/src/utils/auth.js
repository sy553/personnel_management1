import { message } from 'antd';

/**
 * 认证相关的工具函数
 */

/**
 * 获取存储的token
 * @returns {string|null} token字符串或null
 */
export const getToken = () => {
  return localStorage.getItem('token');
};

/**
 * 设置token
 * @param {string} token - 要存储的token
 */
export const setToken = (token) => {
  localStorage.setItem('token', token);
};

/**
 * 移除token
 */
export const removeToken = () => {
  localStorage.removeItem('token');
};

/**
 * 检查用户是否已认证
 * @returns {boolean} 是否已认证
 */
export const isAuthenticated = () => {
  const token = getToken();
  if (!token) return false;
  
  try {
    // 检查token是否过期
    const tokenData = JSON.parse(atob(token.split('.')[1]));
    const expirationTime = tokenData.exp * 1000; // 转换为毫秒
    return expirationTime > Date.now();
  } catch (error) {
    console.error('Token验证失败:', error);
    return false;
  }
};

/**
 * 检查token是否即将过期
 * @param {number} thresholdMinutes - 过期阈值（分钟）
 * @returns {boolean} 是否即将过期
 */
export const isTokenExpiringSoon = (thresholdMinutes = 5) => {
  const token = getToken();
  if (!token) return false;

  try {
    const tokenData = JSON.parse(atob(token.split('.')[1]));
    const expirationTime = tokenData.exp * 1000;
    const timeUntilExpiry = expirationTime - Date.now();
    return timeUntilExpiry > 0 && timeUntilExpiry < thresholdMinutes * 60 * 1000;
  } catch (error) {
    console.error('Token验证失败:', error);
    return false;
  }
};

/**
 * 获取当前用户信息
 * @returns {Object|null} 用户信息对象或null
 */
export const getCurrentUser = () => {
  const token = getToken();
  if (!token) return null;

  try {
    const tokenData = JSON.parse(atob(token.split('.')[1]));
    return {
      id: tokenData.user_id,
      username: tokenData.username,
      role: tokenData.role,
    };
  } catch (error) {
    console.error('获取用户信息失败:', error);
    return null;
  }
};

/**
 * 获取用户信息
 * @returns {Object|null} 返回用户信息对象，如果不存在则返回null
 */
export const getUserInfo = () => {
  try {
    const userInfoStr = localStorage.getItem('userInfo');
    if (!userInfoStr) {
      return null;
    }
    return JSON.parse(userInfoStr);
  } catch (error) {
    console.error('解析用户信息失败:', error);
    return null;
  }
};

/**
 * 检查用户是否已登录
 * @returns {boolean} 返回是否已登录
 */
export const isLoggedIn = () => {
  const token = localStorage.getItem('token');
  const userInfo = getUserInfo();
  return !!(token && userInfo);
};

/**
 * 检查用户是否有员工信息
 * @returns {boolean} 返回是否有员工信息
 */
export const hasEmployeeInfo = () => {
  const user = getUserInfo();
  return user && user.employee_id !== null;  // 使用新的employee_id字段
};

/**
 * 获取员工ID
 * @returns {number|null} 返回员工ID，如果不存在则返回null
 */
export const getEmployeeId = () => {
  const user = getUserInfo();
  return user ? user.employee_id : null;  // 使用新的employee_id字段
};
