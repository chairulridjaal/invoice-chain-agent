import React from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  Upload, 
  Database, 
  MessageCircle, 
  Settings, 
  Shield, 
  Activity,
  BarChart3
} from 'lucide-react';

// Import pages with relative paths
import UploadPage from './pages/UploadPage';
import AuditLogsPage from './pages/AuditLogsPage';
import ChatPage from './pages/ChatPage';
import ValidationConfigPage from './pages/ValidationConfigPage';
import { cn } from './lib/utils';

const App: React.FC = () => {
  const location = useLocation();

  const navigation = [
    { 
      name: 'Upload & Validate', 
      href: '/', 
      icon: Upload,
      description: 'Upload invoices for validation'
    },
    { 
      name: 'Audit Logs', 
      href: '/audit', 
      icon: Database,
      description: 'View blockchain audit trail'
    },
    { 
      name: 'Chat with Agent', 
      href: '/chat', 
      icon: MessageCircle,
      description: 'Natural language queries'
    },
    { 
      name: 'Validation Rules', 
      href: '/config', 
      icon: Settings,
      description: 'Configure custom rules'
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Shield className="h-8 w-8 text-primary-600" />
                <div>
                  <h1 className="text-xl font-bold text-gray-900">
                    Invoice Chain Agent
                  </h1>
                  <p className="text-xs text-gray-500">
                    Fetch.ai × Internet Computer Hackathon 2025
                  </p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1 text-sm text-gray-600">
                <Activity className="h-4 w-4 text-green-500" />
                <span>ICP Canister Connected</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              const Icon = item.icon;
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={cn(
                    'flex items-center space-x-2 py-4 px-1 border-b-2 text-sm font-medium transition-colors',
                    isActive
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/audit" element={<AuditLogsPage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/config" element={<ValidationConfigPage />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <span>© 2025 Invoice Chain Agent</span>
              <span>•</span>
              <span>NextGen Agents Hackathon</span>
            </div>
            <div className="flex items-center space-x-4 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <BarChart3 className="h-4 w-4" />
                <span>Privacy-First AI</span>
              </div>
              <span>•</span>
              <div className="flex items-center space-x-1">
                <Shield className="h-4 w-4" />
                <span>Blockchain Secured</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
