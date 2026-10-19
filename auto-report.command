#!/bin/zsh
# Каждое утро в 8:00 его открывает расписание (launchd) — см. README. Можно запустить и вручную.
/bin/zsh "$(dirname "$0")/auto-report.sh" 2>&1 | tee -a "$HOME/Library/Logs/daily-report.log"
echo
echo "Окно можно закрыть."
