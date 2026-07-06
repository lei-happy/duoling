import { PageParam } from '@/api';

/**
 * 经营主体（法人/独立核算单元）
 */
export interface BusinessEntity {
  /** 主键ID */
  id?: number;
  /** 主体编码（留空自动生成） */
  entityCode?: string;
  /** 主体名称（法人全称） */
  entityName?: string;
  /** 简称 */
  shortName?: string;
  /** 统一社会信用代码 */
  unifiedCreditCode?: string;
  /** 法定代表人 */
  legalPerson?: string;
  /** 注册地址 */
  registeredAddress?: string;
  /** 联系人 */
  contactPerson?: string;
  /** 联系电话 */
  contactPhone?: string;
  /** 对公开户行 */
  bankName?: string;
  /** 对公账号 */
  bankAccount?: string;
  /** 开票抬头 */
  invoiceTitle?: string;
  /** 开票税号 */
  invoiceTaxNo?: string;
  /** 是否默认主体 1-是 0-否 */
  isDefault?: number;
  /** 状态 1-正常 0-停用 */
  status?: number;
  /** 排序号 */
  sortOrder?: number;
  /** 备注 */
  remark?: string;
  /** 创建时间 */
  createdAt?: string;
}

/**
 * 经营主体下拉选项
 */
export interface BusinessEntityOption {
  id: number;
  entityName: string;
  shortName?: string;
  isDefault?: number;
}

/**
 * 经营主体搜索条件
 */
export interface BusinessEntityParam extends PageParam {
  /** 名称/编码/简称关键字 */
  keyword?: string;
  /** 状态 1-正常 0-停用 */
  status?: number;
}
