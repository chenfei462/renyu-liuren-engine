const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "..");
const source = fs.readFileSync(path.join(root, "static", "realtime", "language.js"), "utf8");

let observerCallbackCount = 0;
const observers = [];

const Node = {
  ELEMENT_NODE: 1,
  TEXT_NODE: 3,
};

const NodeFilter = {
  SHOW_TEXT: 4,
  FILTER_ACCEPT: 1,
  FILTER_REJECT: 2,
};

function createClassList(initial = []) {
  const names = new Set(initial);
  return {
    add(name) {
      names.add(name);
    },
    remove(name) {
      names.delete(name);
    },
    toggle(name, force) {
      if (force === undefined) {
        if (names.has(name)) {
          names.delete(name);
          return false;
        }
        names.add(name);
        return true;
      }
      if (force) {
        names.add(name);
      } else {
        names.delete(name);
      }
      return !!force;
    },
    contains(name) {
      return names.has(name);
    },
  };
}

function toDatasetKey(name) {
  return name.slice(5).replace(/-([a-z])/g, (_, char) => char.toUpperCase());
}

function notifyChildList(target, addedNodes) {
  observers.forEach((observer) => {
    if (!observer.active || !observer.options.childList) {
      return;
    }
    const inScope = observer.target === target || (observer.options.subtree && observer.target.contains(target));
    if (!inScope) {
      return;
    }
    observerCallbackCount += 1;
    if (observerCallbackCount > 8) {
      throw new Error("MutationObserver callback count exceeded safe bound");
    }
    observer.callback([{ type: "childList", target, addedNodes }]);
  });
}

class TextNode {
  constructor(value) {
    this.nodeType = Node.TEXT_NODE;
    this.parentElement = null;
    this._nodeValue = String(value);
  }

  get nodeValue() {
    return this._nodeValue;
  }

  set nodeValue(value) {
    this._nodeValue = String(value);
  }

  get textContent() {
    return this._nodeValue;
  }

  set textContent(value) {
    this._nodeValue = String(value);
  }
}

class ElementNode {
  constructor(tagName, attrs = {}, children = []) {
    this.nodeType = Node.ELEMENT_NODE;
    this.tagName = tagName.toUpperCase();
    this.parentElement = null;
    this.childNodes = [];
    this.attributes = {};
    this.dataset = {};
    this.listeners = {};
    this.hidden = false;
    this.classList = createClassList();
    Object.entries(attrs).forEach(([name, value]) => this.setAttribute(name, value));
    children.forEach((child) => this.appendChild(child));
  }

  appendChild(node) {
    node.parentElement = this;
    this.childNodes.push(node);
    notifyChildList(this, [node]);
    return node;
  }

  contains(node) {
    if (node === this) {
      return true;
    }
    return this.childNodes.some((child) => child.nodeType === Node.ELEMENT_NODE && child.contains(node));
  }

  get textContent() {
    return this.childNodes.map((child) => child.textContent).join("");
  }

  set textContent(value) {
    this.childNodes = [new TextNode(value)];
    this.childNodes[0].parentElement = this;
    notifyChildList(this, this.childNodes);
  }

  setAttribute(name, value) {
    const stringValue = String(value);
    this.attributes[name] = stringValue;
    if (name === "class") {
      this.classList = createClassList(stringValue.split(/\s+/).filter(Boolean));
    }
    if (name.startsWith("data-")) {
      this.dataset[toDatasetKey(name)] = stringValue;
    }
  }

  getAttribute(name) {
    return Object.prototype.hasOwnProperty.call(this.attributes, name) ? this.attributes[name] : null;
  }

  addEventListener(type, handler) {
    this.listeners[type] = handler;
  }

  click() {
    if (this.listeners.click) {
      this.listeners.click({ target: this });
    }
  }

