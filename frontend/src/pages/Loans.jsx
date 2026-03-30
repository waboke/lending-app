import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function Loans() {
  const [products, setProducts] = useState([])
  const [applications, setApplications] = useState([])
  const [error, setError] = useState('')
  const [form, setForm] = useState({ product: '', requested_amount: '', tenure_months: 1 })

  const load = async () => {
    try {
      const [p, a] = await Promise.all([
        api.get('/loan-products/'),
        api.get('/loan-applications/')
      ])
      setProducts(p.data)
      setApplications(a.data)
    } catch (err) {
      setError(err?.response?.data ? JSON.stringify(err.response.data) : 'Failed to load loans')
    }
  }

  useEffect(() => {
    load()
  }, [])

  const apply = async (e) => {
    e.preventDefault()
    try {
      await api.post('/loan-applications/', form)
      await load()
    } catch (err) {
      setError(err?.response?.data ? JSON.stringify(err.response.data) : 'Loan application failed')
    }
  }

  return (
    <div>
      <h1>Loans</h1>
      <form onSubmit={apply} className="card form-grid">
        <select value={form.product} onChange={e => setForm({ ...form, product: e.target.value })}>
          <option value="">Select Product</option>
          {products.map((item) => (
            <option key={item.id} value={item.id}>{item.name}</option>
          ))}
        </select>
        <input placeholder="Requested Amount" value={form.requested_amount} onChange={e => setForm({ ...form, requested_amount: e.target.value })} />
        <input placeholder="Tenure Months" value={form.tenure_months} onChange={e => setForm({ ...form, tenure_months: e.target.value })} />
        <button type="submit">Create Application</button>
      </form>

      <div className="card">
        <h2>Applications</h2>
        <pre>{JSON.stringify(applications, null, 2)}</pre>
      </div>
      {error && <p className="error">{error}</p>}
    </div>
  )
}
