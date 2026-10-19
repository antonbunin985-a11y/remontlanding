#!/usr/bin/env python3
"""Собирает ежедневный отчёт из data/ГГГГ-ММ-ДД.txt в reports/отчёт-ГГГГ-ММ-ДД.html.

Запуск: python3 report.py            — отчёт за вчера
        python3 report.py 2026-10-17 — отчёт за выбранный день
"""
import datetime
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Записи за дни лежат в закрытом репозитории remontlanding-data (на Mac — ~/remontlanding-data),
# оттуда они сами уходят на GitHub. Если такой папки нет (например, в GitHub Actions) — берём data/ рядом.
ENTRIES = Path.home() / "remontlanding-data" / "data"
DATA = ENTRIES if ENTRIES.is_dir() else ROOT / "data"
REPORTS = ROOT / "reports"
TEMPLATE = ROOT / "data" / "_шаблон.txt"

SECTIONS = {"сделано": "done", "цифры": "metrics", "на сегодня": "today"}
MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля",
          "августа", "сентября", "октября", "ноября", "декабря"]
WEEKDAYS = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]


def parse(path):
    """Читает файл дня: списки «Сделано» и «На сегодня», числа из «Цифры»."""
    day = {"done": [], "metrics": {}, "today": []}
    section = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("# ") or line == "#":
            continue
        if line.startswith("##"):
            section = SECTIONS.get(line.lstrip("#").strip().lower())
            continue
        if section == "metrics":
            name, sep, value = line.partition(":")
            number = re.sub(r"[^\d,.\-]", "", value).replace(",", ".")
            if sep and number:
                day["metrics"][name.strip()] = float(number)
        elif section:
            item = line.lstrip("-•* ").strip()
            if item:
                day[section].append(item)
    return day


def previous_file(date):
    """Ближайший более ранний день, за который есть данные."""
    earlier = sorted(p for p in DATA.glob("????-??-??.txt") if p.stem < date.isoformat())
    return earlier[-1] if earlier else None


def fmt(n):
    text = f"{n:,.2f}".rstrip("0").rstrip(".")
    return text.replace(",", " ")


def human_date(d):
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}, {WEEKDAYS[d.weekday()]}"


def items(lst, empty):
    if not lst:
        return f'<p class="empty">{empty}</p>'
    return "<ul>" + "".join(f"<li>{html.escape(x)}</li>" for x in lst) + "</ul>"


def metrics_html(cur, prev, prev_date):
    if not cur:
        return '<p class="empty">Цифр за день нет</p>'
    cards = []
    for name, value in cur.items():
        delta = ""
        if name in prev:
            diff = value - prev[name]
            cls = "up" if diff > 0 else "down" if diff < 0 else "same"
            sign = "+" if diff > 0 else "−" if diff < 0 else "±"
            delta = f'<div class="delta {cls}">{sign}{fmt(abs(diff))} к {prev_date}</div>'
        cards.append(f'<div class="card"><div class="label">{html.escape(name)}</div>'
                     f'<div class="value">{fmt(value)}</div>{delta}</div>')
    return '<div class="cards">' + "".join(cards) + "</div>"


def render(date, day, prev, prev_date):
    made = datetime.datetime.now().strftime("%d.%m.%Y %H:%M")
    return f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Отчёт за {date.strftime('%d.%m.%Y')}</title>
<style>
  :root {{ --bg:#f6f5f2; --panel:#fff; --text:#1d1d1f; --muted:#6e6e73; --line:#e5e3de;
          --up:#1a7f37; --down:#c0392b; --accent:#2f5bea; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#161618; --panel:#212124; --text:#f2f2f2; --muted:#9a9aa0; --line:#333338;
            --up:#4cc26a; --down:#ff6b5e; --accent:#7c9cff; }} }}
  body {{ margin:0; background:var(--bg); color:var(--text);
         font:16px/1.5 -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif; }}
  main {{ max-width:760px; margin:0 auto; padding:32px 16px 48px; }}
  h1 {{ font-size:28px; margin:0; }}
  .sub {{ color:var(--muted); margin:4px 0 28px; }}
  section {{ background:var(--panel); border:1px solid var(--line); border-radius:14px;
            padding:20px 22px; margin-bottom:16px; }}
  h2 {{ font-size:15px; text-transform:uppercase; letter-spacing:.06em; color:var(--accent); margin:0 0 12px; }}
  ul {{ margin:0; padding-left:20px; }} li {{ margin:4px 0; }}
  .cards {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; }}
  .card {{ border:1px solid var(--line); border-radius:10px; padding:12px 14px; }}
  .label {{ color:var(--muted); font-size:14px; }}
  .value {{ font-size:28px; font-weight:600; font-variant-numeric:tabular-nums; }}
  .delta {{ font-size:13px; }} .up {{ color:var(--up); }} .down {{ color:var(--down); }} .same {{ color:var(--muted); }}
  .empty {{ color:var(--muted); margin:0; }}
  footer {{ color:var(--muted); font-size:13px; margin-top:24px; }}
</style></head>
<body><main>
  <h1>Отчёт за {human_date(date)}</h1>
  <p class="sub">Сводка за вчерашний день и план на сегодня</p>
  <section><h2>Что сделано</h2>{items(day["done"], "Ничего не записано")}</section>
  <section><h2>Цифры</h2>{metrics_html(day["metrics"], prev, prev_date)}</section>
  <section><h2>На сегодня</h2>{items(day["today"], "Планов не записано")}</section>
  <footer>Собрано {made} из файла data/{date.isoformat()}.txt</footer>
</main></body></html>
"""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if args:
        date = datetime.date.fromisoformat(args[0])
    else:
        date = datetime.date.today() - datetime.timedelta(days=1)

    src = DATA / f"{date.isoformat()}.txt"
    if not src.exists():
        shutil.copy(TEMPLATE, src)
        print(f"За {date.strftime('%d.%m.%Y')} данных ещё не было — создал пустой файл {src.name}.")
        print("Открываю его: заполни, сохрани и запусти отчёт ещё раз.")
        subprocess.run(["open", "-e", str(src)])
        return

    day = parse(src)
    prev_src = previous_file(date)
    prev = parse(prev_src)["metrics"] if prev_src else {}
    prev_date = datetime.date.fromisoformat(prev_src.stem).strftime("%d.%m") if prev_src else ""

    REPORTS.mkdir(exist_ok=True)
    out = REPORTS / f"отчёт-{date.isoformat()}.html"
    page = render(date, day, prev, prev_date)
    out.write_text(page, encoding="utf-8")
    # Главная страница сайта — самый свежий отчёт.
    latest = max(p.name for p in REPORTS.glob("отчёт-*.html"))
    if out.name == latest:
        (REPORTS / "index.html").write_text(page, encoding="utf-8")
    print(f"Готово: {out}")
    if "--no-open" not in sys.argv:
        subprocess.run(["open", str(out)])


if __name__ == "__main__":
    main()
