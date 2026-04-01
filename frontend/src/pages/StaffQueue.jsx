import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function StaffQueue() {
  const [applications, setApplications] = useState([])
  const [dashboard, setDashboard] = useState(null)
  const [error, setError] = useState('')

  const load = async () => {
    try {
      const [appsRes, dashRes] = await Promise.all([
        api.get('/loan-applications/'),
        api.get('/branches/staff/dashboard/'),
      ])
      setApplications(appsRes.data)
      setDashboard(dashRes.data)
    } catch (err) {
      setError(err?.response?.data ? JSON.stringify(err.response.data) : 'Branch staff access required')
    }
  }

  useEffect(() => { load() }, [])

  const recommend = async (id, recommended) => {
    await api.post(`/loan-applications/${id}/recommend/`, { recommended, note: recommended ? 'Recommended by branch office' : 'Not recommended by branch office' })
    await load()
  }

  const approve = async (id) => {
    await api.post(`/loan-applications/${id}/approve/`)
    await load()
  }

  return (
    <div>
      <h1>Staff Queue</h1>
      {dashboard && <pre>{JSON.stringify(dashboard, null, 2)}</pre>}
      <div className="card">
        {applications.map(app => (
          <div className="inline-card" key={app.id}>
            <div>
              <strong>{app.product_name || app.product}</strong>
              <div>Borrower Branch: {app.branch_name}</div>
              <div>Status: {app.status}</div>
              <div>Decision: {app.branch_decision}</div>
            </div>
            <div className="button-row">
              <button onClick={() => recommend(app.id, true)}>Recommend</button>
              <button onClick={() => recommend(app.id, false)}>Reject</button>
              <button onClick={() => approve(app.id)}>Approve</button>
            </div>
          </div>
        ))}
      </div>
      {error && <p className="error">{error}</p>}
    </div>
  )
}
