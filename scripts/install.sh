#!/bin/bash
# Hermes House 安装脚本

set -e

echo "🏠 Hermes House 安装程序"
echo "========================="

# 检测操作系统
OS=$(uname -s)
echo "检测到系统: $OS"

# 安装目录
HERMES_SKILLS="$HOME/.hermes/skills"

# 创建目录
mkdir -p "$HERMES_SKILLS/devops"

# 复制技能
echo "📦 安装技能..."

if [ -d "skills" ]; then
    cp -r skills/* "$HERMES_SKILLS/devops/"
    echo "✅ 技能已安装到 $HERMES_SKILLS/devops/"
else
    echo "❌ 未找到 skills 目录，请确保在仓库根目录运行此脚本"
    exit 1
fi

# 验证安装
echo ""
echo "📋 已安装技能:"
ls -la "$HERMES_SKILLS/devops/"

echo ""
echo "🎉 安装完成！"
echo ""
echo "使用示例："
echo "  hermes skills list    # 查看已安装技能"
echo "  hermes skills enable <skill-name>  # 启用技能"