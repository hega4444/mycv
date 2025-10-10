import axios from 'axios';
import type {
  AuthResponse,
  Profile,
  CV,
  Settings,
  Provider,
  PersonalData,
  CVContent,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth endpoints
export const authApi = {
  signup: async (email: string, password: string): Promise<AuthResponse> => {
    const { data } = await api.post<AuthResponse>('/api/v1/auth/signup', {
      email,
      password,
    });
    return data;
  },

  login: async (email: string, password: string): Promise<AuthResponse> => {
    const { data } = await api.post<AuthResponse>('/api/v1/auth/login', {
      email,
      password,
    });
    return data;
  },

  logout: async (): Promise<void> => {
    await api.post('/api/v1/auth/logout');
  },

  getMe: async () => {
    const { data } = await api.get('/api/v1/auth/me');
    return data;
  },
};

// Profile endpoints
export const profileApi = {
  getProfile: async (): Promise<Profile> => {
    const { data } = await api.get<Profile>('/api/v1/profile');
    return data;
  },

  updatePersonalData: async (personalData: Partial<PersonalData>): Promise<void> => {
    await api.put('/api/v1/profile/personal', personalData);
  },

  updateCVContent: async (cvContent: CVContent): Promise<void> => {
    await api.put('/api/v1/profile/content', { cv_content: cvContent });
  },

  getPreview: async (): Promise<string> => {
    const { data } = await api.get<{ html: string }>('/api/v1/profile/preview');
    return data.html;
  },
};

// CV endpoints
export const cvApi = {
  listCVs: async (): Promise<CV[]> => {
    const { data } = await api.get<{ cvs: CV[] }>('/api/v1/cvs');
    return data.cvs;
  },

  createCV: async (cvData: {
    description: string;
    job_description: string;
    link?: string;
  }): Promise<CV> => {
    const { data } = await api.post<CV>('/api/v1/cvs', cvData);
    return data;
  },

  getCV: async (cvId: string): Promise<CV> => {
    const { data } = await api.get<CV>(`/api/v1/cvs/${cvId}`);
    return data;
  },

  deleteCV: async (cvId: string): Promise<void> => {
    await api.delete(`/api/v1/cvs/${cvId}`);
  },

  getCVStatus: async (cvId: string): Promise<{ status: string; error_message: string | null }> => {
    const { data } = await api.get(`/api/v1/cvs/${cvId}/status`);
    return data;
  },

  downloadPDF: async (cvId: string, filename: string): Promise<void> => {
    const response = await api.get(`/api/v1/cvs/${cvId}/pdf`, {
      responseType: 'blob',
    });

    // Create blob link to download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.parentNode?.removeChild(link);
  },
};

// Settings endpoints
export const settingsApi = {
  getSettings: async (): Promise<Settings> => {
    const { data } = await api.get<Settings>('/api/v1/settings');
    return data;
  },

  updateSettings: async (settings: {
    provider: string;
    model: string;
    api_key?: string;
  }): Promise<void> => {
    await api.put('/api/v1/settings', settings);
  },

  deleteApiKey: async (): Promise<void> => {
    await api.delete('/api/v1/settings/api-key');
  },
};

// Provider endpoints
export const providerApi = {
  listProviders: async (): Promise<Provider[]> => {
    const { data } = await api.get<{ providers: Provider[] }>('/api/v1/providers');
    return data.providers;
  },

  getProviderModels: async (providerId: string) => {
    const { data } = await api.get(`/api/v1/providers/${providerId}/models`);
    return data;
  },
};

export default api;
