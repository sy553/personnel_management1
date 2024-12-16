import { theme } from 'antd';

// 自定义主题配置
export const customTheme = {
  algorithm: theme.defaultAlgorithm,
  token: {
    // 品牌色
    colorPrimary: '#1890ff',
    // 链接色
    colorLink: '#1890ff',
    // 成功色
    colorSuccess: '#52c41a',
    // 警告色
    colorWarning: '#faad14',
    // 错误色
    colorError: '#ff4d4f',
    // 主字号
    fontSize: 14,
    // 圆角
    borderRadius: 6,
    // 线框
    wireframe: false,
  },
  components: {
    Button: {
      // 按钮相关样式
      colorPrimary: 'var(--button-primary-color, #1890ff)',
      colorPrimaryHover: 'var(--button-primary-hover-color, #40a9ff)',
      colorPrimaryActive: 'var(--button-primary-active-color, #096dd9)',
      borderRadius: 6,
      controlHeight: 40,
      controlHeightLG: 48,
      controlHeightSM: 32,
      paddingContentHorizontal: 24,
    },
    Input: {
      // 输入框相关样式
      colorBgContainer: 'var(--input-background-color, #ffffff)',
      colorBorder: 'var(--input-border-color, #d9d9d9)',
      colorText: 'var(--input-text-color, rgba(0, 0, 0, 0.88))',
      borderRadius: 6,
      controlHeight: 40,
      controlHeightLG: 48,
      controlHeightSM: 32,
      paddingContentHorizontal: 16,
    },
    Card: {
      // 卡片相关样式
      borderRadiusLG: 8,
      boxShadowTertiary: '0 1px 2px 0 rgba(0, 0, 0, 0.03), 0 1px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px 0 rgba(0, 0, 0, 0.02)',
      colorBgContainer: '#ffffff',
      paddingLG: 24,
    },
    Menu: {
      // 菜单相关样式
      itemBg: 'var(--menu-background-color, transparent)',
      itemColor: 'var(--menu-text-color, rgba(0, 0, 0, 0.88))',
      itemSelectedColor: 'var(--menu-selected-text-color, #1890ff)',
      itemHoverColor: 'var(--menu-hover-text-color, #1890ff)',
      itemSelectedBg: 'var(--menu-selected-bg-color, #e6f4ff)',
      itemHoverBg: 'var(--menu-hover-bg-color, #f5f5f5)',
    },
    Message: {
      // 消息提示相关样式
      borderRadius: 8,
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
      contentPadding: '12px 20px',
    },
  },
};
