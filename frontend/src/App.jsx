import React, { useState, useEffect } from 'react'
import './App.css'
import DocumentUpload from './DocumentUpload'

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8001'

function App() {
  const [invoiceData, setInvoiceData] = useState({
    invoice_id: '',
    vendor_name: '',
    tax_id: '',
    amount: '',
    date: new Date().toISOString().split('T')[0]
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [systemHealth, setSystemHealth] = useState(null)

  useEffect(() => {
    fetchStats()
    fetchHealth()
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/stats`)
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Failed to fetch stats:', error)
    }
  }

  const fetchHealth = async () => {
    try {
      const response = await fetch(`${API_BASE}/health`)
      const data = await response.json()
      setSystemHealth(data)
    } catch (error) {
      console.error('Failed to fetch health:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)

    try {
      const response = await fetch(`${API_BASE}/submit`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...invoiceData,
          amount: parseFloat(invoiceData.amount)
        })
      })

      const data = await response.json()
      setResult(data)
      fetchStats() // Refresh stats after submission
    } catch (error) {
      setResult({
        status: 'error',
        explanation: `Failed to submit invoice: ${error.message}`
      })
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e) => {
    setInvoiceData({
      ...invoiceData,
      [e.target.name]: e.target.value
    })
  }

  const generateSampleInvoice = () => {
    const samples = [
      {
        invoice_id: `INV-${Date.now()}`,
        vendor_name: 'Acme Corporation',
        tax_id: '123456789',
        amount: '1500.00',
        date: new Date().toISOString().split('T')[0]
      },
      {
        invoice_id: `INV-${Date.now() + 1}`,
        vendor_name: 'Tech Solutions Inc',
        tax_id: '987654321',
        amount: '2750.50',
        date: new Date().toISOString().split('T')[0]
      },
      {
        invoice_id: `INV-${Date.now() + 2}`,
        vendor_name: 'Bad Example Co',
        tax_id: '', // Missing tax ID
        amount: '-100', // Invalid amount
        date: new Date().toISOString().split('T')[0]
      }
    ]
    
    const randomSample = samples[Math.floor(Math.random() * samples.length)]
    setInvoiceData(randomSample)
  }

  const handleOCRExtraction = (extractedData) => {
    setInvoiceData(extractedData)
    // Show a success message
    alert('Invoice data extracted successfully! Please review and submit.')
  }

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🧾 Invoice Chain Agent</h1>
          <p>AI-Powered Invoice Validation & Blockchain Logging</p>
          {systemHealth && (
            <div className={`health-badge ${systemHealth.status}`}>
              {systemHealth.status === 'healthy' ? '🟢' : '🔴'} System {systemHealth.status}
              {systemHealth.mode && ` (${systemHealth.mode})`}
            </div>
          )}
        </header>

        <div className="main-content">
          <div className="form-section">
            <div className="card">
              <h2>Submit Invoice</h2>
              
              <DocumentUpload onInvoiceExtracted={handleOCRExtraction} />
              
              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label htmlFor="invoice_id">Invoice ID</label>
                  <input
                    type="text"
                    id="invoice_id"
                    name="invoice_id"
                    value={invoiceData.invoice_id}
                    onChange={handleInputChange}
                    placeholder="INV-2025-001"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="vendor_name">Vendor Name</label>
                  <input
                    type="text"
                    id="vendor_name"
                    name="vendor_name"
                    value={invoiceData.vendor_name}
                    onChange={handleInputChange}
                    placeholder="Acme Corporation"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="tax_id">Tax ID</label>
                  <input
                    type="text"
                    id="tax_id"
                    name="tax_id"
                    value={invoiceData.tax_id}
                    onChange={handleInputChange}
                    placeholder="123456789"
                    required
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="amount">Amount ($)</label>
                    <input
                      type="number"
                      id="amount"
                      name="amount"
                      value={invoiceData.amount}
                      onChange={handleInputChange}
                      placeholder="1000.00"
                      step="0.01"
                      min="0"
                      required
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="date">Date</label>
                    <input
                      type="date"
                      id="date"
                      name="date"
                      value={invoiceData.date}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>

                <div className="button-group">
                  <button 
                    type="button" 
                    onClick={generateSampleInvoice}
                    className="button secondary"
                  >
                    🎲 Generate Sample
                  </button>
                  <button 
                    type="submit" 
                    disabled={loading}
                    className="button primary"
                  >
                    {loading ? '⏳ Processing...' : '📤 Submit Invoice'}
                  </button>
                </div>
              </form>
            </div>
          </div>

          <div className="results-section">
            {result && (
              <div className="card">
                <h3>Validation Result</h3>
                <div className={`result ${result.status}`}>
                  <div className="status">
                    {result.status === 'approved' ? '✅' : result.status === 'rejected' ? '❌' : '⚠️'} 
                    Status: <strong>{result.status?.toUpperCase()}</strong>
                  </div>
                  <div className="explanation">
                    <strong>AI Explanation:</strong>
                    <p>{result.explanation}</p>
                  </div>
                  {result.blockchain && (
                    <div className="blockchain-info">
                      <strong>Blockchain Status:</strong>
                      <p>
                        {result.blockchain.success ? '🟢' : '🔴'} 
                        {result.blockchain.message}
                      </p>
                      {result.blockchain.canister_id && (
                        <small>Canister: {result.blockchain.canister_id}</small>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {stats && (
              <div className="card">
                <h3>📊 System Statistics</h3>
                <div className="stats-grid">
                  <div className="stat-item approved">
                    <div className="stat-number">{stats.stats?.approved || 0}</div>
                    <div className="stat-label">Approved</div>
                  </div>
                  <div className="stat-item rejected">
                    <div className="stat-number">{stats.stats?.rejected || 0}</div>
                    <div className="stat-label">Rejected</div>
                  </div>
                  <div className="stat-item total">
                    <div className="stat-number">{stats.stats?.total || 0}</div>
                    <div className="stat-label">Total</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <footer className="footer">
          <p>🤖 Powered by Fetch.ai uAgents • ⛓️ ICP Blockchain • 🧠 OpenAI GPT-4</p>
          {systemHealth?.icp_canister && (
            <p>
              <small>
                ICP Network: {systemHealth.icp_canister.status} 
                {systemHealth.icp_canister.message && ` - ${systemHealth.icp_canister.message}`}
              </small>
            </p>
          )}
        </footer>
      </div>
    </div>
  )
}

export default App
