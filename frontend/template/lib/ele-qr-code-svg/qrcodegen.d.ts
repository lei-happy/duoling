import { UpdateOptions } from '../ele-watermark/types';
import { injectContext } from '../ele-config-provider/receiver';

export declare function mergeProp(g: any, h: any, j: any, d: any): any;
export declare function updateProp(cs: any, p: any, ms: any, ts: any, v: any, j: any): any;
export declare const updateOptions: UpdateOptions;
export declare function mergeOptions(m: any, n: any, o: any, f: any, v: any, h: any): void;
export declare function rotate(ctx: CanvasRenderingContext2D, rotateX: number, rotateY: number, rotate: number, info: any): void;
export declare const svgText: any;
export declare const svgId: any;
export { injectContext as svgContents };
