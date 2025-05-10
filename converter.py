"""
מודול המרת מקלדת
"""
import pyperclip
import keyboard
import time
from keyboard_utils import switch_keyboard_language, LANG_HEBREW, LANG_ENGLISH

# מיפויי מקשים
# מיפוי מקשים מעברית לאנגלית
hebrew_to_english = {
    'א': 't', 'ב': 'c', 'ג': 'd', 'ד': 's', 'ה': 'v', 'ו': 'u',
    'ז': 'z', 'ח': 'j', 'ט': 'y', 'י': 'h', 'כ': 'f', 'ך': 'l', 'ל': 'k',
    'מ': 'n', 'ם': 'o', 'נ': 'b', 'ן': 'i', 'ס': 'x', 'ע': 'g', 'פ': 'p',
    'ף': ';', 'צ': 'm', 'ץ': '.', 'ק': 'e', 'ר': 'r', 'ש': 'a', 'ת': ',',
    ' ': ' ', '\n': '\n', '\t': '\t', ',': 'w', '.': '/', ';': 'q', '/': '/',
    "'": "'", '-': '-', '=': '='
}

# מיפוי מקשים מאנגלית לעברית
english_to_hebrew = {
    't': 'א', 'c': 'ב', 'd': 'ג', 's': 'ד', 'v': 'ה', 'u': 'ו',
    'z': 'ז', 'j': 'ח', 'y': 'ט', 'h': 'י', 'f': 'כ', 'l': 'ך', 'k': 'ל',
    'n': 'מ', 'o': 'ם', 'b': 'נ', 'i': 'ן', 'x': 'ס', 'g': 'ע', 'p': 'פ',
    ';': 'ף', 'm': 'צ', '.': 'ץ', 'e': 'ק', 'r': 'ר', 'a': 'ש', ',': 'ת',
    ' ': ' ', '\n': '\n', '\t': '\t', 'w': ',', '/': '.', 'q': ';', '/': '/',
    "'": "'", '-': '-', '=': '='
}

def convert_text(text, convert_direction="auto"):
    """
    ממירה טקסט בין עברית לאנגלית ולהיפך
    
    :param text: הטקסט להמרה
    :param convert_direction: כיוון ההמרה ("auto", "he_to_en", או "en_to_he")
    :return: הטקסט המומר וכיוון ההמרה שבוצע
    """
    if convert_direction == "auto":
        # זיהוי אוטומטי של השפה
        hebrew_chars = sum(1 for c in text if c in hebrew_to_english)
        english_chars = sum(1 for c in text if c in english_to_hebrew)
        
        if hebrew_chars > english_chars:
            convert_direction = "he_to_en"
        else:
            convert_direction = "en_to_he"
    
    result = ""
    if convert_direction == "he_to_en":
        # המרה מעברית לאנגלית
        for char in text:
            result += hebrew_to_english.get(char, char)
    else:
        # המרה מאנגלית לעברית
        for char in text:
            result += english_to_hebrew.get(char, char)
    return result, convert_direction

def hotkey_conversion(direction="auto", auto_switch_language=True, callback=None):
    """
    פונקציה לביצוע ההמרה עם קיצור מקשים
    
    :param direction: כיוון ההמרה
    :param auto_switch_language: האם להחליף את שפת המקלדת באופן אוטומטי
    :param callback: פונקציה להפעלה לאחר ההמרה (למשל לעדכון סטטוס)
    """
    try:
        # שמירת הטקסט הנוכחי בלוח
        current_clipboard = pyperclip.paste()
        
        # שליחת Ctrl+C כדי להעתיק את הטקסט המסומן
        keyboard.press_and_release('ctrl+c')
        # המתנה קצרה כדי לוודא שהטקסט הועתק
        time.sleep(0.1)
        
        # קבלת הטקסט המסומן
        selected_text = pyperclip.paste()
        
        if selected_text and selected_text != current_clipboard:
            # המרת הטקסט וקבלת כיוון ההמרה בפועל
            converted_text, actual_direction = convert_text(selected_text, direction)
            
            # אם הפעלנו החלפת שפה אוטומטית, החלפת שפת המקלדת לפי כיוון ההמרה
            if auto_switch_language:
                if actual_direction == "he_to_en":
                    # אם המרנו מעברית לאנגלית, נעבור לאנגלית
                    switch_keyboard_language(LANG_ENGLISH)
                else:
                    # אם המרנו מאנגלית לעברית, נעבור לעברית
                    switch_keyboard_language(LANG_HEBREW)
            
            # העתקת הטקסט המומר ללוח
            pyperclip.copy(converted_text)
            
            # הדבקת הטקסט המומר במקום הטקסט המסומן
            keyboard.press_and_release('ctrl+v')
            
            # החזרת הטקסט המקורי ללוח
            time.sleep(0.1)
            pyperclip.copy(current_clipboard)
            
            # קריאה לפונקציית הקולבק אם הועברה
            if callback:
                callback(f"בוצעה המרה אחרונה: {time.strftime('%H:%M:%S')}")
            
            return True
    except Exception as e:
        if callback:
            callback(f"שגיאה בהמרה: {str(e)}")
        return False