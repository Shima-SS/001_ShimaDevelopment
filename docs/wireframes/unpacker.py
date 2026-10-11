#!/usr/bin/env python3
"""
Claude Design の「Bundled Page」HTML から、中身のデザイン部分だけを
取り出して、素の静的HTMLとして保存する。

バンドル版は React 本体などを base64 で抱えているため 100KB 超になるが、
実際の中身は <script type="__bundler/template"> の中に JSON 文字列として
1つだけ入っている。ここを取り出せば数十KBの普通のHTMLになる。

使い方:
    python3 extract-design-html.py 入力.html [出力.html]
    python3 extract-design-html.py *.html          （複数まとめて）

出力ファイル名を省略すると、元のファイル名に .clean.html を付けて保存する。
元のファイルは変更しない。
"""

import json
import re
import sys
from pathlib import Path

TEMPLATE_OPEN = re.compile(
    r'<script\s+type="__bundler/template"\s*>',
    re.IGNORECASE,
)

# テンプレート内で Design のランタイムを読み込んでいる行（uuid 参照）。
# ランタイムが無くても中身は静的HTMLとして読めるので、取り除く。
RUNTIME_SCRIPT = re.compile(
    r'<script\s+src="[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-'
    r'[0-9a-f]{4}-[0-9a-f]{12}"\s*>\s*</script\s*>',
    re.IGNORECASE,
)

# Design 独自のタグ（x-dc / helmet / sc-if）はランタイムが解釈するもの。
# display:contents で「無いもの」として扱い、中身だけを素通しさせる。
SHIM = (
    "<style>x-dc,helmet,sc-if,sc-for,sc-slot{display:contents}"
    "script[type='text/x-dc']{display:none}</style>"
)


def extract(html: str) -> str | None:
    m = TEMPLATE_OPEN.search(html)
    if not m:
        return None
    # タグ直後から JSON 文字列を1つだけ読む。中身に </script> が
    # 素で入っていても、終了タグ探しに頼らないので影響を受けない。
    start = m.end()
    while start < len(html) and html[start] in " \t\r\n":
        start += 1
    try:
        inner, _ = json.JSONDecoder().raw_decode(html, start)
    except json.JSONDecodeError:
        return None
    if not isinstance(inner, str):
        return None

    inner = RUNTIME_SCRIPT.sub("", inner)

    head = re.search(r"<head[^>]*>", inner, re.IGNORECASE)
    if head:
        i = head.end()
        inner = inner[:i] + SHIM + inner[i:]
    else:
        inner = SHIM + inner
    return inner


def size(n: int) -> str:
    return f"{n/1_000_000:.2f}MB" if n >= 1_000_000 else f"{n/1_000:.1f}KB"


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 1

    # 引数が2つで、2つめが .html かつ存在しない → 出力先の指定とみなす
    explicit_out = None
    if len(args) == 2 and not Path(args[1]).exists():
        explicit_out = Path(args[1])
        args = args[:1]

    failed = 0
    for name in args:
        src = Path(name)
        if not src.is_file():
            print(f"× {name}: ファイルが見つかりません")
            failed += 1
            continue

        html = src.read_text(encoding="utf-8", errors="replace")
        out = extract(html)
        if out is None:
            print(f"× {src.name}: バンドル形式ではないようです（そのままで使えます）")
            failed += 1
            continue

        dst = explicit_out or src.with_suffix(".clean.html")
        dst.write_text(out, encoding="utf-8")
        ratio = (1 - len(out) / len(html)) * 100 if html else 0
        print(f"○ {src.name}  {size(len(html))} → {dst.name}  {size(len(out))}  （{ratio:.1f}% 削減）")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
