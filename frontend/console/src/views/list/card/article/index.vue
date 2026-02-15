<template>
  <ele-page>
    <top-search />
    <ele-card :body-style="{ padding: '16px 8px' }">
      <div class="article-list">
        <div v-for="item in data" :key="item.id" class="list-item">
          <div class="list-item-body">
            <div style="flex: 1">
              <ele-text size="md">{{ item.title }}</ele-text>
              <div style="margin-top: 8px; display: flex; align-items: center">
                <el-tag
                  v-for="tag in item.tags"
                  :key="tag"
                  type="info"
                  size="small"
                  :disable-transitions="true"
                  style="margin-right: 8px"
                >
                  {{ tag }}
                </el-tag>
              </div>
              <div style="margin-top: 16px">{{ item.content }}</div>
              <div style="margin-top: 16px; display: flex; align-items: center">
                <el-avatar :src="item.avatar" :size="24" />
                <ele-text type="secondary" style="flex: 1; padding-left: 6px">
                  {{ item.user }} 发表于 {{ item.time }}
                </ele-text>
              </div>
              <div style="margin-top: 16px; display: flex; align-items: center">
                <ele-text
                  :icon="Star"
                  type="placeholder"
                  style="cursor: pointer"
                >
                  &nbsp;{{ item.likes }}
                </ele-text>
                <el-divider direction="vertical" style="margin: 0 14px" />
                <ele-text
                  :icon="CollectionTag"
                  type="placeholder"
                  style="cursor: pointer"
                >
                  &nbsp;{{ item.favorites }}
                </ele-text>
                <el-divider direction="vertical" style="margin: 0 14px" />
                <ele-text
                  :icon="ChatLineSquare"
                  type="placeholder"
                  style="cursor: pointer"
                >
                  &nbsp;{{ item.comments }}
                </ele-text>
              </div>
            </div>
            <div class="list-item-extra">
              <img-grid :images="item.covers" @preview="openPreview" />
            </div>
          </div>
          <el-divider style="margin: 0; opacity: 0.6" />
        </div>
      </div>
      <div style="margin-top: 16px; text-align: center">
        <el-button v-if="page !== 1" :loading="loading" @click="query">
          {{ loading ? '加载中..' : '加载更多' }}
        </el-button>
      </div>
      <ele-image-viewer
        v-model="showImageViewer"
        :urlList="viewerImages"
        :initialIndex="viewerIndex"
        :infinite="false"
      />
    </ele-card>
  </ele-page>
</template>

