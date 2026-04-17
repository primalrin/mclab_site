from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIR = ROOT / "public"
STATIC_DIR = ROOT / "static"
MAX_ASSET_SIZE_BYTES = 25 * 1024 * 1024

sys.path.insert(0, str(ROOT))

from app import app

ROUTES = {
    "/": "index.html",
    "/features": "features/index.html",
    "/use-cases": "use-cases/index.html",
    "/specs": "specs/index.html",
    "/downloads": "downloads/index.html",
    "/contact": "contact/index.html",
}

NOT_FOUND_HTML = """<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Страница не найдена</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <main class="section-shell">
        <div class="container">
            <div class="surface-card text-center p-5">
                <p class="section-kicker">Ошибка 404</p>
                <h1>Страница не найдена</h1>
                <p class="section-lead">Возможно, ссылка устарела или страница была перемещена.</p>
                <a class="btn btn-primary" href="/">Вернуться на главную</a>
            </div>
        </div>
    </main>
</body>
</html>
"""

HEADERS_FILE = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: SAMEORIGIN
  Permissions-Policy: camera=(), geolocation=(), microphone=()
"""


def reset_public_dir() -> None:
    if PUBLIC_DIR.exists():
        resolved_public = PUBLIC_DIR.resolve()
        if resolved_public.parent != ROOT.resolve():
            raise RuntimeError(f"Refusing to remove unexpected directory: {resolved_public}")
        shutil.rmtree(resolved_public)

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)


def export_pages() -> None:
    with app.test_client() as client:
        for route, relative_output in ROUTES.items():
            response = client.get(route)
            if response.status_code != 200:
                raise RuntimeError(f"Route {route} returned {response.status_code}")

            target = PUBLIC_DIR / relative_output
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(response.get_data(as_text=True), encoding="utf-8")


def copy_static_assets() -> None:
    target_static_dir = PUBLIC_DIR / "static"
    for source_path in STATIC_DIR.rglob("*"):
        if source_path.is_dir():
            continue

        relative_path = source_path.relative_to(STATIC_DIR)
        target_path = target_static_dir / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if source_path.stat().st_size > MAX_ASSET_SIZE_BYTES:
            print(f"Skipping oversized asset: {relative_path}")
            continue

        shutil.copy2(source_path, target_path)


def write_support_files() -> None:
    (PUBLIC_DIR / "404.html").write_text(NOT_FOUND_HTML, encoding="utf-8")
    (PUBLIC_DIR / "_headers").write_text(HEADERS_FILE, encoding="utf-8")


def main() -> None:
    reset_public_dir()
    export_pages()
    copy_static_assets()
    write_support_files()
    print(f"Exported static site to {PUBLIC_DIR}")


if __name__ == "__main__":
    main()
