import { useState } from 'react'
import { api, setAuthToken } from '../api/client'

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' })
  const [response, setResponse] = useState(null)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await api.post('/auth/login/', form)
      if (res.data.access) setAuthToken(res.data.access)
      setResponse(res.data)
    } catch (err) {
      setError(err?.response?.data ? JSON.stringify(err.response.data) : 'Login failed')
    }
  }

  return (
    <div>
      <h1>Login</h1>
      <form onSubmit={submit} className="card form-grid">
        <input placeholder="Email" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
        <input placeholder="Password" type="password" value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
        <button type="submit">Login</button>
      </form>
      {response && <pre>{JSON.stringify(response, null, 2)}</pre>}
      {error && <p className="error">{error}</p>}
    </div>
  )
}
