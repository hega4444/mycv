import type { ReactNode } from 'react';
import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Avatar, Dropdown, Typography, Modal, Grid } from 'antd';
import {
  HomeOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  MenuOutlined,
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { Settings } from '../pages/Settings';

const { Header, Content } = Layout;
const { Title } = Typography;
const { useBreakpoint } = Grid;

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const screens = useBreakpoint();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigation = [
    { key: '/', label: 'Dashboard', icon: <HomeOutlined /> },
    { key: '/profile', label: 'Profile', icon: <UserOutlined /> },
    {
      key: 'settings',
      label: 'Settings',
      icon: <SettingOutlined />,
      onClick: () => setSettingsOpen(true),
    },
  ];

  const userMenuItems = [
    {
      key: 'logout',
      label: 'Logout',
      icon: <LogoutOutlined />,
      onClick: handleLogout,
    },
  ];

  const mobileMenuItems = [
    ...navigation.map(item => ({
      ...item,
      onClick: item.onClick || (() => navigate(item.key)),
    })),
    {
      key: 'logout',
      label: 'Logout',
      icon: <LogoutOutlined />,
      onClick: handleLogout,
    },
  ];

  return (
    <Layout className="min-h-screen">
      <Header style={{
        background: '#fff',
        padding: screens.md ? '0 24px' : '0 16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: 64,
        lineHeight: 'normal'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', flex: 1, minWidth: 0 }}>
          <Title level={screens.md ? 3 : 4} style={{
            margin: 0,
            background: 'linear-gradient(90deg, #1677ff 0%, #69b1ff 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            whiteSpace: 'nowrap'
          }}>
            myCV
          </Title>

          {screens.md && (
            <Menu
              mode="horizontal"
              selectedKeys={[location.pathname]}
              onClick={({ key, domEvent }) => {
                const item = navigation.find((nav) => nav.key === key);
                if (item?.onClick) {
                  domEvent.preventDefault();
                  item.onClick();
                } else {
                  navigate(key);
                }
              }}
              items={navigation}
              style={{ marginLeft: 24, flex: 1, minWidth: 0, border: 'none' }}
            />
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {!screens.md ? (
            <Dropdown
              menu={{
                items: mobileMenuItems,
                onClick: ({ key }) => {
                  const item = mobileMenuItems.find(i => i.key === key);
                  item?.onClick?.();
                }
              }}
              placement="bottomRight"
              arrow
            >
              <MenuOutlined style={{ fontSize: 20, cursor: 'pointer' }} />
            </Dropdown>
          ) : (
            <Dropdown
              menu={{ items: userMenuItems }}
              placement="bottomRight"
              arrow
            >
              <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
                <Avatar style={{ backgroundColor: '#1677ff' }}>
                  {user?.email?.charAt(0).toUpperCase()}
                </Avatar>
                {screens.lg && <span style={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis' }}>{user?.email}</span>}
              </div>
            </Dropdown>
          )}
        </div>
      </Header>
      <Content style={{ padding: screens.md ? '24px' : '16px', minHeight: 'calc(100vh - 64px)', background: '#f5f5f5' }}>
        {children}
      </Content>

      <Modal
        title="Settings"
        open={settingsOpen}
        onCancel={() => setSettingsOpen(false)}
        footer={null}
        width={550}
      >
        <Settings />
      </Modal>
    </Layout>
  );
}
