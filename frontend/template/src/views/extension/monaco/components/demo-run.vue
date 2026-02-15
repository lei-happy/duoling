<template>
  <ele-card header="代码运行" :body-style="{ padding: '12px' }">
    <div class="run-wrapper">
      <div class="editor-wrapper">
        <div class="editor-item">
          <div class="editor-item-header">
            <el-icon class="editor-item-icon">
              <CodeOutlined />
            </el-icon>
            <div>HTML</div>
          </div>
          <div class="editor-item-body">
            <monaco-editor
              v-model="htmlCode"
              language="html"
              style="height: 128px"
            />
          </div>
        </div>
        <div class="editor-item">
          <div class="editor-item-header">
            <div class="editor-item-icon is-css">*</div>
            <div>CSS</div>
          </div>
          <div class="editor-item-body">
            <monaco-editor
              v-model="cssCode"
              language="css"
              style="height: 220px"
            />
          </div>
        </div>
        <div class="editor-item">
          <div class="editor-item-header">
            <div class="editor-item-icon is-js">{}</div>
            <div>JS</div>
          </div>
          <div class="editor-item-body">
            <monaco-editor
              v-model="jsCode"
              language="javascript"
              style="height: 320px"
            />
          </div>
        </div>
      </div>
      <div class="result-wrapper">
        <div class="frame-header">
          <div class="frame-tool"></div>
          <div class="frame-tool is-warning"></div>
          <div class="frame-tool is-success"></div>
          <div style="margin: 1.68px 2px 0 auto; font-size: 12px">重新运行</div>
          <div class="frame-btn" @click="runCode()">
            <el-icon style="transform: scale(1.09) translate(0.38px, 0.48px)">
              <ReloadOutlined />
            </el-icon>
          </div>
        </div>
        <div class="result-body">
          <iframe :key="iframeKey" ref="iframeRef"></iframe>
        </div>
        <div class="console-wrapper">
          <div class="console-header">
            <span style="font-family: Consolas; vertical-align: -1px">
              <span style="font-size: 18px">></span>
              <span style="margin: 0 4px 0 -4px; vertical-align: 2px">_</span>
            </span>
            <span>Console</span>
          </div>
          <div ref="consoleBodyRef" class="console-body">
            <pre
              v-for="(item, index) in consoleCodes"
              :key="index"
              :class="[
                'console-item',
                { 'is-error': item.type === 'error' },
                { 'is-warn': item.type === 'warn' }
              ]"
              >{{ item.code }}</pre
            >
          </div>
        </div>
      </div>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import {
    ref,
    onMounted,
    onBeforeUnmount,
    nextTick,
    onActivated,
    onDeactivated
  } from 'vue';
  import { CodeOutlined, ReloadOutlined } from '@/components/icons';
  import MonacoEditor from '@/components/MonacoEditor/index.vue';
  import { generateRunCode } from './demo-codes';

  /** html代码 */
  const htmlCode =
    ref(`<div style="text-align: center;padding-top: calc(50vh - 24px);">
  <div class="demo-btn" onclick="console.warn('点击了登录按钮');">登录</div>
  <div class="demo-btn" onclick="abcdefghijk">注册</div>
</div>
<canvas class="bg-canvas" id="bgCanvas"></canvas>
`);

  /** css代码 */
  const cssCode = ref(`html {
  height: 100%;
}

body {
  margin: 0;
  padding: 0;
  height: 100%;
  background: #001121;
}

.bg-canvas {
  position: fixed;
  top: 0;
  left: 0;
  opacity: 0.6;
  pointer-events: none;
  z-index: -1;
}

.demo-btn {
  color: #01c1ec;
  background: rgba(1, 193, 236, 0.38);
  backdrop-filter: blur(4px);
  padding: 14px 42px;
  display: inline-block;
  clip-path: polygon(0 0, 90% 0, 100% 28%, 100% 100%, 10% 100%, 0 72%);
  transition: all 0.2s;
  letter-spacing: 8px;
  font-weight: bold;
  user-select: none;
  cursor: pointer;
}

.demo-btn:hover {
  color: #fff;
  background: rgba(1, 193, 236, 0.68);
}

.demo-btn + .demo-btn {
  margin-left: 12px;
}
`);

  /** js代码 */
  const jsCode = ref(`console.log('Hello World!');

const bgCanvas = document.getElementById('bgCanvas');
const ctx = bgCanvas.getContext('2d');
let width = window.innerWidth;
let height = window.innerHeight;
bgCanvas.width = width;
bgCanvas.height = height;

const points = Array.from({ length: 250 }).map(function () {
  return {
    x: Math.random() * width,
    y: Math.random() * height,
    xa: 2 * Math.random() - 1,
    ya: 2 * Math.random() - 1,
    max: 9000
  };
});

const cursor = { x: null, y: null, max: 20000 };

window.onmousemove = function (e) {
  cursor.x = e.clientX;
  cursor.y = e.clientY;
};

window.onmouseout = function () {
  cursor.x = null;
  cursor.y = null;
};

window.onresize = function () {
  width = window.innerWidth;
  height = window.innerHeight;
  bgCanvas.width = width;
  bgCanvas.height = height;
};

function move() {
  ctx.clearRect(0, 0, width, height);
  const data = [cursor].concat(points);
  points.forEach(function (item) {
    item.x += item.xa;
    item.y += item.ya;
    item.xa *= item.x > width || item.x < 0 ? -1 : 1;
    item.ya *= item.y > height || item.y < 0 ? -1 : 1;
    ctx.fillRect(item.x - 0.5, item.y - 0.5, 1, 1);
    data.forEach((p) => {
      if (item !== p && null !== p.x && null !== p.y) {
        const dX = item.x - p.x;
        const dY = item.y - p.y;
        const distance = dX * dX + dY * dY;
        if (distance < p.max) {
          if (p === cursor && distance >= p.max / 2) {
            item.x -= 0.03 * dX;
            item.y -= 0.03 * dY;
          }
          const level = (p.max - distance) / p.max;
          ctx.beginPath();
          ctx.lineWidth = level / 2;
          ctx.strokeStyle = 'rgba(1, 211, 255, ' + (level + 0.2) + ')';
          ctx.moveTo(item.x, item.y);
          ctx.lineTo(p.x, p.y);
          ctx.stroke();
        }
      }
    });
    data.splice(data.indexOf(item), 1);
  });
  window.requestAnimationFrame(move);
}

move();

console.log('Start Move.');
`);

  /** iframe */
  const iframeRef = ref<HTMLIFrameElement | null>(null);

  /** 用于重新渲染iframe */
  const iframeKey = ref(0);

  /** 控制台 */
  const consoleBodyRef = ref<HTMLElement | null>(null);

  /** 控制台信息类型 */
  interface ConsoleItem {
    /** 类型 */
    type?: 'log' | 'error' | 'warn';
    /** 内容 */
    code?: string;
  }

  /** 控制台信息 */
  const consoleCodes = ref<ConsoleItem[]>([]);

  /** 运行代码到iframe */
  const runCode = (first?: boolean) => {
    if (!first) {
      iframeKey.value++;
      nextTick(() => {
        runCode(true);
      });
      return;
    }
    consoleCodes.value = [];
    const doc = iframeRef.value?.contentWindow?.document;
    if (!doc) {
      return;
    }
    doc.open();
    doc.write(generateRunCode(cssCode.value, htmlCode.value, jsCode.value));
    doc.close();
  };

  /** 收集iframe内日志的消息监听 */
  const handleMessage = (e: MessageEvent<any>) => {
    if (e.data && e.data.id === 'iframeConsole') {
      consoleCodes.value.push(e.data);
      nextTick(() => {
        consoleBodyRef.value?.scrollTo?.(0, consoleBodyRef.value.scrollHeight);
      });
    }
  };

  onMounted(() => {
    window.addEventListener('message', handleMessage);
    runCode(true);
  });

  onBeforeUnmount(() => {
    window.removeEventListener('message', handleMessage);
  });

  const isDeactivated = ref(false);

  onActivated(() => {
    if (isDeactivated.value) {
      runCode(true);
      isDeactivated.value = false;
    }
  });

  onDeactivated(() => {
    isDeactivated.value = true;
  });
