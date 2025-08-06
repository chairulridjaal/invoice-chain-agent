import React, { useState, useEffect } from 'react';
import { 
  Database, 
  Search, 
  Filter, 
  RefreshCw,
  Calendar,
  TrendingUp,
  TrendingDown,
  Minus,
  ExternalLink,
  Eye
} from 'lucide-react';

import { InvoiceChainApi, handleApiError, formatTimestamp } from '@/services/api';
import type { BlockchainInvoice } from '@/types';
import { cn, getStatusBadgeClass, getRiskBadgeClass } from '@/lib/utils';

const AuditLogsPage: React.FC = () => {
  const [invoices, setInvoices] = useState<BlockchainInvoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'date' | 'amount' | 'score'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    loadInvoices();
  }, []);

  const loadInvoices = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await InvoiceChainApi.getAllInvoices();
      console.log('Loaded invoices:', data);
      setInvoices(data);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const filteredAndSortedInvoices = React.useMemo(() => {
    let filtered = invoices;

    // Apply search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(invoice => 
        invoice.id.toLowerCase().includes(query) ||
        invoice.status.toLowerCase().includes(query)
      );
    }

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(invoice => 
        invoice.status.toLowerCase() === statusFilter.toLowerCase()
      );
    }

    // Apply risk filter
    if (riskFilter !== 'all') {
      filtered = filtered.filter(invoice => 
        invoice.fraudRisk.toLowerCase() === riskFilter.toLowerCase()
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'date':
          comparison = a.timestamp - b.timestamp;
          break;
        case 'score':
          comparison = a.validationScore - b.validationScore;
          break;
        default:
          comparison = a.timestamp - b.timestamp;
      }
      
      return sortOrder === 'desc' ? -comparison : comparison;
    });

    return filtered;
  }, [invoices, searchQuery, statusFilter, riskFilter, sortBy, sortOrder]);

  const stats = React.useMemo(() => {
    const total = invoices.length;
    const approved = invoices.filter(inv => inv.status === 'approved').length;
    const rejected = invoices.filter(inv => inv.status === 'rejected').length;
    const avgScore = total > 0 
      ? Math.round(invoices.reduce((sum, inv) => sum + inv.validationScore, 0) / total)
      : 0;
    
    return { total, approved, rejected, avgScore };
  }, [invoices]);

  const getRiskIcon = (risk: string) => {
    switch (risk.toLowerCase()) {
      case 'high':
        return <TrendingUp className="h-4 w-4 text-danger-500" />;
      case 'low':
        return <TrendingDown className="h-4 w-4 text-success-500" />;
      default:
        return <Minus className="h-4 w-4 text-warning-500" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <RefreshCw className="h-12 w-12 text-primary-500 animate-spin mx-auto mb-4" />
          <p className="text-lg text-gray-600">Loading audit logs from ICP blockchain...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center">
        <div className="card max-w-md mx-auto">
          <Database className="h-12 w-12 text-danger-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Failed to Load Audit Logs
          </h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={loadInvoices}
            className="btn-primary"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Blockchain Audit Logs
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Immutable audit trail of all invoice validations stored on the Internet Computer Protocol blockchain.
        </p>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Invoices</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
            <Database className="h-8 w-8 text-primary-500" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Approved</p>
              <p className="text-2xl font-bold text-success-600">{stats.approved}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-success-500" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Rejected</p>
              <p className="text-2xl font-bold text-danger-600">{stats.rejected}</p>
            </div>
            <TrendingDown className="h-8 w-8 text-danger-500" />
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Score</p>
              <p className="text-2xl font-bold text-primary-600">{stats.avgScore}/100</p>
            </div>
            <Calendar className="h-8 w-8 text-primary-500" />
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="card">
        <div className="flex flex-col lg:flex-row lg:items-center space-y-4 lg:space-y-0 lg:space-x-4">
          {/* Search */}
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search by invoice ID or status..."
                className="input-field pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-500" />
            <select
              className="input-field"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Status</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="approved_with_conditions">Approved with Conditions</option>
            </select>
          </div>

          {/* Risk Filter */}
          <select
            className="input-field"
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
          >
            <option value="all">All Risk Levels</option>
            <option value="low">Low Risk</option>
            <option value="medium">Medium Risk</option>
            <option value="high">High Risk</option>
          </select>

          {/* Sort */}
          <select
            className="input-field"
            value={`${sortBy}-${sortOrder}`}
            onChange={(e) => {
              const [field, order] = e.target.value.split('-');
              setSortBy(field as any);
              setSortOrder(order as any);
            }}
          >
            <option value="date-desc">Newest First</option>
            <option value="date-asc">Oldest First</option>
            <option value="score-desc">Highest Score</option>
            <option value="score-asc">Lowest Score</option>
          </select>

          {/* Refresh */}
          <button
            onClick={loadInvoices}
            className="btn-secondary"
            disabled={loading}
          >
            <RefreshCw className={cn('h-4 w-4', loading && 'animate-spin')} />
          </button>
        </div>
      </div>

      {/* Results */}
      {filteredAndSortedInvoices.length === 0 ? (
        <div className="text-center py-12">
          <Database className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No invoices found</h3>
          <p className="text-gray-600">
            {searchQuery || statusFilter !== 'all' || riskFilter !== 'all'
              ? 'Try adjusting your filters'
              : 'Upload your first invoice to see audit logs here'
            }
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredAndSortedInvoices.map((invoice) => (
            <div key={invoice.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {invoice.id}
                        </h3>
                        <span className={cn('text-sm', getStatusBadgeClass(invoice.status))}>
                          {invoice.status.replace('_', ' ').toUpperCase()}
                        </span>
                        <span className={cn('inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium border', getRiskBadgeClass(invoice.fraudRisk))}>
                          {getRiskIcon(invoice.fraudRisk)}
                          <span>{invoice.fraudRisk} Risk</span>
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-600">Validation Score:</span>
                          <span className="ml-1 font-medium">{invoice.validationScore}/100</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Risk Score:</span>
                          <span className="ml-1 font-medium">{invoice.riskScore}/100</span>
                        </div>
                        <div>
                          <span className="text-gray-600">Processed:</span>
                          <span className="ml-1 font-medium">{formatTimestamp(invoice.timestamp)}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <button className="inline-flex items-center space-x-1 text-primary-600 hover:text-primary-700">
                            <Eye className="h-4 w-4" />
                            <span>View Details</span>
                          </button>
                          <button className="inline-flex items-center space-x-1 text-gray-600 hover:text-gray-700">
                            <ExternalLink className="h-4 w-4" />
                            <span>ICP Explorer</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AuditLogsPage;
