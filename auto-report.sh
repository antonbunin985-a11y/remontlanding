#!/bin/zsh
# Запускается сам каждое утро (через launchd): собирает отчёт за вчера и выкладывает его на сайт.
# Если данных за вчера нет — откроет пустой файл для заполнения и пришлёт уведомление.
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:/usr/bin:/bin:/usr/sbin:/sbin"
echo "=== $(date '+%Y-%m-%d %H:%M') ==="

notify() {
  /usr/bin/osascript -e "display notification \"$1\" with title \"Ежедневный отчёт\""
}

yesterday=$(date -v-1d +%Y-%m-%d)
had_data=0
[ -f "data/$yesterday.txt" ] && had_data=1

/usr/bin/python3 report.py --no-open || { notify "Не получилось собрать отчёт"; exit 1; }

if [ $had_data -eq 0 ]; then
  notify "За вчера нет записей — открыл файл. Заполните его и дважды щёлкните «Открыть отчёт»."
  exit 0
fi

if [ -f .netlify/state.json ] && netlify deploy --dir reports --prod --no-build >/dev/null 2>&1; then
  echo "Выложено на сайт"
  notify "Отчёт за вчера готов и выложен на remontlanding.netlify.app"
else
  echo "Выложить на сайт не получилось"
  notify "Отчёт собран, но выложить на сайт не получилось (нет интернета?)"
fi
