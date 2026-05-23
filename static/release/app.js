(function () {
  const STORAGE_KEY = "renyu.language";
  const state = {
    release: null,
    ops: null,
    canaryConfig: null,
    calendar: null,
    canaryMetrics: null,
    publicGate: null,
    publicStatus: null,
    publicMetrics: null,
    productGate: null,
    productMetrics: null,
    monetizationGate: null,
    monetizationMetrics: null,
    paymentGate: null,
    paymentMetrics: null,
    errors: new Set(),
  };

  const els = {};

  const ids = [
    "releaseGateBadge",
    "releaseStatusSummary",
    "releaseMetricStrip",
    "releaseBlockerList",
    "releaseNextActionList",
    "releasePhasePath",
    "releasePathLinks",
    "opsStatusText",
    "opsStatusMeta",
    "canaryStatusText",
    "canaryStatusMeta",
    "contentCalendarList",
    "phase11CanaryText",
    "phase11CanaryMeta",
    "phase12PublicText",
    "phase12PublicMeta",
    "phase13ProductizationText",
    "phase13ProductizationMeta",
    "phase14MonetizationText",
    "phase14MonetizationMeta",
    "phase15PaymentText",
    "phase15PaymentMeta",
  ];

  const STATUS_LABELS = {
    blocked: { zh: "等待前置门槛", en: "Waiting for prerequisite gate" },
    paused: { zh: "已暂停", en: "Paused" },
    canary: { zh: "灰度开放", en: "Canary open" },
    ready: { zh: "可发布", en: "Ready" },
    ready_for_phase12: { zh: "可进入公开最小可用版", en: "Ready for public build" },
    preview: { zh: "公开预览", en: "Public preview" },
    live: { zh: "公开运行", en: "Public live" },
    experiment: { zh: "实验开放", en: "Experiment open" },
    sandbox: { zh: "支付沙箱", en: "Payment sandbox" },
    draft: { zh: "草稿", en: "Draft" },
    unavailable: { zh: "暂不可用", en: "Unavailable" },
    unknown: { zh: "未知状态", en: "Unknown status" },
  };

  const REASON_LABELS = {
    beta_manual_review_pending: {
      zh: "内测人工复核仍有待处理",
      en: "Beta manual review is still pending",
    },
    beta_safety_blocks_pending: {
      zh: "内测安全阻断仍有待处理",
      en: "Beta safety blockers are still pending",
    },
    expert_review_pending: {
      zh: "专家审校队列尚未清空",
      en: "Expert review queue is not clear yet",
    },
    copyright_blocked_visible: {
      zh: "可见内容仍有版权阻断",
      en: "Visible content still has copyright blockers",
    },
    release_readiness_blocked: {
      zh: "发布准入仍被阻断",
      en: "Launch readiness is still blocked",
    },
    canary_not_active: {
      zh: "灰度阶段尚未开放",
      en: "Canary stage is not active",
    },
    insufficient_canary_sessions: {
      zh: "灰度会话数未达到公开发布门槛",
      en: "Canary session volume has not reached the public launch gate",
    },
    insufficient_returning_testers: {
      zh: "回访测试用户数量不足",
      en: "Returning tester count is below threshold",
    },
    insufficient_feedback: {
      zh: "反馈提交数量不足",
      en: "Feedback volume is below threshold",
    },
    insufficient_share_reports: {
      zh: "分享报告数量不足",
      en: "Share report volume is below threshold",
    },
    high_risk_leak_detected: {
      zh: "检测到高风险输出泄漏",
      en: "High-risk output leak detected",
    },
    hallucination_incident_detected: {
      zh: "检测到事实幻觉事件",
      en: "Hallucination incident detected",
    },
    realtime_tool_bypass_detected: {
      zh: "检测到实时工具绕过事件",
      en: "Realtime tool bypass detected",
    },
    deterministic_promise_detected: {
      zh: "检测到确定性承诺风险",
      en: "Deterministic promise risk detected",
    },
    professional_without_evidence_detected: {
      zh: "检测到缺少证据的专业表述",
      en: "Professional claim without evidence detected",
    },
    public_release_gate_blocked: {
      zh: "公开发布闸门仍未通过",
      en: "Public release gate is still blocked",
    },
    public_launch_not_enabled: {
      zh: "公开发布开关尚未打开",
      en: "Public launch switch is not enabled",
    },
    critical_public_incident: {
      zh: "存在公开阶段关键事件",
      en: "Critical public incident is active",
    },
    public_mvp_not_active: {
      zh: "公开最小可用版尚未开放",
      en: "Public build is not active",
    },
    public_risk_event: {
      zh: "公开阶段存在风险事件",
      en: "Public-stage risk event is active",
    },
    productization_experiment_disabled: {
      zh: "产品化实验开关尚未打开",
      en: "Productization experiment switch is not enabled",
    },
    productization_not_active: {
      zh: "产品化实验尚未开放",
      en: "Productization experiment is not active",
    },
    monetization_experiment_disabled: {
      zh: "商业化实验开关尚未打开",
      en: "Monetization experiment switch is not enabled",
    },
    monetization_not_active: {
      zh: "商业化实验尚未开放",
      en: "Monetization experiment is not active",
    },
    insufficient_monetization_interest: {
      zh: "会员兴趣、权益浏览或权益点击还没有达到沙箱门槛",
      en: "Membership interest, offer views, or offer clicks are below the sandbox gate",
    },
    payment_sandbox_disabled: {
      zh: "支付沙箱开关尚未打开",
      en: "Payment sandbox switch is not enabled",
    },
    forbidden_payment_copy: {
      zh: "支付文案仍含禁用承诺词",
      en: "Payment copy still contains forbidden promise terms",
    },
    risk_or_compliance_block: {
      zh: "风险或合规阻断仍在",
      en: "Risk or compliance blocker is still active",
    },
    risk_or_copyright_block: {
      zh: "风险或版权阻断仍在",
      en: "Risk or copyright blocker is still active",
    },
    return_to_canary_or_review_fix: {
      zh: "回到灰度和审校修复",
      en: "Return to canary and review fixes",
    },
    return_to_public_launch_fix: {
      zh: "回到公开发布修复",
      en: "Return to public launch fixes",
    },
    return_to_productization_fix: {
      zh: "回到产品化修复",
      en: "Return to productization fixes",
    },
    return_to_monetization_fix: {
      zh: "回到商业化修复",
      en: "Return to monetization fixes",
    },
    prepare_public_release: {
      zh: "准备公开最小可用版",
      en: "Prepare public build",
    },
    run_productization_experiment: {
      zh: "运行产品化实验",
      en: "Run productization experiment",
    },
    run_monetization_interest_experiment: {
      zh: "运行商业兴趣实验",
      en: "Run monetization interest experiment",
    },
    run_payment_sandbox_preparation: {
      zh: "运行支付沙箱准备",
      en: "Run payment sandbox preparation",
    },
  };

  const CALENDAR_FALLBACK = [
    {
      id: "CC-001",
      zhColumn: "一分钟懂三传",
      enColumn: "One-minute Three Transmissions",
      zhTitle: "三传为什么是排盘里的时间线",
      enTitle: "Why the three transmissions act as the chart timeline",
    },
    {
      id: "CC-002",
      zhColumn: "天将电台",
      enColumn: "General persona radio",
      zhTitle: "贵人、青龙、天空如何只作象意提示",
      enTitle: "How the generals stay symbolic instead of predictive",
    },
    {
      id: "CC-003",
      zhColumn: "古籍拆读",
      enColumn: "Classical source reading",
      zhTitle: "出处卡怎样变成可审校规则",
      enTitle: "How source cards become reviewable rules",
    },
    {
      id: "CC-004",
      zhColumn: "复盘手账",
      enColumn: "Review notebook",
      zhTitle: "一次合作问题如何记录观察信号",
      enTitle: "How to log observation signals for a collaboration question",
    },
    {
      id: "CC-005",
      zhColumn: "直播问课夜",
      enColumn: "Live question night",
      zhTitle: "低风险文化问答的测试脚本",
      enTitle: "A test script for low-risk cultural questions",
    },
  ];

  const CALENDAR_FALLBACK_BY_ID = Object.fromEntries(CALENDAR_FALLBACK.map((item) => [item.id, item]));

  function currentLanguage() {
    if (document.documentElement?.dataset?.language === "en") {
      return "en";
    }
    try {
      return localStorage.getItem(STORAGE_KEY) === "en" ? "en" : "zh";
    } catch {
      return "zh";
    }
  }

  function copy(zh, en) {
    return currentLanguage() === "en" ? en : zh;
  }

  function numberValue(value) {
    const numeric = Number(value);
    return Number.isFinite(numeric) ? numeric : 0;
  }

  function formatNumber(value) {
    return new Intl.NumberFormat(currentLanguage() === "en" ? "en-US" : "zh-CN").format(numberValue(value));
  }

  function element(id) {
    return els[id] || null;
  }

  function setText(id, value) {
    const target = element(id);
    if (target) {
      target.textContent = value;
    }
  }

  function setHtml(id, value) {
    const target = element(id);
    if (target) {
      target.innerHTML = value;
    }
  }

  function escapeHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function label(map, key, fallback) {
    const safeFallback = fallback || { zh: "未识别的后端状态", en: "Unknown backend state" };
    return (map[key] || safeFallback)[currentLanguage()] || safeFallback.zh;
  }

  function statusLabel(status) {
    return label(STATUS_LABELS, status || "unknown", STATUS_LABELS.unknown);
  }

  function reasonLabel(reason) {
    return label(REASON_LABELS, reason || "unknown");
  }

  function reasonList(reasons) {
    const list = Array.isArray(reasons) ? reasons.filter(Boolean) : [];
    if (!list.length) {
      return [copy("暂无阻断原因", "No active blockers")];
    }
    return list.map(reasonLabel);
  }

  function firstReason(reasons) {
    return reasonList(reasons)[0];
  }

  function gateTone(status) {
    if (["ready", "ready_for_phase12", "preview", "live", "experiment", "sandbox", "canary"].includes(status)) {
      return "ready";
    }
    if (status === "paused") {
      return "paused";
    }
    return "blocked";
  }

  function setChip(id, status) {
    const target = element(id);
    if (!target) {
      return;
    }
    target.classList.remove("ready");
    target.classList.remove("paused");
    target.classList.remove("blocked");
    target.classList.remove("pending");
    target.classList.add(gateTone(status));
    target.textContent = statusLabel(status);
  }

  async function readJson(path, key) {
    try {
      const response = await fetch(path);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      state[key] = await response.json();
    } catch {
      state.errors.add(key);
      state[key] = null;
    }
    render();
  }

  function metric(labelText, value) {
    return `<span><strong>${escapeHtml(formatNumber(value))}</strong>${escapeHtml(labelText)}</span>`;
  }

  function renderOverview() {
    const releaseStatus = state.release?.release_status || "blocked";
    const opsStatus = state.ops?.status || "unknown";
    const publicStatus = state.publicStatus?.launch_status || "unknown";
    const productStatus = state.productGate?.gate_status || "unknown";
    const moneyStatus = state.monetizationGate?.gate_status || "unknown";
    const paymentStatus = state.paymentGate?.gate_status || "unknown";
    const allReasons = [
      ...(state.release?.blocked_reasons || []),
      ...(state.ops?.blocked_reasons || []),
      ...(state.publicGate?.blocked_reasons || []),
      ...(state.publicStatus?.blocked_reasons || []),
      ...(state.productGate?.blocked_reasons || []),
      ...(state.monetizationGate?.blocked_reasons || []),
      ...(state.paymentGate?.blocked_reasons || []),
    ];
    const uniqueReasons = Array.from(new Set(allReasons.filter(Boolean)));
    const topStatus = paymentStatus === "sandbox" ? "sandbox" : releaseStatus === "ready" ? publicStatus : releaseStatus;

    setChip("releaseGateBadge", topStatus);
    setText(
      "releaseStatusSummary",
      copy(
        `真实路径：发布准入为${statusLabel(releaseStatus)}，运维为${statusLabel(opsStatus)}，公开阶段为${statusLabel(publicStatus)}，支付准备为${statusLabel(paymentStatus)}。`,
        `Real path: launch readiness is ${statusLabel(releaseStatus)}, operations are ${statusLabel(opsStatus)}, public stage is ${statusLabel(publicStatus)}, and payment readiness is ${statusLabel(paymentStatus)}.`,
      ),
    );
    setHtml(
      "releaseMetricStrip",
      [
        metric(copy("灰度会话", "canary sessions"), state.canaryMetrics?.session_count),
        metric(copy("公开会话", "public sessions"), state.publicMetrics?.session_count),
        metric(copy("学习访客", "learning visitors"), state.productMetrics?.visitor_count),
        metric(copy("商务线索", "business leads"), state.monetizationMetrics?.business_lead_count),
        metric(copy("沙箱订单", "sandbox orders"), state.paymentMetrics?.order_count),
      ].join(""),
    );
    setHtml(
      "releaseBlockerList",
      reasonList(uniqueReasons)
        .slice(0, 7)
        .map((reason) => `<li>${escapeHtml(reason)}</li>`)
        .join(""),
    );
    const nextActions = [
      state.publicGate?.next_step,
      state.productGate?.next_step,
      state.monetizationGate?.next_step,
      state.paymentGate?.next_step,
    ].filter(Boolean);
    const uniqueActions = nextActions.length
      ? Array.from(new Set(nextActions)).map(reasonLabel)
      : [copy("继续观察现有指标并保持安全边界", "Continue observing current metrics and keep safety boundaries")];
    setHtml(
      "releaseNextActionList",
      uniqueActions
        .slice(0, 5)
        .map((action) => `<li>${escapeHtml(action)}</li>`)
        .join(""),
    );
  }

  function phaseStep(phase, title, status, meta) {
    return `
      <li class="phase-step ${escapeHtml(gateTone(status))}">
        <span>${escapeHtml(phase)}</span>
        <strong>${escapeHtml(title)}</strong>
        <em>${escapeHtml(statusLabel(status))}</em>
        <small>${escapeHtml(meta)}</small>
      </li>`;
  }

  function renderPhasePath() {
    setHtml(
      "releasePhasePath",
      [
        phaseStep(
          copy("阶段 10", "Phase 10"),
          copy("内容日历", "Content calendar"),
          state.calendar ? "ready" : "unknown",
          copy("本地草稿与学习卡关联", "Local drafts and learning-card links"),
        ),
        phaseStep(
          copy("阶段 11", "Phase 11"),
          copy("灰度准入", "Canary access"),
          state.publicGate?.gate_status || "unknown",
          copy(
            `${formatNumber(state.canaryMetrics?.session_count)} 次灰度会话`,
            `${formatNumber(state.canaryMetrics?.session_count)} canary sessions`,
          ),
        ),
        phaseStep(
          copy("阶段 12", "Phase 12"),
          copy("公开最小可用版", "Public build"),
          state.publicStatus?.launch_status || "unknown",
          copy(
            `${formatNumber(state.publicMetrics?.session_count)} 次公开会话`,
            `${formatNumber(state.publicMetrics?.session_count)} public sessions`,
          ),
        ),
        phaseStep(
          copy("阶段 13", "Phase 13"),
          copy("产品化实验", "Productization"),
          state.productGate?.gate_status || "unknown",
          copy(
            `${formatNumber(state.productMetrics?.visitor_count)} 位学习访客`,
            `${formatNumber(state.productMetrics?.visitor_count)} learning visitors`,
          ),
        ),
        phaseStep(
          copy("阶段 14", "Phase 14"),
          copy("商业化实验", "Monetization"),
          state.monetizationGate?.gate_status || "unknown",
          copy(
            `${formatNumber(state.monetizationMetrics?.event_count)} 条兴趣事件`,
            `${formatNumber(state.monetizationMetrics?.event_count)} interest events`,
          ),
        ),
        phaseStep(
          copy("阶段 15", "Phase 15"),
          copy("支付准备", "Payment readiness"),
          state.paymentGate?.gate_status || "unknown",
          copy(
            `${formatNumber(state.paymentMetrics?.order_count)} 个沙箱订单`,
            `${formatNumber(state.paymentMetrics?.order_count)} sandbox orders`,
          ),
        ),
      ].join(""),
    );
  }

  function renderStatusCards() {
    const ops = state.ops || {};
    const canaryGate = ops.canary_gate || {};
    setText(
      "opsStatusText",
      copy(
        `上线闸门为${statusLabel(ops.status)}；${firstReason(ops.blocked_reasons)}。`,
        `Launch gate is ${statusLabel(ops.status)}; ${firstReason(ops.blocked_reasons)}.`,
      ),
    );
    setText(
      "opsStatusMeta",
      copy(
        `审校队列 ${formatNumber(ops.review_queue?.case_count)} 项；受邀测试上限 ${formatNumber(ops.allowed_tester_count)} 人。`,
        `${formatNumber(ops.review_queue?.case_count)} review items; invited tester limit ${formatNumber(ops.allowed_tester_count)}.`,
      ),
    );
    setText(
      "canaryStatusText",
      canaryGate.canary_allowed
        ? copy("专家审校闸门已放行，仍需测试编号或邀请码进入。", "Expert review gate is clear; tester ID or invite code is still required.")
        : copy(`专家审校仍阻断灰度：${firstReason(ops.blocked_reasons)}。`, `Expert review still blocks canary: ${firstReason(ops.blocked_reasons)}.`),
    );
    setText(
      "canaryStatusMeta",
      copy(
        `当前灰度配置已接入真实校验接口；测试上限 ${formatNumber(ops.allowed_tester_count || state.canaryConfig?.tester_user_limit)} 人。`,
        `Current canary config uses the real validation API; tester limit ${formatNumber(ops.allowed_tester_count || state.canaryConfig?.tester_user_limit)}.`,
      ),
    );

    const publicGate = state.publicGate || {};
    setText(
      "phase11CanaryText",
      copy(
        `灰度累计 ${formatNumber(state.canaryMetrics?.session_count)} 次会话；公开闸门为${statusLabel(publicGate.gate_status)}。`,
        `Canary has ${formatNumber(state.canaryMetrics?.session_count)} sessions; public gate is ${statusLabel(publicGate.gate_status)}.`,
      ),
    );
    setText(
      "phase11CanaryMeta",
      copy(
        `回访 ${formatNumber(state.canaryMetrics?.returning_tester_count)} 人，反馈 ${formatNumber(state.canaryMetrics?.feedback_submit_count)} 条，分享报告 ${formatNumber(state.canaryMetrics?.share_report_count)} 份。`,
        `${formatNumber(state.canaryMetrics?.returning_tester_count)} returning testers, ${formatNumber(state.canaryMetrics?.feedback_submit_count)} feedback items, ${formatNumber(state.canaryMetrics?.share_report_count)} share reports.`,
      ),
    );

    const publicStatus = state.publicStatus || {};
    setText(
      "phase12PublicText",
      copy(
        `公开状态为${statusLabel(publicStatus.launch_status)}；${firstReason(publicStatus.blocked_reasons)}。`,
        `Public status is ${statusLabel(publicStatus.launch_status)}; ${firstReason(publicStatus.blocked_reasons)}.`,
      ),
    );
    setText(
      "phase12PublicMeta",
      copy(
        `公开会话 ${formatNumber(state.publicMetrics?.session_count)} 次，反馈 ${formatNumber(state.publicMetrics?.feedback_submit_count)} 条，关键事件 ${formatNumber(state.publicMetrics?.critical_incident_count)} 起。`,
        `${formatNumber(state.publicMetrics?.session_count)} public sessions, ${formatNumber(state.publicMetrics?.feedback_submit_count)} feedback items, ${formatNumber(state.publicMetrics?.critical_incident_count)} critical incidents.`,
      ),
    );

    const productGate = state.productGate || {};
    setText(
      "phase13ProductizationText",
      copy(
        `产品化闸门为${statusLabel(productGate.gate_status)}；${firstReason(productGate.blocked_reasons)}。`,
        `Productization gate is ${statusLabel(productGate.gate_status)}; ${firstReason(productGate.blocked_reasons)}.`,
      ),
    );
    setText(
      "phase13ProductizationMeta",
      copy(
        `学习访客 ${formatNumber(state.productMetrics?.visitor_count)} 人，完成节点 ${formatNumber(state.productMetrics?.completed_node_count)} 个，回访 ${formatNumber(state.productMetrics?.returning_visitor_count)} 人。`,
        `${formatNumber(state.productMetrics?.visitor_count)} learning visitors, ${formatNumber(state.productMetrics?.completed_node_count)} completed nodes, ${formatNumber(state.productMetrics?.returning_visitor_count)} returning visitors.`,
      ),
    );

    const moneyGate = state.monetizationGate || {};
    setText(
      "phase14MonetizationText",
      copy(
        `商业化闸门为${statusLabel(moneyGate.gate_status)}；${firstReason(moneyGate.blocked_reasons)}。`,
        `Monetization gate is ${statusLabel(moneyGate.gate_status)}; ${firstReason(moneyGate.blocked_reasons)}.`,
      ),
    );
    setText(
      "phase14MonetizationMeta",
      copy(
        `兴趣事件 ${formatNumber(state.monetizationMetrics?.event_count)} 条，商务线索 ${formatNumber(state.monetizationMetrics?.business_lead_count)} 条，权益点击 ${formatNumber(state.monetizationMetrics?.offer_click_count)} 次。`,
        `${formatNumber(state.monetizationMetrics?.event_count)} interest events, ${formatNumber(state.monetizationMetrics?.business_lead_count)} business leads, ${formatNumber(state.monetizationMetrics?.offer_click_count)} offer clicks.`,
      ),
    );

    const paymentGate = state.paymentGate || {};
    setText(
      "phase15PaymentText",
      copy(
        `支付准备为${statusLabel(paymentGate.gate_status)}；${firstReason(paymentGate.blocked_reasons)}。`,
        `Payment readiness is ${statusLabel(paymentGate.gate_status)}; ${firstReason(paymentGate.blocked_reasons)}.`,
      ),
    );
    setText(
      "phase15PaymentMeta",
      copy(
        `支付沙箱订单 ${formatNumber(state.paymentMetrics?.order_count)} 个，已支付演示 ${formatNumber(state.paymentMetrics?.paid_sandbox_count)} 个，退款案例 ${formatNumber(state.paymentMetrics?.refund_case_count)} 个。`,
        `${formatNumber(state.paymentMetrics?.order_count)} Payment sandbox orders, ${formatNumber(state.paymentMetrics?.paid_sandbox_count)} paid demos, ${formatNumber(state.paymentMetrics?.refund_case_count)} refund cases.`,
      ),
    );
  }

  function localizedCalendarItem(item, index) {
    const fallback = CALENDAR_FALLBACK_BY_ID[item.content_id] || CALENDAR_FALLBACK[index] || null;
    if (currentLanguage() === "en") {
      return {
        column: fallback?.enColumn || copy("本地栏目", "Local column"),
        title: fallback?.enTitle || copy("待整理内容", "Draft content"),
        status: statusLabel(item.status || "draft"),
      };
    }
    return {
      column: fallback?.zhColumn || item.column || "本地栏目",
      title: fallback?.zhTitle || item.title || "待整理内容",
      status: statusLabel(item.status || "draft"),
    };
  }

  function renderCalendar() {
    const items = (state.calendar?.items || CALENDAR_FALLBACK).slice(0, 5);
    setHtml(
      "contentCalendarList",
      items
        .map((item, index) => {
          const display = localizedCalendarItem(item, index);
          return `<li><strong>${escapeHtml(display.column)}</strong>: ${escapeHtml(display.title)} <span>${escapeHtml(display.status)}</span></li>`;
        })
        .join(""),
    );
  }

  function render() {
    renderOverview();
    renderPhasePath();
    renderStatusCards();
    renderCalendar();
  }

  function bindElements() {
    ids.forEach((id) => {
      els[id] = document.getElementById(id);
    });
  }

  function loadStatusBoard() {
    [
      ["/api/release/readiness", "release"],
      ["/api/ops/status", "ops"],
      ["/api/canary/config", "canaryConfig"],
      ["/api/content/calendar", "calendar"],
      ["/api/canary/metrics", "canaryMetrics"],
      ["/api/public-release/gate", "publicGate"],
      ["/api/public/status", "publicStatus"],
      ["/api/public/metrics", "publicMetrics"],
      ["/api/productization/gate", "productGate"],
      ["/api/product/metrics", "productMetrics"],
      ["/api/monetization/gate", "monetizationGate"],
      ["/api/monetization/metrics", "monetizationMetrics"],
      ["/api/payment/gate", "paymentGate"],
      ["/api/payment/metrics", "paymentMetrics"],
    ].forEach(([path, key]) => {
      readJson(path, key);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    bindElements();
    render();
    loadStatusBoard();
  });

  document.addEventListener("renyu:languagechange", () => {
    render();
  });
})();
