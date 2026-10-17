#!/bin/zsh
# Двойной щелчок в Finder — собирает отчёт за вчера, открывает его и выкладывает на сайт.
cd "$(dirname "$0")"
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:$PATH"
/usr/bin/python3 report.py || exit 1
if [ -f .netlify/state.json ]; then
  echo "Выкладываю на сайт…"
  netlify deploy --dir reports --prod --no-build >/dev/null 2>&1 \
    && echo "На сайте: https://remontlanding.netlify.app" \
    || echo "Выложить на сайт не получилось — отчёт есть только на компьютере."
fi
