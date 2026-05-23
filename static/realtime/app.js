const state = {
  pc: null,
  dc: null,
  stream: null,
  lastResponseItemId: null,
  lastToolResult: null,
  betaConfig: null,
  betaReport: null,
  opsStatus: null,
  canaryRunConfig: null,
  canaryTaskStatus: null,
  publicStatus: null,
  productizationGate: null,
  learningPath: null,
  learningCardsCatalog: [],
  learningCardsAvailable: false,
  selectedLearningNodeId: null,
  growthMetrics: null,
  monetizationGate: null,
  monetizationMetrics: null,
  offerCatalog: null,
  paymentGate: null,
  paymentMetrics: null,
  membershipTiers: null,
  sandboxOrder: null,
  sandboxPaymentResult: null,
  businessLeadResult: null,
  businessLeadPayload: null,
  personaCardLines: [],
  personaCardsExpanded: false,
  lastShareReportEventKey: "",
  shareReportPayload: null,
  shareReportView: null,
};

const els = {
  connectBtn: document.getElementById("connectBtn"),
  disconnectBtn: document.getElementById("disconnectBtn"),
  interruptBtn: document.getElementById("interruptBtn"),
  modeSelect: document.getElementById("modeSelect"),
  testerId: document.getElementById("testerId"),
  inviteCode: document.getElementById("inviteCode"),
  status: document.getElementById("status"),
  textQuestion: document.getElementById("textQuestion"),
  runTextInterpretBtn: document.getElementById("runTextInterpretBtn"),
  textInterpretStatus: document.getElementById("textInterpretStatus"),
  betaNotice: document.getElementById("betaNotice"),
  opsPauseNotice: document.getElementById("opsPauseNotice"),
  publicFeedbackNotice: document.getElementById("publicFeedbackNotice"),
  visitorNickname: document.getElementById("visitorNickname"),
  saveVisitorProfileBtn: document.getElementById("saveVisitorProfileBtn"),
  visitorProfileStatus: document.getElementById("visitorProfileStatus"),
  transcript: document.getElementById("transcript"),
  toolLog: document.getElementById("toolLog"),
  interpretationPreview: document.getElementById("interpretationPreview"),
  explainResult: document.getElementById("explainResult"),
  debugDetails: document.getElementById("debugDetails"),
  debugJson: document.getElementById("debugJson"),
  learningMaterials: document.getElementById("learningMaterials"),
  personaCards: document.getElementById("personaCards"),
  personaCardsToggle: document.getElementById("personaCardsToggle"),
  learningCards: document.getElementById("learningCards"),
  learningPathPanel: document.getElementById("learningPathPanel"),
  learningPathSummary: document.getElementById("learningPathSummary"),
  learningPathRecommended: document.getElementById("learningPathRecommended"),
  learningPathNodes: document.getElementById("learningPathNodes"),
  learningPathDetail: document.getElementById("learningPathDetail"),
  learningPathStatus: document.getElementById("learningPathStatus"),
  safetyState: document.getElementById("safetyState"),
  feedbackType: document.getElementById("feedbackType"),
  feedbackNote: document.getElementById("feedbackNote"),
  submitFeedbackBtn: document.getElementById("submitFeedbackBtn"),
  feedbackStatus: document.getElementById("feedbackStatus"),
  canaryStatusBadge: document.getElementById("canaryStatusBadge"),
  canaryOverview: document.getElementById("canaryOverview"),
  canaryProgressLabel: document.getElementById("canaryProgressLabel"),
  canaryProgressBarFill: document.getElementById("canaryProgressBarFill"),
  canaryMilestones: document.getElementById("canaryMilestones"),
  canaryTaskList: document.getElementById("canaryTaskList"),
  commercialInterest: document.getElementById("commercialInterest"),
  commercialInterestSummary: document.getElementById("commercialInterestSummary"),
  commercialInterestStatus: document.getElementById("commercialInterestStatus"),
  monetizationGateBadge: document.getElementById("monetizationGateBadge"),
  monetizationMetricsHeadline: document.getElementById("monetizationMetricsHeadline"),
  monetizationOverview: document.getElementById("monetizationOverview"),
  monetizationReasonList: document.getElementById("monetizationReasonList"),
  monetizationMetricsList: document.getElementById("monetizationMetricsList"),
  offerCatalogList: document.getElementById("offerCatalogList"),
  monetizationStatus: document.getElementById("monetizationStatus"),
  monetizationInterestButtons: document.querySelectorAll(".monetizationInterest"),
  commercialPathSteps: document.getElementById("commercialPathSteps"),
  commercialPathSummary: document.getElementById("commercialPathSummary"),
  commercialPathMetrics: document.getElementById("commercialPathMetrics"),
  businessLeadNickname: document.getElementById("businessLeadNickname"),
  businessLeadChannel: document.getElementById("businessLeadChannel"),
  businessLeadSummary: document.getElementById("businessLeadSummary"),
  submitBusinessLeadBtn: document.getElementById("submitBusinessLeadBtn"),
  businessLeadStatus: document.getElementById("businessLeadStatus"),
  businessLeadOutcome: document.getElementById("businessLeadOutcome"),
  membershipTiersList: document.getElementById("membershipTiersList"),
  paymentGateStatus: document.getElementById("paymentGateStatus"),
  paymentGateBadge: document.getElementById("paymentGateBadge"),
  paymentGateReasonList: document.getElementById("paymentGateReasonList"),
  paymentCapabilitiesList: document.getElementById("paymentCapabilitiesList"),
  paymentMetricsList: document.getElementById("paymentMetricsList"),
  paymentTierSelect: document.getElementById("paymentTierSelect"),
  startSandboxCheckoutBtn: document.getElementById("startSandboxCheckoutBtn"),
  confirmSandboxPaymentBtn: document.getElementById("confirmSandboxPaymentBtn"),
  failSandboxPaymentBtn: document.getElementById("failSandboxPaymentBtn"),
  cancelSandboxOrderBtn: document.getElementById("cancelSandboxOrderBtn"),
  refundSandboxOrderBtn: document.getElementById("refundSandboxOrderBtn"),
  sandboxOrderStatus: document.getElementById("sandboxOrderStatus"),
  sandboxOrderDetail: document.getElementById("sandboxOrderDetail"),
  shareReport: document.getElementById("shareReport"),
  shareReportMeta: document.getElementById("shareReportMeta"),
  shareReportLead: document.getElementById("shareReportLead"),
  shareReportCards: document.getElementById("shareReportCards"),
  shareReportCopyStatus: document.getElementById("shareReportCopyStatus"),
  copyShareReportTextBtn: document.getElementById("copyShareReportTextBtn"),
  copyShareReportHtmlBtn: document.getElementById("copyShareReportHtmlBtn"),
  shareReportDraftDetails: document.getElementById("shareReportDraftDetails"),
  shareReportDraftMeta: document.getElementById("shareReportDraftMeta"),
  shareReportDraftCards: document.getElementById("shareReportDraftCards"),
  copyShareReportDraftBtn: document.getElementById("copyShareReportDraftBtn"),
  remoteAudio: document.getElementById("remoteAudio"),
};

const allowedModes = new Set(["professional", "plain", "story", "mentor"]);
const defaultPersonaCardCount = 4;
const generalSlugMap = Object.freeze({
  贵人: "guiren",
  螣蛇: "tengshe",
  朱雀: "zhuque",
  六合: "liuhe",
  勾陈: "gouchen",
  青龙: "qinglong",
  天空: "tiankong",
  白虎: "baihu",
  太常: "taichang",
  玄武: "xuanwu",
  太阴: "taiyin",
  天后: "tianhou",
});
const learningPathUnavailableCopy = Object.freeze({
  message: "学习闯关暂不可用。",
  detail: "请稍后重试。",
});
const learningTopicSummaries = {
  four_lessons: "先看四课结构，理解这节的骨架，再进入细部判断。",
  three_transmissions: "先抓住事情的起因、推进和收束，建立推演顺序。",
  nine_rules: "先从取传路径入手，判断当前节点更适合作为研究参考还是公开学习。",
  generals: "把天将当作象征角色来读，而不是现实承诺。",
  shensha: "先识别神煞的提示意义，再决定是否继续展开。",
  classical_symbols: "把经典象征和问题类型连起来看，形成可复用的理解框架。",
  safety_boundary: "先分清哪些问题不能直接落到现实结论。",
  report_export: "先理解本地分享和报告草稿的边界，再看输出内容。",
};

function setStatus(value) {
  els.status.textContent = displayStatusValue(value);
}

function writeLog(element, value) {
  element.textContent = typeof value === "string" ? value : JSON.stringify(value, null, 2);
}

const navTargetIds = ["questionPanel", "learningPathPanel", "feedbackPanel", "experimentsPanel"];

function isDetailsElement(element) {
  return element?.tagName === "DETAILS" || Object.prototype.hasOwnProperty.call(element || {}, "open");
}

function setActiveNavTarget(target) {
  navTargetIds.forEach((id) => {
    const panel = document.getElementById(id);
    if (!panel?.classList) {
      return;
    }
    const isActive = panel === target;
    panel.classList.toggle("nav-target-active", isActive);
    if (isActive) {
      panel.setAttribute("data-nav-active", "true");
    } else {
      panel.removeAttribute("data-nav-active");
    }
  });
}

function updateNavCurrent(activeLink) {
  if (typeof document.querySelectorAll !== "function") {
    return;
  }
  document.querySelectorAll(".app-nav a").forEach((link) => {
    if (link === activeLink) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  });
}

