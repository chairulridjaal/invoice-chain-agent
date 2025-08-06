// Core types for Invoice Chain Agent
export interface InvoiceData {
  invoice_id: string;
  vendor_name: string;
  tax_id: string;
  amount: number;
  date: string;
  status?: string;
  explanation?: string;
  blockchain_hash?: string | null;
}

export interface ValidationResult {
  score: number;
  riskScore: number;
  fraudRisk: 'LOW' | 'MEDIUM' | 'HIGH';
  status: 'valid' | 'suspicious' | 'fraud' | 'approved' | 'rejected' | 'approved_with_conditions';
  explanation: string;
  timestamp: number;
  processedAt?: number;
}

export interface ProcessingResult {
  success: boolean;
  message: string;
  invoice_data: InvoiceData;
  validation_result: ValidationResult;
  blockchain_result?: {
    success: boolean;
    canister_id: string;
    network: string;
    transaction_hash: string;
  };
  error?: string;
}

export interface BlockchainInvoice {
  id: string;
  status: string;
  validationScore: number;
  riskScore: number;
  fraudRisk: string;
  timestamp: number;
  processedAt?: number;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
}

export interface SystemStats {
  total_invoices: number;
  processed_today: number;
  success_rate: number;
  avg_processing_time: number;
  canister_status: string;
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  canister_health: boolean;
  api_health: boolean;
  last_check: string;
}

export interface ValidationStage {
  name: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  duration?: number;
  description: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface UploadResponse {
  success: boolean;
  message: string;
  invoice_data?: InvoiceData;
  validation_result?: ValidationResult;
  processing_stages: ValidationStage[];
  blockchain_result?: any;
}

// Custom validation rules
export interface ValidationRule {
  id: string;
  name: string;
  type: 'vendor_whitelist' | 'amount_limit' | 'date_range' | 'tax_id_format';
  enabled: boolean;
  parameters: Record<string, any>;
  description: string;
}

export interface CustomValidationConfig {
  rules: ValidationRule[];
  strictMode: boolean;
  autoApproveThreshold: number;
  autoRejectThreshold: number;
}
