import axios from 'axios';
import { message } from 'antd';

/**
 * 创建axios实例
 * 配置baseURL为后端服务地址
 * 配置请求超时时间和跨域设置
 */
const request = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000', // 优先使用环境变量中的API地址
  timeout: 10000,
  withCredentials: true, // 允许跨域携带cookie
});

/**
 * 请求拦截器
 * 在发送请求之前做一些处理
 */
request.interceptors.request.use(
  config => {
    // 从localStorage获取token
    const token = localStorage.getItem('token');
    if (token) {
      // 将token添加到请求头
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    // 处理请求数据
    if (config.data instanceof FormData) {
      // 如果是FormData类型的数据，删除Content-Type让浏览器自动设置
      delete config.headers['Content-Type'];
    } else {
      // 其他情况设置为application/json
      config.headers['Content-Type'] = 'application/json';
    }

    return config;
  },
  error => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

/**
 * 响应拦截器
 * 在接收响应之后做一些处理
 */
request.interceptors.response.use(
  response => {
    // 直接返回响应数据
    return response.data;
  },
  error => {
    console.error('响应错误:', error);
    
    if (error.response) {
      const { status, data } = error.response;
      
      // 处理401未授权错误
      if (status === 401) {
        // 如果是登录接口的401错误，直接返回错误信息
        if (error.config.url === '/api/auth/login') {
          return Promise.reject({
            message: data.message || '登录失败',
            status: status,
            data: data
          });
        }
        
        // 其他接口的401错误，需要重新登录
        const currentPath = window.location.pathname;
        if (currentPath !== '/login') {
          // 保存当前路径，登录后可以重定向回来
          localStorage.setItem('redirectPath', currentPath);
        }
        // 清除认证信息
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        // 跳转到登录页
        window.location.href = '/login';
        message.error(data.message || '未授权，请重新登录');
        return Promise.reject({
          message: data.message || '未授权，请重新登录',
          status: status,
          data: data
        });
      }
      
      // 其他错误交给调用方处理
      return Promise.reject({
        message: data.message || '请求失败',
        status: status,
        data: data
      });
    }
    
    // 网络错误等其他错误
    return Promise.reject({
      message: '网络错误，请稍后重试',
      status: null,
      data: null
    });
  }
);

export default request;
