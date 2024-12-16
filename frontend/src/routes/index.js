import React, { Suspense, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';

// 懒加载组件
const Login = React.lazy(() => import('../pages/auth/Login'));
const Register = React.lazy(() => import('../pages/auth/Register'));
const Layout = React.lazy(() => import('../components/Layout'));
const Dashboard = React.lazy(() => import('../pages/Dashboard'));
const EmployeeList = React.lazy(() => import('../pages/employee/EmployeeList'));
const EmployeeForm = React.lazy(() => import('../pages/employee/EmployeeForm'));
const EmployeeDetail = React.lazy(() => import('../pages/employee/EmployeeDetail')); 
const DepartmentList = React.lazy(() => import('../pages/department/DepartmentList'));
const PositionList = React.lazy(() => import('../pages/position/PositionList'));
const SalaryStructure = React.lazy(() => import('../pages/salary/SalaryStructure'));
const SalaryRecords = React.lazy(() => import('../pages/salary/SalaryRecords'));
const InternList = React.lazy(() => import('../pages/intern/InternList'));
const InternEvaluation = React.lazy(() => import('../pages/intern/InternEvaluation'));

// 路由保护组件
const ProtectedRoute = ({ children }) => {
  const location = useLocation();
  
  // 使用useEffect处理token检查，避免同步状态更新
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      
      if (!token) {
        const userInfo = localStorage.getItem('userInfo');
        if (userInfo) {
          try {
            const { token: storedToken } = JSON.parse(userInfo);
            if (storedToken) {
              localStorage.setItem('token', storedToken);
            }
          } catch (error) {
            console.error('解析用户信息失败:', error);
          }
        }
      }
    };
    
    checkAuth();
  }, []);

  // 获取认证状态
  const isAuthenticated = () => {
    const token = localStorage.getItem('token');
    return !!token;
  };

  return isAuthenticated() ? children : <Navigate to="/login" state={{ from: location }} replace />;
};

// 加载提示组件
const LoadingComponent = () => (
  <div style={{ 
    width: '100%', 
    height: '100vh', 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center' 
  }}>
    <Spin size="large" tip="加载中..." />
  </div>
);

// 路由配置
const AppRoutes = () => {
  // 启用 React Router v7 的新特性
  useEffect(() => {
    // 设置未来版本标志
    window.__reactRouterFutureFlags = {
      v7_startTransition: true,
      v7_relativeSplatPath: true
    };
  }, []);

  return (
    <Suspense fallback={<LoadingComponent />}>
      <Routes>
        {/* 公开路由 */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* 受保护路由 */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          {/* 仪表盘 */}
          <Route
            index
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          
          {/* 员工管理 */}
          <Route
            path="employees"
            element={
              <ProtectedRoute>
                <EmployeeList />
              </ProtectedRoute>
            }
          />
          
          {/* 实习管理路由 */}
          <Route path="intern">
            <Route
              index
              element={
                <ProtectedRoute>
                  <InternList />
                </ProtectedRoute>
              }
            />
            <Route
              path="evaluation/:id"
              element={
                <ProtectedRoute>
                  <InternEvaluation />
                </ProtectedRoute>
              }
            />
          </Route>
          
          {/* 员工管理路由 */}
          <Route path="employees">
            <Route
              index
              element={
                <ProtectedRoute>
                  <EmployeeList />
                </ProtectedRoute>
              }
            />
            <Route
              path="new"
              element={
                <ProtectedRoute>
                  <EmployeeForm />
                </ProtectedRoute>
              }
            />
            <Route
              path=":id/edit"
              element={
                <ProtectedRoute>
                  <EmployeeForm />
                </ProtectedRoute>
              }
            />
            <Route
              path=":id"
              element={
                <ProtectedRoute>
                  <EmployeeDetail />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* 部门管理路由 */}
          <Route
            path="departments"
            element={
              <ProtectedRoute>
                <DepartmentList />
              </ProtectedRoute>
            }
          />

          {/* 职位管理路由 */}
          <Route
            path="positions"
            element={
              <ProtectedRoute>
                <PositionList />
              </ProtectedRoute>
            }
          />

          {/* 薪资管理路由 */}
          <Route
            path="salary/structure"
            element={
              <ProtectedRoute>
                <SalaryStructure />
              </ProtectedRoute>
            }
          />
          <Route
            path="salary/records"
            element={
              <ProtectedRoute>
                <SalaryRecords />
              </ProtectedRoute>
            }
          />
        </Route>
      </Routes>
    </Suspense>
  );
};

export default AppRoutes;
