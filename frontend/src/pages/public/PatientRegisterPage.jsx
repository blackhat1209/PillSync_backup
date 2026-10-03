import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export default function PatientRegisterPage({ onLoginSuccess }) {
  const [form, setForm] = useState({name:'',email:'',password:'',confirm:'',phone:''});
  const [error,setError]=useState(''); const {register}=useAuth(); const navigate=useNavigate();
  const submit=async(e)=>{e.preventDefault();setError(''); if(form.password!==form.confirm){setError('Passwords do not match.');return;} try{const parts=form.name.trim().split(/\s+/);const user=await register({username:form.email.split('@')[0],email:form.email,password:form.password,firstName:parts[0],lastName:parts.slice(1).join(' '),phone:form.phone,role:'patient'});onLoginSuccess?.(user);navigate('/patient/dashboard');}catch(err){setError(err.message);}};
  return <div style={{maxWidth:440,margin:'20px auto'}} className="glass-card"><div style={{padding:28}}><h2 style={{color:'#DC143C',textAlign:'center'}}>Patient Registration</h2><form onSubmit={submit} style={{display:'flex',flexDirection:'column',gap:12}}>
    <input placeholder="Full name" value={form.name} onChange={e=>setForm({...form,name:e.target.value})} required style={{padding:9}}/><input type="email" placeholder="Email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} required style={{padding:9}}/><input placeholder="Phone" value={form.phone} onChange={e=>setForm({...form,phone:e.target.value})} style={{padding:9}}/><input type="password" placeholder="Password (8+ characters)" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} required style={{padding:9}}/><input type="password" placeholder="Confirm password" value={form.confirm} onChange={e=>setForm({...form,confirm:e.target.value})} required style={{padding:9}}/>
    {error&&<div style={{color:'#dc2626',fontSize:13}}>{error}</div>}<button className="btn-primary" type="submit" style={{padding:12}}>Create Patient Account</button></form><p style={{textAlign:'center'}}><button onClick={()=>navigate('/login/patient')} style={{border:0,background:'none',color:'#DC143C',fontWeight:700}}>Already have an account?</button></p></div></div>;
}
