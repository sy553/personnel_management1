import request from '../utils/request';

const authService = {
  /**
   * 用户登录
   * @param {Object} params - 登录参数
   * @param {string} params.username - 用户名
   * @param {string} params.password - 密码
   * @returns {Promise<Object>} 登录结果
   */
  login: async (params) => {
    try {
      console.log('Auth service: Attempting login with params:', params);
      const response = await request.post('/api/auth/login', params);
      console.log('Auth service: Received login response:', response);
      
      // 登录成功
      if (response?.data?.token && response?.data?.user) {
        // 保存token和用户信息到localStorage
        localStorage.setItem('token', response.data.token);
        localStorage.setItem('auth', JSON.stringify(response.data.user));
        // 设置token过期时间（24小时）
        const expiresAt = new Date().getTime() + 24 * 60 * 60 * 1000;
        localStorage.setItem('tokenExpiresAt', expiresAt.toString());
        
        return response.data;
      }
      
      // 登录失败但有错误信息
      if (response?.message) {
        throw new Error(response.message);
      }
      
      // 其他未知错误
      throw new Error('登录失败，请重试');
    } catch (error) {
      console.error('Auth service: Login error:', {
        message: error.message || '登录失败',
        response: error.response,
        data: error.data,
        status: error.status
      });
      
      // 确保错误信息被正确传递
      if (error.data?.message) {
        throw new Error(error.data.message);
      }
      throw error;
    }
  },

  /**
   * 检查用户是否已登录
   * @returns {boolean} 是否已登录
   */
  isAuthenticated: () => {
    const token = localStorage.getItem('token');
    const expiresAt = localStorage.getItem('tokenExpiresAt');
    
    if (!token || !expiresAt) {
      return false;
    }

    // 检查token是否过期
    const now = new Date().getTime();
    if (now > parseInt(expiresAt)) {
      // 清除过期的token
      authService.clearAuth();
      return false;
    }

    return true;
  },

  /**
   * 清除认证信息
   */
  clearAuth: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
    localStorage.removeItem('tokenExpiresAt');
  },

  /**
   * 用户注册
   * @param {Object} params - 注册参数
   * @param {string} params.username - 用户名
   * @param {string} params.password - 密码
   * @param {string} params.email - 邮箱
   * @returns {Promise<Object>} 注册结果
   */
  register: async (params) => {
    try {
      console.log('Auth service: Attempting registration with params:', params);
      const response = await request.post('/api/auth/register', params);
      console.log('Auth service: Registration response:', response);
      
      // 处理201和200状态码
      if (response?.code === undefined && response?.data?.user) {
        return {
          code: 200,
          message: '注册成功',
          data: response.data
        };
      }
      return response;
    } catch (error) {
      console.error('Auth service: Registration error:', error);
      throw error;
    }
  },

  /**
   * 发送重置密码验证码
   * @param {Object} params - 发送验证码参数
   * @param {string} params.email - 邮箱地址
   * @returns {Promise<Object>} 发送结果
   */
  sendResetCode: async (params) => {
    try {
      console.log('Auth service: Sending reset code to:', params.email);
      const response = await request.post('/api/auth/send-reset-code', params);
      console.log('Auth service: Reset code sent response:', response);
      return response; // 直接返回完整的响应，包含 code、message 和 data
    } catch (error) {
      console.error('Auth service: Send reset code error:', error);
      throw error;
    }
  },

  /**
   * 重置密码
   * @param {Object} params - 重置密码参数
   * @param {string} params.email - 邮箱
   * @param {string} params.code - 验证码
   * @param {string} params.new_password - 新密码
   * @returns {Promise<Object>} 重置结果
   */
  resetPassword: async (params) => {
    try {
      console.log('Auth service: Attempting password reset with params:', params);
      const response = await request.post('/api/auth/reset-password', params);
      console.log('Auth service: Password reset response:', response);
      return response;  // 返回完整响应，不再只返回data
    } catch (error) {
      console.error('Auth service: Password reset error:', error);
      throw error;
    }
  },

  /**
   * 退出登录
   * @returns {Promise<Object>} 退出结果
   */
  logout: async () => {
    try {
      console.log('Auth service: Attempting logout');
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
      localStorage.removeItem('tokenExpiresAt');
      return { code: 200, message: '退出登录成功' };
    } catch (error) {
      console.error('Auth service: Logout error:', error);
      throw error;
    }
  },

  /**
   * 获取当前用户信息
   * @returns {Promise<Object>} 用户信息
   */
  getCurrentUser: async () => {
    try {
      console.log('Auth service: Fetching current user');
      const response = await request.get('/api/auth/profile');
      console.log('Auth service: Current user data:', response);
      return response.data;
    } catch (error) {
      console.error('Auth service: Get current user error:', error);
      throw error;
    }
  }
};

export default authService;
