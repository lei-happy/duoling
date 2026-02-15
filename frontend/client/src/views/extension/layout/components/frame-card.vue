<template>
  <div class="frame-wrapper">
    <div class="frame-header">
      <div class="frame-tool"></div>
      <div class="frame-tool is-warning"></div>
      <div class="frame-tool is-success"></div>
      <div></div>
    </div>
    <div class="frame-body">
      <slot></slot>
    </div>
  </div>
</template>

<style lang="scss" scoped>
  .frame-wrapper {
    max-width: 920px;
    margin: 0 auto;
  }

  .frame-header {
    display: flex;
    align-items: center;
    height: 26px;
    padding: 0 16px;
    background: #3c3c3c;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
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

  .frame-body {
    border-left: 6px solid #3c3c3c;
    border-right: 6px solid #3c3c3c;
    border-bottom: 6px solid #3c3c3c;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
    overflow: auto;
  }
</style>
