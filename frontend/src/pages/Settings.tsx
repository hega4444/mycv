import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Typography,
  Form,
  Select,
  Button,
  Space,
  Input,
  Spin,
  notification,
  Tooltip,
} from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import { settingsApi, providerApi } from '../services/api';

const { Title, Text } = Typography;
const { Password } = Input;

interface SettingsFormValues {
  provider: string;
  model: string;
  api_key: string;
}

export function Settings() {
  const queryClient = useQueryClient();
  const [form] = Form.useForm<SettingsFormValues>();

  const { data: settings, isLoading: settingsLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: settingsApi.getSettings,
  });

  const { data: providers = [] } = useQuery({
    queryKey: ['providers'],
    queryFn: providerApi.listProviders,
  });

  // Update form when settings load
  if (settings && !form.getFieldValue('provider')) {
    form.setFieldsValue({
      provider: settings.provider,
      model: settings.model,
      api_key: '',
    });
  }

  const updateMutation = useMutation({
    mutationFn: settingsApi.updateSettings,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      notification.success({
        message: 'Success',
        description: 'Settings updated',
      });
      form.setFieldValue('api_key', '');
    },
    onError: (error: any) => {
      notification.error({
        message: 'Error',
        description: error.response?.data?.detail || 'Failed to update settings',
      });
    },
  });

  const deleteKeyMutation = useMutation({
    mutationFn: settingsApi.deleteApiKey,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      notification.success({
        message: 'Success',
        description: 'API key removed',
      });
    },
    onError: (error: any) => {
      notification.error({
        message: 'Error',
        description: error.response?.data?.detail || 'Failed to remove API key',
      });
    },
  });

  const selectedProvider = providers.find((p) => p.id === form.getFieldValue('provider'));
  const modelOptions = selectedProvider?.models.map((m) => ({ value: m.id, label: m.name })) || [];

  const handleProviderChange = (providerId: string) => {
    form.setFieldValue('provider', providerId);
    const provider = providers.find((p) => p.id === providerId);
    if (provider && provider.models.length > 0) {
      form.setFieldValue('model', provider.models[0].id);
    }
  };

  if (settingsLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '24px 0' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <Form
      form={form}
      layout="vertical"
      onFinish={(values) => updateMutation.mutate(values)}
      initialValues={{
        provider: settings?.provider || '',
        model: settings?.model || '',
        api_key: '',
      }}
    >
      <Form.Item
        label="AI Provider"
        name="provider"
        rules={[{ required: true, message: 'Please select an AI provider' }]}
      >
        <Select
          options={providers.map((p) => ({ value: p.id, label: p.name }))}
          onChange={handleProviderChange}
        />
      </Form.Item>

      <Form.Item
        label="Model"
        name="model"
        rules={[{ required: true, message: 'Please select a model' }]}
      >
        <Select
          options={modelOptions}
          disabled={!form.getFieldValue('provider')}
        />
      </Form.Item>

      <Form.Item
        label={
          <Space>
            <Text>API Key</Text>
            {settings?.has_api_key && (
              <Space size="small">
                <Text type="secondary">{settings.api_key_display}</Text>
                <Tooltip title="Remove API Key">
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => deleteKeyMutation.mutate()}
                    loading={deleteKeyMutation.isPending}
                    size="small"
                  />
                </Tooltip>
              </Space>
            )}
          </Space>
        }
        name="api_key"
        extra="Leave empty to use default limited key if available"
      >
        <Password
          placeholder={
            settings?.has_api_key ? 'Leave empty to keep current key' : 'Enter your API key'
          }
        />
      </Form.Item>

      <Form.Item style={{ marginBottom: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <Button
            type="primary"
            htmlType="submit"
            loading={updateMutation.isPending}
          >
            Save
          </Button>
        </div>
      </Form.Item>
    </Form>
  );
}
