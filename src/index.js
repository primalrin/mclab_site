const JSON_HEADERS = {
  'content-type': 'application/json; charset=UTF-8',
  'cache-control': 'no-store'
}

const EMAIL_ENDPOINT = 'https://api.resend.com/emails'

export default {
  async fetch(request, env) {
    const url = new URL(request.url)

    if (url.pathname === '/api/contact' && request.method === 'POST') {
      return handleContactRequest(request, env)
    }

    if (url.pathname.startsWith('/api/')) {
      return jsonResponse(
        {
          ok: false,
          message: 'Маршрут API не найден.'
        },
        404
      )
    }

    return env.ASSETS.fetch(request)
  }
}

async function handleContactRequest(request, env) {
  if (!env.RESEND_API_KEY || !env.CONTACT_TO_EMAIL || !env.CONTACT_FROM_EMAIL) {
    console.error('Missing Worker email configuration')
    return jsonResponse(
      {
        ok: false,
        message: 'Форма временно недоступна. Свяжитесь с нами напрямую.'
      },
      500
    )
  }

  let payload

  try {
    payload = await readPayload(request)
  } catch {
    return jsonResponse(
      {
        ok: false,
        message: 'Не удалось прочитать данные формы.'
      },
      400
    )
  }

  const data = normalizePayload(payload)
  const validationError = validatePayload(data)

  if (validationError) {
    return jsonResponse(
      {
        ok: false,
        message: validationError
      },
      400
    )
  }

  if (data.website) {
    return jsonResponse(
      {
        ok: true,
        message: 'Сообщение отправлено. Мы свяжемся с вами в рабочее время.'
      },
      200
    )
  }

  const resendResponse = await fetch(EMAIL_ENDPOINT, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
      'Idempotency-Key': request.headers.get('Idempotency-Key') || crypto.randomUUID()
    },
    body: JSON.stringify({
      from: env.CONTACT_FROM_EMAIL,
      to: [env.CONTACT_TO_EMAIL],
      subject: `Новый запрос с сайта от ${data.name}`,
      html: buildHtmlEmail(data, request),
      text: buildTextEmail(data, request)
    })
  })

  if (!resendResponse.ok) {
    const resendError = await resendResponse.text()
    console.error('Resend API error:', resendError)
    return jsonResponse(
      {
        ok: false,
        message: 'Не удалось отправить запрос. Попробуйте позже или свяжитесь с нами напрямую.'
      },
      502
    )
  }

  return jsonResponse(
    {
      ok: true,
      message: 'Сообщение отправлено. Мы свяжемся с вами в рабочее время.'
    },
    200
  )
}

async function readPayload(request) {
  const contentType = request.headers.get('content-type') || ''

  if (contentType.includes('application/json')) {
    return request.json()
  }

  if (
    contentType.includes('application/x-www-form-urlencoded') ||
    contentType.includes('multipart/form-data')
  ) {
    const formData = await request.formData()
    return Object.fromEntries(
      Array.from(formData.entries()).map(([key, value]) => [key, typeof value === 'string' ? value : ''])
    )
  }

  throw new Error('Unsupported payload')
}

function normalizePayload(payload) {
  return {
    name: sanitizeText(payload.name, 120),
    company: sanitizeText(payload.company, 160),
    email: sanitizeText(payload.email, 160),
    phone: sanitizeText(payload.phone, 80),
    message: sanitizeText(payload.message, 5000),
    website: sanitizeText(payload.website, 120)
  }
}

function validatePayload(data) {
  if (!data.name) {
    return 'Укажите имя.'
  }

  if (!data.email) {
    return 'Укажите email.'
  }

  if (!EMAIL_PATTERN.test(data.email)) {
    return 'Введите корректный email.'
  }

  if (!data.message) {
    return 'Опишите задачу или запрос.'
  }

  return null
}

function buildHtmlEmail(data, request) {
  const metadata = buildMetadata(request)

  return `
    <h2>Новый запрос с сайта mclab_site</h2>
    <p><strong>Имя:</strong> ${escapeHtml(data.name)}</p>
    <p><strong>Компания:</strong> ${escapeHtml(data.company || 'Не указана')}</p>
    <p><strong>Email:</strong> ${escapeHtml(data.email)}</p>
    <p><strong>Телефон:</strong> ${escapeHtml(data.phone || 'Не указан')}</p>
    <p><strong>Сообщение:</strong></p>
    <p>${escapeHtml(data.message).replaceAll('\n', '<br>')}</p>
    <hr>
    <p><strong>Источник:</strong> ${escapeHtml(metadata.origin)}</p>
    <p><strong>IP:</strong> ${escapeHtml(metadata.ip)}</p>
    <p><strong>Локация:</strong> ${escapeHtml(metadata.location)}</p>
    <p><strong>Время UTC:</strong> ${escapeHtml(metadata.submittedAt)}</p>
  `.trim()
}

function buildTextEmail(data, request) {
  const metadata = buildMetadata(request)

  return [
    'Новый запрос с сайта mclab_site',
    '',
    `Имя: ${data.name}`,
    `Компания: ${data.company || 'Не указана'}`,
    `Email: ${data.email}`,
    `Телефон: ${data.phone || 'Не указан'}`,
    '',
    'Сообщение:',
    data.message,
    '',
    `Источник: ${metadata.origin}`,
    `IP: ${metadata.ip}`,
    `Локация: ${metadata.location}`,
    `Время UTC: ${metadata.submittedAt}`
  ].join('\n')
}

function buildMetadata(request) {
  return {
    origin: request.headers.get('origin') || request.headers.get('referer') || 'unknown',
    ip: request.headers.get('cf-connecting-ip') || 'unknown',
    location: formatLocation(request.cf),
    submittedAt: new Date().toISOString()
  }
}

function formatLocation(cf) {
  if (!cf) {
    return 'unknown'
  }

  return [cf.country, cf.city, cf.region].filter(Boolean).join(', ') || 'unknown'
}

function sanitizeText(value, maxLength) {
  return String(value || '')
    .replace(/\r\n/g, '\n')
    .replace(/\u0000/g, '')
    .trim()
    .slice(0, maxLength)
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

function jsonResponse(payload, status) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: JSON_HEADERS
  })
}

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
