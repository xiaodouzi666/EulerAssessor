import React from 'react';
import {
  AppstoreOutlined,
  MailOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';

type MenuItem = Required<MenuProps>['items'][number];

const items: MenuItem[] = [
  {
    key: '/',
    label: '迁移可行性评估建议',
    // icon: <MailOutlined />,
  },
  {
    type: 'divider',
  },
  {
    key: '/environment',
    label: '环境兼容信息收集',
    // icon: <SettingOutlined />,
  },
  {
    key: '/software',
    label: '软件包分析',
  },
  {
    key: '/configuration',
    label: '配置文件对比',
  },
  {
    key: '/compatibility',
    label: '兼容性分析',
  },
];

const SideBarMenu: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const onClick: MenuProps['onClick'] = (e) => {
    navigate(e.key as string);
    console.log(navigate, 'click ', e);
  };

  return (
    <Menu
      onClick={onClick}
      style={{
        width: 200,
        height: '100vh',
        backgroundColor: 'rgba(22,119, 255, 0.5)',
        textAlign: 'left',
      }}
      defaultSelectedKeys={[location.pathname]}
      mode="inline"
      theme="dark"
      items={items}
    />
  );
};

export default SideBarMenu;
