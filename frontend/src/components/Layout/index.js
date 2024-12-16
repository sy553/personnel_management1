import React, { useState, useEffect } from 'react';
import { Layout, Menu, Button, Dropdown, message } from 'antd';
import { MenuFoldOutlined, MenuUnfoldOutlined, LogoutOutlined, UserOutlined } from '@ant-design/icons';
import { useNavigate, useLocation, Outlet } from 'react-router-dom';
import menuConfig from '../../config/menu';
import { getCurrentUser } from '../../services/user';  
import './style.css';

const { Header, Sider, Content } = Layout;

/**
 * 主布局组件
 * 包含顶部导航栏、侧边菜单和主要内容区域
 */
const MainLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);  

  // 获取当前用户信息
  useEffect(() => {
    const fetchCurrentUser = async () => {
      try {
        const response = await getCurrentUser();
        if (response.code === 200) {
          setCurrentUser(response.data);
          // 更新localStorage中的用户信息
          localStorage.setItem('userInfo', JSON.stringify(response.data));
        }
      } catch (error) {
        console.error('获取当前用户信息失败:', error);
        message.error('获取用户信息失败，请重新登录');
        // 如果获取用户信息失败，可能是token过期，跳转到登录页
        navigate('/login');
      }
    };
    fetchCurrentUser();
  }, [navigate]);

  // 从localStorage获取用户信息
  const userInfo = currentUser || JSON.parse(localStorage.getItem('userInfo') || '{}');

  // 处理菜单点击
  const handleMenuClick = ({ key }) => {
    const menuItem = findMenuItemByKey(key, menuConfig);
    if (menuItem && menuItem.path) {
      navigate(menuItem.path);
    }
  };

  // 递归查找菜单项
  const findMenuItemByKey = (key, items) => {
    for (const item of items) {
      if (item.key === key) return item;
      if (item.children) {
        const found = findMenuItemByKey(key, item.children);
        if (found) return found;
      }
    }
    return null;
  };

  // 获取当前选中的菜单项
  const getSelectedKeys = () => {
    const pathname = location.pathname;
    const findKeyByPath = (items) => {
      for (const item of items) {
        if (item.path === pathname) return [item.key];
        if (item.children) {
          const found = findKeyByPath(item.children);
          if (found) return found;
        }
      }
      return [];
    };
    return findKeyByPath(menuConfig);
  };

  // 获取打开的子菜单
  const getOpenKeys = () => {
    const pathname = location.pathname;
    const findOpenKeys = (items, parentKey = null) => {
      for (const item of items) {
        if (item.path === pathname && parentKey) return [parentKey];
        if (item.children) {
          const found = findOpenKeys(item.children, item.key);
          if (found) return found;
        }
      }
      return [];
    };
    return findOpenKeys(menuConfig);
  };

  // 处理退出登录
  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userInfo');
    navigate('/login');
  };

  // 用户菜单项
  const userMenuItems = [
    {
      key: '1',
      label: '个人信息',
      icon: <UserOutlined />,
      onClick: () => navigate('/profile'),
    },
    {
      key: '2',
      label: '退出登录',
      icon: <LogoutOutlined />,
      onClick: handleLogout,
    },
  ];

  // 渲染菜单项
  const renderMenuItems = (items) => {
    return items.map(item => {
      if (item.children) {
        return {
          key: item.key,
          icon: item.icon ? React.createElement(item.icon) : null,
          label: item.label,
          children: renderMenuItems(item.children),
        };
      }
      return {
        key: item.key,
        icon: item.icon ? React.createElement(item.icon) : null,
        label: item.label,
      };
    });
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider 
        trigger={null} 
        collapsible 
        collapsed={collapsed}
        theme="light"
      >
        <div className="logo">
          {!collapsed && <span>人事管理系统</span>}
        </div>
        <Menu
          mode="inline"
          selectedKeys={getSelectedKeys()}
          defaultOpenKeys={getOpenKeys()}
          items={renderMenuItems(menuConfig)}
          onClick={handleMenuClick}
        />
      </Sider>
      <Layout>
        <Header className="site-layout-header">
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
          />
          <div className="header-right">
            <Dropdown
              menu={{ items: userMenuItems }}
              placement="bottomRight"
            >
              <span className="user-info">
                <UserOutlined className="user-avatar" />
                <span className="username">{userInfo.username || '用户'}</span>
              </span>
            </Dropdown>
          </div>
        </Header>
        <Content className="site-layout-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
