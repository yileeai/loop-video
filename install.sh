#!/usr/bin/env bash
# 用法：bash install.sh            → 装到 ~/.claude/skills（任何文件夹都能用）
#       bash install.sh 某个库路径  → 只装进那个库
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
if [ $# -ge 1 ]; then DEST="$1/.claude/skills"; else DEST="$HOME/.claude/skills"; fi
mkdir -p "$DEST"
cp -R "$HERE/skills/." "$DEST/"
if [ $# -ge 1 ] && [ -d "$1/_claude-skills" ]; then cp -R "$HERE/skills/." "$1/_claude-skills/"; fi
echo "完成：视频技能已安装到 $DEST"
echo "需要 Python 3、Pillow ≥ 10、FFmpeg。重启 Claude Code 后输入 /speech-motion-edit"
