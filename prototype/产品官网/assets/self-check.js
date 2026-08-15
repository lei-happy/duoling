/* 朵灵·企云官网 · 企业数智化水位快测（3 道画像 + 10 题计分）
   计分口径与销售物料《管理者精读版》完全一致：
   - 四维各自归一化到 0–20，总分 0–80
   - 先按总分落档（L1–L8），再按短板维度封顶，L8 额外要求四维均 ≥14
   完整 20 题深度自检仍以精读版为准，本页只做约 3 分钟粗测。 */

(function () {
  'use strict';

  const root = document.querySelector('[data-self-check]');
  if (!root) return;

  /* ---------------- 题库：四维共 10 题，全部写成企业日常语言 ---------------- */

  const CHOICES = [
    { v: 0, label: '几乎没有' },
    { v: 1, label: '偶尔做到' },
    { v: 2, label: '部分做到' },
    { v: 3, label: '多数做到' },
    { v: 4, label: '稳定做到' }
  ];

  const PROFILE = [
    {
      id: 'P1',
      text: '自有板车大概多少台？',
      choices: [
        { v: 'lt10', label: '10 台以内' },
        { v: '10-30', label: '10–30 台' },
        { v: '30-100', label: '30–100 台' },
        { v: 'gt100', label: '100 台以上' }
      ]
    },
    {
      id: 'P2',
      text: '现在主要靠什么管日常业务？',
      choices: [
        { v: 'excel', label: 'Excel 和微信' },
        { v: 'bypass', label: '有系统，但一线常绕路' },
        { v: 'online', label: '系统已是主流程' }
      ]
    },
    {
      id: 'P3',
      text: '当前最想先解决哪一块？',
      choices: [
        { v: 'plan', label: '计划调度' },
        { v: 'receipt', label: '回单在途' },
        { v: 'recon', label: '对账结算' },
        { v: 'cost', label: '成本利润' },
        { v: 'energy', label: '能源加油' }
      ]
    }
  ];

  const GROUPS = [
    {
      dim: 'A',
      title: '业务在线',
      note: '单据和现场作业是否真的在系统里跑',
      questions: [
        {
          id: 'A1',
          text: '运输计划、任务单、回单、运费这些核心单据，是不是都在系统里流转，而不是靠 Excel 台账加微信群转发？'
        },
        {
          id: 'A2',
          text: '派车、装车、到货、签收这些节点，系统里有没有时间和责任人，出了纠纷能直接倒查？'
        },
        {
          id: 'A3',
          text: '司机是不是在现场用手机交回单、报异常，而不是跑完一圈回场后由内勤统一补录？'
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
          text: '客户、车辆、线路、运价这些基础档案是不是只有一套，业务、调度、财务算出来的数能对上？'
        },
        {
          id: 'B2',
          text: '一趟运输的收入和成本（运费、油或能源、路桥、外协、人工）能不能自动归到单车和单线路，而不是月底人工拉表拼？'
        },
        {
          id: 'B3',
          text: '调报价、停亏损线路、换承运商这类决定，是不是先看系统里的数据再拍板？'
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
          text: '配载组合、证照到期、运费异常这些事，系统会不会主动给建议或预警，并且能直接变成调度或财务的下一步动作？'
        },
        {
          id: 'C2',
          text: '这些建议进了真实流程之后，有没有人回头核对：采纳了多少、省了多少、错了怎么改？'
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
          text: '发现亏损线路或异常单据之后，是不是会派到具体的人、限时处理，并且回看处理结果？'
        },
        {
          id: 'D2',
          text: '每月是不是用经营结果复盘运价和成本政策，并把结论改回系统里的规则？'
        }
      ]
    }
  ];

  const DIM_NAME = { A: '业务在线', B: '数据贯通', C: '智能应用', D: '经营闭环' };
  const DIM_ORDER = ['A', 'B', 'C', 'D'];

  /* 各维题数不同，统一折算到 20 分制，保证与 20 题版落档一致 */
  const DIM_FACTOR = { A: 20 / 12, B: 20 / 12, C: 20 / 8, D: 20 / 8 };

  const QUESTION_IDS = GROUPS.reduce(
    (acc, group) => acc.concat(group.questions.map((q) => q.id)),
    []
  );

  /* ---------------- 八个档位：画像 + 版本落点 + 先做三件事 ---------------- */

  const STAGE_ORDER = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8'];

  const STAGE = {
    s1: {
      band: 'L1',
      name: '信息化起步期',
      short: '在线起步',
      tier: 1,
      desc: '企业的真相还在 Excel 和微信群里。这个阶段先别谈 AI，把计划、派车、回单在线上跑通，比买任何模型都值钱。',
      plan: '基础版',
      planWhy: '先把核心单据在线化，投入最小、见效最快',
      moves: [
        '计划中心在线建单，客户的运输需求不再散落在微信和邮件里',
        '司机用手机接任务、拍回单，装车到签收全程留时间和责任人',
        '组织、角色、审批一次配好，谁能改运费、谁能确认到货都说得清'
      ]
    },
    s2: {
      band: 'L2',
      name: '信息化夯实期',
      short: '在线夯实',
      tier: 1,
      desc: '系统有了，但一线还在绕路：线下派完车再补录、回单靠拍照发群。先把系统外的动作压掉，底座才算稳。',
      plan: '基础版',
      planWhy: '重点是让一线愿意用，而不是加更多模块',
      moves: [
        '配载建单加调度工作台，把打电话派车这一步搬进系统',
        '回单签收在线闭环，回单齐不齐一眼看得见，不再翻群聊',
        '操作记录与审批留痕，改单、改运费都有人负责'
      ]
    },
    s3: {
      band: 'L3',
      name: '数字化起步期',
      short: '数据起步',
      tier: 2,
      desc: '业务在线了，但数还是各算各的：调度的车数、财务的运费、老板的利润，三张表对不上。下一步是统一口径。',
      plan: '基础版',
      planWhy: '先把主数据和运价合同收口，为算利润打底',
      moves: [
        '客户、车辆、线路、经销商门店统一建档，全公司只认一套档案',
        '运价合同和路线在线管理，报价按合同自动取价，不再凭记忆',
        '应付管理与费用单台账，外协运费该给多少、给没给，账上清楚'
      ]
    },
    s4: {
      band: 'L4',
      name: '数字化推进期',
      short: '数据推进',
      tier: 2,
      desc: '数据开始影响决策了，但还停在事后看。把成本自动算到每台车、每条线，经营会议才能从拍脑袋变成看数。',
      plan: '基础版起步，按需加旗舰版',
      planWhy: '利润核算与对账用基础版可跑，深度分析在旗舰版',
      moves: [
        '成本政策自动归集油费、路桥、外协、人工，单车利润按趟结算',
        '对账中心把客户对账和承运商结算并到一处，月底不再拉表拼',
        '经营驾驶舱利润总览，哪条线亏、哪个客户报价低，进门就看见'
      ]
    },
    s5: {
      band: 'L5',
      name: '智能化试点期',
      short: '智能试点',
      tier: 3,
      desc: '底座和数据都够用了，可以让机器开始干活。选一两件高频又费人的事先试，别一上来铺满全公司。',
      plan: '旗舰版',
      planWhy: 'AI 数字员工与智能配载是旗舰版能力',
      moves: [
        'AI 录单员读客户的 Excel 和运单照片，直接生成运输计划',
        '智能配载按车型、板位、线路推荐组合，空板位先降下来',
        '证照到期与异常运费自动预警，不再靠车队长记在本子上'
      ]
    },
    s6: {
      band: 'L6',
      name: '智能化扩展期',
      short: '智能扩展',
      tier: 3,
      desc: '单点智能跑通了，接下来是让它进入更多岗位，并且能被考核：采纳了多少、省了多少、错了怎么纠。',
      plan: '旗舰版',
      planWhy: '数据分析员、运营看板与运费引擎都在旗舰版',
      moves: [
        'AI 数据分析员上线，老板一句话问出上月利润和线路排名',
        '运营看板与数据报表覆盖调度、财务、车队长三个岗位',
        '承运商运费引擎自动算外协费用，减少人工核对与扯皮'
      ]
    },
    s7: {
      band: 'L7',
      name: '数智化成型期',
      short: '数智成型',
      tier: 4,
      desc: '数据和智能已经进了部分经营动作，还差最后一段：预警要变成任务，任务要有结果，结果要改回规则。',
      plan: '旗舰版',
      planWhy: '预测、闭环任务与生态撮合是旗舰版组合拳',
      moves: [
        '智能预测接进计划与运力筹备，旺季前先知道缺多少车',
        '预警自动派到审批与待办，异常有人领、有时限、有回看',
        '货源大厅与运力大厅补缺口，旺季不缺车，淡季不缺货'
      ]
    },
    s8: {
      band: 'L8',
      name: '数智化闭环期',
      short: '数智闭环',
      tier: 4,
      desc: '四个维度都比较均衡，闭环已经跑起来了。接下来是把这套机制复制到更多业务和更多经营主体上。',
      plan: '旗舰版',
      planWhy: '开放平台与多主体管理需要旗舰版承载',
      moves: [
        '开放平台对接主机厂 DMS 与客户系统，运输指令自动进单',
        '生态撮合扩容，把稳定合作的承运商沉淀成自己的可控运力池',
        '多经营主体与数据权限精细化，扩张时管理半径不失控'
      ]
    }
  };

  const ACTIONS_BY_WEAK = {
    A: [
      '盘一遍还在系统外跑的活：Excel 台账、微信群派车、口头改单，列清单逐条收回系统',
      '挑一条主力线路，把计划到回单跑成完整在线闭环，关键节点必须留时间和责任人',
      '给司机和车队长配好手机端，现场就能交回单、报异常，取消事后集中补录'
    ],
    B: [
      '先统一一套经营口径：车次、公里、运费、成本各自怎么算，业务财务先对齐',
      '打通一条数据链，让一趟运输的收入和成本自动落到单车和单线路上',
      '经营会议改成先看数再讨论，看完当场定动作和责任人'
    ],
    C: [
      '按价值高、数据够、能验证，挑 1–2 个场景先做，比如智能配载或运单识别录入',
      '给试点定好验收标准：省多少人工、采纳率多少、多久回看一次',
      '把智能结果接到实际动作上，并留一条纠错通道，错了能反馈能改'
    ],
    D: [
      '把看板和预警接到人：异常出现后自动派单、限时处理、结果回看',
      '写清楚哪些事机器定、哪些事必须人拍板、多大金额要升级到老板',
      '每月固定一次复盘，把结论改回运价、成本政策和系统规则里'
    ]
  };

  /* ---------------- 计分与判档（与精读版同一套函数） ---------------- */

  function stageByTotal(total) {
    if (total <= 18) return 's1';
    if (total <= 28) return 's2';
    if (total <= 38) return 's3';
    if (total <= 48) return 's4';
    if (total <= 56) return 's5';
    if (total <= 64) return 's6';
    if (total <= 72) return 's7';
    return 's8';
  }

  function capStage(current, maxAllowed) {
    return STAGE_ORDER.indexOf(current) > STAGE_ORDER.indexOf(maxAllowed)
      ? maxAllowed
      : current;
  }

  function judgeStage(dims, total, complete) {
    let key = stageByTotal(total);
    if (!complete) return key;

    const { A, B, C, D } = dims;

    if (A <= 6) key = capStage(key, 's1');
    else if (A <= 10) key = capStage(key, 's2');
    else if (A <= 12) key = capStage(key, 's3');

    if (B <= 8) key = capStage(key, 's3');
    else if (B <= 11) key = capStage(key, 's4');

    if (C <= 8) key = capStage(key, 's5');
    else if (C <= 12) key = capStage(key, 's6');

    if (D <= 10) key = capStage(key, 's6');
    else if (D <= 13) key = capStage(key, 's7');

    if (key === 's8' && (A < 14 || B < 14 || C < 14 || D < 14)) key = 's7';

    return key;
  }

  function weakestDim(dims) {
    let weak = 'A';
    let min = Infinity;
    DIM_ORDER.forEach((d) => {
      if (dims[d] < min) {
        min = dims[d];
        weak = d;
      }
    });
    return weak;
  }

  function readScores(form) {
    const raw = { A: 0, B: 0, C: 0, D: 0 };
    const missing = [];
    let answered = 0;

    QUESTION_IDS.forEach((id) => {
      const checked = form.querySelector('input[name="' + id + '"]:checked');
      if (!checked) {
        missing.push(id);
        return;
      }
      answered += 1;
      raw[id.charAt(0)] += Number(checked.value);
    });

    const dims = {};
    DIM_ORDER.forEach((d) => {
      dims[d] = Math.round(raw[d] * DIM_FACTOR[d]);
    });

    const total = DIM_ORDER.reduce((sum, d) => sum + dims[d], 0);

    return { dims, total, answered, missing, complete: missing.length === 0 };
  }

  /* ---------------- 渲染题目 ---------------- */

  const form = root.querySelector('[data-check-form]');
  const listHost = root.querySelector('[data-check-list]');

  const profileHtml =
    '<section class="q-group">' +
    '<header class="q-group-head">' +
    '<span class="tag tag-brand">画像 · 不计分</span>' +
    '<p class="muted">先告诉顾问你是谁、卡在哪，后面 10 题才用来量水位</p>' +
    '</header>' +
    '<ul class="q-list">' +
    PROFILE.map((q, i) => {
      const no = String(i + 1).padStart(2, '0');
      const choices = q.choices
        .map(
          (c) =>
            '<label class="ch">' +
            '<input type="radio" name="' +
            q.id +
            '" value="' +
            c.v +
            '" />' +
            '<span class="ch-box">' +
            c.label +
            '</span>' +
            '</label>'
        )
        .join('');
      return (
        '<li class="q" data-q="' +
        q.id +
        '">' +
        '<div class="q-head"><span class="q-no num">' +
        no +
        '</span><p class="q-text">' +
        q.text +
        '</p></div>' +
        '<div class="q-choices" data-cols="' +
        q.choices.length +
        '" role="radiogroup" aria-label="画像第 ' +
        no +
        ' 题">' +
        choices +
        '</div>' +
        '</li>'
      );
    }).join('') +
    '</ul></section>';

  let index = 3;
  listHost.innerHTML = profileHtml + GROUPS.map((group) => {
    const items = group.questions
      .map((q) => {
        index += 1;
        const no = String(index).padStart(2, '0');
        const choices = CHOICES.map(
          (c) =>
            '<label class="ch">' +
            '<input type="radio" name="' +
            q.id +
            '" value="' +
            c.v +
            '" />' +
            '<span class="ch-box"><b class="num">' +
            c.v +
            '</b>' +
            c.label +
            '</span>' +
            '</label>'
        ).join('');

        return (
          '<li class="q" data-q="' +
          q.id +
          '">' +
          '<div class="q-head"><span class="q-no num">' +
          no +
          '</span><p class="q-text">' +
          q.text +
          '</p></div>' +
          '<div class="q-choices" role="radiogroup" aria-label="第 ' +
          no +
          ' 题作答">' +
          choices +
          '</div>' +
          '</li>'
        );
      })
      .join('');

    return (
      '<section class="q-group">' +
      '<header class="q-group-head">' +
      '<span class="tag tag-brand">' +
      group.dim +
      ' · ' +
      group.title +
      '</span>' +
      '<p class="muted">' +
      group.note +
      '</p>' +
      '</header>' +
      '<ul class="q-list">' +
      items +
      '</ul>' +
      '</section>'
    );
  }).join('');

  /* ---------------- 实时刻度盘 ---------------- */

  const gauge = root.querySelector('[data-gauge]');
  const gaugeAnswered = root.querySelector('[data-gauge-answered]');
  const gaugeTotal = root.querySelector('[data-gauge-total]');
  const gaugeStage = root.querySelector('[data-gauge-stage]');
  const pointer = root.querySelector('[data-gauge-pointer]');
  const segs = root.querySelectorAll('[data-gauge-seg]');
  const dimHost = root.querySelector('[data-gauge-dims]');
  const submitBtn = root.querySelector('[data-check-submit]');

  function paintLadder(stageKey, started) {
    const idx = STAGE_ORDER.indexOf(stageKey) + 1;
    segs.forEach((seg) => {
      const n = Number(seg.dataset.gaugeSeg);
      seg.classList.toggle('is-on', started && n <= idx);
      seg.classList.toggle('is-current', started && n === idx);
    });
    if (pointer) {
      pointer.hidden = !started;
      pointer.style.setProperty('--pos', ((idx - 0.5) / 8) * 100 + '%');
      pointer.textContent = STAGE[stageKey].band;
    }
  }

  function paintDims(dims, weak, complete) {
    if (!dimHost) return;
    dimHost.innerHTML = DIM_ORDER.map((d) => {
      const score = dims[d];
      const isWeak = complete && d === weak;
      return (
        '<div class="dim' +
        (isWeak ? ' is-weak' : '') +
        '">' +
        '<div class="dim-top"><span>' +
        DIM_NAME[d] +
        '</span><b class="num">' +
        score +
        '<i>/20</i></b></div>' +
        '<div class="dim-bar"><i style="width:' +
        (score / 20) * 100 +
        '%"></i></div>' +
        (isWeak ? '<span class="dim-flag">最弱一环</span>' : '') +
        '</div>'
      );
    }).join('');
  }

  function updateLive() {
    const { dims, total, answered, complete } = readScores(form);
    const stageKey = judgeStage(dims, total, complete);
    const weak = weakestDim(dims);

    if (gaugeAnswered) gaugeAnswered.textContent = answered;
    if (gaugeTotal) gaugeTotal.textContent = total;
    if (gauge) gauge.dataset.stage = stageKey;
    if (gaugeStage) {
      gaugeStage.textContent = complete
        ? STAGE[stageKey].name
        : answered === 0
          ? '还没开始作答'
          : '作答中，预估' + STAGE[stageKey].short;
    }

    paintLadder(stageKey, answered > 0);
    paintDims(dims, weak, complete);

    if (submitBtn) {
      submitBtn.disabled = answered === 0;
      submitBtn.textContent = complete
        ? '查看我的水位与建议'
        : '查看结果（还剩 ' + (QUESTION_IDS.length - answered) + ' 题）';
    }
  }

  form.addEventListener('change', (event) => {
    const target = event.target;
    if (target && target.name) {
      const item = form.querySelector('[data-q="' + target.name + '"]');
      if (item) item.classList.remove('is-missing');
    }
    updateLive();
  });

  /* ---------------- 结果 ---------------- */

  const resultBox = root.querySelector('[data-check-result]');

  function showResult() {
    const { dims, total, missing, complete } = readScores(form);

    if (!complete) {
      form.querySelectorAll('.q').forEach((el) => el.classList.remove('is-missing'));
      missing.forEach((id) => {
        const item = form.querySelector('[data-q="' + id + '"]');
        if (item) item.classList.add('is-missing');
      });
      const first = form.querySelector('[data-q="' + missing[0] + '"]');
      if (first) first.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }

    const stageKey = judgeStage(dims, total, true);
    const stage = STAGE[stageKey];
    const weak = weakestDim(dims);

    resultBox.dataset.stage = stageKey;
    resultBox.hidden = false;
    resultBox.innerHTML =
      '<header class="rs-head">' +
      '<span class="eyebrow">测评结果</span>' +
      '<h3 class="h-sec">你的企业在 ' +
      stage.band +
      ' · ' +
      stage.name +
      '</h3>' +
      '<p class="rs-meta num">总分 ' +
      total +
      '/80 · ' +
      DIM_ORDER.map((d) => DIM_NAME[d] + ' ' + dims[d]).join(' · ') +
      '</p>' +
      '<p class="lede">' +
      stage.desc +
      '</p>' +
      '</header>' +
      '<div class="rs-cols">' +
      '<section class="rs-col">' +
      '<h4 class="h-sub">先补最弱的一环：' +
      DIM_NAME[weak] +
      '</h4>' +
      '<ol class="rs-list">' +
      ACTIONS_BY_WEAK[weak].map((t) => '<li>' + t + '</li>').join('') +
      '</ol>' +
      '<p class="muted">这三件事建议放进 90 天内完成，都能用经营结果验证。</p>' +
      '</section>' +
      '<section class="rs-col rs-col-plan">' +
      '<h4 class="h-sub">这个阶段，朵灵·企云先帮你做三件事</h4>' +
      '<ol class="rs-list">' +
      stage.moves.map((t) => '<li>' + t + '</li>').join('') +
      '</ol>' +
      '<p class="rs-plan"><span class="tag tag-pro">建议版本</span>' +
      stage.plan +
      '<i>' +
      stage.planWhy +
      '</i></p>' +
      '</section>' +
      '</div>' +
      '<footer class="rs-foot">' +
      '<a class="btn btn-primary" href="05-价格方案.html">看 ' +
      stage.plan +
      '包含什么<span class="arrow">→</span></a>' +
      '<a class="btn btn-line" href="02-数智化转型.html">读懂四个阶段怎么走</a>' +
      '</footer>';

    const stageInput = document.querySelector('[data-lead-stage]');
    if (stageInput) stageInput.value = stage.band + ' · ' + stage.name;
    const stageEcho = document.querySelector('[data-lead-stage-echo]');
    if (stageEcho) {
      stageEcho.textContent = '已带入你的测评结果：' + stage.band + ' · ' + stage.name;
      stageEcho.hidden = false;
    }

    resultBox.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  if (submitBtn) submitBtn.addEventListener('click', showResult);

  const resetBtn = root.querySelector('[data-check-reset]');
  if (resetBtn) {
    resetBtn.addEventListener('click', () => {
      form.reset();
      form.querySelectorAll('.q').forEach((el) => el.classList.remove('is-missing'));
      if (resultBox) resultBox.hidden = true;
      updateLive();
      root.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }

  updateLive();
})();
