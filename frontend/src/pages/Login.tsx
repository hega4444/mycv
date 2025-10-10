import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Form, Input, Button, Typography, Card, Space, notification } from 'antd';
import { MailOutlined, LockOutlined } from '@ant-design/icons';
import { useAuth } from '../contexts/AuthContext';

const { Title, Text } = Typography;

interface LoginFormValues {
  email: string;
  password: string;
}

export function Login() {
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const handleSubmit = async (values: LoginFormValues) => {
    setIsLoading(true);
    try {
      await login(values.email, values.password);
      notification.success({
        message: 'Success',
        description: 'Logged in successfully',
      });
      navigate('/dashboard');
    } catch (error: any) {
      notification.error({
        message: 'Error',
        description: error.response?.data?.detail || 'Login failed',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 420, margin: '40px auto', padding: '0 16px' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ textAlign: 'center' }}>
          <Title level={2} style={{ marginBottom: 8 }}>
            Welcome Back
          </Title>
          <Text type="secondary">
            Sign in to your account
          </Text>
        </div>

        <Card>
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSubmit}
            autoComplete="off"
            requiredMark={false}
          >
            <Form.Item
              name="email"
              label="Email"
              rules={[
                { required: true, message: 'Please input your email!' },
                { type: 'email', message: 'Please enter a valid email!' }
              ]}
            >
              <Input prefix={<MailOutlined />} placeholder="your@email.com" />
            </Form.Item>

            <Form.Item
              name="password"
              label="Password"
              rules={[
                { required: true, message: 'Please input your password!' }
              ]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="Your password" />
            </Form.Item>

            <Form.Item>
              <Button type="primary" htmlType="submit" loading={isLoading} block>
                Sign in
              </Button>
            </Form.Item>

            <div style={{ textAlign: 'center' }}>
              <Text type="secondary">
                Don't have an account?{' '}
                <Link to="/signup">Sign up</Link>
              </Text>
            </div>
          </Form>
        </Card>
      </Space>
    </div>
  );
}
