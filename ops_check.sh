#!/usr/bin/env bash
set -euo pipefail

# 自动获取脚本所在目录（写成绝对路径，后续配定时任务才不会找不到文件）
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_FILE="$PROJECT_DIR/data/users.db"
LOG_FILE="$PROJECT_DIR/app.log"
BACKUP_DIR="$PROJECT_DIR/backups"
TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"

echo "=== 开始执行运维巡检 [$TIMESTAMP] ==="

# 1. 自动备份用户数据
mkdir -p "$BACKUP_DIR"
if [ -f "$DATA_FILE" ]; then
    BACKUP_FILE="$BACKUP_DIR/users_${TIMESTAMP}.db"
    cp "$DATA_FILE" "$BACKUP_FILE"
    echo "[备份成功] 已生成: $BACKUP_FILE"
else
    echo "[跳过备份] 未找到数据文件: $DATA_FILE"
fi

# 2. 巡检日志中的异常告警
if [ -f "$LOG_FILE" ]; then
    ALERT_COUNT=$(grep -cE "WARNING|ERROR|CRITICAL" "$LOG_FILE" || true)
    echo "[日志巡检] 共发现 $ALERT_COUNT 条异常记录"
    if [ "$ALERT_COUNT" -gt 0 ]; then
        echo "--- 最近 5 条异常日志 ---"
        grep -E "WARNING|ERROR|CRITICAL" "$LOG_FILE" | tail -n 5
    fi
else
    echo "[跳过巡检] 未找到日志文件: $LOG_FILE"
fi

echo "=== 运维巡检结束 ==="
