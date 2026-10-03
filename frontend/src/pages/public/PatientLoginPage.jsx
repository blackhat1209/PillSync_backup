import React, { useState } from 'react';
import { User, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function PatientLoginPage({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('');
    try {
      const user = await login(username, password);
      if (user.role !== 'patient') throw new Error('This account is not a patient account.');
      onLoginSuccess?.(user); navigate('/patient/dashboard');
    } catch (err) { setError(err.message); }
  };

  return <div style={{ maxWidth: '420px', margin: '30px auto 0' }} className="glass-card"><div style={{ padding: '28px' }}>
    <button onClick={() => navigate('/')} style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 4, marginBottom: 12 }}><ArrowLeft size={14}/> Back</button>
    <div style={{ textAlign: 'center' }}><User size={40} color="#DC143C"/><h2 style={{ color:'#DC143C' }}>Patient Portal Login</h2><p style={{ color:'#64748b' }}>Sign in to manage your medication schedule.</p></div>
    <form onSubmit={handleSubmit} style={{ display:'flex', flexDirection:'column', gap:14 }}>
      <input value={username} onChange={e=>setUsername(e.target.value)} placeholder="Username or email" required style={{padding:10,borderRadius:8,border:'1px solid #cbd5e1'}}/>
      <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password" required style={{padding:10,borderRadius:8,border:'1px solid #cbd5e1'}}/>
      {error && <div style={{color:'#dc2626',fontSize:13}}>{error}</div>}
      <button className="btn-primary" type="submit" style={{padding:12}}>Login as Patient</button>
    </form>
    <p style={{textAlign:'center',fontSize:13,color:'#64748b'}}>No account? <button onClick={()=>navigate('/register/patient')} style={{border:0,background:'none',color:'#DC143C',fontWeight:700,cursor:'pointer'}}>Create one</button></p>
  </div></div>;
}
