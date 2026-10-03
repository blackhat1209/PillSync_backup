import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function CaregiverLoginPage({ onLoginSuccess }) {
  const [username,setUsername]=useState(''); const [password,setPassword]=useState(''); const [error,setError]=useState(''); const {login}=useAuth(); const navigate=useNavigate();
  const submit=async(e)=>{e.preventDefault();setError('');try{const u=await login(username,password);if(u.role!=='caregiver')throw new Error('This account is not a caregiver account.');onLoginSuccess?.(u);navigate('/caregiver/dashboard');}catch(err){setError(err.message);}};
  return <div style={{maxWidth:420,margin:'30px auto'}} className="glass-card"><div style={{padding:28}}><h2 style={{color:'#d97706',textAlign:'center'}}>Caregiver Login</h2><form onSubmit={submit} style={{display:'flex',flexDirection:'column',gap:14}}><input value={username} onChange={e=>setUsername(e.target.value)} placeholder="Username or email" required style={{padding:10}}/><input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password" required style={{padding:10}}/>{error&&<div style={{color:'#dc2626',fontSize:13}}>{error}</div>}<button type="submit" style={{padding:12,background:'#d97706',color:'#fff',border:0,borderRadius:8,fontWeight:700}}>Login as Caregiver</button></form></div></div>;
}