function handleNavLinkClick(event) {
  const link = event.currentTarget;
  const href = link?.getAttribute("href") || "";
  if (!href.startsWith("#")) {
    return;
  }
  const target = document.getElementById(href.slice(1));
  if (!target) {
    return;
  }
  event.preventDefault();
  if (isDetailsElement(target)) {
    target.open = true;
  }
  updateNavCurrent(link);
  setActiveNavTarget(target);
  if (typeof target.scrollIntoView === "function") {
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function bindTopNavLinks() {
  if (typeof document.querySelectorAll !== "function") {
    return;
  }
  document.querySelectorAll(".app-nav a").forEach((link) => {
    link.addEventListener("click", handleNavLinkClick);
  });
}

function openPanelById(panelId) {
  const target = document.getElementById(panelId);
  if (!target) {
    return;
  }
  if (isDetailsElement(target)) {
    target.open = true;
  }
  setActiveNavTarget(target);
  if (typeof target.scrollIntoView === "function") {
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function friendlyBlockedReason(reasons, fallback) {
  const reasonSet = new Set(reasons || []);
  if (reasonSet.has("productization_not_active")) {
    return "偏好保存暂未开放，不影响起课使用。";
  }
  if (reasonSet.has("monetization_not_active")) {
    return "兴趣记录暂未开放，不影响起课使用。";
  }
  if (reasonSet.has("payment_not_active")) {
    return "沙箱支付暂未开放，不影响起课使用。";
  }
  return fallback;
}

function numberValue(value) {
  const number = Number(value);
  return Number.isFinite(number) ? number : 0;
}

function monetizationGateStatusLabel(status) {
  if (selectedDisplayLanguage() === "en") {
    if (status === "experiment") {
      return "Experiment active";
    }
    if (status === "canary") {
      return "Canary";
    }
    if (status === "preview") {
      return "Preview";
    }
    if (status === "live") {
      return "Open";
    }
    if (status === "paused") {
      return "Paused";
    }
    if (status === "blocked") {
      return "Waiting for upstream";
    }
    return "Unknown";
  }
  if (status === "experiment") {
    return "实验进行中";
  }
  if (status === "canary") {
    return "灰测中";
  }
  if (status === "preview") {
    return "预览中";
  }
  if (status === "live") {
    return "已开放";
  }
  if (status === "paused") {
    return "实验已暂停";
  }
  if (status === "blocked") {
    return "等待上游阶段";
  }
  return "状态未知";
}

function monetizationGateStatusClass(status) {
  if (status === "experiment") {
    return "is-active";
  }
  if (status === "paused" || status === "blocked") {
    return "is-blocked";
  }
  return "";
}

function friendlyMonetizationReason(reason) {
  const mapping = {
    productization_not_active: {
      zh: "产品化阶段尚未进入实验。",
      en: "Productization has not entered the experiment stage.",
    },
    public_mvp_not_active: {
      zh: "公开最小可用版本仍未激活。",
      en: "The public build is not active yet.",
    },
    public_release_gate_blocked: {
      zh: "公开发布闸门仍在阻塞。",
      en: "The public release gate is still blocked.",
    },
    canary_not_active: {
      zh: "当前不是灰测窗口。",
      en: "The current window is not a canary run.",
    },
    expert_review_pending: {
      zh: "专家审校仍未完成。",
      en: "Expert review is still pending.",
    },
    beta_manual_review_pending: {
      zh: "内测人工复核仍未完成。",
      en: "Manual beta review is still pending.",
    },
    insufficient_canary_sessions: {
      zh: "灰测样本会话还不够。",
      en: "The canary sample does not have enough sessions yet.",
    },
    insufficient_returning_testers: {
      zh: "回访测试者样本还不够。",
      en: "The returning tester sample is not large enough yet.",
    },
    insufficient_feedback: {
      zh: "有效反馈样本还不够。",
      en: "The feedback sample is not large enough yet.",
    },
    insufficient_share_reports: {
      zh: "分享报告样本还不够。",
      en: "The share report sample is not large enough yet.",
    },
    insufficient_monetization_interest: {
      zh: "会员兴趣、权益浏览或权益点击还没有达到沙箱门槛。",
      en: "Membership interest, benefit views, or offer clicks have not reached the sandbox threshold.",
    },
    critical_public_incident: {
      zh: "存在关键公共事故，需要先止损。",
      en: "A critical public incident must be handled first.",
    },
    copyright_blocked_visible: {
      zh: "可见内容仍有版权阻塞。",
      en: "Visible content still has a copyright blocker.",
    },
    forbidden_payment_copy: {
      zh: "支付文案里仍有禁用承诺词。",
      en: "Payment copy still contains forbidden promise terms.",
    },
    monetization_experiment_disabled: {
      zh: "商业化实验被手动关闭。",
      en: "The monetization experiment has been manually disabled.",
    },
    monetization_not_active: {
      zh: "当前阶段不会持久化第 14 阶段兴趣事件。",
      en: "The current stage does not persist phase 14 interest events.",
    },
    payment_not_active: {
      zh: "沙箱支付当前未开放，不会创建订单。",
      en: "Sandbox payment is not open, so no order is created.",
    },
    payment_sandbox_disabled: {
      zh: "沙箱支付被手动关闭。",
      en: "Sandbox payment has been manually disabled.",
    },
    risk_or_copyright_block: {
      zh: "风险或版权问题导致实验暂停。",
      en: "Risk or copyright issues paused the experiment.",
    },
  };
  const entry = mapping[reason];
  if (entry) {
    return entry[selectedDisplayLanguage()];
  }
  return String(reason || displayCopy("待补充", "To be filled"));
}

function friendlyMonetizationReasons(reasons) {
  return [...new Set((reasons || []).map((reason) => friendlyMonetizationReason(reason)).filter(Boolean))];
}

function monetizationEventLabel(eventType) {
  const mapping = {
    member_interest: { zh: "会员兴趣", en: "Membership interest" },
    course_interest: { zh: "课程兴趣", en: "Course interest" },
    business_interest: { zh: "商务合作兴趣", en: "Business interest" },
    ip_interest: { zh: "文创周边兴趣", en: "Creative merchandise interest" },
    pricing_view: { zh: "权益边界浏览", en: "Benefit boundary view" },
    offer_click: { zh: "权益详情查看", en: "Benefit detail view" },
  };
  return mapping[eventType]?.[selectedDisplayLanguage()] || String(eventType || displayCopy("兴趣事件", "Interest event"));
}

function monetizationOfferCategoryLabel(category) {
  const mapping = {
    free: { zh: "免费层", en: "Free tier" },
    membership: { zh: "会员预览", en: "Membership preview" },
    expert_course: { zh: "课程/老师", en: "Courses / teachers" },
    course: { zh: "课程/老师", en: "Courses / teachers" },
    b2b: { zh: "机构合作", en: "Institutional partnership" },
    ip_goods: { zh: "文创周边", en: "Creative merchandise" },
    ip_presale: { zh: "文创周边", en: "Creative merchandise" },
  };
  return mapping[category]?.[selectedDisplayLanguage()] || String(category || displayCopy("未分类", "Uncategorized"));
}

function nowIso() {
  return new Date().toISOString();
}

function userTimezone() {
  return Intl.DateTimeFormat().resolvedOptions().timeZone || "Asia/Shanghai";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function stringValue(value) {
  return typeof value === "string" ? value : value == null ? "" : String(value);
}

const knownDisplayTextZh = Object.freeze({
  "RenYu local share report": "澹语本地分享报告",
  "RenYu local PDF report draft": "澹语本地文档报告草稿",
  Overview: "概览",
  "Chart Facts": "课式信息",
  "Persona Lines": "角色化句子",
  "Learning Cards": "学习卡",
  Safety: "安全提示",
  Evidence: "证据",
  Report: "报告",
  Draft: "草稿",
  "Chart ID": "课题 ID",
  Mode: "口吻",
  Storage: "存储",
  "Print CSS": "打印样式",
  "HTML 草稿": "网页草稿",
  "PDF 草稿提纲": "文档草稿提纲",
  "All offers are interest-only previews.": "所有权益都只是兴趣预览，不收款，也不发放付费权益。",
  "All offers are interest-only previews. They do not collect payment or unlock paid rights.": "所有权益都只是兴趣预览，不收款，也不发放付费权益。",
  "Free learning layer": "免费学习层",
  "Membership preview": "会员预览",
  "Expert and course preview": "专家与课程预览",
  "B2B cultural event preview": "商务文化活动预览",
  "IP goods preview": "文创周边预览",
  "Basic voice questions, term learning, limited chart attempts, and safety reminders.": "基础语音提问、术语学习、有限起课次数和安全提醒。",
  "Complete reports, more learning cards, case library, extended source cards, and richer persona expression.": "完整报告、更多学习卡、案例库、扩展出处卡和更丰富的角色化表达。",
  "Complete reports and richer persona expression.": "完整报告和更丰富的角色化表达。",
  "Authorized consultant courses, classic readings, and case livestream concepts.": "授权顾问课程、经典阅读和案例直播概念。",
  "Traditional culture installations for exhibitions, culture venues, bookstores, and travel scenes.": "面向展览、文化空间、书店和文旅场景的传统文化装置。",
  "Twelve generals cards, journals, stickers, and tabletop concept drafts.": "十二天将卡牌、手账、贴纸和桌游概念草稿。",
  "Designed for traditional culture learning and entertainment only.": "仅用于传统文化学习与娱乐体验。",
  "The preview sells content organization and learning experience, not outcomes.": "预览展示的是内容组织和学习体验，不售卖现实结果。",
  "All expert, likeness, voice, and course rights must be cleared before sale.": "专家、肖像、声音和课程权益售卖前必须完成授权。",
  "Positioned as a culture experience, not a decision tool.": "定位为文化体验，不是决策工具。",
  "Artwork, text, and voice material must be original or licensed.": "图像、文字和声音素材必须原创或获得授权。",
  "Interest only.": "仅记录兴趣。",
  "Free learning preview": "免费学习预览",
  "Membership sandbox preview": "会员沙箱预览",
  "Course sandbox preview": "课程沙箱预览",
  "B2B sandbox preview": "商务沙箱预览",
  "IP goods sandbox preview": "文创周边沙箱预览",
  "Beta notice": "内测说明",
  "受限 Beta：传统文化学习与娱乐体验。": "受限内测：传统文化学习与娱乐体验。",
  "受限 Beta：本功能仅用于传统文化学习与娱乐体验，不构成医疗、法律、投资、人身安全或其他现实决策建议。": "受限内测：本功能仅用于传统文化学习与娱乐体验，不构成医疗、法律、投资、人身安全或其他现实决策建议。",
  "受限内测：传统文化学习与娱乐体验，不构成现实建议。": "Limited beta: traditional culture learning and entertainment only, not real-world advice.",
  "受限内测：本功能仅用于传统文化学习与娱乐体验，不构成医疗、法律、投资、人身安全或其他现实决策建议。": "Limited beta: this feature is for traditional culture learning and entertainment only, not medical, legal, investment, personal safety, or other real-world decision advice.",
  "受限内测：配置暂不可用，请按安全边界测试。": "Limited beta: configuration is unavailable. Please test within the safety boundary.",
  "公开最小可用版本已暂停；当前仅提供安全说明、维护说明和反馈入口。": "The public build is paused. Only safety notes, maintenance information, and feedback remain available.",
  "公开最小可用版本：传统文化学习与娱乐体验，不保存录音；反馈、课式和删除请求仅用于产品复盘。": "Public build: traditional culture learning and entertainment. Audio is not stored; feedback, charts, and deletion requests are used only for product review.",
  "Complete report draft, more learning cards, case library preview, and source-card expansion.": "完整报告草稿、更多学习卡、案例库预览和出处卡扩展。",
  "Authorized course outline, classic reading plan, and case live-session concept.": "授权课程大纲、经典阅读计划和案例直播概念。",
  "Culture venue, bookstore, exhibition, and travel-scene interaction plan.": "文化空间、书店、展览和文旅场景互动方案。",
  "Twelve generals card, journal, sticker, and tabletop concept drafts.": "十二天将卡牌、手账、贴纸和桌游概念草稿。",
  "traditional culture learning and entertainment experience, not real-world advice": "传统文化学习与娱乐体验，不构成现实建议",
  basic_voice: "基础语音提问",
  term_learning: "术语学习",
  limited_chart_attempts: "有限起课次数",
  complete_report: "完整报告草稿",
  learning_card_extension: "学习卡扩展",
  case_library_preview: "案例库预览",
  course_outline: "课程大纲",
  classic_reading_plan: "经典阅读计划",
  case_session_preview: "案例场次预览",
  event_plan_preview: "活动方案预览",
  venue_script_preview: "场馆脚本预览",
  installation_outline: "装置大纲",
  card_concept: "卡牌概念",
  journal_concept: "手账概念",
  tabletop_concept: "桌游概念",
  mock_sandbox_checkout: "沙箱订单创建",
  sandbox_payment_confirm: "沙箱支付确认",
  sandbox_cancel: "沙箱取消",
  sandbox_refund: "沙箱退款",
  membership_tier_preview: "会员层级预览",
  checkout_started: "沙箱订单已创建",
  sandbox_paid: "沙箱支付成功",
  payment_failed: "沙箱支付失败",
  subscription_canceled: "沙箱订单已取消",
  refund_completed: "沙箱退款完成",
  payment_blocked: "沙箱支付阻断",
  frontend_cancel_demo: "前端取消演示",
  frontend_refund_demo: "前端退款演示",
  order_not_found: "未找到订单",
});

const knownDisplayTextEn = Object.freeze({
  ...Object.fromEntries(Object.entries(knownDisplayTextZh).map(([english, chinese]) => [chinese, english])),
  "受限 Beta：传统文化学习与娱乐体验。": "Limited beta: traditional culture learning and entertainment only.",
  "受限 Beta：本功能仅用于传统文化学习与娱乐体验，不构成医疗、法律、投资、人身安全或其他现实决策建议。": "Limited beta: this feature is for traditional culture learning and entertainment only, not medical, legal, investment, personal safety, or other real-world decision advice.",
  "受限内测：传统文化学习与娱乐体验，不构成现实建议。": "Limited beta: traditional culture learning and entertainment only, not real-world advice.",
  "受限内测：本功能仅用于传统文化学习与娱乐体验，不构成医疗、法律、投资、人身安全或其他现实决策建议。": "Limited beta: this feature is for traditional culture learning and entertainment only, not medical, legal, investment, personal safety, or other real-world decision advice.",
  "受限内测：配置暂不可用，请按安全边界测试。": "Limited beta: configuration is unavailable. Please test within the safety boundary.",
});

const knownDisplayValueLabels = Object.freeze({
  local_share_report: { zh: "本地分享报告", en: "Local share report" },
  local_only: { zh: "仅本地", en: "Local only" },
  pdf_draft: { zh: "文档草稿", en: "Document draft" },
  plain_text: { zh: "纯文本", en: "Plain text" },
  plain: { zh: "白话", en: "Plain" },
  story: { zh: "故事", en: "Story" },
  mentor: { zh: "导师", en: "Mentor" },
  professional: { zh: "专业", en: "Professional" },
  canary_denied: { zh: "灰测未通过", en: "Canary denied" },
  connecting: { zh: "连接中", en: "Connecting" },
  listening: { zh: "聆听中", en: "Listening" },
  idle: { zh: "空闲", en: "Idle" },
  error: { zh: "错误", en: "Error" },
  todo: { zh: "待处理", en: "To do" },
  completed: { zh: "已完成", en: "Completed" },
  started: { zh: "已开始", en: "Started" },
  blocked: { zh: "已阻塞", en: "Blocked" },
  paused: { zh: "已暂停", en: "Paused" },
  experiment: { zh: "实验中", en: "Experiment" },
  sandbox: { zh: "沙箱可用", en: "Sandbox ready" },
  pending_payment: { zh: "等待沙箱支付", en: "Pending sandbox payment" },
  paid_sandbox: { zh: "沙箱支付成功", en: "Paid in sandbox" },
  failed: { zh: "沙箱支付失败", en: "Sandbox payment failed" },
  canceled: { zh: "已取消", en: "Canceled" },
  refunded: { zh: "已退款", en: "Refunded" },
  mock_sandbox: { zh: "沙箱模拟", en: "Mock sandbox" },
  CNY: { zh: "人民币", en: "CNY" },
  canary: { zh: "灰测中", en: "Canary" },
  preview: { zh: "预览中", en: "Preview" },
  live: { zh: "已开放", en: "Live" },
  unknown: { zh: "未知", en: "Unknown" },
});

function selectedDisplayLanguage() {
  const htmlLanguage = document.documentElement?.dataset?.language;
  if (htmlLanguage === "en") {
    return "en";
  }
  if (htmlLanguage === "zh") {
    return "zh";
  }
  try {
    return window.localStorage?.getItem("renyu.language") === "en" ? "en" : "zh";
  } catch {
    return "zh";
  }
}

function displayCopy(chinese, english) {
  return selectedDisplayLanguage() === "en" ? english : chinese;
}

function preserveOuterWhitespace(original, replacement) {
  const text = String(original ?? "");
  const leading = text.match(/^\s*/)?.[0] || "";
  const trailing = text.match(/\s*$/)?.[0] || "";
  return `${leading}${replacement}${trailing}`;
}

function localizeKnownDisplayText(value) {
  const text = stringValue(value);
  const trimmed = text.trim();
  if (!trimmed) {
    return text;
  }
  const mapping = selectedDisplayLanguage() === "en" ? knownDisplayTextEn : knownDisplayTextZh;
  return mapping[trimmed] ? preserveOuterWhitespace(text, mapping[trimmed]) : text;
}

function localizeKnownDisplayValue(value) {
  const text = readableScalar(value);
  const trimmed = text.trim();
  if (!trimmed) {
    return "";
  }
  const label = knownDisplayValueLabels[trimmed];
  if (label) {
    return preserveOuterWhitespace(text, label[selectedDisplayLanguage()]);
  }
  return localizeKnownDisplayText(text);
}

function displayStatusValue(value) {
  return localizeKnownDisplayValue(value || "unknown");
}

function displayIdentifier(value) {
  const text = stringValue(value).trim();
  if (!text) {
    return "";
  }
  if (selectedDisplayLanguage() === "en") {
    return text;
  }
  const knownPrefixes = [
    [/^sandbox[_-]order[_-](.+)$/i, "沙箱订单"],
    [/^business[_-]lead[_-](.+)$/i, "商务线索"],
    [/^payment[_-]event[_-](.+)$/i, "支付事件"],
    [/^refund[_-]case[_-](.+)$/i, "退款案例"],
  ];
  for (const [pattern, label] of knownPrefixes) {
    const match = text.match(pattern);
    if (match) {
      return `${label} ${match[1]}`;
    }
  }
  const tokenLabels = {
    sandbox: "沙箱",
    order: "订单",
    business: "商务",
    lead: "线索",
    payment: "支付",
    event: "事件",
    refund: "退款",
    case: "案例",
    tier: "权益",
    membership: "会员",
    free: "免费",
    course: "课程",
    b2b: "机构",
    ip: "文创",
    presale: "预售",
    mock: "模拟",
    frontend: "前端",
    realtime: "实时",
    demo: "演示",
    v0: "版本 0",
  };
  return text
    .split(/[_-]+/)
    .map((part) => tokenLabels[part.toLowerCase()] || part)
    .join(" ");
}

function localizedNumber(value) {
  const formatter = new Intl.NumberFormat(selectedDisplayLanguage() === "en" ? "en-US" : "zh-CN");
  return formatter.format(numberValue(value));
}

function boolLabel(value) {
  return value ? displayCopy("是", "Yes") : displayCopy("否", "No");
}

function formatAmountCents(amountCents, currency = "CNY") {
  const amount = numberValue(amountCents) / 100;
  if (!amount) {
    return displayCopy("沙箱金额 0 元", "Sandbox amount 0");
  }
  try {
    return new Intl.NumberFormat(selectedDisplayLanguage() === "en" ? "en-US" : "zh-CN", {
      style: "currency",
      currency: currency || "CNY",
      maximumFractionDigits: 2,
    }).format(amount);
  } catch {
    return `${amount.toFixed(2)} ${currency || ""}`.trim();
  }
}

function paymentGateStatusLabel(status) {
  if (status === "sandbox") {
    return displayCopy("沙箱可用", "Sandbox ready");
  }
  if (status === "paused") {
    return displayCopy("支付准备已暂停", "Payment readiness paused");
  }
  if (status === "blocked") {
    return displayCopy("等待前置门槛", "Waiting for prerequisites");
  }
  return displayStatusValue(status);
}

function paymentGateStatusClass(status) {
  if (status === "sandbox") {
    return "is-active";
  }
  if (status === "paused" || status === "blocked") {
    return "is-blocked";
  }
  return "";
}

function orderStatusClass(status) {
  if (["paid_sandbox", "refunded"].includes(status)) {
    return "is-completed";
  }
  if (["failed", "canceled", "blocked"].includes(status)) {
    return "is-blocked";
  }
  return "is-ready";
}

function canAttemptCheckout() {
  return state.paymentGate?.gate_status === "sandbox";
}

function nonEmptyLines(value) {
  return stringValue(value)
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

function labeledLineParts(line) {
  const match = String(line || "").match(/^([^:：]{1,24})\s*[：:]\s*(.+)$/);
  if (!match) {
    return null;
  }
  return {
    label: match[1].trim(),
    content: match[2].trim(),
  };
}

function shareReportSectionLabel(title) {
  const value = localizeKnownDisplayText(title).trim();
  const accentTitles = new Set(["摘要", "概览", "结论", "安全提示", "故事场景", "下一步", "Summary", "Overview"]);
  return accentTitles.has(value) ? "accent" : "";
}

function isPlainObject(value) {
  return Boolean(value) && typeof value === "object" && !Array.isArray(value);
}

const shareReportFieldLabels = Object.freeze({
  question: "问题",
  chart_id: "课题 ID",
  lesson_type: "课体",
  category: "分类",
  datetime: "时间",
  datetime_normalized: "时间",
  evidence_count: "证据数",
  title: "标题",
  summary: "摘要",
  description: "说明",
  status: "状态",
  node_id: "节点",
});

const shareReportPreferredKeys = Object.freeze([
  "question",
  "chart_id",
  "lesson_type",
  "category",
  "datetime",
  "datetime_normalized",
  "evidence_count",
]);

const shareReportNoisyKeys = new Set([
  "evidence",
  "evidences",
  "raw",
  "debug",
  "payload",
  "json",
  "html",
  "copy_html",
]);

function readableScalar(value) {
  if (value == null || value === "") {
    return "";
  }
  if (typeof value === "string") {
    return value.trim();
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  return "";
}

function labeledShareReportField(key, value) {
  const scalar = localizeKnownDisplayValue(value);
  if (!scalar) {
    return "";
  }
  return `${localizeKnownDisplayText(shareReportFieldLabels[key] || key)}：${scalar}`;
}

function summarizeObjectSectionContent(content) {
  if (!isPlainObject(content)) {
    return { body: "", items: [] };
  }
  const body = readableScalar(content.summary || content.description || content.body || content.text || content.value);
  const items = [];
  shareReportPreferredKeys.forEach((key) => {
    const item = labeledShareReportField(key, content[key]);
    if (item) {
      items.push(item);
    }
  });
  Object.entries(content).forEach(([key, value]) => {
    if (items.length >= 8 || shareReportPreferredKeys.includes(key) || shareReportNoisyKeys.has(key)) {
      return;
    }
    if (["summary", "description", "body", "text", "value"].includes(key)) {
      return;
    }
    const item = labeledShareReportField(key, value);
    if (item) {
      items.push(item);
    }
  });
  return { body, items };
}

function summarizeObjectListItem(item) {
  if (!isPlainObject(item)) {
    return localizeKnownDisplayValue(item);
  }
  const title = localizeKnownDisplayValue(item.title || item.name || item.heading || item.label);
  const generalLine = [localizeKnownDisplayValue(item.general), localizeKnownDisplayValue(item.line)].filter(Boolean).join(" - ");
  const description = localizeKnownDisplayValue(item.description || item.summary || item.content || item.text || item.body);
  const nodeStatus = [readableScalar(item.node_id), localizeKnownDisplayValue(item.status)].filter(Boolean).join(" / ");
  return [title, generalLine, description, nodeStatus].filter(Boolean).join("；");
}

function isCodeLikeText(value) {
  const text = readableScalar(value);
  if (!text) {
    return false;
  }
  const trimmed = text.trim();
  return trimmed.startsWith("{")
    || trimmed.startsWith("[")
    || trimmed.startsWith("```")
    || trimmed.includes("\n{")
    || trimmed.length > 700;
}

function normalizeSectionList(items) {
  return (Array.isArray(items) ? items : [])
    .map((item) => summarizeObjectListItem(item))
    .filter(Boolean);
}

function normalizeShareReportContent(content, kind) {
  if (Array.isArray(content)) {
    const items = content
      .map((item) => summarizeObjectListItem(item))
      .filter(Boolean)
      .slice(0, 6);
    return { body: "", items, display: "list" };
  }
  if (isPlainObject(content)) {
    const summary = summarizeObjectSectionContent(content);
    return { body: summary.body, items: summary.items.slice(0, 8), display: "facts" };
  }
  const body = readableScalar(content) || stringValue(content).trim();
  const looksTechnical = kind === "code" || isCodeLikeText(body);
  return { body, items: [], display: looksTechnical ? "technical" : "text" };
}

function normalizeShareReportSection(section, fallbackTitle = "内容") {
  if (typeof section === "string") {
    return {
      title: localizeKnownDisplayText(fallbackTitle),
      body: section.trim(),
      items: [],
      tone: "",
      display: "text",
    };
  }
  const rawTitle = stringValue(section?.title || section?.label || section?.heading || section?.name || fallbackTitle).trim();
  const title = localizeKnownDisplayText(rawTitle).trim();
  const kind = stringValue(section?.kind || section?.format || "").trim();
  const rawContent = section?.content ?? section?.summary ?? section?.body ?? section?.text ?? section?.value ?? section?.description;
  const normalizedContent = normalizeShareReportContent(rawContent, kind);
  const explicitItems = normalizeSectionList(section?.items || section?.bullets || section?.highlights || section?.points);
  const items = explicitItems.length ? explicitItems : normalizedContent.items;
  if (!title && !normalizedContent.body && !items.length) {
    return null;
  }
  return {
    title: title || localizeKnownDisplayText(fallbackTitle),
    body: normalizedContent.body,
    items,
    tone: stringValue(section?.tone || section?.variant || section?.style || shareReportSectionLabel(title)).trim(),
    display: normalizedContent.display,
  };
}

function collectShareReportSections(report) {
  const sources = [
    report?.sections,
    report?.cards,
    report?.share_sections,
    report?.share_cards,
    report?.content?.sections,
  ];
  for (const source of sources) {
    const normalized = (Array.isArray(source) ? source : [])
      .map((section, index) => normalizeShareReportSection(section, `内容 ${index + 1}`))
      .filter(Boolean);
    if (normalized.length) {
      return normalized;
    }
  }
  return [];
}

function parseLegacyShareReport(report) {
  const lines = nonEmptyLines(report?.text || report?.copy_text || "");
  const sections = [];
  let title = stringValue(report?.title || report?.heading || report?.report_title).trim();
  let summary = stringValue(report?.summary || report?.abstract || report?.overview || report?.lead).trim();
  let note = stringValue(report?.disclaimer || report?.notice || report?.safety_note).trim();
  if (!title && lines.length) {
    title = localizeKnownDisplayText(lines.shift());
  }
  const extraLines = [];
  lines.forEach((line) => {
    const labeledLine = labeledLineParts(line);
    if (!labeledLine) {
      extraLines.push(line);
      return;
    }
    sections.push({
      title: localizeKnownDisplayText(labeledLine.label),
      body: labeledLine.content,
      items: [],
      tone: shareReportSectionLabel(labeledLine.label),
    });
    if (!summary && ["摘要", "概览", "结论", "Summary", "Overview"].includes(labeledLine.label)) {
      summary = labeledLine.content;
    }
    if (!note && ["安全提示", "免责声明", "Safety"].includes(labeledLine.label)) {
      note = labeledLine.content;
    }
  });
  extraLines.forEach((line) => {
    sections.push({
      title: localizeKnownDisplayText("补充说明"),
      body: line,
      items: [],
      tone: "",
    });
  });
  if (!summary && sections.length) {
    summary = sections[0].body;
  }
  return {
    title: localizeKnownDisplayText(title || "本地分享报告"),
    summary,
    note,
    sections,
  };
}

function normalizeShareReportDraft(draftSource) {
  const draft = draftSource && typeof draftSource === "object" ? draftSource : {};
  const sections = [];
  (Array.isArray(draft.sections) ? draft.sections : []).forEach((section, index) => {
    const normalized = normalizeShareReportSection(section, `草稿 ${index + 1}`);
    if (normalized) {
      sections.push(normalized);
    }
  });
  if (!sections.length && draft.html) {
    sections.push({
      title: localizeKnownDisplayText("HTML 草稿"),
      body: stringValue(draft.html).trim(),
      items: [],
      tone: "",
      display: "technical",
    });
  }
  if (draft.print_css) {
    sections.push({
      title: localizeKnownDisplayText("Print CSS"),
      body: stringValue(draft.print_css).trim(),
      items: [],
      tone: "",
      display: "technical",
    });
  }
  if (draft.disclaimer) {
    sections.push({
      title: "免责声明",
      body: stringValue(draft.disclaimer).trim(),
      items: [],
      tone: "accent",
      display: "text",
    });
  }
  const meta = [
    { label: "Draft", value: draft.format },
    { label: "Chart ID", value: draft.chart_id },
    { label: "Storage", value: draft.storage },
  ].filter((item) => stringValue(item.value).trim());
  const copyText = stringValue(draft.copy_text).trim()
    || [draft.title, ...sections.map((section) => [section.title, section.body, ...section.items].filter(Boolean).join("\n"))]
      .filter(Boolean)
      .join("\n\n");
  return {
    available: meta.length > 0 || sections.length > 0 || !!copyText,
    meta,
    sections,
    copyText,
  };
}

function normalizeShareReport(report) {
  const safeReport = report && typeof report === "object" ? report : {};
  const structuredSections = collectShareReportSections(safeReport);
  const legacy = parseLegacyShareReport(safeReport);
  const sections = structuredSections.length ? structuredSections : legacy.sections;
  const title = localizeKnownDisplayText(stringValue(
    safeReport.title || safeReport.heading || safeReport.report_title || legacy.title || "本地分享报告",
  ).trim());
  const summary = stringValue(
    safeReport.summary || safeReport.abstract || safeReport.overview || safeReport.lead || legacy.summary,
  ).trim();
  const note = stringValue(
    safeReport.disclaimer || safeReport.notice || safeReport.safety_note || legacy.note,
  ).trim();
  const meta = [
    { label: "Report", value: safeReport.report_type },
    { label: "Chart ID", value: safeReport.chart_id || safeReport.report_id },
    { label: "Mode", value: safeReport.mode },
    { label: "Storage", value: safeReport.storage },
  ].filter((item) => stringValue(item.value).trim());
  const draft = normalizeShareReportDraft(
    safeReport.pdf_report_draft || safeReport.advanced_draft || safeReport.draft || safeReport.pdfDraft,
  );
  const copyText = stringValue(safeReport.copy_text || safeReport.text).trim()
    || [title, summary, note, ...sections.map((section) => [section.title, section.body, ...section.items].filter(Boolean).join("\n"))]
      .filter(Boolean)
      .join("\n\n");
  const copyHtml = stringValue(safeReport.copy_html || safeReport.html).trim();
  return {
    title,
    summary,
    note,
    meta,
    sections,
    copyText,
    copyHtml,
    draft,
  };
}

function shareReportHasContent(report) {
  const view = normalizeShareReport(report);
  return Boolean(view.copyText || view.copyHtml || view.sections.length || view.draft.available);
}

function renderShareReportMeta(items) {
  const chips = (Array.isArray(items) ? items : []).filter((item) => stringValue(item?.value).trim());
  if (!chips.length) {
    return `<span class="share-report-chip">${escapeHtml(displayCopy("本地草稿，仅在当前浏览器可见", "Local draft, visible only in this browser"))}</span>`;
  }
  return chips
    .map(
      (item) => `
        <span class="share-report-chip">
          <strong>${escapeHtml(localizeKnownDisplayText(item.label))}</strong>
          <span>${escapeHtml(localizeKnownDisplayValue(item.value))}</span>
        </span>
      `,
    )
    .join("");
}

function renderShareReportCard(section) {
  const items = (section.items || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
  const toneClass = section.tone === "accent" ? " share-report-card--accent" : "";
  const technicalClass = section.display === "technical" ? " share-report-card--technical" : "";
  const labelHtml = section.tone === "accent"
    ? `<span class="share-report-card__label">${escapeHtml(displayCopy("重点", "Key"))}</span>`
    : "";
  const bodyHtml = section.body
    ? section.display === "technical"
      ? `<pre class="share-report-card__code">${escapeHtml(section.body)}</pre>`
      : `<p>${escapeHtml(localizeKnownDisplayText(section.body))}</p>`
    : "";
  return `
    <article class="share-report-card${toneClass}${technicalClass}">
      ${labelHtml}
      <h3>${escapeHtml(localizeKnownDisplayText(section.title))}</h3>
      ${bodyHtml}
      ${items ? `<ul>${items}</ul>` : ""}
    </article>
  `;
}

function setShareReportCopyStatus(message) {
  if (els.shareReportCopyStatus) {
    els.shareReportCopyStatus.textContent = message;
  }
}

async function copyTextToClipboard(value) {
  const text = stringValue(value).trim();
  if (!text) {
    throw new Error("Nothing to copy");
  }
  if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return;
  }
  throw new Error("Clipboard API unavailable");
}

async function copyShareReport(kind) {
  const view = state.shareReportView || normalizeShareReport({});
  const copyMap = {
    text: { label: "分享文案", value: view.copyText },
    html: { label: "HTML 草稿", value: view.copyHtml },
    draft: { label: "PDF 草稿提纲", value: view.draft.copyText },
  };
  const target = copyMap[kind];
  if (!target || !stringValue(target.value).trim()) {
    setShareReportCopyStatus(`当前没有可复制的${target?.label || "内容"}。`);
    return;
  }
  try {
    await copyTextToClipboard(target.value);
    setShareReportCopyStatus(`已复制${target.label}。`);
  } catch (error) {
    setShareReportCopyStatus(`${target.label}复制失败。`);
    writeLog(els.toolLog, error.message);
  }
}

function setActionUnavailable(button, unavailable, message) {
  if (!button) {
    return;
  }
  button.disabled = false;
  button.classList?.toggle?.("is-unavailable", Boolean(unavailable));
  button.setAttribute?.("aria-disabled", unavailable ? "true" : "false");
  if (message) {
    button.title = message;
  } else {
    button.removeAttribute?.("title");
  }
  if (unavailable && message) {
    button.setAttribute?.("data-unavailable-message", message);
  } else {
    button.removeAttribute?.("data-unavailable-message");
  }
}

function renderCommercialInterestSummary() {
  if (!els.commercialInterestSummary) {
    renderCommercialPathOverview();
    return;
  }
  const growthMetrics = state.growthMetrics || state.monetizationMetrics?.product_metrics?.public_metrics?.growth_metrics || {};
  const monetizationMetrics = state.monetizationMetrics || {};
  const gateStatus = state.monetizationGate?.gate_status || "unknown";
  const gateReasons = friendlyMonetizationReasons(state.monetizationGate?.blocked_reasons || []);
  const upstreamMemberInterest = numberValue(growthMetrics.member_interest_count);
  const phase14MemberInterest = numberValue(monetizationMetrics.member_interest_count);
  const pricingViewCount = numberValue(monetizationMetrics.pricing_view_count);
  const offerClickCount = numberValue(monetizationMetrics.offer_click_count);
  const nextStepCopy = gateStatus === "experiment"
    ? displayCopy(
      "右侧已经开放第 14 阶段仅记录兴趣，可继续采集会员、课程和合作兴趣。",
      "Phase 14 interest-only collection is open. Continue collecting membership, course, and partnership interest.",
    )
    : displayCopy(
      "右侧当前以预览说明为主，等产品化门槛通过后才会开始写入第 14 阶段事件。",
      "The right side is currently preview-only. Phase 14 events are written only after productization gates pass.",
    );

  els.commercialInterestSummary.innerHTML = `
    <section class="mini">
      <strong>${escapeHtml(displayCopy("上游兴趣信号", "Upstream interest signals"))}：${escapeHtml(localizedNumber(upstreamMemberInterest))}</strong>
      <p>${escapeHtml(displayCopy("这个按钮写入 growth 侧，用来判断内测用户是否愿意继续了解学习型权益。", "This button writes to growth metrics to test whether beta users want to learn about benefit tiers."))}</p>
      <small>${escapeHtml(displayCopy("它不会触发支付，也不会自动进入会员阶段。", "It does not trigger payment or automatically open membership."))}</small>
    </section>
    <section class="mini">
      <strong>${escapeHtml(displayCopy("商业化阶段", "Monetization stage"))}：${escapeHtml(monetizationGateStatusLabel(gateStatus))}</strong>
      <p>${escapeHtml(nextStepCopy)}</p>
      <small>${escapeHtml(gateReasons[0] || displayCopy("当前未发现额外阻塞。", "No extra blocker is currently reported."))}</small>
    </section>
    <section class="mini">
      <strong>${escapeHtml(displayCopy("第 15 阶段前置指标", "Phase 15 prerequisite metrics"))}</strong>
      <p>${escapeHtml(displayCopy("会员兴趣", "Membership interest"))} ${escapeHtml(localizedNumber(phase14MemberInterest))} · ${escapeHtml(displayCopy("权益浏览", "Benefit views"))} ${escapeHtml(localizedNumber(pricingViewCount))} · ${escapeHtml(displayCopy("权益点击", "Benefit clicks"))} ${escapeHtml(localizedNumber(offerClickCount))}</p>
      <small>${escapeHtml(displayCopy("支付准备阶段只看仅记录兴趣指标，不看真实收入。", "Payment readiness uses interest-only metrics, not real revenue."))}</small>
    </section>
  `;
  renderCommercialPathOverview();
}

function renderCommercialPathOverview() {
  const monetizationStatus = state.monetizationGate?.gate_status || "unknown";
  const paymentStatus = state.paymentGate?.gate_status || "unknown";
  const hasLead = numberValue(state.monetizationMetrics?.business_lead_count) > 0;
  const hasTier = Boolean((state.membershipTiers?.tiers || []).length);
  const orderStatus = state.sandboxOrder?.order_status || "";
  const orderStarted = Boolean(state.sandboxOrder?.order_id);
  const orderCompleted = ["paid_sandbox", "refunded", "canceled", "failed"].includes(orderStatus);
  const steps = [
    {
      label: displayCopy("线索", "Lead"),
      title: displayCopy("提交商务线索", "Submit business lead"),
      detail: monetizationStatus === "experiment"
        ? displayCopy("可写入第 14 阶段线索池", "Can write to the phase 14 lead pool")
        : displayCopy("等待商业化实验开放", "Waiting for the monetization experiment"),
      className: hasLead ? "is-completed" : monetizationStatus === "experiment" ? "is-active" : "is-blocked",
    },
    {
      label: displayCopy("权益", "Benefits"),
      title: displayCopy("选择会员权益层", "Choose a benefit tier"),
      detail: hasTier
        ? displayCopy("权益目录已从会员接口读取", "Benefit tiers are loaded from the membership API")
        : displayCopy("等待会员权益接口", "Waiting for membership tiers"),
      className: hasTier ? "is-completed" : "is-blocked",
    },
    {
      label: displayCopy("沙箱", "Sandbox"),
      title: displayCopy("创建沙箱订单", "Create sandbox order"),
      detail: paymentStatus === "sandbox"
        ? displayCopy("可创建沙箱模拟订单", "Can create mock_sandbox orders")
        : displayCopy("等待支付准备闸门", "Waiting for the payment readiness gate"),
      className: paymentStatus === "sandbox" ? "is-active" : "is-blocked",
    },
    {
      label: displayCopy("结果", "Result"),
      title: displayCopy("演示支付、取消或退款", "Simulate payment, cancel, or refund"),
      detail: orderStarted
        ? displayStatusValue(orderStatus)
        : displayCopy("尚未创建沙箱订单", "No sandbox order yet"),
      className: orderCompleted ? "is-completed" : orderStarted ? "is-active" : "is-blocked",
    },
  ];

  if (els.commercialPathSteps) {
    els.commercialPathSteps.innerHTML = steps
      .map((step, index) => `
        <section class="commercial-step ${step.className}">
          <span>${escapeHtml(String(index + 1))}</span>
          <div>
            <small>${escapeHtml(step.label)}</small>
            <strong>${escapeHtml(step.title)}</strong>
            <p>${escapeHtml(step.detail)}</p>
          </div>
        </section>
      `)
      .join("");
  }

  if (els.commercialPathSummary) {
    const summary = paymentStatus === "sandbox"
      ? displayCopy(
        "当前路径可从线索采集进入会员权益选择，并完成沙箱订单演示。",
        "This path can collect a lead, choose a benefit tier, and complete a sandbox order demo.",
      )
      : displayCopy(
        "当前路径会展示真实接口状态；未达门槛时只显示阻断原因，不创建真实支付。",
        "This path shows real API state. When gates are blocked it shows reasons and never creates real payment.",
      );
    els.commercialPathSummary.textContent = summary;
  }

  if (els.commercialPathMetrics) {
    const chips = [
      [displayCopy("线索", "Leads"), state.monetizationMetrics?.business_lead_count],
      [displayCopy("会员兴趣", "Member interest"), state.monetizationMetrics?.member_interest_count],
      [displayCopy("订单", "Orders"), state.paymentMetrics?.order_count],
      [displayCopy("沙箱成功", "Sandbox paid"), state.paymentMetrics?.paid_sandbox_count],
    ];
    els.commercialPathMetrics.innerHTML = chips
      .map(([label, value]) => `
        <span class="monetization-chip">
          <strong>${escapeHtml(localizedNumber(value))}</strong>
          <span>${escapeHtml(label)}</span>
        </span>
      `)
      .join("");
  }
}

function isPublicActive() {
  return ["preview", "live"].includes(state.publicStatus?.launch_status);
}

function selectedMode(args) {
  if (allowedModes.has(args.mode)) {
    return args.mode;
  }
  return allowedModes.has(els.modeSelect.value) ? els.modeSelect.value : "plain";
}

function normalizeToolArguments(args) {
  return {
    question: args.question || args.query || "语音占问",
    datetime: args.datetime || nowIso(),
    timezone: args.timezone || userTimezone(),
    location: args.location || null,
    category: args.category || null,
    mode: selectedMode(args),
    tester_id: args.tester_id || els.testerId.value.trim() || null,
    invite_code: args.invite_code || els.inviteCode.value.trim() || null,
  };
}

function currentTesterIdentity() {
  return {
    tester_id: els.testerId.value.trim() || "",
    invite_code: els.inviteCode.value.trim() || "",
  };
}

function resolvedVisitorId() {
  const testerId = els.testerId.value.trim();
  if (testerId) {
    return testerId;
  }
  const nickname = els.visitorNickname?.value.trim() || "";
  if (nickname) {
    return `visitor_${nickname.slice(0, 40)}`;
  }
  try {
    if (typeof window !== "undefined" && window.localStorage) {
      const storageKey = "liuren_public_visitor_id";
      const existingId = window.localStorage.getItem(storageKey);
      if (existingId) {
        return existingId;
      }
      const generatedId = `visitor_${Math.random().toString(36).slice(2, 10)}`;
      window.localStorage.setItem(storageKey, generatedId);
      return generatedId;
    }
  } catch (error) {
    writeLog(els.toolLog, String(error));
  }
  return "visitor_local_browser";
}

function sendRealtimeEvent(event) {
  if (!state.dc || state.dc.readyState !== "open") {
    throw new Error("Realtime data channel is not open");
  }
  state.dc.send(JSON.stringify(event));
}

function renderPersonaLines(lines) {
  const personaLines = Array.isArray(lines) ? lines : [];
  state.personaCardLines = personaLines;
  if (els.personaCards) {
    els.personaCards.classList.toggle(
      "persona-cards--expanded",
      state.personaCardsExpanded && personaLines.length > defaultPersonaCardCount,
    );
  }
  if (els.personaCardsToggle) {
    els.personaCardsToggle.classList.toggle("hidden", personaLines.length <= defaultPersonaCardCount);
    els.personaCardsToggle.textContent = state.personaCardsExpanded ? "收起" : "展开全部";
  }
  if (!personaLines.length) {
    els.personaCards.innerHTML = '<p class="muted">本次暂无角色化输出。</p>';
    return;
  }
  const visiblePersonaLines = state.personaCardsExpanded
    ? personaLines
    : personaLines.slice(0, defaultPersonaCardCount);
  els.personaCards.innerHTML = visiblePersonaLines
    .map(
      (line) => {
        const generalSlug = generalSlugMap[line.general] || "fallback";
        const imageUrl = generalSlugMap[line.general]
          ? `/static/realtime/assets/persona-bg/general-${generalSlug}@2x.webp`
          : "";
        const imageStyle = imageUrl ? `--persona-card-image: url('${imageUrl}');` : "";
        return `
        <section class="persona-card persona-card--${escapeHtml(generalSlug)}">
          <div class="persona-card__overlay"></div>
          <div class="persona-card__content" style="${imageStyle}">
            <p class="persona-card__eyebrow">${escapeHtml(line.general)}</p>
            <strong class="persona-card__title">${escapeHtml(line.role_name)}</strong>
            <p class="persona-card__line">${escapeHtml(line.line)}</p>
            <small class="persona-card__note">${escapeHtml(line.safety_note)}</small>
          </div>
        </section>
      `;
      },
    )
    .join("");
}

function renderLearningCards(cards) {
  if (!cards || !cards.length) {
    els.learningCards.innerHTML = '<p class="muted">暂无学习卡。</p>';
    return;
  }
  els.learningCards.innerHTML = cards
    .map(
      (card) => `
        <section class="mini">
          <strong>${escapeHtml(card.title)}</strong>
          <p>${escapeHtml(card.summary)}</p>
          <small>${escapeHtml((card.source_ids || []).join("、"))}</small>
        </section>
      `,
    )
    .join("");
}

function learningNodeStatusMeta(reviewStatus) {
  if (reviewStatus === "approved_for_mvp") {
    return { label: "可学", className: "approved" };
  }
  if (reviewStatus === "research_only") {
    return { label: "研究中", className: "research" };
  }
  return { label: reviewStatus || "待整理", className: "unknown" };
}

function getLearningNodes() {
  return state.learningPath?.nodes || [];
}

function getLearningNodeById(nodeId) {
  return getLearningNodes().find((node) => node.node_id === nodeId) || null;
}

function getLearningCardsForNode(node) {
  const cardIds = new Set(node?.learning_card_ids || []);
  return state.learningCardsCatalog.filter((card) => cardIds.has(card.card_id));
}

function summarizeLearningNode(node) {
  if (!node) {
    return "从推荐节点开始，先看骨架，再看细节。";
  }
  return learningTopicSummaries[node.topic] || `从 ${node.title || "这个节点"} 开始，先理解来源、案例和输出。`;
}

function getLearningNodeStats(node) {
  return {
    cardCount: (node?.learning_card_ids || []).length,
    sourceCount: (node?.source_ids || []).length,
    exampleCount: (node?.example_case_ids || []).length,
    outputCount: (node?.unlocked_outputs || []).length,
  };
}

function renderLearningPathSummary(nodes, recommended) {
  if (!els.learningPathSummary) {
    return;
  }
  if (!nodes.length) {
    els.learningPathSummary.innerHTML = '<p class="muted">暂无学习闯关节点。</p>';
    return;
  }
  const approvedCount = nodes.filter((node) => node.review_status === "approved_for_mvp").length;
  const researchCount = nodes.filter((node) => node.review_status === "research_only").length;
  els.learningPathSummary.innerHTML = `
    <section class="learning-path-card learning-path-summary-card">
      <p class="learning-path-eyebrow">学习闯关</p>
      <strong>共 ${nodes.length} 个节点，当前可学 ${approvedCount} 个，研究中 ${researchCount} 个</strong>
      <p>${escapeHtml(recommended ? `推荐下一步：${recommended.title}` : "推荐下一步：暂无可学节点")}</p>
    </section>
  `;
}

function renderLearningPathRecommended(node) {
  if (!els.learningPathRecommended) {
    return;
  }
  if (!node) {
    els.learningPathRecommended.innerHTML = '<p class="muted">当前暂无可学节点，请先浏览研究节点摘要。</p>';
    return;
  }
  const statusMeta = learningNodeStatusMeta(node.review_status);
  const readOnly = node.review_status === "research_only";
  const stats = getLearningNodeStats(node);
  els.learningPathRecommended.innerHTML = `
    <section class="learning-path-card learning-path-card-accent">
      <p class="learning-path-eyebrow">推荐下一步</p>
      <div class="learning-path-inline">
        <strong>${escapeHtml(node.title)}</strong>
        <span class="learning-path-badge ${statusMeta.className}">${escapeHtml(statusMeta.label)}</span>
      </div>
      <p>${escapeHtml(summarizeLearningNode(node))}</p>
      <div class="learning-path-meta">
        <p><strong>学习卡：</strong>${stats.cardCount}</p>
        <p><strong>出处：</strong>${stats.sourceCount}</p>
        <p><strong>示例：</strong>${stats.exampleCount}</p>
      </div>
      <button
        type="button"
        class="learning-path-action${readOnly ? " is-unavailable" : ""}"
        data-action="start-learning"
        data-node-id="${escapeHtml(node.node_id)}"
        aria-disabled="${readOnly ? "true" : "false"}"
        title="${escapeHtml(readOnly ? displayCopy("研究节点只能浏览，不能写入学习进度。", "Research nodes can be viewed but cannot write learning progress.") : displayCopy("开始这个学习节点。", "Start this learning node."))}"
      >${readOnly ? "暂不可学" : "开始学习"}</button>
    </section>
  `;
}

function renderLearningPathNodes(nodes) {
  if (!els.learningPathNodes) {
    return;
  }
  const listHtml = !nodes.length
    ? '<p class="muted">学习闯关暂不可用。</p>'
    : nodes
      .map((node) => {
        const statusMeta = learningNodeStatusMeta(node.review_status);
        const activeClass = node.node_id === state.selectedLearningNodeId ? " is-active" : "";
        const stats = getLearningNodeStats(node);
        return `
          <button
            type="button"
            class="learning-path-node${activeClass}"
            data-node-id="${escapeHtml(node.node_id)}"
            aria-pressed="${node.node_id === state.selectedLearningNodeId ? "true" : "false"}"
          >
            <span class="learning-path-node-main">
              <strong>${escapeHtml(node.title)}</strong>
              <small>${escapeHtml(summarizeLearningNode(node))}</small>
              <small>${stats.cardCount} 张学习卡 · ${stats.sourceCount} 个出处 · ${stats.exampleCount} 个示例</small>
            </span>
            <span class="learning-path-badge ${statusMeta.className}">${escapeHtml(statusMeta.label)}</span>
          </button>
        `;
      })
      .join("");
  els.learningPathNodes.innerHTML = listHtml;
}

function renderLearningPathDetail(node) {
  if (!els.learningPathDetail) {
    return;
  }
  if (!node) {
    els.learningPathDetail.innerHTML = '<p class="muted">点击节点查看详情。</p>';
    return;
  }
  const statusMeta = learningNodeStatusMeta(node.review_status);
  const readOnly = node.review_status === "research_only";
  const cards = getLearningCardsForNode(node);
  const stats = getLearningNodeStats(node);
  const cardHtml = state.learningCardsAvailable
    ? cards.length
      ? cards.map((card) => `
          <section class="learning-path-card learning-path-card-soft">
            <strong>${escapeHtml(card.title)}</strong>
            <p>${escapeHtml(card.summary)}</p>
            <small>${escapeHtml((card.tags || []).join("、"))}</small>
          </section>
        `).join("")
      : '<p class="muted">当前节点暂无关联学习卡。</p>'
    : '<p class="muted">关联学习卡暂不可用，请先阅读节点摘要与来源。</p>';
  els.learningPathDetail.innerHTML = `
    <section class="learning-path-card learning-path-detail-card">
      <div class="learning-path-inline">
        <h3>${escapeHtml(node.title)}</h3>
        <span class="learning-path-badge ${statusMeta.className}">${escapeHtml(statusMeta.label)}</span>
      </div>
      <p>${escapeHtml(summarizeLearningNode(node))}</p>
      <p class="muted">主题：${escapeHtml(node.topic || "未分类主题")}</p>
      <div class="learning-path-meta">
        <p><strong>学习卡：</strong>${stats.cardCount}</p>
        <p><strong>来源：</strong>${escapeHtml((node.source_ids || []).join("、") || "暂无")}</p>
        <p><strong>案例：</strong>${escapeHtml((node.example_case_ids || []).join("、") || "暂无")}</p>
        <p><strong>解锁输出：</strong>${escapeHtml((node.unlocked_outputs || []).join("、") || "暂无")}</p>
      </div>
      <p class="learning-path-detail-note">${
        readOnly ? "当前仅供研究参考，暂不写入学习进度。" : "可以先查看学习卡，再标记为已读。"
      }</p>
      <div class="learning-path-detail-actions">
        <button
          type="button"
          class="learning-path-action learning-path-action-secondary"
          data-action="view-cards"
          data-node-id="${escapeHtml(node.node_id)}"
        >查看学习卡</button>
        <button
          type="button"
          class="learning-path-action${readOnly ? " is-unavailable" : ""}"
          data-action="mark-read"
          data-node-id="${escapeHtml(node.node_id)}"
          aria-disabled="${readOnly ? "true" : "false"}"
          title="${escapeHtml(readOnly ? displayCopy("研究节点只能浏览，不能标记进度。", "Research nodes can be viewed but cannot be marked as progress.") : displayCopy("把这个学习节点标记为已读。", "Mark this learning node as read."))}"
        >${readOnly ? "研究阶段只读" : "记为已读"}</button>
      </div>
    </section>
    <section class="stack">
      <p class="learning-path-eyebrow">关联学习卡</p>
      ${cardHtml}
    </section>
  `;
}

function setLearningPathStatus(message) {
  if (els.learningPathStatus) {
    els.learningPathStatus.textContent = message;
  }
}

function learningProgressStatus(result, action, node) {
  if (result?.skipped) {
    return "研究节点当前仅供浏览，不记录进度。";
  }
  if (result?.stored === false || (result?.blocked_reasons || []).includes("productization_not_active")) {
    return "当前不保存进度，不影响浏览。";
  }
  if (action === "mark-read") {
    return `已标记 ${node?.title || "当前节点"} 为已读。`;
  }
  return `已开始 ${node?.title || "当前节点"}。`;
}

function learningCardsStatus(node) {
  if (!state.learningCardsAvailable) {
    return "关联学习卡暂不可用，请先阅读节点摘要与来源。";
  }
  if (!getLearningCardsForNode(node).length) {
    return "当前节点暂无关联学习卡。";
  }
  return "学习卡已在详情区展开。";
}

function renderLearningPathUnavailableState() {
  const unavailableMessage = escapeHtml(learningPathUnavailableCopy.message);
  if (els.learningPathSummary) {
    els.learningPathSummary.innerHTML = `<p class="muted">${unavailableMessage}</p>`;
  }
  if (els.learningPathRecommended) {
    els.learningPathRecommended.innerHTML = `<p class="muted">${unavailableMessage}</p>`;
  }
  if (els.learningPathNodes) {
    els.learningPathNodes.innerHTML = `<p class="muted">${unavailableMessage}</p>`;
  }
  if (els.learningPathDetail) {
    els.learningPathDetail.innerHTML = `<p class="muted">${escapeHtml(learningPathUnavailableCopy.detail)}</p>`;
  }
  setLearningPathStatus(learningPathUnavailableCopy.message);
}

function renderLearningPathState() {
  const nodes = getLearningNodes();
  const recommended = nodes.find((node) => node.review_status === "approved_for_mvp") || null;
  const selectedNode = getLearningNodeById(state.selectedLearningNodeId) || recommended || nodes[0] || null;
  if (!state.selectedLearningNodeId && selectedNode) {
    state.selectedLearningNodeId = selectedNode.node_id;
  }
  renderLearningPathSummary(nodes, recommended);
  renderLearningPathRecommended(recommended);
  renderLearningPathNodes(nodes);
  renderLearningPathDetail(selectedNode);
}

async function sendLearningPathProgress(nodeId, action) {
  const node = getLearningNodeById(nodeId);
  if (!node || node.review_status === "research_only") {
    setLearningPathStatus("研究节点当前仅供浏览，不记录进度。");
    return { skipped: true };
  }
  const payload = {
    visitor_id: resolvedVisitorId(),
    node_id: node.node_id,
    event_type: "learning_progress",
    status: action === "mark-read" ? "completed" : "started",
    mode: els.modeSelect.value,
    source: "realtime_frontend",
  };
  const response = await fetch("/api/learning/progress", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (response.ok) {
    return response.json();
  }
  throw new Error(`Learning progress failed: ${response.status}`);
}

function selectLearningPathNode(nodeId) {
  if (!getLearningNodeById(nodeId)) {
    return;
  }
  state.selectedLearningNodeId = nodeId;
  renderLearningPathState();
}

async function handleLearningPathAction(nodeId, action) {
  selectLearningPathNode(nodeId);
  try {
    const node = getLearningNodeById(nodeId);
    if (action === "view-cards") {
      setLearningPathStatus(learningCardsStatus(node));
      return;
    }
    const result = await sendLearningPathProgress(nodeId, action);
    setLearningPathStatus(learningProgressStatus(result, action, node));
  } catch (error) {
    setLearningPathStatus("学习进度记录失败。");
    writeLog(els.toolLog, error.message);
  }
}

function renderShareReport(report) {
  state.shareReportPayload = report && typeof report === "object" ? report : {};
  const view = normalizeShareReport(report);
  state.shareReportView = view;
  if (els.shareReportMeta) {
    els.shareReportMeta.innerHTML = renderShareReportMeta(view.meta);
  }
  if (els.shareReportLead) {
    const leadCopy = view.summary || displayCopy(
      "分享报告会把这次结果整理成可读卡片，方便你本地留存或复制。",
      "The share report organizes this result into readable local cards for saving or copying.",
    );
    const noteHtml = view.note ? `<p class="muted">${escapeHtml(localizeKnownDisplayText(view.note))}</p>` : "";
    els.shareReportLead.innerHTML = `
      <h3>${escapeHtml(localizeKnownDisplayText(view.title || "本地分享报告"))}</h3>
      <p>${escapeHtml(localizeKnownDisplayText(leadCopy))}</p>
      ${noteHtml}
    `;
  }
  if (els.shareReportCards) {
    els.shareReportCards.innerHTML = view.sections.length
      ? view.sections.map((section) => renderShareReportCard(section)).join("")
      : `
        <article class="share-report-card share-report-card--empty">
          <p class="muted">${escapeHtml(displayCopy("当前还没有分享报告。起课完成后，会在这里展示摘要、提示和可复制内容。", "No share report yet. After a session, summary, prompts, and copyable content appear here."))}</p>
        </article>
      `;
  }
  if (els.copyShareReportTextBtn) {
    setActionUnavailable(
      els.copyShareReportTextBtn,
      !view.copyText,
      view.copyText
        ? displayCopy("复制本地分享文案。", "Copy local share text.")
        : displayCopy("完成一次起课后才会生成可复制文案。", "A copyable text appears after one completed session."),
    );
  }
  if (els.copyShareReportHtmlBtn) {
    setActionUnavailable(
      els.copyShareReportHtmlBtn,
      !view.copyHtml,
      view.copyHtml
        ? displayCopy("复制网页草稿。", "Copy the web draft.")
        : displayCopy("完成一次起课后才会生成网页草稿。", "A web draft appears after one completed session."),
    );
  }
  if (els.shareReportDraftDetails) {
    const hasDraft = view.draft.available;
    els.shareReportDraftDetails.classList.toggle("hidden", !hasDraft);
    if (!hasDraft) {
      els.shareReportDraftDetails.open = false;
    }
  }
  if (els.shareReportDraftMeta) {
    els.shareReportDraftMeta.innerHTML = renderShareReportMeta(view.draft.meta);
  }
  if (els.shareReportDraftCards) {
    els.shareReportDraftCards.innerHTML = view.draft.sections.length
      ? view.draft.sections.map((section) => renderShareReportCard(section)).join("")
      : `
        <article class="share-report-card share-report-card--empty">
          <p class="muted">${escapeHtml(displayCopy("当前没有高级草稿。", "No advanced draft yet."))}</p>
        </article>
      `;
  }
  if (els.copyShareReportDraftBtn) {
    setActionUnavailable(
      els.copyShareReportDraftBtn,
      !view.draft.copyText,
      view.draft.copyText
        ? displayCopy("复制文档草稿提纲。", "Copy the document draft outline.")
        : displayCopy("当前没有高级草稿可复制。", "No advanced draft is available to copy."),
    );
  }
  setShareReportCopyStatus(
    view.copyText
      ? "复制只在当前浏览器本地进行，不生成外链。"
      : "当前还没有可复制的分享文案。",
  );
}

function renderBetaStatus(result) {
  const interpretation = result?.interpretation || {};
  const scope = interpretation.beta_scope || {};
  const safety = result?.safety || interpretation.safety_notice || {};
  const blockedReasons = interpretation.blocked_reasons || [];
  const lines = [
    `内测状态：${displayStatusValue(scope.status)}`,
    `安全动作：${displayStatusValue(safety.action)}`,
    `反馈令牌：${interpretation.feedback_token || ""}`,
  ];
  if (scope.reason) {
    lines.push(`范围说明：${scope.reason}`);
  }
  if (blockedReasons.length) {
    lines.push(`阻断原因：${blockedReasons.join("、")}`);
  }
  els.safetyState.textContent = lines.join("\n");
}

function renderEntertainment(result) {
  const entertainment = result.interpretation?.entertainment || {};
  const personaLines = entertainment.persona_lines || [];
  const learningCards = entertainment.learning_cards || [];
  const hasLearningMaterials = personaLines.length > 0 || learningCards.length > 0;
  state.personaCardLines = personaLines;
  state.personaCardsExpanded = false;
  renderPersonaLines(personaLines);
  renderLearningCards(learningCards);
  renderShareReport(entertainment.share_report || {});
  if (els.learningMaterials) {
    els.learningMaterials.open = hasLearningMaterials;
  }
}

function renderRenYuLocalizedViews() {
  if (state.shareReportPayload) {
    renderShareReport(state.shareReportPayload);
  }
  if (state.offerCatalog) {
    syncMonetizationInterestButtons(state.offerCatalog);
    renderOfferCatalog(state.offerCatalog);
  }
  renderMonetizationMetrics(state.monetizationMetrics);
  renderMonetizationGate(state.monetizationGate);
  renderCommercialInterestSummary();
  renderPaymentGate(state.paymentGate);
  renderPaymentMetrics(state.paymentMetrics);
  renderMembershipTiers(state.membershipTiers);
  renderBusinessLeadOutcome(state.businessLeadResult, state.businessLeadPayload || {});
  renderSandboxOrderDetail(state.sandboxPaymentResult);
  renderCommercialPathOverview();
  renderPublicStatus(state.publicStatus);
  renderProductizationGate(state.productizationGate);
  if (state.betaConfig && els.betaNotice) {
    els.betaNotice.textContent = localizeKnownDisplayText(state.betaConfig.tester_notice || "受限内测：传统文化学习与娱乐体验。");
  }
}

function markdownToReadableHtml(markdown) {
  const lines = String(markdown || "")
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
  if (!lines.length) {
    return '<p class="muted">暂无解释结果。</p>';
  }
  const sections = [];
  let current = { title: "解读", items: [] };
  for (const line of lines) {
    const heading = line.replace(/^#{1,4}\s*/, "").replace(/\*/g, "").trim();
    if (/^#{1,4}\s/.test(line) || /^\*{0,2}[^*：:]{2,12}\*{0,2}[：:]?\s*$/.test(line) || /^【.+】$/.test(line)) {
      if (current.items.length) {
        sections.push(current);
      }
      current = { title: heading.replace(/^【|】$/g, "").replace(/[：:]$/, ""), items: [] };
    } else {
      current.items.push(line.replace(/^[-*]\s*/, "").replace(/\*/g, ""));
    }
  }
  if (current.items.length) {
    sections.push(current);
  }
  return sections
    .map((section) => {
      const body = section.items.length > 1
        ? `<ul>${section.items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`
        : `<p>${escapeHtml(section.items[0] || "")}</p>`;
      return `<section><h2>${escapeHtml(section.title)}</h2>${body}</section>`;
    })
    .join("");
}

function localFallbackSummary(result) {
  const interpretation = result.interpretation || {};
  const lines = [
    interpretation.overview,
    ...(interpretation.plain_explanation || []),
    ...(interpretation.action_prompts || []),
  ].filter(Boolean);
  return lines.join("\n");
}

function renderQuestionFocus(result) {
  const focus = result.interpretation?.question_focus || {};
  const question = focus.display_question || focus.question || "";
  const terms = focus.focus_terms || [];
  if (!question) {
    return "";
  }
  const termText = terms.length ? `<span>焦点：${escapeHtml(terms.join("、"))}</span>` : "";
  return `
    <section class="question-focus">
      <h2>本次问题</h2>
      <p>${escapeHtml(question)}</p>
      ${termText}
    </section>
  `;
}

function renderReadableResult(result) {
  const readableText = result.openrouter?.content || localFallbackSummary(result);
  els.explainResult.innerHTML = renderQuestionFocus(result) + markdownToReadableHtml(readableText);
}

function renderNonLiurenQuestion(result) {
  const interpretation = result.interpretation || {};
  const prompts = interpretation.action_prompts || [];
  els.explainResult.innerHTML = `
    <section>
      <h2>这个问题不适合起课</h2>
      <p>${escapeHtml(interpretation.overview || "这个输入框只用于具体事项占问。")}</p>
      <ul>${prompts.map((prompt) => `<li>${escapeHtml(prompt)}</li>`).join("")}</ul>
    </section>
  `;
  els.transcript.textContent = "";
  if (els.learningMaterials) {
    els.learningMaterials.open = false;
  }
}

function renderTextInterpretResult(result) {
  state.lastToolResult = result;
  if ((result.interpretation?.blocked_reasons || []).includes("non_liuren_question")) {
    renderNonLiurenQuestion(result);
    writeLog(els.toolLog, {
      endpoint: "/api/liuren/text-interpret",
      blocked_reasons: result.interpretation.blocked_reasons,
      deepseek: result.openrouter,
      latency_ms: result.latency_ms,
    });
    writeLog(els.interpretationPreview, result.interpretation);
    writeLog(els.debugJson, result);
    renderEntertainment(result);
    renderBetaStatus(result);
    return;
  }
  const deepseekContent = result.openrouter?.content || "";
  els.transcript.textContent = deepseekContent || result.interpretation?.overview || "";
  renderReadableResult(result);
  writeLog(els.toolLog, {
    endpoint: "/api/liuren/text-interpret",
    deepseek: result.openrouter,
    chart_id: result.chart?.chart_id,
    latency_ms: result.latency_ms,
  });
  writeLog(els.interpretationPreview, result.interpretation);
  writeLog(els.debugJson, result);
  renderEntertainment(result);
  renderBetaStatus(result);
}

async function loadBetaConfig() {
  try {
    const response = await fetch("/api/beta/config");
    if (!response.ok) {
      throw new Error(`Beta config failed: ${response.status}`);
    }
    state.betaConfig = await response.json();
    els.betaNotice.textContent = localizeKnownDisplayText(state.betaConfig.tester_notice || "受限内测：传统文化学习与娱乐体验。");
  } catch (error) {
    els.betaNotice.textContent = localizeKnownDisplayText("受限内测：配置暂不可用，请按安全边界测试。");
    writeLog(els.toolLog, error.message);
  }
}

async function loadBetaReport() {
  try {
    const response = await fetch("/api/beta/report");
    if (response.ok) {
      state.betaReport = await response.json();
    }
  } catch (error) {
    writeLog(els.toolLog, error.message);
  }
}

function renderOpsStatus(status) {
  if (!els.opsPauseNotice) {
    return;
  }
  if (status?.status === "paused") {
    els.opsPauseNotice.classList.remove("hidden");
    els.opsPauseNotice.textContent = status.notice || "当前运维状态暂停讲盘，仅提供安全说明与反馈入口。";
  } else {
    els.opsPauseNotice.classList.add("hidden");
  }
}

async function loadOpsStatus() {
  try {
    const response = await fetch("/api/ops/status");
    if (!response.ok) {
      throw new Error(`Ops status failed: ${response.status}`);
    }
    state.opsStatus = await response.json();
    renderOpsStatus(state.opsStatus);
    renderCanaryTaskPanel();
  } catch (error) {
    writeLog(els.toolLog, error.message);
  }
}

function renderPublicStatus(status) {
  if (!els.publicFeedbackNotice) {
    return;
  }
  const prefix = status?.launch_status || "unknown";
  if (status?.launch_status === "paused") {
    els.publicFeedbackNotice.textContent = localizeKnownDisplayText("公开最小可用版本已暂停；当前仅提供安全说明、维护说明和反馈入口。");
  } else if (isPublicActive()) {
    els.publicFeedbackNotice.textContent = localizeKnownDisplayText(
      "公开最小可用版本：传统文化学习与娱乐体验，不保存录音；反馈、课式和删除请求仅用于产品复盘。",
    );
  } else {
    els.publicFeedbackNotice.textContent = displayCopy(
      `公开最小可用版本未开放：${displayStatusValue(prefix)}。可查看范围说明与安全边界。`,
      `Public build is not open: ${displayStatusValue(prefix)}. Check scope and safety boundaries.`,
    );
  }
}

async function loadPublicStatus() {
  try {
    const response = await fetch("/api/public/status");
    if (!response.ok) {
      throw new Error(`Public status failed: ${response.status}`);
    }
    state.publicStatus = await response.json();
    renderPublicStatus(state.publicStatus);
  } catch (error) {
    writeLog(els.toolLog, error.message);
  }
}

function renderProductizationGate(gate) {
  if (!els.visitorProfileStatus) {
    return;
  }
  els.visitorProfileStatus.textContent = gate?.gate_status === "experiment"
    ? "可以保存本地偏好。"
    : "偏好保存暂未开放，不影响起课使用。";
}

async function loadProductizationGate() {
  try {
    const response = await fetch("/api/productization/gate");
    if (!response.ok) {
      throw new Error(`Productization gate failed: ${response.status}`);
    }
    state.productizationGate = await response.json();
    renderProductizationGate(state.productizationGate);
  } catch (error) {
    writeLog(els.toolLog, error.message);
  }
}

async function loadLearningPath() {
  if (!els.learningPathPanel || !els.learningPathSummary || !els.learningPathRecommended || !els.learningPathNodes || !els.learningPathDetail || !els.learningPathStatus) {
    return;
  }
  setLearningPathStatus("正在加载学习闯关...");
  try {
    const [pathResponse, cardsResponse] = await Promise.allSettled([
      fetch("/api/learning/path"),
      fetch("/api/learning/cards"),
    ]);
    if (pathResponse.status !== "fulfilled" || !pathResponse.value.ok) {
      const status = pathResponse.status === "fulfilled" ? pathResponse.value.status : "network";
      throw new Error(`Learning path failed: ${status}`);
    }
    state.learningPath = await pathResponse.value.json();
    state.selectedLearningNodeId = null;
    if (cardsResponse.status === "fulfilled" && cardsResponse.value.ok) {
      const cardsPayload = await cardsResponse.value.json();
      state.learningCardsCatalog = cardsPayload.learning_cards || [];
      state.learningCardsAvailable = true;
      setLearningPathStatus("学习闯关已就绪。");
    } else {
      state.learningCardsCatalog = [];
      state.learningCardsAvailable = false;
      setLearningPathStatus("学习卡暂不可用，仍可浏览节点摘要。");
    }
    renderLearningPathState();
  } catch (error) {
    state.learningPath = { nodes: [] };
    state.learningCardsCatalog = [];
    state.learningCardsAvailable = false;
    state.selectedLearningNodeId = null;
    renderLearningPathUnavailableState();
    writeLog(els.toolLog, error.message);
  }
}

function renderMonetizationGate(gate) {
  if (!els.monetizationStatus) {
    renderCommercialPathOverview();
    return;
  }
  const gateStatus = gate?.gate_status || "unknown";
  const friendlyReasons = friendlyMonetizationReasons(gate?.blocked_reasons || []);
  if (els.monetizationGateBadge) {
    const statusClass = monetizationGateStatusClass(gateStatus);
    els.monetizationGateBadge.className = `canary-status-badge${statusClass ? ` ${statusClass}` : ""}`;
    els.monetizationGateBadge.textContent = monetizationGateStatusLabel(gateStatus);
  }
  if (els.monetizationOverview) {
    els.monetizationOverview.textContent = gateStatus === "experiment"
      ? displayCopy("当前已进入仅记录兴趣的商业化实验，可继续记录权益预览和合作兴趣。", "The interest-only monetization experiment is active; continue recording benefit previews and partnership interest.")
      : gateStatus === "paused"
        ? displayCopy("商业化实验已暂停，先处理风险或版权问题，再恢复兴趣采集。", "The monetization experiment is paused. Resolve risk or copyright issues before collecting interest again.")
        : displayCopy("商业化实验尚未启动，先满足产品化、灰测和公开发布的上游门槛。", "The monetization experiment has not started. Productization, canary, and public launch gates must pass first.");
  }
  if (els.monetizationReasonList) {
    const reasons = friendlyReasons.length ? friendlyReasons : [displayCopy("当前未发现额外阻塞说明。", "No extra blocker is currently reported.")];
    els.monetizationReasonList.innerHTML = reasons
      .slice(0, 6)
      .map((reason) => `<span class="canary-milestone">${escapeHtml(reason)}</span>`)
      .join("");
  }
  if (!els.monetizationStatus.textContent) {
    els.monetizationStatus.textContent = gateStatus === "experiment"
      ? displayCopy("只记录兴趣、体验偏好和合作线索，不产生真实支付。", "Only interest, experience preference, and partnership leads are recorded. No real payment is created.")
      : displayCopy("当前仍是权益预览阶段，不会产生支付或会员开通。", "This remains a benefit preview. It does not create payment or activate membership.");
  }
  renderCommercialInterestSummary();
  renderCommercialPathOverview();
}

async function loadMonetizationGate() {
  try {
    const response = await fetch("/api/monetization/gate");
    if (!response.ok) {
      throw new Error(`Monetization gate failed: ${response.status}`);
    }
    state.monetizationGate = await response.json();
    renderMonetizationGate(state.monetizationGate);
  } catch (error) {
    writeLog(els.toolLog, error.message);
  }
}

function renderMonetizationMetrics(metrics) {
  if (els.monetizationMetricsHeadline) {
    if (metrics) {
      els.monetizationMetricsHeadline.textContent = displayCopy(
        `已记录 ${numberValue(metrics.event_count)} 条第 14 阶段事件，${numberValue(metrics.business_lead_count)} 条商务线索。`,
        `${localizedNumber(metrics.event_count)} phase 14 events and ${localizedNumber(metrics.business_lead_count)} business leads recorded.`,
      );
    } else {
      els.monetizationMetricsHeadline.textContent = displayCopy("实验指标暂不可用。", "Experiment metrics are unavailable.");
    }
  }
  if (els.monetizationMetricsList) {
    const chips = [
      [displayCopy("会员兴趣", "Member interest"), numberValue(metrics?.member_interest_count)],
      [displayCopy("课程兴趣", "Course interest"), numberValue(metrics?.course_interest_count)],
      [displayCopy("商务兴趣", "Business interest"), numberValue(metrics?.business_interest_count)],
      [displayCopy("权益浏览", "Benefit views"), numberValue(metrics?.pricing_view_count)],
      [displayCopy("权益点击", "Benefit clicks"), numberValue(metrics?.offer_click_count)],
      [displayCopy("线索数", "Leads"), numberValue(metrics?.business_lead_count)],
    ];
    els.monetizationMetricsList.innerHTML = chips
      .map(
        ([label, value]) => `
          <span class="monetization-chip">
            <strong>${escapeHtml(localizedNumber(value))}</strong>
            <span>${escapeHtml(label)}</span>
          </span>
        `,
      )
      .join("");
  }
  renderCommercialInterestSummary();
  renderCommercialPathOverview();
}

async function loadGrowthMetrics() {
  try {
    const response = await fetch("/api/growth/metrics");
    if (!response.ok) {
      throw new Error(`Growth metrics failed: ${response.status}`);
    }
    state.growthMetrics = await response.json();
    renderCommercialInterestSummary();
  } catch (error) {
    renderCommercialInterestSummary();
    writeLog(els.toolLog, error.message);
  }
}

async function loadMonetizationMetrics() {
  try {
    const response = await fetch("/api/monetization/metrics");
    if (!response.ok) {
      throw new Error(`Monetization metrics failed: ${response.status}`);
    }
    state.monetizationMetrics = await response.json();
    renderMonetizationMetrics(state.monetizationMetrics);
  } catch (error) {
    renderMonetizationMetrics(null);
    writeLog(els.toolLog, error.message);
  }
}

function syncMonetizationInterestButtons(catalog) {
  const offersById = new Map((catalog?.offers || []).map((offer) => [offer.offer_id, offer]));
  els.monetizationInterestButtons.forEach((button) => {
    const offer = offersById.get(button.dataset.offerId);
    const enabledEventTypes = Array.isArray(offer?.enabled_event_types) ? offer.enabled_event_types : [];
    const isEnabled = Boolean(offer) && enabledEventTypes.includes(button.dataset.eventType);
    setActionUnavailable(
      button,
      !isEnabled,
      isEnabled
        ? `${localizeKnownDisplayText(offer.title)}：${monetizationEventLabel(button.dataset.eventType)}`
        : displayCopy("当前权益目录未开放这个快捷动作。", "This quick action is not open in the current offer catalog."),
    );
  });
}

function monetizationQuickActionAvailability(eventType, offerId) {
  const offers = state.offerCatalog?.offers || [];
  const offer = offers.find((item) => item.offer_id === offerId);
  if (!offer) {
    return {
      available: false,
      reason: displayCopy("当前权益目录未开放这个快捷动作。", "This quick action is not open in the current offer catalog."),
    };
  }
  const enabledEventTypes = Array.isArray(offer.enabled_event_types) ? offer.enabled_event_types : [];
  if (!enabledEventTypes.includes(eventType)) {
    return {
      available: false,
      reason: displayCopy("当前权益目录未开放这个快捷动作。", "This quick action is not open in the current offer catalog."),
    };
  }
  return { available: true, reason: "" };
}

function bindOfferCatalogActions() {
  if (typeof document.querySelectorAll !== "function") {
    return;
  }
  document.querySelectorAll("[data-offer-preview]").forEach((button) => {
    button.addEventListener("click", () => recordMonetizationEvent(button.dataset.offerPreview, button.dataset.offerId));
  });
}

function renderOfferCatalog(catalog) {
  if (!els.offerCatalogList) {
    return;
  }
  const offers = catalog?.offers || [];
  if (!offers.length) {
    els.offerCatalogList.innerHTML = `<section class="offer-card-empty"><p class="muted">${escapeHtml(displayCopy("商业化权益预览暂不可用。", "Commercial benefit previews are unavailable."))}</p></section>`;
    return;
  }
  const noticeHtml = catalog?.catalog_notice
    ? `<section class="offer-card-empty"><p class="muted">${escapeHtml(localizeKnownDisplayText(catalog.catalog_notice))}</p></section>`
    : "";
  const offerHtml = offers
    .map((offer) => {
      const enabledEventTypes = Array.isArray(offer.enabled_event_types) ? offer.enabled_event_types : [];
      const previewButtons = enabledEventTypes
        .filter((eventType) => ["pricing_view", "offer_click"].includes(eventType))
        .map((eventType) => {
          const label = eventType === "pricing_view"
            ? displayCopy("查看权益边界", "View benefit boundary")
            : displayCopy("查看适用场景", "View use cases");
          return `<button type="button" class="offer-card-action" data-offer-preview="${escapeHtml(eventType)}" data-offer-id="${escapeHtml(offer.offer_id)}">${escapeHtml(label)}</button>`;
        })
        .join("");
      return `
        <section class="offer-card">
          <div class="offer-card-head">
            <div>
              <span class="canary-task-stage">${escapeHtml(monetizationOfferCategoryLabel(offer.category))}</span>
              <strong>${escapeHtml(localizeKnownDisplayText(offer.title))}</strong>
            </div>
            <span class="canary-task-chip is-ready">${escapeHtml(offer.interest_only ? displayCopy("仅记录兴趣", "Interest only") : displayCopy("实验中", "Experiment"))}</span>
          </div>
          <p class="offer-card-copy">${escapeHtml(localizeKnownDisplayText(offer.summary))}</p>
          <div class="canary-milestones">
            ${enabledEventTypes.map((eventType) => `<span class="canary-milestone">${escapeHtml(monetizationEventLabel(eventType))}</span>`).join("")}
          </div>
          <p class="offer-card-note">${escapeHtml(localizeKnownDisplayText(offer.safety_note))}</p>
          ${previewButtons ? `<div class="offer-card-actions">${previewButtons}</div>` : ""}
        </section>
      `;
    })
    .join("");
  els.offerCatalogList.innerHTML = `${noticeHtml}${offerHtml}`;
  bindOfferCatalogActions();
}

async function loadOfferCatalog() {
  if (!els.offerCatalogList) {
    return;
  }
  try {
    const response = await fetch("/api/monetization/offers");
    if (!response.ok) {
      throw new Error(`Offer catalog failed: ${response.status}`);
    }
    state.offerCatalog = await response.json();
    syncMonetizationInterestButtons(state.offerCatalog);
    renderOfferCatalog(state.offerCatalog);
  } catch (error) {
    syncMonetizationInterestButtons(null);
    renderOfferCatalog(null);
    writeLog(els.toolLog, error.message);
  }
}

async function recordMonetizationEvent(eventType, offerId) {
  const availability = monetizationQuickActionAvailability(eventType, offerId);
  if (!availability.available) {
    if (els.monetizationStatus) {
      els.monetizationStatus.textContent = availability.reason;
    }
    renderCommercialPathOverview();
    return;
  }
  const payload = {
    visitor_id: resolvedVisitorId(),
    event_type: eventType,
    offer_id: offerId,
    mode: els.modeSelect.value,
    source: "realtime_frontend",
  };
  try {
    const response = await fetch("/api/monetization/event", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Monetization event failed: ${response.status}`);
    }
    const result = await response.json();
    if (result.gate) {
      state.monetizationGate = result.gate;
      renderMonetizationGate(state.monetizationGate);
    }
    if (result.metrics) {
      state.monetizationMetrics = result.metrics;
      renderMonetizationMetrics(state.monetizationMetrics);
    }
    els.monetizationStatus.textContent = result.stored
      ? displayCopy(
        `${monetizationEventLabel(eventType)}已记录，仅用于实验复盘。`,
        `${monetizationEventLabel(eventType)} recorded for experiment review only.`,
      )
      : displayCopy(
        `未写入第 14 阶段：${friendlyMonetizationReasons(result.blocked_reasons || []).join("；") || "当前实验未开放。"}`,
        `Phase 14 was not written: ${friendlyMonetizationReasons(result.blocked_reasons || []).join("; ") || "the experiment is not open."}`,
      )
    ;
    renderCommercialPathOverview();
  } catch (error) {
    els.monetizationStatus.textContent = displayCopy("商业化兴趣记录失败。", "Commercial interest recording failed.");
    writeLog(els.toolLog, error.message);
  }
}

async function submitBusinessLead() {
  const contactNickname = els.businessLeadNickname?.value.trim() || "";
  const channel = els.businessLeadChannel?.value.trim() || "";
  const needSummary = els.businessLeadSummary?.value.trim() || "";
  if (!contactNickname || !needSummary) {
    if (els.businessLeadStatus) {
      els.businessLeadStatus.textContent = displayCopy(
        "请先补全联系人昵称和需求摘要，再提交商务线索。",
        "Add a contact nickname and need summary before submitting the business lead.",
      );
    }
    return;
  }
  const payload = {
    visitor_id: resolvedVisitorId(),
    contact_nickname: contactNickname,
    channel: channel || "web",
    need_summary: needSummary,
    offer_id: "offer-b2b-v0",
    source: "realtime_frontend",
  };
  if (els.submitBusinessLeadBtn) {
    els.submitBusinessLeadBtn.disabled = true;
  }
  try {
    const response = await fetch("/api/business/lead", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Business lead failed: ${response.status}`);
    }
    const result = await response.json();
    if (result.gate) {
      state.monetizationGate = result.gate;
      renderMonetizationGate(state.monetizationGate);
    }
    if (result.metrics) {
      state.monetizationMetrics = result.metrics;
      renderMonetizationMetrics(state.monetizationMetrics);
    }
    state.businessLeadResult = result;
    state.businessLeadPayload = payload;
    els.businessLeadStatus.textContent = result.stored
      ? displayCopy("商务线索已记录，仅用于渠道实验复盘。", "Business lead recorded for channel experiment review only.")
      : displayCopy(
        `商务线索未记录：${friendlyMonetizationReasons(result.blocked_reasons || []).join("；") || "当前实验未开放。"}`,
        `Business lead was not recorded: ${friendlyMonetizationReasons(result.blocked_reasons || []).join("; ") || "the experiment is not open."}`,
      )
    ;
    renderBusinessLeadOutcome(result, payload);
    renderCommercialPathOverview();
    if (result.stored && els.businessLeadSummary) {
      els.businessLeadSummary.value = "";
    }
  } catch (error) {
    els.businessLeadStatus.textContent = displayCopy("商务线索记录失败。", "Business lead recording failed.");
    writeLog(els.toolLog, error.message);
  } finally {
    if (els.submitBusinessLeadBtn) {
      els.submitBusinessLeadBtn.disabled = false;
    }
  }
}

function renderBusinessLeadOutcome(result, submittedPayload) {
  if (!els.businessLeadOutcome) {
    return;
  }
  if (!result) {
    els.businessLeadOutcome.innerHTML = `
      <section class="commerce-outcome">
        <span class="canary-task-chip is-ready">${escapeHtml(displayCopy("待提交", "Ready to submit"))}</span>
        <p>${escapeHtml(displayCopy("填写联系人、渠道和需求摘要后，会调用商务线索接口；未开放时只返回阻断原因。", "After contact, channel, and need summary are filled, the business lead API is called; blocked gates return reasons only."))}</p>
      </section>
    `;
    return;
  }
  const lead = result?.lead || {};
  const stored = result?.stored === true;
  const reasonText = friendlyMonetizationReasons(result?.blocked_reasons || []).join(selectedDisplayLanguage() === "en" ? "; " : "；");
  const rows = stored
    ? [
      [displayCopy("线索编号", "Lead ID"), lead.lead_id || displayCopy("已生成", "Generated")],
      [displayCopy("联系人", "Contact"), lead.contact_nickname || submittedPayload.contact_nickname],
      [displayCopy("渠道", "Channel"), lead.channel || submittedPayload.channel],
      [displayCopy("写入状态", "Write state"), displayCopy("已写入实验线索池", "Written to experiment lead pool")],
    ]
    : [
      [displayCopy("写入状态", "Write state"), displayCopy("未写入", "Not written")],
      [displayCopy("原因", "Reason"), reasonText || displayCopy("当前实验未开放", "The experiment is not open")],
      [displayCopy("保留路径", "Available path"), displayCopy("可继续查看权益和支付闸门", "Benefit and payment gate views remain available")],
    ];
  els.businessLeadOutcome.innerHTML = `
    <section class="commerce-outcome ${stored ? "is-completed" : "is-blocked"}">
      <span class="canary-task-chip ${stored ? "is-completed" : "is-blocked"}">${escapeHtml(stored ? displayCopy("已记录", "Recorded") : displayCopy("未写入", "Not written"))}</span>
      ${rows.map(([label, value]) => `
        <div class="commerce-kv">
          <span>${escapeHtml(label)}</span>
          <strong>${escapeHtml(value)}</strong>
        </div>
      `).join("")}
    </section>
  `;
}

function renderPaymentGate(gate) {
  const gateStatus = gate?.gate_status || "unknown";
  const reasons = friendlyMonetizationReasons(gate?.blocked_reasons || []);
  if (els.paymentGateBadge) {
    const statusClass = paymentGateStatusClass(gateStatus);
    els.paymentGateBadge.className = `canary-status-badge${statusClass ? ` ${statusClass}` : ""}`;
    els.paymentGateBadge.textContent = paymentGateStatusLabel(gateStatus);
  }
  if (els.paymentGateStatus) {
    els.paymentGateStatus.textContent = gateStatus === "sandbox"
      ? displayCopy("支付准备状态：沙箱可用；可以创建模拟订单，不会真实扣款。", "Payment readiness: sandbox ready. You can create mock orders; no real charge is made.")
      : displayCopy(
        `支付准备状态：${paymentGateStatusLabel(gateStatus)}；${reasons[0] || "等待上游兴趣指标或合规门槛。"}`,
        `Payment readiness: ${paymentGateStatusLabel(gateStatus)}; ${reasons[0] || "waiting for upstream interest or compliance gates."}`,
      );
  }
  if (els.paymentGateReasonList) {
    const reasonItems = reasons.length ? reasons : [displayCopy("沙箱演示不产生真实扣款。", "The sandbox demo never creates a real charge.")];
    els.paymentGateReasonList.innerHTML = reasonItems
      .slice(0, 6)
      .map((reason) => `<span class="canary-milestone">${escapeHtml(reason)}</span>`)
      .join("");
  }
  if (els.paymentCapabilitiesList) {
    const capabilities = gate?.enabled_capabilities || [];
    els.paymentCapabilitiesList.innerHTML = capabilities.length
      ? capabilities.map((capability) => `<span class="canary-milestone">${escapeHtml(localizeKnownDisplayText(capability))}</span>`).join("")
      : `<span class="canary-milestone">${escapeHtml(displayCopy("当前无可用支付能力", "No payment capability is currently available"))}</span>`;
  }
  syncSandboxActionState();
  renderCommercialPathOverview();
}

async function loadPaymentGate() {
  try {
    const response = await fetch("/api/payment/gate");
    if (!response.ok) {
      throw new Error(`Payment gate failed: ${response.status}`);
    }
    state.paymentGate = await response.json();
    renderPaymentGate(state.paymentGate);
  } catch (error) {
    renderPaymentGate(null);
    writeLog(els.toolLog, error.message);
  }
}

function renderPaymentMetrics(metrics) {
  if (!els.paymentMetricsList) {
    renderCommercialPathOverview();
    return;
  }
  const chips = [
    [displayCopy("订单数", "Orders"), metrics?.order_count],
    [displayCopy("等待支付", "Pending"), metrics?.pending_payment_count],
    [displayCopy("沙箱成功", "Sandbox paid"), metrics?.paid_sandbox_count],
    [displayCopy("退款", "Refunds"), metrics?.refunded_count],
    [displayCopy("阻断", "Blocked"), metrics?.blocked_order_count],
  ];
  els.paymentMetricsList.innerHTML = chips
    .map(([label, value]) => `
      <span class="monetization-chip">
        <strong>${escapeHtml(localizedNumber(value))}</strong>
        <span>${escapeHtml(label)}</span>
      </span>
    `)
    .join("");
  renderCommercialPathOverview();
}

async function loadPaymentMetrics() {
  try {
    const response = await fetch("/api/payment/metrics");
    if (!response.ok) {
      throw new Error(`Payment metrics failed: ${response.status}`);
    }
    state.paymentMetrics = await response.json();
    renderPaymentMetrics(state.paymentMetrics);
  } catch (error) {
    state.paymentMetrics = null;
    renderPaymentMetrics(null);
    writeLog(els.toolLog, error.message);
  }
}

function renderMembershipTiers(payload) {
  if (!els.membershipTiersList) {
    return;
  }
  const tiers = payload?.tiers || [];
  if (tiers.length) {
    els.membershipTiersList.innerHTML = tiers
      .map((tier) => {
        const rights = Array.isArray(tier.rights_preview) ? tier.rights_preview : [];
        return `
          <section class="tier-row">
            <div class="tier-row-main">
              <span class="canary-task-stage">${escapeHtml(monetizationOfferCategoryLabel(tier.category))}</span>
              <strong>${escapeHtml(localizeKnownDisplayText(tier.title))}</strong>
              <p>${escapeHtml(localizeKnownDisplayText(tier.summary))}</p>
              <div class="canary-milestones">
                ${rights.map((right) => `<span class="canary-milestone">${escapeHtml(localizeKnownDisplayText(right))}</span>`).join("")}
              </div>
            </div>
            <div class="tier-row-meta">
              <span class="canary-task-chip is-ready">${escapeHtml(displayCopy("仅沙箱演示", "Sandbox only"))}</span>
              <small>${escapeHtml(displayCopy(`高风险解锁：${boolLabel(tier.high_risk_unlocked)}`, `High-risk unlocked: ${boolLabel(tier.high_risk_unlocked)}`))}</small>
              <small>${escapeHtml(displayCopy(`复杂规则解锁：${boolLabel(tier.unreviewed_complex_rules_unlocked)}`, `Complex rules unlocked: ${boolLabel(tier.unreviewed_complex_rules_unlocked)}`))}</small>
            </div>
          </section>
        `;
      })
      .join("");
    if (els.paymentTierSelect) {
      els.paymentTierSelect.innerHTML = tiers
        .map((tier) => `<option value="${escapeHtml(tier.tier_id)}">${escapeHtml(localizeKnownDisplayText(tier.title))}</option>`)
        .join("");
      if (!els.paymentTierSelect.value && tiers[0]?.tier_id) {
        els.paymentTierSelect.value = tiers[0].tier_id;
      }
      els.paymentTierSelect.disabled = false;
    }
    syncSandboxActionState();
    renderCommercialPathOverview();
    return;
  }
  els.membershipTiersList.innerHTML = `<p class="muted">${escapeHtml(displayCopy("会员权益预览暂不可用。", "Membership previews are unavailable."))}</p>`;
  if (els.paymentTierSelect) {
    els.paymentTierSelect.innerHTML = "";
    els.paymentTierSelect.value = "";
    els.paymentTierSelect.disabled = true;
  }
  syncSandboxActionState();
  renderCommercialPathOverview();
}

async function loadMembershipTiers() {
  if (!els.membershipTiersList) {
    return;
  }
  try {
    const response = await fetch("/api/membership/tiers");
    if (!response.ok) {
      throw new Error(`Membership tiers failed: ${response.status}`);
    }
    state.membershipTiers = await response.json();
    renderMembershipTiers(state.membershipTiers);
  } catch (error) {
    state.membershipTiers = null;
    renderMembershipTiers(null);
    writeLog(els.toolLog, error.message);
  }
}

function syncSandboxActionState() {
  const hasTier = Boolean(els.paymentTierSelect?.value);
  if (els.startSandboxCheckoutBtn) {
    setActionUnavailable(
      els.startSandboxCheckoutBtn,
      !hasTier,
      hasTier
        ? displayCopy("创建一笔沙箱订单；若闸门未开放，会显示阻断原因。", "Create a sandbox order; if the gate is closed, the blocker is shown.")
        : displayCopy("暂无可用会员层级，点击可查看原因。", "No membership tier is available; click to see why."),
    );
  }
  const orderStatus = state.sandboxOrder?.order_status || "";
  const hasOrder = Boolean(state.sandboxOrder?.order_id);
  const pendingMessage = hasOrder
    ? displayCopy(`当前订单状态为${displayStatusValue(orderStatus)}。`, `Current order status is ${displayStatusValue(orderStatus)}.`)
    : displayCopy("请先创建沙箱订单。", "Create a sandbox order first.");
  if (els.confirmSandboxPaymentBtn) {
    setActionUnavailable(
      els.confirmSandboxPaymentBtn,
      !hasTier || orderStatus !== "pending_payment",
      hasTier && orderStatus === "pending_payment"
        ? displayCopy("把当前沙箱订单标记为支付成功。", "Mark the current sandbox order as paid.")
        : pendingMessage,
    );
  }
  if (els.failSandboxPaymentBtn) {
    setActionUnavailable(
      els.failSandboxPaymentBtn,
      !hasTier || orderStatus !== "pending_payment",
      hasTier && orderStatus === "pending_payment"
        ? displayCopy("把当前沙箱订单标记为支付失败。", "Mark the current sandbox order as failed.")
        : pendingMessage,
    );
  }
  if (els.cancelSandboxOrderBtn) {
    setActionUnavailable(
      els.cancelSandboxOrderBtn,
      !hasTier || orderStatus !== "pending_payment",
      hasTier && orderStatus === "pending_payment"
        ? displayCopy("取消当前待支付沙箱订单。", "Cancel the current pending sandbox order.")
        : pendingMessage,
    );
  }
  if (els.refundSandboxOrderBtn) {
    setActionUnavailable(
      els.refundSandboxOrderBtn,
      !hasTier || orderStatus !== "paid_sandbox",
      hasTier && orderStatus === "paid_sandbox"
        ? displayCopy("为已支付沙箱订单演示退款。", "Demonstrate a refund for a paid sandbox order.")
        : pendingMessage,
    );
  }
}

function explainSandboxTierUnavailable(actionLabel) {
  const message = displayCopy(
    `暂无可用会员层级，无法执行${actionLabel}。请先确认会员权益接口是否返回可演示层级。`,
    `No membership tier is available, so ${actionLabel} cannot run. Check that the membership tier API returns a demo tier.`,
  );
  if (els.sandboxOrderStatus) {
    els.sandboxOrderStatus.textContent = message;
  }
  if (els.sandboxOrderDetail) {
    els.sandboxOrderDetail.innerHTML = `
      <section class="commerce-outcome is-blocked">
        <span class="canary-task-chip is-blocked">${escapeHtml(displayCopy("缺少权益层", "Missing tier"))}</span>
        <p>${escapeHtml(message)}</p>
      </section>
    `;
  }
  return message;
}

function hasAvailableSandboxTier(actionLabel) {
  if (els.paymentTierSelect?.value) {
    return true;
  }
  explainSandboxTierUnavailable(actionLabel);
  return false;
}

function requireSandboxOrder(actionLabel) {
  if (!hasAvailableSandboxTier(actionLabel)) {
    return "";
  }
  const orderId = state.sandboxOrder?.order_id || "";
  if (orderId) {
    return orderId;
  }
  if (els.sandboxOrderStatus) {
    els.sandboxOrderStatus.textContent = displayCopy(
      `请先创建沙箱订单，再执行${actionLabel}。`,
      `Create a sandbox order before ${actionLabel}.`,
    );
  }
  return "";
}

function explainSandboxGateBlocked() {
  const reasons = friendlyMonetizationReasons(state.paymentGate?.blocked_reasons || []);
  const message = displayCopy(
    `沙箱订单暂不可创建：${reasons.join("；") || "支付准备闸门未开放。"}`,
    `Sandbox order cannot be created yet: ${reasons.join("; ") || "the payment readiness gate is not open."}`,
  );
  if (els.sandboxOrderStatus) {
    els.sandboxOrderStatus.textContent = message;
  }
  renderSandboxOrderDetail({ stored: false, blocked_reasons: state.paymentGate?.blocked_reasons || [] });
  return message;
}

function requirePendingSandboxOrder(actionLabel) {
  const orderId = requireSandboxOrder(actionLabel);
  if (!orderId) {
    return "";
  }
  if (state.sandboxOrder?.order_status !== "pending_payment") {
    if (els.sandboxOrderStatus) {
      els.sandboxOrderStatus.textContent = displayCopy(
        `当前订单不是待支付状态，不能执行${actionLabel}。`,
        `The current order is not pending payment, so ${actionLabel} cannot run.`,
      );
    }
    renderSandboxOrderDetail(state.sandboxPaymentResult || { order: state.sandboxOrder });
    return "";
  }
  if (!canAttemptCheckout()) {
    explainSandboxGateBlocked();
    return "";
  }
  return orderId;
}

function requirePaidSandboxOrder(actionLabel) {
  const orderId = requireSandboxOrder(actionLabel);
  if (!orderId) {
    return "";
  }
  if (state.sandboxOrder?.order_status !== "paid_sandbox") {
    if (els.sandboxOrderStatus) {
      els.sandboxOrderStatus.textContent = displayCopy(
        `当前订单还不是沙箱支付成功状态，不能执行${actionLabel}。`,
        `The current order is not paid in the sandbox yet, so ${actionLabel} cannot run.`,
      );
    }
    renderSandboxOrderDetail(state.sandboxPaymentResult || { order: state.sandboxOrder });
    return "";
  }
  if (!canAttemptCheckout()) {
    explainSandboxGateBlocked();
    return "";
  }
  return orderId;
}

function updateSandboxOrderStatus(result) {
  if (!els.sandboxOrderStatus) {
    return;
  }
  const order = result?.order || {};
  if (order.order_id) {
    state.sandboxOrder = order;
  }
  if (result?.gate) {
    state.paymentGate = result.gate;
    renderPaymentGate(state.paymentGate);
  }
  if (result?.metrics) {
    state.paymentMetrics = result.metrics;
    renderPaymentMetrics(state.paymentMetrics);
  }
  state.sandboxPaymentResult = result || null;
  els.sandboxOrderStatus.textContent = result?.stored === false
    ? displayCopy(
      `沙箱支付未启用：${friendlyMonetizationReasons(result.blocked_reasons || []).join("；") || "当前实验未开放。"}`,
      `Sandbox payment is not enabled: ${friendlyMonetizationReasons(result.blocked_reasons || []).join("; ") || "the experiment is not open."}`,
    )
    : displayCopy(
      `订单 ${order.order_id || displayStatusValue("unknown")}：${displayStatusValue(order.order_status)}`,
      `Order ${order.order_id || displayStatusValue("unknown")}: ${displayStatusValue(order.order_status)}`,
    );
  renderSandboxOrderDetail(result);
  syncSandboxActionState();
  renderCommercialPathOverview();
}

function renderSandboxOrderDetail(result) {
  if (!els.sandboxOrderDetail) {
    return;
  }
  const order = result?.order || state.sandboxOrder || {};
  if (!order.order_id) {
    const gateReasons = friendlyMonetizationReasons(state.paymentGate?.blocked_reasons || []);
    els.sandboxOrderDetail.innerHTML = `
      <section class="commerce-outcome ${canAttemptCheckout() ? "" : "is-blocked"}">
        <span class="canary-task-chip ${canAttemptCheckout() ? "is-ready" : "is-blocked"}">${escapeHtml(canAttemptCheckout() ? displayCopy("待创建", "Ready to create") : displayCopy("闸门阻断", "Gate blocked"))}</span>
        <p>${escapeHtml(canAttemptCheckout()
          ? displayCopy("选择权益层后，可以创建一笔沙箱订单。", "Choose a tier, then create a sandbox order.")
          : gateReasons[0] || displayCopy("沙箱支付暂未开放。", "Sandbox payment is not open yet."))}</p>
      </section>
    `;
    return;
  }
  const rows = [
    [displayCopy("订单编号", "Order ID"), displayIdentifier(order.order_id)],
    [displayCopy("权益层", "Tier"), localizeKnownDisplayText(getTierTitle(order.tier_id)) || displayIdentifier(order.tier_id)],
    [displayCopy("状态", "Status"), displayStatusValue(order.order_status)],
    [displayCopy("金额", "Amount"), formatAmountCents(order.amount_cents, order.currency)],
    [displayCopy("服务商", "Provider"), displayStatusValue(order.provider || "mock_sandbox")],
  ];
  if (order.timestamp) {
    rows.push([displayCopy("时间", "Time"), order.timestamp]);
  }
  if (order.reason) {
    rows.push([displayCopy("原因", "Reason"), localizeKnownDisplayText(order.reason)]);
  }
  const eventType = result?.event?.event_type ? localizeKnownDisplayValue(result.event.event_type) : "";
  els.sandboxOrderDetail.innerHTML = `
    <section class="commerce-outcome ${orderStatusClass(order.order_status)}">
      <span class="canary-task-chip ${orderStatusClass(order.order_status)}">${escapeHtml(displayStatusValue(order.order_status))}</span>
      ${rows.map(([label, value]) => `
        <div class="commerce-kv">
          <span>${escapeHtml(label)}</span>
          <strong>${escapeHtml(value)}</strong>
        </div>
      `).join("")}
      ${eventType ? `<p class="muted">${escapeHtml(displayCopy("最近事件", "Latest event"))}：${escapeHtml(eventType)}</p>` : ""}
    </section>
  `;
}

function getTierTitle(tierId) {
  const tier = (state.membershipTiers?.tiers || []).find((item) => item.tier_id === tierId);
  return tier?.title || "";
}

async function callPaymentEndpoint(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Payment endpoint failed: ${response.status}`);
  }
  const result = await response.json();
  updateSandboxOrderStatus(result);
  return result;
}

async function startSandboxCheckout() {
  const tierId = els.paymentTierSelect?.value || "";
  if (!hasAvailableSandboxTier("创建沙箱订单")) {
    return;
  }
  if (!canAttemptCheckout()) {
    explainSandboxGateBlocked();
    return;
  }
  const payload = {
    visitor_id: resolvedVisitorId(),
    tier_id: tierId,
    source: "realtime_frontend",
  };
  try {
    if (els.startSandboxCheckoutBtn) {
      els.startSandboxCheckoutBtn.disabled = true;
    }
    await callPaymentEndpoint("/api/payment/checkout", payload);
  } catch (error) {
    els.sandboxOrderStatus.textContent = displayCopy("创建沙箱订单失败。", "Creating the sandbox order failed.");
    writeLog(els.toolLog, error.message);
  } finally {
    syncSandboxActionState();
  }
}

async function confirmSandboxPayment(outcome) {
  const orderId = requirePendingSandboxOrder("支付确认");
  if (!orderId) {
    return;
  }
  try {
    await callPaymentEndpoint("/api/payment/sandbox/confirm", { order_id: orderId, outcome });
  } catch (error) {
    els.sandboxOrderStatus.textContent = displayCopy("沙箱支付确认失败。", "Sandbox payment confirmation failed.");
    writeLog(els.toolLog, error.message);
  }
}

async function cancelSandboxOrder() {
  const orderId = requirePendingSandboxOrder("取消订单");
  if (!orderId) {
    return;
  }
  try {
    await callPaymentEndpoint("/api/payment/cancel", { order_id: orderId, reason: "frontend_cancel_demo" });
  } catch (error) {
    els.sandboxOrderStatus.textContent = displayCopy("取消沙箱订单失败。", "Canceling the sandbox order failed.");
    writeLog(els.toolLog, error.message);
  }
}

async function refundSandboxOrder() {
  const orderId = requirePaidSandboxOrder("退款演示");
  if (!orderId) {
    return;
  }
  try {
    await callPaymentEndpoint("/api/payment/refund", { order_id: orderId, reason: "frontend_refund_demo" });
  } catch (error) {
    els.sandboxOrderStatus.textContent = displayCopy("沙箱退款演示失败。", "Sandbox refund demo failed.");
    writeLog(els.toolLog, error.message);
  }
}

async function saveVisitorProfile() {
  const payload = {
    visitor_id: resolvedVisitorId(),
    nickname: els.visitorNickname?.value.trim() || null,
    mode_preference: els.modeSelect.value,
    source: "realtime_frontend",
  };
  try {
    const response = await fetch("/api/visitor/profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Visitor profile failed: ${response.status}`);
    }
    const result = await response.json();
    els.visitorProfileStatus.textContent = result.stored
      ? "偏好已保存。"
      : friendlyBlockedReason(result.blocked_reasons, "偏好暂未保存，不影响起课使用。");
  } catch (error) {
    els.visitorProfileStatus.textContent = "偏好暂未保存，不影响起课使用。";
    writeLog(els.toolLog, error.message);
  }
}

async function validateCanaryAccess() {
  const payload = {
    tester_id: els.testerId.value.trim() || null,
    invite_code: els.inviteCode.value.trim() || null,
  };
  const response = await fetch("/api/canary/validate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Canary validation failed: ${response.status}`);
  }
  const validation = await response.json();
  if (!validation.allowed) {
    setStatus("canary_denied");
    writeLog(els.toolLog, {
      allowed: validation.allowed,
      blocked_reasons: friendlyMonetizationReasons(validation.blocked_reasons || []),
    });
  }
  return validation;
}

async function loadCanaryRunConfig() {
  if (!els.canaryTaskList) {
    return;
  }
  try {
    const response = await fetch("/api/canary/run/config");
    if (!response.ok) {
      throw new Error(`Canary run config failed: ${response.status}`);
    }
    state.canaryRunConfig = await response.json();
    await loadCanaryTaskStatus();
  } catch (error) {
    state.canaryRunConfig = null;
    state.canaryTaskStatus = null;
    renderCanaryTaskFallback("灰测任务暂不可用。");
    writeLog(els.toolLog, error.message);
  }
}

function renderCanaryTaskFallback(message) {
  if (els.canaryStatusBadge) {
    els.canaryStatusBadge.textContent = "任务暂不可用";
    els.canaryStatusBadge.className = "canary-status-badge is-blocked";
  }
  if (els.canaryProgressLabel) {
    els.canaryProgressLabel.textContent = "0 / 4 已完成";
  }
  if (els.canaryOverview) {
    els.canaryOverview.textContent = message;
  }
  if (els.canaryProgressBarFill) {
    els.canaryProgressBarFill.style.width = "0%";
  }
  if (els.canaryMilestones) {
    els.canaryMilestones.innerHTML = "";
  }
  if (els.canaryTaskList) {
    els.canaryTaskList.innerHTML = `<li class="canary-task-card is-blocked"><p class="canary-task-copy">${escapeHtml(message)}</p></li>`;
  }
}

function canaryTaskStatusLabel(status) {
  if (status === "completed") {
    return "已完成";
  }
  if (status === "blocked") {
    return "未开放";
  }
  if (status === "ready") {
    return "可执行";
  }
  return "待完成";
}

function canaryTaskStatusClass(status) {
  if (status === "completed") {
    return "is-completed";
  }
  if (status === "blocked") {
    return "is-blocked";
  }
  return "is-ready";
}

function friendlyCanaryReason(reasons, fallback) {
  const reasonSet = new Set(reasons || []);
  if (reasonSet.has("invalid_canary_credentials")) {
    return "测试编号或邀请码未通过校验，当前不会按你的身份追踪任务。";
  }
  if (reasonSet.has("expert_review_pending")) {
    return "当前批次仍在专家审校，受邀测试尚未开放。";
  }
  if (reasonSet.has("beta_manual_review_pending")) {
    return "当前版本仍在内测手工审查，任务区先展示计划与门槛。";
  }
  if (reasonSet.has("canary_not_active")) {
    return "当前不是灰测窗口，先保留任务说明与门槛。";
  }
  return fallback;
}

function buildCanaryStatusQuery() {
  const identity = currentTesterIdentity();
  const params = [];
  if (identity.tester_id) {
    params.push(`tester_id=${encodeURIComponent(identity.tester_id)}`);
  }
  if (identity.invite_code) {
    params.push(`invite_code=${encodeURIComponent(identity.invite_code)}`);
  }
  return params.length ? `?${params.join("&")}` : "";
}

async function loadCanaryTaskStatus() {
  if (!els.canaryTaskList) {
    return;
  }
  try {
    const response = await fetch(`/api/canary/tasks/status${buildCanaryStatusQuery()}`);
    if (!response.ok) {
      throw new Error(`Canary task status failed: ${response.status}`);
    }
    state.canaryTaskStatus = await response.json();
    renderCanaryTaskPanel();
  } catch (error) {
    state.canaryTaskStatus = null;
    renderCanaryTaskFallback("灰测状态暂不可用，请稍后重试。");
    writeLog(els.toolLog, error.message);
  }
}

function canaryActionLabel(task) {
  if (task.completed) {
    if (task.cta_action === "focus_share_report") {
      return "查看分享报告";
    }
    if (task.cta_action === "focus_feedback") {
      return "查看反馈区";
    }
    return "查看任务";
  }
  return task.cta_label || "继续";
}

function localizedCanaryTaskCopy(value) {
  return stringValue(value)
    .replaceAll("story", "故事")
    .replaceAll("mentor", "导师");
}

function derivedCanaryTaskStatus(task) {
  const baseStatus = task.status || "todo";
  if (baseStatus === "completed" || baseStatus === "blocked") {
    return baseStatus;
  }
  if (task.task_id === "C11-T02" && ["story", "mentor"].includes(els.modeSelect.value)) {
    return "ready";
  }
  if (task.task_id === "C11-T03" && shareReportHasContent(state.lastToolResult?.interpretation?.entertainment?.share_report)) {
    return "ready";
  }
  if (task.task_id === "C11-T04" && state.lastToolResult) {
    return "ready";
  }
  return "todo";
}

function renderCanaryMilestones(status) {
  if (!els.canaryMilestones) {
    return;
  }
  const progress = status?.cohort_progress || {};
  const thresholds = progress.thresholds || {};
  els.canaryMilestones.innerHTML = [
    `会话 ${progress.session_count || 0} / ${thresholds.min_sessions || 20}`,
    `反馈 ${progress.feedback_submit_count || 0} / ${thresholds.min_feedback_submissions || 10}`,
    `分享 ${progress.share_report_count || 0} / ${thresholds.min_share_reports || 3}`,
  ]
    .map((line) => `<span class="canary-milestone">${escapeHtml(line)}</span>`)
    .join("");
}

function renderCanaryTaskPanel() {
  if (!els.canaryTaskList) {
    return;
  }
  const config = state.canaryRunConfig;
  const status = state.canaryTaskStatus;
  if (!config || !status) {
    renderCanaryTaskFallback("灰测任务暂不可用。");
    return;
  }

  const completedCount = status?.tester_progress?.completed_task_count || 0;
  const totalCount = status?.tester_progress?.total_task_count || (config.tester_tasks || []).length || 4;
  const percent = totalCount ? Math.round((completedCount / totalCount) * 100) : 0;
  const blockedReasons = [
    ...(status?.ops_status?.blocked_reasons || []),
    ...(status?.validation?.blocked_reasons || []),
  ];

  if (els.canaryStatusBadge) {
    const isCompleted = status.overall_status === "completed";
    const isBlocked = status.overall_status === "blocked";
    els.canaryStatusBadge.textContent = isCompleted
      ? "本轮任务已完成"
      : isBlocked
      ? "受邀测试未开放"
      : status.identity_status === "missing"
      ? "等待绑定测试身份"
      : "灰测可继续";
    els.canaryStatusBadge.className = `canary-status-badge ${isCompleted ? "is-done" : isBlocked ? "is-blocked" : "is-active"}`;
  }
  if (els.canaryProgressLabel) {
    els.canaryProgressLabel.textContent = `${completedCount} / ${totalCount} 已完成`;
  }
  if (els.canaryOverview) {
    els.canaryOverview.textContent = status.identity_status === "missing"
      ? "先填写测试编号或邀请码，任务区才会按你的个人进度追踪本轮灰测。"
      : friendlyCanaryReason(
        blockedReasons,
        status?.ops_status?.status === "canary"
          ? "按任务顺序完成一次语音起课、一次口吻切换、一次分享报告和一次有效反馈。"
          : status?.ops_status?.notice || "当前批次暂未开放，先查看任务门槛和阻断原因。",
      );
  }
  if (els.canaryProgressBarFill) {
    els.canaryProgressBarFill.style.width = `${percent}%`;
  }
  renderCanaryMilestones(status);

  els.canaryTaskList.innerHTML = (status.tasks || [])
    .map((task) => {
      const derivedStatus = derivedCanaryTaskStatus(task);
      const statusLabel = canaryTaskStatusLabel(derivedStatus);
      const completedAt = task.completed_at ? `完成时间：${task.completed_at}` : "";
      const evidenceCopy = task.completed
        ? completedAt || "已记录一次有效完成。"
        : task.task_id === "C11-T02" && ["story", "mentor"].includes(els.modeSelect.value)
        ? `当前已切到 ${displayStatusValue(els.modeSelect.value)}口吻，下一次起课就会记入任务。`
        : task.task_id === "C11-T04" && state.lastToolResult
        ? "已有一轮结果，可直接补充反馈。"
        : task.description || "";
      const evidenceHtml = evidenceCopy && evidenceCopy !== (task.description || "")
        ? `<p class="canary-task-evidence">${escapeHtml(evidenceCopy)}</p>`
        : "";
      return `
        <li class="canary-task-card ${canaryTaskStatusClass(derivedStatus)}">
          <div class="canary-task-head">
            <div>
              <span class="canary-task-stage">${escapeHtml(task.stage || "任务")}</span>
          <strong>${escapeHtml(localizedCanaryTaskCopy(task.label || task.task_id))}</strong>
            </div>
            <span class="canary-task-chip ${canaryTaskStatusClass(derivedStatus)}">${escapeHtml(statusLabel)}</span>
          </div>
          <p class="canary-task-copy">${escapeHtml(localizedCanaryTaskCopy(task.description || ""))}</p>
          ${evidenceHtml}
          <div class="canary-task-actions">
            <button type="button" class="canary-task-action" data-canary-action="${escapeHtml(task.cta_action || "")}" data-task-id="${escapeHtml(task.task_id)}">${escapeHtml(canaryActionLabel(task))}</button>
          </div>
        </li>
      `;
    })
    .join("");
}

async function recordGrowthEvent(eventType, extra = {}) {
  const identity = currentTesterIdentity();
  const payload = {
    tester_id: identity.tester_id || "anonymous",
    invite_code: identity.invite_code || null,
    event_type: eventType,
    mode: els.modeSelect.value,
    source: "realtime_frontend",
    ...extra,
  };
  const response = await fetch("/api/growth/event", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Growth event failed: ${response.status}`);
  }
  return response.json();
}

async function maybeRecordShareReport(result) {
  if (state.opsStatus?.status !== "canary") {
    return null;
  }
  const reportView = normalizeShareReport(result?.interpretation?.entertainment?.share_report || {});
  const chartId = result?.chart?.chart_id || "";
  if ((!reportView.copyText && !reportView.copyHtml) || !chartId || state.lastShareReportEventKey === chartId) {
    return null;
  }
  state.lastShareReportEventKey = chartId;
  try {
    return await recordGrowthEvent("share_report_generated", {
      chart_id: chartId,
      category: result?.chart?.category || result?.safety?.category || null,
      task_id: "C11-T03",
      channel: "realtime",
    });
  } catch (error) {
    writeLog(els.toolLog, error.message);
    return null;
  }
}

async function recordCanarySession(result) {
  const interpretation = result?.interpretation || {};
  const chart = result?.chart || {};
  const payload = {
    tester_id: els.testerId.value.trim() || null,
    invite_code: els.inviteCode.value.trim() || null,
    chart_id: chart.chart_id || null,
    mode: interpretation.mode || els.modeSelect.value,
    category: chart.category || result?.safety?.category || null,
    session_status: chart.chart_id ? "completed" : "blocked",
    safety_action: result?.safety?.action || interpretation.safety_validation?.action || null,
    blocked_reasons: interpretation.blocked_reasons || [],
    latency_ms: result?.latency_ms || null,
    channel: "realtime",
  };
  const response = await fetch("/api/canary/session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (response.ok) {
    return response.json();
  }
  return { stored: false, blocked_reasons: [`canary_session_http_${response.status}`] };
}

async function recordPublicSession(result) {
  const interpretation = result?.interpretation || {};
  const chart = result?.chart || {};
  const payload = {
    visitor_id: resolvedVisitorId(),
    chart_id: chart.chart_id || null,
    mode: interpretation.mode || els.modeSelect.value,
    category: chart.category || result?.safety?.category || null,
    session_status: chart.chart_id ? "completed" : "blocked",
    feedback_type: els.feedbackType?.value || null,
    safety_action: result?.safety?.action || interpretation.safety_validation?.action || null,
    blocked_reasons: interpretation.blocked_reasons || [],
    latency_ms: result?.latency_ms || null,
    source: "realtime_frontend",
  };
  const response = await fetch("/api/public/session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (response.ok) {
    return response.json();
  }
  return { stored: false, blocked_reasons: [`public_session_http_${response.status}`] };
}

async function recordLearningProgress(result) {
  const chart = result?.chart || {};
  const payload = {
    visitor_id: resolvedVisitorId(),
    node_id: "LP-REPORT-001",
    event_type: "pdf_report_generated",
    status: chart.chart_id ? "completed" : "blocked",
    mode: result?.interpretation?.mode || els.modeSelect.value,
    chart_id: chart.chart_id || null,
    source: "realtime_frontend",
  };
  const response = await fetch("/api/learning/progress", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (response.ok) {
    return response.json();
  }
  return { stored: false, blocked_reasons: [`learning_progress_http_${response.status}`] };
}

async function recordCommercialInterest() {
  try {
    const result = await recordGrowthEvent("member_interest");
    if (result.metrics) {
      state.growthMetrics = result.metrics;
      renderCommercialInterestSummary();
    }
    els.commercialInterestStatus.textContent = result.stored
      ? "上游兴趣已记录，可继续查看右侧权益预览。"
      : "兴趣未记录。";
  } catch (error) {
    els.commercialInterestStatus.textContent = "兴趣记录失败。";
    writeLog(els.toolLog, error.message);
  }
}

async function submitFeedback() {
  if (!state.lastToolResult) {
    els.feedbackStatus.textContent = "请先完成一次起课解释。";
    return;
  }
  const interpretation = state.lastToolResult.interpretation || {};
  const chart = state.lastToolResult.chart || {};
  const payload = {
    tester_id: els.testerId.value.trim() || "anonymous",
    chart_id: chart.chart_id || "",
    mode: interpretation.mode || els.modeSelect.value,
    category: chart.category || state.lastToolResult.safety?.category || null,
    safety_action: state.lastToolResult.safety?.action || interpretation.safety_validation?.action || null,
    blocked_reasons: interpretation.blocked_reasons || [],
    feedback_type: els.feedbackType.value,
    note: els.feedbackNote.value.trim(),
    feedback_token: interpretation.feedback_token || null,
    beta_scope_status: interpretation.beta_scope?.status || null,
  };
  try {
    const response = await fetch("/api/beta/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Feedback failed: ${response.status}`);
    }
    const result = await response.json();
    if (result.stored && state.opsStatus?.status === "canary") {
      try {
        await recordGrowthEvent("feedback_submitted", {
          chart_id: chart.chart_id || null,
          category: chart.category || state.lastToolResult.safety?.category || null,
          feedback_token: interpretation.feedback_token || null,
          task_id: "C11-T04",
          channel: "realtime",
          note: payload.note || "",
        });
      } catch (growthError) {
        writeLog(els.toolLog, growthError.message);
      }
      await loadCanaryTaskStatus();
    }
    els.feedbackStatus.textContent = result.stored ? "反馈已记录。" : "反馈未写入。";
    els.feedbackNote.value = "";
    await loadBetaReport();
  } catch (error) {
    els.feedbackStatus.textContent = "反馈提交失败。";
    writeLog(els.toolLog, error.message);
  }
}

async function runTextInterpret() {
  const question = els.textQuestion?.value.trim() || "";
  if (!question) {
    els.textInterpretStatus.textContent = "请先输入一个问题。";
    return;
  }
  setStatus("text_interpreting");
  els.runTextInterpretBtn.disabled = true;
  els.textInterpretStatus.textContent = "正在生成解释...";
  const payload = normalizeToolArguments({
    question,
    datetime: nowIso(),
    timezone: userTimezone(),
    mode: els.modeSelect.value,
    tester_id: els.testerId.value.trim() || null,
    invite_code: els.inviteCode.value.trim() || null,
  });
  try {
    const response = await fetch("/api/liuren/text-interpret", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...payload, use_openrouter: true }),
    });
    if (!response.ok) {
      throw new Error(`Text interpretation failed: ${response.status}`);
    }
    const result = await response.json();
    renderTextInterpretResult(result);
    els.textInterpretStatus.textContent = (result.interpretation?.blocked_reasons || []).includes("non_liuren_question")
      ? "这个问题不适合起课，请改成具体事项占问。"
      : result.openrouter?.status === "ok"
      ? "已生成 DeepSeek 润色解释。"
      : "已生成本地结构化解释，DeepSeek 润色不可用。";
    setStatus("idle");
  } catch (error) {
    setStatus("error");
    els.textInterpretStatus.textContent = "文字起课失败。";
    writeLog(els.toolLog, error.message);
  } finally {
    els.runTextInterpretBtn.disabled = false;
  }
}

