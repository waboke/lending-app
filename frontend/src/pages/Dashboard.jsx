import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function Dashboard() {
  const [dashboard, setDashboard] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/branches/staff/dashboard/')
      .then(res => setDashboard(res.data))
      .catch(() => setError('Login as branch staff or head office to view dashboard'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading" style={{ margin: '50px auto' }}></div>

  return (
    <div>
      <h1>Branch Lending Dashboard</h1>
      <p>Overview of lending activities and key metrics.</p>
      {dashboard ? (
        <div className="grid-cards">
          {Object.entries(dashboard).map(([key, value]) => (
            <div key={key} className="card">
              <h3>{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h3>
              <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>
                {typeof value === 'number' ? value.toLocaleString() : value}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <div className="card">
          <p>{error}</p>
        </div>
      )}
    </div>
  )
}
