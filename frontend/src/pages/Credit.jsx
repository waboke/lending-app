import { useState } from 'react'
import { api } from '../api/client'

export default function Credit() {
  const [response, setResponse] = useState(null)
  const [error, setError] = useState('')

  const evaluate = async () => {
    setError('')
    try {
      const res = await api.post('/credit/evaluate/')
      setResponse(res.data)
    } catch (err) {
      setError(err?.response?.data ? JSON.stringify(err.response.data) : 'Credit evaluation failed')
    }
  }

  return (
    <div>
      <h1>Credit Evaluation</h1>
      <button onClick={evaluate}>Run Credit Check</button>
      {response && <pre>{JSON.stringify(response, null, 2)}</pre>}
      {error && <p className="error">{error}</p>}
    </div>
  )
}
