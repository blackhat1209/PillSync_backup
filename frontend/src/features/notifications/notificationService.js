import { apiFetch } from '../../api/client';
export const getStoredNotifications = (profileId) => apiFetch(`/notifications/${profileId ? `?profile_id=${profileId}` : ''}`);
export const markNotificationRead = (id) => apiFetch(`/notifications/${id}/`, {method:'PATCH',body:JSON.stringify({is_read:true})});
