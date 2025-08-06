import React, { useState, useEffect } from 'react';
import { 
  Settings, 
  Plus, 
  Edit2, 
  Trash2, 
  Save, 
  X,
  AlertTriangle,
  Info,
  Shield,
  DollarSign,
  Calendar,
  FileText
} from 'lucide-react';

import type { ValidationRule, CustomValidationConfig } from '@/types';
import { storage, generateId } from '@/lib/utils';

const ValidationConfigPage: React.FC = () => {
  const [config, setConfig] = useState<CustomValidationConfig>({
    rules: [],
    strictMode: false,
    autoApproveThreshold: 85,
    autoRejectThreshold: 30
  });
  const [editingRule, setEditingRule] = useState<ValidationRule | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    // Load config from localStorage
    const savedConfig = storage.get<CustomValidationConfig>('validation-config', {
      rules: [
        {
          id: generateId(),
          name: 'Trusted Vendor Whitelist',
          type: 'vendor_whitelist',
          enabled: true,
          parameters: {
            vendors: ['ACME Corp', 'Tech Solutions Inc', 'Global Supplies Ltd']
          },
          description: 'Only allow invoices from pre-approved vendors'
        },
        {
          id: generateId(),
          name: 'Maximum Invoice Amount',
          type: 'amount_limit',
          enabled: true,
          parameters: {
            maxAmount: 10000,
            currency: 'USD'
          },
          description: 'Reject invoices above specified amount'
        }
      ],
      strictMode: false,
      autoApproveThreshold: 85,
      autoRejectThreshold: 30
    });
    setConfig(savedConfig);
  }, []);

  const saveConfig = () => {
    storage.set('validation-config', config);
    setHasChanges(false);
  };

  const updateConfig = (updates: Partial<CustomValidationConfig>) => {
    setConfig(prev => ({ ...prev, ...updates }));
    setHasChanges(true);
  };

  const addRule = (rule: Omit<ValidationRule, 'id'>) => {
    const newRule: ValidationRule = {
      ...rule,
      id: generateId()
    };
    updateConfig({
      rules: [...config.rules, newRule]
    });
    setShowAddForm(false);
  };

  const updateRule = (ruleId: string, updates: Partial<ValidationRule>) => {
    updateConfig({
      rules: config.rules.map(rule => 
        rule.id === ruleId ? { ...rule, ...updates } : rule
      )
    });
    setEditingRule(null);
  };

  const deleteRule = (ruleId: string) => {
    updateConfig({
      rules: config.rules.filter(rule => rule.id !== ruleId)
    });
  };

  const toggleRule = (ruleId: string) => {
    updateRule(ruleId, { 
      enabled: !config.rules.find(r => r.id === ruleId)?.enabled 
    });
  };

  const getRuleIcon = (type: ValidationRule['type']) => {
    switch (type) {
      case 'vendor_whitelist':
        return <Shield className="h-5 w-5 text-blue-500" />;
      case 'amount_limit':
        return <DollarSign className="h-5 w-5 text-green-500" />;
      case 'date_range':
        return <Calendar className="h-5 w-5 text-purple-500" />;
      case 'tax_id_format':
        return <FileText className="h-5 w-5 text-orange-500" />;
      default:
        return <Settings className="h-5 w-5 text-gray-500" />;
    }
  };

  const RuleForm: React.FC<{
    rule?: ValidationRule;
    onSave: (rule: Omit<ValidationRule, 'id'>) => void;
    onCancel: () => void;
  }> = ({ rule, onSave, onCancel }) => {
    const [formData, setFormData] = useState<Omit<ValidationRule, 'id'>>({
      name: rule?.name || '',
      type: rule?.type || 'vendor_whitelist',
      enabled: rule?.enabled ?? true,
      parameters: rule?.parameters || {},
      description: rule?.description || ''
    });

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      onSave(formData);
    };

    return (
      <div className="card">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              {rule ? 'Edit Rule' : 'Add New Rule'}
            </h3>
            <button
              type="button"
              onClick={onCancel}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rule Name
              </label>
              <input
                type="text"
                required
                className="input-field"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Enter rule name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rule Type
              </label>
              <select
                className="input-field"
                value={formData.type}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  type: e.target.value as ValidationRule['type'],
                  parameters: {} // Reset parameters when type changes
                }))}
              >
                <option value="vendor_whitelist">Vendor Whitelist</option>
                <option value="amount_limit">Amount Limit</option>
                <option value="date_range">Date Range</option>
                <option value="tax_id_format">Tax ID Format</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              className="input-field"
              rows={2}
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Describe what this rule does"
            />
          </div>

          {/* Type-specific parameters */}
          {formData.type === 'vendor_whitelist' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Allowed Vendors (comma-separated)
              </label>
              <input
                type="text"
                className="input-field"
                value={(formData.parameters.vendors as string[])?.join(', ') || ''}
                onChange={(e) => setFormData(prev => ({
                  ...prev,
                  parameters: {
                    ...prev.parameters,
                    vendors: e.target.value.split(',').map(v => v.trim()).filter(Boolean)
                  }
                }))}
                placeholder="ACME Corp, Tech Solutions Inc, Global Supplies Ltd"
              />
            </div>
          )}

          {formData.type === 'amount_limit' && (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Maximum Amount
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  className="input-field"
                  value={formData.parameters.maxAmount || ''}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    parameters: {
                      ...prev.parameters,
                      maxAmount: parseFloat(e.target.value) || 0
                    }
                  }))}
                  placeholder="10000"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Currency
                </label>
                <select
                  className="input-field"
                  value={formData.parameters.currency || 'USD'}
                  onChange={(e) => setFormData(prev => ({
                    ...prev,
                    parameters: {
                      ...prev.parameters,
                      currency: e.target.value
                    }
                  }))}
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                </select>
              </div>
            </div>
          )}

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="rule-enabled"
              checked={formData.enabled}
              onChange={(e) => setFormData(prev => ({ ...prev, enabled: e.target.checked }))}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label htmlFor="rule-enabled" className="text-sm text-gray-700">
              Enable this rule
            </label>
          </div>

          <div className="flex justify-end space-x-3">
            <button type="button" onClick={onCancel} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              <Save className="h-4 w-4 mr-2" />
              Save Rule
            </button>
          </div>
        </form>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Validation Rule Configuration
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Configure custom validation rules for your enterprise requirements. 
          Rules are stored locally and applied during invoice validation.
        </p>
      </div>

      {/* Global Settings */}
      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Global Settings
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Auto-Approve Threshold
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="range"
                min="50"
                max="100"
                value={config.autoApproveThreshold}
                onChange={(e) => updateConfig({ autoApproveThreshold: parseInt(e.target.value) })}
                className="flex-1"
              />
              <span className="text-sm font-medium text-gray-900 w-12">
                {config.autoApproveThreshold}%
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Invoices above this score are auto-approved
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Auto-Reject Threshold
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="range"
                min="0"
                max="50"
                value={config.autoRejectThreshold}
                onChange={(e) => updateConfig({ autoRejectThreshold: parseInt(e.target.value) })}
                className="flex-1"
              />
              <span className="text-sm font-medium text-gray-900 w-12">
                {config.autoRejectThreshold}%
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Invoices below this score are auto-rejected
            </p>
          </div>

          <div>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={config.strictMode}
                onChange={(e) => updateConfig({ strictMode: e.target.checked })}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <span className="text-sm font-medium text-gray-700">Strict Mode</span>
            </label>
            <p className="text-xs text-gray-500 mt-1">
              Require all rules to pass for approval
            </p>
          </div>
        </div>

        {hasChanges && (
          <div className="mt-6 flex items-center justify-between p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-yellow-500" />
              <span className="text-sm text-yellow-700">
                You have unsaved changes
              </span>
            </div>
            <button onClick={saveConfig} className="btn-primary">
              <Save className="h-4 w-4 mr-2" />
              Save Changes
            </button>
          </div>
        )}
      </div>

      {/* Rules List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-gray-900">
            Validation Rules ({config.rules.length})
          </h2>
          <button
            onClick={() => setShowAddForm(true)}
            className="btn-primary"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Rule
          </button>
        </div>

        {showAddForm && (
          <RuleForm
            onSave={addRule}
            onCancel={() => setShowAddForm(false)}
          />
        )}

        {editingRule && (
          <RuleForm
            rule={editingRule}
            onSave={(updatedRule) => updateRule(editingRule.id, updatedRule)}
            onCancel={() => setEditingRule(null)}
          />
        )}

        {config.rules.length === 0 ? (
          <div className="card text-center py-12">
            <Settings className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No validation rules configured
            </h3>
            <p className="text-gray-600 mb-4">
              Add custom rules to enforce your business requirements during invoice validation.
            </p>
            <button
              onClick={() => setShowAddForm(true)}
              className="btn-primary"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Your First Rule
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {config.rules.map((rule) => (
              <div key={rule.id} className="card">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      {getRuleIcon(rule.type)}
                      <div>
                        <h3 className="font-medium text-gray-900">{rule.name}</h3>
                        <p className="text-sm text-gray-600">{rule.description}</p>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={rule.enabled}
                        onChange={() => toggleRule(rule.id)}
                        className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                      />
                      <span className="text-sm text-gray-600">
                        {rule.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setEditingRule(rule)}
                        className="p-2 text-gray-400 hover:text-gray-600"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => deleteRule(rule.id)}
                        className="p-2 text-gray-400 hover:text-danger-600"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>

                {/* Rule Details */}
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Type:</span>
                      <span className="ml-1 font-medium capitalize">
                        {rule.type.replace('_', ' ')}
                      </span>
                    </div>
                    {rule.type === 'vendor_whitelist' && rule.parameters.vendors && (
                      <div className="md:col-span-3">
                        <span className="text-gray-600">Vendors:</span>
                        <span className="ml-1 font-medium">
                          {(rule.parameters.vendors as string[]).join(', ')}
                        </span>
                      </div>
                    )}
                    {rule.type === 'amount_limit' && (
                      <>
                        <div>
                          <span className="text-gray-600">Max Amount:</span>
                          <span className="ml-1 font-medium">
                            {rule.parameters.currency} {rule.parameters.maxAmount}
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Info Section */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-start space-x-3">
          <Info className="h-6 w-6 text-blue-500 mt-0.5" />
          <div>
            <h3 className="font-medium text-blue-900 mb-2">
              How Validation Rules Work
            </h3>
            <div className="text-sm text-blue-700 space-y-2">
              <p>
                • **Vendor Whitelist**: Only approve invoices from specified vendors
              </p>
              <p>
                • **Amount Limit**: Reject invoices exceeding the maximum amount
              </p>
              <p>
                • **Date Range**: Validate invoice dates within acceptable ranges
              </p>
              <p>
                • **Tax ID Format**: Ensure tax IDs match expected patterns
              </p>
              <p className="pt-2 border-t border-blue-200">
                Rules are processed in order and combined with AI-based validation. 
                In strict mode, all enabled rules must pass for approval.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ValidationConfigPage;
