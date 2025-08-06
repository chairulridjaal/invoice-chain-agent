import axios from 'axios';
import type { 
  InvoiceData, 
  ProcessingResult, 
  SystemStats, 
  SystemHealth, 
  BlockchainInvoice,
  ApiResponse,
  UploadResponse
} from '@/types';

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8001';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Request interceptor for logging
api.interceptors.request.use((config) => {
  console.log(`🔗 API Request: ${config.method?.toUpperCase()} ${config.url}`);
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export class InvoiceChainApi {
  // Upload and process invoice
  static async uploadInvoice(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post<UploadResponse>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for file processing
    });
    
    return response.data;
  }

  // Manual invoice submission
  static async submitInvoice(invoiceData: InvoiceData): Promise<ProcessingResult> {
    const response = await api.post<ProcessingResult>('/submit', invoiceData);
    return response.data;
  }

  // Get system statistics
  static async getStats(): Promise<SystemStats> {
    const response = await api.get<SystemStats>('/stats');
    return response.data;
  }

  // Get system health
  static async getHealth(): Promise<SystemHealth> {
    const response = await api.get<SystemHealth>('/health');
    return response.data;
  }

  // Get all invoices from blockchain
  static async getAllInvoices(): Promise<BlockchainInvoice[]> {
    const response = await api.get<ApiResponse<BlockchainInvoice[]>>('/invoices');
    return response.data.data || [];
  }

  // Get specific invoice by ID
  static async getInvoice(invoiceId: string): Promise<BlockchainInvoice | null> {
    try {
      const response = await api.get<ApiResponse<BlockchainInvoice>>(`/invoices/${invoiceId}`);
      return response.data.data || null;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  // Chat with agent
  static async chatWithAgent(message: string): Promise<string> {
    const response = await api.post<ApiResponse<{ reply: string }>>('/chat', { 
      message,
      timestamp: new Date().toISOString()
    });
    
    return response.data.data?.reply || 'Sorry, I could not process your request.';
  }

  // Get audit logs for an invoice
  static async getAuditLogs(invoiceId: string): Promise<any[]> {
    try {
      const response = await api.get<ApiResponse<any[]>>(`/audit/${invoiceId}`);
      return response.data.data || [];
    } catch (error) {
      console.warn(`Audit logs not available for ${invoiceId}`);
      return [];
    }
  }

  // Test canister connectivity
  static async testCanister(): Promise<boolean> {
    try {
      const response = await api.get<ApiResponse<any>>('/canister/health');
      return response.data.success;
    } catch (error) {
      return false;
    }
  }
}

// Utility functions for error handling
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const message = error.response?.data?.error || error.response?.data?.message || error.message;
    return message || 'An unexpected error occurred';
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unknown error occurred';
};

// Utility for formatting currency
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

// Utility for formatting dates
export const formatDate = (date: string | number): string => {
  const dateObj = typeof date === 'number' ? new Date(date / 1000000) : new Date(date);
  return dateObj.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

// Utility for formatting timestamps
export const formatTimestamp = (timestamp: number): string => {
  // Convert nanoseconds to milliseconds
  const date = new Date(timestamp / 1000000);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export default api;
