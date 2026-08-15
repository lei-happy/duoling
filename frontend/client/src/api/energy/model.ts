export interface EnergySupplier {
  id?: number;
  supplierCode?: string;
  supplierName?: string;
  supplierType?: number;
  status?: number;
  contactName?: string;
  contactPhone?: string;
  remark?: string;
}

export interface EnergyAccount {
  id?: number;
  accountCode?: string;
  accountName?: string;
  supplierId?: number;
  supplierName?: string;
  energyType?: string;
  accountType?: string;
  ledgerBalance?: number;
  supplierBalance?: number;
  frozenAmount?: number;
  availableBalance?: number;
  diffAmount?: number;
  status?: number;
  cardCount?: number;
  remark?: string;
}

export interface EnergyCard {
  id?: number;
  accountId?: number;
  accountName?: string;
  cardNo?: string;
  status?: number;
  vehicleId?: number;
  driverId?: number;
}

export interface EnergyRecharge {
  id?: number;
  docNo?: string;
  accountId?: number;
  accountName?: string;
  plannedAmount?: number;
  actualAmount?: number;
  status?: number;
  rechargeTime?: string;
}

export interface EnergyConsumption {
  id?: number;
  consumptionNo?: string;
  plateNumber?: string;
  cardNo?: string;
  energyType?: string;
  productName?: string;
  quantity?: number;
  unit?: string;
  unitPrice?: number;
  amount?: number;
  consumptionTime?: string;
  sourceChannel?: number;
  isLedgerAffecting?: number;
  matchStatus?: string;
}

export interface PageParam {
  page?: number;
  limit?: number;
  keyword?: string;
  [key: string]: unknown;
}
