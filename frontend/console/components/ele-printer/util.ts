import { onBeforeUnmount } from 'vue';
import { useTimer } from '../utils/hook';
import type { PrintOption, PrintTarget, PrintPdfOption } from './types';
export const printContainerId = 'ele-printer-container';
export const printFrameId = 'ele-printer-iframe';
export const printingClass = 'ele-printing';
let printIdNum = 0;

/**
 * 合并打印方法参数
 * @param options 参数
 * @param userOptions 自定义参数
 */
export function mergeOptions(options?: any, userOptions?: any) {
  if (options == null) {
    return userOptions;
  }
  return Object.assign({}, options, userOptions);
}

/**
 * 创建并获取打印容器
 */
export function getPrintContainer(): Element {
  const container = document.getElementById(printContainerId);
  if (container) {
    return container;
  }
  const elem = document.createElement('div');
  elem.id = printContainerId;
  document.body.appendChild(elem);
  return elem;
}

/**
 * 生成打印设置的样式
 * @param opt 打印参数
 */
function getOptionCss(opt: PrintOption) {
  const css = ['@page {'];
  if (opt.margin != null && opt.margin !== '') {
    const v = typeof opt.margin === 'number' ? opt.margin + 'px' : opt.margin;
    css.push(`margin: ${v};`);
  }
  if (opt.direction != null && opt.direction !== '') {
    css.push(`size: ${opt.direction};`);
  }
  if (opt.orientation != null && opt.orientation !== '') {
    css.push(`page-orientation: ${opt.orientation};`);
  }
  css.push('}');
  return css.join(' ');
}

/**
 * 移除打印子窗口
 */
function removePrintFrame() {
  const pFrame = document.getElementById(printFrameId);
  if (pFrame) {
    if (pFrame.parentNode) {
      pFrame.parentNode.removeChild(pFrame);
    }
    const url = pFrame.getAttribute('src');
    if (url) {
      try {
        window.URL.revokeObjectURL(url);
      } catch (e) {
        console.error(e);
      }
    }
  }
}

/**
 * 创建并获取打印子窗口
 */
function getPrintFrame(): HTMLIFrameElement {
  removePrintFrame();
  const elem = document.createElement('iframe');
  elem.id = printFrameId;
  elem.style.width = '66px';
  elem.style.height = '66px';
  elem.style.position = 'fixed';
  elem.style.left = '-666px';
  elem.style.top = '-666px';
  document.body.appendChild(elem);
  elem.focus();
  return elem;
}

/**
 * 在子窗口中打印
 * @param opt 打印参数
 * @param printId 唯一标识
 * @param timeout 延迟时间
 */
function doPrintOnFrame(opt: PrintOption, printId: number, timeout?: number) {
  const pFrame = getPrintFrame();
  const pWin = pFrame.contentWindow;
  if (!pWin) {
    return;
  }
  pWin.focus();
  const pDoc = pFrame.contentDocument || pWin.document;
  if (!pDoc) {
    return;
  }
  const container = getPrintContainer();
  Array.from(
    container.querySelectorAll('input[type="text"], input[type="number"]')
  ).forEach((el: HTMLInputElement) => {
    el.setAttribute('value', el.value);
  });
  pDoc.open();
  const printOption = opt.options
    ? `JSON.parse('${JSON.stringify(opt.options)}')`
    : '';
  const optHtml = `
  <style type="text/css" media="print">
    ${getOptionCss(opt)}
  </style>
  <script>
    const $html = document.querySelector('html');
    if($html && $html.classList && $html.classList.add) {
      $html.classList.add('${printingClass}');
    }
    window.onload = function() {
      if(${opt.title == null ? 0 : 1}) {
        document.title = '${opt.title}';
      }
      ${timeout != null ? 'setTimeout(() => {' : ''}
        window.print(${printOption});
        window.parent.postMessage('elePrintDone_${printId}', '*');
      ${timeout != null ? ['}, ', timeout, ');'].join('') : ''}
    };
  </script>
  `;
  const html = document.querySelector('html')?.outerHTML || '';
  const content = html
    .replace(/<script/g, '<textarea style="display:none;" ')
    .replace(/<\/script>/g, '</textarea>')
    .replace(/<\/html>/, optHtml + '</html>');
  pDoc.write(`<!DOCTYPE html>${content}`);
  pDoc.close();
  return pWin;
}

/**
 * usePrinter
 * @param done 打印结束回调
 */
export function usePrinter(done: () => void) {
  printIdNum++;
  const printId = printIdNum;
  const printTimeout = 500;
  const [startPrintTimer] = useTimer(printTimeout);

  /** 打印 */
  const doPrint = (option: PrintOption, target?: PrintTarget | null) => {
    if (target === '_iframe') {
      doPrintOnFrame(option, printId, printTimeout);
      return;
    }
    const $html = document.querySelector('html');
    if (!$html) {
      done && done();
      return;
    }
    $html.classList.add(printingClass);
    // 打印设置
    const elem = document.createElement('style');
    elem.setAttribute('type', 'text/css');
    elem.setAttribute('media', 'print');
    elem.innerHTML = getOptionCss(option);
    document.body.appendChild(elem);
    // 修改页面标题
    const title = document.title;
    if (option.title != null && option.title !== '') {
      document.title = option.title;
    }
    // 打印
    startPrintTimer(() => {
      (window as any).print(option.options);
      // 打印结束
      startPrintTimer(() => {
        $html.classList.remove(printingClass);
        document.body.removeChild(elem);
        // 恢复页面标题
        if (option.title != null) {
          document.title = title;
        }
        done && done();
      });
    });
  };

  /** 在子窗口中打印完回调 */
  const handleMessage = (e: MessageEvent<any>) => {
    if (e.data === `elePrintDone_${printId}`) {
      startPrintTimer(() => {
        removePrintFrame();
        done && done();
      });
    }
  };

  onBeforeUnmount(() => {
    window.removeEventListener('message', handleMessage);
  });

  window.addEventListener('message', handleMessage);

  return doPrint;
}

/**
 * 打印 pdf
 * @param option 打印参数
 */
export function printPdf(option: PrintPdfOption) {
  const pFrame: any = getPrintFrame();
  pFrame.onload = () => {
    const url = pFrame.getAttribute('src');
    if (!url) {
      return;
    }
    pFrame.focus();
    try {
      pFrame.contentWindow && pFrame.contentWindow.print(option.options);
      option.done && option.done();
      window.URL.revokeObjectURL(url);
      return;
    } catch (e) {
      console.error(e);
    }
    if (!option.arraybuffer && option.url) {
      window.URL.revokeObjectURL(url);
      window.open(option.url);
    } else {
      window.open(url);
    }
    option.done && option.done();
  };

  /** 开始打印 */
  const doPrint = (buffer: ArrayBuffer) => {
    const blob = new window.Blob([buffer], { type: 'application/pdf' });
    if (window.navigator && window.navigator['msSaveOrOpenBlob']) {
      window.navigator['msSaveOrOpenBlob'](blob, 'print.pdf');
      option.done && option.done();
      return;
    }
    pFrame.setAttribute('src', window.URL.createObjectURL(blob));
  };

  if (option.arraybuffer) {
    doPrint(option.arraybuffer);
    return;
  }

  // 请求地址数据
  if (option.url) {
    const req = new window.XMLHttpRequest();
    req.open('GET', option.url, true);
    req.responseType = 'arraybuffer';
    req.onload = () => {
      if ([200, 201].indexOf(req.status) !== -1) {
        doPrint(req.response);
        return;
      }
      option.error && option.error(req.status, req.statusText);
    };
    req.send();
  }
}