async function runToolCall(call) {
  setStatus("tool_calling");
  const args = normalizeToolArguments(JSON.parse(call.arguments || "{}"));
  writeLog(els.toolLog, { name: call.name, arguments: args });
  const response = await fetch("/api/liuren/interpret", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(args),
  });
  if (!response.ok) {
    throw new Error(`Tool call failed: ${response.status}`);
  }
  const result = await response.json();
  state.lastToolResult = result;
  writeLog(els.interpretationPreview, result.interpretation);
  if ((result.interpretation?.blocked_reasons || []).includes("ops_paused")) {
    await loadOpsStatus();
  }
  if ((result.interpretation?.blocked_reasons || []).includes("public_paused")) {
    await loadPublicStatus();
  }
  if (isPublicActive()) {
    const publicSession = await recordPublicSession(result);
    const learningProgress = await recordLearningProgress(result);
    writeLog(els.toolLog, { tool_result: result, public_session: publicSession, learning_progress: learningProgress });
  } else if (state.opsStatus?.status === "canary") {
    const canarySession = await recordCanarySession(result);
    const shareReportEvent = await maybeRecordShareReport(result);
    await loadCanaryTaskStatus();
    writeLog(els.toolLog, { tool_result: result, canary_session: canarySession, share_report_event: shareReportEvent });
  }
  renderEntertainment(result);
  renderBetaStatus(result);
  sendRealtimeEvent({
    type: "conversation.item.create",
    item: {
      type: "function_call_output",
      call_id: call.call_id,
      output: JSON.stringify(result),
    },
  });
  sendRealtimeEvent({ type: "response.create" });
  setStatus("responding");
}

