<template>
  <ele-card header="用于试卷批阅">
    <div style="margin-bottom: 12px">点击鼠标右键评分</div>
    <ele-viewer
      ref="viewerRef"
      src="https://cdn.eleadmin.com/20200610/pECunlF.jpg"
      :markers="paperMarkers"
      :image-style="{ filter: 'contrast(120%)' }"
      style="height: 560px; max-width: 900px"
      @contentContextmenu="handleContentContextmenu"
    >
      <template #markerItem="{ item }">
        <div v-if="item.isPanel" class="paper-score">
          <div class="paper-score-content">
            <template v-if="item.selected != null || item.selectedDecimal">
              <span>{{
                (item.selected ?? 0) + (item.selectedDecimal ? 0.5 : 0)
              }}</span>
              <span>分</span>
            </template>
          </div>
          <div
            :class="[
              'paper-score-panel',
              { 'is-top-left': item.placement === 'topLeft' },
              { 'is-top-right': item.placement === 'topRight' },
              { 'is-bottom-left': item.placement === 'bottomLeft' }
            ]"
            @contextmenu.stop.prevent=""
          >
            <div class="paper-score-panel-list">
              <div
                v-for="num in 11"
                :key="num"
                :class="[{ 'is-active': item.selected === num - 1 }]"
                @click="handleScoreClick(num - 1)"
              >
                {{ num - 1 }}
              </div>
            </div>
            <div class="paper-score-panel-list">
              <div
                :class="[{ 'is-active': item.selectedDecimal }]"
                @click="handleDecimalClick"
              >
                0.5
              </div>
            </div>
            <div class="paper-score-panel-footer">
              <el-button
                size="small"
                class="ele-btn-icon"
                @click="handleCancel"
              >
                取消
              </el-button>
              <el-button
                type="primary"
                size="small"
                class="ele-btn-icon"
                @click="handleSave"
              >
                确定
              </el-button>
            </div>
          </div>
        </div>
        <div v-else class="paper-score">
          <div class="paper-score-content">
            <span>{{ item.score }}</span>
            <span>分</span>
          </div>
          <el-icon
            @click="handleScoreDelete(item)"
            @contextmenu.stop.prevent=""
          >
            <CloseCircleFilled />
          </el-icon>
        </div>
      </template>
    </ele-viewer>
    <div style="margin-top: 12px">
      <el-button class="ele-btn-icon" @click="handleCallViewer('zoomIn')">
        放大
      </el-button>
      <el-button class="ele-btn-icon" @click="handleCallViewer('zoomOut')">
        缩小
      </el-button>
      <el-button class="ele-btn-icon" @click="handleCallViewer('rotateLeft')">
        向左旋转
      </el-button>
      <el-button class="ele-btn-icon" @click="handleCallViewer('rotateRight')">
        向右旋转
      </el-button>
      <el-button class="ele-btn-icon" @click="handleCallViewer('autoIntoView')">
        自适应缩放
      </el-button>
      <el-button class="ele-btn-icon" @click="handleCallViewer('reset')">
        重置
      </el-button>
    </div>
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { CloseCircleFilled } from '@/components/icons';

  interface ScoreItem {
    key?: number;
    x?: number;
    y?: number;
    fixed?: boolean;
    score?: number;
    isPanel?: boolean;
    selected?: number;
    selectedDecimal?: boolean;
    placement?: string;
  }

  /** 试卷批阅标记数据 */
  const paperMarkers = ref<ScoreItem[]>([
    { key: 1, x: 1080, y: 208, fixed: true, score: 6 },
    { key: 1, x: 1100, y: 980, fixed: true, score: 9 }
  ]);

  /** 删除分数 */
  const handleScoreDelete = (item: ScoreItem) => {
    const index = paperMarkers.value.indexOf(item);
    if (index !== -1) {
      paperMarkers.value.splice(index, 1);
    }
  };

  /** 打开评分面板 */
  const handleContentContextmenu = (e: MouseEvent) => {
    e.preventDefault();
    // 自动调整面板位置
    let placement: string | undefined = void 0;
    const rect = viewerRef.value?.$el?.getBoundingClientRect?.();
    if (rect) {
      let isLeft = false;
      let isTop = false;
      if (rect.right - e.clientX < 220) {
        isLeft = true;
      }
      if (rect.bottom - e.clientY < 168) {
        isTop = true;
      }
      if (isLeft || isTop) {
        if (isLeft && isTop) {
          placement = 'topLeft';
        } else if (isTop) {
          placement = 'topRight';
        } else {
          placement = 'bottomLeft';
        }
      }
    }
    // 在右键位置打开
    const x = e.offsetX;
    const y = e.offsetY;
    const item = paperMarkers.value.find((d) => d.isPanel);
    if (item) {
      item.x = x;
      item.y = y;
      item.selected = void 0;
      item.selectedDecimal = false;
      item.placement = placement;
      item.key = Date.now();
      return;
    }
    paperMarkers.value.push({
      key: Date.now(),
      x,
      y,
      fixed: true,
      isPanel: true,
      placement
    });
  };

  /** 分数选项点击事件 */
  const handleScoreClick = (num: number) => {
    const item = paperMarkers.value.find((d) => d.isPanel);
    if (item) {
      item.selected = item.selected === num ? void 0 : num;
      if (item.selected === 10 && item.selectedDecimal) {
        item.selectedDecimal = false;
      }
    }
  };

  /** 分数小数选项点击事件 */
  const handleDecimalClick = () => {
    const item = paperMarkers.value.find((d) => d.isPanel);
    if (item) {
      if (item.selected === 10) {
        item.selected = void 0;
      }
      item.selectedDecimal = !item.selectedDecimal;
    }
  };

  /** 关闭评分面板 */
  const handleCancel = () => {
    const index = paperMarkers.value.findIndex((d) => d.isPanel);
    if (index !== -1) {
      paperMarkers.value.splice(index, 1);
    }
  };

  /** 保存添加分数 */
  const handleSave = () => {
    const item = paperMarkers.value.find((d) => d.isPanel);
    if (item == null || (item.selected == null && !item.selectedDecimal)) {
      handleCancel();
      return;
    }
    const score = (item.selected ?? 0) + (item.selectedDecimal ? 0.5 : 0);
    paperMarkers.value.push({
      key: Date.now(),
      x: item.x,
      y: item.y,
      fixed: true,
      score
    });
    handleCancel();
  };

  /** 查看器组件 */
  const viewerRef = ref<any>(null);

  /** 调用查看器组件方法 */
  const handleCallViewer = (methodName: string) => {
    if (viewerRef.value) {
      viewerRef.value[methodName]();
    }
  };
