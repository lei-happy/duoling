import type { ModuleOverviewConfig } from './types';
import heroInsight from '@/assets/overview/hero-insight.svg';

/** 数据洞察总览配置 */
const insight: ModuleOverviewConfig = {
  key: 'insight',
  title: '数据洞察',
  positioning:
    '数据洞察汇聚运营、运力与财务数据，通过经营驾驶舱、运营看板、数据报表与智能预测，帮助管理者掌握全局并辅助决策。',
  description:
    '在这里从不同视角洞察经营：老板视角的驾驶舱、运营核心指标看板、多维数据报表，以及基于历史数据的业务趋势预测。',
  heroIllustration: heroInsight,
  accentColor: '#1098ad',
  moduleCards: [
    {
      path: '/insight/cockpit',
      icon: 'cockpit',
      desc: '老板视角的经营与利润总览'
    },
    {
      path: '/insight/overview',
      icon: 'board',
      desc: '运营核心指标看板'
    },
    {
      path: '/insight/report',
      icon: 'report',
      desc: '多维数据报表与分析'
    },
    {
      path: '/insight/prediction',
      icon: 'forecast',
      desc: '基于数据的业务趋势预测'
    }
  ],
  quickActions: [
    { title: '经营驾驶舱', path: '/insight/cockpit', primary: true },
    { title: '运营看板', path: '/insight/overview' }
  ],
  tips: [
    '数据依赖运营、计费与结算的完整录入，数据越全洞察越准',
    '经营驾驶舱适合管理层，运营看板适合日常盯盘'
  ]
};

export default insight;
