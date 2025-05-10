"""
מודול עזר לעבודה עם המקלדת ושפות
"""
import ctypes
import time
import keyboard

# קבועים עבור שינוי שפת מקלדת
LANG_HEBREW = 0x040D  # Hebrew
LANG_ENGLISH = 0x0409  # English (US)

def get_current_keyboard_language():
    """מחזירה את קוד השפה של המקלדת הנוכחית"""
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    # מקבלת את ה-thread ID של החלון הפעיל
    thread_id = user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), 0)
    # מקבלת את ה-keyboard layout ID
    layout_id = user32.GetKeyboardLayout(thread_id)
    # מחזירה את ה-language identifier (נמצא ב-16 הביטים התחתונים)
    return layout_id & 0xFFFF

def switch_keyboard_language(to_language):
    """
    מחליפה את שפת המקלדת
    :param to_language: קוד השפה להחלפה אליה (LANG_HEBREW או LANG_ENGLISH)
    """
    current_lang = get_current_keyboard_language()
    
    # אם השפה כבר מוגדרת, אין צורך להחליף
    if current_lang == to_language:
        return
    
    # שימוש בקיצור המקשים להחלפת שפה
    keyboard.press_and_release('alt+shift')
    
    # המתנה קצרה לוודא שהשפה הוחלפה
    time.sleep(0.1)

def detect_language(text):
    """מזהה את שפת הטקסט (עברית או אנגלית)"""
    hebrew_chars = sum(1 for c in text if '\u0590' <= c <= '\u05FF')
    english_chars = sum(1 for c in text if 'a' <= c.lower() <= 'z')
    
    if hebrew_chars > english_chars:
        return "he"
    else:
        return "en"