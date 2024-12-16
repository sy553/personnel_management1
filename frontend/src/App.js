import React, { useEffect } from 'react';
import { ConfigProvider } from 'antd';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { startTransition } from 'react';
import './App.css';
import LoginForm from './pages/login';  
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import EmployeeList from './pages/employee/EmployeeList';
import DepartmentList from './pages/department/DepartmentList';
import PositionList from './pages/position/PositionList';
import SalaryStructure from './pages/salary/SalaryStructure';
import SalaryRecords from './pages/salary/Records';
import SalaryStatistics from './pages/salary/Statistics';
import PersonalSalary from './pages/salary/Personal';
import SalaryStructureAssignments from './pages/salary/SalaryStructureAssignments';
import PrivateRoute from './components/common/PrivateRoute';

// 配置React Router v7的特性标志
if (typeof window !== 'undefined') {
  window.__reactRouterFutureFlags = {
    v7_startTransition: true,
    v7_relativeSplatPath: true
  };
}

const App = () => {
  // 使用useEffect确保路由配置在组件挂载后生效
  useEffect(() => {
    // 使用startTransition包装状态更新
    startTransition(() => {
      // 这里可以放置需要在路由变化时进行的状态更新
    });
  }, []);

  return (
    <ConfigProvider>
      <Router future={{ v7_startTransition: true }}>
        <Routes>
          {/* 登录路由 */}
          <Route path="/login" element={<LoginForm />} />

          {/* 根路由重定向到登录页面 */}
          <Route 
            path="/" 
            element={<Navigate to="/login" replace />} 
          />

          {/* 受保护的路由 */}
          <Route 
            element={<PrivateRoute />}
            future={{ v7_relativeSplatPath: true }}
          >
            <Route 
              element={<Layout />}
              future={{ v7_relativeSplatPath: true }}
            >
              <Route 
                path="/dashboard" 
                element={<Dashboard />} 
              />
              <Route 
                path="/employees" 
                element={<EmployeeList />} 
              />
              <Route 
                path="/departments" 
                element={<DepartmentList />} 
              />
              <Route 
                path="/positions" 
                element={<PositionList />} 
              />
              {/* 薪资管理路由 */}
              <Route path="/salary">
                <Route path="structures" element={<SalaryStructure />} />
                <Route path="assignments" element={<SalaryStructureAssignments />} />
                <Route path="records" element={<SalaryRecords />} />
                <Route path="statistics" element={<SalaryStatistics />} />
                <Route path="personal" element={<PersonalSalary />} />
              </Route>
            </Route>
          </Route>

          {/* 404 重定向到登录页面 */}
          <Route 
            path="*" 
            element={<Navigate to="/login" replace />} 
          />
        </Routes>
      </Router>
    </ConfigProvider>
  );
};

export default App;
