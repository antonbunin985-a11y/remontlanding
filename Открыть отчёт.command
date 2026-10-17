#!/bin/zsh
# Двойной щелчок в Finder — собирает и открывает отчёт за вчера.
cd "$(dirname "$0")"
/usr/bin/python3 report.py
