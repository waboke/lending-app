import { Link } from 'react-router-dom'
import { useState } from 'react'

export default function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <h2>Nigeria Lending</h2>
        <nav>
          <Link to="/" onClick={() => setSidebarOpen(false)}>Dashboard</Link>
          <Link to="/register" onClick={() => setSidebarOpen(false)}>Register</Link>
          <Link to="/login" onClick={() => setSidebarOpen(false)}>Login</Link>
          <Link to="/branches" onClick={() => setSidebarOpen(false)}>Branches</Link>
          <Link to="/profile" onClick={() => setSidebarOpen(false)}>Profile</Link>
          <Link to="/kyc" onClick={() => setSidebarOpen(false)}>KYC</Link>
          <Link to="/credit" onClick={() => setSidebarOpen(false)}>Credit</Link>
          <Link to="/loans" onClick={() => setSidebarOpen(false)}>Loans</Link>
          <Link to="/staff" onClick={() => setSidebarOpen(false)}>Staff Queue</Link>
          <Link to="/payments" onClick={() => setSidebarOpen(false)}>Payments</Link>
        </nav>
      </aside>
      <main className="content">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          style={{
            display: 'none',
            position: 'fixed',
            top: '16px',
            left: '16px',
            zIndex: 101,
            background: 'var(--primary)',
            color: 'white',
            border: 'none',
            padding: '8px 12px',
            borderRadius: '8px',
            cursor: 'pointer'
          }}
          className="mobile-menu-toggle"
        >
          ☰ Menu
        </button>
        {children}
      </main>
    </div>
  )
}