  matches(selector) {
    if (selector.startsWith(".")) {
      return this.classList.contains(selector.slice(1));
    }
    if (selector === "[placeholder]") {
      return this.getAttribute("placeholder") !== null;
    }
    if (selector === "[aria-label]") {
      return this.getAttribute("aria-label") !== null;
    }
    const attrMatch = selector.match(/^\[([^=\]]+)(?:="([^"]*)")?\]$/);
    if (attrMatch) {
      const [, name, expected] = attrMatch;
      const actual = this.getAttribute(name);
      return expected === undefined ? actual !== null : actual === expected;
    }
    return false;
  }

  querySelectorAll(selector) {
    const results = [];
    const visit = (node) => {
      if (node.nodeType !== Node.ELEMENT_NODE) {
        return;
      }
      if (node.matches(selector)) {
        results.push(node);
      }
      node.childNodes.forEach(visit);
    };
    this.childNodes.forEach(visit);
    return results;
  }

  querySelector(selector) {
    return this.querySelectorAll(selector)[0] || null;
  }
}

class MutationObserver {
  constructor(callback) {
    this.callback = callback;
    this.active = false;
    this.target = null;
    this.options = {};
    observers.push(this);
  }

  observe(target, options) {
    this.active = true;
    this.target = target;
    this.options = options;
  }

  disconnect() {
    this.active = false;
  }
}

function text(value) {
  return new TextNode(value);
}

function element(tagName, attrs = {}, children = []) {
  return new ElementNode(tagName, attrs, children);
}

const trigger = element("button", { class: "language-trigger", "aria-label": "语言" }, [
  element("span", { "data-language-region": "" }, [text("中")]),
  element("span", { "data-language-current": "" }, [text("中文")]),
]);
const zhOption = element("button", { "data-language-option": "zh" }, [text("中文")]);
const enOption = element("button", { "data-language-option": "en" }, [text("英文")]);
const menu = element("div", { class: "language-menu" }, [zhOption, enOption]);
menu.hidden = true;

const switcher = element("div", { "data-language-switcher": "" }, [trigger, menu]);
const heading = element("h2", {}, [text("本次占问")]);
const input = element("input", {
  placeholder: "例如：明天出行是否顺利？这个合作能不能推进？",
});
const releaseOverview = element("section", { "aria-label": "发布状态总览" }, [
  element("h3", {}, [text("发布总控")]),
  element("h3", {}, [text("当前阻断")]),
  element("h3", {}, [text("下一步")]),
  element("a", {}, [text("发布准入")]),
  element("a", {}, [text("灰度报告")]),
  element("a", {}, [text("支付报告")]),
  element("span", {}, [text("阶段 15")]),
  element("strong", {}, [text("支付准备")]),
  element("p", {}, [text("正在读取沙箱订单、退款和支付能力。")]),
]);
const dynamic = element("div", {}, []);

const document = {
  documentElement: element("html", {}, []),
  body: element("body", {}, [switcher, heading, input, releaseOverview, dynamic]),
  listeners: {},
  addEventListener(type, handler) {
    this.listeners[type] = handler;
  },
  dispatchEvent(event) {
    if (this.listeners[event.type]) {
      this.listeners[event.type](event);
    }
  },
  querySelectorAll(selector) {
    return this.body.querySelectorAll(selector);
  },
  createTreeWalker(rootNode, whatToShow, filter) {
    const nodes = [];
    const visit = (node) => {
      if (node.nodeType === Node.TEXT_NODE) {
        if (whatToShow === NodeFilter.SHOW_TEXT && filter.acceptNode(node) === NodeFilter.FILTER_ACCEPT) {
          nodes.push(node);
        }
        return;
      }
      node.childNodes.forEach(visit);
    };
    visit(rootNode);
    let index = -1;
    return {
      currentNode: null,
      nextNode() {
        index += 1;
        this.currentNode = nodes[index] || null;
        return !!this.currentNode;
      },
    };
  },
};

const storage = {};
const localStorage = {
  getItem(key) {
    return Object.prototype.hasOwnProperty.call(storage, key) ? storage[key] : null;
  },
  setItem(key, value) {
    storage[key] = String(value);
  },
};

const window = {};
const context = {
  console,
  document,
  localStorage,
  MutationObserver,
  Node,
  NodeFilter,
  window,
};
window.window = window;
window.document = document;
window.localStorage = localStorage;

