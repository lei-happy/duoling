import { execa } from 'execa';
/** 异步任务类型 */
export type TaskType = () => Promise<any>;

/**
 * 执行打包命令
 * @param format 打包类型, es | cjs
 * @param name 组件名称
 * @param input 输入路径
 * @param output 输出文件
 * @param target 输出目录
 * @param directory 组件目录
 */
export function build(
  format?: string,
  name?: string,
  input?: string,
  output?: string,
  target?: string,
  directory?: string
): Promise<any> {
  return execa('vite', ['build', '--config', 'vite.build.ts'], {
    stdio: 'inherit',
    env: {
      NODE_ENV: 'production',
      FORMAT: format,
      NAME: name,
      INPUT: input,
      OUTPUT: output,
      TARGET: target,
      DIRECTORY: directory
    }
  });
}

/**
 * 获取组件名称
 * @param name 文件名称
 * @param directory 目录名称
 */
export function getComponentName(name: string, directory?: string) {
  if (name === 'index') {
    if (!directory || directory === '/') {
      return 'EleAdminPlus';
    }
    const dir = directory.substring(directory.lastIndexOf('/') + 1);
    return camelCase(dir);
  }
  return camelCase(name);
}

/**
 * 中划线转驼峰
 */
export function camelCase(value: string) {
  const str = value.replace(/-(\w)/g, (_, c) => (c ? c.toUpperCase() : ''));
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * 打乱数组顺序
 */
export function randomSort(array: any[]) {
  return array.sort(() => (Math.random() > 0.5 ? -1 : 1));
}

/**
 * 首字母大写
 */
export function capitalize(str: string) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * 字符串替换
 * @param content 内容
 * @param reg 正则
 * @param search 目标字符
 * @param replace 替换字符
 */
export function replaceStr(
  content: string,
  reg: RegExp | RegExp[],
  search: string,
  replace: string
) {
  let result = content;
  (Array.isArray(reg) ? reg : [reg]).forEach((r) => {
    result = result.replace(r, (m) => m.replace(search, replace));
  });
  return result;
}

/**
 * 获取命令行参数的组件路径
 */
export function getComponentArgs(): string | undefined {
  for (const argV of process.argv) {
    if (argV && argV.startsWith('src=/')) {
      return argV.substring(4);
    }
  }
}
