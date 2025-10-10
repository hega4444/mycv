import { Typography, Space } from 'antd';

const { Title, Text } = Typography;

export function Profile() {
  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '32px 24px' }}>
      <Space direction="vertical" size="large">
        <Title level={2}>Profile</Title>
        <Text type="secondary">CV template editor coming soon...</Text>
      </Space>
    </div>
  );
}
