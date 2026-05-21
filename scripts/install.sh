#!/usr/bin/env bash
# Hermes House installer
#
# Installs the Harmes-House skill pack into the active Hermes home.
# Prefer HERMES_HOME over HOME/.hermes because embedded runtimes such as
# Hermes WebUI may sandbox HOME while the active config lives under HERMES_HOME.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_SKILLS="$REPO_ROOT/skills"
HERMES_HOME_PATH="${HERMES_HOME:-$HOME/.hermes}"
TARGET_ROOT=""
MODE="standard"

print_usage() {
  cat <<'USAGE'
🏠 Hermes House 安装程序

用法：
  bash scripts/install.sh [--core|--standard|--full] [--target PATH]
  bash scripts/install.sh [--core|--standard|--full] [PATH]

模式：
  --core      只安装 A 档核心技能（32 个）
  --standard  安装 A+B 档推荐技能（78 个，默认）
  --full      安装全部技能（101 个，含强场景/个人化/C 档）

示例：
  bash scripts/install.sh
  bash scripts/install.sh --core
  bash scripts/install.sh --full --target "$HERMES_HOME/skills/harmes-house"
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --core)
      MODE="core"
      shift
      ;;
    --standard)
      MODE="standard"
      shift
      ;;
    --full)
      MODE="full"
      shift
      ;;
    -t|--target)
      if [ "$#" -lt 2 ]; then
        echo "❌ --target 需要路径参数。"
        exit 1
      fi
      TARGET_ROOT="$2"
      shift 2
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    --*)
      echo "❌ 未知参数: $1"
      print_usage
      exit 1
      ;;
    *)
      if [ -n "$TARGET_ROOT" ]; then
        echo "❌ 只能指定一个安装目标路径。"
        exit 1
      fi
      TARGET_ROOT="$1"
      shift
      ;;
  esac
done

TARGET_ROOT="${TARGET_ROOT:-$HERMES_HOME_PATH/skills/harmes-house}"

CORE_SKILLS=(
  'claude-code'
  'cli-utilities'
  'codebase-inspection'
  'codex'
  'copilot-cli'
  'custom-openai-provider'
  'debugging-hermes-tui-commands'
  'github-auth'
  'github-code-review'
  'github-issues'
  'github-pages-site'
  'github-pr-workflow'
  'github-repo-management'
  'hermes-agent'
  'hermes-agent-skill-authoring'
  'hermes-telegram-setup'
  'matplotlib-charts'
  'model-fallback'
  'native-mcp'
  'node-inspect-debugger'
  'opencode'
  'plan'
  'python-debugpy'
  'report-generation'
  'requesting-code-review'
  'spike'
  'sqlite-data'
  'subagent-driven-development'
  'systematic-debugging'
  'test-driven-development'
  'webhook-subscriptions'
  'writing-plans'
)

OPTIONAL_SKILLS=(
  'airtable'
  'architecture-diagram'
  'arxiv'
  'baoyu-comic'
  'baoyu-infographic'
  'blogwatcher'
  'claude-design'
  'comfyui'
  'design-md'
  'evaluation'
  'excalidraw'
  'github-trend-daily'
  'google-workspace'
  'himalaya'
  'huggingface-hub'
  'humanizer'
  'inference'
  'jupyter-live-kernel'
  'linear'
  'llm-wiki'
  'mails'
  'manim-video'
  'maps'
  'models'
  'nano-pdf'
  'notion'
  'obsidian'
  'ocr-and-documents'
  'p5js'
  'polymarket'
  'popular-web-designs'
  'powerpoint'
  'pretext'
  'public-api-tools'
  'research'
  'research-paper-writing'
  'scrapling'
  'seo-verify'
  'sketch'
  'training'
  'trendradar'
  'trendradar-daily'
  'vector-databases'
  'website-seo'
  'xurl'
  'youtube-content'
)

