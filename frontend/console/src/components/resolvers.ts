import type { ComponentResolver } from 'unplugin-vue-components/types';
import { resolve } from 'node:path';
import { readdirSync } from 'node:fs';
const excludes = ['icons', 'index.ts', 'lite.ts', 'resolvers.ts'];
const componentNames = readdirSync(resolve('src/components')).filter(
  (name) => !excludes.includes(name)
);

/**
 * 公共组件按需引入方式
 */
export function ComponentsResolver(): ComponentResolver {
  return {
    type: 'component',
    resolve: (name: string): any => {
      if (componentNames.includes(name)) {
        return {
          name,
          from: `@/components`
        };
      }
    }
  };
}
