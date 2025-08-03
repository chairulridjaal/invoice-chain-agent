import React, { useState } from 'react'

const API_BASE = import.meta.env.PROD ? '' : 'http://localhost:8001'

const DocumentUpload = ({ onInvoiceExtracted }) => {
  const [file, setFile] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [preview, setPreview] = useState(null)
  const [extractedText, setExtractedText] = useState('')

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      
      // Create preview
      const reader = new FileReader()
      reader.onload = (e) => setPreview(e.target.result)
      reader.readAsDataURL(selectedFile)
    }
  }

  const extractInvoiceData = async () => {
    if (!file) return

    setProcessing(true)

    try {
      const formData = new FormData()
      formData.append('file', file)

      console.log('🚀 Sending OCR request...')

      const response = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData
      })

      console.log('📡 Response status:', response.status)
      console.log('📡 Response headers:', [...response.headers.entries()])

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const result = await response.json()
      console.log('📄 Response data:', result)

      if (result.success && result.invoice_data) {
        setExtractedText(result.extracted_text || '')
        onInvoiceExtracted(result.invoice_data)
      } else {
        console.error('❌ OCR failed:', result)
        alert(`❌ Failed to extract invoice data: ${result.error || 'Unknown error'}`)
      }
      
    } catch (error) {
      console.error('💥 OCR Error:', error)
      alert(`💥 Failed to process document: ${error.message}. Please check the console for details and try again.`)
    } finally {
      setProcessing(false)
    }
  }

  const clearFile = () => {
    setFile(null)
    setPreview(null)
    setExtractedText('')
  }

  return (
    <div className="document-upload">
      <h3>📄 Upload Invoice Document</h3>
      <p className="upload-description">
        Upload an image or PDF of your invoice and we'll extract the data automatically using OCR.
      </p>

      <div className="upload-area">
        {!file ? (
          <label className="upload-label">
            <input
              type="file"
              accept="image/*,.pdf"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
            <div className="upload-zone">
              <div className="upload-icon">📁</div>
              <div className="upload-text">
                <strong>Click to upload</strong> or drag and drop
              </div>
              <div className="upload-formats">
                Supports: JPG, PNG, PDF
              </div>
            </div>
          </label>
        ) : (
          <div className="file-preview">
            {preview && (
              <img 
                src={preview} 
                alt="Document preview" 
                className="preview-image"
              />
            )}
            <div className="file-info">
              <div className="file-name">{file.name}</div>
              <div className="file-size">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </div>
            </div>
            
            {processing && (
              <div className="processing-status">
                <div className="spinner"></div>
                <div className="progress-text">
                  Processing document with OCR...
                </div>
              </div>
            )}
            
            <div className="file-actions">
              <button 
                onClick={extractInvoiceData}
                disabled={processing}
                className="button primary"
              >
                {processing ? '🔄 Processing...' : '🔍 Extract Data'}
              </button>
              <button 
                onClick={clearFile}
                disabled={processing}
                className="button secondary"
              >
                ❌ Remove
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentUpload
