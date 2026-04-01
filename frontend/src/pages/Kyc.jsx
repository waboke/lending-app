import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function Kyc() {
  const [form, setForm] = useState({ id_type: 'nin', id_number: '' })
  const [response, setResponse] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/kyc/status/').then(res => setForm({ id_type: res.data.id_type || 'nin', id_number: res.data.id_number || '' })).catch(() => {})
  }, [])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await api.patch('/kyc/submit/', form)
      setResponse(res.data)
    } catch (err) {
      setError(err?.response?.data ? JSON.stringify(err.response.data) : 'KYC submit failed')
    }
  }

  return (
    <div>
      <h1>KYC</h1>
      <form onSubmit={submit} className="card form-grid">
        <select value={form.id_type} onChange={e => setForm({ ...form, id_type: e.target.value })}>
          <option value="nin">NIN</option>
          <option value="bvn">BVN</option>
          <option value="passport">Passport</option>
        </select>
        <input placeholder="ID Number" value={form.id_number} onChange={e => setForm({ ...form, id_number: e.target.value })} />
        <button type="submit">Submit KYC</button>
      </form>
      {response && <pre>{JSON.stringify(response, null, 2)}</pre>}
      {error && <p className="error">{error}</p>}
    </div>
  )
}
