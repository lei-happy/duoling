import request from '@/utils/request';
import type { ApiResult, PageResult } from '@/api';
import type { Message, UserItem, UserScore, Piece, PieceParam } from './model';

/**
 * 分页查询通知
 */
export async function pageNotices(_params: any) {
  const res = await request.get<PageResult<Message>>(
    'https://cdn.eleadmin.com/20200610/notices.json'
  );
  return res.data;
}

/**
 * 分页查询私信
 */
export async function pageLetters(_params: any) {
  const res = await request.get<PageResult<Message>>(
    'https://cdn.eleadmin.com/20200610/letters.json'
  );
  return res.data;
}

/**
 * 分页查询代办
 */
export async function pageTodos(_params: any) {
  const res = await request.get<PageResult<Message>>(
    'https://cdn.eleadmin.com/20200610/todos.json'
  );
  return res.data;
}

/**
 * 查询未读数量
 */
export async function getUnReadNum() {
  return { notice: 2, letter: 3, todo: 4 };
}

/**
 * 获取已添加成员
 */
export async function listAddedUsers() {
  const data: UserItem[] = [
    {
      key: '1',
      number: '00001',
      name: 'John Brown',
      department: '研发部'
    },
    {
      key: '2',
      number: '00002',
      name: 'Jim Green',
      department: '产品部'
    },
    {
      key: '3',
      number: '00003',
      name: 'Joe Black',
      department: '产品部'
    }
  ];
  return data;
}

/**
 * 获取成绩
 */
export async function pageUserScores() {
  const data: UserScore[] = [
    {
      id: 1,
      userName: '张三',
      courseName: '语文',
      score: 90,
      userNameRowSpan: 3
    },
    {
      id: 2,
      userName: '张三',
      courseName: '数学',
      score: 98,
      userNameRowSpan: 0
    },
    {
      id: 3,
      userName: '张三',
      courseName: '英语',
      score: 80,
      userNameRowSpan: 0
    },
    {
      id: 4,
      userName: '李四',
      courseName: '语文',
      score: 92,
      userNameRowSpan: 4
    },
    {
      id: 5,
      userName: '李四',
      courseName: '数学',
      score: 96,
      userNameRowSpan: 0
    },
    {
      id: 6,
      userName: '李四',
      courseName: '英语',
      score: 60,
      userNameRowSpan: 0
    },
    {
      id: 7,
      userName: '李四',
      courseName: '理综',
      score: 150,
      userNameRowSpan: 0
    },
    {
      id: 8,
      userName: '王五',
      courseName: '语文',
      score: 88,
      userNameRowSpan: 2
    },
    {
      id: 9,
      userName: '王五',
      courseName: '数学',
      score: 80,
      userNameRowSpan: 0
    },
    {
      id: 10,
      userName: '赵六',
      courseName: '语文',
      score: 90
    },
    {
      id: 11,
      userName: '支持跨多行多列',
      courseName: '',
      score: 0,
      userNameRowSpan: 1,
      userNameColSpan: 3,
      courseNameRowSpan: 0,
      courseNameColSpan: 0,
      scoreRowSpan: 0,
      scoreColSpan: 0
    },
    {
      id: 12,
      userName: 'EleAdmin',
      courseName: '',
      score: 20,
      userNameRowSpan: 3,
      userNameColSpan: 2,
      courseNameRowSpan: 0,
      courseNameColSpan: 0
    },
    {
      id: 13,
      userName: 'EleAdmin',
      courseName: '',
      score: 30,
      userNameRowSpan: 0,
      userNameColSpan: 1,
      courseNameRowSpan: 0,
      courseNameColSpan: 1
    },
    {
      id: 14,
      userName: 'EleAdmin',
      courseName: '',
      score: 10,
      userNameRowSpan: 0,
      userNameColSpan: 1,
      courseNameRowSpan: 0,
      courseNameColSpan: 1
    },
    {
      id: 15,
      userName: 'HTML',
      courseName: 'CSS',
      score: 0,
      userNameRowSpan: 1,
      userNameColSpan: 1,
      courseNameRowSpan: 3,
      courseNameColSpan: 2,
      scoreRowSpan: 0,
      scoreColSpan: 0
    },
    {
      id: 16,
      userName: 'JavaScript',
      courseName: 'CSS',
      score: 0,
      userNameRowSpan: 3,
      userNameColSpan: 1,
      courseNameRowSpan: 0,
      courseNameColSpan: 1,
      scoreRowSpan: 0,
      scoreColSpan: 1
    },
    {
      id: 17,
      userName: 'JavaScript',
      courseName: 'CSS',
      score: 0,
      userNameRowSpan: 0,
      userNameColSpan: 1,
      courseNameRowSpan: 0,
      courseNameColSpan: 1,
      scoreRowSpan: 0,
      scoreColSpan: 1
    },
    {
      id: 18,
      userName: 'JavaScript',
      courseName: 'Vue',
      score: 100,
      userNameRowSpan: 0,
      userNameColSpan: 1,
      courseNameRowSpan: 1,
      courseNameColSpan: 1,
      scoreRowSpan: 2,
      scoreColSpan: 1
    },
    {
      id: 19,
      userName: 'element-plus',
      courseName: 'element-plus',
      score: 100,
      userNameRowSpan: 1,
      userNameColSpan: 2,
      courseNameRowSpan: 1,
      courseNameColSpan: 0,
      scoreRowSpan: 0,
      scoreColSpan: 1
    },
    {
      id: 20,
      userName: 'pinia',
      courseName: 'axios',
      score: 0,
      userNameRowSpan: 1,
      userNameColSpan: 1,
      courseNameRowSpan: 1,
      courseNameColSpan: 2,
      scoreRowSpan: 1,
      scoreColSpan: 0
    }
  ];
  return data;
}

