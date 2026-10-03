import { apiFetch } from '../../api/client';
export const getStoredHistoryLogs = async (profileId) => apiFetch(`/adherence/${profileId ? `?profile_id=${profileId}` : ''}`);
export const recordIntakeLog = async (logItem) => apiFetch('/adherence/', { method:'POST', body:JSON.stringify(logItem) });
export const calculateAdherenceStats = (logs) => {
  const total=logs.length, taken=logs.filter(l=>l.status==='Taken').length, missed=logs.filter(l=>l.status==='Missed').length, snoozed=logs.filter(l=>l.status==='Snoozed').length;
  return { total, taken, missed, snoozed, percentage: total ? Math.round(taken/total*100) : 0 };
};
