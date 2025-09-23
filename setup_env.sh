#!/bin/bash
# 一键设置项目所需的环境变量；执行：
#   source ./setup_env.sh

export ARK_API_KEY="9d9b53eb-d58b-4763-b8f8-54f99c461948"
# 兼容HTTP接口调用的变量名（本仓库其它脚本使用 DOUBAO_API_KEY）
export DOUBAO_API_KEY="${ARK_API_KEY}"

export DOUBAO_BASE_URL="https://ark.cn-beijing.volces.com/api/v3/chat/completions"
export DOUBAO_MODEL="doubao-seed-1-6-250615"

# 禁用本地降级，强制走云端
export VOICE_FALLBACK="0"

# 可选：为官方实时语音接口预留的环境变量（如你已有，请在此处填写）
# export DOUBAO_API_APP_ID=""
# export DOUBAO_API_ACCESS_KEY=""
# export DOUBAO_API_APP_KEY=""
# export DOUBAO_API_RESOURCE_ID="volc.speech.dialog"

echo "✅ 环境变量已导出。当前关键变量："
echo "  ARK_API_KEY=***${ARK_API_KEY: -6}"
echo "  DOUBAO_BASE_URL=${DOUBAO_BASE_URL}"
echo "  DOUBAO_MODEL=${DOUBAO_MODEL}"
echo "  VOICE_FALLBACK=${VOICE_FALLBACK}"

# 同步写入 .env 供 python-dotenv 读取
cat > ./.env <<EOF
DOUBAO_API_KEY=${DOUBAO_API_KEY}
DOUBAO_BASE_URL=${DOUBAO_BASE_URL}
DOUBAO_MODEL=${DOUBAO_MODEL}
VOICE_FALLBACK=${VOICE_FALLBACK}
EOF

echo "📄 已更新 .env 文件（用于 python-dotenv 读取）。"
