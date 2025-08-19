import os
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
from dotenv import load_dotenv
load_dotenv() # Загружает переменные из .env файла

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-very-secret-key-for-dev')


# Словарь для передачи активного состояния страницы в навигацию
# Это позволяет подсвечивать текущий пункт меню
nav_items = {
    'home': 'Главная',
    'features': 'Возможности',
    'use_cases': 'Примеры применения',
    'specs': 'Спецификации',
    'downloads': 'Загрузки',
    'contact': 'Купить'
}

# --- Mail Configuration ---
# Рекомендуется использовать переменные окружения для чувствительных данных
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.your-mail-provider.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 't']
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') # Ваш email
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') # Пароль от вашего email
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

# Email, на который будут приходить заявки с формы
MAIL_RECIPIENT = os.environ.get('MAIL_RECIPIENT', 'sales@mclab.ru')

mail = Mail(app)
# --- End Mail Configuration ---

@app.route('/')
def home():
    return render_template('index.html', title='Точные измерения. Простая визуализация.', active_page='home', nav_items=nav_items)

@app.route('/features')
def features():
    return render_template('features.html', title='Возможности комплекса «Мк100-ML»', active_page='features', nav_items=nav_items)

@app.route('/use-cases')
def use_cases():
    return render_template('use_cases.html', title='Примеры применения «Мк100-ML»', active_page='use_cases', nav_items=nav_items)

@app.route('/specs')
def specs():
    return render_template('specs.html', title='Технические характеристики', active_page='specs', nav_items=nav_items)

@app.route('/downloads')
def downloads():
    return render_template('downloads.html', title='Загрузки', active_page='downloads', nav_items=nav_items)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        company = request.form.get('company')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        # Простая серверная валидация
        if not name or not email or not message:
            flash('Пожалуйста, заполните все обязательные поля.', 'danger')
            return render_template('contact.html', title='Купить / Контакты', active_page='contact', nav_items=nav_items, form_data=request.form)

        try:
            msg_title = f"Новый запрос с сайта от {name}"
            msg_body = f"""
Вы получили новое сообщение с контактной формы сайта mclab.ru.

Имя: {name}
Компания: {company if company else 'Не указана'}
Email: {email}
Телефон: {phone if phone else 'Не указан'}

Сообщение:
{message}
"""
            msg = Message(subject=msg_title,
                          recipients=[MAIL_RECIPIENT],
                          body=msg_body)
            mail.send(msg)
            flash('Ваше сообщение успешно отправлено! Мы скоро с вами свяжемся.', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            app.logger.error(f"Ошибка отправки email: {e}")
            flash('Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте позже или свяжитесь с нами напрямую.', 'danger')

    return render_template('contact.html', title='Купить / Контакты', active_page='contact', nav_items=nav_items)

if __name__ == '__main__':
    app.run(debug=True)