function findFunctionCalls(responseDoneEvent) {
  const output = responseDoneEvent.response?.output || [];
  return output.filter((item) => item.type === "function_call" && item.name === "create_liuren_interpretation");
}

async function handleRealtimeEvent(event) {
  if (event.type === "response.output_audio_transcript.delta" || event.type === "response.output_text.delta") {
    els.transcript.textContent += event.delta || "";
  }
  if (event.type === "response.output_item.added") {
    state.lastResponseItemId = event.item?.id || state.lastResponseItemId;
  }
  if (event.type === "response.done") {
    const calls = findFunctionCalls(event);
    if (calls.length) {
      await runToolCall(calls[0]);
    } else {
      setStatus("listening");
    }
  }
  if (event.type === "error") {
    setStatus("error");
    writeLog(els.toolLog, event);
  }
}

async function connect() {
  try {
    setStatus("connecting");
    if (state.opsStatus?.status === "canary" && !isPublicActive()) {
      const validation = await validateCanaryAccess();
      if (!validation.allowed) {
        return;
      }
    }
    state.pc = new RTCPeerConnection();
    state.pc.ontrack = (event) => {
      els.remoteAudio.srcObject = event.streams[0];
    };
    state.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    state.stream.getTracks().forEach((track) => state.pc.addTrack(track, state.stream));
    state.dc = state.pc.createDataChannel("oai-events");
    state.dc.addEventListener("open", () => setStatus("listening"));
    state.dc.addEventListener("message", (event) => handleRealtimeEvent(JSON.parse(event.data)));
    const offer = await state.pc.createOffer();
    await state.pc.setLocalDescription(offer);
    const sdpResponse = await fetch("/api/realtime/session", {
      method: "POST",
      body: offer.sdp,
      headers: { "Content-Type": "application/sdp" },
    });
    if (!sdpResponse.ok) {
      throw new Error(`Realtime session failed: ${sdpResponse.status}`);
    }
    await state.pc.setRemoteDescription({ type: "answer", sdp: await sdpResponse.text() });
    els.connectBtn.disabled = true;
    els.disconnectBtn.disabled = false;
    els.interruptBtn.disabled = false;
  } catch (error) {
    setStatus("error");
    writeLog(els.toolLog, error.message);
  }
}

