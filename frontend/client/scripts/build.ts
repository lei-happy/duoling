/** 打包组件库 */
import pLimit from 'p-limit';
import { rm, mkdir, cp, writeFile, readFile, readdir } from 'node:fs/promises';
import { readdirSync, statSync } from 'node:fs';
import {
  TaskType,
  build,
  getComponentName,
  camelCase,
  randomSort,
  capitalize,
  getComponentArgs
} from './build-util';
/** 项目根目录 */
const PROJECT_PATH = process.cwd().replace(/\\/g, '/');
/** 打包的源目录 */
const ROOT_PATH = `${PROJECT_PATH}/components`;
/** 需要打包的文件后缀 */
const INCLUDE_SUFFIXS = ['.ts', '.js', '.vue', '.tsx', '.jsx'];
/** 排除的文件 */
const EXCLUDE_SUFFIXS = [];
/** 需要直接复制的文件后缀 */
const STATIC_SUFFIXS = [
  '.scss',
  '/types.ts',
  '/ele-app/el.ts',
  '/ele-app/plus.ts',
  '/ele-app/plusx.ts'
];
/** 限制并行任务数量, Infinity | 8 */
const LIMIT_TASK = 6;

setup(getComponentArgs());

async function setup(component?: string) {
  const timestamp = Date.now();
  await clearTarget(component);
  const tasks = buildTarget(ROOT_PATH + (component ?? ''));
  if (!component) {
    tasks.push(() => buildTypings());
  }
  console.log(`Start processing ${tasks.length} tasks...`);
  const limit = pLimit(LIMIT_TASK);
  await Promise.all(randomSort(tasks).map((t) => limit(t)));
  await copyDTS();
  const time = ((Date.now() - timestamp) / 1000).toFixed(2);
  console.log(`Done in ${time}s. (${tasks.length} tasks)`);
}

/**
 * 清空输出目录
 * @param component 只清空指定组件目录
 */
function clearTarget(component?: string): Promise<void[]> {
  const ps: Promise<void>[] = [];
  if (component) {
    ps.push(
      rm(`${PROJECT_PATH}/es${component}`, { force: true, recursive: true })
    );
    ps.push(
      rm(`${PROJECT_PATH}/lib${component}`, { force: true, recursive: true })
    );
  } else {
    ps.push(rm(`${PROJECT_PATH}/es`, { force: true, recursive: true }));
    ps.push(rm(`${PROJECT_PATH}/lib`, { force: true, recursive: true }));
    //ps.push(rm(`${PROJECT_PATH}/dist`, { force: true, recursive: true }));
    ps.push(rm(`${PROJECT_PATH}/typings`, { force: true, recursive: true }));
  }
  return Promise.all(ps);
}

/**
 * 递归打包源文件
 * @param path 路径
 */
function buildTarget(path: string): TaskType[] {
  const tasks: TaskType[] = [];
  const stat = statSync(path);
  if (isExclude(path)) {
    return tasks;
  }
  if (stat.isDirectory()) {
    const list = readdirSync(path);
    for (const item of list) {
      buildTarget(path + '/' + item).forEach((t) => {
        tasks.push(t);
      });
    }
  } else if (isStatic(path)) {
    const output = path.substring(ROOT_PATH.length + 1);
    if (output.endsWith('.ts')) {
      tasks.push(() =>
        writeDTS(path, `${PROJECT_PATH}/es/${output.replace(/.ts$/, '.d.ts')}`)
      );
    } else {
      tasks.push(() => cp(path, `${PROJECT_PATH}/es/${output}`));
      tasks.push(() => cp(path, `${PROJECT_PATH}/lib/${output}`));
    }
  } else if (isStyleJs(path)) {
    const output = path.substring(ROOT_PATH.length + 1);
    tasks.push(() => cp(path, `${PROJECT_PATH}/es/${output}`));
    tasks.push(() =>
      writeStyleJs(
        path,
        `${PROJECT_PATH}/lib/${output.replace(/.js$/, '.cjs')}`
      )
    );
  } else if (isInclude(path)) {
    const file = path.substring(path.lastIndexOf('/') + 1);
    const name = file.substring(0, file.lastIndexOf('.'));
    const start = ROOT_PATH.length + 1;
    const end = path.lastIndexOf('/');
    const directory = '/' + (end <= start ? '' : path.substring(start, end));
    const cName = getComponentName(name, directory);
    tasks.push(() =>
      build('es', cName, path, `${name}.js`, `es${directory}`, directory)
    );
    tasks.push(() =>
      build('cjs', cName, path, `${name}.cjs`, `lib${directory}`, directory)
    );
  }
  return tasks;
}

