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
