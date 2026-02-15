import dts from 'vite-plugin-dts';
import type { PluginOption } from 'vite';
import { replaceStr } from './build-util';
const FILE_REGEX = /\.(js|vue|ts|jsx|tsx)$/;

/**
 * vue 引入路径处理插件
 */
export function VuePathPlugin(): PluginOption {
  return {
    name: 'VuePathPlugin',
    apply: 'build',
    enforce: 'post',
    transform: (src: string, id: string) => {
      if (
        FILE_REGEX.test(id) &&
        !id.endsWith('code-generator.ts') &&
        !id.endsWith('code-template.ts')
      ) {
        const vueSuffixReg = [/from\s".*?\.vue"/g, /from\s'.*?\.vue'/g];
        const result = replaceStr(src, vueSuffixReg, '.vue', '');
        return { code: result };
      }
    }
  };
}

/**
 * 生成 DTS 的插件
 */
export function DTSPlugin(directory?: string, name?: string): PluginOption {
  const path = `components${directory}/`.replace(/\/\//g, '/');
  return dts({
    /** 静态导入 */
    staticImport: false,
    /** 是否跳过类型检查 */
    //skipDiagnostics: true,
    /** .vue.d.ts 转为 .d.ts */
    cleanVueFileName: true,
    /** 是否使用路径别名 */
    pathsToAliases: false,
    /** 入口文件的根路径 */
    entryRoot: `${path}`,
    /** 包含路径 */
    include: [`${path}${name}.ts`, `${path}${name}.vue`, `${path}${name}.tsx`],
    /** 排除路径 */
    exclude: ['node_module/**'],
    /** 转换文件路径和文件内容 */
    beforeWriteFile: (filePath: string, content: string) => {
      const mjsSuffixReg = [
        /import\("element-plus.*?\.mjs"/g,
        /import\('element-plus.*?\.mjs'/g,
        /from\s"element-plus.*?\.mjs"/g,
        /from\s'element-plus.*?\.mjs'/g
      ];
      const result = replaceStr(content, mjsSuffixReg, '.mjs', '')
        .replace(/import\('vue\/dist\/vue.js'/g, `import\('vue'`)
        .replace(
          /import\('element-plus\/es\/element-plus\/index.js'/g,
          `import\('element-plus'`
        );
      return { filePath, content: result };
    }
  });
}
