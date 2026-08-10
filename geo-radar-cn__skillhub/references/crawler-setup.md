# GEO 雷达 v2.0 · 爬虫环境搭建

## 1. 安装依赖

```bash
# Python 3.10+ 已装
python3 --version  # 应输出 3.10 或更高

# 安装 playwright
pip install playwright

# 下载 Chromium(~150MB)
playwright install chromium
```

## 2. 验证安装

```bash
python3 -c "from playwright.sync_api import sync_playwright; print('playwright OK')"
# 输出: playwright OK 即表示成功
```

## 3. 首次使用:登录各平台

```bash
cd /Users/shike/Desktop/code/location-skill/geo-radar-cn__skillhub
python3 -m crawler.runner --login
```

执行后:
- Playwright 打开 Chromium 浏览器(headless=False)
- 依次打开豆包/Kimi/通义的 tab
- 用户**手动**登录(扫码/手机验证/邮箱等)
- 登录完成后,在终端**按 Enter** 继续
- cookie 自动保存到 `~/.geo-radar-cn/browser-profile-{platform}/`
- 后续跑批无需重新登录(cookie 30 天有效)

## 4. cookie 管理

```bash
# cookie 目录
~/.geo-radar-cn/
├── browser-profile-doubao/    # 豆包 cookie
│   └── Default/
│       └── Cookies            # 加密的 sqlite db
├── browser-profile-kimi/       # Kimi cookie
└── browser-profile-tongyi/    # 通义 cookie
```

**清理**:`rm -rf ~/.geo-radar-cn/browser-profile-*/` 然后重新 `--login`

## 5. 跑批

```bash
# 完整跑批(3 平台 × 20 prompts = 60 次)
python3 -m crawler.runner \
  --brand "蜜雪冰城" \
  --auto-prompts \
  --category 奶茶 \
  --output json

# 输出文件: ~/.geo-radar-cn/reports/geo_report_蜜雪冰城_20260810-192000.json
#          ~/.geo-radar-cn/reports/geo_report_蜜雪冰城_20260810-192000.md
```

## 6. 截图管理

每次问询会截图(便于审计),保存在:
```
~/.geo-radar-cn/browser-profile-{platform}/screenshots/
├── doubao_1723296000000.png
├── kimi_1723296005000.png
└── tongyi_1723296010000.png
```

**自动清理**:7 天前的截图自动删除(可改 `scripts/crawler/doubao.py` 里的逻辑)

## 7. 常见问题

### Q: 跑批中途断网了怎么办?
A: 报告 JSON 里会标"问询失败:网络中断",其他已跑的结果保留。可重跑失败项。

### Q: 平台反爬了(出现验证码)怎么办?
A: 报告第 7 节"数据局限"会明示"该平台跑批受反爬限制",verdict 强制 🟡。需手动去浏览器完成验证码,然后重跑。

### Q: 文心一言 / 腾讯元宝 怎么加?
A: 复制 `scripts/crawler/doubao.py` 改 URL + selector 即可,v2.0.1 计划合并。

### Q: 海外 LLM (ChatGPT / Claude) 怎么加?
A: 需要海外环境 + 海外 playwright profile,v2.1 规划。

## 8. 性能基准(2026-08 实测,仅供参考)

- 3 平台 × 20 prompts = 60 次问询
- 平均 4-6 秒/次
- 总耗时 4-6 分钟
- CPU: 中等(M1/M2 Mac)
- 内存: ~500MB
- 网络: 持续 50-100 KB/s
