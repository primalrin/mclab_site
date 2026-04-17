from flask import Flask, render_template

app = Flask(__name__)

DOWNLOAD_URLS = {
    "installer": "https://github.com/primalrin/mclab_site/raw/main/static/downloads/MicroLab.exe",
    "manual": "/static/downloads/%D0%9F%D0%9B%D0%9A%20MK100%20%D0%98%D0%BD%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%86%D0%B8%D1%8F%20MicroLab%20ver.%201.0.2.4%20%D0%BE%D1%82%D1%80%D0%B5%D0%B4%D0%B0%D0%BA%D1%82%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%B0.pdf",
}

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
        download_urls=DOWNLOAD_URLS,
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
