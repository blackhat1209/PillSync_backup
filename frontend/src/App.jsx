import React, { useEffect, useState } from 'react';
import { BrowserRouter, useLocation } from 'react-router-dom';
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';
import AppRoutes from './routes/AppRoutes';
import { useAuth } from './context/AuthContext';
import './App.css';

function MainLayout() {
  const location = useLocation();
  const { user: currentUser } = useAuth();
  const [currentRole, setCurrentRole] = useState(currentUser?.role || 'patient');
  useEffect(() => { if (currentUser?.role) setCurrentRole(currentUser.role); }, [currentUser]);

  const isPublicAuthPage = ['/', '/login', '/login/patient', '/login/caregiver', '/login/admin', '/register', '/register/patient', '/register/caregiver', '/forgot-password'].includes(location.pathname);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#fcf8f9', display: 'flex', flexDirection: 'column' }}>
      <Navbar currentUser={currentUser} setRole={setCurrentRole} />
      
      <div style={{ display: 'flex', flex: 1 }}>
        {!isPublicAuthPage && (
          <Sidebar currentRole={currentRole} />
        )}

        <main style={{ flex: 1, padding: '24px', maxWidth: isPublicAuthPage ? '100%' : '1200px', margin: isPublicAuthPage ? '0 auto' : '0', width: '100%' }}>
          <AppRoutes 
            setCurrentUser={() => {}} 
            setCurrentRole={setCurrentRole} 
          />
        </main>
      </div>

    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <MainLayout />
    </BrowserRouter>
  );
}

export default App;
