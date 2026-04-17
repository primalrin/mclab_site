
(() => {
  'use strict'

  const forms = document.querySelectorAll('.needs-validation')

  Array.from(forms).forEach(form => {
    form.addEventListener('submit', async event => {
      if (!form.checkValidity()) {
        event.preventDefault()
        event.stopPropagation()
        form.classList.add('was-validated')
        return
      }

      form.classList.add('was-validated')

      if (!form.hasAttribute('data-contact-form')) {
        return
      }

      event.preventDefault()

      const feedback = document.getElementById('contact-feedback')
      const submitButton = form.querySelector('button[type="submit"]')
      const formData = new FormData(form)
      const payload = Object.fromEntries(formData.entries())

      setSubmitState(submitButton, true)
      setFeedback(feedback, '', '')

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(payload)
        })

        const result = await response.json().catch(() => ({}))
        if (!response.ok || !result.ok) {
          throw new Error(result.message || 'Не удалось отправить запрос. Попробуйте позже.')
        }

        form.reset()
        form.classList.remove('was-validated')
        setFeedback(
          feedback,
          'success',
          result.message || 'Сообщение отправлено. Мы свяжемся с вами в рабочее время.'
        )
      } catch (error) {
        setFeedback(
          feedback,
          'danger',
          error.message || 'Не удалось отправить запрос. Попробуйте позже.'
        )
      } finally {
        setSubmitState(submitButton, false)
      }
    }, false)
  })

  function setSubmitState(button, isLoading) {
    if (!button) {
      return
    }

    const idleLabel = button.dataset.idleLabel || button.textContent
    const loadingLabel = button.dataset.loadingLabel || 'Отправка...'

    if (!button.dataset.idleLabel) {
      button.dataset.idleLabel = idleLabel
    }

    button.disabled = isLoading
    button.textContent = isLoading ? loadingLabel : idleLabel
  }

  function setFeedback(target, tone, message) {
    if (!target) {
      return
    }

    if (!message) {
      target.innerHTML = ''
      return
    }

    target.innerHTML = `
      <div class="alert alert-${tone} mb-4" role="alert">
        ${escapeHtml(message)}
      </div>
    `
  }

  function escapeHtml(value) {
    return String(value)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;')
  }
})()
