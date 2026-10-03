import { apiFetch } from '../../api/client';
export const getAdherenceTrendsData = (profileId) => apiFetch(`/analytics/trends/${profileId ? `?profile_id=${profileId}` : ''}`);
