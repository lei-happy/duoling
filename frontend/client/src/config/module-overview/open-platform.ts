import type { ModuleOverviewConfig } from './types';
import heroOpenPlatform from '@/assets/overview/hero-open-platform.svg';

/** 开放平台总览配置 */
const openPlatform: ModuleOverviewConfig = {
  key: 'open-platform',
  title: '开放平台',
  positioning:
    '把智途的数据与能力，安全地开放给你自己的系统和 AI 办公工具使用——系统对接走 API 密钥，AI 工具走 MCP 连接，全程可授权、可审计、可随时停用。',
  description:
    '你不需要懂技术：为每个要对接的系统或 AI 工具建一个应用，按需勾选可用能力，生成密钥或 MCP 配置后交付使用。敏感字段自动打码，所有调用都记录在案。',
  heroIllustration: heroOpenPlatform,
  accentColor: '#3b5bdb',
  workflow: [
    {
      title: '创建接入应用',
      desc: '为每个系统或 AI 工具建一个应用，便于分开管理与停用',
      icon: 'box',
      path: '/open-platform/apps'
    },
    {
      title: '按需授权能力',
      desc: '生成 API 密钥或 MCP 连接，勾选可访问的能力，最小授权',
      icon: 'shield',
      path: '/open-platform/apps'
    },
    {
      title: '复制配置去使用',
      desc: '系统对接交付密钥；AI 工具复制 MCP 配置即可连接',
      icon: 'settings',
      path: '/open-platform/docs'
    },
    {
      title: '查看调用记录',
      desc: '随时追溯每一次调用，异常可定位、可停用',
      icon: 'list',
      path: '/open-platform/logs'
    }
  ],
  moduleCards: [
    {
      path: '/open-platform/apps',
      icon: 'box',
      desc: '管理接入应用、API 密钥与 MCP 连接'
    },
    {
      path: '/open-platform/capabilities',
      icon: 'list',
      desc: '查看对外开放的能力清单与字段说明'
    },
    {
      path: '/open-platform/docs',
      icon: 'contract',
      desc: 'API 签名与 MCP 接入指南'
    },
    {
      path: '/open-platform/logs',
      icon: 'chart',
      desc: '调用明细与成功率、耗时统计'
    }
  ],
  quickActions: [
    { title: '接入应用', path: '/open-platform/apps', primary: true },
    { title: '接入指南', path: '/open-platform/docs' }
  ],
  tips: [
    '密钥/Token 只在创建时显示一次，请立即复制保存；遗失只能重置',
    '每把密钥只能访问你勾选的能力，敏感字段（如手机号）会自动打码',
    'MCP 连接改名不影响已配置的连接，可放心修改'
  ]
};

export default openPlatform;
