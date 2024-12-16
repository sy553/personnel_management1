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
  SolutionOutlined,
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
          label: '工资结构',
          icon: <ProfileOutlined />,
        },
        {
          key: '/salary/assignments',
          label: '工资结构分配',
          icon: <ProfileOutlined />,
        },
        {
          key: '/salary/records',
          label: '工资发放',
          icon: <PayCircleOutlined />,
        },
        {
          key: '/salary/statistics',
          label: '薪资统计',
          icon: <BarChartOutlined />,
        },
        {
          key: '/salary/personal',
          label: '个人工资',
          icon: <UserOutlined />,
        },
      ],
    },
    {
      key: '/intern',
      icon: <SolutionOutlined />,
      label: '实习管理',
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
          return childItem.label; // 获取文本
        }
      }
    }
    
    // 处理实习管理子页面
    if (pathname.startsWith('/intern')) {
      const internMenu = menuItems.find(item => item.key === '/intern');
      if (internMenu) {
        return '实习管理';
      }
    }
    
    // 处理其他页面
    const item = menuItems.find(item => item.key === pathname);
    return item ? item.label : '';
  };

  // 处理菜单点击
  const handleMenuClick = ({ key }) => {
    if (key === 'logout') {
      // 处理登出
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
      navigate('/login');
      return;
    }
    navigate(key);
  };

  // 获取当前选中的菜单项
  const getSelectedKeys = () => {
    const pathname = location.pathname;
    if (pathname === '/') return ['/dashboard'];
    return [pathname];
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
          selectedKeys={getSelectedKeys()}
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
