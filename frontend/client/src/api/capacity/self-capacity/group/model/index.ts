/** 运力分组 */
export interface CapacityGroup {
  id?: number;
  enterpriseId?: number;
  groupName?: string;
  groupCode?: string;
  color?: string;
  sortOrder?: number;
  status?: number;
  remark?: string;
  memberCount?: number;
  createdAt?: string;
  updatedAt?: string;
}

/** 分组列表查询参数 */
export interface CapacityGroupParam {
  keyword?: string;
  status?: number;
  enterpriseId?: number;
  page?: number;
  limit?: number;
}

/** 分组精简项（成本规则条件下拉） */
export interface CapacityGroupOption {
  id: number;
  groupName: string;
  groupCode?: string;
  color?: string;
}

/** 分组成员 */
export interface CapacityGroupMember {
  id: number;
  groupId: number;
  driverId: number;
  driverName: string;
  driverPhone?: string;
  capacityId?: number;
  plateNumber?: string;
  bound?: boolean;
  createdAt?: string;
}

export interface CapacityGroupMemberParam {
  keyword?: string;
  page?: number;
  limit?: number;
}
