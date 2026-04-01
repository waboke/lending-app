import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function Dashboard() {
  const [dashboard, setDashboard] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/branches/staff/dashboard/')
      .then(res => setDashboard(res.data))
      .catch(() => setError('Login as branch staff or head office to view dashboard'))
  }, [])

  return (
    <div>
      <h1>Branch Lending Dashboard</h1>
      <p>This frontend works with the DRF backend, customer flows, and branch-office administration model.</p>
      {dashboard && <pre>{JSON.stringify(dashboard, null, 2)}</pre>}
      {error && <p className="error">{error}</p>}
    </div>
  )
}
