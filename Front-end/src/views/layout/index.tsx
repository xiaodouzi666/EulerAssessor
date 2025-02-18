import React from 'react';
import { Flex, Layout } from 'antd';
import { Outlet } from 'react-router-dom';
import { SideBarMenu } from '@components';

const { Header, Footer, Sider, Content } = Layout;

const headerStyle: React.CSSProperties = {
  textAlign: 'center',
  color: '#fff',
  height: 64,
  paddingInline: 48,
  lineHeight: '64px',
  // backgroundColor: '#4096ff',
};

const contentStyle: React.CSSProperties = {
  // textAlign: 'center',
  minHeight: 120,
  // lineHeight: '120px',
  color: '#fff',
  // backgroundColor: '#0958d9',
  flex: 1,
  height: '100%',
  backgroundColor: '#fff',
};

const siderStyle: React.CSSProperties = {
  textAlign: 'center',
  lineHeight: '120px',
  color: '#fff',
  // backgroundColor: '#1677ff',
};

const footerStyle: React.CSSProperties = {
  textAlign: 'center',
  color: '#fff',
  // backgroundColor: '#4096ff',
};

const layoutStyle = {
  // borderRadius: 8,
  overflow: 'hidden',
  width: '100%',
  height: '100vh',
  maxWidth: '100%',
};

export default function AppLayout() {
  return (
    <Layout style={layoutStyle}>
      <Sider width="200px" style={siderStyle}>
        <SideBarMenu />
      </Sider>
      <Layout>
        {/* <Header style={headerStyle}>Header</Header> */}
        <Content style={contentStyle}>
          <Outlet />
        </Content>
        {/* <Footer style={footerStyle}>Footer</Footer> */}
      </Layout>
    </Layout>
  );
}
