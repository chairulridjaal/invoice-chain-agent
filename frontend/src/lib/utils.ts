import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Status badge utilities
export const getStatusBadgeClass = (status: string): string => {
  switch (status.toLowerCase()) {
    case 'approved':
    case 'valid':
      return 'status-valid';
    case 'suspicious':
    case 'approved_with_conditions':
      return 'status-suspicious';
    case 'rejected':
    case 'fraud':
      return 'status-fraud';
    default:
      return 'status-badge bg-gray-100 text-gray-800';
  }
};

// Risk level utilities
export const getRiskBadgeClass = (risk: string): string => {
  switch (risk.toLowerCase()) {
    case 'low':
      return 'risk-low';
    case 'medium':
      return 'risk-medium';
    case 'high':
      return 'risk-high';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

// File validation
export const validateFile = (file: File): { valid: boolean; error?: string } => {
  const maxSize = 10 * 1024 * 1024; // 10MB
  const allowedTypes = [
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'application/pdf'
  ];

  if (file.size > maxSize) {
    return { valid: false, error: 'File size must be less than 10MB' };
  }

  if (!allowedTypes.includes(file.type)) {
    return { valid: false, error: 'File must be an image (JPEG, PNG, GIF, WebP) or PDF' };
  }

  return { valid: true };
};

// Debounce utility
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Local storage utilities
export const storage = {
  get: <T>(key: string, defaultValue: T): T => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch {
      return defaultValue;
    }
  },
  
  set: <T>(key: string, value: T): void => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.warn('Failed to save to localStorage:', error);
    }
  },
  
  remove: (key: string): void => {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.warn('Failed to remove from localStorage:', error);
    }
  }
};

// Generate unique IDs
export const generateId = (): string => {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
};

// Format file size
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Validation score to percentage
export const scoreToPercentage = (score: number): number => {
  return Math.min(100, Math.max(0, score));
};

// Risk score to risk level
export const riskScoreToLevel = (score: number): 'LOW' | 'MEDIUM' | 'HIGH' => {
  if (score <= 25) return 'LOW';
  if (score <= 75) return 'MEDIUM';
  return 'HIGH';
};
