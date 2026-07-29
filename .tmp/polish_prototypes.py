# -*- coding: utf-8 -*-
"""Add pt-rules sections to prototype modules missing them."""
from pathlib import Path

RULES = {
    "后台人员微信小程序/01-登录与企业切换.html": """
  <div class="pt-rules">
    <h4>登录规则</h4>
    <ul>
      <li>复用租户 PC 账号体系，JWT 含 <code>tenant_code</code>。</li>
      <li>多企业用户登录后必选企业；切换企业重签 token 并清空缓存。</li>
      <li>失败文案：账号或密码不对 / 登录失败，请稍后重试。</li>
    </ul>
  </div>""",
    "后台人员微信小程序/03-计划中心.html": """
  <div class="pt-rules">
    <h4>计划操作规则</h4>
    <ul>
      <li>移动侧以确认/驳回为主，不做批量导入与复杂编辑。</li>
      <li>确认后计划进入待调度池，调度员在模块 04 继续派车。</li>
      <li>API 规划复用 <code>/api/client/waybill/*</code>。</li>
    </ul>
  </div>""",
    "后台人员微信小程序/04-调度工作台.html": """
  <div class="pt-rules">
    <h4>调度池规则</h4>
    <table>
      <tr><th>状态池</th><th>移动可操作</th><th>对齐 PC</th></tr>
      <tr><td>待派车</td><td>派车、改派</td><td>task-workbench</td></tr>
      <tr><td>已派车</td><td>催办司机、查看详情</td><td>模块 05 可代操作</td></tr>
      <tr><td>在途</td><td>跳转模块 06 监控</td><td>tracking</td></tr>
    </table>
  </div>""",
    "后台人员微信小程序/05-任务执行干预.html": """
  <div class="pt-rules">
    <h4>代操作规则</h4>
    <ul>
      <li>调度员可代确认装车/到达，系统留痕「调度代操作」。</li>
      <li>不能代替司机签收或上传回单。</li>
      <li>司机拒单后任务回流模块 04 待派车池（参见驾驶员模块 05）。</li>
    </ul>
  </div>""",
    "后台人员微信小程序/06-在途监控.html": """
  <div class="pt-rules">
    <h4>在途监控规则</h4>
    <ul>
      <li>列表按风险优先：异常 &gt; 超时 &gt; 正常在途。</li>
      <li>支持一键拨打司机电话、查看任务详情。</li>
      <li>异常详情可跳转模块 08/09 或 PC 端处理。</li>
    </ul>
  </div>""",
    "后台人员微信小程序/07-回单与签收.html": """
  <div class="pt-rules">
    <h4>回单闭环</h4>
    <ul>
      <li>司机上传回单见驾驶员模块 06；后台在此审核确认。</li>
      <li>确认回单后运单状态 5→6，与司机 item 签收不同层级。</li>
      <li>API 规划复用 <code>/api/client/receipt/*</code>。</li>
    </ul>
  </div>""",
    "后台人员微信小程序/10-经营看板.html": """
  <div class="pt-rules">
    <h4>看板规则</h4>
    <ul>
      <li>老板/管理层深页；工作台模块 02 仅放摘要 KPI。</li>
      <li>卡片可下钻到明细列表，不在手机端做复杂筛选导出。</li>
      <li>API 规划复用 <code>/api/client/insight/*</code>。</li>
    </ul>
  </div>""",
    "后台人员微信小程序/11-资源与客商查询.html": """
  <div class="pt-rules">
    <h4>只读查询</h4>
    <ul>
      <li>运力、司机、客商均只读，改主数据请回 PC 端。</li>
      <li>支持搜索 + 详情，证照到期项跳转运力证照监控。</li>
    </ul>
  </div>""",
    "后台人员微信小程序/12-消息与我的.html": """
  <div class="pt-rules">
    <h4>消息与权限</h4>
    <ul>
      <li>消息分类：审批 / 调度 / 资金 / 系统；点击直达对应模块。</li>
      <li>「权限说明」用白话解释可见入口，减少误报。</li>
      <li>P1：微信订阅消息 + 站内信并存。</li>
    </ul>
  </div>""",
    "驾驶员微信小程序/07-位置与导航.html": """
  <div class="pt-rules">
    <h4>导航规则</h4>
    <ul>
      <li>P1 增量：调起微信地图导航，不自建路线规划。</li>
      <li>到厂签到可选上报定位，作为辅助凭证。</li>
    </ul>
  </div>""",
    "驾驶员微信小程序/08-异常上报.html": """
  <div class="pt-rules">
    <h4>异常上报</h4>
    <ul>
      <li>P1 增量：结构化类型（车辆/道路/货损/其他）+ 描述 + 照片。</li>
      <li>提交后后台模块 06 在途监控可见，调度可联系处理。</li>
    </ul>
  </div>""",
    "驾驶员微信小程序/10-车辆与证照.html": """
  <div class="pt-rules">
    <h4>车辆证照</h4>
    <ul>
      <li>P0 只读：当前绑定车辆、证照有效期。</li>
      <li>P1：到期前 7/30 天提醒，引导联系车队长更新。</li>
    </ul>
  </div>""",
    "驾驶员微信小程序/11-油卡与维修.html": """
  <div class="pt-rules">
    <h4>油卡与维修（P2 远期）</h4>
    <ul>
      <li>油卡余额只读；报修提交后进入后台审批流。</li>
      <li>接口待定，原型先定交互。</li>
    </ul>
  </div>""",
    "驾驶员微信小程序/12-排班与绩效.html": """
  <div class="pt-rules">
    <h4>排班与绩效（P2 远期）</h4>
    <ul>
      <li>排班日历只读；绩效摘要来自 PC 端统计。</li>
      <li>一期可不开发，原型预留入口。</li>
    </ul>
  </div>""",
    "驾驶员微信小程序/13-消息中心.html": """
  <div class="pt-rules">
    <h4>消息规则</h4>
    <ul>
      <li>分类：调令 / 费用 / 系统；未读 badge 同步 tabBar。</li>
      <li>P1：订阅消息模板 + 小程序内消息列表。</li>
    </ul>
  </div>""",
    "驾驶员微信小程序/14-我的与设置.html": """
  <div class="pt-rules">
    <h4>个人中心</h4>
    <ul>
      <li>白名单可改：紧急联系人、住址、头像；身份证/姓名只读。</li>
      <li>切换企业后清空任务与财务缓存，防数据串租户。</li>
      <li>API：<code>/api/driver/profile/me</code>、<code>/auth/switch-tenant</code>。</li>
    </ul>
  </div>""",
}

root = Path(r"D:\zhitu\prototype\移动端")
for rel, rules_html in RULES.items():
    path = root / rel.replace("/", "\\") if "\\" in str(root) else root / Path(rel)
    path = root / Path(rel)
    if not path.exists():
        print("SKIP missing", path)
        continue
    text = path.read_text(encoding="utf-8")
    if "pt-rules" in text:
        print("SKIP has rules", path.name)
        continue
    if "</main>" not in text:
        print("SKIP no main", path.name)
        continue
    text = text.replace("</main>", rules_html + "\n\n</main>", 1)
    path.write_text(text, encoding="utf-8")
    print("OK", path.name)

print("Done")
