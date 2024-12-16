import React from 'react';
import { Menu } from 'antd';
import { UserOutlined } from '@ant-design/icons';

const TestLayout = () => {
  return (
    <div style={{ width: 256 }}>
      <Menu
        defaultSelectedKeys={['1']}
        defaultOpenKeys={['sub1']}
        mode="inline"
        theme="dark"
      >
        <Menu.Item key="1" icon={<UserOutlined />}>
          测试菜单项 1
        </Menu.Item>
        <Menu.Item key="2" icon={<UserOutlined />}>
          测试菜单项 2
        </Menu.Item>
      </Menu>
    </div>
  );
};

export default TestLayout;
