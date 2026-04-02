import { useState } from 'react'
import { api } from '../api/client'

export default function Credit() {
  const [response, setResponse] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const evaluate = async () => {
    setError('')
    setResponse(null)
    setLoading(true)
    try {
      const res = await api.post('/credit/evaluate/')
      setResponse(res.data)
    } catch (err) {
      setError(err?.response?.data ? JSON.stringify(err.response.data) : 'Credit evaluation failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1>Credit Evaluation</h1>
      <p>Check your creditworthiness for loan eligibility.</p>
      <div className="card">
        <button onClick={evaluate} disabled={loading}>
          {loading ? <span className="loading"></span> : 'Run Credit Check'}
        </button>
        {response && (
          <div className="success" style={{ marginTop: '16px' }}>
            <h3>Credit Assessment Results</h3>
            <div className="form-grid">
              <div><strong>Score:</strong> {response.score}/100</div>
              <div><strong>Decision:</strong> {response.decision}</div>
              <div><strong>Max Loan Amount:</strong> ₦{response.max_loan}</div>
              <div><strong>Reason:</strong> {response.reason}</div>
            </div>
          </div>
        )}
        {error && <p className="error">{error}</p>}
      </div>
    </div>
  )
}
