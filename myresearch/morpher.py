from typing import Optional

from myresearch.core import morpher

res = morpher.parse('asf')

SIGNS_TO_REMOVE = {",", ".", "?", "!", "/", "\\"}


def cut_side_punctuation(string: str) -> str:
    symbols = list(string.strip())
    for sym in symbols.copy():
        if sym in SIGNS_TO_REMOVE:
            symbols.remove(sym)
        else:
            break
    symbols.reverse()

    for sym in symbols.copy():
        if sym in SIGNS_TO_REMOVE:
            symbols.remove(sym)
        else:
            break
    symbols.reverse()

    return ''.join(symbols)


def to_normal_form(word: str) -> Optional[str]:
    word = word.strip()
    normalized_word: str = morpher.parse(word)[0].normal_form
    return normalized_word


def is_adj(word: str) -> bool:
    word = word.strip()
    normalized_word: str = morpher.parse(word)[0]
    if "ADJF" in normalized_word.tag:
        return True
    return False

