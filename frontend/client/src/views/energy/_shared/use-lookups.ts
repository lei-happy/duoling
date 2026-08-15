import { ref } from 'vue';
import { pageAccounts, pageStations, pageSuppliers, listProducts } from '@/api/energy';
import { pageVehicles } from '@/api/capacity/self-capacity/vehicle';
import { pageDrivers } from '@/api/capacity/self-capacity/driver';
import { asPage } from './options';

export function useEnergyLookups() {
  const suppliers = ref<any[]>([]);
  const accounts = ref<any[]>([]);
  const products = ref<any[]>([]);
  const vehicles = ref<any[]>([]);
  const drivers = ref<any[]>([]);
  const stations = ref<any[]>([]);

  const loadSuppliers = async () => {
    try {
      suppliers.value = asPage(await pageSuppliers({ page: 1, limit: 100 })).list;
    } catch {
      suppliers.value = [];
    }
  };

  const loadAccounts = async () => {
    try {
      accounts.value = asPage(await pageAccounts({ page: 1, limit: 100 })).list;
    } catch {
      accounts.value = [];
    }
  };

  const loadProducts = async () => {
    try {
      products.value = (await listProducts()) || [];
    } catch {
      products.value = [];
    }
  };

  const loadVehicles = async () => {
    try {
      vehicles.value = asPage(await pageVehicles({ page: 1, limit: 200 })).list;
    } catch {
      vehicles.value = [];
    }
  };

  const loadDrivers = async () => {
    try {
      drivers.value = asPage(await pageDrivers({ page: 1, limit: 200 })).list;
    } catch {
      drivers.value = [];
    }
  };

  const loadStations = async (supplierId?: number) => {
    try {
      stations.value = asPage(
        await pageStations({ page: 1, limit: 100, supplierId })
      ).list;
    } catch {
      stations.value = [];
    }
  };

  return {
    suppliers,
    accounts,
    products,
    vehicles,
    drivers,
    stations,
    loadSuppliers,
    loadAccounts,
    loadProducts,
    loadVehicles,
    loadDrivers,
    loadStations
  };
}
