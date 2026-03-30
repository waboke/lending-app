import { useState } from 'react'
import { api } from '../api/client'

export default function Register() {
  const [form, setForm] = useState({ email: '', phone_number: '', password: '' })
  const [response, setResponse] = useState(null)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await api.post('/auth/register/', form)
      setResponse(res.data)
    } catch (err) {
      setError(err?.response?.data ? JSON.stringify(err.response.data) : 'Registration failed')
    }
  }

  return (
    <div>
      <h1>Register</h1>
      <form onSubmit={submit} className="card form-grid">
        <input placeholder="Email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
        <input placeholder="Phone Number" value={form.phone_number} onChange={e => setForm({ ...form, phone_number: e.target.value })} />
        <input placeholder="Password" type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
        <button type="submit">Register</button>
      </form>
      {response && <pre>{JSON.stringify(response, null, 2)}</pre>}
      {error && <p className="error">{error}</p>}
    </div>
  )
}
