import type { PageParam } from '@/api';

export interface Driver {
  id?: number;
  driverCode?: string;
  userId?: number;
  name?: string;
  gender?: number;
  phone?: string;
  idCard?: string;
  avatar?: string;
  emergencyContact?: string;
  emergencyPhone?: string;
  homeAddress?: string;
  status?: number;
  remark?: string;
  licenseType?: string;
  licenseNo?: string;
  licenseExpire?: string;
  qualificationNo?: string;
  qualificationExpire?: string;
  licensePhoto?: string;
  qualificationPhoto?: string;
  idCardFrontPhoto?: string;
  idCardBackPhoto?: string;
  departmentId?: number;
  departmentName?: string;
  /** 所属经营主体ID */
  enterpriseId?: number;
  driverType?: string;
  residentAreas?: ResidentArea[];
  commonRoutes?: string;
  operationStatus?: number;
  createdAt?: string;
}

export interface ResidentArea {
  province?: string;
  city?: string;
}

export interface DriverParam extends PageParam {
  keyword?: string;
  status?: number;
  driverType?: string;
  operationStatus?: number;
  departmentId?: number;
  enterpriseId?: number;
}

export interface DriverAccount {
  id?: number;
  driverId?: number;
  enterpriseId?: number;
  accountType?: number;
  accountName?: string;
  accountNo?: string;
  balance?: number;
  status?: number;
  createdAt?: string;
  updatedAt?: string;
}

export interface DriverRoute {
  id?: number;
  driverId?: number;
  originCode?: string;
  originName?: string;
  destCode?: string;
  destName?: string;
  status?: number;
}

/** 驾驶员资金账户（往来账） */
export interface DriverFundAccount {
  id?: number;
  driverId?: number;
  enterpriseId?: number;
  balance?: number;
  frozenAmount?: number;
  totalIn?: number;
  totalOut?: number;
  status?: number;
  lastTxnAt?: string;
  remark?: string;
  createdAt?: string;
  updatedAt?: string;
}

/** 资金流水 */
export interface DriverFundTransaction {
  id?: number;
  accountId?: number;
  driverId?: number;
  enterpriseId?: number;
  txnNo?: string;
  bizType?: number;
  direction?: number;
  amount?: number;
  delta?: number;
  balanceBefore?: number;
  balanceAfter?: number;
  relatedTaskId?: number;
  relatedFinanceDocId?: number;
  source?: number;
  operatorId?: number;
  operatorName?: string;
  voucherUrl?: string;
  remark?: string;
  createdAt?: string;
}

/** 记账入参 */
export interface DriverFundTransactionParam {
  bizType: number;
  amount: number;
  direction?: number;
  relatedTaskId?: number;
  relatedFinanceDocId?: number;
  voucherUrl?: string;
  remark?: string;
}
