# Vercel + Google Search 发布说明

## Vercel 部署

1. 把项目推到 GitHub、GitLab 或 Bitbucket。
2. 在 Vercel 导入这个仓库，Framework Preset 选择 Other 或让 Vercel 自动识别 Python/FastAPI。
3. Build Command 保持仓库里的 `vercel.json` 设置即可；它会执行 `python scripts/prepare_vercel_public.py`，把 `static/` 同步到 `public/static/`。
4. 需要 DeepSeek/OpenRouter 润色时，在 Vercel Environment Variables 配置 `DEEPSEEK_API_KEY` 或 `OPENROUTER_API_KEY`。
5. 绑定自定义域名后，建议配置 `PUBLIC_SITE_URL=https://你的域名`，用于生成 sitemap URL。

不要把本地的 `Python/`、日志、缓存或测试产物上传到仓库；这些已在 `.gitignore` 和 `.vercelignore` 中排除。

## Google 收录准备

1. 部署成功后确认以下地址可访问：
   - `/`
   - `/app`
   - `/robots.txt`
   - `/sitemap.xml`
2. 在 Google Search Console 添加站点资源并完成域名验证。
3. 在 Search Console 提交 `https://你的域名/sitemap.xml`。
4. 等待 Google 抓取。Sitemap 是抓取提示，不保证立刻收录；页面仍需要可访问、可索引、有稳定内容。

## 当前发布边界

项目首页和工作台已允许索引，接口路径 `/api/` 在 `robots.txt` 中禁止普通抓取，避免搜索结果暴露内部 JSON 接口。
