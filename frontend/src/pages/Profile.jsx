import { useState } from 'react'
import { api } from '../api/client'

const initialForm = {
  customer_category: 'civil_servant',
  residency_status: 'resident_nigeria',
  first_name: '',
  last_name: '',
  date_of_birth: '',
  bvn: '',
  state_of_residence: '',
  country_of_residence: 'Nigeria',
  employer_name: '',
  monthly_income: '',
  business_name: '',
  average_monthly_turnover: '',
}

export default function Profile() {
  const [form, setForm] = useState(initialForm)
  const [response, setResponse] = useState(null)
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const res = await api.post('/profile/', form)
      setResponse(res.data)
    } catch (err) {
      try {
        const res = await api.patch('/profile/', form)
        setResponse(res.data)
      } catch (patchErr) {
        setError(patchErr?.response?.data ? JSON.stringify(patchErr.response.data) : 'Profile save failed')
      }
    }
  }

  return (
    <div>
      <h1>Profile</h1>
      <form onSubmit={submit} className="card form-grid two-col">
        <select value={form.customer_category} onChange={e => setForm({ ...form, customer_category: e.target.value })}>
          <option value="military">Military</option>
          <option value="paramilitary">Paramilitary</option>
          <option value="civil_servant">Civil Servant</option>
          <option value="businessman">Businessman</option>
        </select>
        <select value={form.residency_status} onChange={e => setForm({ ...form, residency_status: e.target.value })}>
          <option value="resident_nigeria">Resident Nigeria</option>
          <option value="diaspora">Diaspora</option>
        </select>
        <input placeholder="First Name" value={form.first_name} onChange={e => setForm({ ...form, first_name: e.target.value })} />
        <input placeholder="Last Name" value={form.last_name} onChange={e => setForm({ ...form, last_name: e.target.value })} />
        <input type="date" value={form.date_of_birth} onChange={e => setForm({ ...form, date_of_birth: e.target.value })} />
        <input placeholder="BVN" value={form.bvn} onChange={e => setForm({ ...form, bvn: e.target.value })} />
        <input placeholder="State of Residence" value={form.state_of_residence} onChange={e => setForm({ ...form, state_of_residence: e.target.value })} />
        <input placeholder="Country of Residence" value={form.country_of_residence} onChange={e => setForm({ ...form, country_of_residence: e.target.value })} />
        <input placeholder="Employer Name" value={form.employer_name} onChange={e => setForm({ ...form, employer_name: e.target.value })} />
        <input placeholder="Monthly Income" value={form.monthly_income} onChange={e => setForm({ ...form, monthly_income: e.target.value })} />
        <input placeholder="Business Name" value={form.business_name} onChange={e => setForm({ ...form, business_name: e.target.value })} />
        <input placeholder="Average Monthly Turnover" value={form.average_monthly_turnover} onChange={e => setForm({ ...form, average_monthly_turnover: e.target.value })} />
        <button type="submit">Save Profile</button>
      </form>
      {response && <pre>{JSON.stringify(response, null, 2)}</pre>}
      {error && <p className="error">{error}</p>}
    </div>
  )
}
