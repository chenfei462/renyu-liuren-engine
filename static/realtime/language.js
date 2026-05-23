(function () {
  const STORAGE_KEY = "renyu.language";
  const LANGUAGES = {
    zh: {
      htmlLang: "zh-CN",
      region: "中",
      current: "中文",
      options: { zh: "中文", en: "英文" },
    },
    en: {
      htmlLang: "en",
      region: "US",
      current: "English",
      options: { zh: "Chinese", en: "English" },
    },
  };

  const TEXT = {
    "受限最小可用版": "Limited public build",
    "澹语 · 大六壬": "RenYu · Da Liu Ren",
    "起课": "Start",
    "学习闯关": "Learning",
    "反馈": "Feedback",
    "更多": "More",
    "当前状态": "Current status",
    "空闲": "Idle",
    "文化学习体验，不构成现实建议。": "Cultural learning experience, not real-world advice.",
    "公开体验不保存录音；反馈、课式和删除请求仅用于产品复盘。": "Public sessions do not store recordings. Feedback, chart sessions, and deletion requests are used only for product review.",
    "发布入口": "Launch page",
    "隐私政策": "Privacy",
    "安全边界": "Safety boundary",
    "版权说明": "Copyright",
    "受限内测：传统文化学习与娱乐体验，不构成现实建议。": "Limited beta: traditional culture learning and entertainment only, not real-world advice.",
    "当前运维状态暂停讲盘，仅提供安全说明与反馈入口。": "Interpretation is paused by operations status. Only safety notes and feedback remain available.",
    "公开最小可用版状态读取中。公开体验不保存录音；反馈、课式和删除请求仅用于产品复盘。": "Reading public build status. Public sessions do not store recordings. Feedback, chart sessions, and deletion requests are used only for product review.",
    "本次占问": "Question",
    "输入一个具体事项": "Enter one concrete situation",
    "例如出行、合作、学习安排等；不回答天气、新闻、百科、计算或闲聊问题。": "Use a specific travel, collaboration, or study question. Weather, news, encyclopedia, calculation, and casual chat are not supported.",
    "文字起课": "Text session",
    "只用于具体事项占问": "Only for concrete questions",
    "解读口吻": "Tone",
    "专业": "Professional",
    "白话": "Plain",
    "故事": "Story",
    "导师": "Mentor",
    "连接": "Connect",
    "断开": "Disconnect",
    "打断": "Interrupt",
    "开始起课": "Start session",
    "不回答天气、新闻、百科、计算或闲聊问题。": "Weather, news, encyclopedia, calculation, and casual chat are not supported.",
    "解读结果": "Result",
    "先读结论，再看依据": "Read the takeaway, then the evidence",
    "安全边界优先": "Safety first",
    "输入问题后，这里会显示可直接阅读的解释。": "After you enter a question, the readable explanation appears here.",
    "辅助信息": "Support information",
    "访问与状态": "Access and status",
    "本地偏好": "Local preference",
    "本地昵称": "Local nickname",
    "保存本地访客偏好": "Save local visitor preference",
    "测试访问": "Test access",
    "测试编号": "Tester ID",
    "邀请码": "Invite code",
    "内测安全状态": "Beta safety status",
    "等待起课结果。": "Waiting for session result.",
    "学习资料": "Learning material",
    "学习资料会在生成解释后显示，不代表已经为当前问题起课。": "Learning material appears after an explanation is generated; it does not mean the current question has already been charted.",
    "天将角色卡": "General persona cards",
    "展开全部": "Expand all",
    "学习卡": "Learning cards",
    "类型": "Type",
    "有帮助": "Helpful",
    "看不懂": "Confusing",
    "出处不足": "Insufficient sources",
    "安全问题": "Safety issue",
    "排盘疑问": "Chart question",
    "语音体验问题": "Voice issue",
    "备注": "Note",
    "提交反馈": "Submit feedback",
    "更多 / 实验功能": "More / experiments",
    "灰度": "Canary",
    "灰度测试任务": "Canary test tasks",
    "正在读取状态": "Reading status",
    "已完成": "completed",
    "正在读取受邀测试说明、任务进度和当前阻断原因。": "Reading tester instructions, task progress, and current blockers.",
    "兴趣": "Interest",
    "兴趣记录": "Interest record",
    "先记录上游学习/会员兴趣，再判断是否值得进入后续商业化实验。": "Record upstream learning and membership interest before deciding whether to continue commercial experiments.",
    "正在读取兴趣信号和实验阶段。": "Reading interest signals and experiment stage.",
    "记录学习/会员兴趣": "Record learning / membership interest",
    "实验": "Experiment",
    "商业化兴趣实验": "Commercial interest experiment",
    "权益预览只记录兴趣，不售卖、不发放会员权益。": "Offer previews record interest only. They do not sell or grant benefits.",
    "读取中": "Reading",
    "正在读取实验指标。": "Reading experiment metrics.",
    "正在读取当前阶段、阻塞原因和下一步。": "Reading current stage, blockers, and next step.",
    "会员权益预览": "Membership preview",
    "课程兴趣": "Course interest",
    "商务合作兴趣": "Business interest",
    "文创周边兴趣": "Creative merchandise interest",
    "合作": "Partnership",
    "商务线索": "Business lead",
    "只在实验开放时写入线索，用来判断老师、书店、展陈或文旅合作是否值得继续设计。": "Leads are stored only when the experiment is open, to evaluate teacher, bookstore, exhibition, or cultural tourism partnerships.",
    "商业路径": "Commercial path",
    "正在读取商业路径状态。": "Reading commercial path status.",
    "联系人昵称": "Contact nickname",
    "渠道": "Channel",
    "需求摘要": "Need summary",
    "提交商务线索": "Submit business lead",
    "会员": "Membership",
    "支付准备闸门": "Payment readiness gate",
    "沙箱": "Sandbox",
    "会员权益预览": "Membership preview",
    "沙箱演示不产生真实扣款，权益只用于上线前准备。": "Sandbox demos do not create real charges; benefits are only for launch preparation.",
    "沙箱支付演示": "Sandbox payment demo",
    "权益层": "Tier",
    "创建沙箱订单": "Create sandbox order",
    "模拟支付成功": "Simulate payment success",
    "模拟支付失败": "Simulate payment failure",
    "取消订单": "Cancel order",
    "退款演示": "Refund demo",
    "尚未创建沙箱订单。": "No sandbox order has been created.",
    "调试详情": "Debug details",
    "调用状态": "Call status",
    "结构化数据": "Structured data",
    "报告": "Report",
    "分享报告": "Share report",
    "复制分享文案": "Copy share text",
    "复制网页草稿": "Copy web draft",
    "完成一次起课后，这里会整理成更易读的分享卡片与本地草稿。": "After one session, this area becomes readable share cards and a local draft.",
    "当前还没有分享报告。起课完成后，会在这里展示摘要、提示和可复制内容。": "No share report yet. After a session, summary, prompts, and copyable content appear here.",
    "复制只在当前浏览器本地进行，不生成外链。": "Copying happens locally in this browser. No public link is generated.",
    "高级草稿": "Advanced draft",
    "复制文档草稿提纲": "Copy document draft outline",
    "澹语 · 大六壬最小可用版": "RenYu · Da Liu Ren public build",
    "范围": "Scope",
    "安全": "Safety",
    "状态": "Status",
    "进入体验": "Enter",
    "进入工作台": "Open workbench",
    "受限发布准备版": "Limited launch candidate",
    "大六壬实时解读的文化学习入口": "A cultural learning entry for realtime Da Liu Ren interpretation",
    "壬语最小可用版延续为澹语发布准备版；本产品不构成医疗、法律、投资、人身安全或其他现实决策建议。": "RenYu continues as the DanYu launch candidate. This product is not medical, legal, investment, personal safety, or other real-world decision advice.",
    "查看发布准入": "View launch readiness",
    "澹语工作台": "DanYu workbench",
    "本次占问": "Question",
    "这个合作能不能在本月推进？": "Can this collaboration move forward this month?",
    "出处卡": "Source cards",
    "信任摘要": "Trust summary",
    "最小可用版范围": "Build scope",
    "起课、解释、学习材料": "Sessions, interpretation, learning material",
    "语音/文字体验、出处卡、学习卡、本地分享报告。": "Voice and text sessions, source cards, learning cards, and local share reports.",
    "高风险问题降级": "High-risk questions are downgraded",
    "医疗、法律、投资、人身安全等只提供风险提醒。": "Medical, legal, investment, and personal safety topics receive risk reminders only.",
    "闸门透明可查": "Gates are transparent",
    "发布、灰度、公开最小可用版、支付准备状态均可追踪。": "Release, canary, public build, and payment readiness are trackable.",
    "先说明能做什么，再说明不做什么": "State what it does before what it will not do",
    "澹语当前仍是受限发布准备版，优先保证文化学习、可解释性和安全边界。": "DanYu is still a limited launch candidate focused on cultural learning, explainability, and safety boundaries.",
    "开放体验": "Open experience",
    "继续关闭": "Still closed",
    "发布状态": "Launch status",
    "阶段状态保留，但不抢首屏入口": "Stage status remains visible without taking over the first screen",
    "以下信息从现有接口读取，用于透明展示当前闸门、实验和支付准备状态。": "The following information is read from current APIs to show gates, experiments, and payment readiness transparently.",
    "查看运维状态数据": "View ops status data",
    "灰度准入": "Canary access",
    "查看受邀测试配置": "View tester configuration",
    "增长内容日历": "Growth content calendar",
    "第 10 阶段仅整理本地栏目、标题、摘要、学习卡和出处卡关联，不发布外部平台内容。": "Phase 10 only organizes local columns, titles, summaries, learning cards, and source-card links. It does not publish external content.",
    "查看内容日历数据": "View content calendar data",
    "第 11 阶段灰度": "Phase 11 canary",
    "正在读取灰度指标与公开发布准入。": "Reading canary metrics and public launch readiness.",
    "查看灰度指标": "View canary metrics",
    "查看公开发布闸门": "View public launch gate",
    "第 12 阶段公开最小可用版": "Phase 12 public build",
    "公开最小可用版仍限定为传统文化学习与娱乐体验，不构成现实建议。": "The public build remains limited to traditional culture learning and entertainment. It is not real-world advice.",
    "查看公开状态": "View public status",
    "查看公开指标": "View public metrics",
    "查看第 12 阶段报告": "View phase 12 report",
    "第 13 阶段产品化实验": "Phase 13 productization experiment",
    "正在读取产品化闸门、学习路径和留存指标。": "Reading productization gate, learning path, and retention metrics.",
    "产品化实验只做匿名访客、学习闯关、留存指标和本地文档报告草案，不开放账号、支付或高风险断法。": "Productization experiments cover anonymous visitors, learning paths, retention metrics, and local report drafts only. Accounts, payments, and high-risk claims remain closed.",
    "查看产品化闸门": "View productization gate",
    "查看产品化指标": "View productization metrics",
    "查看第 13 阶段报告": "View phase 13 report",
    "第 14 阶段商业化实验": "Phase 14 monetization experiment",
    "正在读取商业化闸门、权益目录和兴趣指标。": "Reading monetization gate, offer catalog, and interest metrics.",
    "商业化实验只记录会员、课程、商务合作和文创周边兴趣；不接支付、不发放权益、不承诺现实结果。": "Monetization experiments only record membership, course, business, and merchandise interest. They do not accept payment, grant benefits, or promise outcomes.",
    "查看商业化闸门": "View monetization gate",
    "查看权益目录": "View offer catalog",
    "查看商业化指标": "View monetization metrics",
    "查看第 14 阶段报告": "View phase 14 report",
    "第 15 阶段支付准备": "Phase 15 payment readiness",
    "正在读取支付准备闸门、会员权益和沙箱订单指标。": "Reading payment readiness gate, membership benefits, and sandbox order metrics.",
    "支付准备只做沙箱演示、订单状态机和会员权益模拟；不产生真实扣款，不承诺现实结果。": "Payment readiness only covers sandbox demos, order states, and membership benefit simulations. It does not charge real money or promise outcomes.",
    "查看支付准备闸门": "View payment gate",
    "查看会员权益": "View membership benefits",
    "查看支付准备指标": "View payment metrics",
    "查看第 15 阶段报告": "View phase 15 report",
    "发布总控": "Launch control",
    "正在读取真实接口状态。": "Reading real API status.",
    "发布指标摘要": "Launch metrics summary",
    "正在读取指标。": "Reading metrics.",
    "当前阻断": "Current blockers",
    "正在读取阻断原因。": "Reading blocker reasons.",
    "下一步": "Next step",
    "正在读取下一步动作。": "Reading next actions.",
    "真实路径入口": "Real path entries",
    "发布准入": "Launch readiness",
    "灰度报告": "Canary report",
    "支付报告": "Payment report",
    "发布阶段路径": "Launch phase path",
    "阶段 10": "Phase 10",
    "内容日历": "Content calendar",
    "正在读取": "Reading",
    "阶段 11": "Phase 11",
    "阶段 12": "Phase 12",
    "公开最小可用版": "Public build",
    "阶段 13": "Phase 13",
    "产品化实验": "Productization experiment",
    "阶段 14": "Phase 14",
    "商业化实验": "Monetization experiment",
    "阶段 15": "Phase 15",
    "支付准备": "Payment readiness",
    "正在读取审校队列和受邀测试限制。": "Reading review queue and invited tester limits.",
    "正在读取受邀测试配置。": "Reading invited tester configuration.",
    "查看第 11 阶段报告": "View phase 11 report",
    "正在读取会话、反馈和分享报告指标。": "Reading session, feedback, and share report metrics.",
    "正在读取公开会话、反馈和安全事件。": "Reading public sessions, feedback, and safety events.",
    "正在读取访客、闯关和留存数据。": "Reading visitor, learning path, and retention data.",
    "正在读取兴趣、权益浏览和商务线索。": "Reading interest, offer views, and business leads.",
    "正在读取沙箱订单、退款和支付能力。": "Reading sandbox orders, refunds, and payment capabilities.",
    "合规说明": "Compliance",
    "进入体验前，先看清边界": "Read the boundaries before entering",
    "安全边界说明": "Safety boundary document",
    "隐私说明": "Privacy notice",
    "浏览器麦克风仅用于会话，不保存用户录音；反馈记录仅用于测试改进。": "Browser microphone access is used only during the session. User audio is not stored; feedback is used only for testing improvements.",
    "版权说明": "Copyright notice",
    "古籍和现代资料只做出处、摘要、定位和规则化转写，不展示受限正文。": "Classical and modern materials are used only as sources, summaries, references, and rule transformations. Restricted full text is not shown.",
    "准备好后，进入工作台起课": "When ready, open the workbench",
    "传统文化学习与娱乐体验，不构成现实建议。受邀用户可在工作台内提交“有帮助、看不懂、出处不足、安全问题、排盘疑问、语音体验问题”等反馈。": "Traditional culture learning and entertainment only. Invited users can submit feedback such as helpful, confusing, insufficient sources, safety issue, chart question, or voice issue in the workbench.",
  };

  const PLACEHOLDERS = {
    "例如：明天出行是否顺利？这个合作能不能推进？": "Example: Will tomorrow's travel go smoothly? Can this collaboration move forward?",
    "例如：书店主理人 / 课程负责人": "Example: bookstore owner / course lead",
    "例如：微信社群 / 线下活动 / 朋友转介绍": "Example: messaging group / offline event / referral",
    "例如：想做 20 人传统文化工作坊，重点看讲解节奏、互动体验和现场物料。": "Example: a 20-person traditional culture workshop focused on pacing, interaction, and printed material.",
  };

  const ATTR_TEXT = {
    "安全边界": "Safety boundary",
    "辅助信息": "Support information",
    "本地访客昵称": "Local visitor nickname",
    "测试用户编号": "Tester ID",
    "学习闯关概览": "Learning path overview",
    "推荐下一步": "Recommended next step",
    "闯关节点": "Learning nodes",
    "节点详情": "Node details",
    "反馈备注": "Feedback note",
    "次级实验区": "Secondary experiments",
    "文字解读": "Text interpretation",
    "语音控制": "Voice controls",
    "灰度邀请码": "Canary invite code",
    "应用导航": "App navigation",
    "商业路径": "Commercial path",
    "最小可用版范围说明": "Public build scope",
    "发布页导航": "Launch page navigation",
    "澹语首页": "DanYu home",
    "工作台预览": "Workbench preview",
    "信任摘要": "Trust summary",
    "发布状态总览": "Launch status overview",
    "发布指标摘要": "Launch metrics summary",
    "真实路径入口": "Real path entries",
    "发布阶段路径": "Launch phase path",
  };

  const ZH_DYNAMIC = {
    idle: "空闲",
    loading: "读取中",
    ready: "就绪",
    connected: "已连接",
    disconnected: "已断开",
    text_interpreting: "文字起课中",
    error: "错误",
    "Beta 状态": "内测状态",
    "HTML 草稿": "网页草稿",
    "PDF 草稿提纲": "文档草稿提纲",
    "Canary": "灰度",
    "B2B": "商务",
    "IP": "文创",
    "JSON": "数据",
    "MVP": "最小可用版",
  };

  const EN_DYNAMIC = {
    "Beta": "Beta",
    "Canary": "Canary",
    "B2B": "Business",
    "IP": "Merchandise",
    "HTML": "Web",
    "PDF": "Document",
    "JSON": "Data",
    "MVP": "Public build",
    "DeepSeek": "AI polish",
    "phase": "phase",
    "offer": "offer",
    "unknown": "unknown",
  };

  function invert(map) {
    return Object.fromEntries(Object.entries(map).map(([zh, en]) => [en, zh]));
  }

  const EN_TO_ZH = invert(TEXT);
  const PLACEHOLDER_EN_TO_ZH = invert(PLACEHOLDERS);
  const ATTR_EN_TO_ZH = invert(ATTR_TEXT);
  const mutationOptions = { childList: true, subtree: true };
  let observer = null;

  function selectedLanguage() {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === "en" ? "en" : "zh";
  }

  function translateText(value, language) {
    const trimmed = String(value || "").trim();
    if (!trimmed) {
      return value;
    }
    if (language === "en" && TEXT[trimmed]) {
      return TEXT[trimmed];
    }
    if (language === "zh" && EN_TO_ZH[trimmed]) {
      return EN_TO_ZH[trimmed];
    }
    const dynamicMap = language === "zh" ? ZH_DYNAMIC : EN_DYNAMIC;
    return dynamicMap[trimmed] || trimmed;
  }

  function translateComposedText(value, language) {
    const text = String(value || "");
    const leading = text.match(/^\s*/)?.[0] || "";
    const trailing = text.match(/\s*$/)?.[0] || "";
    const translated = translateText(text, language);
    return `${leading}${translated}${trailing}`;
  }

  function setTextContent(element, value) {
    if (element && element.textContent !== value) {
      element.textContent = value;
    }
  }

  function withLanguageMutationsPaused(callback) {
    if (window.__renyuLanguageApplying) {
      return;
    }
    window.__renyuLanguageApplying = true;
    if (observer) {
      observer.disconnect();
    }
    try {
      callback();
    } finally {
      window.__renyuLanguageApplying = false;
      if (observer && document.body) {
        observer.observe(document.body, mutationOptions);
      }
    }
  }

  function applyTextNode(node, language) {
    if (!node?.nodeValue?.trim()) {
      return;
    }
    const nextValue = translateComposedText(node.nodeValue, language);
    if (nextValue !== node.nodeValue) {
      node.nodeValue = nextValue;
    }
  }

  function translateAttributes(root, language) {
    root.querySelectorAll("[placeholder]").forEach((element) => {
      const value = element.getAttribute("placeholder") || "";
      const nextValue = language === "en" ? PLACEHOLDERS[value] : PLACEHOLDER_EN_TO_ZH[value];
      if (nextValue && nextValue !== value) {
        element.setAttribute("placeholder", nextValue);
      }
    });
    root.querySelectorAll("[aria-label]").forEach((element) => {
      const value = element.getAttribute("aria-label") || "";
      const nextValue = language === "en" ? ATTR_TEXT[value] : ATTR_EN_TO_ZH[value];
      if (nextValue && nextValue !== value) {
        element.setAttribute("aria-label", nextValue);
      }
    });
  }

  function translateTextNodes(root, language) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const parent = node.parentElement;
        if (!parent || ["SCRIPT", "STYLE", "TEMPLATE"].includes(parent.tagName)) {
          return NodeFilter.FILTER_REJECT;
        }
        return node.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
      },
    });
    const nodes = [];
    while (walker.nextNode()) {
      nodes.push(walker.currentNode);
    }
    nodes.forEach((node) => applyTextNode(node, language));
  }

  function updateSwitcher(language) {
    const config = LANGUAGES[language];
    document.querySelectorAll("[data-language-switcher]").forEach((switcher) => {
      const current = switcher.querySelector("[data-language-current]");
      const region = switcher.querySelector("[data-language-region]");
      const trigger = switcher.querySelector(".language-trigger");
      setTextContent(current, config.current);
      setTextContent(region, config.region);
      switcher.querySelectorAll("[data-language-option]").forEach((option) => {
        const key = option.getAttribute("data-language-option");
        setTextContent(option, config.options[key] || key);
        option.classList.toggle("is-selected", key === language);
      });
      if (trigger) {
        trigger.setAttribute("aria-label", language === "en" ? "Language" : "语言");
      }
    });
  }

  function applyRenYuLanguage(language = selectedLanguage()) {
    const safeLanguage = language === "en" ? "en" : "zh";
    withLanguageMutationsPaused(() => {
      document.documentElement.lang = LANGUAGES[safeLanguage].htmlLang;
      document.documentElement.dataset.language = safeLanguage;
      translateTextNodes(document.body, safeLanguage);
      translateAttributes(document.body, safeLanguage);
      updateSwitcher(safeLanguage);
      localStorage.setItem(STORAGE_KEY, safeLanguage);
    });
    if (typeof document.dispatchEvent === "function") {
      const event = typeof CustomEvent === "function"
        ? new CustomEvent("renyu:languagechange", { detail: { language: safeLanguage } })
        : { type: "renyu:languagechange", detail: { language: safeLanguage } };
      document.dispatchEvent(event);
    }
  }

  function bindSwitchers() {
    document.querySelectorAll("[data-language-switcher]").forEach((switcher) => {
      const trigger = switcher.querySelector(".language-trigger");
      const menu = switcher.querySelector(".language-menu");
      if (trigger && menu) {
        trigger.addEventListener("click", () => {
          const nextOpen = menu.hidden;
          menu.hidden = !nextOpen;
          trigger.setAttribute("aria-expanded", String(nextOpen));
        });
      }
      switcher.querySelectorAll("[data-language-option]").forEach((option) => {
        option.addEventListener("click", () => {
          const language = option.getAttribute("data-language-option") === "en" ? "en" : "zh";
          if (menu) menu.hidden = true;
          if (trigger) trigger.setAttribute("aria-expanded", "false");
          applyRenYuLanguage(language);
        });
      });
    });
    document.addEventListener("click", (event) => {
      document.querySelectorAll("[data-language-switcher]").forEach((switcher) => {
        if (switcher.contains(event.target)) {
          return;
        }
        const menu = switcher.querySelector(".language-menu");
        const trigger = switcher.querySelector(".language-trigger");
        if (menu) menu.hidden = true;
        if (trigger) trigger.setAttribute("aria-expanded", "false");
      });
    });
  }

  function watchMutations() {
    observer = new MutationObserver((mutations) => {
      const language = selectedLanguage();
      withLanguageMutationsPaused(() => {
        mutations.forEach((mutation) => {
          mutation.addedNodes.forEach((node) => {
            if (node.nodeType === Node.ELEMENT_NODE) {
              translateTextNodes(node, language);
              translateAttributes(node, language);
            }
            if (node.nodeType === Node.TEXT_NODE) {
              applyTextNode(node, language);
            }
          });
        });
        updateSwitcher(language);
      });
    });
    observer.observe(document.body, mutationOptions);
  }

  window.applyRenYuLanguage = applyRenYuLanguage;

  document.addEventListener("DOMContentLoaded", () => {
    bindSwitchers();
    applyRenYuLanguage(selectedLanguage());
    watchMutations();
  });
})();
