import React, { useEffect, useState } from 'react';
import { Pill, Plus, Search, Trash2 } from 'lucide-react';
import { getStoredMedicines, deleteMedicine } from '../../features/medications/medicationService';
import { getActiveProfile } from '../../features/profile/familyProfileService';
import { useNavigate } from 'react-router-dom';

export default function MyMedicinesPage() {
  const [searchTerm,setSearchTerm]=useState(''); const [medicines,setMedicines]=useState([]); const [error,setError]=useState(''); const navigate=useNavigate();
  const load=async()=>{try{const profile=await getActiveProfile();setMedicines(profile?await getStoredMedicines(profile.id):[]);}catch(e){setError(e.message);}};
  useEffect(()=>{load();},[]);
  const remove=async(id)=>{if(!window.confirm('Delete this medicine and its schedules?'))return;try{await deleteMedicine(id);await load();}catch(e){setError(e.message);}};
  const filtered=medicines.filter(m=>m.name.toLowerCase().includes(searchTerm.toLowerCase()));
  return <div style={{display:'flex',flexDirection:'column',gap:20}}><div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}><div><h2 style={{margin:0}}>💊 My Medicines</h2><span style={{fontSize:13,color:'#64748b'}}>Data is loaded from the authenticated backend.</span></div><button onClick={()=>navigate('/patient/add-medicine')} className="btn-primary"><Plus size={16}/> Add Medicine</button></div>
  {error&&<div style={{color:'#dc2626'}}>{error}</div>}<div className="glass-card" style={{padding:20}}><div style={{position:'relative',marginBottom:16}}><Search size={18} color="#94a3b8" style={{position:'absolute',left:12,top:'50%',transform:'translateY(-50%)'}}/><input value={searchTerm} onChange={e=>setSearchTerm(e.target.value)} placeholder="Search medicine" style={{width:'100%',padding:'10px 10px 10px 38px',boxSizing:'border-box'}}/></div>
  {!filtered.length?<div style={{padding:36,textAlign:'center',background:'#fff0f3',borderRadius:12}}><Pill size={40} color="#DC143C"/><h3>No medicines yet</h3><button onClick={()=>navigate('/patient/add-medicine')} className="btn-primary">Add Medicine</button></div>:<div style={{overflowX:'auto'}}><table style={{width:'100%',borderCollapse:'collapse'}}><thead><tr><th>Medicine</th><th>Dosage</th><th>Category</th><th>Stock</th><th>Status</th><th/></tr></thead><tbody>{filtered.map(m=><tr key={m.id}><td style={{padding:12,fontWeight:700}}>💊 {m.name}</td><td>{m.dosage}</td><td>{m.category}</td><td style={{fontWeight:700,color:m.stock_quantity<=10?'#dc2626':'#16a34a'}}>{m.stock_quantity} {m.unit}</td><td>{m.is_active?'Active':'Inactive'}</td><td><button onClick={()=>remove(m.id)} style={{border:0,background:'#fef2f2',padding:7,color:'#dc2626',cursor:'pointer'}}><Trash2 size={14}/></button></td></tr>)}</tbody></table></div>}</div></div>;
}
