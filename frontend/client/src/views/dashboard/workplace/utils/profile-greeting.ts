import type { User } from '@/api/system/user/model';
import rawGreetings from '../data/profile-greetings.json';

const FALLBACK_GREETING = '你好，伙伴，愿你今天工作顺利、心情愉快。';

export interface ProfileGreetingSegment {
  id: string;
  matchHours?: number[];
  startHour?: number;
  endHour?: number;
  templates: string[];
}

interface ProfileGreetingsData {
  version: number;
  segments: ProfileGreetingSegment[];
}

const greetings = rawGreetings as ProfileGreetingsData;

/** 中国（上海）当前整点小时 0–23 */
export function getShanghaiHour(date: Date = new Date()): number {
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Shanghai',
    hour: 'numeric',
    hour12: false
  });
  const hourPart = formatter.formatToParts(date).find((p) => p.type === 'hour');
  let h = hourPart ? parseInt(hourPart.value, 10) : 0;
  if (Number.isNaN(h)) {
    h = 0;
  }
  if (h === 24) {
    h = 0;
  }
  return h;
}

function segmentMatchesHour(
  seg: ProfileGreetingSegment,
  hour: number
): boolean {
  if (seg.matchHours?.length) {
    return seg.matchHours.includes(hour);
  }
  if (seg.startHour != null && seg.endHour != null) {
    return hour >= seg.startHour && hour <= seg.endHour;
  }
  return false;
}

function findSegmentForHour(
  segments: ProfileGreetingSegment[],
  hour: number
): ProfileGreetingSegment | undefined {
  return segments.find((s) => segmentMatchesHour(s, hour));
}

function pickRandomTemplate(templates: string[]): string {
  if (!templates.length) {
    return FALLBACK_GREETING;
  }
  const i = Math.floor(Math.random() * templates.length);
  return templates[i] ?? FALLBACK_GREETING;
}

/** 展示名：昵称优先，否则手机号，否则「伙伴」 */
export function resolveGreetingDisplayName(
  info: User | null | undefined
): string {
  const nick = info?.nickname?.trim();
  if (nick) {
    return nick;
  }
  const phone = info?.phone?.trim();
  if (phone) {
    return phone;
  }
  return '伙伴';
}

function stripNicknameFromTemplate(template: string): string {
  let text = template.replace(/\{nickname\}/g, '');
  text = text.replace(/^[，,、\s]+/, '');
  text = text.replace(/[，,、\s]+$/, '');
  text = text.replace(/，{2,}/g, '，');
  return text.trim();
}

export interface ProfileGreetingParts {
  displayName: string;
  message: string;
}

/** 问候语拆分为「用户名」与「祝福语」两段，便于两行展示 */
export function getProfileGreetingParts(
  info: User | null | undefined,
  date: Date = new Date()
): ProfileGreetingParts {
  const displayName = resolveGreetingDisplayName(info);
  const hour = getShanghaiHour(date);
  const seg = findSegmentForHour(greetings.segments, hour);
  const templates = seg?.templates;
  if (!templates?.length) {
    return {
      displayName,
      message: stripNicknameFromTemplate(FALLBACK_GREETING)
    };
  }
  const raw = pickRandomTemplate(templates);
  return {
    displayName,
    message: stripNicknameFromTemplate(raw)
  };
}

/** 根据上海当前时间与词库随机一条问候语 */
export function getProfileGreetingText(
  info: User | null | undefined,
  date: Date = new Date()
): string {
  const { displayName, message } = getProfileGreetingParts(info, date);
  if (!message) {
    return `你好，${displayName}`;
  }
  return `你好，${displayName}，${message}`;
}
