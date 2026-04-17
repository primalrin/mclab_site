from flask import Flask, render_template

app = Flask(__name__)

NAV_ITEMS = {
    "home": "Главная",
    "features": "Возможности",
    "use_cases": "Примеры применения",
    "specs": "Спецификации",
    "downloads": "Загрузки",
    "contact": "Контакты",
}

PAGE_TITLES = {
    "home": "Измерительный комплекс для точных измерений",
    "features": "Возможности комплекса «Мк100-ML»",
    "use_cases": "Сценарии применения «Мк100-ML»",
    "specs": "Технические характеристики",
    "downloads": "Загрузки и документация",
    "contact": "Запрос предложения и контакты",
}


def render_page(template_name: str, active_page: str):
    return render_template(
        template_name,
        title=PAGE_TITLES[active_page],
        active_page=active_page,
        nav_items=NAV_ITEMS,
    )


@app.route("/")
def home():
    return render_page("index.html", "home")


@app.route("/features")
def features():
    return render_page("features.html", "features")


@app.route("/use-cases")
def use_cases():
    return render_page("use_cases.html", "use_cases")


@app.route("/specs")
def specs():
    return render_page("specs.html", "specs")


@app.route("/downloads")
def downloads():
    return render_page("downloads.html", "downloads")


@app.route("/contact")
def contact():
    return render_page("contact.html", "contact")

if __name__ == '__main__':
    app.run(debug=True)