/**
 * 获取案卷列表
 */
export async function getPieceList(params: PieceParam) {
  const res = await request.get<ApiResult<PageResult<Piece>>>(
    'https://cdn.eleadmin.com/20200610/document.json',
    { params }
  );
  if (res.data.code === 0 && res.data.data) {
    return res.data.data;
  }
  return Promise.reject(new Error(res.data.message));
}

/**
 * 查询项目进度
 */
export async function getProjectList() {
  const res = await request.get(
    'https://cdn.eleadmin.com/20200610/project-list.json'
  );
  return res.data;
}

/**
 * 获取演示markdown
 */
export async function getDemoMD() {
  const res = await request.get<string>(
    'https://cdn.eleadmin.com/20200610/demo.md'
  );
  return res.data;
}

/**
 * 获取演示多选卡片
 */
export async function getDemoCardData() {
  return [
    {
      value: 1,
      title: 'ElementUI',
      content:
        'Element, 一套为开发者、设计师和产品经理准备的基于 Vue 2.0 的组件库, 提供了配套设计资源, 帮助你的网站快速成型。',
      avatar:
        'https://cdn.eleadmin.com/20200609/c184eef391ae48dba87e3057e70238fb.jpg'
    },
    {
      value: 2,
      title: 'Vue.js',
      content:
        'Vue 是一套用于构建用户界面的渐进式框架。与其它大型框架不同的是, Vue 被设计为可以自底向上逐层应用。',
      avatar:
        'https://cdn.eleadmin.com/20200609/b6a811873e704db49db994053a5019b2.jpg'
    },
    {
      value: 3,
      title: 'Vue Router',
      content:
        'Vue Router 是 Vue.js 官方的路由管理器。它和 Vue.js 的核心深度集成, 让构建单页面应用变得易如反掌。',
      avatar:
        'https://cdn.eleadmin.com/20200609/f6bc05af944a4f738b54128717952107.jpg'
    }
  ];
}
