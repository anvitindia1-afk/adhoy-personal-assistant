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
    "add-email": handlers.add_email,
    "add-address": handlers.add_address,
    "add-birthday": handlers.add_birthday,
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
OTHER_COMMANDS = ["hello", "help"]

ALL_COMMANDS = (
    list(CONTACT_COMMANDS) + list(NOTE_COMMANDS)
    + EXIT_COMMANDS + OTHER_COMMANDS
)

HELP_TEXT = """
Available commands:

  CONTACTS
  add [name] [phone]                 add a contact or one more phone
  change [name] [old] [new]          change a phone number
  remove-phone [name] [phone]        remove a phone number
  phone [name]                       show phone numbers
  add-email [name] [email]           add or change email
  add-address [name] [address]       add or change address
  add-birthday [name] [DD.MM.YYYY]   add or change birthday
  show-birthday [name]               show birthday
  birthdays [days]                   birthdays in the next N days (default 7)
  search [text]                      find contacts by any field
  delete [name]                      delete a contact
  all                                show all contacts

  NOTES
  add-note [text] [#tag ...]         add a note (tags start with #)
  notes                              show all notes
  find-note [text]                   find notes by text or tag
  edit-note [id] [text] [#tag ...]   change a note
  delete-note [id]                   delete a note
  add-tag [id] [tag ...]             add tags to a note
  remove-tag [id] [tag]              remove a tag from a note
  find-tag [tag]                     show notes with this tag
  sort-notes                         show notes sorted by tags

  OTHER
  hello                              greeting
  help                               show this menu
  exit / close                       save and exit
"""


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
        elif command == "help":
            print(HELP_TEXT)
        elif command in CONTACT_COMMANDS:
            print(CONTACT_COMMANDS[command](args, book))
        elif command in NOTE_COMMANDS:
            print(NOTE_COMMANDS[command](args, notes))
        else:
            print(suggest_command(command))

    save_data(book, notes)


if __name__ == "__main__":
    main()
