"""Build all five static language pages with the Python standard library."""
from html import escape
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
BASE = "https://solar-car.pechenko.org/"
LANGUAGES = ("en", "ru", "zh", "fr", "es")
LOCALES = {code: json.loads((ROOT / "web/locales" / f"{code}.json").read_text(encoding="utf-8")) for code in LANGUAGES}
TEMPLATE = (ROOT / "web/template.html").read_text(encoding="utf-8")


def route(code):
    return "" if code == "en" else code + "/"


def build():
    reference_keys = set(LOCALES["en"])
    alternate_links = '\n'.join(
        f'<link rel="alternate" hreflang="{LOCALES[code]["htmlLang"]}" href="{BASE}{route(code)}">'
        for code in LANGUAGES
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{BASE}">'
    for code, strings in LOCALES.items():
        if set(strings) != reference_keys:
            raise ValueError(f"Mismatched translation keys in {code}: {set(strings) ^ reference_keys}")
        if not all(isinstance(value, str) and value for value in strings.values()):
            raise ValueError(f"Empty or non-string translation in {code}")
        prefix = "" if code == "en" else "../"
        language_links = []
        for other in LANGUAGES:
            language = LOCALES[other]
            href = prefix + route(other) or "./"
            current = ' aria-current="page"' if other == code else ""
            language_links.append(
                f'<li><a href="{href}" data-language-choice="{other}" '
                f'lang="{language["htmlLang"]}" hreflang="{language["htmlLang"]}"{current}>'
                f'{escape(language["nativeName"])}</a></li>'
            )
        context = {key: escape(value, quote=True).replace('\n', '<br>') for key, value in strings.items()}
        context.update(
            code=code, homePath=prefix or "./", prefix=prefix,
            canonical=BASE + route(code), alternateLinks=alternate_links,
            languageLinks='\n'.join(language_links),
            guideFile="solar-car-assembly.pdf" if code == "ru" else "solar-car-assembly.en.pdf",
        )
        page = re.sub(r"\{\{(\w+)\}\}", lambda match: context[match.group(1)], TEMPLATE)
        destination = SITE / route(code) / "index.html"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(page, encoding="utf-8")
    urls = ''.join(f'<url><loc>{BASE}{route(code)}</loc></url>' for code in LANGUAGES)
    (SITE / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8"
    )
    print("Built English, Russian, Simplified Chinese, French and Spanish pages")


if __name__ == "__main__":
    build()