<script lang="ts" setup>
  import { ref } from 'vue';
  import { Star, CollectionTag, ChatLineSquare } from '@element-plus/icons-vue';
  import { random } from 'ele-admin-plus';
  import TopSearch from '../project/components/top-search.vue';
  import ImgGrid from './components/img-grid.vue';

  defineOptions({ name: 'ListCardArticle' });

  interface Item {
    id: number;
    title: string;
    content: string;
    time: string;
    covers: string[];
    tags: string[];
    user: string;
    avatar: string;
    favorites: number;
    likes: number;
    comments: number;
  }

  /** 请求状态 */
  const loading = ref(false);

  /** 列表数据 */
  const data = ref<Item[]>([]);

  /** 当前页码 */
  const page = ref(2);

  /** 是否打开图片预览 */
  const showImageViewer = ref(false);

  /** 图片预览数据 */
  const viewerImages = ref<string[]>([]);

  /** 图片预览初始位置 */
  const viewerIndex = ref(0);

  /** 加载下一页 */
  const query = () => {
    loading.value = true;
    setTimeout(() => {
      loading.value = false;
      page.value++;
      data.value = data.value.concat(
        data.value.slice(0, 3).map((d, i) => {
          return {
            ...d,
            id: data.value.length + i + 1,
            covers: randomCovers()
          };
        })
      );
    }, 1000);
  };

  /** 打开图片预览 */
  const openPreview = (images: string[], index: number) => {
    viewerImages.value = images;
    viewerIndex.value = index;
    showImageViewer.value = true;
  };

  const randomCovers = () => {
    const urls = [
      'https://cdn.eleadmin.com/20200610/RZ8FQmZfHkcffMlTBCJllBFjEhEsObVo.jpg',
      'https://cdn.eleadmin.com/20200610/WLXm7gp1EbLDtvVQgkeQeyq5OtDm00Jd.jpg',
      'https://cdn.eleadmin.com/20200610/4Z0QR2L0J1XStxBh99jVJ8qLfsGsOgjU.jpg',
      'https://cdn.eleadmin.com/20200610/ttkIjNPlVDuv4lUTvRX8GIlM2QqSe0jg.jpg',
      'https://cdn.eleadmin.com/20200610/fAenQ8nvRjL7x0i0jEfuDBZHvJfHf3v6.jpg',
      'https://cdn.eleadmin.com/20200610/LrCTN2j94lo9N7wEql7cBr1Ux4rHMvmZ.jpg',
      'https://cdn.eleadmin.com/20200610/yeKvhT20lMU0f1T3Y743UlGEOLLnZSnp.jpg',
      'https://cdn.eleadmin.com/20200610/CyrCNmTJfv7D6GFAg39bjT3eRkkRm5dI.jpg',
      'https://cdn.eleadmin.com/20200609/0568caaf0a7e41dda2d901d4ac2f3243.jpg',
      'https://cdn.eleadmin.com/20200609/0bfaa58e801b47fb9f56dcb128206d94.jpg',
      'https://cdn.eleadmin.com/20200609/12b3d575a2a24e0789a014bd6ce7585b.jpg',
      'https://cdn.eleadmin.com/20200609/21222950dc174485b2ec5088435a46a3.jpg',
      'https://cdn.eleadmin.com/20200609/2d98970a51b34b6b859339c96b240dcd.jpg',
      'https://cdn.eleadmin.com/20200609/3cc0f65fefbe448191aa728d80f6b97e.jpg',
      'https://cdn.eleadmin.com/20200609/41d81834e87546f49d3ff48c3806ea92.jpg',
      'https://cdn.eleadmin.com/20200609/4e60a84551fa48439bf42ecdb9673331.jpg',
      'https://cdn.eleadmin.com/20200609/66e6f6c60cfa44b288d6343027b544d0.jpg',
      'https://cdn.eleadmin.com/20200609/8931360b593040238d894a542c9037bc.jpg',
      'https://cdn.eleadmin.com/20200609/948344a2a77c47a7a7b332fe12ff749a.jpg',
      'https://cdn.eleadmin.com/20200609/adb3ad5e05614fd2a59cf886ffc37f74.jpg',
      'https://cdn.eleadmin.com/20200609/b3ce64e10db7497b8b9f5a31df1b4eb2.jpg',
      'https://cdn.eleadmin.com/20200609/b6a811873e704db49db994053a5019b2.jpg',
      'https://cdn.eleadmin.com/20200609/be7dc0c24fc342fda44e12a2c2a2b7bb.jpg',
      'https://cdn.eleadmin.com/20200609/c184eef391ae48dba87e3057e70238fb.jpg',
      'https://cdn.eleadmin.com/20200609/d3519518b00d42d3936b2ab5ce3a4cc3.jpg',
      'https://cdn.eleadmin.com/20200609/d6442cfa99b64b51aabfc470055b05dc.jpg',
      'https://cdn.eleadmin.com/20200609/e36594e7423147748b2592ccb720ae9e.jpg',
      'https://cdn.eleadmin.com/20200609/f6bc05af944a4f738b54128717952107.jpg',
      'https://cdn.eleadmin.com/20200609/faa0202700ee455b90fe77d8bef98bc0.jpg',
      'https://cdn.eleadmin.com/20200609/fe9196dd091e438fba115205c1003ee7.jpg'
    ];
    const covers: string[] = [];
    for (let i = 0; i < 6; i++) {
      const index = random(0, urls.length);
      const url = urls[index];
      urls.splice(index, 1);
      covers.push(url);
    }
    return covers;
  };

  data.value = [
    {
      id: 1,
      title: 'ElementUI',
      content:
        'Element, 一套为开发者、设计师和产品经理准备的基于 Vue 2.0 的组件库, 提供了配套设计资源, 帮助你的网站快速成型。',
      time: '2 小时前',
      covers: randomCovers(),
      tags: ['EleAdminPro', 'UI框架', '设计语言'],
      user: 'SunSmile',
      avatar:
        'https://cdn.eleadmin.com/20200609/c184eef391ae48dba87e3057e70238fb.jpg',
      favorites: 104,
      likes: 189,
      comments: 15
    },
    {
      id: 2,
      title: 'Vue.js',
      content:
        'Vue 是一套用于构建用户界面的渐进式框架。与其它大型框架不同的是, Vue 被设计为可以自底向上逐层应用。',
      time: '4 小时前',
      covers: randomCovers(),
      tags: ['EleAdminPro', 'UI框架', '设计语言'],
      user: '你的名字很好听',
      avatar:
        'https://cdn.eleadmin.com/20200609/b6a811873e704db49db994053a5019b2.jpg',
      favorites: 104,
      likes: 189,
      comments: 15
    },
    {
      id: 3,
      title: 'Vuex',
      content:
        'Vuex 是一个专为 Vue.js 应用程序开发的状态管理模式。它采用集中式存储管理应用的所有组件的状态, 并以相应的规则保证状态以一种可预测的方式发生变化。',
      time: '12 小时前',
      covers: randomCovers(),
      tags: ['EleAdminPro', 'UI框架', '设计语言'],
      user: '全村人的希望',
      avatar:
        'https://cdn.eleadmin.com/20200609/948344a2a77c47a7a7b332fe12ff749a.jpg',
      favorites: 104,
      likes: 189,
      comments: 15
    },
    {
      id: 4,
      title: 'Vue Router',
      content:
        'Vue Router 是 Vue.js 官方的路由管理器。它和 Vue.js 的核心深度集成, 让构建单页面应用变得易如反掌。',
      time: '14 小时前',
      covers: randomCovers(),
      tags: ['EleAdminPro', 'UI框架', '设计语言'],
      user: 'Jasmine',
      avatar:
        'https://cdn.eleadmin.com/20200609/f6bc05af944a4f738b54128717952107.jpg',
      favorites: 104,
      likes: 189,
      comments: 15
    },
    {
      id: 5,
      title: 'Sass',
      content: 'Sass 是世界上最成熟、稳定、强大的专业级 CSS 扩展语言。',
      time: '10 小时前',
      covers: randomCovers(),
      tags: ['EleAdminPro', 'UI框架', '设计语言'],
      user: '酷酷的大叔',
      avatar:
        'https://cdn.eleadmin.com/20200609/2d98970a51b34b6b859339c96b240dcd.jpg',
      favorites: 104,
      likes: 189,
      comments: 15
    },
    {
      id: 6,
      title: 'Axios',
      content:
        'Axios 是一个基于 promise 的 HTTP 库, 可以用在浏览器和 node.js 中。',
      time: '16 小时前',
      covers: randomCovers(),
      tags: ['EleAdminPro', 'UI框架', '设计语言'],
      user: 'SunSmile',
      avatar:
        'https://cdn.eleadmin.com/20200609/c184eef391ae48dba87e3057e70238fb.jpg',
      favorites: 104,
      likes: 189,
      comments: 15
    },
    {
      id: 7,
      title: 'Webpack',
      content:
        'webpack 是一个模块打包器。webpack 的主要目标是将 JavaScript 文件打包在一起, 打包后的文件用于在浏览器中使用。',
      time: '6 小时前',
      covers: randomCovers(),
      tags: ['EleAdminPro', 'UI框架', '设计语言'],
      user: '全村人的希望',
      avatar:
        'https://cdn.eleadmin.com/20200609/948344a2a77c47a7a7b332fe12ff749a.jpg',
      favorites: 104,
      likes: 189,
      comments: 15
    },
    {
      id: 8,
      title: 'Node.js',
      content:
        'Node.js 是一个基于 Chrome V8 引擎的 JavaScript 运行环境。Node.js 使用了一个事件驱动、非阻塞式 I/O 的模型, 使其轻量又高效。',
      time: '8 小时前',
      covers: randomCovers(),
      tags: ['EleAdminPro', 'UI框架', '设计语言'],
      user: 'Jasmine',
      avatar:
        'https://cdn.eleadmin.com/20200609/f6bc05af944a4f738b54128717952107.jpg',
      favorites: 104,
      likes: 189,
      comments: 15
    }
  ];
</script>

<style lang="scss" scoped>
  .list-item-body {
    display: flex;
    padding: 16px 24px;
  }

  .list-item-extra {
    width: 280px;
    height: 175px;
    margin-left: 12px;

    :deep(.el-image) {
      height: calc((175px - 2px - 4px - 3px) / 2) !important;
    }
  }

  @media screen and (max-width: 880px) {
    .list-item-extra {
      width: 200px;
      height: 125px;

      :deep(.el-image) {
        height: calc((125px - 2px - 4px - 3px) / 2) !important;
      }
    }
  }

  @media screen and (max-width: 576px) {
    .list-item-body {
      display: block;
    }

    .list-item-extra {
      width: 100%;
      height: 200px;
      margin: 16px 0 0 0;

      :deep(.el-image) {
        height: calc((200px - 2px - 4px - 3px) / 2) !important;
      }
    }
  }
</style>
