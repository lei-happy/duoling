import { PageParam } from '@/api';

/**
 * 文件上传记录
 */
export interface FileRecord {
  /** id */
  id: number;
  /** 文件名称 */
  name?: string;
  /** 文件存储路径 */
  path?: string;
  /** 文件大小 */
  length?: number;
  /** 文件类型 */
  contentType?: string;
  /** 上传人id */
  createUserId?: number;
  /** 上传时间 */
  createTime?: string;
  /** 文件访问地址 */
  url?: string;
  /** 文件缩略图访问地址 */
  thumbnail?: string;
  /** 文件下载地址 */
  downloadUrl?: string;
  /** 上传人账号 */
  createUsername?: string;
  /** 上传人名称 */
  createNickname?: string;
}

/**
 * 文件上传记录查询参数
 */
export interface FileRecordParam extends PageParam {
  /** 文件名称 */
  name?: string;
  /** 文件存储路径 */
  path?: string;
  /** 上传人名称 */
  createNickname?: string;
}
