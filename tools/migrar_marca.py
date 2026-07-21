#!/usr/bin/env python3
"""
Adapta um export autorizado de documentação para a marca Cobzap.

Uso:
    python tools/migrar_marca.py /caminho/do/export --apply

Sem --apply, apenas apresenta a prévia das alterações.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
from typing import Iterable

TEXT_EXTENSIONS = {
    ".md", ".mdx", ".markdown", ".html", ".htm", ".txt",
    ".yaml", ".yml", ".json", ".xml", ".css", ".js", ".jsx",
    ".ts", ".tsx", ".toml", ".ini", ".csv"
}

DEFAULT_REPLACEMENTS = [
    ("Central de Ajuda ZPRO", "Central de Ajuda Cobzap"),
    ("Central de Ajuda Z-PRO", "Central de Ajuda Cobzap"),
    ("API ZPRO", "API Cobzap"),
    ("API Z-PRO", "API Cobzap"),
    ("Z-PRO", "Cobzap"),
    ("ZPRO", "Cobzap"),
    ("Z Pro", "Cobzap"),
    ("z-pro", "cobzap"),
    ("zpro", "cobzap"),
    ("ajuda.zdg.com.br", "ajuda.cobzap.com.br"),
    ("suporte.zdg.com.br", "suporte.cobzap.com.br"),
    ("zpro.zdg.com.br", "cobzap.com.br"),
]

def iter_text_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_EXTENSIONS:
            yield path

def replace_content(text: str, replacements: list[tuple[str, str]]) -> tuple[str, int]:
    total = 0
    for old, new in replacements:
        count = text.count(old)
        if count:
            text = text.replace(old, new)
            total += count
    return text, total

def rename_path_component(name: str) -> str:
    result = name
    for old, new in [
        ("Z-PRO", "Cobzap"), ("ZPRO", "Cobzap"), ("Z Pro", "Cobzap"),
        ("z-pro", "cobzap"), ("zpro", "cobzap")
    ]:
        result = result.replace(old, new)
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="Pasta do export autorizado")
    parser.add_argument("--apply", action="store_true", help="Gravar alterações")
    parser.add_argument("--config", type=Path, help="JSON adicional de substituições")
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Pasta inválida: {root}")

    replacements = list(DEFAULT_REPLACEMENTS)
    if args.config:
        custom = json.loads(args.config.read_text(encoding="utf-8"))
        replacements = [(str(k), str(v)) for k, v in custom.items()] + replacements

    changed_files = 0
    replacements_count = 0

    for path in iter_text_files(root):
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"[IGNORADO] Codificação não UTF-8: {path}")
            continue

        updated, count = replace_content(original, replacements)
        if count:
            changed_files += 1
            replacements_count += count
            print(f"[CONTEÚDO] {path.relative_to(root)}: {count} substituições")
            if args.apply:
                path.write_text(updated, encoding="utf-8")

    # Rename bottom-up to avoid invalidating child paths.
    paths = sorted(root.rglob("*"), key=lambda p: len(p.parts), reverse=True)
    renamed = 0
    for path in paths:
        new_name = rename_path_component(path.name)
        if new_name == path.name:
            continue
        destination = path.with_name(new_name)
        print(f"[RENOMEAR] {path.relative_to(root)} -> {destination.relative_to(root)}")
        renamed += 1
        if args.apply:
            if destination.exists():
                raise SystemExit(f"Destino já existe: {destination}")
            path.rename(destination)

    # Audit remaining brand references after planned/applied substitutions.
    patterns = re.compile(r"z[\s-]?pro|zdg", re.IGNORECASE)
    pending = []
    for path in iter_text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            if patterns.search(line):
                pending.append((str(path.relative_to(root)), line_no, line.strip()[:180]))

    print()
    print(f"Arquivos com conteúdo alterado: {changed_files}")
    print(f"Substituições encontradas: {replacements_count}")
    print(f"Arquivos/pastas para renomear: {renamed}")
    print(f"Referências pendentes: {len(pending)}")

    report = root / "RELATORIO_REVISAO_MARCA.txt"
    report_text = "\n".join(f"{p}:{n}: {line}" for p, n, line in pending)
    if args.apply:
        report.write_text(
            "Referências que ainda precisam de revisão manual:\n\n" + report_text + "\n",
            encoding="utf-8",
        )
        print(f"Relatório gravado em: {report}")

    if not args.apply:
        print("\nPrévia concluída. Execute novamente com --apply para gravar.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
