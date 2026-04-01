import { Link } from 'react-router-dom'

export default function Layout({ children }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <h2>Nigeria Lending</h2>
        <nav>
          <Link to="/">Dashboard</Link>
          <Link to="/register">Register</Link>
          <Link to="/login">Login</Link>
          <Link to="/branches">Branches</Link>
          <Link to="/profile">Profile</Link>
          <Link to="/kyc">KYC</Link>
          <Link to="/credit">Credit</Link>
          <Link to="/loans">Loans</Link>
          <Link to="/staff">Staff Queue</Link>
          <Link to="/payments">Payments</Link>
        </nav>
      </aside>
      <main className="content">{children}</main>
    </div>
  )
}
