<template>
  <ele-card header="直播功能功能演示">
    <!-- 操作按钮 -->
    <div style="margin-bottom: 16px">
      <el-button type="primary" class="ele-btn-icon" @click="play">
        播放
      </el-button>
      <el-button type="primary" class="ele-btn-icon" @click="pause">
        暂停
      </el-button>
      <el-button type="primary" class="ele-btn-icon" @click="changeSrc">
        切换视频源
      </el-button>
    </div>
    <!-- 播放器 -->
    <ele-xg-player :config="config" @player="handlePlayer" />
  </ele-card>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import type Player from 'xgplayer';
  import HlsPlugin from 'xgplayer-hls';
  const url1 =
    'https://ali-m-l.cztv.com/channels/lantian/channel001/1080p.m3u8';
  const poster1 =
    'https://imgcache.qq.com/open_proj/proj_qcloud_v2/gateway/solution/general-video/css/img/scene/6.png';
  const url2 =
    'https://ali-m-l.cztv.com/channels/lantian/channel008/1080p.m3u8';
  const poster2 =
    'https://imgcache.qq.com/open_proj/proj_qcloud_v2/gateway/solution/general-video/css/img/scene/1.png';

  /** 视频播放器配置 */
  const config = ref({
    lang: 'zh-cn',
    fluid: true,
    // 视频地址
    url: url1,
    // 封面
    poster: poster1,
    // 开启画中画
    pip: true,
    // 默认音量
    volume: 1,
    // 自动播放
    autoplay: false,
    // 是否是直播
    isLive: true,
    // 移除进度条/时间/倍数播放插件
    ignores: ['progress', 'time', 'playbackrate'],
    // 插件
    plugins: [HlsPlugin],
    // 插件配置
    hls: {
      retryCount: 3, // 重试 3 次，默认值
      retryDelay: 1000, // 每次重试间隔 1 秒，默认值
      loadTimeout: 10000 // 请求超时时间为 10 秒，默认值
    }
  });

  /** 视频播放器实例 */
  let player: Player;

  /** 播放器渲染完成 */
  const handlePlayer = (e: Player) => {
    player = e;
  };

  /** 播放 */
  const play = () => {
    if (player && player.paused) {
      player.play();
    }
  };

  /** 暂停 */
  const pause = () => {
    if (player) {
      player.pause();
    }
  };

  /** 切换视频源 */
  const changeSrc = () => {
    config.value = {
      ...config.value,
      url: config.value.url == url1 ? url2 : url1,
      poster: config.value.url == url1 ? poster2 : poster1,
      autoplay: true
    };
  };
</script>
