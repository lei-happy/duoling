/**
 * 企业数智化水位快测 · 题库
 *
 * 计分口径与销售物料《企业数智化转型-管理者精读版》完全一致：
 * 四维各自归一化到 0–20，总分 0–80。完整 20 题深度自检仍以精读版为准，
 * 本页只做约 3 分钟的粗测。改题目和分值前先跟市场对齐，
 * 否则官网结论会和销售手上的结论对不上。
 */

export type DimKey = 'A' | 'B' | 'C' | 'D';

export interface Choice {
  value: string;
  label: string;
}

export interface Question {
  id: string;
  text: string;
  choices: Choice[];
}

export interface QuestionGroup {
  dim: DimKey;
  title: string;
  note: string;
  questions: Question[];
}

/** 计分题统一五档，0–4 分 */
export const CHOICES: Choice[] = [
  { value: '0', label: '几乎没有' },
  { value: '1', label: '偶尔做到' },
  { value: '2', label: '部分做到' },
  { value: '3', label: '多数做到' },
  { value: '4', label: '稳定做到' }
];

/** 开头三道画像题，不计分，只用于顾问判断你是谁、卡在哪 */
export const PROFILE: Question[] = [
  {
    id: 'P1',
    text: '自有板车大概多少台？',
    choices: [
      { value: 'lt10', label: '10 台以内' },
      { value: '10-30', label: '10–30 台' },
      { value: '30-100', label: '30–100 台' },
      { value: 'gt100', label: '100 台以上' }
    ]
  },
  {
    id: 'P2',
    text: '现在主要靠什么管日常业务？',
    choices: [
      { value: 'excel', label: 'Excel 和微信' },
      { value: 'bypass', label: '有系统，但一线常绕路' },
      { value: 'online', label: '系统已是主流程' }
    ]
  },
  {
    id: 'P3',
    text: '当前最想先解决哪一块？',
    choices: [
      { value: 'plan', label: '计划调度' },
      { value: 'receipt', label: '回单在途' },
      { value: 'recon', label: '对账结算' },
      { value: 'cost', label: '成本利润' },
      { value: 'energy', label: '能源加油' }
    ]
  }
];

export const GROUPS: QuestionGroup[] = [
  {
    dim: 'A',
    title: '业务在线',
    note: '单据和现场作业是否真的在系统里跑',
    questions: [
      {
        id: 'A1',
        text: '运输计划、任务单、回单、运费这些核心单据，是不是都在系统里流转，而不是靠 Excel 台账加微信群转发？',
        choices: CHOICES
      },
      {
        id: 'A2',
        text: '派车、装车、到货、签收这些节点，系统里有没有时间和责任人，出了纠纷能直接倒查？',
        choices: CHOICES
      },
      {
        id: 'A3',
        text: '司机是不是在现场用手机交回单、报异常，而不是跑完一圈回场后由内勤统一补录？',
        choices: CHOICES
      }
    ]
  },
  {
    dim: 'B',
    title: '数据贯通',
    note: '数据能不能算出利润、改变决策',
    questions: [
      {
        id: 'B1',
        text: '客户、车辆、线路、运价这些基础档案是不是只有一套，业务、调度、财务算出来的数能对上？',
        choices: CHOICES
      },
      {
        id: 'B2',
        text: '一趟运输的收入和成本（运费、油或能源、路桥、外协、人工）能不能自动归到单车和单线路，而不是月底人工拉表拼？',
        choices: CHOICES
      },
      {
        id: 'B3',
        text: '调报价、停亏损线路、换承运商这类决定，是不是先看系统里的数据再拍板？',
        choices: CHOICES
      }
    ]
  },
  {
    dim: 'C',
    title: '智能应用',
    note: '系统会不会主动提醒和给建议',
    questions: [
      {
        id: 'C1',
        text: '配载组合、证照到期、运费异常这些事，系统会不会主动给建议或预警，并且能直接变成调度或财务的下一步动作？',
        choices: CHOICES
      },
      {
        id: 'C2',
        text: '这些建议进了真实流程之后，有没有人回头核对：采纳了多少、省了多少、错了怎么改？',
        choices: CHOICES
      }
    ]
  },
  {
    dim: 'D',
    title: '经营闭环',
    note: '发现问题后有没有人管到底',
    questions: [
      {
        id: 'D1',
        text: '发现亏损线路或异常单据之后，是不是会派到具体的人、限时处理，并且回看处理结果？',
        choices: CHOICES
      },
      {
        id: 'D2',
        text: '每月是不是用经营结果复盘运价和成本政策，并把结论改回系统里的规则？',
        choices: CHOICES
      }
    ]
  }
];

export const DIM_NAME: Record<DimKey, string> = {
  A: '业务在线',
  B: '数据贯通',
  C: '智能应用',
  D: '经营闭环'
};

export const DIM_ORDER: DimKey[] = ['A', 'B', 'C', 'D'];

/** 全部计分题 ID，按维度顺序排列 */
export const QUESTION_IDS: string[] = GROUPS.flatMap((g) =>
  g.questions.map((q) => q.id)
);
