# Збереження та завантаження даних (pickle).
# Файли лежать у домашній папці користувача: ~/.personal_assistant/

import pickle
from pathlib import Path

from contacts import AddressBook
from notes import NoteBook

# Path.home() — домашня папка користувача
# (наприклад /Users/anna або C:\Users\anna)
DATA_DIR = Path.home() / ".personal_assistant"
CONTACTS_FILE = DATA_DIR / "contacts.pkl"
NOTES_FILE = DATA_DIR / "notes.pkl"


def save_object(obj, path):
    """Зберігає будь-який об'єкт у файл."""
    # Створюємо папку, якщо її ще немає
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        pickle.dump(obj, f)


def load_object(path, default):
    """
    Завантажує об'єкт з файлу.
    Якщо файлу немає або він пошкоджений — повертає default.
    """
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return default
    except Exception:
        print(f"Warning: saved data in {path} is damaged. Starting fresh.")
        return default


def load_data():
    """Повертає (адресна книга, записник нотаток)."""
    book = load_object(CONTACTS_FILE, AddressBook())
    notes = load_object(NOTES_FILE, NoteBook())
    return book, notes


def save_data(book, notes):
    save_object(book, CONTACTS_FILE)
    save_object(notes, NOTES_FILE)
