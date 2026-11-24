# Personal Assistant — команда ADHOY

> **ADHOY** читається як «Ahoy!» — привітання моряків. Наш помічник теж починає з привітання.
> Команда: Anvit, Dmytro, Hryhorii, Oleksandr, Yurii.

Консольний персональний помічник на Python. Зберігає **контакти** (імена, телефони, email, адреси, дні народження) та **нотатки з тегами**. Усі дані зберігаються на диску й не губляться після перезапуску.

## Можливості

**Контакти**
- додавання контакту з кількома телефонами, email, адресою та днем народження;
- перевірка даних: телефон — рівно 10 цифр, email — формат `name@example.com`, дата — `DD.MM.YYYY`;
- пошук контактів за іменем, телефоном, email або адресою;
- редагування та видалення контактів і телефонів;
- список днів народження на найближчі N днів.

**Нотатки**
- додавання, пошук, редагування та видалення нотаток;
- теги (`#shop`, `#family`), пошук і сортування нотаток за тегами.

**Зручність**
- меню команд показується при запуску й за командою `help`;
- якщо команду введено з помилкою, помічник підказує найближчу (`ad` → `add`);
- неправильне введення не закриває програму, а показує зрозуміле повідомлення.

## Встановлення та запуск

Потрібен **Python 3.10** або новіший. Сторонні бібліотеки не потрібні.

```bash
git clone https://github.com/anvitindia1-afk/adhoy-personal-assistant.git
cd adhoy-personal-assistant
python3 main.py
```

На Windows замість `python3` використовуйте `python`.

## Команди

### Контакти

| Команда | Що робить |
|---|---|
| `add [name] [phone]` | додати контакт або ще один телефон до існуючого |
| `change [name] [old phone] [new phone]` | змінити телефон |
| `remove-phone [name] [phone]` | видалити телефон |
| `phone [name]` | показати телефони контакту |
| `add-email [name] [email]` | додати або змінити email |
| `add-address [name] [address]` | додати або змінити адресу (можна з пробілами) |
| `add-birthday [name] [DD.MM.YYYY]` | додати або змінити день народження |
| `show-birthday [name]` | показати день народження |
| `birthdays [days]` | дні народження в найближчі N днів (за замовчуванням 7) |
| `search [text]` | знайти контакти за будь-яким полем |
| `delete [name]` | видалити контакт |
| `all` | показати всі контакти |

### Нотатки

| Команда | Що робить |
|---|---|
| `add-note [text] [#tag ...]` | додати нотатку; слова з `#` стають тегами |
| `notes` | показати всі нотатки |
| `find-note [text]` | знайти нотатки за текстом або тегом |
| `edit-note [id] [text] [#tag ...]` | змінити текст (і теги, якщо вказані) |
| `delete-note [id]` | видалити нотатку |
| `add-tag [id] [tag ...]` | додати теги до нотатки |
| `remove-tag [id] [tag]` | видалити тег з нотатки |
| `find-tag [tag]` | показати нотатки з цим тегом |
| `sort-notes` | показати нотатки, відсортовані за тегами |

### Інше

| Команда | Що робить |
|---|---|
| `hello` | привітання |
| `help` | показати меню команд |
| `exit` / `close` | зберегти дані й вийти |

## Приклад

```
Enter a command: add Anna 0501234567
Contact added.
Enter a command: add-email Anna anna@gmail.com
Email saved.
Enter a command: add-birthday Anna 28.11.1995
Birthday saved.
Enter a command: birthdays 10
Birthdays in the next 10 days:
  Anna: 28.11.2026
Enter a command: add-note Buy a gift for Anna #shop #birthday
Note added with ID 1.
Enter a command: find-tag birthday
[1] Buy a gift for Anna | tags: #shop #birthday
Enter a command: exit
Good bye!
```

## Де зберігаються дані

У домашній папці користувача, у прихованій папці `.personal_assistant`:
- `contacts.pkl` — контакти;
- `notes.pkl` — нотатки.

Наприклад: `/Users/anna/.personal_assistant/` (macOS) або `C:\Users\anna\.personal_assistant\` (Windows).

## Структура проєкту

| Файл | Що всередині |
|---|---|
| `main.py` | запуск, меню та цикл команд |
| `contacts.py` | класи `Field`, `Name`, `Phone`, `Email`, `Address`, `Birthday`, `Record`, `AddressBook` |
| `notes.py` | класи `Note`, `NoteBook` |
| `handlers.py` | функції команд і декоратор `input_error` для обробки помилок |
| `storage.py` | збереження та завантаження даних (`pickle`) |
| `docs/trello-tasks.md` | план роботи команди: ролі, спринти, задачі для Trello |
| `docs/presentation-draft.pdf` | чернетка презентації (перегляд); `.pptx` — для редагування |

Усі поля контакту успадковуються від `Field` (**спадкування**) і самі перевіряють свої значення. `Record` складається з цих полів, а `AddressBook` і `NoteBook` зберігають записи (**композиція**).
