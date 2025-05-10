"""
מודול ממשק משתמש גרפי
"""
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import converter
import translator
from keyboard_utils import detect_language
import threading
import time
import ctypes

try:
    from pynput import keyboard
    from pynput.keyboard import Key, KeyCode
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    import keyboard as keyboard_lib  # ספריית keyboard המקורית כגיבוי

class KeyboardConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ממיר מקלדת עברית-אנגלית")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # משתני המצב
        self.hotkey = "ctrl+q"  # קיצור מקשים להמרה
        self.translate_hotkey = "ctrl+w"  # קיצור מקשים לתרגום
        self.direction = "auto"
        self.is_listening = False
        self.auto_switch_language = True
        self.listener = None  # לpynput
        
        # בדיקה אם pynput זמין
        if not PYNPUT_AVAILABLE:
            messagebox.showwarning("אזהרה", "ספריית pynput לא נמצאה. נא להתקין אותה עם הפקודה: pip install pynput")
        
        # יצירת הממשק
        self.create_gui()
        
        # התקנת סוגר חלון
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_gui(self):
        # מסגרת ראשית
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # כותרת
        title_label = ttk.Label(main_frame, text="ממיר מקלדת עברית-אנגלית", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # מסגרת להגדרות קיצורי מקשים
        hotkey_frame = ttk.LabelFrame(main_frame, text="הגדרות קיצורי מקשים")
        hotkey_frame.pack(fill=tk.X, pady=10)
        
        hotkey_inner_frame = ttk.Frame(hotkey_frame)
        hotkey_inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # קיצור המרת מקלדת
        ttk.Label(hotkey_inner_frame, text="קיצור להמרת מקלדת:").grid(row=0, column=0, padx=5, sticky=tk.W)
        self.hotkey_entry = ttk.Entry(hotkey_inner_frame, width=15)
        self.hotkey_entry.grid(row=0, column=1, padx=5)
        self.hotkey_entry.insert(0, self.hotkey)
        
        # קיצור תרגום
        ttk.Label(hotkey_inner_frame, text="קיצור לתרגום:").grid(row=1, column=0, padx=5, sticky=tk.W)
        self.translate_hotkey_entry = ttk.Entry(hotkey_inner_frame, width=15)
        self.translate_hotkey_entry.grid(row=1, column=1, padx=5)
        self.translate_hotkey_entry.insert(0, self.translate_hotkey)
        
        self.save_hotkey_button = ttk.Button(hotkey_inner_frame, text="שמור קיצורים", command=self.save_hotkeys)
        self.save_hotkey_button.grid(row=0, column=2, rowspan=2, padx=5)
        
        self.toggle_button = ttk.Button(hotkey_inner_frame, text="הפעל האזנה לקיצורי מקשים", command=self.toggle_listener)
        self.toggle_button.grid(row=0, column=3, rowspan=2, padx=5)
        
        ttk.Label(hotkey_inner_frame, text="לדוגמה: ctrl+q, ctrl+w").grid(row=2, column=0, columnspan=4, pady=5, sticky=tk.W)
        
        # בחירת כיוון ההמרה
        direction_frame = ttk.LabelFrame(main_frame, text="כיוון המרה")
        direction_frame.pack(fill=tk.X, pady=10)
        
        direction_inner_frame = ttk.Frame(direction_frame)
        direction_inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.direction_var = tk.StringVar(value="auto")
        
        ttk.Radiobutton(direction_inner_frame, text="זיהוי אוטומטי", variable=self.direction_var, value="auto").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(direction_inner_frame, text="עברית → אנגלית", variable=self.direction_var, value="he_to_en").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(direction_inner_frame, text="אנגלית → עברית", variable=self.direction_var, value="en_to_he").pack(side=tk.LEFT, padx=10)
        
        save_direction_button = ttk.Button(direction_inner_frame, text="שמור כיוון המרה", command=self.save_direction)
        save_direction_button.pack(side=tk.LEFT, padx=10)
        
        # הגדרות החלפת שפת מקלדת
        keyboard_frame = ttk.LabelFrame(main_frame, text="החלפת שפת מקלדת אוטומטית")
        keyboard_frame.pack(fill=tk.X, pady=10)
        
        keyboard_inner_frame = ttk.Frame(keyboard_frame)
        keyboard_inner_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.auto_switch_var = tk.BooleanVar(value=True)
        auto_switch_checkbox = ttk.Checkbutton(
            keyboard_inner_frame,
            text="החלף שפת מקלדת באופן אוטומטי בעת המרה",
            variable=self.auto_switch_var,
            command=self.toggle_auto_switch
        )
        auto_switch_checkbox.pack(side=tk.LEFT, padx=10)
        
        # מסגרת לבדיקת המרה ותרגום
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # לשונית המרת מקלדת
        conversion_tab = ttk.Frame(notebook)
        notebook.add(conversion_tab, text="המרת מקלדת")
        
        # שדה קלט להמרה
        input_frame = ttk.Frame(conversion_tab)
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(input_frame, text="טקסט להמרה:").pack(anchor=tk.W)
        self.input_textbox = tk.Text(input_frame, wrap=tk.WORD, height=5)
        self.input_textbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # כפתורים להמרה
        button_frame = ttk.Frame(conversion_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        test_button = ttk.Button(button_frame, text="בדוק המרה", command=self.test_conversion)
        test_button.pack(side=tk.LEFT, padx=5)
        
        clear_button = ttk.Button(button_frame, text="נקה", command=self.clear_conversion_fields)
        clear_button.pack(side=tk.LEFT, padx=5)
        
        # שדה פלט להמרה
        output_frame = ttk.Frame(conversion_tab)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(output_frame, text="תוצאה:").pack(anchor=tk.W)
        self.output_textbox = tk.Text(output_frame, wrap=tk.WORD, height=5)
        self.output_textbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # כפתור העתקה להמרה
        copy_button = ttk.Button(conversion_tab, text="העתק תוצאה ללוח", command=self.copy_conversion_to_clipboard)
        copy_button.pack(pady=5, padx=10, anchor=tk.E)
        
        # לשונית תרגום
        translation_tab = ttk.Frame(notebook)
        notebook.add(translation_tab, text="תרגום")
        
        # שדה קלט לתרגום
        trans_input_frame = ttk.Frame(translation_tab)
        trans_input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(trans_input_frame, text="טקסט לתרגום:").pack(anchor=tk.W)
        self.trans_input_textbox = tk.Text(trans_input_frame, wrap=tk.WORD, height=5)
        self.trans_input_textbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # כפתורים לתרגום
        trans_button_frame = ttk.Frame(translation_tab)
        trans_button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # כפתורי כיוון תרגום
        self.trans_direction_var = tk.StringVar(value="auto")
        
        ttk.Radiobutton(trans_button_frame, text="זיהוי אוטומטי", variable=self.trans_direction_var, value="auto").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(trans_button_frame, text="עברית → אנגלית", variable=self.trans_direction_var, value="he_to_en").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(trans_button_frame, text="אנגלית → עברית", variable=self.trans_direction_var, value="en_to_he").pack(side=tk.LEFT, padx=5)
        
        translate_button = ttk.Button(trans_button_frame, text="תרגם", command=self.test_translation)
        translate_button.pack(side=tk.LEFT, padx=5)
        
        clear_trans_button = ttk.Button(trans_button_frame, text="נקה", command=self.clear_translation_fields)
        clear_trans_button.pack(side=tk.LEFT, padx=5)
        
        # שדה פלט לתרגום
        trans_output_frame = ttk.Frame(translation_tab)
        trans_output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        ttk.Label(trans_output_frame, text="תרגום:").pack(anchor=tk.W)
        self.trans_output_textbox = tk.Text(trans_output_frame, wrap=tk.WORD, height=5)
        self.trans_output_textbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # כפתור העתקה לתרגום
        copy_trans_button = ttk.Button(translation_tab, text="העתק תרגום ללוח", command=self.copy_translation_to_clipboard)
        copy_trans_button.pack(pady=5, padx=10, anchor=tk.E)
        
        # תווית הסבר
        instruction_text = """
הוראות שימוש:
1. הגדר קיצורי מקשים להמרה ולתרגום ולחץ על "שמור קיצורים"
2. בחר את כיוון ההמרה הרצוי ולחץ על "שמור כיוון המרה"
3. סמן את האפשרות "החלף שפת מקלדת באופן אוטומטי" אם ברצונך להחליף אוטומטית את שפת המקלדת בעת המרה
4. לחץ על "הפעל האזנה לקיצורי מקשים"
5. עבור לכל תוכנה, סמן טקסט:
   - הקש על קיצור מקשי ההמרה להחלפת אותיות מעברית לאנגלית ולהיפך
   - הקש על קיצור מקשי התרגום לתרגום הטקסט המסומן

* בלשוניות המתאימות ניתן לבדוק את ההמרה והתרגום לפני השימוש בקיצורי המקשים
* שים לב: יש להתקין את ספריית pynput: pip install pynput
        """
        
        instruction_label = ttk.Label(main_frame, text=instruction_text, justify=tk.LEFT, wraplength=550)
        instruction_label.pack(fill=tk.X, pady=10)
        
        # תווית סטטוס
        self.status_var = tk.StringVar()
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.pack(pady=5)
    
    # פונקציות הממשק
    def update_status(self, message):
        """עדכון הודעת סטטוס"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def perform_translation(self):
        """פונקציה לביצוע תרגום"""
        try:
            translator.hotkey_translation(
                self.trans_direction_var.get(),
                self.update_status
            )
        except Exception as e:
            self.update_status(f"שגיאה בתרגום: {str(e)}")
    
    def perform_conversion(self):
        """פונקציה לביצוע המרה"""
        try:
            converter.hotkey_conversion(
                self.direction, 
                self.auto_switch_language, 
                self.update_status
            )
        except Exception as e:
            self.update_status(f"שגיאה בהמרה: {str(e)}")
    
    def parse_hotkey(self, hotkey_str):
        """המרת מחרוזת קיצור מקשים למבנה של pynput"""
        parts = hotkey_str.lower().split('+')
        modifiers = []
        key = None
        
        for part in parts[:-1]:  # כל החלקים פרט לאחרון הם מקשי modifier
            if part == 'ctrl':
                modifiers.append(Key.ctrl)
            elif part == 'alt':
                modifiers.append(Key.alt)
            elif part == 'shift':
                modifiers.append(Key.shift)
            elif part == 'cmd' or part == 'win':
                modifiers.append(Key.cmd)
        
        # החלק האחרון הוא המקש עצמו
        last_part = parts[-1]
        if len(last_part) == 1:  # אם זה תו יחיד
            key = KeyCode.from_char(last_part)
        elif last_part.startswith('f') and last_part[1:].isdigit():  # מקשי F1-F12
            f_num = int(last_part[1:])
            if 1 <= f_num <= 12:
                key = getattr(Key, f'f{f_num}')
        else:
            # מקשים מיוחדים אחרים
            special_keys = {
                'space': Key.space,
                'esc': Key.esc,
                'tab': Key.tab,
                'enter': Key.enter,
                'backspace': Key.backspace
            }
            key = special_keys.get(last_part)
        
        return (modifiers, key)
    
    def on_pynput_press(self, key):
        """מטפל בלחיצות מקשים כשמשתמשים בpynput"""
        # בדיקה אם זה המקש של הקונטרול
        ctrl_pressed = Key.ctrl in self.current_keys
        
        # זיהוי מקש Q (לפי הקוד ASCII שלו)
        if hasattr(key, 'char') and key.char == 'q' and ctrl_pressed:
            # הפעלת המרה
            threading.Thread(target=self.perform_conversion).start()
            return True
        
        # זיהוי מקש W (לפי הקוד ASCII שלו)
        if hasattr(key, 'char') and key.char == 'w' and ctrl_pressed:
            # הפעלת תרגום
            threading.Thread(target=self.perform_translation).start()
            return True
        
        # הוספת המקש לרשימת המקשים הלחוצים
        if key not in self.current_keys:
            self.current_keys.add(key)
    
    def on_pynput_release(self, key):
        """מטפל בשחרור מקשים כשמשתמשים בpynput"""
        # הסרת המקש מרשימת המקשים הלחוצים
        if key in self.current_keys:
            self.current_keys.remove(key)
    
    def toggle_listener(self):
        """פונקציה להפעלה/כיבוי של האזנה לקיצורי המקשים"""
        if self.is_listening:
            # כיבוי האזנה
            self.is_listening = False
            
            if PYNPUT_AVAILABLE and self.listener:
                self.listener.stop()
                self.listener = None
            else:
                # שימוש בספריית keyboard כגיבוי
                keyboard_lib.unhook_all()
            
            self.toggle_button.config(text="הפעל האזנה לקיצורי מקשים")
            self.update_status("האזנה לקיצורי מקשים כבויה")
            self.hotkey_entry.config(state="normal")
            self.translate_hotkey_entry.config(state="normal")
            self.save_hotkey_button.config(state="normal")
        else:
            # קבלת קיצורי המקשים מהשדות
            new_hotkey = self.hotkey_entry.get().strip()
            new_translate_hotkey = self.translate_hotkey_entry.get().strip()
            
            if not new_hotkey or not new_translate_hotkey:
                messagebox.showerror("שגיאה", "נא להזין את כל קיצורי המקשים")
                return
            
            if new_hotkey == new_translate_hotkey:
                messagebox.showerror("שגיאה", "קיצורי המקשים חייבים להיות שונים זה מזה")
                return
            
            try:
                # שמירת קיצורי המקשים החדשים
                self.hotkey = new_hotkey
                self.translate_hotkey = new_translate_hotkey
                
                if PYNPUT_AVAILABLE:
                    # שימוש בpynput
                    self.current_keys = set()
                    
                    # מתחיל האזנה למקשים
                    self.listener = keyboard.Listener(
                        on_press=self.on_pynput_press,
                        on_release=self.on_pynput_release
                    )
                    self.listener.start()
                else:
                    # שימוש בספריית keyboard כגיבוי
                    keyboard_lib.add_hotkey(self.hotkey, self.perform_conversion)
                    keyboard_lib.add_hotkey(self.translate_hotkey, self.perform_translation)
                
                # עדכון המצב
                self.is_listening = True
                self.toggle_button.config(text="כבה האזנה לקיצורי מקשים")
                self.update_status(f"מאזין לקיצורים: המרה ({self.hotkey}), תרגום ({self.translate_hotkey})")
                self.hotkey_entry.config(state="disabled")
                self.translate_hotkey_entry.config(state="disabled")
                self.save_hotkey_button.config(state="disabled")
                
            except Exception as e:
                messagebox.showerror("שגיאה", f"קיצור מקשים לא תקין: {str(e)}")
    
    def save_hotkeys(self):
        """פונקציה לשמירת קיצורי המקשים"""
        new_hotkey = self.hotkey_entry.get().strip()
        new_translate_hotkey = self.translate_hotkey_entry.get().strip()
        
        if not new_hotkey or not new_translate_hotkey:
            messagebox.showerror("שגיאה", "נא להזין את כל קיצורי המקשים")
            return
        
        if new_hotkey == new_translate_hotkey:
            messagebox.showerror("שגיאה", "קיצורי המקשים חייבים להיות שונים זה מזה")
            return
        
        try:
            # שמירת קיצורי המקשים החדשים
            self.hotkey = new_hotkey
            self.translate_hotkey = new_translate_hotkey
            
            self.update_status(f"קיצורי מקשים נשמרו: המרה ({self.hotkey}), תרגום ({self.translate_hotkey})")
            
        except Exception as e:
            messagebox.showerror("שגיאה", f"קיצור מקשים לא תקין: {str(e)}")
    
    def save_direction(self):
        """פונקציה לשמירת כיוון ההמרה"""
        self.direction = self.direction_var.get()
        self.update_status(f"כיוון המרה נשמר: {self.get_direction_text()}")
    
    def toggle_auto_switch(self):
        """פונקציה להפעלה/כיבוי של שינוי שפת מקלדת אוטומטי"""
        self.auto_switch_language = self.auto_switch_var.get()
        if self.auto_switch_language:
            self.update_status("שינוי שפת מקלדת אוטומטי: מופעל")
        else:
            self.update_status("שינוי שפת מקלדת אוטומטי: כבוי")
    
    def get_direction_text(self):
        """פונקציה להחזרת טקסט של כיוון ההמרה"""
        if self.direction == "auto":
            return "זיהוי אוטומטי"
        elif self.direction == "he_to_en":
            return "עברית → אנגלית"
        else:
            return "אנגלית → עברית"
    
    def test_conversion(self):
        """פונקציה לבדיקת המרה ידנית"""
        input_text = self.input_textbox.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showinfo("הודעה", "נא להזין טקסט לבדיקה")
            return
        
        convert_dir = self.direction_var.get()
        result, _ = converter.convert_text(input_text, convert_dir)
        
        self.output_textbox.delete("1.0", tk.END)
        self.output_textbox.insert("1.0", result)
    
    def test_translation(self):
        """פונקציה לבדיקת תרגום ידנית"""
        input_text = self.trans_input_textbox.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showinfo("הודעה", "נא להזין טקסט לתרגום")
            return
        
        direction = self.trans_direction_var.get()
        result = translator.translate_text(input_text, direction)
        
        self.trans_output_textbox.delete("1.0", tk.END)
        self.trans_output_textbox.insert("1.0", result)
    
    def copy_conversion_to_clipboard(self):
        """פונקציה להעתקת תוצאת ההמרה ללוח"""
        output_text = self.output_textbox.get("1.0", tk.END).strip()
        if output_text:
            pyperclip.copy(output_text)
            self.update_status("תוצאת ההמרה הועתקה ללוח!")
        else:
            messagebox.showinfo("הודעה", "אין טקסט להעתקה")
    
    def copy_translation_to_clipboard(self):
        """פונקציה להעתקת תוצאת התרגום ללוח"""
        output_text = self.trans_output_textbox.get("1.0", tk.END).strip()
        if output_text:
            pyperclip.copy(output_text)
            self.update_status("התרגום הועתק ללוח!")
        else:
            messagebox.showinfo("הודעה", "אין טקסט להעתקה")
    
    def clear_conversion_fields(self):
        """פונקציה לניקוי שדות ההמרה"""
        self.input_textbox.delete("1.0", tk.END)
        self.output_textbox.delete("1.0", tk.END)
    
    def clear_translation_fields(self):
        """פונקציה לניקוי שדות התרגום"""
        self.trans_input_textbox.delete("1.0", tk.END)
        self.trans_output_textbox.delete("1.0", tk.END)
    
    def on_closing(self):
        """פונקציה לסגירת החלון"""
        if self.is_listening:
            if PYNPUT_AVAILABLE and self.listener:
                self.listener.stop()
            else:
                keyboard_lib.unhook_all()
        self.root.destroy()