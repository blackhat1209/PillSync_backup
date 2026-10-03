import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, CheckCircle2, RefreshCw, AlertTriangle, Pill, Plus, FileText } from 'lucide-react';
import { getActiveProfile } from '../../features/profile/familyProfileService';
import { getDashboardData } from '../../features/analytics/analyticsService';
import { getStoredMedicines, getSchedules } from '../../features/medications/medicationService';
import { getStoredHistoryLogs, recordIntakeLog } from '../../features/adherence/historyService';

export default function PatientDashboard({ currentUser }) {
  const navigate = useNavigate();

  const [doses, setDoses] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadDashboard = async () => {
    try {
      setLoading(true);
      setError('');

      const activeProfile = await getActiveProfile();

      if (!activeProfile) {
        setProfile(null);
        setDoses([]);
        setDashboard(null);
        return;
      }

      setProfile(activeProfile);

      const [dashboardData, medicines, schedules, history] = await Promise.all([
        getDashboardData(activeProfile.id),
        getStoredMedicines(activeProfile.id),
        getSchedules(activeProfile.id),
        getStoredHistoryLogs(activeProfile.id),
      ]);

      setDashboard(dashboardData);

      const today = new Date().toISOString().split('T')[0];

      const todayLogs = history.filter(
        log => log.action_date === today
      );

      const scheduleDoses = schedules
        .filter(schedule => schedule.is_active !== false)
        .map(schedule => {
          const medicine = medicines.find(
            m => m.id === schedule.medicine || m.id === schedule.medicine_id
          );

          const existingLog = todayLogs.find(
            log =>
              log.medicine_id === medicine?.id &&
              log.action_time === schedule.scheduled_time
          );

          return {
            id: schedule.id,
            medicineId: medicine?.id || schedule.medicine || schedule.medicine_id,
            scheduleId: schedule.id,
            name: medicine?.name || 'Medicine',
            category: medicine?.category || 'Other',
            instructions: medicine?.instructions || medicine?.dosage || '',
            time: schedule.scheduled_time?.slice(0, 5) || '--:--',
            dosage: schedule.dosage_amount || '1',
            status: existingLog?.status || 'PENDING',
            logId: existingLog?.id || null,
            loggedAt: existingLog?.logged_at
              ? new Date(existingLog.logged_at).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit'
                })
              : null
          };
        })
        .sort((a, b) => a.time.localeCompare(b.time));

      setDoses(scheduleDoses);
    } catch (e) {
      console.error(e);
      setError(e.message || 'Unable to load dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleStatusChange = async (dose, newStatus) => {
    try {
      if (!profile || !dose.medicineId) return;

      await recordIntakeLog({
        patient_profile: profile.id,
        medicine: dose.medicineId,
        schedule: dose.scheduleId,
        action_date: new Date().toISOString().split('T')[0],
        action_time: `${dose.time}:00`,
        status: newStatus,
        notes: `Marked ${newStatus.toLowerCase()} from dashboard`
      });

      await loadDashboard();
    } catch (e) {
      console.error(e);
      setError(e.message || 'Unable to update medication status.');
    }
  };

  const adherence = dashboard?.adherence || {};
  const takenCount = adherence.taken || 0;
  const totalCount = adherence.total || 0;
  const adherenceRate = Math.round(adherence.percentage || 0);

  if (loading) {
    return (
      <div className="glass-card" style={{ padding: 30, textAlign: 'center' }}>
        Loading your medication dashboard...
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

      {error && (
        <div style={{
          padding: '12px 16px',
          borderRadius: '10px',
          backgroundColor: '#fef2f2',
          color: '#b91c1c',
          border: '1px solid #fecaca'
        }}>
          {error}
        </div>
      )}

      {/* Top Stat Cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '16px'
      }}>

        {/* Adherence Rate Widget */}
        <div className="glass-card" style={{ padding: '20px' }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <span style={{
              fontSize: '0.85rem',
              fontWeight: 600,
              color: '#64748b'
            }}>
              Today's Adherence Rate
            </span>

            <span style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              color: totalCount > 0 ? '#DC143C' : '#94a3b8',
              backgroundColor: '#FFF0F3',
              padding: '2px 8px',
              borderRadius: '12px'
            }}>
              {totalCount > 0
                ? `${takenCount}/${totalCount} Completed`
                : 'No Data'}
            </span>
          </div>

          <div style={{
            fontSize: '2.2rem',
            fontWeight: 900,
            color: '#DC143C',
            margin: '8px 0'
          }}>
            {adherenceRate}%
          </div>

          <div style={{
            height: '8px',
            backgroundColor: '#f1f5f9',
            borderRadius: '4px',
            overflow: 'hidden'
          }}>
            <div style={{
              width: `${adherenceRate}%`,
              height: '100%',
              backgroundColor: '#DC143C',
              transition: 'width 0.4s ease'
            }} />
          </div>

          <span style={{
            fontSize: '0.8rem',
            color: '#64748b',
            display: 'block',
            marginTop: '6px'
          }}>
            {totalCount > 0
              ? `${takenCount} of ${totalCount} recorded doses completed`
              : 'Add medicines to track daily adherence'}
          </span>
        </div>

        {/* Quick Actions */}
        <div className="glass-card" style={{
          padding: '20px',
          backgroundColor: '#FFF0F3',
          border: '1px solid #FFD6DC'
        }}>
          <span style={{
            fontSize: '0.8rem',
            fontWeight: 800,
            color: '#DC143C',
            textTransform: 'uppercase'
          }}>
            Quick Actions
          </span>

          <h3 style={{
            margin: '4px 0 10px',
            fontSize: '1.05rem',
            fontWeight: 800,
            color: '#2B181D'
          }}>
            Manage Your Medication
          </h3>

          <div style={{
            display: 'flex',
            gap: '8px',
            flexWrap: 'wrap'
          }}>
            <button
              onClick={() => navigate('/add-medicine')}
              className="btn-primary"
              style={{
                fontSize: '0.82rem',
                padding: '8px 14px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <Plus size={15} /> Add Medicine
            </button>

            <button
              onClick={() => navigate('/prescriptions')}
              style={{
                border: '1px solid #DC143C',
                color: '#DC143C',
                background: 'white',
                padding: '8px 12px',
                borderRadius: '8px',
                fontWeight: 700,
                fontSize: '0.82rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <FileText size={15} /> Upload Prescription
            </button>
          </div>
        </div>

      </div>

      {/* Additional Summary */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '12px'
      }}>
        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ color: '#64748b', fontSize: '0.8rem' }}>
            Active Medicines
          </div>
          <div style={{
            fontSize: '1.6rem',
            fontWeight: 800,
            marginTop: '5px'
          }}>
            {dashboard?.medicines?.active || 0}
          </div>
        </div>

        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ color: '#64748b', fontSize: '0.8rem' }}>
            Missed Doses
          </div>
          <div style={{
            fontSize: '1.6rem',
            fontWeight: 800,
            marginTop: '5px'
          }}>
            {adherence.missed || 0}
          </div>
        </div>

        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ color: '#64748b', fontSize: '0.8rem' }}>
            Low Stock
          </div>
          <div style={{
            fontSize: '1.6rem',
            fontWeight: 800,
            marginTop: '5px'
          }}>
            {dashboard?.refills?.low_stock || 0}
          </div>
        </div>

        <div className="glass-card" style={{ padding: '16px' }}>
          <div style={{ color: '#64748b', fontSize: '0.8rem' }}>
            Pending Refills
          </div>
          <div style={{
            fontSize: '1.6rem',
            fontWeight: 800,
            marginTop: '5px'
          }}>
            {dashboard?.refills?.pending_requests || 0}
          </div>
        </div>
      </div>

      {/* Daily Medication Schedule */}
      <div className="glass-card" style={{ padding: '24px' }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '16px'
        }}>
          <div>
            <h2 style={{
              margin: 0,
              fontSize: '1.15rem',
              fontWeight: 800,
              color: '#0f172a'
            }}>
              Good Morning, {profile?.name || currentUser?.name || 'User'} 👋
            </h2>

            <span style={{
              fontSize: '0.85rem',
              color: '#64748b'
            }}>
              Today's Dosage Schedule
            </span>
          </div>

          <button
            onClick={() => navigate('/add-medicine')}
            className="btn-primary"
            style={{
              fontSize: '0.85rem',
              padding: '6px 12px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <Plus size={14} /> Add Medicine
          </button>
        </div>

        {doses.length === 0 ? (
          <div style={{
            padding: '40px 20px',
            textAlign: 'center',
            backgroundColor: '#FFF0F3',
            borderRadius: '16px',
            border: '2px dashed #FFD6DC'
          }}>
            <Pill size={44} color="#DC143C" style={{ marginBottom: '12px' }} />

            <h3 style={{
              margin: '0 0 6px',
              fontSize: '1.1rem',
              fontWeight: 800,
              color: '#2B181D'
            }}>
              No Medicines Scheduled Today
            </h3>

            <p style={{
              margin: '0 0 16px',
              fontSize: '0.88rem',
              color: '#7E646A',
              maxWidth: '440px',
              marginLeft: 'auto',
              marginRight: 'auto'
            }}>
              Add a medicine and create a schedule to see your daily doses here.
            </p>

            <button
              onClick={() => navigate('/add-medicine')}
              className="btn-primary"
              style={{
                fontSize: '0.9rem',
                padding: '10px 20px',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px'
              }}
            >
              <Plus size={16} /> Add Medicine Schedule
            </button>
          </div>
        ) : (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}>
            {doses.map((dose) => (
              <div
                key={dose.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '16px',
                  borderRadius: '10px',
                  border: '1px solid #e2e8f0',
                  backgroundColor:
                    dose.status === 'TAKEN'
                      ? '#f0fdf4'
                      : dose.status === 'SNOOZED'
                        ? '#fffbeb'
                        : '#ffffff'
                }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '14px'
                }}>
                  <div style={{
                    padding: '10px',
                    borderRadius: '10px',
                    backgroundColor:
                      dose.status === 'TAKEN'
                        ? '#dcfce7'
                        : '#FFF0F3',
                    color:
                      dose.status === 'TAKEN'
                        ? '#166534'
                        : '#DC143C'
                  }}>
                    <Pill size={24} />
                  </div>

                  <div>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}>
                      <h3 style={{
                        margin: 0,
                        fontSize: '1rem',
                        fontWeight: 700,
                        color: '#0f172a'
                      }}>
                        {dose.name}
                      </h3>

                      <span style={{
                        fontSize: '0.7rem',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        backgroundColor: '#e2e8f0',
                        color: '#475569',
                        fontWeight: 600
                      }}>
                        {dose.category}
                      </span>
                    </div>

                    <span style={{
                      fontSize: '0.85rem',
                      color: '#64748b'
                    }}>
                      {dose.instructions}
                    </span>
                  </div>
                </div>

                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '16px'
                }}>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      fontSize: '0.9rem',
                      fontWeight: 700,
                      color: '#1e293b'
                    }}>
                      <Clock size={15} color="#64748b" />
                      {dose.time}
                    </div>

                    {dose.loggedAt && (
                      <span style={{
                        fontSize: '0.75rem',
                        color: '#16a34a',
                        fontWeight: 600
                      }}>
                        Recorded at {dose.loggedAt}
                      </span>
                    )}
                  </div>

                  {dose.status === 'TAKEN' ? (
                    <span className="badge-taken">
                      ✓ TAKEN
                    </span>
                  ) : dose.status === 'SNOOZED' ? (
                    <span className="badge-snoozed">
                      SNOOZED
                    </span>
                  ) : (
                    <div style={{
                      display: 'flex',
                      gap: '8px'
                    }}>
                      <button
                        onClick={() => handleStatusChange(dose, 'TAKEN')}
                        className="btn-primary"
                        style={{
                          fontSize: '0.8rem',
                          padding: '6px 12px'
                        }}
                      >
                        Taken
                      </button>

                      <button
                        onClick={() => handleStatusChange(dose, 'SNOOZED')}
                        style={{
                          border: '1px solid #d97706',
                          color: '#d97706',
                          backgroundColor: '#fffbeb',
                          borderRadius: '6px',
                          padding: '6px 10px',
                          fontSize: '0.8rem',
                          fontWeight: 600,
                          cursor: 'pointer'
                        }}
                      >
                        Snooze 15m
                      </button>

                      <button
                        onClick={() => handleStatusChange(dose, 'MISSED')}
                        style={{
                          border: '1px solid #dc2626',
                          color: '#dc2626',
                          backgroundColor: '#fef2f2',
                          borderRadius: '6px',
                          padding: '6px 10px',
                          fontSize: '0.8rem',
                          fontWeight: 600,
                          cursor: 'pointer'
                        }}
                      >
                        Missed
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
