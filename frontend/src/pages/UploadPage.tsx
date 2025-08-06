import React, { useState, useCallback, useRef } from 'react';
import { 
  Upload, 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  XCircle,
  Clock,
  Shield,
  Database,
  X,
  Edit3,
  DollarSign,
  Building,
  Calendar,
  Hash
} from 'lucide-react';

import { InvoiceChainApi, handleApiError, formatCurrency, formatDate } from '@/services/api';
import type { UploadResponse, ValidationStage } from '@/types';
import { cn, validateFile, formatFileSize, getStatusBadgeClass, getRiskBadgeClass } from '@/lib/utils';

const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [stages, setStages] = useState<ValidationStage[]>([]);
  const [activeTab, setActiveTab] = useState<'upload' | 'manual'>('upload');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Manual form state
  const [manualData, setManualData] = useState({
    invoice_id: '',
    vendor_name: '',
    tax_id: '',
    amount: '',
    date: '',
    notes: ''
  });

  // Default validation stages
  const defaultStages: ValidationStage[] = [
    { name: 'OCR Processing', status: 'pending', description: 'Extracting text from document' },
    { name: 'ERP Cross-check', status: 'pending', description: 'Validating against ERP system' },
    { name: 'GPT Analysis', status: 'pending', description: 'AI-powered fraud detection' },
    { name: 'Risk Scoring', status: 'pending', description: 'Calculating risk assessment' },
    { name: 'Blockchain Storage', status: 'pending', description: 'Storing on ICP canister' },
  ];

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    if (droppedFiles.length > 0) {
      handleFileSelect(droppedFiles[0]);
    }
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
  };

  const handleFileSelect = (selectedFile: File) => {
    const validation = validateFile(selectedFile);
    if (!validation.valid) {
      setError(validation.error || 'Invalid file');
      return;
    }
    
    setFile(selectedFile);
    setError(null);
    setResult(null);
    setStages([]);
  };

  const simulateStageProgress = (isManualEntry = false) => {
    let currentStage = 0;
    const newStages = [...defaultStages];
    setStages(newStages);

    // For manual entry, adjust stage names
    if (isManualEntry) {
      newStages[0] = { name: 'Data Validation', status: 'pending', description: 'Validating input data' };
    }

    const progressStage = () => {
      if (currentStage < newStages.length) {
        newStages[currentStage] = {
          ...newStages[currentStage],
          status: 'processing'
        };
        setStages([...newStages]);

        // Only auto-complete the first 3 stages, wait for API response for blockchain stage
        if (currentStage < 3) {
          setTimeout(() => {
            newStages[currentStage] = {
              ...newStages[currentStage],
              status: 'completed',
              duration: Math.random() * 2000 + 500
            };
            setStages([...newStages]);
            currentStage++;
            
            if (currentStage < 3) {
              setTimeout(progressStage, 500); // Slightly faster progression
            } else {
              // Start the blockchain stage but don't complete it automatically
              setTimeout(() => {
                newStages[currentStage] = {
                  ...newStages[currentStage],
                  status: 'processing'
                };
                setStages([...newStages]);
              }, 1000);
            }
          }, Math.random() * 1500 + 1000);
        }
      }
    };

    progressStage();
  };

  const completeBlockchainStage = (success = true) => {
    setStages(prev => prev.map((stage, index) => {
      if (index === 4 && stage.name === 'Blockchain Storage') { // Target the specific blockchain stage
        return {
          ...stage,
          status: success ? 'completed' : 'failed',
          duration: success ? 2500 : undefined
        };
      }
      return stage;
    }));
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setError(null);
    setResult(null);
    
    // Start stage simulation (false for file upload)
    simulateStageProgress(false);

    try {
      const response = await InvoiceChainApi.uploadInvoice(file);
      
      // Complete the blockchain stage when API responds
      completeBlockchainStage(response.success);
      
      // Wait for stage animation to complete before showing results
      setTimeout(() => {
        setResult(response);
      }, 500);
    } catch (err) {
      const errorMessage = handleApiError(err);
      
      // Complete blockchain stage as failed
      completeBlockchainStage(false);
      
      setTimeout(() => {
        setError(errorMessage);
      }, 500);
    } finally {
      setIsUploading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setResult(null);
    setError(null);
    setStages([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const clearManualForm = () => {
    setManualData({
      invoice_id: '',
      vendor_name: '',
      tax_id: '',
      amount: '',
      date: '',
      notes: ''
    });
    setError(null);
    setResult(null);
    setStages([]);
  };

  const handleManualInputChange = (field: string, value: string) => {
    setManualData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleManualSubmit = async () => {
    // Validate required fields
    if (!manualData.invoice_id.trim() || !manualData.vendor_name.trim() || !manualData.amount.trim()) {
      setError('Invoice ID, Vendor Name, and Amount are required fields');
      return;
    }

    const amount = parseFloat(manualData.amount);
    if (isNaN(amount) || amount <= 0) {
      setError('Amount must be a valid positive number');
      return;
    }

    setIsUploading(true);
    setError(null);
    simulateStageProgress(true); // Start stage progression with manual entry flag

    try {
      const invoiceData = {
        invoice_id: manualData.invoice_id.trim(),
        vendor_name: manualData.vendor_name.trim(),
        tax_id: manualData.tax_id.trim(),
        amount: amount,
        date: manualData.date || new Date().toISOString().split('T')[0],
        line_items: [],
        notes: manualData.notes.trim()
      };

      // Use submitInvoice API and transform response to match UploadResponse format
      const processingResult = await InvoiceChainApi.submitInvoice(invoiceData);
      
      // Complete the blockchain stage when API responds
      completeBlockchainStage(processingResult.success);
      
      // Transform ProcessingResult to UploadResponse format
      const uploadResponse: UploadResponse = {
        success: processingResult.success,
        message: processingResult.message,
        invoice_data: processingResult.invoice_data,
        validation_result: processingResult.validation_result,
        processing_stages: stages, // Use the actual stages
        blockchain_result: processingResult.blockchain_result
      };
      
      // Wait for stage animation to complete before showing results
      setTimeout(() => {
        setResult(uploadResponse);
      }, 500);
    } catch (err) {
      completeBlockchainStage(false);
      setTimeout(() => {
        setError(handleApiError(err));
      }, 500);
    } finally {
      setIsUploading(false);
    }
  };

  const getStageIcon = (status: ValidationStage['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-success-500" />;
      case 'processing':
        return <Clock className="h-5 w-5 text-primary-500 animate-spin" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-danger-500" />;
      default:
        return <div className="h-5 w-5 rounded-full border-2 border-gray-300" />;
    }
  };

  const getStageColor = (status: ValidationStage['status']) => {
    switch (status) {
      case 'completed':
        return 'border-success-200 bg-success-50';
      case 'processing':
        return 'border-primary-200 bg-primary-50';
      case 'failed':
        return 'border-danger-200 bg-danger-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Upload & Validate Invoice
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Upload an invoice image or PDF for AI-powered validation and blockchain storage. 
          Our privacy-first approach ensures sensitive data never leaves your control.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Section */}
        <div className="space-y-6">
          <div className="card">
            {/* Tab Navigation */}
            <div className="flex space-x-1 p-1 bg-gray-100 rounded-lg mb-6">
              <button
                onClick={() => setActiveTab('upload')}
                className={cn(
                  'flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  activeTab === 'upload'
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                <Upload className="h-4 w-4 inline mr-2" />
                File Upload
              </button>
              <button
                onClick={() => setActiveTab('manual')}
                className={cn(
                  'flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors',
                  activeTab === 'manual'
                    ? 'bg-white text-primary-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                )}
              >
                <Edit3 className="h-4 w-4 inline mr-2" />
                Manual Entry
              </button>
            </div>

            {activeTab === 'upload' ? (
              <>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Document Upload
                </h2>
                
                {/* File Upload Area */}
                <div
                  className={cn(
                    'border-2 border-dashed rounded-lg p-8 text-center transition-colors',
                    isDragging 
                      ? 'border-primary-400 bg-primary-50' 
                      : 'border-gray-300 hover:border-gray-400',
                    file && 'border-success-300 bg-success-50'
                  )}
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                >
                  {file ? (
                    <div className="space-y-4">
                      <FileText className="h-12 w-12 text-success-500 mx-auto" />
                      <div>
                        <p className="font-medium text-gray-900">{file.name}</p>
                        <p className="text-sm text-gray-600">{formatFileSize(file.size)}</p>
                      </div>
                      <button
                        onClick={clearFile}
                        className="inline-flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-800"
                      >
                        <X className="h-4 w-4" />
                        <span>Remove file</span>
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <Upload className="h-12 w-12 text-gray-400 mx-auto" />
                      <div>
                        <p className="text-lg font-medium text-gray-900">
                          Drop your invoice here
                        </p>
                        <p className="text-gray-600">
                          or{' '}
                          <button
                            onClick={() => fileInputRef.current?.click()}
                            className="text-primary-600 hover:text-primary-700 font-medium"
                          >
                            browse files
                          </button>
                        </p>
                      </div>
                      <p className="text-xs text-gray-500">
                        Supports: JPG, PNG, GIF, WebP, PDF (max 10MB)
                      </p>
                    </div>
                  )}
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  className="hidden"
                  accept="image/*,application/pdf"
                  onChange={handleFileInputChange}
                />

                {error && (
                  <div className="flex items-center space-x-2 p-4 bg-danger-50 border border-danger-200 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-danger-500" />
                    <p className="text-danger-700">{error}</p>
                  </div>
                )}

                {file && !isUploading && (
                  <button
                    onClick={handleUpload}
                    className="w-full btn-primary"
                  >
                    Start Validation Process
                  </button>
                )}
              </>
            ) : (
              <>
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Manual Invoice Entry
                </h2>
                
                {/* Manual Form */}
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        <Hash className="h-4 w-4 inline mr-1" />
                        Invoice ID *
                      </label>
                      <input
                        type="text"
                        value={manualData.invoice_id}
                        onChange={(e) => handleManualInputChange('invoice_id', e.target.value)}
                        placeholder="INV-2025-001"
                        className="input-field"
                        disabled={isUploading}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        <Building className="h-4 w-4 inline mr-1" />
                        Vendor Name *
                      </label>
                      <input
                        type="text"
                        value={manualData.vendor_name}
                        onChange={(e) => handleManualInputChange('vendor_name', e.target.value)}
                        placeholder="Acme Corp"
                        className="input-field"
                        disabled={isUploading}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        <DollarSign className="h-4 w-4 inline mr-1" />
                        Amount *
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        value={manualData.amount}
                        onChange={(e) => handleManualInputChange('amount', e.target.value)}
                        placeholder="1250.00"
                        className="input-field"
                        disabled={isUploading}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        <Calendar className="h-4 w-4 inline mr-1" />
                        Invoice Date
                      </label>
                      <input
                        type="date"
                        value={manualData.date}
                        onChange={(e) => handleManualInputChange('date', e.target.value)}
                        className="input-field"
                        disabled={isUploading}
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tax ID / VAT Number
                    </label>
                    <input
                      type="text"
                      value={manualData.tax_id}
                      onChange={(e) => handleManualInputChange('tax_id', e.target.value)}
                      placeholder="VAT123456789"
                      className="input-field"
                      disabled={isUploading}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Notes (Optional)
                    </label>
                    <textarea
                      value={manualData.notes}
                      onChange={(e) => handleManualInputChange('notes', e.target.value)}
                      placeholder="Additional notes about this invoice..."
                      className="input-field"
                      rows={3}
                      disabled={isUploading}
                    />
                  </div>
                </div>

                {error && (
                  <div className="flex items-center space-x-2 p-4 bg-danger-50 border border-danger-200 rounded-lg">
                    <AlertTriangle className="h-5 w-5 text-danger-500" />
                    <p className="text-danger-700">{error}</p>
                  </div>
                )}

                <div className="flex space-x-3">
                  <button
                    onClick={handleManualSubmit}
                    disabled={isUploading || !manualData.invoice_id.trim() || !manualData.vendor_name.trim() || !manualData.amount.trim()}
                    className="flex-1 btn-primary"
                  >
                    {isUploading ? 'Processing...' : 'Validate Invoice'}
                  </button>
                  <button
                    onClick={clearManualForm}
                    disabled={isUploading}
                    className="btn-secondary"
                  >
                    Clear Form
                  </button>
                </div>
              </>
            )}
          </div>

          {/* Privacy Notice */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <Shield className="h-5 w-5 text-blue-500 mt-0.5" />
              <div>
                <h3 className="font-medium text-blue-900">Privacy Protected</h3>
                <p className="text-sm text-blue-700 mt-1">
                  Sensitive invoice data is redacted before AI analysis. Only metadata 
                  and validation results are stored on the blockchain.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Results Section */}
        <div className="space-y-6">
          {/* Validation Stages */}
          {stages.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Validation Pipeline
              </h3>
              <div className="space-y-3">
                {stages.map((stage) => (
                  <div
                    key={stage.name}
                    className={cn(
                      'flex items-center space-x-3 p-3 rounded-lg border',
                      getStageColor(stage.status)
                    )}
                  >
                    {getStageIcon(stage.status)}
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">{stage.name}</p>
                      <p className="text-sm text-gray-600">{stage.description}</p>
                    </div>
                    {stage.duration && (
                      <span className="text-xs text-gray-500">
                        {Math.round(stage.duration)}ms
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Results */}
          {result && result.validation_result && result.invoice_data && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Validation Results
              </h3>
              
              {/* Status Badge */}
              <div className="flex items-center justify-between mb-6">
                <span className={cn('text-lg font-medium', getStatusBadgeClass(result.validation_result.status || 'unknown'))}>
                  {(result.validation_result.status || 'unknown').replace('_', ' ').toUpperCase()}
                </span>
                <span className={cn('px-3 py-1 rounded-full text-sm font-medium border', getRiskBadgeClass(result.validation_result.fraudRisk || 'unknown'))}>
                  {result.validation_result.fraudRisk || 'unknown'} Risk
                </span>
              </div>

              {/* Invoice Details */}
              <div className="space-y-4">
                {result.invoice_data && (
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-600">Invoice ID</label>
                      <p className="text-gray-900">{result.invoice_data.invoice_id || 'N/A'}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Vendor</label>
                      <p className="text-gray-900">{result.invoice_data.vendor_name || 'N/A'}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Amount</label>
                      <p className="text-gray-900">{result.invoice_data.amount ? formatCurrency(result.invoice_data.amount) : 'N/A'}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-600">Date</label>
                      <p className="text-gray-900">{result.invoice_data.date ? formatDate(result.invoice_data.date) : 'N/A'}</p>
                    </div>
                  </div>
                )}

                {/* Scores */}
                <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Validation Score</label>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-primary-500 h-2 rounded-full"
                          style={{ width: `${result.validation_result.score || 0}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{result.validation_result.score || 0}/100</span>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Risk Score</label>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-danger-500 h-2 rounded-full"
                          style={{ width: `${result.validation_result.riskScore || 0}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium">{result.validation_result.riskScore || 0}/100</span>
                    </div>
                  </div>
                </div>

                {/* Blockchain Info */}
                {result.blockchain_result && (
                  <div className="pt-4 border-t">
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Database className="h-4 w-4" />
                      <span>Stored on ICP Canister: {result.blockchain_result.canister_id}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Show partial results or error */}
          {result && (!result.validation_result || !result.invoice_data) && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Processing Result
              </h3>
              
              <div className="flex items-center space-x-2 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-yellow-500" />
                <div>
                  <p className="font-medium text-yellow-800">
                    {result.success ? 'Partial Success' : 'Processing Failed'}
                  </p>
                  <p className="text-sm text-yellow-700">{result.message}</p>
                </div>
              </div>
            </div>
          )}

          {isUploading && (
            <div className="card">
              <div className="flex items-center justify-center space-x-3 py-8">
                <Clock className="h-8 w-8 text-primary-500 animate-spin" />
                <p className="text-lg text-gray-600">Processing your invoice...</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadPage;
