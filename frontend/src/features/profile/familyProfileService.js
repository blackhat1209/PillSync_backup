import { apiFetch } from '../../api/client';

export const getStoredProfiles = async () => apiFetch('/profiles/');
export const getActiveProfile = async () => {
  const profiles = await getStoredProfiles();
  return profiles.find(p => p.is_primary) || profiles[0] || null;
};
export const setActiveProfileId = async (profileId) => apiFetch(`/profiles/${profileId}/set_primary/`, { method: 'POST' });
export const saveProfile = async (profileObj) => {
  if (profileObj.id) return apiFetch(`/profiles/${profileObj.id}/`, { method:'PATCH', body: JSON.stringify(profileObj) });
  return apiFetch('/profiles/', { method:'POST', body: JSON.stringify(profileObj) });
};
export const deleteProfile = async (profileId) => apiFetch(`/profiles/${profileId}/`, { method:'DELETE' });
