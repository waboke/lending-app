import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Register from './pages/Register'
import Login from './pages/Login'
import Profile from './pages/Profile'
import Kyc from './pages/Kyc'
import Credit from './pages/Credit'
import Loans from './pages/Loans'
import Payments from './pages/Payments'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/kyc" element={<Kyc />} />
        <Route path="/credit" element={<Credit />} />
        <Route path="/loans" element={<Loans />} />
        <Route path="/payments" element={<Payments />} />
      </Routes>
    </Layout>
  )
}
