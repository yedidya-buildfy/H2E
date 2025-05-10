"""
קובץ ראשי להפעלת התוכנה
"""
import tkinter as tk
import sys
import traceback
from gui import KeyboardConverterApp

def main():
    """פונקציה ראשית להפעלת התוכנה"""
    try:
        root = tk.Tk()
        app = KeyboardConverterApp(root)
        root.mainloop()
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        traceback.print_exc()
        input("לחץ Enter לסגירה...")

if __name__ == "__main__":
    main()