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

function applyNickname(template: string, displayName: string): string {
  return template.replaceAll('{nickname}', displayName);
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

/** 根据上海当前时间与词库随机一条问候语 */
export function getProfileGreetingText(
  info: User | null | undefined,
  date: Date = new Date()
): string {
  const hour = getShanghaiHour(date);
  const seg = findSegmentForHour(greetings.segments, hour);
  const templates = seg?.templates;
  if (!templates?.length) {
    return applyNickname(FALLBACK_GREETING, resolveGreetingDisplayName(info));
  }
  const raw = pickRandomTemplate(templates);
  return applyNickname(raw, resolveGreetingDisplayName(info));
}
