import type { ModuleOverviewConfig } from './types';
import heroEnterprise from '@/assets/overview/hero-enterprise.svg';

/** 企业配置总览配置 */
const enterprise: ModuleOverviewConfig = {
  key: 'enterprise',
  title: '企业配置',
  positioning:
    '企业配置管理组织架构、员工与角色权限、经营主体、基础数据与系统设置，是企业运行的基础配置与治理中心。',
  description:
    '在这里搭建企业运行底座：维护组织架构与员工账号，配置角色权限与审批流程，管理开票经营主体与基础数据，设置系统参数与偏好。',
  heroIllustration: heroEnterprise,
  accentColor: '#5f3dc4',
  moduleCards: [
    {
      path: '/enterprise/organization',
      icon: 'org',
      desc: '维护企业部门与组织架构'
    },
    {
      path: '/enterprise/user',
      icon: 'user',
      desc: '管理企业员工账号'
    },
    {
      path: '/enterprise/role',
      icon: 'role',
      desc: '配置角色与功能权限'
    },
    {
      path: '/enterprise/approval-config',
      icon: 'approval',
      desc: '配置审批流程'
    },
    {
      path: '/enterprise/business-entity',
      icon: 'entity',
      desc: '管理开票经营主体'
    },
    {
      path: '/enterprise/basic-data',
      icon: 'data',
      desc: '维护地区、品牌车型等基础数据'
    },
    {
      path: '/enterprise/config',
      icon: 'settings',
      desc: '系统参数与偏好设置'
    }
  ],
  quickActions: [
    { title: '员工管理', path: '/enterprise/user', primary: true },
    { title: '角色权限', path: '/enterprise/role' }
  ],
  tips: [
    '建议先搭建组织架构，再分配员工与角色权限',
    '经营主体用于开票，请确保信息真实完整'
  ]
};

export default enterprise;