vm.createContext(context);
vm.runInContext(source, context, { filename: "language.js" });
document.dispatchEvent({ type: "DOMContentLoaded" });

enOption.click();
const afterEnglishClick = {
  heading: heading.textContent,
  placeholder: input.getAttribute("placeholder"),
  current: trigger.querySelector("[data-language-current]").textContent,
  releaseOverviewText: releaseOverview.textContent,
  releaseOverviewLabel: releaseOverview.getAttribute("aria-label"),
  callbackCount: observerCallbackCount,
};

const chineseBusinessCopy = "针对 Q-001 合作推进：先看三传，再看 Beta 阶段的边界，不要承诺现实结果。";
dynamic.appendChild(element("p", {}, [text(chineseBusinessCopy)]));
const afterBusinessAppendInEnglish = {
  dynamicText: dynamic.textContent,
  callbackCount: observerCallbackCount,
};

zhOption.click();
const afterBusinessAppendBackToChinese = {
  dynamicText: dynamic.textContent,
  callbackCount: observerCallbackCount,
};

enOption.click();
dynamic.appendChild(element("p", {}, [text("安全边界优先")]));
dynamic.appendChild(text("学习资料"));
const afterDynamicAppend = {
  dynamicText: dynamic.textContent,
  callbackCount: observerCallbackCount,
};

zhOption.click();
const afterChineseClick = {
  heading: heading.textContent,
  dynamicText: dynamic.textContent,
  current: trigger.querySelector("[data-language-current]").textContent,
  callbackCount: observerCallbackCount,
};

const result = {
  afterEnglishClick,
  afterBusinessAppendInEnglish,
  afterBusinessAppendBackToChinese,
  afterDynamicAppend,
  afterChineseClick,
};

if (afterEnglishClick.heading !== "Question") {
  throw new Error(`Expected translated heading after English click, got ${afterEnglishClick.heading}`);
}
if (!afterEnglishClick.placeholder.startsWith("Example:")) {
  throw new Error(`Expected English placeholder, got ${afterEnglishClick.placeholder}`);
}
if (/[\u4e00-\u9fff]/.test(afterEnglishClick.releaseOverviewText)) {
  throw new Error(`Expected release overview static copy in English, got ${afterEnglishClick.releaseOverviewText}`);
}
if (afterEnglishClick.releaseOverviewLabel !== "Launch status overview") {
  throw new Error(`Expected English release overview aria-label, got ${afterEnglishClick.releaseOverviewLabel}`);
}
if (afterBusinessAppendInEnglish.dynamicText !== chineseBusinessCopy) {
  throw new Error(`Expected business copy to be preserved, got ${afterBusinessAppendInEnglish.dynamicText}`);
}
if (afterBusinessAppendBackToChinese.dynamicText !== chineseBusinessCopy) {
  throw new Error(`Expected business copy to survive Chinese switch, got ${afterBusinessAppendBackToChinese.dynamicText}`);
}
if (afterBusinessAppendInEnglish.dynamicText.includes("Status information is being prepared")) {
  throw new Error(`Business copy was replaced by English fallback: ${afterBusinessAppendInEnglish.dynamicText}`);
}
if (afterBusinessAppendBackToChinese.dynamicText.includes("状态信息读取中")) {
  throw new Error(`Business copy was replaced by Chinese fallback: ${afterBusinessAppendBackToChinese.dynamicText}`);
}
if (afterDynamicAppend.dynamicText !== `${chineseBusinessCopy}Safety firstLearning material`) {
  throw new Error(`Expected dynamic English translation, got ${afterDynamicAppend.dynamicText}`);
}
if (afterChineseClick.heading !== "本次占问") {
  throw new Error(`Expected translated heading after Chinese click, got ${afterChineseClick.heading}`);
}
if (afterChineseClick.dynamicText !== `${chineseBusinessCopy}安全边界优先学习资料`) {
  throw new Error(`Expected dynamic Chinese translation, got ${afterChineseClick.dynamicText}`);
}

console.log(JSON.stringify(result));
