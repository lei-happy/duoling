import { defineStore } from 'pinia';

/**
 * 消息通知
 */
export interface Notice {
  /** 通知id */
  id: number;
  /** 图标颜色 */
  color?: string;
  /** 图标 */
  icon?: string;
  /** 标题 */
  title?: string;
  /** 时间 */
  time?: string;
}

/**
 * 用户私信
 */
export interface Letter {
  /** 私信id */
  id: number;
  /** 头像 */
  avatar?: string;
  /** 标题 */
  title?: string;
  /** 内容 */
  content?: string;
  /** 时间 */
  time?: string;
}

/**
 * 待办事项
 */
export interface Todo {
  /** 待办id */
  id: number;
  /** 状态 */
  status?: number;
  /** 标题 */
  title?: string;
  /** 描述 */
  description?: string;
}

/**
 * 消息通知状态管理
 */
export const useNoticeStore = defineStore('notice', {
  state: () => ({
    /** 消息通知 */
    notices: [] as Notice[],
    /** 用户私信 */
    letters: [] as Letter[],
    /** 待办事项 */
    todos: [] as Todo[]
  }),
  getters: {
    /** 未读数量 */
    unreadNum(): number {
      return this.notices.length + this.letters.length + this.todos.length;
    }
  },
  actions: {
    /**
     * 设置消息通知数据
     */
    setNotices(data: Notice[]) {
      this.notices = data;
    },
    /**
     * 添加消息通知
     */
    addNotice(item: Notice) {
      this.notices.push(item);
    },
    /**
     * 清空消息通知
     */
    clearNotice() {
      this.notices = [];
    },
    /**
     * 设置用户私信数据
     */
    setLetters(data: Letter[]) {
      this.letters = data;
    },
    /**
     * 添加用户私信
     */
    addLetter(item: Letter) {
      this.letters.push(item);
    },
    /**
     * 清空用户私信
     */
    clearLetter() {
      this.letters = [];
    },
    /**
     * 设置待办事项数据
     */
    setTodos(data: Todo[]) {
      this.todos = data;
    },
    /**
     * 添加待办事项
     */
    addTodo(item: Todo) {
      this.todos.push(item);
    },
    /**
     * 清空待办事项
     */
    clearTodo() {
      this.todos = [];
    }
  }
});
