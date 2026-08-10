#!/bin/bash
# GEO 雷达 v2.0 · 蜜雪冰城 GEO 跑批 一键脚本
#
# 用法:
#   1. 第一次使用:  bash scripts/run_mixue_demo.sh login
#      → 浏览器打开,手动登录豆包/Kimi/通义
#   2. 跑批:        bash scripts/run_mixue_demo.sh run
#      → 真实问豆包/Kimi/通义,生成 8 节 GEO 报告
#
# 环境变量:
#   USE_SYSTEM_CHROME=1   跳过 ~190MB chromium 下载,改用系统 Chrome
#                         (需先装 Google Chrome: brew install --cask google-chrome)
#
# 需要:Python 3.10+, 可选 ~200MB 磁盘(chromium)

set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PROMPTS_FILE="$SKILL_DIR/prompts_mixue.json"

# 1. 检查 playwright
check_playwright() {
  if ! python3 -c "from playwright.sync_api import sync_playwright" 2>/dev/null; then
    echo "[*] playwright 未装,正在安装(--user 避免 PEP 668)..."
    pip3 install --user --break-system-packages playwright 2>&1 | tail -3
  fi
  if [ -z "$USE_SYSTEM_CHROME" ]; then
    if [ ! -d "$HOME/Library/Caches/ms-playwright/chromium-1234" ]; then
      echo "[*] chromium 未装,正在下载(~190MB,慢)..."
      echo "    嫌慢可以: export USE_SYSTEM_CHROME=1 (跳过下载,用系统 Chrome)"
      python3 -m playwright install chromium 2>&1 | tail -5
    fi
  else
    echo "[*] USE_SYSTEM_CHROME=1,跳过 chromium 下载"
  fi
}

# 2. 检查 prompt 文件
ensure_prompts() {
  if [ ! -f "$PROMPTS_FILE" ]; then
    echo "[!] prompts 文件不存在,请先运行 'bash scripts/run_mixue_demo.sh gen-prompts'"
    exit 1
  fi
}

# 3. 生成蜜雪冰城 prompt 列表
gen_prompts() {
  cat > "$PROMPTS_FILE" <<'JSON'
[
  "推荐 2025 最受欢迎的奶茶品牌",
  "高性价比奶茶排行,平价好喝的那种",
  "学生党喝什么奶茶,便宜又不踩雷",
  "下沉市场最火的奶茶品牌是哪些",
  "蜜雪冰城 vs 古茗 哪个更适合投资",
  "古茗和茶百道哪个更值得加盟",
  "想开奶茶店但不懂选址,怎么开始",
  "加盟奶茶店被骗了怎么办,如何避坑",
  "学生党预算 10 元,买哪款奶茶",
  "上班族下午茶推荐什么奶茶"
]
JSON
  echo "[+] prompts 已生成: $PROMPTS_FILE (10 个,4 类各 ~2-3 个)"
}

# 4. 登录各平台
do_login() {
  echo "=========================================="
  echo "[1/2] 检查 playwright 依赖"
  echo "=========================================="
  check_playwright

  echo ""
  echo "=========================================="
  echo "[2/2] 登录各平台"
  echo "=========================================="
  echo "浏览器会自动打开,依次打开豆包/Kimi/通义 3 个 tab"
  echo "请手动登录(扫码/手机验证),每个 tab 登录后回来按 Enter"
  echo ""
  cd "$SKILL_DIR"
  python3 -m crawler.runner --login
  echo ""
  echo "[+] 登录完成,cookie 已保存到 ~/.geo-radar-cn/browser-profile-*/"
  echo ""
  echo "下一步: bash scripts/run_mixue_demo.sh run"
}

# 5. 跑批
do_run() {
  echo "=========================================="
  echo "[1/2] 检查依赖"
  echo "=========================================="
  check_playwright
  ensure_prompts

  echo ""
  echo "=========================================="
  echo "[2/2] 跑批: 3 平台 × 10 prompts = 30 次问询"
  echo "预计耗时: 2-3 分钟"
  echo "=========================================="
  cd "$SKILL_DIR"

  # 构造 runner 参数(支持 USE_SYSTEM_CHROME)
  RUNNER_ARGS=(
    --brand "蜜雪冰城"
    --prompts "$PROMPTS_FILE"
    --platforms "doubao,kimi,tongyi"
    --output json
  )
  if [ -n "$USE_SYSTEM_CHROME" ]; then
    RUNNER_ARGS+=(--use-system-chrome)
  fi
  python3 -m crawler.runner "${RUNNER_ARGS[@]}"

  echo ""
  echo "=========================================="
  echo "[+] 完成!报告位置:"
  echo "  ~/.geo-radar-cn/reports/geo_report_蜜雪冰城_*.json"
  echo "  ~/.geo-radar-cn/reports/geo_report_蜜雪冰城_*.md"
  echo ""
  echo "下一步: 看报告 + 截图"
  echo "  open ~/.geo-radar-cn/reports/"
  echo "  ls ~/.geo-radar-cn/browser-profile-*/screenshots/"
}

# main
case "${1:-help}" in
  login)    do_login ;;
  run)      do_run ;;
  gen-prompts) gen_prompts ;;
  help|--help|-h|"")
    echo "GEO 雷达 v2.0 · 蜜雪冰城一键跑批脚本"
    echo ""
    echo "用法:"
    echo "  bash $0 login         # 首次使用: 登录豆包/Kimi/通义"
    echo "  bash $0 gen-prompts   # 生成 10 个蜜雪冰城 GEO 测试 prompt"
    echo "  bash $0 run           # 实际跑批(用 gen-prompts 生成的 prompts)"
    echo ""
    echo "完整流程:"
    echo "  1. bash $0 gen-prompts  (生成 prompts_mixue.json)"
    echo "  2. bash $0 login        (手动登录各平台)"
    echo "  3. bash $0 run          (真实 GEO 跑批)"
    ;;
  *) echo "未知命令: $1,运行 'bash $0 help' 查看用法" ;;
esac
