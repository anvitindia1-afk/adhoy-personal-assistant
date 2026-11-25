# Функції-обробники команд.
# Кожна функція отримує аргументи й дані, а ПОВЕРТАЄ рядок-відповідь.
# Усі print та input — тільки в main.py.
#
# Перший рядок docstring кожної команди — це підказка, як її писати.
# Декоратор input_error показує її, якщо команду введено неправильно.

from contacts import Record, looks_like_phone
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
            usage = func.__doc__.strip().splitlines()[0]
            return f"Wrong command format. Usage: {usage}"
        except KeyError as e:
            # Повідомлення з KeyError("...") або стандартне
            return e.args[0] if e.args else "Not found."

    return inner


# ---------- Допоміжні функції для контактів ----------

def not_found(book, name):
    """KeyError з підказкою найближчого імені."""
    message = f"Contact '{name}' not found."
    similar = book.similar_name(name)
    if similar:
        message += f" Did you mean '{similar}'?"
    return KeyError(message)


def get_record(book, args):
    """
    Для команд, де після імені нічого немає: phone Anna Maria.
    Усі слова — це ім'я.
    """
    if not args:
        raise IndexError
    name = " ".join(args)
    record = book.find(name)
    if record is None:
        raise not_found(book, name)
    return record


def split_name(args, book, values):
    """
    Для команд, де після імені йдуть значення: add-email Anna Maria a@b.ua.
    Ім'я може бути з кількох слів, тому шукаємо на початку args
    найдовше ім'я, яке є в книзі.
    values — скільки слів щонайменше має бути після імені.
    Повертає (контакт, решта слів).
    """
    if len(args) < values + 1:
        raise IndexError
    for end in range(len(args) - values, 0, -1):
        record = book.find(" ".join(args[:end]))
        if record is not None:
            return record, args[end:]
    raise not_found(book, " ".join(args[:len(args) - values]))


def parse_note_id(text):
    """Перетворює номер нотатки з тексту на число."""
    if not text.isdigit():
        raise ValueError("Note ID must be a number. Type 'notes' to see IDs.")
    return int(text)


# ---------- Контакти ----------

@input_error
def add_contact(args, book):
    """add <name> [phone]
    Новий контакт (телефон необов'язковий) або ще один телефон.
    Якщо останнє слово схоже на телефон — це телефон, решта — ім'я.
    """
    if not args:
        raise IndexError

    phone = None
    if looks_like_phone(args[-1]):
        phone = args[-1]
        args = args[:-1]
        if not args:
            raise ValueError("Write a name before the phone: add Anna 0501234567")
    name = " ".join(args)

    record = book.find(name)
    if record is None:
        record = Record(name)
        if phone:
            record.add_phone(phone)   # спершу перевіряємо телефон
        message = phone_warning(book, phone)
        book.add_record(record)
        return "Contact added." + message

    if phone is None:
        raise ValueError(
            f"Contact {record.name} already exists. "
            "To add a phone: add <name> <phone>"
        )
    message = phone_warning(book, phone)
    record.add_phone(phone)
    return f"Phone added to {record.name}." + message


def phone_warning(book, phone):
    """Попередження, якщо такий номер уже є в іншого контакту."""
    if phone is None:
        return ""
    owner = book.find_by_phone(phone)
    if owner is None:
        return ""
    return f"\nNote: this number also belongs to {owner.name}."


@input_error
def change_phone(args, book):
    """change <name> <old phone> <new phone>"""
    record, values = split_name(args, book, 2)
    if len(values) != 2:
        raise IndexError
    old_phone, new_phone = values
    record.edit_phone(old_phone, new_phone)
    return "Phone updated."


@input_error
def remove_phone(args, book):
    """remove-phone <name> <phone>"""
    record, values = split_name(args, book, 1)
    if len(values) != 1:
        raise IndexError
    record.remove_phone(values[0])
    return "Phone removed."


@input_error
def show_phone(args, book):
    """phone <name>"""
    record = get_record(book, args)
    if not record.phones:
        return f"{record.name} has no phones."
    return "; ".join(p.value for p in record.phones)


@input_error
def show_contact(args, book):
    """show <name>"""
    return get_record(book, args).card()


@input_error
def rename_contact(args, book):
    """rename <old name> <new name>"""
    record, values = split_name(args, book, 1)
    old_name = record.name.value
    book.rename(record, " ".join(values))
    return f"Contact {old_name} renamed to {record.name}."


