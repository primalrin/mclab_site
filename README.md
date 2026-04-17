# mclab_site

Сайт переписан под схему Cloudflare Worker + Static Assets.

## Структура

- `public/` — готовый статический сайт для деплоя.
- `src/index.js` — Worker API для `/api/contact`.
- `templates/` и `app.py` — локальный источник страниц, из которого экспортируется `public/`.

## Обновление статического сайта

```bash
pip install -r requirements.txt
python scripts/export_static.py
```

## Переменные Worker

- `RESEND_API_KEY`
- `CONTACT_FROM_EMAIL`
- `CONTACT_TO_EMAIL`

Для локальной разработки можно скопировать `.dev.vars.example` в `.dev.vars`.

## Деплой в Cloudflare

- `Build command`: оставить пустым
- `Deploy command`: `npx wrangler deploy`

Cloudflare-конфиг хранится в `wrangler.jsonc`.