EXTRA_SKILLS=(
  '3x-ui'
  'apple-notes'
  'apple-reminders'
  'ascii-art'
  'ascii-video'
  'creative-ideation'
  'findmy'
  'foreign-trade-operations'
  'gif-search'
  'godmode'
  'heartmula'
  'imessage'
  'kanban-orchestrator'
  'kanban-worker'
  'minecraft-modpack-server'
  'npm-publishing'
  'openhue'
  'pixel-art'
  'pokemon-player'
  'songsee'
  'songwriting-and-ai-music'
  'spotify'
  'touchdesigner-mcp'
)

case "$MODE" in
  core)
    INSTALL_SKILLS=("${CORE_SKILLS[@]}")
    MODE_LABEL="A 档核心"
    ;;
  standard)
    INSTALL_SKILLS=("${CORE_SKILLS[@]}" "${OPTIONAL_SKILLS[@]}")
    MODE_LABEL="A+B 档推荐"
    ;;
  full)
    INSTALL_SKILLS=("${CORE_SKILLS[@]}" "${OPTIONAL_SKILLS[@]}" "${EXTRA_SKILLS[@]}")
    MODE_LABEL="全量"
    ;;
  *)
    echo "❌ 无效安装模式: $MODE"
    exit 1
    ;;
esac
ALL_KNOWN_SKILLS=("${CORE_SKILLS[@]}" "${OPTIONAL_SKILLS[@]}" "${EXTRA_SKILLS[@]}")

if [ ! -d "$SOURCE_SKILLS" ]; then
  echo "❌ 未找到 skills 目录，请确保仓库完整。"
  exit 1
fi

if ! command -v hermes >/dev/null 2>&1; then
  echo "⚠️  未检测到 hermes 命令。"
  echo "先安装 Hermes Agent："
  echo "  curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash"
  echo "然后重新运行："
  echo "  bash scripts/install.sh"
  exit 1
fi

missing=0
for skill in "${INSTALL_SKILLS[@]}"; do
  if [ ! -d "$SOURCE_SKILLS/$skill" ]; then
    echo "❌ 缺少技能目录: $SOURCE_SKILLS/$skill"
    missing=1
  fi
done
if [ "$missing" -ne 0 ]; then
  exit 1
fi

CONFIG_PATH="$(hermes config path 2>/dev/null || true)"

echo "🏠 Hermes House 安装程序"
echo "========================="
echo "仓库目录: $REPO_ROOT"
echo "Hermes Home: $HERMES_HOME_PATH"
if [ -n "$CONFIG_PATH" ]; then
  echo "Hermes 配置: $CONFIG_PATH"
fi
echo "技能来源: $SOURCE_SKILLS"
echo "安装目标: $TARGET_ROOT"
echo "安装模式: $MODE ($MODE_LABEL, ${#INSTALL_SKILLS[@]} 个技能)"
echo ""

echo "📦 同步技能..."
mkdir -p "$TARGET_ROOT"

# Remove only known Harmes-House skill directories so switching from --full to
# --standard/--core does not leave stale C/B skills behind, while unrelated
# files in a custom target directory are preserved.
for skill in "${ALL_KNOWN_SKILLS[@]}"; do
  rm -rf "$TARGET_ROOT/$skill"
done

for skill in "${INSTALL_SKILLS[@]}"; do
  cp -R "$SOURCE_SKILLS/$skill" "$TARGET_ROOT/"
done

installed_count=0
for skill in "${INSTALL_SKILLS[@]}"; do
  if [ -d "$TARGET_ROOT/$skill" ]; then
    installed_count=$((installed_count + 1))
  fi
done

if [ "$installed_count" -ne "${#INSTALL_SKILLS[@]}" ]; then
  echo "❌ 安装数量不一致：期望 ${#INSTALL_SKILLS[@]}，实际 $installed_count"
  exit 1
fi

echo "✅ 已同步 $installed_count 个技能到 $TARGET_ROOT"
echo ""
echo "🔍 验证："
echo "  hermes skills list"
echo "  hermes -s harmes-house/hermes-agent"
echo ""
echo "💡 下一步："
echo "  1. 在当前 Hermes 会话输入 /reset，或重新启动 hermes，让新技能生效。"
echo "  2. 默认 --standard 不安装 C 档；需要全量时运行 bash scripts/install.sh --full。"
echo "  3. 需要 Telegram / GitHub 集成时，复制 .env.example 并填入自己的密钥。"