</script>

<style lang="scss" scoped>
  .run-wrapper {
    display: flex;
  }

  /* 编辑器 */
  .editor-wrapper {
    flex: 1;
    background: #1e1e1e;
    box-shadow: -1px 0 0 1px #1e1e1e inset;
    overflow: hidden;
  }

  .editor-item {
    border-top: 1px solid #2f3742;
  }

  .editor-item-header {
    font-size: 12px;
    color: #babdc0;
    background: #18212d;
    border-bottom: 1px solid #2f3742;
    display: flex;
    align-items: center;
    height: 30px;
    padding: 0 16px;
  }

  .editor-item-body {
    border-left: 1px solid #1e1e1e;
    border-right: 1px solid #1e1e1e;
  }

  .editor-wrapper > .editor-item:last-child .editor-item-body {
    border-bottom: 1px solid #1e1e1e;
  }

  /* 编辑器顶栏图标 */
  .editor-item-icon {
    width: 16px;
    height: 16px;
    line-height: 16px;
    border-radius: 4px;
    color: #18212d;
    background: #e86435;
    font-size: 12px;
    margin-right: 6px;
    text-align: center;
    box-sizing: border-box;
    user-select: none;

    &.is-css {
      font-size: 26px;
      line-height: 30px;
      background: #2397d6;
    }

    &.is-js {
      font-size: 12px;
      line-height: 15px;
      background: #eecc3b;
      font-weight: bold;
      letter-spacing: 3px;
      padding-left: 2px;
    }

    & + div {
      transform: translateY(1px);
      font-weight: bold;
    }
  }

  /* 右侧容器 */
  .result-wrapper {
    flex: 1;
    border: 1px solid #2f3742;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }

  /* 代码运行容器 */
  .result-body {
    flex: 1;
    overflow: hidden;

    iframe {
      width: 100%;
      height: 100%;
      display: block;
      border: none;
    }
  }

  /* 右侧顶栏 */
  .frame-header {
    display: flex;
    align-items: center;
    height: 30px;
    padding: 0 8px 0 20px;
    color: #babdc0;
    background: #18212d;
    border-bottom: 1px solid #2f3742;
  }

  .frame-tool {
    width: 10px;
    height: 10px;
    margin-right: 10px;
    border-radius: 50%;
    background: #ff4a4a;

    &.is-warning {
      background: #ffb83d;
    }

    &.is-success {
      background: #00c543;
    }
  }

  /* 右侧顶栏的右侧按钮 */
  .frame-btn {
    width: 22px;
    height: 22px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    user-select: none;
    cursor: pointer;

    &:hover {
      background: #445265;
    }
  }

  /* 控制台容器 */
  .console-wrapper {
    color: #e3e3e3;
    background: #1e1e1e;
  }

  .console-header {
    color: #babdc0;
    background: #18212d;
    border-bottom: 1px solid #2f3742;
    height: 30px;
    line-height: 30px;
    padding: 0 6px;
    user-select: none;
  }

  .console-body {
    height: 180px;
    overflow: auto;
    padding: 0 4px;
    font-size: 12px;
    line-height: 16px;
    --ele-scrollbar-color: #5e5e5e;
    --ele-scrollbar-hover-color: #707070;
  }

  /* 控制台信息 */
  .console-item {
    padding: 2px 6px;
    margin: 5px 0 5px 0;
    transition: all 0.2s;
    border-radius: 4px;
    position: relative;
    word-break: break-all;
    white-space: pre-wrap;

    &:hover {
      background: rgba(0, 110, 255, 0.2);
    }

    & + .console-item {
      margin-top: 0;

      &::after {
        content: '';
        border-top: 1px solid #2f3742;
        position: absolute;
        top: -3px;
        left: 6px;
        right: 6px;
      }
    }

    /* 错误信息 */
    &.is-error {
      color: #f9dedc;
      background: #4e3534;

      &::before {
        content: '⨯';
        font-size: 13px;
        color: #1e1e1e;
        background: #e46962;
        width: 11px;
        height: 11px;
        line-height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 3px;
        font-weight: bold;
        text-align: center;
        transform: translateX(-1px);
      }
    }

    /* 警告信息 */
    &.is-warn {
      color: #fdf3aa;
      background: #413c26;

      &::before {
        content: '!';
        font-size: 12px;
        color: #1e1e1e;
        background: #fe8d59;
        width: 14px;
        height: 11px;
        line-height: 12px;
        display: inline-block;
        margin-right: 1px;
        font-weight: bold;
        text-align: center;
        transform: translateX(-1px);
        clip-path: polygon(50% 0, 100% 100%, 0 100%);
      }
    }
  }

  @media screen and (max-width: 1200px) {
    .run-wrapper {
      display: block;
    }

    .result-wrapper {
      height: 762px;
    }
  }
</style>
