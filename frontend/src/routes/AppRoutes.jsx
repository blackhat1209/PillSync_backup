import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LandingPage from '../pages/public/LandingPage';
import PatientLoginPage from '../pages/public/PatientLoginPage';
import CaregiverLoginPage from '../pages/public/CaregiverLoginPage';
import AdminLoginPage from '../pages/public/AdminLoginPage';
import PatientRegisterPage from '../pages/public/PatientRegisterPage';
import CaregiverRegisterPage from '../pages/public/CaregiverRegisterPage';
import ForgotPasswordPage from '../pages/public/ForgotPasswordPage';
import PatientDashboard from '../pages/patient/PatientDashboard';
import PatientProfile from '../pages/patient/PatientProfile';
import MyMedicinesPage from '../pages/patient/MyMedicinesPage';
import AddMedicinePage from '../pages/patient/AddMedicinePage';
import MedicineSchedulePage from '../pages/patient/MedicineSchedulePage';
import AdherencePage from '../pages/patient/AdherencePage';
import RefillPredictionPage from '../pages/patient/RefillPredictionPage';
import DiseaseCategoriesPage from '../pages/patient/DiseaseCategoriesPage';
import NotificationsPage from '../pages/patient/NotificationsPage';
import MedicationHistoryPage from '../pages/patient/MedicationHistoryPage';
import PrescriptionsPage from '../pages/patient/PrescriptionsPage';
import CaregiverDashboard from '../pages/caregiver/CaregiverDashboard';
import CaregiverPatientDetail from '../pages/caregiver/CaregiverPatientDetail';
import AdminDashboard from '../pages/admin/AdminDashboard';
import UserManagementPage from '../pages/admin/UserManagementPage';
import NotificationSettingsPage from '../pages/admin/NotificationSettingsPage';
import { useAuth } from '../context/AuthContext';

function Protected({ roles, children }) {
  const { user, loading } = useAuth();
  if (loading) return <div style={{padding:40,textAlign:'center'}}>Loading secure session…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to={`/${user.role}/dashboard`} replace />;
  return children;
}

export default function AppRoutes({ setCurrentUser, setCurrentRole }) {
  const handleLoginSuccess = (user) => { setCurrentUser(user); setCurrentRole(user.role); };
  return <Routes>
    <Route path="/" element={<LandingPage />} />
    <Route path="/login" element={<PatientLoginPage onLoginSuccess={handleLoginSuccess} />} />
    <Route path="/login/patient" element={<PatientLoginPage onLoginSuccess={handleLoginSuccess} />} />
    <Route path="/login/caregiver" element={<CaregiverLoginPage onLoginSuccess={handleLoginSuccess} />} />
    <Route path="/login/admin" element={<AdminLoginPage onLoginSuccess={handleLoginSuccess} />} />
    <Route path="/register" element={<PatientRegisterPage onLoginSuccess={handleLoginSuccess} />} />
    <Route path="/register/patient" element={<PatientRegisterPage onLoginSuccess={handleLoginSuccess} />} />
    <Route path="/register/caregiver" element={<CaregiverRegisterPage onLoginSuccess={handleLoginSuccess} />} />
    <Route path="/forgot-password" element={<ForgotPasswordPage />} />

    <Route path="/patient" element={<Protected roles={['patient']}><PatientDashboard /></Protected>} />
    <Route path="/patient/dashboard" element={<Protected roles={['patient']}><PatientDashboard /></Protected>} />
    <Route path="/profile" element={<Protected roles={['patient']}><PatientProfile /></Protected>} />
    <Route path="/patient/profile" element={<Protected roles={['patient']}><PatientProfile /></Protected>} />
    <Route path="/medicines" element={<Protected roles={['patient']}><MyMedicinesPage /></Protected>} />
    <Route path="/patient/medicines" element={<Protected roles={['patient']}><MyMedicinesPage /></Protected>} />
    <Route path="/add-medicine" element={<Protected roles={['patient']}><AddMedicinePage /></Protected>} />
    <Route path="/patient/add-medicine" element={<Protected roles={['patient']}><AddMedicinePage /></Protected>} />
    <Route path="/schedule" element={<Protected roles={['patient']}><MedicineSchedulePage /></Protected>} />
    <Route path="/patient/schedule" element={<Protected roles={['patient']}><MedicineSchedulePage /></Protected>} />
    <Route path="/prescriptions" element={<Protected roles={['patient']}><PrescriptionsPage /></Protected>} />
    <Route path="/patient/prescriptions" element={<Protected roles={['patient']}><PrescriptionsPage /></Protected>} />
    <Route path="/adherence" element={<Protected roles={['patient']}><AdherencePage /></Protected>} />
    <Route path="/patient/adherence" element={<Protected roles={['patient']}><AdherencePage /></Protected>} />
    <Route path="/refills" element={<Protected roles={['patient']}><RefillPredictionPage /></Protected>} />
    <Route path="/patient/refills" element={<Protected roles={['patient']}><RefillPredictionPage /></Protected>} />
    <Route path="/categories" element={<Protected roles={['patient']}><DiseaseCategoriesPage /></Protected>} />
    <Route path="/patient/categories" element={<Protected roles={['patient']}><DiseaseCategoriesPage /></Protected>} />
    <Route path="/notifications" element={<Protected roles={['patient']}><NotificationsPage /></Protected>} />
    <Route path="/history" element={<Protected roles={['patient']}><MedicationHistoryPage /></Protected>} />

    <Route path="/caregiver" element={<Protected roles={['caregiver']}><CaregiverDashboard /></Protected>} />
    <Route path="/caregiver/dashboard" element={<Protected roles={['caregiver']}><CaregiverDashboard /></Protected>} />
    <Route path="/caregiver/patients" element={<Protected roles={['caregiver']}><CaregiverPatientDetail /></Protected>} />
    <Route path="/caregiver/patient/:id" element={<Protected roles={['caregiver']}><CaregiverPatientDetail /></Protected>} />

    <Route path="/admin" element={<Protected roles={['admin']}><AdminDashboard /></Protected>} />
    <Route path="/admin/dashboard" element={<Protected roles={['admin']}><AdminDashboard /></Protected>} />
    <Route path="/admin/users" element={<Protected roles={['admin']}><UserManagementPage /></Protected>} />
    <Route path="/admin/settings" element={<Protected roles={['admin']}><NotificationSettingsPage /></Protected>} />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>;
}
