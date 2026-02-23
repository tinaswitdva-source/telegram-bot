# text_processing.py (Код9)

import re

# --- службові слова ---
FUNCTION_WORDS = {"на", "с", "в", "и"}  # вага 0.8

# --- ключові слова (смислові) ---
KEYWORDS = {
    "пришел", "гастролирует", "одесской", "булгакова", "молодая",
    "публика", "серая", "одевается", "моды", "тоже", "странно",
    "красивых", "женщин", "трясет"
}  # вага 1.3

# --- допустимі варіанти ---
ALLOWED_Y_VARIANTS = {
    "известный": {"известный", "известний"},
    "способный": {"способный", "способний"},
    "моды": {"моды", "моди"},
    "красивых": {"красивых", "красивих"},
    "мы": {"мы", "ми"},
    "одессы": {"одессы", "одесси"},
    "это": {"это", "ето"},
}

# --- нормалізація слова ---
def normalize_word(word: str) -> str:
    word = word.lower().strip(".,!?\"'()")
    word = word.replace("ьі", "ы")
    for base_word, variants in ALLOWED_Y_VARIANTS.items():
        if word in variants:
            return base_word
    return word

# --- вага слова ---
def word_weight(word: str) -> float:
    norm = normalize_word(word)
    if norm in FUNCTION_WORDS:
        return 0.8
    elif norm in KEYWORDS:
        return 1.3
    else:
        return 1.0

# --- підрахунок відсотка ---
def text_match_percentage(user_text: str, template_text: str) -> float:
    user_words = re.findall(r'\b\w+\b', user_text.lower())
    template_words = re.findall(r'\b\w+\b', template_text.lower())

    user_words_norm = [normalize_word(w) for w in user_words]
    template_words_norm = [normalize_word(w) for w in template_words]

    matches = 0.0
    total = sum(word_weight(w) for w in template_words_norm)

    template_idx = 0
    for uw in user_words_norm:
        if template_idx >= len(template_words_norm):
            break

        tw = template_words_norm[template_idx]
        weight = word_weight(tw)

        if uw == tw:
            matches += weight
            template_idx += 1
        elif uw in template_words_norm[template_idx + 1:]:
            while template_idx < len(template_words_norm) and template_words_norm[template_idx] != uw:
                template_idx += 1
            if template_idx < len(template_words_norm):
                matches += weight
                template_idx += 1

    if total == 0:
        return 0.0

    return round((matches / total) * 100, 2)

# --- рівень ---
def get_level_from_percentage(percent: float) -> str:
    if 0 <= percent <= 25:
        return "<b>Поверхневий – 0–25%</b>: упізнано окремі слова й фрагменти, загальний зміст не складено"
    elif 26 <= percent <= 50:
        return "<b>Читаючий – 26–50%</b>: текст читається частково, сенс уловлений фрагментарно"
    elif 50 < percent <= 75:
        return "<b>Вдумливий – 51–75%</b>: більшість тексту зрозуміла, зв’язки між частинами простежуються"
    elif 75 < percent <= 85:
        return "<b>Проникливий – 76–85%</b>: текст майже повністю розгаданий, дрібні прогалини не заважають розумінню"
    elif 85 < percent <= 100:
        return "<b>Безпомилковий – 86–100%</b>: текст відтворений точно, без смислових втрат"
    else:
        return "0 рівень"
