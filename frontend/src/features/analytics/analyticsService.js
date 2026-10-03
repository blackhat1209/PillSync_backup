import { apiFetch } from '../../api/client';

export const getDashboardData = (profileId) =>
  apiFetch(`/analytics/dashboard/${profileId ? `?profile_id=${profileId}` : ''}`);

export const getAdherenceTrendsData = (profileId) =>
  apiFetch(`/analytics/trends/${profileId ? `?profile_id=${profileId}` : ''}`);