</script>

<style lang="scss" scoped>
  .paper-score {
    width: 0;
    height: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    position: relative;

    & > .paper-score-content {
      flex-shrink: 0;
      width: 34px;
      height: 34px;
      line-height: 34px;
      border-radius: 50%;
      color: #fff;
      font-size: 14px;
      background: rgba(22, 119, 255, 0.68);
      white-space: nowrap;
      text-align: center;

      & > span + span {
        font-size: 12px;
        vertical-align: 1px;
      }
    }

    & > .el-icon {
      color: #ff4d4f;
      font-size: 16px;
      position: absolute;
      background: #fff;
      border-radius: 50%;
      top: -20px;
      right: -24px;
      pointer-events: auto;
      cursor: pointer;

      &:hover {
        color: #cc3e3f;
      }
    }
  }

  /* 评分板 */
  .paper-score-panel {
    width: 220px;
    padding: 10px;
    border-radius: 6px;
    background: var(--el-bg-color-overlay);
    box-shadow: var(--el-box-shadow-light);
    box-sizing: border-box;
    position: absolute;
    top: 20px;
    left: -18px;
    pointer-events: auto;
    cursor: default;

    &.is-bottom-left {
      left: auto;
      right: -18px;
    }

    &.is-top-right {
      top: auto;
      bottom: 20px;
    }

    &.is-top-left {
      top: auto;
      left: auto;
      right: -18px;
      bottom: 20px;
    }
  }

  .paper-score-panel-list {
    display: grid;
    gap: 6px;
    grid-template-columns: repeat(6, 1fr);
    margin-bottom: 10px;

    & > div {
      height: 22px;
      line-height: 22px;
      color: var(--el-text-color-primary);
      font-size: 12px;
      border-radius: 4px;
      border: 1px solid var(--el-border-color);
      transition: all 0.2s;
      text-align: center;
      cursor: pointer;

      &:hover {
        border-color: var(--el-color-primary);
      }

      &.is-active {
        color: #fff;
        background: var(--el-color-primary);
        border-color: var(--el-color-primary);
      }
    }
  }

  .paper-score-panel-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;

    & > .el-button + .el-button {
      margin-left: 8px;
    }
  }
</style>
