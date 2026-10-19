#!/bin/zsh
# Двойной щелчок в Finder — собирает отчёт за вчера и открывает его на компьютере.
# На сайт отчёт выкладывает GitHub Actions (каждое утро в 08:00 и сразу после этого запуска).
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"
/usr/bin/python3 report.py || exit 1
if [ -x "$HOME/remontlanding-data/sync.sh" ]; then
  echo "Отправляю записи на GitHub…"
  "$HOME/remontlanding-data/sync.sh" >/dev/null 2>&1
  if gh workflow run daily-report.yml -R antonbunin985-a11y/remontlanding-data >/dev/null 2>&1; then
    echo "Через пару минут отчёт обновится на сайте: https://remontlanding.netlify.app"
  else
    echo "Не получилось запустить выкладку — сайт обновится утром сам."
  fi
fi
