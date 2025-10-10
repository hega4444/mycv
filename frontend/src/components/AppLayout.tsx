import type { ReactNode } from 'react';
import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Avatar, Dropdown, Typography, Modal } from 'antd';
import {
  HomeOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';
import { Settings } from '../pages/Settings';

const { Header, Content } = Layout;
const { Title } = Typography;

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [settingsOpen, setSettingsOpen] = useState(false);

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

  return (
    <Layout className="min-h-screen">
      <Header style={{ background: '#fff', padding: '0 24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <Title level={3} style={{ margin: 0, background: 'linear-gradient(90deg, #1677ff 0%, #69b1ff 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              myCV
            </Title>
            
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
              style={{ marginLeft: 24 }}
            />
          </div>

          <Dropdown
            menu={{ items: userMenuItems }}
            placement="bottomRight"
            arrow
          >
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8 }}>
              <Avatar style={{ backgroundColor: '#1677ff' }}>
                {user?.email?.charAt(0).toUpperCase()}
              </Avatar>
              <span>{user?.email}</span>
            </div>
          </Dropdown>
        </div>
      </Header>
      <Content style={{ padding: '24px' }}>
        {children}
      </Content>

      <Modal
        title="Settings"
        open={settingsOpen}
        onCancel={() => setSettingsOpen(false)}
        footer={null}
        width={700}
      >
        <Settings />
      </Modal>
    </Layout>
  );
}
