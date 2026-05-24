<template>
  <div class="not-found">
    <van-empty image="error" description="页面不存在">
      <van-button round type="primary" class="bottom-button" @click="$router.replace('/home')">
        返回工作台
      </van-button>
    </van-empty>
  </div>
</template>

<style lang="scss" scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.bottom-button {
  width: 160px;
}
</style>
