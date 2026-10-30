import axios from 'axios';
import { 
  CaseRecord, 
  ComplaintCreate, 
  CaseDecisionRequest, 
  EvaluationMetrics, 
  DashboardStats,
  LoginResponse,
  AuthStatusResponse,
  NotionStatusResponse,
  NotionSyncResult
} from '../types';

const getApiBaseUrl = (): string => {
  const envUrl = (import.meta.env.VITE_API_BASE_URL || '').trim();
  // Default to live Render deployment if not explicitly configured locally
  const rawUrl = envUrl || 'https://resolveai-trr9.onrender.com/api/v1';
  let cleanUrl = rawUrl.replace(/\/+$/, '');
  if (!cleanUrl.endsWith('/api/v1')) {
    cleanUrl = `${cleanUrl}/api/v1`;
  }
  return cleanUrl;
};

const API_BASE = getApiBaseUrl();

const client = axios.create({
  baseURL: API_BASE,
  withCredentials: true, // Send HTTP-only session cookies with every request
  headers: {
    'Content-Type': 'application/json'
  }
});

// Attach bearer token for cross-origin deployments (e.g. Vercel frontend -> Render backend)
client.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('resolveai_token') : null;
  if (token) {
    config.headers = config.headers || {};
    config.headers['Authorization'] = `Bearer ${token}`;
    config.headers['X-Session-Token'] = token;
  }
  return config;
});

export const apiService = {
  // Authentication & Session
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await client.post<LoginResponse>('/auth/login', { username, password });
    if (response.data?.token) {
      localStorage.setItem('resolveai_token', response.data.token);
    }
    return response.data;
  },

  async logout(): Promise<{ message: string }> {
    try {
      const response = await client.post<{ message: string }>('/auth/logout');
      return response.data;
    } finally {
      localStorage.removeItem('resolveai_token');
    }
  },

  async getAuthStatus(): Promise<AuthStatusResponse> {
    const response = await client.get<AuthStatusResponse>('/auth/me');
    return response.data;
  },

  // Submit a complaint (Public)
  async submitComplaint(
    data: ComplaintCreate,
    images: File[] = [],
    onUploadProgress?: (percent: number) => void,
  ): Promise<CaseRecord> {
    if (!images.length) {
      const response = await client.post<CaseRecord>('/complaints', data);
      return response.data;
    }
    const form = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined && value !== null) form.append(key, String(value));
    });
    images.forEach((image) => form.append('images', image));
    const response = await client.post<CaseRecord>('/complaints', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (event) => {
        if (event.total && onUploadProgress) onUploadProgress(Math.round((event.loaded / event.total) * 100));
      },
    });
    return response.data;
  },

  // Track complaint publicly by Ticket Number (RES-2026-xxx) or Case ID
  async trackComplaint(identifier: string): Promise<CaseRecord> {
    const response = await client.get<CaseRecord>(`/cases/track/${encodeURIComponent(identifier.trim())}`);
    return response.data;
  },

  // Get cases with optional filters (Admin Triage - Protected)
  async getCases(params?: { status?: string; category?: string; priority?: string; location?: string; search?: string; sort?: string }): Promise<CaseRecord[]> {
    const response = await client.get<CaseRecord[]>('/cases', { params });
    return response.data;
  },

  // Get cases for testing portal (Testing - Protected)
  async getTestingCases(): Promise<CaseRecord[]> {
    const response = await client.get<CaseRecord[]>('/testing/cases');
    return response.data;
  },

  // Get single case by ID (Public)
  async getCaseById(caseId: string): Promise<CaseRecord> {
    const response = await client.get<CaseRecord>(`/cases/${caseId}`);
    return response.data;
  },

  // Admin decision (Admin - Protected)
  async makeCaseDecision(caseId: string, decision: CaseDecisionRequest): Promise<CaseRecord> {
    const response = await client.post<CaseRecord>(`/cases/${caseId}/decision`, decision);
    return response.data;
  },

  // Update Case Status (Admin - Protected)
  async updateCaseStatus(caseId: string, status: string, note?: string): Promise<CaseRecord> {
    const response = await client.patch<CaseRecord>(`/cases/${caseId}/status`, { status, note });
    return response.data;
  },

  // Get Dashboard Stats (Public)
  async getStats(): Promise<DashboardStats> {
    const response = await client.get<DashboardStats>('/stats');
    return response.data;
  },

  // Get Benchmark & Ablation Metrics (Testing - Protected)
  async getBenchmarkMetrics(): Promise<EvaluationMetrics> {
    const response = await client.get<EvaluationMetrics>('/metrics/benchmark');
    return response.data;
  },

  // Notion Documentation & Test Results Sync (Testing - Protected)
  async syncNotion(): Promise<NotionSyncResult> {
    const response = await client.post<NotionSyncResult>('/integrations/notion/sync');
    return response.data;
  },

  async getNotionStatus(): Promise<NotionStatusResponse> {
    const response = await client.get<NotionStatusResponse>('/integrations/notion/status');
    return response.data;
  },

  // Reset Demo State (Testing - Protected)
  async resetDemo(): Promise<{ message: string }> {
    const response = await client.post<{ message: string }>('/reset-demo');
    return response.data;
  }
};
