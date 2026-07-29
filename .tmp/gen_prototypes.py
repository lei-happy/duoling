# -*- coding: utf-8 -*-
"""Generate remaining mobile prototype HTML modules."""
from pathlib import Path

DRIVER = Path(r"D:\zhitu\prototype\移动端\驾驶员微信小程序")
ADMIN = Path(r"D:\zhitu\prototype\移动端\后台人员微信小程序")


def page(title, app, kicker, module_no, h1, badges, intent, meta_rows, rail, body, foot_extra=""):
    badge_html = "".join(f'<span class="badge {b[0]}">{b[1]}</span>' for b in badges)
    meta_html = "".join(
        f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in meta_rows
    )
    rail_html = "".join(
        f'<a href="#{aid}"><span class="n">{n}</span><span class="t">{t}</span></a>'
        for aid, n, t in rail
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<link rel="stylesheet" href="assets/mp.css" />
</head>
<body data-app="{app}">

<header class="pt-head">
  <div class="pt-head-inner">
    <div class="pt-kicker"><i></i><b>{kicker}</b><span>模块 {module_no}</span></div>
    <div class="pt-title">
      <h1>{h1}</h1>
      {badge_html}
    </div>
    <p class="pt-intent">{intent}</p>
    <dl class="pt-meta">{meta_html}</dl>
    <nav class="pt-rail">{rail_html}</nav>
  </div>
</header>

<main class="pt-body">
  <div class="pt-gallery">
{body}
  </div>
{foot_extra}
</main>

<footer class="pt-foot">智途 · {kicker}原型 · 模块 {module_no} {h1}</footer>
<script src="assets/mp.js"></script>
</body>
</html>
"""


def board(sid, num, title, tip, phone_inner, notes, auto=False):
    tip_html = f'<span class="tip">{tip}</span>' if tip else ""
    notes_html = "\n".join(f"<li>{n}</li>" for n in notes)
    cls = "dev auto" if auto else "dev"
    return f"""
    <section class="board" id="{sid}">
      <div class="board-cap"><span class="n">{num}</span><h3>{title}</h3>{tip_html}</div>
      <div class="{cls}">
{phone_inner}
      </div>
      <ol class="notes">{notes_html}</ol>
    </section>
"""


def phone(nav_title, body, bottom="", back=True, light_nav=False):
    back_attr = ' data-back' if back else ""
    head_cls = ' class="wx-head onpage"' if light_nav else ' class="wx-head"'
    return f"""        <div{head_cls}>
          <div class="wx-nav"{back_attr}><span class="ttl">{nav_title}</span></div>
        </div>
        <div class="wx-body scroll">
{body}
        </div>
{bottom}"""


def action_bar(*btns):
    # btns: list of (label, cls)
    inner = "".join(f'<a class="btn {c}">{lab}</a>' for lab, c in btns)
    return f'        <div class="action-bar">{inner}</div>\n'


def tabbar(active, badges=None):
    # active: home|task|finance|profile or home|dispatch|approve|profile
    badges = badges or {}
    items_driver = [
        ("home", "工作台", "home"),
        ("task", "任务", "list"),
        ("finance", "收入", "wallet"),
        ("profile", "我的", "user"),
    ]
    items_admin = [
        ("home", "工作台", "home"),
        ("dispatch", "调度", "truck"),
        ("approve", "审批", "check"),
        ("profile", "我的", "user"),
    ]
    items = items_admin if active in ("dispatch", "approve") or active.startswith("a_") else items_driver
    if active.startswith("a_"):
        active = active[2:]
        items = items_admin
    html = ['        <div class="tabbar">']
    for key, lab, ico in items:
        on = " on" if key == active else ""
        extra = ""
        if key in badges:
            b = badges[key]
            if b == "dot":
                extra = '<i class="dot"></i>'
            else:
                extra = f'<i class="num">{b}</i>'
        html.append(
            f'          <div class="item{on}"><svg class="ico"><use href="#i-{ico}"></use></svg>{lab}{extra}</div>'
        )
    html.append("        </div>")
    return "\n".join(html) + "\n"


# ========== DRIVER MODULES ==========

def gen_driver_07():
    boards = []
    # 1 auth guide
    boards.append(board("s1", "01", "位置授权引导", "P1", phone(
        "位置服务",
        """          <div class="pad" style="padding-top:36px;text-align:center">
            <div style="width:72px;height:72px;border-radius:20px;background:var(--brand-tint);color:var(--brand);display:flex;align-items:center;justify-content:center;margin:0 auto 18px">
              <svg class="ico" style="width:36px;height:36px"><use href="#i-nav"></use></svg>
            </div>
            <div class="t1 strong" style="font-size:20px">允许智途使用你的位置</div>
            <div class="t3 mt12" style="font-size:13px;line-height:1.7;padding:0 12px">
              装车、到达需要打卡定位；在途可上报轨迹，方便调度知道你到哪了。<br/>我们不会在收工后持续定位。
            </div>
            <a class="btn block mt16" style="margin-top:36px">允许使用位置</a>
            <a class="btn line block mt12">暂不开启</a>
          </div>"""
    ), [
        '<span class="flag">P1</span>需小程序位置权限与后端接收坐标。装车/到达打卡可先用可选文本 location（现有接口已支持），轨迹上报需新增 API。',
        '文案说清用途与边界（收工不定位），提高授权通过率。',
    ]))
    # 2 denied
    boards.append(board("s2", "02", "授权被拒 · 补救", "P1", phone(
        "位置服务",
        """          <div class="pad" style="padding-top:28px">
            <div class="notice danger">
              <svg class="ico"><use href="#i-warn"></use></svg>
              <span>你之前拒绝了位置权限。没有定位就没法打卡装车和到达。</span>
            </div>
            <div class="card" style="margin-top:14px">
              <div class="hd">怎么打开</div>
              <div class="t2" style="font-size:13px;line-height:1.7">
                1. 点下方「去设置」<br/>
                2. 找到「位置信息」<br/>
                3. 选「使用小程序时允许」
              </div>
            </div>
            <a class="btn block" style="margin:16px 12px">去设置打开</a>
            <div class="t3" style="text-align:center;font-size:12px">还是不行？联系调度，让他在电脑上代确认</div>
          </div>"""
    ), [
        '被拒后不弹系统死胡同，给出可行动步骤；并保留「调度代操作」退路（后台模块 05）。',
    ]))
    # 3 map + track
    boards.append(board("s3", "03", "任务内地图与轨迹开关", "P1", phone(
        "任务详情",
        """          <div class="banner">
            <div class="top"><span class="stat info">在途</span><span class="no">TK202607290031</span></div>
            <div class="nm">上海嘉定 → 合肥包河</div>
          </div>
          <div class="map" style="margin-top:12px">
            <div class="hint">轨迹上报已开启 · 每 2 分钟</div>
            <div class="mrk" style="left:58%;top:42%"><span class="bub"><svg class="ico"><use href="#i-truck"></use></svg>沪B·D7392</span></div>
          </div>
          <div class="card">
            <div class="cell" style="padding:0;border:none">
              <div class="k">轨迹上报</div>
              <div class="v green">已开启</div>
            </div>
            <div class="hr"></div>
            <div class="t3" style="font-size:12px;line-height:1.6">开启后，调度能在「在途监控」看到你的位置。费电较多时，可在休息时暂时关闭。</div>
          </div>
          <div class="card">
            <a class="btn soft block"><svg class="ico"><use href="#i-nav"></use></svg>导航去卸车地</a>
          </div>""",
        action_bar(("上报异常", "line"), ("确认到达", "wide"))
    ), [
        '<span class="flag">P1</span>轨迹上报开关本地记忆；后台在途监控（admin 06）消费同一数据源。',
        '导航走 <code>wx.openLocation</code> / 跳转腾讯或系统地图。',
    ]))
    # 4 nav confirm
    boards.append(board("s4", "04", "一键导航确认", "P1", phone(
        "任务详情",
        """          <div class="pad" style="filter:blur(1px);opacity:.45;pointer-events:none">
            <div class="card"><div class="hd">卸车地</div><div>合肥包河 · 徽通汽车城</div></div>
          </div>
          <div class="mask bottom">
            <div class="sheet">
              <div class="handle"></div>
              <div class="t1 strong" style="font-size:16px;margin-bottom:6px">打开地图导航</div>
              <div class="t3" style="font-size:13px;margin-bottom:14px">合肥包河 · 徽通汽车城<br/>合肥市包河区徽州大道 188 号</div>
              <a class="btn block mb8">腾讯地图</a>
              <a class="btn line block mb8">高德地图</a>
              <a class="btn line block">苹果地图</a>
            </div>
          </div>"""
    ), [
        '按手机已安装地图应用展示可选列表；一个都没有则直接 <code>wx.openLocation</code>。',
    ]))
    # 5 geofence
    boards.append(board("s5", "05", "到场围栏提醒", "P1", phone(
        "智途司机",
        """          <div class="pad" style="padding-top:80px">
            <div class="dialog" style="margin:0 auto;box-shadow:var(--shadow)">
              <div style="font-size:32px;margin-bottom:8px">📍</div>
              <div class="t">你已接近装车地</div>
              <div class="d">距离安亭商品车库约 480 米。到场后记得确认装车并拍照。</div>
              <div class="af">
                <a class="btn line wide">稍后</a>
                <a class="btn wide">去确认装车</a>
              </div>
            </div>
          </div>"""
    ), [
        '<span class="flag">P1</span>围栏半径建议 500m；仅对当前进行中任务触发一次，避免刷屏。',
        '可结合订阅消息，锁屏时也能提醒。',
    ]))

    return page(
        "07 位置与导航 · 驾驶员微信小程序", "driver", "驾驶员微信小程序", "07",
        "位置与导航",
        [("p1", "P1 需后端新增")],
        "装车、到达要打卡，在途要能被调度看见。位置能力不是炫技，而是让「我到了」这件事可核验。",
        [
            ("覆盖屏数", "5 屏"),
            ("使用角色", "驾驶员"),
            ("数据来源", "<code>wx.getLocation</code><span class=\"sep\">·</span>轨迹上报 API（新增）"),
            ("关联模块", "05 任务执行<span class=\"sep\">·</span>后台 06 在途监控"),
        ],
        [("s1", "1", "授权引导"), ("s2", "2", "被拒补救"), ("s3", "3", "地图轨迹"), ("s4", "4", "导航"), ("s5", "5", "围栏")],
        "\n".join(boards),
    )


def gen_driver_08():
    boards = []
    types = [("等货", "warn"), ("堵车", "info"), ("故障", "danger"), ("事故", "danger"), ("货损", "danger"), ("超时", "warning")]
    chips = "".join(f'<div class="chip">{t[0]}</div>' for t in types)
    boards.append(board("s1", "01", "选择异常类型", "P1", phone(
        "上报异常",
        f"""          <div class="pad">
            <div class="t1 strong" style="font-size:16px;margin-bottom:6px">这趟活出了什么情况？</div>
            <div class="t3" style="font-size:12px;margin-bottom:14px">选一个最贴近的，调度能更快帮你处理。</div>
            <div class="chips" style="padding:0;flex-wrap:wrap">{chips}</div>
          </div>"""
    ), [
        '<span class="flag">P1</span>异常类型枚举与后台告警（admin 06）共用；提交后任务详情出现「处理中」标记。',
    ]))
    boards.append(board("s2", "02", "填写异常详情", "P1", phone(
        "上报异常",
        """          <div class="pad">
            <div class="chip danger mb12">故障</div>
            <div class="field"><div class="lab">发生位置</div><div class="inp">沪陕高速 K326 · 已定位</div></div>
            <div class="field"><div class="lab">情况说明 <span class="req">*</span></div><div class="ta">右后轮胎爆胎，已靠边。预计换胎 40 分钟，可能晚到 1 小时。</div></div>
            <div class="field"><div class="lab">现场照片</div>
              <div class="photos">
                <div class="slot filled">1</div>
                <div class="slot filled">2</div>
                <div class="slot"><span class="add">+</span>添加</div>
              </div>
            </div>
          </div>""",
        action_bar(("提交给调度", "wide"))
    ), [
        '说明必填；照片最多 6 张。提交中文案：「正在通知调度，请稍候…」',
    ], auto=True))
    boards.append(board("s3", "03", "提交成功", "P1", phone(
        "上报异常",
        """          <div class="pad" style="padding-top:60px;text-align:center">
            <div style="width:64px;height:64px;border-radius:50%;background:var(--success-soft);color:var(--success);display:flex;align-items:center;justify-content:center;margin:0 auto 14px;font-size:28px">✓</div>
            <div class="t1 strong" style="font-size:18px">调度已收到</div>
            <div class="t3 mt8" style="font-size:13px;line-height:1.6;padding:0 20px">我们会尽快联系你。也可以在「我的异常」里看处理进度。</div>
            <a class="btn block" style="margin:28px 12px 10px">返回任务</a>
            <a class="btn line block" style="margin:0 12px">查看异常记录</a>
          </div>"""
    ), [
        '成功页给出路：回任务或看记录，不停留在空白成功态。',
    ]))
    boards.append(board("s4", "04", "我的异常记录", "P1", phone(
        "我的异常",
        """          <div class="pad">
            <div class="task">
              <div class="top"><span class="chip danger">故障</span><span class="chip muted">处理中</span></div>
              <div class="nm" style="font-size:14px">TK202607290031 · 爆胎靠边</div>
              <div class="meta"><span>今日 15:22</span><span>沪陕高速 K326</span></div>
            </div>
            <div class="task">
              <div class="top"><span class="chip warning">等货</span><span class="chip success">已完结</span></div>
              <div class="nm" style="font-size:14px">TK202607250018 · 厂家晚放行</div>
              <div class="meta"><span>07-25 09:40</span><span>等了 2.5 小时</span></div>
            </div>
          </div>"""
    ), [
        '列表按时间倒序；「处理中 / 已完结」状态与后台回执同步。',
    ]))
    boards.append(board("s5", "05", "处理结果回执", "P1", phone(
        "异常详情",
        """          <div class="pad">
            <div class="card">
              <div class="fx between mb8"><span class="chip danger">故障</span><span class="chip success">已完结</span></div>
              <div class="t1 strong">右后轮胎爆胎</div>
              <div class="t3 mt8" style="font-size:12px">TK202607290031 · 今日 15:22</div>
            </div>
            <div class="card">
              <div class="hd">调度回复</div>
              <div style="font-size:13px;line-height:1.65">已安排附近救援换胎，费用公司承担。晚到已跟客户报备，你安心处理。</div>
              <div class="t3 mt10" style="font-size:11px">调度 · 李敏 16:05</div>
            </div>
            <div class="card">
              <div class="hd">处理时间线</div>
              <div class="steps">
                <div class="s done"><div class="t">你已上报</div><div class="d">15:22</div></div>
                <div class="s done"><div class="t">调度已接单</div><div class="d">15:28</div></div>
                <div class="s done"><div class="t">已完结</div><div class="d">16:05 · 救援到位</div></div>
              </div>
            </div>
          </div>"""
    ), [
        '回执必须让司机看见「公司知道了、怎么处理的」，否则上报意愿会掉。',
    ], auto=True))

    return page(
        "08 异常上报 · 驾驶员微信小程序", "driver", "驾驶员微信小程序", "08",
        "异常上报",
        [("p1", "P1 需后端新增")],
        "路上出状况时，司机需要一条「一键喊调度」的通路。异常不是工单系统，而是让调度在 5 分钟内知道并回应。",
        [
            ("覆盖屏数", "5 屏"),
            ("使用角色", "驾驶员"),
            ("关联", "任务详情<span class=\"sep\">·</span>后台在途监控"),
        ],
        [("s1", "1", "类型"), ("s2", "2", "填写"), ("s3", "3", "成功"), ("s4", "4", "记录"), ("s5", "5", "回执")],
        "\n".join(boards),
    )


def gen_driver_13():
    boards = []
    boards.append(board("s1", "01", "订阅消息授权", "P1", phone(
        "消息通知",
        """          <div class="pad" style="padding-top:40px;text-align:center">
            <div style="font-size:40px;margin-bottom:12px">🔔</div>
            <div class="t1 strong" style="font-size:18px">打开重要通知</div>
            <div class="t3 mt10" style="font-size:13px;line-height:1.7;padding:0 8px">
              新调令、费用到账、证照快到期时，我们会用微信通知你。<br/>可随时在设置里关闭。
            </div>
            <div class="card" style="text-align:left;margin-top:22px">
              <div class="cell" style="padding:10px 0;border:none"><div class="k">新调令提醒</div><div class="v">建议开启</div></div>
              <div class="cell" style="padding:10px 0;border:none"><div class="k">费用到账</div><div class="v">建议开启</div></div>
              <div class="cell" style="padding:10px 0;border:none"><div class="k">证照到期</div><div class="v">建议开启</div></div>
            </div>
            <a class="btn block" style="margin:8px 12px">去开启</a>
            <div class="t3" style="font-size:12px">暂不开启</div>
          </div>"""
    ), [
        '<span class="flag">P1</span>使用微信订阅消息模板；一次引导勾选多项，减少反复弹窗。',
    ]))
    boards.append(board("s2", "02", "消息列表", "P1", phone(
        "消息",
        """          <div class="tabs">
            <div class="tab on">全部</div><div class="tab">调令</div><div class="tab">资金</div><div class="tab">证照</div><div class="tab">系统</div>
          </div>
          <div class="cells" style="margin-top:10px">
            <div class="cell">
              <div class="ib" style="background:var(--warning-soft);color:#b45309"><svg class="ico"><use href="#i-bell"></use></svg></div>
              <div class="grow">
                <div class="fx between"><span class="strong" style="font-size:14px">新调令待接收</span><span class="t3" style="font-size:11px">10:02</span></div>
                <div class="t3" style="font-size:12px;margin-top:3px">上海嘉定 → 合肥包河 · 请在 30 分钟内确认</div>
              </div>
            </div>
            <div class="cell">
              <div class="ib" style="background:var(--success-soft);color:var(--success)">¥</div>
              <div class="grow">
                <div class="fx between"><span style="font-size:14px">预付已到账</span><span class="t3" style="font-size:11px">昨天</span></div>
                <div class="t3" style="font-size:12px;margin-top:3px">TK031 · ¥800.00 已转入你的资金账户</div>
              </div>
            </div>
            <div class="cell">
              <div class="ib" style="background:var(--danger-soft);color:var(--danger)"><svg class="ico"><use href="#i-shield"></use></svg></div>
              <div class="grow">
                <div class="fx between"><span style="font-size:14px">驾驶证将于 28 天后到期</span><span class="t3" style="font-size:11px">周一</span></div>
                <div class="t3" style="font-size:12px;margin-top:3px">过期前请更新，否则可能无法派车</div>
              </div>
            </div>
          </div>"""
    ), [
        '未读用左侧色块+粗体标题区分；点击跳转对应业务页。',
    ]))
    boards.append(board("s3", "03", "消息详情跳转", "P1", phone(
        "消息详情",
        """          <div class="pad">
            <div class="card">
              <div class="chip warning mb8">调令</div>
              <div class="t1 strong" style="font-size:17px">新调令待接收</div>
              <div class="t3 mt8" style="font-size:12px">今日 10:02</div>
              <div class="hr"></div>
              <div style="font-size:14px;line-height:1.7">
                调度把任务 <b>TK202607290031</b> 派给了你。<br/>
                线路：上海嘉定 → 合肥包河<br/>
                台数：8 台 · 计划装车 07-29 08:30
              </div>
            </div>
            <a class="btn block" style="margin:8px 12px">查看任务并确认</a>
          </div>"""
    ), [
        '详情页主按钮直达业务动作，减少「看完消息还要自己找页面」。',
    ]))
    boards.append(board("s4", "04", "空态 / 全部已读", "P1", phone(
        "消息",
        """          <div class="empty">
            <svg class="ico" style="width:48px;height:48px"><use href="#i-msg"></use></svg>
            <div class="t">暂时没有新消息</div>
            <div class="d">有新调令或费用到账时，会第一时间通知你</div>
          </div>"""
    ), [
        '空态说清「什么时候会有消息」，避免司机以为坏了。',
    ]))

    return page(
        "13 消息中心 · 驾驶员微信小程序", "driver", "驾驶员微信小程序", "13",
        "消息中心",
        [("p1", "P1 需后端新增")],
        "司机不会一直盯着小程序。订阅消息是把「该干活了」「钱到了」送到他拇指上的唯一通道。",
        [("覆盖屏数", "4 屏"), ("使用角色", "驾驶员"), ("能力", "订阅消息 · 站内信")],
        [("s1", "1", "授权"), ("s2", "2", "列表"), ("s3", "3", "详情"), ("s4", "4", "空态")],
        "\n".join(boards),
    )


def gen_driver_09():
    boards = []
    boards.append(board("s1", "01", "收入 Tab · 费用单列表", "P0", phone(
        "收入",
        """          <div class="hero pad-b">
            <div class="t3" style="font-size:12px;opacity:.85">本月收入</div>
            <div style="font-size:32px;font-weight:700;font-family:var(--mono);margin-top:4px">¥ 18,600</div>
            <div class="fx g14 mt12" style="font-size:12px;opacity:.9">
              <span>预付 6,200</span><span>补款 1,400</span><span>结算 11,000</span>
            </div>
          </div>
          <div class="tabs">
            <div class="tab on">全部</div><div class="tab">预付单</div><div class="tab">补款单</div><div class="tab">结算单</div>
          </div>
          <div class="task">
            <div class="top"><span class="chip success">已支付</span><span class="chip primary">预付单</span></div>
            <div class="fx between"><span class="strong">TK202607290031</span><span class="money">¥ 800.00</span></div>
            <div class="meta mt8"><span>上海 → 合肥</span><span>07-29 支付</span></div>
          </div>
          <div class="task">
            <div class="top"><span class="chip info">已审批</span><span class="chip primary">结算单</span></div>
            <div class="fx between"><span class="strong">TK202607250018</span><span class="money">¥ 2,100.00</span></div>
            <div class="meta mt8"><span>杭州 → 南京</span><span>待打款</span></div>
          </div>""",
        tabbar("finance")
    ), [
        '金额与状态同屏。API：<code>GET /api/driver/finance/my</code>、<code>/summary</code>。',
    ]))
    boards.append(board("s2", "02", "费用单详情", "P0", phone(
        "费用单详情",
        """          <div class="pad">
            <div class="card" style="text-align:center">
              <div class="chip success mb8">已支付</div>
              <div class="money" style="font-size:28px">¥ 800.00</div>
              <div class="t3 mt8">预付单 · FP202607290012</div>
            </div>
            <div class="card">
              <div class="cell" style="padding:8px 0;border:none"><div class="k">关联任务</div><div class="v">TK202607290031</div></div>
              <div class="cell" style="padding:8px 0;border:none"><div class="k">支付方式</div><div class="v">银行转账</div></div>
              <div class="cell" style="padding:8px 0;border:none"><div class="k">支付时间</div><div class="v">07-29 11:20</div></div>
            </div>
            <div class="card">
              <div class="hd">费用明细</div>
              <div class="fx between mb8"><span class="t2">运输费预付</span><span>¥ 800.00</span></div>
            </div>
          </div>"""
    ), [
        '只读。司机不能改金额、不能自己「确认支付」。',
    ]))
    boards.append(board("s3", "03", "收入汇总", "P0", phone(
        "收入汇总",
        """          <div class="pad">
            <div class="card">
              <div class="t3">近 6 个月合计</div>
              <div class="money" style="font-size:26px;margin-top:4px">¥ 96,480</div>
              <div class="chart-bars mt12">
                <div class="bar" style="height:40%"><span class="lbl">2月</span></div>
                <div class="bar" style="height:55%"><span class="lbl">3月</span></div>
                <div class="bar" style="height:48%"><span class="lbl">4月</span></div>
                <div class="bar" style="height:70%"><span class="lbl">5月</span></div>
                <div class="bar" style="height:62%"><span class="lbl">6月</span></div>
                <div class="bar" style="height:85%"><span class="lbl">7月</span></div>
              </div>
            </div>
            <div class="card">
              <div class="fx between mb10"><span class="t2">预付</span><span class="strong">¥ 28,400</span></div>
              <div class="fx between mb10"><span class="t2">补款</span><span class="strong">¥ 6,080</span></div>
              <div class="fx between"><span class="t2">结算</span><span class="strong">¥ 62,000</span></div>
            </div>
          </div>"""
    ), [
        'API：<code>GET /api/driver/finance/summary</code>。柱状为示意，正式版可换轻量图表。',
    ]))
    boards.append(board("s4", "04", "资金往来账", "P0", phone(
        "资金账户",
        """          <div class="hero pad-b">
            <div class="t3" style="opacity:.85">可用余额</div>
            <div style="font-size:30px;font-weight:700;font-family:var(--mono)">¥ 3,260.00</div>
            <div class="fx g14 mt12" style="font-size:12px;opacity:.9"><span>累计入 96,480</span><span>累计出 93,220</span></div>
          </div>
          <div class="pad">
            <div class="t1 strong mb12">近期流水</div>
            <div class="fx between mb12" style="font-size:13px">
              <div><div class="strong">任务结算入账</div><div class="t3" style="font-size:11px">07-28 · TK018</div></div>
              <span class="green strong">+2,100.00</span>
            </div>
            <div class="fx between mb12" style="font-size:13px">
              <div><div class="strong">预付登记</div><div class="t3" style="font-size:11px">07-29 · TK031</div></div>
              <span class="green strong">+800.00</span>
            </div>
            <div class="fx between" style="font-size:13px">
              <div><div class="strong">人工出账</div><div class="t3" style="font-size:11px">07-20 · 提现</div></div>
              <span class="err strong">-5,000.00</span>
            </div>
          </div>"""
    ), [
        'API：<code>/finance/fund-account</code>、<code>/transactions</code>。',
    ]))
    boards.append(board("s5", "05", "收款账户", "P0", phone(
        "收款账户",
        """          <div class="pad">
            <div class="card">
              <div class="fx g10">
                <div class="ib" style="width:40px;height:40px;border-radius:10px;background:var(--brand-tint);color:var(--brand);display:flex;align-items:center;justify-content:center">卡</div>
                <div class="grow">
                  <div class="strong">工商银行</div>
                  <div class="t3" style="font-size:12px">尾号 6682 · 王建军</div>
                </div>
                <span class="chip success">默认</span>
              </div>
            </div>
            <div class="card">
              <div class="fx g10">
                <div class="ib" style="width:40px;height:40px;border-radius:10px;background:var(--warning-soft);color:#b45309;display:flex;align-items:center;justify-content:center">油</div>
                <div class="grow">
                  <div class="strong">中石油油卡</div>
                  <div class="t3" style="font-size:12px">尾号 0199</div>
                </div>
              </div>
            </div>
            <div class="notice info" style="margin:12px;border-radius:8px">
              <span>账户由公司维护。要换卡请联系调度或财务，不要自己改。</span>
            </div>
          </div>"""
    ), [
        '只读列表。API：<code>GET /api/driver/finance/account</code>。',
    ]))

    return page(
        "09 收入与资金 · 驾驶员微信小程序", "driver", "驾驶员微信小程序", "09",
        "收入与资金",
        [("p0", "P0 已有能力")],
        "司机最关心两件事：这趟能拿多少、钱到哪了。收入模块只做透明查询，不做支付操作。",
        [("覆盖屏数", "5 屏"), ("tabBar", "第 3 个 · 收入"), ("API", "<code>/api/driver/finance/*</code>")],
        [("s1", "1", "列表"), ("s2", "2", "详情"), ("s3", "3", "汇总"), ("s4", "4", "资金账"), ("s5", "5", "收款账户")],
        "\n".join(boards),
    )


def gen_driver_10():
    boards = []
    boards.append(board("s1", "01", "我的车辆", "P1", phone(
        "我的车辆",
        """          <div class="pad">
            <div class="card">
              <div class="fx between mb8"><span class="strong" style="font-size:18px">沪B·D7392</span><span class="chip success">出车中</span></div>
              <div class="t3" style="font-size:12px">解放 JH6 · 板车 · 2021 款</div>
              <div class="hr"></div>
              <div class="fx between" style="font-size:13px"><span class="t2">挂车</span><span>沪B·挂 8821</span></div>
            </div>
            <div class="card">
              <div class="hd">当前任务</div>
              <div class="strong">上海嘉定 → 合肥包河</div>
              <div class="t3 mt6" style="font-size:12px">TK202607290031 · 在途</div>
            </div>
          </div>"""
    ), [
        '<span class="flag">P1</span>司机端无车辆 CRUD；只读展示任务关联与运力绑定信息。',
    ]))
    boards.append(board("s2", "02", "证照到期倒计时", "P1", phone(
        "我的证照",
        """          <div class="pad">
            <div class="card">
              <div class="fx between"><span class="strong">驾驶证</span><span class="chip danger">28 天后到期</span></div>
              <div class="t3 mt8" style="font-size:12px">有效期至 2026-08-26</div>
              <div class="progress mt10"><div class="bar" style="width:18%;background:var(--danger)"></div></div>
            </div>
            <div class="card">
              <div class="fx between"><span class="strong">从业资格证</span><span class="chip warning">61 天后到期</span></div>
              <div class="t3 mt8" style="font-size:12px">有效期至 2026-09-28</div>
            </div>
            <div class="card">
              <div class="fx between"><span class="strong">行驶证</span><span class="chip success">正常</span></div>
              <div class="t3 mt8" style="font-size:12px">有效期至 2027-03-12</div>
            </div>
            <div class="card">
              <div class="fx between"><span class="strong">交强险</span><span class="chip success">正常</span></div>
              <div class="t3 mt8" style="font-size:12px">有效期至 2027-01-08</div>
            </div>
          </div>"""
    ), [
        '≤30 天红色，≤60 天橙色。过期会影响派车，工作台应置顶提醒。',
    ]))
    boards.append(board("s3", "03", "上传更新证照", "P1", phone(
        "更新驾驶证",
        """          <div class="pad">
            <div class="field"><div class="lab">证照照片</div>
              <div class="photos"><div class="slot filled">正面</div><div class="slot"><span class="add">+</span>反面</div><div class="slot"><span class="add">+</span></div></div>
            </div>
            <div class="field"><div class="lab">新的有效期至</div><div class="inp ph">请选择日期</div></div>
            <div class="notice info" style="border-radius:8px"><span>提交后由公司审核，通过前仍显示原有效期。</span></div>
          </div>""",
        action_bar(("提交更新", "wide"))
    ), [
        '<span class="flag">P1</span>需后端证照更新与审核流；也可先做「联系调度更新」降级。',
    ]))
    boards.append(board("s4", "04", "出车前点检", "P1", phone(
        "出车前点检",
        """          <div class="pad">
            <div class="t3 mb12" style="font-size:12px">TK202607290031 · 沪B·D7392</div>
            <div class="cells" style="margin:0">
              <div class="cell"><span class="ck on">✓</span><div class="k">轮胎气压正常</div></div>
              <div class="cell"><span class="ck on">✓</span><div class="k">灯光 / 刹车正常</div></div>
              <div class="cell"><span class="ck"></span><div class="k">捆绑器具齐全</div></div>
              <div class="cell"><span class="ck"></span><div class="k">证件随车</div></div>
            </div>
            <div class="field mt16"><div class="lab">备注（选填）</div><div class="ta">右后轮胎花纹偏浅，已告知调度</div></div>
          </div>""",
        action_bar(("完成点检并装车", "wide"))
    ), [
        '<span class="flag">P1</span>点检可作为确认装车的前置步骤；未勾齐全时主按钮置灰并提示。',
    ]))

    return page(
        "10 车辆与证照 · 驾驶员微信小程序", "driver", "驾驶员微信小程序", "10",
        "车辆与证照",
        [("p1", "P1 需后端新增")],
        "车和证是司机的饭碗。到期提醒要提前，点检要轻量，不能做成又一张复杂表单。",
        [("覆盖屏数", "4 屏"), ("使用角色", "驾驶员")],
        [("s1", "1", "车辆"), ("s2", "2", "证照"), ("s3", "3", "更新"), ("s4", "4", "点检")],
        "\n".join(boards),
    )


def gen_driver_11():
    boards = []
    boards.append(board("s1", "01", "油卡余额与加油记录", "P2", phone(
        "油卡与加油",
        """          <div class="hero pad-b">
            <div class="t3" style="opacity:.85">油卡余额</div>
            <div style="font-size:30px;font-weight:700;font-family:var(--mono)">¥ 1,280.50</div>
            <div class="t3 mt8" style="font-size:12px;opacity:.85">中石油 · 尾号 0199</div>
          </div>
          <div class="pad">
            <div class="fx between mb12"><span class="strong">近期加油</span><span class="lnk">全部</span></div>
            <div class="fx between mb12" style="font-size:13px">
              <div><div class="strong">沪陕服务区</div><div class="t3" style="font-size:11px">07-29 16:10 · 柴油</div></div>
              <span class="strong">¥ 680.00</span>
            </div>
            <div class="fx between" style="font-size:13px">
              <div><div class="strong">嘉定加油站</div><div class="t3" style="font-size:11px">07-28 07:40 · 柴油</div></div>
              <span class="strong">¥ 520.00</span>
            </div>
          </div>"""
    ), [
        '<span class="flag">P2</span>全部需新建油卡/加油领域模型与接口，本版仅产品原型。',
    ]))
    boards.append(board("s2", "02", "维修保养申请", "P2", phone(
        "维修申请",
        """          <div class="pad">
            <div class="field"><div class="lab">车辆</div><div class="inp">沪B·D7392</div></div>
            <div class="field"><div class="lab">类型</div><div class="inp">轮胎更换</div></div>
            <div class="field"><div class="lab">预估费用</div><div class="inp ph">选填</div></div>
            <div class="field"><div class="lab">情况说明</div><div class="ta">右后轮胎爆胎，需更换并做动平衡</div></div>
            <div class="photos"><div class="slot filled">1</div><div class="slot"><span class="add">+</span></div></div>
          </div>""",
        action_bar(("提交申请", "wide"))
    ), [
        '提交后进入审批（可对接审批中心）；司机只看进度。',
    ]))
    boards.append(board("s3", "03", "维修进度", "P2", phone(
        "维修进度",
        """          <div class="pad">
            <div class="card">
              <div class="fx between"><span class="strong">轮胎更换</span><span class="chip info">审批中</span></div>
              <div class="t3 mt8" style="font-size:12px">沪B·D7392 · 今日 15:40 提交</div>
            </div>
            <div class="card">
              <div class="steps">
                <div class="s done"><div class="t">已提交</div><div class="d">15:40</div></div>
                <div class="s now"><div class="t">车队长审批</div><div class="d">处理中</div></div>
                <div class="s"><div class="t">维修完成确认</div><div class="d">待完成</div></div>
              </div>
            </div>
          </div>"""
    ), ["进度节点与审批中心对齐，避免两套状态。"]))
    boards.append(board("s4", "04", "垫付费用报销", "P2", phone(
        "垫付报销",
        """          <div class="pad">
            <div class="field"><div class="lab">费用类型</div><div class="inp">路桥费</div></div>
            <div class="field"><div class="lab">金额</div><div class="inp">¥ 245.00</div></div>
            <div class="field"><div class="lab">关联任务</div><div class="inp">TK202607290031</div></div>
            <div class="field"><div class="lab">发票 / 收据照片</div>
              <div class="photos"><div class="slot filled">票</div><div class="slot"><span class="add">+</span></div></div>
            </div>
          </div>""",
        action_bar(("提交报销", "wide"))
    ), [
        '报销审核通过后进入财务支付；司机在收入/资金账中可见入账。',
    ]))

    return page(
        "11 油卡与维修 · 驾驶员微信小程序", "driver", "驾驶员微信小程序", "11",
        "油卡与维修",
        [("p2", "P2 远期 · 需后端新增")],
        "油和修是司机日常现金压力最大的两块。本模块全部为远期能力，原型用于对齐产品方向，开发勿误判为 P0。",
        [("覆盖屏数", "4 屏"), ("优先级", "P2 远期")],
        [("s1", "1", "油卡"), ("s2", "2", "维修申请"), ("s3", "3", "进度"), ("s4", "4", "报销")],
        "\n".join(boards),
    )


def gen_driver_12():
    boards = []
    boards.append(board("s1", "01", "我的排班", "P2", phone(
        "我的排班",
        """          <div class="pad">
            <div class="card">
              <div class="fx between"><span class="strong">今日状态</span><span class="chip success">可出车</span></div>
              <div class="t3 mt8" style="font-size:12px">本周已出车 4 天 · 休息 1 天</div>
            </div>
            <div class="card">
              <div class="hd">本周</div>
              <div class="fx between mb8" style="font-size:13px"><span>周一</span><span class="green">出车 · 沪→合</span></div>
              <div class="fx between mb8" style="font-size:13px"><span>周二</span><span class="green">出车 · 合→宁</span></div>
              <div class="fx between mb8" style="font-size:13px"><span>周三</span><span class="t3">休息</span></div>
              <div class="fx between mb8" style="font-size:13px"><span>周四</span><span class="chip primary">待派</span></div>
              <div class="fx between" style="font-size:13px"><span>周五</span><span class="t3">未排</span></div>
            </div>
          </div>"""
    ), ['<span class="flag">P2</span>排班数据依赖企业端排班能力，当前 PC 无完整模块。']))
    boards.append(board("s2", "02", "请假申请", "P2", phone(
        "请假申请",
        """          <div class="pad">
            <div class="field"><div class="lab">请假类型</div><div class="inp">事假</div></div>
            <div class="field"><div class="lab">开始日期</div><div class="inp">2026-08-02</div></div>
            <div class="field"><div class="lab">结束日期</div><div class="inp">2026-08-03</div></div>
            <div class="field"><div class="lab">原因</div><div class="ta">家中有事，需返乡两天</div></div>
          </div>""",
        action_bar(("提交请假", "wide"))
    ), ["提交后走审批；通过前仍可被派车，需产品规则确认。"]))
    boards.append(board("s3", "03", "请假审批进度", "P2", phone(
        "请假详情",
        """          <div class="pad">
            <div class="card">
              <div class="fx between"><span class="strong">事假 2 天</span><span class="chip info">审批中</span></div>
              <div class="t3 mt8">08-02 至 08-03</div>
            </div>
            <div class="card">
              <div class="steps">
                <div class="s done"><div class="t">已提交</div><div class="d">今日 09:12</div></div>
                <div class="s now"><div class="t">车队长审批</div><div class="d">处理中</div></div>
                <div class="s"><div class="t">完成</div><div class="d">待完成</div></div>
              </div>
            </div>
          </div>"""
    ), ["与审批中心消息打通。"]))
    boards.append(board("s4", "04", "司机排行榜", "P2", phone(
        "本月排行",
        """          <div class="pad">
            <div class="chips" style="padding:0 0 12px"><div class="chip on">准时率</div><div class="chip">签收率</div><div class="chip">里程</div><div class="chip">收入</div></div>
            <div class="card">
              <div class="fx g10 mb12"><span class="strong" style="color:var(--warning)">1</span><div class="grow"><div class="strong">周强</div><div class="t3" style="font-size:11px">准时率 99%</div></div></div>
              <div class="fx g10 mb12"><span class="strong" style="color:var(--t3)">2</span><div class="grow"><div class="strong">王建军（我）</div><div class="t3" style="font-size:11px">准时率 97%</div></div></div>
              <div class="fx g10"><span class="strong" style="color:#b45309">3</span><div class="grow"><div class="strong">刘洋</div><div class="t3" style="font-size:11px">准时率 96%</div></div></div>
            </div>
            <div class="notice info" style="border-radius:8px;margin:0"><span>排行仅本企业司机可见，用于正向激励，不与扣款挂钩。</span></div>
          </div>"""
    ), ["排行数据需运营指标口径，避免变成扣钱工具。"]))

    return page(
        "12 排班与绩效 · 驾驶员微信小程序", "driver", "驾驶员微信小程序", "12",
        "排班与绩效",
        [("p2", "P2 远期 · 需后端新增")],
        "让司机看见自己的出勤与表现。排行榜只做激励，不与惩罚绑定。",
        [("覆盖屏数", "4 屏"), ("优先级", "P2 远期")],
        [("s1", "1", "排班"), ("s2", "2", "请假"), ("s3", "3", "进度"), ("s4", "4", "排行")],
        "\n".join(boards),
    )


def gen_driver_14():
    boards = []
    boards.append(board("s1", "01", "我的首页", "P0", phone(
        "我的",
        """          <div class="hero pad-b">
            <div class="fx g10" style="padding-top:8px">
              <div class="ava lg" style="width:56px;height:56px;font-size:20px">王</div>
              <div>
                <div style="font-size:18px;font-weight:600">王建军</div>
                <div class="t3 mt4" style="font-size:12px;opacity:.9">139****3308</div>
                <div class="fx g4 mt6" style="font-size:12px;opacity:.9"><svg class="ico" style="width:12px;height:12px"><use href="#i-building"></use></svg>皖通汽车物流</div>
              </div>
            </div>
          </div>
          <div class="cells">
            <div class="cell"><div class="ib"><svg class="ico"><use href="#i-user"></use></svg></div><div class="k">个人信息</div><span class="caret">›</span></div>
            <div class="cell"><div class="ib"><svg class="ico"><use href="#i-swap"></use></svg></div><div class="k">切换企业</div><div class="v">皖通</div><span class="caret">›</span></div>
            <div class="cell"><div class="ib"><svg class="ico"><use href="#i-wallet"></use></svg></div><div class="k">收入汇总</div><span class="caret">›</span></div>
            <div class="cell"><div class="ib" style="background:var(--warning-soft);color:#b45309"><svg class="ico"><use href="#i-shield"></use></svg></div><div class="k">我的证照</div><div class="v err">1 即将到期</div><span class="caret">›</span></div>
            <div class="cell"><div class="ib"><svg class="ico"><use href="#i-setting"></use></svg></div><div class="k">隐私与授权</div><span class="caret">›</span></div>
            <div class="cell"><div class="ib"><svg class="ico"><use href="#i-msg"></use></svg></div><div class="k">联系调度 / 帮助</div><span class="caret">›</span></div>
          </div>
          <a class="btn line block" style="margin:16px 12px;color:var(--danger);border-color:#fecaca">退出登录</a>""",
        tabbar("profile", {"profile": "dot"})
    ), [
        'API：<code>GET /auth/user-info</code>、<code>/profile/me</code>。证照预警角标与模块 10 联动。',
    ], auto=True))
    boards.append(board("s2", "02", "个人信息编辑", "P0", phone(
        "个人信息",
        """          <div class="pad">
            <div class="cells" style="margin:0 0 12px">
              <div class="cell"><div class="k">姓名</div><div class="v">王建军</div></div>
              <div class="cell"><div class="k">手机号</div><div class="v">139****3308</div></div>
              <div class="cell"><div class="k">驾驶证号</div><div class="v">已登记</div></div>
            </div>
            <div class="t3 mb8" style="font-size:12px">以下信息可自行修改</div>
            <div class="field"><div class="lab">紧急联系人</div><div class="inp">王芳</div></div>
            <div class="field"><div class="lab">紧急联系电话</div><div class="inp">138****2211</div></div>
            <div class="field"><div class="lab">住址</div><div class="inp">上海市嘉定区安亭镇…</div></div>
          </div>""",
        action_bar(("保存", "wide"))
    ), [
        '白名单字段：紧急联系人/电话/住址/头像。姓名手机号只读。API：<code>PUT /profile/me</code>。',
    ]))
    boards.append(board("s3", "03", "切换企业", "P0", phone(
        "切换企业",
        """          <div class="pad">
            <div class="card" style="border:1.5px solid var(--brand)">
              <div class="fx between"><span class="strong">皖通汽车物流</span><span class="chip success">当前</span></div>
              <div class="t3 mt8" style="font-size:12px">主驾 · 沪B·D7392</div>
            </div>
            <div class="card">
              <div class="fx between"><span class="strong">上汽安吉物流</span><span class="chip muted">在职</span></div>
              <div class="t3 mt8" style="font-size:12px">主驾 · 沪A·K2281</div>
            </div>
            <div class="card dim">
              <div class="fx between"><span class="strong">合众轿运</span><span class="chip muted">已离职</span></div>
              <div class="t3 mt8" style="font-size:12px">可查历史收入，不可接新任务</div>
            </div>
          </div>"""
    ), [
        'API：<code>/auth/user-tenants</code>、<code>/auth/switch-tenant</code>。已离职只读。',
    ]))
    boards.append(board("s4", "04", "修改密码", "P0", phone(
        "修改密码",
        """          <div class="pad">
            <div class="field"><div class="lab">当前密码</div><div class="inp ph">请输入</div></div>
            <div class="field"><div class="lab">新密码</div><div class="inp ph">至少 8 位</div></div>
            <div class="field"><div class="lab">确认新密码</div><div class="inp ph">再输入一次</div></div>
            <div class="notice info" style="border-radius:8px"><span>改密成功后需重新登录。</span></div>
          </div>""",
        action_bar(("确认修改", "wide"))
    ), [
        '强制改密场景带 <code>force=1</code>，成功后进工作台。API：<code>PUT /auth/password</code>。',
    ]))
    boards.append(board("s5", "05", "隐私授权与退出", "P0", phone(
        "隐私与授权",
        """          <div class="cells">
            <div class="cell"><div class="k">位置信息</div><div class="v green">已允许</div><span class="caret">›</span></div>
            <div class="cell"><div class="k">摄像头 / 相册</div><div class="v green">已允许</div><span class="caret">›</span></div>
            <div class="cell"><div class="k">订阅消息</div><div class="v">去管理</div><span class="caret">›</span></div>
          </div>
          <div class="pad" style="filter:blur(.5px);opacity:.5"><div class="card">服务协议 · 隐私政策</div></div>
          <div class="mask center">
            <div class="dialog">
              <div class="t">确定退出登录？</div>
              <div class="d">退出后不会删除你的任务和收入记录，下次用手机号还能进来。</div>
              <div class="af">
                <a class="btn line wide">取消</a>
                <a class="btn danger wide">退出</a>
              </div>
            </div>
          </div>"""
    ), [
        '退出清除本地 Token；不提示「清除数据」等恐吓文案。',
    ]))

    return page(
        "14 我的与设置 · 驾驶员微信小程序", "driver", "驾驶员微信小程序", "14",
        "我的与设置",
        [("p0", "P0 已有能力")],
        "账号、企业、密码、授权——司机很少来，但来的时候必须一次搞定。",
        [("覆盖屏数", "5 屏"), ("tabBar", "第 4 个 · 我的")],
        [("s1", "1", "首页"), ("s2", "2", "资料"), ("s3", "3", "切企业"), ("s4", "4", "改密"), ("s5", "5", "隐私退出")],
        "\n".join(boards),
    )


# ========== ADMIN MODULES ==========

def gen_admin_01():
    boards = []
    boards.append(board("s1", "01", "微信一键登录", "P1", phone(
        "智途管理",
        """          <div class="pad" style="padding-top:32px">
            <div class="fx g10 mb16">
              <div style="width:48px;height:48px;border-radius:14px;background:var(--brand);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:20px">智</div>
              <div><div class="t1 strong" style="font-size:20px">智途管理</div><div class="t3" style="font-size:12px">老板 / 调度 / 车队长 / 财务</div></div>
            </div>
            <div class="t1" style="font-size:20px;font-weight:600;line-height:1.45;margin:28px 0 10px">手机办公，批得快、看得清</div>
            <div class="t3" style="font-size:13px;line-height:1.65;margin-bottom:32px">用微信手机号登录你所在的运输公司。复杂配置仍在电脑上完成。</div>
            <a class="btn block">微信一键登录</a>
            <a class="btn line block mt12">手机号密码登录</a>
          </div>""",
        back=False, light_nav=True
    ), [
        '<span class="flag">P1</span>复用租户账号体系；当前 admin-mp 仅为演示登录。正式对接 <code>/api/client</code> 鉴权。',
        '移动端不做注册，账号由企业在 PC 开通。',
    ]))
    boards.append(board("s2", "02", "选择企业与角色", "P0", phone(
        "选择企业",
        """          <div class="pad">
            <div class="t3 mb12" style="font-size:12px">你的账号属于多家企业，请选择本次要进入的</div>
            <div class="card" style="border:1.5px solid var(--brand)">
              <div class="strong">皖通汽车物流</div>
              <div class="fx g6 mt8"><span class="chip primary">调度</span><span class="chip muted">车队长</span></div>
            </div>
            <div class="card">
              <div class="strong">合众轿运</div>
              <div class="fx g6 mt8"><span class="chip muted">老板</span></div>
            </div>
          </div>"""
    ), ["角色标签来自租户权限；进入后工作台按角色裁剪。"]))
    boards.append(board("s3", "03", "无权限空态", "P0", phone(
        "智途管理",
        """          <div class="empty" style="padding-top:80px">
            <div class="t">当前账号暂无移动端权限</div>
            <div class="d">请联系企业管理员，在电脑端「角色权限」里开通调度、财务或审批相关权限后再试。</div>
            <a class="btn line" style="margin-top:20px">切换企业</a>
          </div>"""
    ), ["无菜单权限时不进空工作台，直接说明怎么办。"]))

    return page(
        "01 登录与企业切换 · 后台人员微信小程序", "admin", "后台人员微信小程序", "01",
        "登录与企业切换",
        [("p0", "密码登录可对接"), ("p1", "微信登录 P1")],
        "后台人员小程序服务老板、调度、车队长、财务。登录要快，角色要一眼可见，没有权限要说清找谁开。",
        [("覆盖屏数", "3 屏"), ("产品名", "智途管理"), ("账号", "租户端用户 sys_user")],
        [("s1", "1", "登录"), ("s2", "2", "选企业"), ("s3", "3", "无权限")],
        "\n".join(boards),
    )


def gen_admin_02():
    boards = []
    boards.append(board("s1", "01", "调度角色 · 工作台", "P0", phone(
        "工作台",
        """          <div class="hero pad-b">
            <div class="fx between">
              <div>
                <div style="font-size:12px;opacity:.85">下午好</div>
                <div style="font-size:18px;font-weight:600;margin-top:2px">李敏 · 调度</div>
                <div style="font-size:12px;opacity:.85;margin-top:4px">皖通汽车物流</div>
              </div>
              <div class="ava">李</div>
            </div>
          </div>
          <div class="t3" style="padding:12px 12px 6px;font-size:12px">今日需关注</div>
          <div class="kpi-grid">
            <div class="kpi warn"><div class="k">待确认计划</div><div class="v">6</div></div>
            <div class="kpi brand"><div class="k">调度在途</div><div class="v">14</div></div>
            <div class="kpi"><div class="k">待我审批</div><div class="v">3</div></div>
            <div class="kpi"><div class="k">异常待处理</div><div class="v" style="color:var(--danger)">2</div></div>
          </div>
          <div class="card">
            <div class="hd">快捷入口</div>
            <div class="quick">
              <div class="q"><div class="ib"><svg class="ico"><use href="#i-truck"></use></svg></div>调度台</div>
              <div class="q"><div class="ib warn"><svg class="ico"><use href="#i-list"></use></svg></div>待派车</div>
              <div class="q"><div class="ib"><svg class="ico"><use href="#i-nav"></use></svg></div>在途</div>
              <div class="q"><div class="ib success"><svg class="ico"><use href="#i-check"></use></svg></div>审批</div>
            </div>
          </div>
          <div class="card">
            <div class="hd">我的待办 <span class="more">全部</span></div>
            <div class="fx between mb10" style="font-size:13px"><span>派车 · TK031 待派</span><span class="chip warning">紧急</span></div>
            <div class="fx between" style="font-size:13px"><span>审批 · 预付单 ¥800</span><span class="t3">1h 前</span></div>
          </div>""",
        tabbar("a_home", {"approve": "3"})
    ), [
        '三指标对齐 PC <code>attention-metrics-registry</code>：待确认计划 / 调度在途 / 待我审批。',
        '调度首屏强调「催与派」，不是经营看板。',
    ], auto=True))
    boards.append(board("s2", "02", "老板角色 · 首屏差异", "P0", phone(
        "工作台",
        """          <div class="hero pad-b">
            <div style="font-size:18px;font-weight:600">张总 · 老板</div>
            <div style="font-size:12px;opacity:.85;margin-top:4px">看利润、看风险，不看填单</div>
            <div class="kpis mt16">
              <div class="kpi"><div class="v sm">128</div><div class="k">本月单量</div></div>
              <div class="kpi"><div class="v sm">286万</div><div class="k">运费</div></div>
              <div class="kpi"><div class="v sm">41万</div><div class="k">毛利</div></div>
              <div class="kpi"><div class="v sm">14%</div><div class="k">毛利率</div></div>
            </div>
          </div>
          <div class="card">
            <div class="hd">今日风险</div>
            <div class="fx between mb8" style="font-size:13px"><span>在途异常未处理</span><span class="err strong">2</span></div>
            <div class="fx between mb8" style="font-size:13px"><span>证照 7 日内到期</span><span class="chip warning">5 人</span></div>
            <div class="fx between" style="font-size:13px"><span>待确认计划超 24h</span><span>3</span></div>
          </div>
          <div class="card">
            <div class="quick">
              <div class="q"><div class="ib"><svg class="ico"><use href="#i-chart"></use></svg></div>经营看板</div>
              <div class="q"><div class="ib"><svg class="ico"><use href="#i-nav"></use></svg></div>在途</div>
              <div class="q"><div class="ib warn"><svg class="ico"><use href="#i-check"></use></svg></div>待审批</div>
              <div class="q"><div class="ib"><svg class="ico"><use href="#i-wallet"></use></svg></div>费用</div>
            </div>
          </div>""",
        tabbar("a_home")
    ), ["老板首屏 = 经营 KPI + 风险，快捷入口导向看板与审批，不放「新建计划」。"]))
    boards.append(board("s3", "03", "财务角色 · 首屏差异", "P0", phone(
        "工作台",
        """          <div class="hero pad-b">
            <div style="font-size:18px;font-weight:600">赵倩 · 财务</div>
            <div class="fx g14 mt16">
              <div><div style="font-size:11px;opacity:.85">待我审批</div><div style="font-size:24px;font-weight:700">8</div></div>
              <div><div style="font-size:11px;opacity:.85">待支付金额</div><div style="font-size:24px;font-weight:700">¥ 6.2万</div></div>
            </div>
          </div>
          <div class="card">
            <div class="hd">待办队列</div>
            <div class="fx between mb10" style="font-size:13px"><span>预付单审批 · 5 笔</span><span class="money">¥ 1.2万</span></div>
            <div class="fx between mb10" style="font-size:13px"><span>结算单待支付 · 3 笔</span><span class="money">¥ 5.0万</span></div>
            <div class="fx between" style="font-size:13px"><span>报销单 · 2 笔</span><span class="t3">来自司机垫付</span></div>
          </div>""",
        tabbar("a_home", {"approve": "8"})
    ), ["财务首屏突出金额与审批队列，入口直达费用工作台。"]))
    boards.append(board("s4", "04", "车队长角色 · 首屏差异", "P0", phone(
        "工作台",
        """          <div class="hero pad-b">
            <div style="font-size:18px;font-weight:600">陈队 · 车队长</div>
            <div class="kpis mt16">
              <div class="kpi"><div class="v">9</div><div class="k">在途车辆</div></div>
              <div class="kpi"><div class="v">3</div><div class="k">待派司机</div></div>
              <div class="kpi"><div class="v" style="color:#fde68a">4</div><div class="k">证照预警</div></div>
              <div class="kpi"><div class="v">1</div><div class="k">请假待批</div></div>
            </div>
          </div>
          <div class="card">
            <div class="quick">
              <div class="q"><div class="ib"><svg class="ico"><use href="#i-truck"></use></svg></div>派车</div>
              <div class="q"><div class="ib"><svg class="ico"><use href="#i-car"></use></svg></div>运力</div>
              <div class="q"><div class="ib warn"><svg class="ico"><use href="#i-shield"></use></svg></div>证照</div>
              <div class="q"><div class="ib"><svg class="ico"><use href="#i-phone"></use></svg></div>催司机</div>
            </div>
          </div>""",
        tabbar("a_home")
    ), ["车队长关注运力状态、证照与催办，不看财务利润。"]))
    boards.append(board("s5", "05", "无待办空态", "P0", phone(
        "工作台",
        """          <div class="hero pad-b"><div style="font-size:18px;font-weight:600">李敏 · 调度</div></div>
          <div class="empty">
            <div class="t">此刻没有待办</div>
            <div class="d">有新计划待确认、任务待派或审批时，会显示在这里</div>
          </div>
          <div class="card">
            <div class="hd">快捷入口</div>
            <div class="quick">
              <div class="q"><div class="ib"><svg class="ico"><use href="#i-truck"></use></svg></div>调度台</div>
              <div class="q"><div class="ib"><svg class="ico"><use href="#i-nav"></use></svg></div>在途</div>
              <div class="q"><div class="ib"><svg class="ico"><use href="#i-list"></use></svg></div>计划</div>
              <div class="q"><div class="ib"><svg class="ico"><use href="#i-chart"></use></svg></div>看板</div>
            </div>
          </div>""",
        tabbar("a_home")
    ), ["空态仍保留快捷入口，避免「没事做了」的死页。"]))

    return page(
        "02 工作台首页 · 后台人员微信小程序", "admin", "后台人员微信小程序", "02",
        "工作台首页",
        [("p0", "P0 核心")],
        "同一套工作台，按角色换卡片。调度催派、老板看数、财务批钱、车队长管车——首屏只放各自最痛的三件事。",
        [("覆盖屏数", "5 屏"), ("对齐", "PC 工作台 + attention-metrics")],
        [("s1", "调度", "调度"), ("s2", "老板", "老板"), ("s3", "财务", "财务"), ("s4", "车队长", "车队长"), ("s5", "空态", "空态")],
        "\n".join(boards),
    )


def gen_admin_03():
    boards = []
    boards.append(board("s1", "01", "计划中心 · 状态池", "P0", phone(
        "计划中心",
        """          <div class="tabs">
            <div class="tab on">待确认</div><div class="tab">待调度</div><div class="tab">调度中</div><div class="tab">运输中</div><div class="tab">更多</div>
          </div>
          <div class="search"><svg class="ico"><use href="#i-search"></use></svg>计划号 / 客户 / 起终地</div>
          <div class="task">
            <div class="top"><span class="chip warning">待确认</span><span class="no">WB202607280117</span></div>
            <div class="nm" style="font-size:15px">上海安亭 → 合肥庐阳</div>
            <div class="meta"><span>上汽乘用车</span><span>3 台</span><span class="money">¥ 4,800</span></div>
          </div>
          <div class="task">
            <div class="top"><span class="chip warning">待确认</span><span class="no">WB202607280119</span></div>
            <div class="nm" style="font-size:15px">上海安亭 → 合肥包河</div>
            <div class="meta"><span>上汽乘用车</span><span>3 台</span><span class="money">¥ 4,600</span></div>
          </div>"""
    ), ["8 状态池对齐 PC 计划中心；移动端首期聚焦待确认 / 待调度查询与确认。"]))
    boards.append(board("s2", "02", "计划详情与确认", "P0", phone(
        "计划详情",
        """          <div class="pad">
            <div class="card">
              <div class="fx between mb8"><span class="chip warning">待确认</span><span class="no">WB…0117</span></div>
              <div class="strong" style="font-size:16px">上海安亭 → 合肥庐阳</div>
              <div class="t3 mt8" style="font-size:12px">上汽乘用车 · 荣威 D5X · 3 台</div>
              <div class="hr"></div>
              <div class="fx between mb8" style="font-size:13px"><span class="t2">运费</span><span class="money">¥ 4,800</span></div>
              <div class="fx between" style="font-size:13px"><span class="t2">计费状态</span><span>已计算</span></div>
            </div>
            <div class="notice warn" style="margin:0 0 10px;border-radius:8px"><span>确认后不可随意删除。若已锁定请先在电脑端解锁。</span></div>
          </div>""",
        action_bar(("返回", "line"), ("确认计划", "wide"))
    ), [
        '确认文案：「确认后计划进入待调度，确定吗？」Loading：正在确认计划，请稍候…',
    ]))
    boards.append(board("s3", "03", "批量确认", "P0", phone(
        "计划中心",
        """          <div class="pad">
            <div class="notice info" style="border-radius:8px;margin-bottom:10px"><span>已选 3 条待确认计划</span></div>
            <div class="task"><div class="fx g8"><span class="ck on">✓</span><div class="grow"><div class="strong">WB…0117</div><div class="t3">3 台 · ¥4,800</div></div></div></div>
            <div class="task"><div class="fx g8"><span class="ck on">✓</span><div class="grow"><div class="strong">WB…0119</div><div class="t3">3 台 · ¥4,600</div></div></div></div>
            <div class="task"><div class="fx g8"><span class="ck on">✓</span><div class="grow"><div class="strong">WB…0120</div><div class="t3">2 台 · ¥3,100</div></div></div></div>
          </div>""",
        action_bar(("取消", "line"), ("确认 3 条", "wide"))
    ), ["成功提示：「已成功确认 3 条计划」。"]))

    return page(
        "03 计划中心 · 后台人员微信小程序", "admin", "后台人员微信小程序", "03",
        "计划中心",
        [("p0", "P0")],
        "移动端计划中心服务「碎片时间确认」，不做复杂录入与计费重算。",
        [("覆盖屏数", "3 屏"), ("对齐", "PC /operation/waybill")],
        [("s1", "1", "列表"), ("s2", "2", "详情"), ("s3", "3", "批量")],
        "\n".join(boards),
    )


def gen_admin_04():
    boards = []
    boards.append(board("s1", "01", "调度工作台 · 五阶段", "P0", phone(
        "调度工作台",
        """          <div class="kpi-grid" style="grid-template-columns:repeat(5,1fr);gap:4px;padding:10px 8px">
            <div class="kpi" style="padding:8px 4px;text-align:center"><div class="v" style="font-size:16px">2</div><div class="k">待分配</div></div>
            <div class="kpi warn" style="padding:8px 4px;text-align:center"><div class="v" style="font-size:16px">5</div><div class="k">待派车</div></div>
            <div class="kpi" style="padding:8px 4px;text-align:center"><div class="v" style="font-size:16px">3</div><div class="k">待装车</div></div>
            <div class="kpi brand" style="padding:8px 4px;text-align:center"><div class="v" style="font-size:16px">14</div><div class="k">在途</div></div>
            <div class="kpi" style="padding:8px 4px;text-align:center"><div class="v" style="font-size:16px">4</div><div class="k">待签收</div></div>
          </div>
          <div class="tabs"><div class="tab on">待派车</div><div class="tab">待装车</div><div class="tab">在途</div><div class="tab">待签收</div></div>
          <div class="task">
            <div class="top"><span class="chip warning">待派车</span><span class="no">TK…0031</span></div>
            <div class="nm" style="font-size:15px">上海嘉定 → 合肥包河</div>
            <div class="meta"><span>8 台</span><span>计划装车今日 08:30</span></div>
            <div class="item-foot"><span class="t3">未派司机</span><a class="btn xs">派车</a></div>
          </div>""",
        tabbar("a_dispatch")
    ), ["对齐 PC task-workbench 五阶段 KPI。"]))
    boards.append(board("s2", "02", "任务详情（调度视角）", "P0", phone(
        "任务详情",
        """          <div class="banner">
            <div class="top"><span class="stat warning">待派车</span><span class="no">TK…0031</span></div>
            <div class="nm">上海嘉定 → 合肥包河</div>
            <div class="mini">
              <div><div class="k">台数</div><div class="v">8</div></div>
              <div><div class="k">计划数</div><div class="v">3</div></div>
              <div><div class="k">承运</div><div class="v" style="font-size:13px">自有</div></div>
            </div>
          </div>
          <div class="card pull-up">
            <div class="hd">执行进度</div>
            <div class="steps-h mb12">
              <span class="s now">待派</span><span class="s">装车</span><span class="s">在途</span><span class="s">到达</span><span class="s">签收</span>
            </div>
          </div>
          <div class="card"><div class="hd">挂接计划</div><div class="t3" style="font-size:12px">WB…0117 / 0119 / 0120 · 共 8 台</div></div>""",
        action_bar(("撤回", "line"), ("派车", "wide"))
    ), ["调度详情强调派车与干预，不展示司机专属接单按钮。"]))
    boards.append(board("s3", "03", "派车面板", "P0", phone(
        "派车",
        """          <div class="pad">
            <div class="search"><svg class="ico"><use href="#i-search"></use></svg>司机 / 车牌 / 运力组</div>
            <div class="card" style="border:1.5px solid var(--brand)">
              <div class="fx between"><span class="strong">王建军 · 沪B·D7392</span><span class="chip success">空闲</span></div>
              <div class="t3 mt6" style="font-size:12px">板车 · 今日无冲突</div>
            </div>
            <div class="card">
              <div class="fx between"><span class="strong">周强 · 沪A·K2281</span><span class="chip warning">冲突</span></div>
              <div class="t3 mt6" style="font-size:12px;color:var(--warning)">已有在途任务 TK…0028，预计明日 10:00 卸完</div>
            </div>
          </div>""",
        action_bar(("确认派给王建军", "wide"))
    ), ["冲突运力可派但需二次确认「该司机仍有在途任务，确定改派/加派？」"]))
    boards.append(board("s4", "04", "改派确认", "P0", phone(
        "改派",
        """          <div class="mask center">
            <div class="dialog">
              <div class="t">确认改派？</div>
              <div class="d">原司机王建军将收到调令取消通知。新司机周强需重新接单。</div>
              <div class="af"><a class="btn line wide">取消</a><a class="btn wide">确认改派</a></div>
            </div>
          </div>
          <div class="pad" style="filter:blur(1px);opacity:.4"><div class="card">任务详情占位</div></div>"""
    ), ["改派成功：「已改派给周强，正在通知双方」。"]))
    boards.append(board("s5", "05", "撤回任务", "P0", phone(
        "任务详情",
        """          <div class="mask center">
            <div class="dialog">
              <div class="t">撤回这趟任务？</div>
              <div class="d">撤回后任务回到待派车，司机端调令将失效。已产生的费用单需财务单独处理。</div>
              <div class="af"><a class="btn line wide">再想想</a><a class="btn danger wide">确认撤回</a></div>
            </div>
          </div>
          <div class="pad" style="filter:blur(1px);opacity:.4"><div class="card">占位</div></div>"""
    ), ["危险操作用危险色按钮，并说清对司机与费用的影响。"]))

    return page(
        "04 调度工作台 · 后台人员微信小程序", "admin", "后台人员微信小程序", "04",
        "调度工作台",
        [("p0", "P0 最高频")],
        "调度的手机战场：看池子、派车、改派、撤回。配载建单仍留在 PC。",
        [("覆盖屏数", "5 屏"), ("对齐", "PC /operation/task-workbench")],
        [("s1", "1", "五阶段"), ("s2", "2", "详情"), ("s3", "3", "派车"), ("s4", "4", "改派"), ("s5", "5", "撤回")],
        "\n".join(boards),
    )


def gen_admin_05():
    boards = []
    boards.append(board("s1", "01", "代确认装车", "P0", phone(
        "代司机操作",
        """          <div class="pad">
            <div class="notice warn" style="border-radius:8px;margin-bottom:10px"><span>司机王建军 30 分钟未响应装车确认。你可代为确认，操作将记入日志。</span></div>
            <div class="card">
              <div class="strong">TK…0031 · 待装车</div>
              <div class="t3 mt6">上海嘉定 · 计划 08:30</div>
            </div>
            <div class="field"><div class="lab">代操作原因 <span class="req">*</span></div><div class="ta">司机手机没电，已电话确认已装完</div></div>
          </div>""",
        action_bar(("取消", "line"), ("代确认装车", "wide"))
    ), ["代操作必须填原因；PC/小程序共用状态机动作。"]))
    boards.append(board("s2", "02", "催办司机", "P0", phone(
        "催办",
        """          <div class="pad">
            <div class="card">
              <div class="fx g10">
                <div class="ava sm">王</div>
                <div class="grow"><div class="strong">王建军</div><div class="t3">139****3308 · 待接收调令</div></div>
                <a class="btn soft xs"><svg class="ico"><use href="#i-phone"></use></svg></a>
              </div>
            </div>
            <div class="card">
              <div class="hd">催办方式</div>
              <div class="cell" style="padding:10px 0;border:none"><div class="k">发送订阅消息</div><span class="chip primary">推荐</span></div>
              <div class="cell" style="padding:10px 0;border:none"><div class="k">短信提醒</div></div>
            </div>
          </div>""",
        action_bar(("发送催办", "wide"))
    ), ["一键拨号用 <code>tel:</code>；订阅消息需司机已授权。"]))
    boards.append(board("s3", "03", "强制取消 / 关闭", "P0", phone(
        "任务详情",
        """          <div class="mask center">
            <div class="dialog">
              <div class="t">强制取消任务？</div>
              <div class="d">取消后不可恢复。挂接计划将回到待调度，请确认客户侧已沟通。</div>
              <div class="af"><a class="btn line wide">返回</a><a class="btn danger wide">强制取消</a></div>
            </div>
          </div>
          <div class="pad" style="opacity:.35;filter:blur(1px)"><div class="card">任务</div></div>"""
    ), ["高风险操作仅对有权限角色展示。"]))

    return page(
        "05 任务执行干预 · 后台人员微信小程序", "admin", "后台人员微信小程序", "05",
        "任务执行干预",
        [("p0", "P0")],
        "司机失联时，调度要能代推状态、催办、紧急取消——这是移动端不可缺的补位能力。",
        [("覆盖屏数", "3 屏"), ("角色", "调度 / 车队长")],
        [("s1", "1", "代操作"), ("s2", "2", "催办"), ("s3", "3", "强制取消")],
        "\n".join(boards),
    )


def gen_admin_06():
    boards = []
    boards.append(board("s1", "01", "在途车辆分布", "P0", phone(
        "在途监控",
        """          <div class="map" style="height:220px;margin:0;border-radius:0">
            <div class="hint">在途 14 辆 · 异常 2</div>
            <div class="mrk" style="left:40%;top:50%"><span class="bub"><svg class="ico"><use href="#i-truck"></use></svg>沪B·D7392</span></div>
            <div class="mrk r" style="left:62%;top:36%"><span class="bub">异常</span></div>
          </div>
          <div class="task" style="margin-top:10px">
            <div class="top"><span class="chip danger">故障</span><span class="no">沪B·D7392</span></div>
            <div class="nm" style="font-size:14px">王建军 · 爆胎靠边</div>
            <div class="meta"><span>沪陕 K326</span><span>15:22 上报</span></div>
          </div>"""
    ), ["地图为示意；异常卡对接驾驶员模块 08。"]))
    boards.append(board("s2", "02", "单车轨迹", "P1", phone(
        "车辆轨迹",
        """          <div class="pad">
            <div class="fx between mb10"><span class="strong">沪B·D7392 · 王建军</span><span class="chip info">在途</span></div>
            <div class="map" style="margin:0 0 10px;height:180px">
              <div class="hint">已行驶 312 km · 更新于 1 分钟前</div>
            </div>
            <div class="card" style="margin:0">
              <div class="fx between mb8" style="font-size:13px"><span class="t2">出发</span><span>今日 08:52 上海嘉定</span></div>
              <div class="fx between" style="font-size:13px"><span class="t2">预计到达</span><span>今日 16:30 合肥包河</span></div>
            </div>
          </div>""",
        action_bar(("电话催办", "line"), ("处理异常", "wide"))
    ), ['<span class="flag">P1</span>依赖轨迹上报；无轨迹时仅展示最近打卡点。']))
    boards.append(board("s3", "03", "超时预警处理", "P0", phone(
        "超时预警",
        """          <div class="pad">
            <div class="card">
              <div class="chip warning mb8">装车超时</div>
              <div class="strong">TK…0028 · 周强</div>
              <div class="t3 mt8" style="font-size:12px">计划装车 14:00，已超时 45 分钟仍未确认装车</div>
            </div>
            <div class="card">
              <div class="hd">建议处理</div>
              <a class="btn soft block mb8">催办司机</a>
              <a class="btn soft block mb8">代确认装车</a>
              <a class="btn line block">改派其他运力</a>
            </div>
          </div>"""
    ), ["预警规则：计划装车/到达时间超时未推进状态。"]))

    return page(
        "06 在途监控 · 后台人员微信小程序", "admin", "后台人员微信小程序", "06",
        "在途监控",
        [("p0", "列表/预警 P0"), ("p1", "轨迹 P1")],
        "让调度在手机上完成「看车 → 发现异常 → 催办/代操作」闭环。",
        [("覆盖屏数", "3 屏"), ("对齐", "PC /operation/tracking")],
        [("s1", "1", "分布"), ("s2", "2", "轨迹"), ("s3", "3", "超时")],
        "\n".join(boards),
    )


def gen_admin_07():
    boards = []
    boards.append(board("s1", "01", "待回单列表", "P0", phone(
        "回单签收",
        """          <div class="tabs"><div class="tab on">待回单</div><div class="tab">待签收</div><div class="tab">已完成</div></div>
          <div class="task">
            <div class="top"><span class="chip info">已签收待回单</span><span class="no">WB…0117</span></div>
            <div class="nm" style="font-size:14px">上海 → 合肥庐阳 · 3 台</div>
            <div class="meta"><span>司机已签收</span><span>回单 2 张</span></div>
          </div>
          <div class="task">
            <div class="top"><span class="chip warning">待签收</span><span class="no">TK…0031</span></div>
            <div class="nm" style="font-size:14px">上海 → 合肥包河 · 8 台</div>
            <div class="meta"><span>已到达</span><span>签收 2/8</span></div>
          </div>"""
    ), ["区分运单回单（企业确认）与任务签收（司机/代签）。"]))
    boards.append(board("s2", "02", "回单凭证预览与确认", "P0", phone(
        "确认回单",
        """          <div class="pad">
            <div class="card">
              <div class="strong">WB…0117</div>
              <div class="t3 mt6">上汽乘用车 · 3 台已签收</div>
            </div>
            <div class="card">
              <div class="hd">司机上传凭证</div>
              <div class="photos"><div class="slot filled">1</div><div class="slot filled">2</div><div class="slot filled">3</div></div>
            </div>
          </div>""",
        action_bar(("驳回补传", "line"), ("确认回单", "wide"))
    ), ["确认回单：运单 5→6。驳回需填原因，司机端收到补传通知。"]))
    boards.append(board("s3", "03", "批量确认回单", "P0", phone(
        "回单签收",
        """          <div class="pad">
            <div class="notice info" style="border-radius:8px;margin-bottom:10px"><span>已选 4 条，凭证齐全</span></div>
            <div class="task"><div class="fx g8"><span class="ck on">✓</span><div class="strong">WB…0117</div></div></div>
            <div class="task"><div class="fx g8"><span class="ck on">✓</span><div class="strong">WB…0119</div></div></div>
          </div>""",
        action_bar(("批量确认回单", "wide"))
    ), ["成功：「已确认 4 条回单」。"]))

    return page(
        "07 回单与签收 · 后台人员微信小程序", "admin", "后台人员微信小程序", "07",
        "回单与签收",
        [("p0", "P0")],
        "司机签收之后，企业还要完成运单回单确认。移动端支持抽空批量过一遍。",
        [("覆盖屏数", "3 屏"), ("对齐", "PC /operation/receipt")],
        [("s1", "1", "列表"), ("s2", "2", "确认"), ("s3", "3", "批量")],
        "\n".join(boards),
    )


def gen_admin_08():
    boards = []
    boards.append(board("s1", "01", "费用工作台", "P0", phone(
        "费用工作台",
        """          <div class="kpi-grid">
            <div class="kpi warn"><div class="k">待审批</div><div class="v">8</div></div>
            <div class="kpi brand"><div class="k">待支付</div><div class="v sm">¥6.2万</div></div>
          </div>
          <div class="tabs"><div class="tab">草稿</div><div class="tab on">待审批</div><div class="tab">待支付</div><div class="tab">已支付</div></div>
          <div class="task">
            <div class="top"><span class="chip warning">待审批</span><span class="chip primary">预付单</span></div>
            <div class="fx between"><span class="strong">TK…0031 · 王建军</span><span class="money">¥ 800</span></div>
          </div>
          <div class="task">
            <div class="top"><span class="chip warning">待审批</span><span class="chip primary">结算单</span></div>
            <div class="fx between"><span class="strong">TK…0018 · 周强</span><span class="money">¥ 2,100</span></div>
          </div>"""
    ), ["对齐 PC task-finance-workbench。"]))
    boards.append(board("s2", "02", "费用单详情 · 审批", "P0", phone(
        "费用单详情",
        """          <div class="pad">
            <div class="card" style="text-align:center">
              <div class="chip warning mb8">待审批</div>
              <div class="money" style="font-size:28px">¥ 800.00</div>
              <div class="t3 mt6">预付单 · 王建军</div>
            </div>
            <div class="card">
              <div class="cell" style="padding:8px 0;border:none"><div class="k">任务</div><div class="v">TK…0031</div></div>
              <div class="cell" style="padding:8px 0;border:none"><div class="k">线路</div><div class="v">上海→合肥</div></div>
              <div class="cell" style="padding:8px 0;border:none"><div class="k">收款账户</div><div class="v">工行尾号 6682</div></div>
            </div>
          </div>""",
        action_bar(("驳回", "line"), ("通过", "wide"))
    ), ["通过：「审批通过，等待支付」。"]))
    boards.append(board("s3", "03", "驳回意见", "P0", phone(
        "驳回",
        """          <div class="mask bottom">
            <div class="sheet">
              <div class="handle"></div>
              <div class="strong mb8">驳回原因（必填）</div>
              <div class="ta" style="margin-bottom:12px">预付比例超出政策，请调整为不超过 30% 后重提。</div>
              <a class="btn danger block">确认驳回</a>
            </div>
          </div>
          <div class="pad" style="opacity:.4;filter:blur(1px)"><div class="card">详情</div></div>"""
    ), ["驳回意见必填，写给调度/申请人看。"]))
    boards.append(board("s4", "04", "标记已支付", "P0", phone(
        "标记支付",
        """          <div class="pad">
            <div class="card"><div class="money" style="font-size:22px">¥ 2,100.00</div><div class="t3 mt6">结算单 · 周强</div></div>
            <div class="field"><div class="lab">支付方式</div><div class="inp">银行转账</div></div>
            <div class="field"><div class="lab">支付凭证</div><div class="photos"><div class="slot filled">回单</div><div class="slot"><span class="add">+</span></div></div></div>
            <div class="field"><div class="lab">备注</div><div class="inp ph">选填</div></div>
          </div>""",
        action_bar(("确认已支付", "wide"))
    ), ["Loading：正在登记支付，请稍候… 成功：已标记支付 ¥2,100.00"]))
    boards.append(board("s5", "05", "批量审批", "P0", phone(
        "费用工作台",
        """          <div class="pad">
            <div class="notice info" style="border-radius:8px;margin-bottom:10px"><span>已选 5 笔预付单，合计 ¥ 4,600</span></div>
            <div class="task"><div class="fx g8"><span class="ck on">✓</span><div class="grow fx between"><span>TK…0031</span><span class="money">¥800</span></div></div></div>
            <div class="task"><div class="fx g8"><span class="ck on">✓</span><div class="grow fx between"><span>TK…0029</span><span class="money">¥900</span></div></div></div>
          </div>""",
        action_bar(("批量驳回", "line"), ("批量通过", "wide"))
    ), ["批量仅允许同一状态；混选提示「请只选待审批的单据」。"]))

    return page(
        "08 费用审批与支付 · 后台人员微信小程序", "admin", "后台人员微信小程序", "08",
        "费用审批与支付",
        [("p0", "P0 财务高频")],
        "财务在手机上要能批、能付、能驳。不做成本政策配置。",
        [("覆盖屏数", "5 屏"), ("对齐", "PC 费用工作台")],
        [("s1", "1", "工作台"), ("s2", "2", "详情"), ("s3", "3", "驳回"), ("s4", "4", "支付"), ("s5", "5", "批量")],
        "\n".join(boards),
    )


def gen_admin_09():
    boards = []
    boards.append(board("s1", "01", "我的待办", "P0", phone(
        "审批中心",
        """          <div class="tabs"><div class="tab on">待办</div><div class="tab">我申请的</div><div class="tab">已处理</div></div>
          <div class="task">
            <div class="top"><span class="chip warning">待审批</span><span class="chip">费用</span></div>
            <div class="nm" style="font-size:14px">预付单 ¥800 · 王建军</div>
            <div class="meta"><span>李敏 提交</span><span>1 小时前</span></div>
          </div>
          <div class="task">
            <div class="top"><span class="chip warning">待审批</span><span class="chip">运力</span></div>
            <div class="nm" style="font-size:14px">社会运力准入 · 张伟</div>
            <div class="meta"><span>车队长提交</span><span>今天 09:20</span></div>
          </div>""",
        tabbar("a_approve", {"approve": "2"})
    ), ["聚合费用审批、运力审批、请假等待办。"]))
    boards.append(board("s2", "02", "审批详情时间轴", "P0", phone(
        "审批详情",
        """          <div class="pad">
            <div class="card">
              <div class="chip warning mb8">待你审批</div>
              <div class="strong" style="font-size:16px">预付单 ¥800</div>
              <div class="t3 mt6">TK…0031 · 王建军 · 上海→合肥</div>
            </div>
            <div class="card">
              <div class="hd">流程</div>
              <div class="steps">
                <div class="s done"><div class="t">李敏 提交</div><div class="d">今日 10:02</div></div>
                <div class="s now"><div class="t">财务赵倩 审批</div><div class="d">处理中 · 就是你</div></div>
                <div class="s"><div class="t">出纳支付</div><div class="d">待完成</div></div>
              </div>
            </div>
          </div>""",
        action_bar(("转办", "line"), ("驳回", "line"), ("通过", "wide"))
    ), ["时间轴展示已走与当前节点。"]))
    boards.append(board("s3", "03", "转办", "P0", phone(
        "转办",
        """          <div class="pad">
            <div class="field"><div class="lab">转给</div><div class="inp">王主管（财务主管）</div></div>
            <div class="field"><div class="lab">说明</div><div class="ta">金额较大，请主管复核</div></div>
          </div>""",
        action_bar(("确认转办", "wide"))
    ), ["转办后待办从我的列表消失，进入对方待办。"]))
    boards.append(board("s4", "04", "我申请的", "P0", phone(
        "审批中心",
        """          <div class="tabs"><div class="tab">待办</div><div class="tab on">我申请的</div><div class="tab">已处理</div></div>
          <div class="task">
            <div class="top"><span class="chip info">审批中</span><span class="chip">费用</span></div>
            <div class="nm" style="font-size:14px">结算单 ¥2,100</div>
            <div class="meta"><span>当前：财务审批</span><span>昨天提交</span></div>
          </div>
          <div class="task">
            <div class="top"><span class="chip success">已通过</span><span class="chip">运力</span></div>
            <div class="nm" style="font-size:14px">社会运力 · 李强</div>
          </div>"""
    ), ["申请人可看进度，不能替审批人点通过。"]))
    boards.append(board("s5", "05", "发起申请入口", "P0", phone(
        "发起申请",
        """          <div class="pad">
            <div class="t3 mb12" style="font-size:12px">常用申请</div>
            <div class="cells" style="margin:0">
              <div class="cell"><div class="ib">¥</div><div class="k">费用单审批</div><span class="caret">›</span></div>
              <div class="cell"><div class="ib"><svg class="ico"><use href="#i-car"></use></svg></div><div class="k">运力准入</div><span class="caret">›</span></div>
              <div class="cell"><div class="ib"><svg class="ico"><use href="#i-calendar"></use></svg></div><div class="k">请假（代提）</div><span class="caret">›</span></div>
            </div>
            <div class="notice info" style="border-radius:8px;margin-top:12px"><span>复杂审批流请在电脑端发起。手机端仅提供高频入口。</span></div>
          </div>"""
    ), ["移动端发起保持克制，避免变成第二套 PC。"]))

    return page(
        "09 审批中心 · 后台人员微信小程序", "admin", "后台人员微信小程序", "09",
        "审批中心",
        [("p0", "P0")],
        "跨角色的待办收件箱。批完即走，不在手机上设计流程。",
        [("覆盖屏数", "5 屏"), ("对齐", "PC /approval/*")],
        [("s1", "1", "待办"), ("s2", "2", "详情"), ("s3", "3", "转办"), ("s4", "4", "我申请的"), ("s5", "5", "发起")],
        "\n".join(boards),
    )


def gen_admin_10():
    boards = []
    boards.append(board("s1", "01", "经营 KPI 总览", "P0", phone(
        "经营看板",
        """          <div class="chips" style="background:#fff;margin:0;border-bottom:1px solid var(--line)"><div class="chip on">本月</div><div class="chip">本季</div><div class="chip">本年</div></div>
          <div class="kpi-grid">
            <div class="kpi"><div class="k">运输单量</div><div class="v">128</div></div>
            <div class="kpi"><div class="k">运费收入</div><div class="v sm">¥286万</div></div>
            <div class="kpi"><div class="k">运输成本</div><div class="v sm">¥245万</div></div>
            <div class="kpi brand"><div class="k">毛利</div><div class="v sm">¥41万</div></div>
          </div>
          <div class="card">
            <div class="hd">运费趋势</div>
            <div class="chart-bars">
              <div class="bar" style="height:45%"><span class="lbl">2月</span></div>
              <div class="bar" style="height:60%"><span class="lbl">3月</span></div>
              <div class="bar" style="height:52%"><span class="lbl">4月</span></div>
              <div class="bar" style="height:75%"><span class="lbl">5月</span></div>
              <div class="bar" style="height:70%"><span class="lbl">6月</span></div>
              <div class="bar" style="height:90%"><span class="lbl">7月</span></div>
            </div>
          </div>"""
    ), ["对齐 PC 经营驾驶舱摘要，不做复杂下钻。"]))
    boards.append(board("s2", "02", "客户排行", "P0", phone(
        "客户排行",
        """          <div class="pad">
            <div class="card">
              <div class="fx between mb12" style="font-size:13px"><span class="strong">1. 上汽乘用车</span><span class="money">¥ 86万</span></div>
              <div class="fx between mb12" style="font-size:13px"><span class="strong">2. 奇瑞商用</span><span class="money">¥ 52万</span></div>
              <div class="fx between mb12" style="font-size:13px"><span class="strong">3. 江淮经销</span><span class="money">¥ 31万</span></div>
              <div class="fx between" style="font-size:13px"><span>4. 本地二网</span><span>¥ 18万</span></div>
            </div>
          </div>"""
    ), ["按运费收入排序；点击不进入复杂客户档案编辑。"]))
    boards.append(board("s3", "03", "线路利润", "P0", phone(
        "线路利润",
        """          <div class="pad">
            <div class="task">
              <div class="nm" style="font-size:14px">上海 → 合肥</div>
              <div class="meta"><span>32 单</span><span class="green">毛利 18%</span></div>
            </div>
            <div class="task">
              <div class="nm" style="font-size:14px">上海 → 南京</div>
              <div class="meta"><span>21 单</span><span class="green">毛利 15%</span></div>
            </div>
            <div class="task">
              <div class="nm" style="font-size:14px">杭州 → 武汉</div>
              <div class="meta"><span>9 单</span><span class="err">毛利 6%</span></div>
            </div>
            <div class="notice info" style="border-radius:8px;margin:0"><span>应收/对账/开票能力在电脑端完善前，手机看板仅作经营速览。</span></div>
          </div>"""
    ), ["低毛利线路用红色提示老板关注。"]))

    return page(
        "10 经营看板 · 后台人员微信小程序", "admin", "后台人员微信小程序", "10",
        "经营看板",
        [("p0", "P0 老板视角")],
        "老板打开手机只问：这个月赚没赚、哪条线在亏。看板回答这两个问题即可。",
        [("覆盖屏数", "3 屏"), ("对齐", "PC /insight/cockpit")],
        [("s1", "1", "KPI"), ("s2", "2", "客户"), ("s3", "3", "线路")],
        "\n".join(boards),
    )


def gen_admin_11():
    boards = []
    boards.append(board("s1", "01", "运力列表（只读）", "P0", phone(
        "运力查询",
        """          <div class="search"><svg class="ico"><use href="#i-search"></use></svg>司机 / 车牌</div>
          <div class="task">
            <div class="top"><span class="chip success">空闲</span><span class="no">沪B·D7392</span></div>
            <div class="nm" style="font-size:14px">王建军 · 板车</div>
            <div class="meta"><span>自有</span><span class="chip warning">证照 28 天到期</span></div>
          </div>
          <div class="task">
            <div class="top"><span class="chip info">在途</span><span class="no">沪A·K2281</span></div>
            <div class="nm" style="font-size:14px">周强 · 板车</div>
            <div class="meta"><span>自有</span><span>预计明日卸完</span></div>
          </div>"""
    ), ["只读查询 + 一键拨号；新建/解绑留在 PC。"]))
    boards.append(board("s2", "02", "司机详情拨号", "P0", phone(
        "司机详情",
        """          <div class="pad">
            <div class="card">
              <div class="fx g10">
                <div class="ava">王</div>
                <div class="grow">
                  <div class="strong" style="font-size:16px">王建军</div>
                  <div class="t3 mt4">139****3308 · 主驾</div>
                </div>
                <a class="btn soft"><svg class="ico"><use href="#i-phone"></use></svg></a>
              </div>
            </div>
            <div class="card">
              <div class="cell" style="padding:8px 0;border:none"><div class="k">车辆</div><div class="v">沪B·D7392</div></div>
              <div class="cell" style="padding:8px 0;border:none"><div class="k">状态</div><div class="v">在途</div></div>
              <div class="cell" style="padding:8px 0;border:none"><div class="k">驾驶证</div><div class="v err">28 天后到期</div></div>
            </div>
          </div>"""
    ), ["点击电话直接拨号，是车队长最高频动作。"]))
    boards.append(board("s3", "03", "客户 / 承运商查询", "P0", phone(
        "客商查询",
        """          <div class="tabs"><div class="tab on">客户</div><div class="tab">承运商</div></div>
          <div class="search"><svg class="ico"><use href="#i-search"></use></svg>名称 / 联系人</div>
          <div class="task">
            <div class="nm" style="font-size:14px">上汽乘用车</div>
            <div class="meta"><span>联系人 刘工</span><span>本月 32 单</span></div>
          </div>
          <div class="task">
            <div class="nm" style="font-size:14px">奇瑞商用</div>
            <div class="meta"><span>联系人 陈经理</span><span>本月 18 单</span></div>
          </div>"""
    ), ["只读；合同与价格策略不在移动端维护。"]))

    return page(
        "11 资源与客商查询 · 后台人员微信小程序", "admin", "后台人员微信小程序", "11",
        "资源与客商查询",
        [("p0", "只读 P0")],
        "查得到、打得通，不在手机上改主数据。",
        [("覆盖屏数", "3 屏")],
        [("s1", "1", "运力"), ("s2", "2", "司机"), ("s3", "3", "客商")],
        "\n".join(boards),
    )


def gen_admin_12():
    boards = []
    boards.append(board("s1", "01", "消息中心", "P1", phone(
        "消息",
        """          <div class="tabs"><div class="tab on">全部</div><div class="tab">审批</div><div class="tab">调度</div><div class="tab">资金</div><div class="tab">系统</div></div>
          <div class="cells" style="margin-top:10px">
            <div class="cell">
              <div class="ib" style="background:var(--warning-soft);color:#b45309"><svg class="ico"><use href="#i-bell"></use></svg></div>
              <div class="grow">
                <div class="strong" style="font-size:14px">费用单待你审批</div>
                <div class="t3" style="font-size:12px;margin-top:3px">预付 ¥800 · 王建军</div>
              </div>
            </div>
            <div class="cell">
              <div class="ib" style="background:var(--danger-soft);color:var(--danger)"><svg class="ico"><use href="#i-warn"></use></svg></div>
              <div class="grow">
                <div class="strong" style="font-size:14px">在途异常：爆胎</div>
                <div class="t3" style="font-size:12px;margin-top:3px">沪B·D7392 · 王建军</div>
              </div>
            </div>
          </div>"""
    ), ['<span class="flag">P1</span>订阅消息 + 站内信；点击进对应业务页。']))
    boards.append(board("s2", "02", "我的", "P0", phone(
        "我的",
        """          <div class="hero pad-b">
            <div class="fx g10">
              <div class="ava">李</div>
              <div>
                <div style="font-size:18px;font-weight:600">李敏</div>
                <div style="font-size:12px;opacity:.9;margin-top:4px">调度 · 皖通汽车物流</div>
              </div>
            </div>
          </div>
          <div class="cells">
            <div class="cell"><div class="k">个人信息</div><span class="caret">›</span></div>
            <div class="cell"><div class="k">切换企业</div><div class="v">皖通</div><span class="caret">›</span></div>
            <div class="cell"><div class="k">角色与权限说明</div><span class="caret">›</span></div>
            <div class="cell"><div class="k">修改密码</div><span class="caret">›</span></div>
            <div class="cell"><div class="k">帮助与反馈</div><span class="caret">›</span></div>
          </div>
          <a class="btn line block" style="margin:16px 12px;color:var(--danger);border-color:#fecaca">退出登录</a>""",
        tabbar("a_profile")
    ), ["展示当前角色，帮助用户理解「为什么我看不到某入口」。"]))
    boards.append(board("s3", "03", "角色权限说明", "P0", phone(
        "我的权限",
        """          <div class="pad">
            <div class="card">
              <div class="strong mb8">当前角色：调度</div>
              <div class="t3" style="font-size:12px;line-height:1.7">
                可以：确认计划、派车改派、在途催办、代操作、查看运力<br/>
                不可以：费用支付、成本政策、企业配置<br/>
                需要这些能力请在电脑端联系管理员开通。
              </div>
            </div>
          </div>"""
    ), ["用白话说明权限边界，减少「小程序坏了」的误报。"]))

    return page(
        "12 消息与我的 · 后台人员微信小程序", "admin", "后台人员微信小程序", "12",
        "消息与我的",
        [("p0", "我的 P0"), ("p1", "消息 P1")],
        "消息是移动办公的触达层；我的页解决身份、企业与权限认知。",
        [("覆盖屏数", "3 屏")],
        [("s1", "1", "消息"), ("s2", "2", "我的"), ("s3", "3", "权限说明")],
        "\n".join(boards),
    )


def main():
    jobs = [
        (DRIVER / "07-位置与导航.html", gen_driver_07),
        (DRIVER / "08-异常上报.html", gen_driver_08),
        (DRIVER / "09-收入与资金.html", gen_driver_09),
        (DRIVER / "10-车辆与证照.html", gen_driver_10),
        (DRIVER / "11-油卡与维修.html", gen_driver_11),
        (DRIVER / "12-排班与绩效.html", gen_driver_12),
        (DRIVER / "13-消息中心.html", gen_driver_13),
        (DRIVER / "14-我的与设置.html", gen_driver_14),
        (ADMIN / "01-登录与企业切换.html", gen_admin_01),
        (ADMIN / "02-工作台首页.html", gen_admin_02),
        (ADMIN / "03-计划中心.html", gen_admin_03),
        (ADMIN / "04-调度工作台.html", gen_admin_04),
        (ADMIN / "05-任务执行干预.html", gen_admin_05),
        (ADMIN / "06-在途监控.html", gen_admin_06),
        (ADMIN / "07-回单与签收.html", gen_admin_07),
        (ADMIN / "08-费用审批与支付.html", gen_admin_08),
        (ADMIN / "09-审批中心.html", gen_admin_09),
        (ADMIN / "10-经营看板.html", gen_admin_10),
        (ADMIN / "11-资源与客商查询.html", gen_admin_11),
        (ADMIN / "12-消息与我的.html", gen_admin_12),
    ]
    for path, fn in jobs:
        html = fn()
        path.write_text(html, encoding="utf-8")
        print("OK", path.name, len(html))


if __name__ == "__main__":
    main()
