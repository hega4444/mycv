import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Typography,
  Button,
  Card,
  Modal,
  Form,
  Input,
  Space,
  Tag,
  Empty,
  Spin,
  List,
  notification
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  DownloadOutlined,
  EyeOutlined,
  LinkOutlined
} from '@ant-design/icons';
import { cvApi } from '../services/api';
import type { CV } from '../types';

const { Title, Text, Paragraph } = Typography;

interface CreateCVForm {
  description: string;
  job_description: string;
  link?: string;
}

export function Dashboard() {
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [detailsModalOpen, setDetailsModalOpen] = useState(false);
  const [selectedCV, setSelectedCV] = useState<CV | null>(null);
  const queryClient = useQueryClient();
  const [form] = Form.useForm<CreateCVForm>();

  const { data: cvs = [], isLoading } = useQuery({
    queryKey: ['cvs'],
    queryFn: cvApi.listCVs,
    refetchInterval: (query) => {
      const cvs = query.state.data as CV[] | undefined;
      const hasActive = cvs?.some((cv) => ['pending', 'processing'].includes(cv.status));
      return hasActive ? 3000 : false;
    },
  });

  const createMutation = useMutation({
    mutationFn: cvApi.createCV,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cvs'] });
      setCreateModalOpen(false);
      form.resetFields();
      notification.success({
        message: 'Success',
        description: 'CV created successfully',
      });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: cvApi.deleteCV,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cvs'] });
      notification.success({
        message: 'Success',
        description: 'CV deleted successfully',
      });
    },
  });

  const handleDownloadPDF = async (cv: CV) => {
    try {
      await cvApi.downloadPDF(cv.id, `${cv.description}.pdf`);
      notification.success({
        message: 'Success',
        description: 'PDF downloaded successfully',
      });
    } catch (error) {
      notification.error({
        message: 'Error',
        description: 'Failed to download PDF',
      });
    }
  };

  const getStatusTag = (status: CV['status']) => {
    const statusConfig = {
      completed: { color: 'success', text: 'COMPLETED' },
      processing: { color: 'processing', text: 'PROCESSING' },
      pending: { color: 'warning', text: 'PENDING' },
      failed: { color: 'error', text: 'FAILED' },
    };
    const config = statusConfig[status] || { color: 'default', text: status.toUpperCase() };
    return <Tag color={config.color}>{config.text}</Tag>;
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '32px 24px' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <Title level={2} style={{ margin: 0 }}>My CVs</Title>
            <Text type="secondary">Manage and create your professional CVs</Text>
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setCreateModalOpen(true)}
          >
            Create New CV
          </Button>
        </div>

        {/* CV List */}
        {isLoading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '100px 0' }}>
            <Spin size="large" />
          </div>
        ) : cvs.length === 0 ? (
          <Card>
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description={
                <Space direction="vertical" size="small">
                  <Text>No CVs yet</Text>
                  <Text type="secondary">Get started by creating your first CV</Text>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => setCreateModalOpen(true)}
                  >
                    Create New CV
                  </Button>
                </Space>
              }
            />
          </Card>
        ) : (
          <List
            itemLayout="horizontal"
            dataSource={cvs}
            renderItem={(cv) => (
              <List.Item
                key={cv.id}
                actions={[
                  <Button
                    key="view"
                    icon={<EyeOutlined />}
                    onClick={() => {
                      setSelectedCV(cv);
                      setDetailsModalOpen(true);
                    }}
                  >
                    PDF
                  </Button>,
                  <Button
                    key="download"
                    icon={<DownloadOutlined />}
                    onClick={() => handleDownloadPDF(cv)}
                    disabled={cv.status !== 'completed'}
                  >
                  </Button>,
                  <Button
                    key="delete"
                    danger
                    icon={<DeleteOutlined />}
                    onClick={() => deleteMutation.mutate(cv.id)}
                  >
                  </Button>
                ]}
              >
                <List.Item.Meta
                  title={
                    <Space align="center">
                      <Text strong style={{ fontSize: 16 }}>{cv.description}</Text>
                      {cv.status != "completed" && getStatusTag(cv.status)}
                    </Space>
                  }
                  description={
                    <Space direction="horizontal" size="small">
                      <Text type="secondary">
                        Created on {new Date(cv.created_at).toLocaleDateString()}
                      </Text>
                      {cv.error_message && (
                        <Text type="danger" style={{ padding: 8, backgroundColor: '#fff1f0' }}>
                          {cv.error_message}
                        </Text>
                      )}
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Space>

      {/* Create CV Modal */}
      <Modal
        title="Create New CV"
        open={createModalOpen}
        onCancel={() => setCreateModalOpen(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={(values) => createMutation.mutate(values)}
        >
          <Form.Item
            name="description"
            label="Description"
            rules={[{ required: true, message: 'Please input a description' }]}
          >
            <Input placeholder="e.g., Software Engineer CV" />
          </Form.Item>

          <Form.Item
            name="job_description"
            label="Job Description"
            rules={[{ required: true, message: 'Please input the job description' }]}
          >
            <Input.TextArea rows={4} placeholder="Paste the job description here" />
          </Form.Item>

          <Form.Item
            name="link"
            label="Job Posting Link (Optional)"
          >
            <Input placeholder="https://..." />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Space>
              <Button onClick={() => setCreateModalOpen(false)}>Cancel</Button>
              <Button
                type="primary"
                htmlType="submit"
                loading={createMutation.isPending}
              >
                Create
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Details Modal */}
      <Modal
        title="CV Details"
        open={detailsModalOpen && selectedCV !== null}
        onCancel={() => {
          setDetailsModalOpen(false);
          setSelectedCV(null);
        }}
        footer={null}
      >
        {selectedCV && (
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <div>
              <Text strong>Description:</Text>
              <Paragraph>{selectedCV.description}</Paragraph>
            </div>
            <div>
              <Text strong>Job Description:</Text>
              <Paragraph>{selectedCV.job_description}</Paragraph>
            </div>
            {selectedCV.link && (
              <div>
                <Text strong>Job Posting Link:</Text>
                <Paragraph>
                  <a href={selectedCV.link} target="_blank" rel="noopener noreferrer">
                    {selectedCV.link}
                  </a>
                </Paragraph>
              </div>
            )}
            <div>
              <Text strong>Status:</Text>
              <Paragraph>{getStatusTag(selectedCV.status)}</Paragraph>
            </div>
            <div>
              <Text strong>Created At:</Text>
              <Paragraph>
                {new Date(selectedCV.created_at).toLocaleDateString()}
              </Paragraph>
            </div>
          </Space>
        )}
      </Modal>
    </div>
  );
}
