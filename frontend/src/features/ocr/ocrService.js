import { apiFetch } from '../../api/client';
export const parsePrescriptionText = (rawText) => apiFetch('/ocr/extract/', {method:'POST',body:JSON.stringify({raw_text:rawText})});
export const uploadPrescription = (file) => { const data=new FormData(); data.append('image',file); return apiFetch('/ocr/extract/',{method:'POST',body:data}); };
