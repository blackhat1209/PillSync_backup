import { apiFetch } from '../../api/client';

export const getStoredMedicines = async (profileId) => {
  const query = profileId ? `?profile_id=${profileId}` : '';
  return apiFetch(`/medications/${query}`);
};

export const saveMedicine = async (medicine) => apiFetch('/medications/', {
  method: medicine.id ? 'PATCH' : 'POST',
  body: JSON.stringify(medicine),
});

export const deleteMedicine = async (id) => apiFetch(`/medications/${id}/`, { method:'DELETE' });
export const getSchedules = async (profileId) => apiFetch(`/medications/schedules/${profileId ? `?profile_id=${profileId}` : ''}`);
export const saveSchedule = async (schedule) => apiFetch('/medications/schedules/', { method:'POST', body:JSON.stringify(schedule) });
