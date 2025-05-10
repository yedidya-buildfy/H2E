"""
מודול תרגום טקסט
"""
import pyperclip
import keyboard
import time
import requests
from keyboard_utils import detect_language

def translate_text(text, direction="auto"):
    """
    מתרגם טקסט בין עברית לאנגלית ולהיפך
    
    :param text: הטקסט לתרגום
    :param direction: כיוון התרגום ("auto", "he_to_en", או "en_to_he")
    :return: הטקסט המתורגם
    """
    try:
        # זיהוי שפת המקור
        if direction == "auto":
            source_lang = detect_language(text)
            if source_lang == "he":
                target_lang = "en"
            else:
                target_lang = "he"
        elif direction == "he_to_en":
            source_lang = "he"
            target_lang = "en"
        else:  # en_to_he
            source_lang = "en"
            target_lang = "he"
        
        # באמצעות Google Translate API
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": source_lang,
            "tl": target_lang,
            "dt": "t",
            "q": text
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            # מחזיר תוצאת תרגום מהתשובה של גוגל
            result = ""
            for sentence in response.json()[0]:
                if sentence[0]:
                    result += sentence[0]
            return result
        else:
            return f"שגיאה בתרגום: {response.status_code}"
    
    except Exception as e:
        return f"שגיאה בתרגום: {str(e)}"

def hotkey_translation(direction="auto", callback=None):
    """
    פונקציה לביצוע תרגום עם קיצור מקשים
    
    :param direction: כיוון התרגום
    :param callback: פונקציה להפעלה לאחר התרגום (למשל לעדכון סטטוס)
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
            # תרגום הטקסט
            translated_text = translate_text(selected_text, direction)
            
            # העתקת הטקסט המתורגם ללוח
            pyperclip.copy(translated_text)
            
            # הדבקת הטקסט המתורגם במקום הטקסט המסומן
            keyboard.press_and_release('ctrl+v')
            
            # החזרת הטקסט המקורי ללוח
            time.sleep(0.1)
            pyperclip.copy(current_clipboard)
            
            # קריאה לפונקציית הקולבק אם הועברה
            if callback:
                callback(f"בוצע תרגום אחרון: {time.strftime('%H:%M:%S')}")
            
            return True
    except Exception as e:
        if callback:
            callback(f"שגיאה בתרגום: {str(e)}")
        return False