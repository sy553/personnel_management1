import React, { useState, useEffect } from 'react';
import { Layout as AntLayout, Menu, Avatar, Breadcrumb, theme } from 'antd';
import { Outlet, useNavigate, useLocation, Link } from 'react-router-dom';
import {
  UserOutlined,
  TeamOutlined,
  ApartmentOutlined,
  LogoutOutlined,
  DashboardOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  DollarOutlined,
  ProfileOutlined,
  PayCircleOutlined,
  BarChartOutlined,
} from '@ant-design/icons';
import './layout.css';

const { Header, Sider, Content } = AntLayout;

/**
 * 布局组件
 * 包含侧边栏、顶部导航和内容区域
 */
const Layout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const userName = 'Admin';
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // 菜单项配置
  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/employees',
      icon: <UserOutlined />,
      label: '员工管理',
    },
    {
      key: '/departments',
      icon: <TeamOutlined />,
      label: '部门管理',
    },
    {
      key: '/positions',
      icon: <ApartmentOutlined />,
      label: '职位管理',
    },
    {
      key: 'salary',
      icon: <DollarOutlined />,
      label: '薪资管理',
      children: [
        {
          key: '/salary/structures',
          label: <Link to="/salary/structures">工资结构</Link>,
          icon: <ProfileOutlined />,
        },
        {
          key: '/salary/assignments',
          label: <Link to="/salary/assignments">工资结构分配</Link>,
          icon: <ProfileOutlined />,
        },
        {
          key: '/salary/records',
          label: <Link to="/salary/records">工资发放</Link>,
          icon: <PayCircleOutlined />,
        },
        {
          key: '/salary/statistics',
          label: <Link to="/salary/statistics">薪资统计</Link>,
          icon: <BarChartOutlined />,
        },
        {
          key: '/salary/personal',
          label: <Link to="/salary/personal">个人工资</Link>,
          icon: <UserOutlined />,
        },
      ],
    },
    {
      type: 'divider'
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出系统',
      danger: true,
    }
  ];

  /**
   * 获取面包屑标题
   * @param {string} pathname - 当前路径
   * @returns {string} 面包屑标题
   */
  const getBreadcrumbTitle = (pathname) => {
    // 处理薪资管理子页面
    if (pathname.startsWith('/salary/')) {
      const salaryMenu = menuItems.find(item => item.key === 'salary');
      if (salaryMenu && salaryMenu.children) {
        const childItem = salaryMenu.children.find(child => child.key === pathname);
        if (childItem) {
          return childItem.label.props.children; // 获取Link组件内的文本
        }
      }
    }
    
    // 处理其他页面
    const item = menuItems.find(item => item.key === pathname);
    return item ? item.label : '';
  };

  /**
   * 处理菜单点击
   * @param {Object} param - 点击参数
   * @param {string} param.key - 菜单项的key
   */
  const handleMenuClick = ({ key }) => {
    // 如果是登出操作
    if (key === 'logout') {
      localStorage.removeItem('token');
      navigate('/login');
      return;
    }
    
    // 检查用户权限和登录状态
    const token = localStorage.getItem('token');
    if (!token) {
      // 如果未登录，先获取token
      const userInfo = localStorage.getItem('userInfo');
      if (userInfo) {
        localStorage.setItem('token', JSON.parse(userInfo).token);
      }
    }
    
    // 如果不是Link包装的菜单项，则直接导航
    if (!key.startsWith('/salary/')) {
      navigate(key);
    }
  };

  // 获取当前页面的面包屑标题
  const currentTitle = getBreadcrumbTitle(location.pathname);

  return (
    <AntLayout>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        className="app-sider"
      >
        <div className="logo">
          {!collapsed && <span className="logo-text">人事管理系统</span>}
        </div>
        <Menu
          theme="dark"
          selectedKeys={[location.pathname]}
          defaultOpenKeys={['salary']}
          mode="inline"
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Sider>
      <AntLayout>
        <Header className="app-header" style={{ background: colorBgContainer }}>
          {React.createElement(collapsed ? MenuUnfoldOutlined : MenuFoldOutlined, {
            className: 'trigger',
            onClick: () => setCollapsed(!collapsed),
          })}
          <Breadcrumb className="app-breadcrumb" items={[
            { title: '首页' },
            ...(currentTitle ? [{ title: currentTitle }] : [])
          ]} />
          <div className="header-right">
            <Avatar icon={<UserOutlined />} />
            <span className="user-name">{userName}</span>
          </div>
        </Header>
        <Content className="app-content" style={{ background: colorBgContainer, borderRadius: borderRadiusLG }}>
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;
