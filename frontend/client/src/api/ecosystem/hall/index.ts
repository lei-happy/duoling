import request from '@/utils/request';
import type { ApiResult } from '@/api';
import { PostType } from '@/config/ecosystem/enums';
import type {
  EcoHallFilters,
  EcoHallParam,
  EcoPost,
  EcoPostPage
} from './model';

/**
 * 两个大厅的接口前缀
 *
 * 后端把货源与运力挂成了两个 router（`/ecosystem/cargo-hall`、
 * `/ecosystem/capacity-hall`），路径之外完全同构。前端也按 `postType` 取前缀，
 * 而不是写两套函数：写两套的下场是某次给货源大厅加了个筛选参数，运力那份忘了加。
 */
function hallBase(postType: number) {
  return postType === PostType.CAPACITY
    ? '/ecosystem/capacity-hall'
    : '/ecosystem/cargo-hall';
}

/**
 * 数组参数按重复键拼接
 *
 * 默认的参数序列化会把数组拼成 `toProvinces[0]=浙江省`，FastAPI 的
 * `List[str] = Query(None)` 收不到，筛选会静默失效（不报错，只是筛不动）。
 * 这里手工拼成 `toProvinces=浙江省&toProvinces=江苏省`。
 */
function toQuery(params: Record<string, any>): string {
  const search = new URLSearchParams();
  Object.keys(params).forEach((key) => {
    const value = params[key];
    if (value == null || value === '') {
      return;
    }
    if (Array.isArray(value)) {
      value.forEach((item) => {
        if (item != null && item !== '') {
          search.append(key, String(item));
        }
      });
      return;
    }
    search.append(key, String(value));
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

/** 大厅分页列表 */
export async function pageHall(postType: number, params: EcoHallParam) {
  const res = await request.get<ApiResult<EcoPostPage>>(
    `${hallBase(postType)}${toQuery(params)}`
  );
  if (res.data.code === 0) {
    return res.data.data as EcoPostPage;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 筛选项元数据（排序方式、计价方式、货物类别等） */
export async function getHallFilters(postType: number) {
  const res = await request.get<ApiResult<EcoHallFilters>>(
    `${hallBase(postType)}/filters`
  );
  if (res.data.code === 0) {
    return res.data.data as EcoHallFilters;
  }
  return Promise.reject(new Error(res.data.message));
}

/** 挂牌详情（后端会记一次浏览，用于给发布方看热度） */
export async function getHallDetail(postType: number, postId: number) {
  const res = await request.get<ApiResult<EcoPost>>(
    `${hallBase(postType)}/${postId}`
  );
  if (res.data.code === 0) {
    return res.data.data as EcoPost;
  }
  return Promise.reject(new Error(res.data.message));
}
