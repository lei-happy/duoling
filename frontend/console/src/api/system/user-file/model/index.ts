import { PageParam } from '@/api';

/**
 * 用户文件
 */
export interface UserFile {
  /** id */
  id?: number;
  /** 用户id */
  userId?: number;
  /** 文件名称 */
  name?: string;
  /** 是否是文件夹, 0否, 1是 */
  isDirectory?: number;
  /** 上级id */
  parentId?: number;
  /** 文件存储路径 */
  path?: string;
  /** 文件大小 */
  length?: number;
  /** 文件类型 */
  contentType?: string;
  /** 上传时间 */
  createTime?: string;
  /** 更新时间 */
  updateTime?: string;
  /** 文件访问地址 */
  url?: string;
  /** 文件缩略图访问地址 */
  thumbnail?: string;
  /** 文件下载地址 */
  downloadUrl?: string;
}

/**
 * 用户文件查询参数
 */
export interface UserFileParam extends PageParam {
  /** 文件名称 */
  name?: string;
  /** 是否是文件夹, 0否, 1是 */
  isDirectory?: number;
  /** 上级id */
  parentId?: number;
}
