# Функції-обробники команд.
# Кожна функція отримує аргументи й дані, а ПОВЕРТАЄ рядок-відповідь.
# Усі print та input — тільки в main.py.

from contacts import Record
from notes import split_text_and_tags


# ---------- Обробка помилок ----------

def input_error(func):
    """Декоратор: ловить помилки введення, щоб програма не падала."""
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Not enough arguments. Type 'help' to see the commands."
        except KeyError as e:
            # Повідомлення з KeyError("...") або стандартне
            return e.args[0] if e.args else "Not found."

    return inner


def get_record(book, name):
    """Знаходить контакт або викликає KeyError."""
    record = book.find(name)
    if record is None:
        raise KeyError("Contact not found.")
    return record


def parse_note_id(text):
    """Перетворює номер нотатки з тексту на число."""
    if not text.isdigit():
        raise ValueError("Note ID must be a number. Type 'notes' to see IDs.")
    return int(text)


# ---------- Контакти ----------

@input_error
def add_contact(args, book):
    """add [ім'я] [телефон] — новий контакт або ще один телефон."""
    name, phone = args[0], args[1]
    record = book.find(name)
    if record is None:
        record = Record(name)
        record.add_phone(phone)      # спершу перевіряємо телефон
        book.add_record(record)
        return "Contact added."
    record.add_phone(phone)
    return "Phone added to existing contact."


@input_error
def change_phone(args, book):
    """change [ім'я] [старий телефон] [новий телефон]."""
    name, old_phone, new_phone = args[0], args[1], args[2]
    get_record(book, name).edit_phone(old_phone, new_phone)
    return "Phone updated."


@input_error
def remove_phone(args, book):
    """remove-phone [ім'я] [телефон]."""
    name, phone = args[0], args[1]
    get_record(book, name).remove_phone(phone)
    return "Phone removed."


@input_error
def show_phone(args, book):
    """phone [ім'я]."""
    record = get_record(book, args[0])
    if not record.phones:
        return f"{record.name.value} has no phones."
    return "; ".join(p.value for p in record.phones)


@input_error
def add_email(args, book):
    """add-email [ім'я] [email] — додає або замінює email."""
    name, email = args[0], args[1]
    get_record(book, name).set_email(email)
    return "Email saved."


@input_error
def add_address(args, book):
    """add-address [ім'я] [адреса з пробілами] — додає або замінює адресу."""
    name = args[0]
    address = " ".join(args[1:])
    get_record(book, name).set_address(address)
    return "Address saved."


@input_error
def add_birthday(args, book):
    """add-birthday [ім'я] [DD.MM.YYYY] — додає або замінює день народження."""
    name, birthday = args[0], args[1]
    get_record(book, name).set_birthday(birthday)
    return "Birthday saved."


@input_error
def show_birthday(args, book):
    """show-birthday [ім'я]."""
    record = get_record(book, args[0])
    if record.birthday is None:
        return f"{record.name.value} has no birthday saved."
    return f"{record.name.value}: {record.birthday}"


@input_error
def birthdays(args, book):
    """birthdays [днів] — дні народження в найближчі N днів (типово 7)."""
    days = 7
    if args:
        if not args[0].isdigit():
            raise ValueError(
                "Days must be a positive number, e.g. 'birthdays 10'."
            )
        days = int(args[0])

    upcoming = book.get_upcoming_birthdays(days)
    if not upcoming:
        return f"No birthdays in the next {days} days."

    lines = [f"Birthdays in the next {days} days:"]
    for record, date in upcoming:
        lines.append(f"  {record.name.value}: {date.strftime('%d.%m.%Y')}")
    return "\n".join(lines)


@input_error
def search_contacts(args, book):
    """search [текст] — пошук за іменем, телефоном, email або адресою."""
    query = " ".join(args)
    if not query:
        raise IndexError
    found = book.search(query)
    if not found:
        return "Nothing found."
    return "\n".join(str(record) for record in found)


@input_error
def delete_contact(args, book):
    """delete [ім'я]."""
    book.delete(args[0])
    return "Contact deleted."


@input_error
def show_all(args, book):
    """all — усі контакти."""
    if not book.data:
        return "No contacts saved."
    return "\n".join(str(record) for record in book.data.values())


# ---------- Нотатки ----------

def format_notes(notes_list):
    if not notes_list:
        return "No notes found."
    return "\n".join(str(note) for note in notes_list)


@input_error
def add_note(args, notes):
    """add-note [текст] [#тег1 #тег2] — нова нотатка."""
    text, tags = split_text_and_tags(args)
    note = notes.add_note(text, tags)
    return f"Note added with ID {note.id}."


@input_error
def show_notes(args, notes):
    """notes — усі нотатки."""
    return format_notes(notes.all_notes())


@input_error
def find_note(args, notes):
    """find-note [текст] — пошук у тексті та тегах."""
    query = " ".join(args)
    if not query:
        raise IndexError
    return format_notes(notes.search(query))


@input_error
def edit_note(args, notes):
    """edit-note [id] [новий текст] [#нові теги]."""
    note_id = parse_note_id(args[0])
    text, tags = split_text_and_tags(args[1:])
    notes.edit_note(note_id, text, tags)
    return "Note updated."


@input_error
def delete_note(args, notes):
    """delete-note [id]."""
    notes.delete(parse_note_id(args[0]))
    return "Note deleted."


@input_error
def add_tag(args, notes):
    """add-tag [id] [тег1 тег2 ...]."""
    note = notes.find(parse_note_id(args[0]))
    tags = args[1:]
    if not tags:
        raise IndexError
    for tag in tags:
        note.add_tag(tag)
    return "Tags added."


@input_error
def remove_tag(args, notes):
    """remove-tag [id] [тег]."""
    note = notes.find(parse_note_id(args[0]))
    note.remove_tag(args[1])
    return "Tag removed."


@input_error
def find_tag(args, notes):
    """find-tag [тег] — нотатки з цим тегом."""
    return format_notes(notes.search_by_tag(args[0]))


@input_error
def sort_notes(args, notes):
    """sort-notes — нотатки, відсортовані за тегами."""
    return format_notes(notes.sorted_by_tags())
