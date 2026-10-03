import { apiFetch } from '../../api/client';
export const calculateRefill = (payload) => apiFetch('/refills/predictions/calculate/', {method:'POST',body:JSON.stringify(payload)});
export const getRefillPredictions = (profileId) => apiFetch(`/refills/predictions/${profileId ? `?profile_id=${profileId}` : ''}`);
export const updateMedicineStock = async (id, amount=30) => {
  const medicine = await apiFetch(`/medications/${id}/`);
  return apiFetch(`/medications/${id}/`, {method:'PATCH',body:JSON.stringify({stock_quantity:medicine.stock_quantity+amount})});
};
