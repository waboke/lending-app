import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function Branches() {
  const [branches, setBranches] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/branches/')
      .then(res => setBranches(res.data))
      .catch(() => setError('Failed to load branches'))
  }, [])

  return (
    <div>
      <h1>Branches</h1>
      <div className="grid-cards">
        {branches.map(branch => (
          <div className="card" key={branch.id}>
            <h3>{branch.name}</h3>
            <p>{branch.state} {branch.lga ? `- ${branch.lga}` : ''}</p>
            <p>{branch.address}</p>
            <p>{branch.phone_number}</p>
          </div>
        ))}
      </div>
      {error && <p className="error">{error}</p>}
    </div>
  )
}
