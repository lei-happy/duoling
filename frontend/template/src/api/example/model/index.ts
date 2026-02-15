import { PageParam } from '@/api';

/**
 * 消息
 */
export interface Message {
  /** 消息id */
  id?: number;
  /** 标题 */
  title?: string;
  /** 时间 */
  time?: string;
  /** 状态 */
  status?: number;
}

/**
 * 成员
 */
export interface UserItem {
  /** 成员id */
  key: string;
  /** 工号 */
  number?: string;
  /** 用户名 */
  name?: string;
  /** 部门 */
  department?: string;
  /** 是否编辑状态 */
  isEdit?: boolean;
}

/**
 * 成绩
 */
export interface UserScore {
  /** 成绩id */
  id: number;
  /** 姓名 */
  userName: string;
  /** 课程 */
  courseName: string;
  /** 得分 */
  score: number;
  /** 姓名跨行 */
  userNameRowSpan?: number;
  /** 姓名跨列 */
  userNameColSpan?: number;
  /** 课程跨行 */
  courseNameRowSpan?: number;
  /** 课程跨列 */
  courseNameColSpan?: number;
  /** 得分跨行 */
  scoreRowSpan?: number;
  /** 得分跨列 */
  scoreColSpan?: number;
}

/**
 * 案卷
 */
export interface Piece {
  /** 案卷id */
  id?: number;
  /** 案卷题名 */
  title?: string;
  /** 案卷档号 */
  piece_no?: string;
  /** 密级 */
  secret?: string;
  /** 存放位置 */
  location?: string;
  /** 案卷类型 */
  type?: string;
  /** 保管期限 */
  retention?: string;
  /** 载体类型 */
  carrier?: string;
  /** 归档年度 */
  year?: string;
  /** 件数 */
  amount?: number;
}

/**
 * 案卷查询参数
 */
export interface PieceParam extends PageParam {
  /** 案卷题名 */
  title?: string;
  /** 案卷档号 */
  piece_no?: string;
}

/**
 * 项目进度数据类型
 */
export interface Project {
  /** id */
  id: string;
  /** 项目名称 */
  projectName: string;
  /** 状态 */
  status: number;
  /** 开始时间 */
  startDate: string;
  /** 结束时间 */
  endDate: string;
  /** 进度 */
  progress: number;
  /** 金额 */
  money: number;
}

/**
 * 房屋租赁合同
 */
export interface Contract {
  /** 甲方 */
  partyA?: string;
  /** 乙方 */
  partyB?: string;
  /** 房屋地址 */
  address?: string;
  /** 日期 */
  date?: string;
  /** 项目 */
  projects?: Project[];
}
