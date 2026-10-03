import { apiFetch } from '../../api/client';
export const getReminders = (profileId) => apiFetch(`/reminders/${profileId ? `?profile_id=${profileId}` : ''}`);
export const processReminderAction = (reminderId, action, profileId, medName) => apiFetch(`/reminders/${reminderId}/${action === 'Taken' ? 'take' : action === 'Missed' ? 'miss' : 'snooze'}/`, {method:'POST',body:action==='Snoozed'?JSON.stringify({minutes:30}):undefined});