/**
 * 判断文件是否需要打包
 * @param path 文件路径
 */
function isInclude(path: string): boolean {
  for (const suffix of INCLUDE_SUFFIXS) {
    if (path.endsWith(suffix)) {
      return true;
    }
  }
  return false;
}

/**
 * 判断文件是否排除打包
 * @param path 文件路径
 */
function isExclude(path: string): boolean {
  for (const suffix of EXCLUDE_SUFFIXS) {
    if (path.endsWith(suffix)) {
      return true;
    }
  }
  return false;
}

/**
 * 判断文件是否直接复制不经过打包
 * @param path 文件路径
 */
function isStatic(path: string): boolean {
  for (const suffix of STATIC_SUFFIXS) {
    if (path.endsWith(suffix)) {
      return true;
    }
  }
  return false;
}

/**
 * 判断文件是否是样式按需引入的 js
 * @param path 文件路径
 */
function isStyleJs(path: string): boolean {
  return (
    path.endsWith('/style/index.js') ||
    (path.includes('/ele-app/style/') && path.endsWith('.js'))
  );
}

/**
 * 获取所有组件名称
 */
async function listComponents(): Promise<string[]> {
  const components = await readdir(ROOT_PATH);
  return components.filter((name) => name.startsWith('ele-'));
}

/**
 * 构建样式按需引入的 js 到 lib
 * @param path 源路径
 * @param output 输出路径
 */
async function writeStyleJs(path: string, output: string): Promise<void> {
  const content = await readFile(path, 'utf-8');
  await mkdir(output.substring(0, output.lastIndexOf('/')), {
    recursive: true
  });
  await writeFile(
    output,
    `"use strict";\n` +
      content
        .replace(/import '/g, 'require("')
        .replace(/';/g, '");')
        .replace(/"element-plus\/es\//g, '"element-plus/lib/')
  );
}

/**
 * 构建类型定义的 ts
 * @param path 源路径
 * @param output 输出路径
 */
async function writeDTS(path: string, output: string): Promise<void> {
  const content = await readFile(path, 'utf-8');
  await mkdir(output.substring(0, output.lastIndexOf('/')), {
    recursive: true
  });
  await writeFile(
    output,
    content
      .replace(/from\s'.*?\.vue'/g, (m) => m.replace('.vue', ''))
      .replace(/from\s".*?\.vue"/g, (m) => m.replace('.vue', ''))
  );
}

/**
 * 生成全局引入的组件类型定义
 */
async function buildTypings(): Promise<void> {
  const components = await listComponents();
  const imports = components
    .map((c) => {
      const name = capitalize(camelCase(c));
      return `    ${name}: (typeof import('ele-admin-plus'))['${name}'];`;
    })
    .join('\n');
  const content = [
    '/* eslint-disable @typescript-eslint/consistent-type-imports */',
    `declare module 'vue' {`,
    '  export interface GlobalComponents {',
    imports,
    '  }',
    '}',
    'export {};',
    ''
  ].join('\n');
  await mkdir(PROJECT_PATH + '/typings', { recursive: true });
  await writeFile(PROJECT_PATH + '/typings/global.d.ts', content);
}

/**
 * 复制 dts 文件到 lib 下
 */
async function copyDTS(): Promise<void> {
  const path = `${PROJECT_PATH}/es`;
  await Promise.all(copyDTSItem(path, path));
}

/**
 * 递归复制所有 dts文件
 * @param path 源路径
 * @param rootPath 根路径
 */
function copyDTSItem(path: string, rootPath: string): Promise<void>[] {
  const ps: Promise<void>[] = [];
  const stat = statSync(path);
  if (stat.isDirectory()) {
    const list = readdirSync(path);
    for (const item of list) {
      copyDTSItem(`${path}/${item}`, rootPath).forEach((t) => {
        ps.push(t);
      });
    }
  } else if (path.endsWith('.d.ts')) {
    const output = path.substring(rootPath.length + 1);
    ps.push(cp(path, `${PROJECT_PATH}/lib/${output}`));
  }
  return ps;
}
