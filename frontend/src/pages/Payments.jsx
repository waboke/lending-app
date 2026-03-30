import { useState } from 'react'
import { api } from '../api/client'

export default function Payments() {
  const [form, setForm] = useState({ loan: '', amount: '', payment_method: 'bank_transfer' })
  const [response, setResponse] = useState(null)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await api.post('/payments/initiate/', form)
      setResponse(res.data)
    } catch (err) {
      setError(err?.response?.data ? JSON.stringify(err.response.data) : 'Payment initiation failed')
    }
  }

  return (
    <div>
      <h1>Payments</h1>
      <form onSubmit={submit} className="card form-grid">
        <input placeholder="Loan ID" value={form.loan} onChange={e => setForm({ ...form, loan: e.target.value })} />
        <input placeholder="Amount" value={form.amount} onChange={e => setForm({ ...form, amount: e.target.value })} />
        <input placeholder="Payment Method" value={form.payment_method} onChange={e => setForm({ ...form, payment_method: e.target.value })} />
        <button type="submit">Initiate Payment</button>
      </form>
      {response && <pre>{JSON.stringify(response, null, 2)}</pre>}
      {error && <p className="error">{error}</p>}
    </div>
  )
}
