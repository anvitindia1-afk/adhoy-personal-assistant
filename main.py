# Персональний помічник: точка запуску.
# Тут цикл "запит — відповідь": читаємо команду,
# викликаємо обробник і друкуємо відповідь.

from difflib import get_close_matches

import handlers
from storage import load_data, save_data

# Команди для контактів і для нотаток: назва команди -> функція-обробник
CONTACT_COMMANDS = {
    "add": handlers.add_contact,
    "change": handlers.change_phone,
    "remove-phone": handlers.remove_phone,
    "phone": handlers.show_phone,
    "show": handlers.show_contact,
    "rename": handlers.rename_contact,
    "add-email": handlers.add_email,
    "remove-email": handlers.remove_email,
    "add-address": handlers.add_address,
    "remove-address": handlers.remove_address,
    "add-birthday": handlers.add_birthday,
    "remove-birthday": handlers.remove_birthday,
    "show-birthday": handlers.show_birthday,
    "birthdays": handlers.birthdays,
    "search": handlers.search_contacts,
    "delete": handlers.delete_contact,
    "all": handlers.show_all,
}

NOTE_COMMANDS = {
    "add-note": handlers.add_note,
    "notes": handlers.show_notes,
    "find-note": handlers.find_note,
    "edit-note": handlers.edit_note,
    "delete-note": handlers.delete_note,
    "add-tag": handlers.add_tag,
    "remove-tag": handlers.remove_tag,
    "find-tag": handlers.find_tag,
    "sort-notes": handlers.sort_notes,
}

EXIT_COMMANDS = ["exit", "close"]
OTHER_COMMANDS = ["hello", "help", "contact-notes"]

ALL_COMMANDS = (
    list(CONTACT_COMMANDS) + list(NOTE_COMMANDS)
    + EXIT_COMMANDS + OTHER_COMMANDS
)

HELP_TEXT = """
Available commands  (<...> required, [...] optional — type WITHOUT brackets)

  CONTACTS
  add <name> [phone]                   add a contact (phone is optional)
                                       or one more phone to a contact
  change <name> <old> <new>            change a phone number
  remove-phone <name> <phone>          remove a phone number
  phone <name>                         show phone numbers
  show <name>                          show all info about a contact
  rename <old name> <new name>         rename a contact
  add-email <name> <email>             add or change email
  remove-email <name>                  remove email
  add-address <name> <address>         add or change address
  remove-address <name>                remove address
  add-birthday <name> <DD.MM.YYYY>     add or change birthday
  remove-birthday <name>               remove birthday
  show-birthday <name>                 show birthday
  birthdays [days]                     birthdays in the next N days (default 7)
  search <text>                        find contacts by any field
  delete <name>                        delete a contact (asks to confirm)
  all                                  show all contacts

  NOTES
  add-note <text> [#tag ...]           add a note (tags start with #)
  notes                                show all notes
  find-note <text>                     find notes by text or tag
  edit-note <id> [text] [#tag ...]     change text and/or tags of a note
  delete-note <id>                     delete a note (asks to confirm)
  add-tag <id> <tag> [tag ...]         add tags to a note
  remove-tag <id> <tag>                remove a tag from a note
  find-tag <tag>                       show notes with this tag
  sort-notes                           show notes sorted by tags
  contact-notes <name>                 notes about a contact (#name or name in text)

  OTHER
  hello                                greeting
  help                                 show this menu
  exit / close                         save and exit

  EXAMPLES
  add Anna Maria +380501234567         name can have several words
  add Anna 050-123-45-67               phone: 0501234567, 380..., +380..., with - ( )
  add-birthday Anna 28.11.1995
  add-note Buy a gift #anna #shop
  contact-notes Anna

Data is saved automatically after every change.
"""

# Команди, які змінюють дані — після них зберігаємо файли
READ_ONLY_COMMANDS = [
    "phone", "show", "show-birthday", "birthdays", "search", "all",
    "notes", "find-note", "find-tag", "sort-notes", "contact-notes",
]


def parse_input(user_input):
    """Розбиває введений рядок на команду та аргументи."""
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def suggest_command(command):
    """Шукає найближчу за написанням команду (наприклад, 'ad' -> 'add')."""
    matches = get_close_matches(command, ALL_COMMANDS, n=1, cutoff=0.6)
    if matches:
        return f"Unknown command '{command}'. Did you mean '{matches[0]}'?"
    return f"Unknown command '{command}'. Type 'help' to see all commands."


def has_brackets(args):
    """Чи ввів користувач дужки з довідки: add [Anna] <050...>."""
    for arg in args:
        if arg[0] in "[<" or arg[-1] in "]>":
            return True
    return False


def ask_yes_no(question):
    """Питає 'так чи ні'. Повертає True, якщо відповідь y / yes."""
    try:
        answer = input(f"{question} (y/n): ")
    except (KeyboardInterrupt, EOFError):
        print()
        return False
    return answer.strip().lower() in ["y", "yes"]


def delete_question(command, args, book, notes):
    """
    Текст питання перед видаленням або None,
    якщо такого контакту / нотатки немає (тоді обробник сам скаже помилку).
    """
    if command == "delete" and args:
        record = book.find(" ".join(args))
        if record is not None:
            return f"Delete contact {record.short_info()}?"
    if command == "delete-note" and args and args[0].isdigit():
        note = notes.notes.get(int(args[0]))
        if note is not None:
            return f"Delete note [{note.id}] {note.text}?"
    return None


def main():
    book, notes = load_data()
    print("Welcome to your Personal Assistant!")
    print(HELP_TEXT)

    while True:
        try:
            user_input = input("Enter a command: ")
        except (KeyboardInterrupt, EOFError):
            # Ctrl+C або Ctrl+D — теж зберігаємо й виходимо
            print("\nGood bye!")
            break

        if not user_input.strip():
            continue

        command, *args = parse_input(user_input)

        if command in EXIT_COMMANDS:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
            continue
        elif command == "help":
            print(HELP_TEXT)
            continue
        elif command not in ALL_COMMANDS:
            print(suggest_command(command))
            continue

        if command in CONTACT_COMMANDS and has_brackets(args):
            print("Type values without brackets, e.g.: add Anna 0501234567")
            continue

        # Перед видаленням перепитуємо
        question = delete_question(command, args, book, notes)
        if question and not ask_yes_no(question):
            print("Cancelled.")
            continue

        if command in CONTACT_COMMANDS:
            print(CONTACT_COMMANDS[command](args, book))
        elif command in NOTE_COMMANDS:
            print(NOTE_COMMANDS[command](args, notes))
        else:
            print(handlers.contact_notes(args, book, notes))

        # Автозбереження: дані не пропадуть, навіть якщо закрити вікно
        if command not in READ_ONLY_COMMANDS:
            save_data(book, notes)

    save_data(book, notes)


if __name__ == "__main__":
    main()