function interrupt() {
  try {
    sendRealtimeEvent({ type: "response.cancel" });
    if (state.lastResponseItemId) {
      sendRealtimeEvent({
        type: "conversation.item.truncate",
        item_id: state.lastResponseItemId,
        content_index: 0,
        audio_end_ms: 0,
      });
    }
    setStatus("listening");
  } catch (error) {
    setStatus("error");
    writeLog(els.toolLog, error.message);
  }
}

function disconnect() {
  if (state.dc) {
    state.dc.close();
  }
  if (state.pc) {
    state.pc.close();
  }
  if (state.stream) {
    state.stream.getTracks().forEach((track) => track.stop());
  }
  state.pc = null;
  state.dc = null;
  state.stream = null;
  els.connectBtn.disabled = false;
  els.disconnectBtn.disabled = true;
  els.interruptBtn.disabled = true;
  setStatus("idle");
}

function focusShareReport() {
  openPanelById("experimentsPanel");
  const target = document.getElementById("shareReport");
  if (typeof target?.scrollIntoView === "function") {
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  const focusTarget = els.copyShareReportTextBtn && !els.copyShareReportTextBtn.disabled
    ? els.copyShareReportTextBtn
    : target;
  if (typeof focusTarget?.focus === "function") {
    focusTarget.focus();
  }
}

function handleCanaryTaskAction(action) {
  if (action === "focus_question") {
    openPanelById("questionPanel");
    if (typeof els.textQuestion?.focus === "function") {
      els.textQuestion.focus();
    }
    return;
  }
  if (action === "switch_to_story") {
    els.modeSelect.value = "story";
    renderCanaryTaskPanel();
    openPanelById("questionPanel");
    return;
  }
  if (action === "focus_share_report") {
    focusShareReport();
    return;
  }
  if (action === "focus_feedback") {
    openPanelById("feedbackPanel");
    if (typeof els.feedbackNote?.focus === "function") {
      els.feedbackNote.focus();
    }
  }
}

els.modeSelect.addEventListener("change", () => {
  if (state.lastToolResult) {
    writeLog(els.toolLog, {
      mode: els.modeSelect.value,
      note: "下一次工具调用会使用新模式；当前结果保持不变。",
    });
  }
  renderCanaryTaskPanel();
});
els.connectBtn.addEventListener("click", connect);
els.disconnectBtn.addEventListener("click", disconnect);
els.interruptBtn.addEventListener("click", interrupt);
if (els.runTextInterpretBtn) {
  els.runTextInterpretBtn.addEventListener("click", runTextInterpret);
}
if (els.personaCardsToggle) {
  els.personaCardsToggle.addEventListener("click", () => {
    state.personaCardsExpanded = !state.personaCardsExpanded;
    renderPersonaLines(state.personaCardLines);
  });
}
if (els.learningPathNodes) {
  els.learningPathNodes.addEventListener("click", (event) => {
    const trigger = event.target?.closest?.("[data-node-id]");
    const nodeId = trigger?.dataset?.nodeId;
    if (nodeId) {
      selectLearningPathNode(nodeId);
    }
  });
}
if (els.learningPathRecommended) {
  els.learningPathRecommended.addEventListener("click", async (event) => {
    const trigger = event.target?.closest?.("[data-action]");
    const nodeId = trigger?.dataset?.nodeId;
    if (!nodeId) {
      return;
    }
    await handleLearningPathAction(nodeId, trigger.dataset.action);
  });
}
if (els.learningPathDetail) {
  els.learningPathDetail.addEventListener("click", async (event) => {
    const trigger = event.target?.closest?.("[data-action]");
    const nodeId = trigger?.dataset?.nodeId;
    if (!nodeId) {
      return;
    }
    await handleLearningPathAction(nodeId, trigger.dataset.action);
  });
}
bindTopNavLinks();
if (els.canaryTaskList) {
  els.canaryTaskList.addEventListener("click", (event) => {
    const trigger = event.target?.closest?.("[data-canary-action]");
    if (!trigger) {
      return;
    }
    handleCanaryTaskAction(trigger.dataset.canaryAction || "");
  });
}
els.submitFeedbackBtn.addEventListener("click", submitFeedback);
if (els.testerId) {
  els.testerId.addEventListener("change", loadCanaryTaskStatus);
}
if (els.inviteCode) {
  els.inviteCode.addEventListener("change", loadCanaryTaskStatus);
}
if (els.commercialInterest) {
  els.commercialInterest.addEventListener("click", recordCommercialInterest);
}
if (els.saveVisitorProfileBtn) {
  els.saveVisitorProfileBtn.addEventListener("click", saveVisitorProfile);
}
if (els.copyShareReportTextBtn) {
  els.copyShareReportTextBtn.addEventListener("click", () => copyShareReport("text"));
}
if (els.copyShareReportHtmlBtn) {
  els.copyShareReportHtmlBtn.addEventListener("click", () => copyShareReport("html"));
}
if (els.copyShareReportDraftBtn) {
  els.copyShareReportDraftBtn.addEventListener("click", () => copyShareReport("draft"));
}
els.monetizationInterestButtons.forEach((button) => {
  button.addEventListener("click", () => recordMonetizationEvent(button.dataset.eventType, button.dataset.offerId));
});
if (els.submitBusinessLeadBtn) {
  els.submitBusinessLeadBtn.addEventListener("click", submitBusinessLead);
}
if (els.paymentTierSelect) {
  els.paymentTierSelect.addEventListener("change", syncSandboxActionState);
}
if (typeof document.addEventListener === "function") {
  document.addEventListener("renyu:languagechange", renderRenYuLocalizedViews);
}
if (els.startSandboxCheckoutBtn) {
  els.startSandboxCheckoutBtn.addEventListener("click", startSandboxCheckout);
}
if (els.confirmSandboxPaymentBtn) {
  els.confirmSandboxPaymentBtn.addEventListener("click", () => confirmSandboxPayment("success"));
}
if (els.failSandboxPaymentBtn) {
  els.failSandboxPaymentBtn.addEventListener("click", () => confirmSandboxPayment("failure"));
}
if (els.cancelSandboxOrderBtn) {
  els.cancelSandboxOrderBtn.addEventListener("click", cancelSandboxOrder);
}
if (els.refundSandboxOrderBtn) {
  els.refundSandboxOrderBtn.addEventListener("click", refundSandboxOrder);
}
syncSandboxActionState();
window.renderRenYuLocalizedViews = renderRenYuLocalizedViews;
renderShareReport({});
loadBetaConfig();
loadBetaReport();
loadOpsStatus();
loadPublicStatus();
loadProductizationGate();
loadGrowthMetrics();
loadMonetizationGate();
loadMonetizationMetrics();
loadPaymentGate();
loadPaymentMetrics();
loadCanaryRunConfig();
loadLearningPath();
loadOfferCatalog();
loadMembershipTiers();