@input_error
def add_email(args, book):
    """add-email <name> <email>"""
    record, values = split_name(args, book, 1)
    if len(values) != 1:
        raise IndexError
    record.set_email(values[0])
    return "Email saved."


@input_error
def remove_email(args, book):
    """remove-email <name>"""
    get_record(book, args).remove_email()
    return "Email removed."


@input_error
def add_address(args, book):
    """add-address <name> <address>
    Адреса може бути з пробілами, тому беремо всі слова після імені.
    """
    record, values = split_name(args, book, 1)
    record.set_address(" ".join(values))
    return "Address saved."


@input_error
def remove_address(args, book):
    """remove-address <name>"""
    get_record(book, args).remove_address()
    return "Address removed."


@input_error
def add_birthday(args, book):
    """add-birthday <name> <DD.MM.YYYY>"""
    record, values = split_name(args, book, 1)
    if len(values) != 1:
        raise IndexError
    record.set_birthday(values[0])
    return "Birthday saved."


@input_error
def remove_birthday(args, book):
    """remove-birthday <name>"""
    get_record(book, args).remove_birthday()
    return "Birthday removed."


@input_error
def show_birthday(args, book):
    """show-birthday <name>"""
    record = get_record(book, args)
    if record.birthday is None:
        return f"{record.name} has no birthday saved."
    return f"{record.name}: {record.birthday}"


@input_error
def birthdays(args, book):
    """birthdays [days]
    Дні народження в найближчі N днів (типово 7).
    """
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
        lines.append(f"  {record.name}: {date.strftime('%d.%m.%Y')}")
    return "\n".join(lines)


@input_error
def search_contacts(args, book):
    """search <text>"""
    query = " ".join(args)
    if not query:
        raise IndexError
    found = book.search(query)
    if not found:
        return "Nothing found."
    return "\n".join(str(record) for record in found)


@input_error
def delete_contact(args, book):
    """delete <name>"""
    record = get_record(book, args)
    book.delete(record.name.value)
    return "Contact deleted."


@input_error
def show_all(args, book):
    """all"""
    if not book.data:
        return "No contacts saved."
    return "\n".join(str(record) for record in book.all_sorted())


# ---------- Контакти + нотатки ----------

@input_error
def contact_notes(args, book, notes):
    """contact-notes <name>
    Нотатки, де ім'я контакту є в тексті або в тегах (#dima).
    Для імені з кількох слів шукаємо за першим словом: Anna Maria -> anna.
    """
    record = get_record(book, args)
    first_name = record.name.value.split()[0].lower()
    found = notes.search(first_name)
    if not found:
        return (f"No notes about {record.name}. "
                f"Tip: add-note Call back #{first_name}")
    return format_notes(found)


# ---------- Нотатки ----------

def format_notes(notes_list):
    if not notes_list:
        return "No notes found."
    return "\n".join(str(note) for note in notes_list)


@input_error
def add_note(args, notes):
    """add-note <text> [#tag ...]"""
    if not args:
        raise IndexError
    text, tags = split_text_and_tags(args)
    note = notes.add_note(text, tags)
    return f"Note added with ID {note.id}."


@input_error
def show_notes(args, notes):
    """notes"""
    return format_notes(notes.all_notes())


@input_error
def find_note(args, notes):
    """find-note <text>"""
    query = " ".join(args)
    if not query:
        raise IndexError
    return format_notes(notes.search(query))


@input_error
def edit_note(args, notes):
    """edit-note <id> [new text] [#tag ...]
    Можна змінити лише текст, лише теги або і те, і те.
    """
    note_id = parse_note_id(args[0])
    text, tags = split_text_and_tags(args[1:])
    notes.edit_note(note_id, text, tags)
    return "Note updated."


@input_error
def delete_note(args, notes):
    """delete-note <id>"""
    notes.delete(parse_note_id(args[0]))
    return "Note deleted."


@input_error
def add_tag(args, notes):
    """add-tag <id> <tag> [tag ...]"""
    note = notes.find(parse_note_id(args[0]))
    tags = args[1:]
    if not tags:
        raise IndexError
    for tag in tags:
        note.add_tag(tag)
    return "Tags added."


@input_error
def remove_tag(args, notes):
    """remove-tag <id> <tag>"""
    note = notes.find(parse_note_id(args[0]))
    note.remove_tag(args[1])
    return "Tag removed."


@input_error
def find_tag(args, notes):
    """find-tag <tag>"""
    return format_notes(notes.search_by_tag(args[0]))


@input_error
def sort_notes(args, notes):
    """sort-notes"""
    return format_notes(notes.sorted_by_tags())
