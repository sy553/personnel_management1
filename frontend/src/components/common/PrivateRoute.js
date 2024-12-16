import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import authService from '../../services/auth';

/**
 * PrivateRoute组件 - 用于保护需要认证的路由
 * @param {Object} props - 组件属性
 * @param {React.ReactNode} props.children - 子组件
 * @returns {React.ReactNode} 渲染的组件
 */
const PrivateRoute = ({ children }) => {
  const location = useLocation();
  const isAuthenticated = authService.isAuthenticated();

  // 如果未认证，重定向到登录页面
  if (!isAuthenticated) {
    // 保存当前路径，以便登录后返回
    const currentPath = location.pathname + location.search + location.hash;
    sessionStorage.setItem('returnPath', currentPath);
    
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 如果已认证，渲染受保护的组件
  return children || <Outlet />;
};

export default PrivateRoute;
