# Контакти: поля (ім'я, телефон, email, адреса, день народження),
# запис контакту (Record) та адресна книга (AddressBook).

import re
from collections import UserDict
from datetime import datetime
from difflib import get_close_matches


# ---------- Поля контакту ----------
# Усі поля успадковуються від Field (спадкування).
# Кожне поле саме перевіряє своє значення (валідація).

class Field:
    """Базовий клас для всіх полів."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Ім'я контакту — обов'язкове поле, може бути з кількох слів."""

    def __init__(self, value):
        # " Anna   Maria " -> "Anna Maria"
        value = " ".join(value.split())
        if not value:
            raise ValueError("Name is required.")
        super().__init__(value)


# Символи, які можна писати в номері, крім цифр: +38(097)183-68-28
PHONE_SYMBOLS = "+-()."


def normalize_phone(value):
    """
    Приводить номер до одного вигляду: 0XXXXXXXXX (10 цифр).
    Приймає: 0971234567, 380971234567, +380971234567,
    097-123-45-67, +38(097)123-45-67.
    """
    digits = ""
    for char in value:
        if char.isdigit():
            digits += char
        elif char not in PHONE_SYMBOLS:
            raise ValueError(
                f"Phone '{value}' has extra symbols. "
                "Example: 0501234567 or +380501234567"
            )

    # 380971234567 -> 0971234567
    if len(digits) == 12 and digits.startswith("380"):
        digits = digits[2:]

    if len(digits) != 10 or not digits.startswith("0"):
        raise ValueError(
            f"Invalid phone '{value}'. "
            "Example: 0501234567 or +380501234567"
        )
    return digits


def looks_like_phone(word):
    """Чи схоже слово на номер телефону (починається з цифри, + або ()."""
    return word[0].isdigit() or word[0] in "+("


class Phone(Field):
    """Номер телефону. Зберігаємо завжди як 0XXXXXXXXX."""

    def __init__(self, value):
        super().__init__(normalize_phone(value))


class Email(Field):
    """Email у форматі name@example.com."""

    def __init__(self, value):
        # До @ — будь-які символи без пробілів, після — домен з крапкою
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}", value):
            raise ValueError("Invalid email. Example: name@example.com")
        super().__init__(value)


class Address(Field):
    """Адреса — будь-який непорожній текст."""

    def __init__(self, value):
        if not value.strip():
            raise ValueError("Address cannot be empty.")
        super().__init__(value.strip())


class Birthday(Field):
    """День народження у форматі DD.MM.YYYY. Зберігаємо як дату."""

    def __init__(self, value):
        # Спершу перевіряємо формат, потім — чи існує така дата
        if not re.fullmatch(r"\d{2}\.\d{2}\.\d{4}", value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        try:
            date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError(f"Date {value} does not exist.")
        if date > datetime.today().date():
            raise ValueError("Birthday cannot be in the future.")
        super().__init__(date)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


# ---------- Запис контакту ----------
# Record складається з полів (композиція):
# Name, список Phone, Email, Address, Birthday.
# Обов'язкове тільки ім'я, усе інше можна додати пізніше.

class Record:
    """Один контакт."""

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.email = None
        self.address = None
        self.birthday = None

    # --- телефони ---
    def add_phone(self, phone):
        new_phone = Phone(phone)      # перевіряємо й приводимо до 0XXXXXXXXX
        if self.find_phone(new_phone.value):
            raise ValueError(f"Phone {new_phone} already exists.")
        self.phones.append(new_phone)

    def find_phone(self, phone):
        phone = normalize_phone(phone)
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def remove_phone(self, phone):
        p = self.find_phone(phone)
        if p is None:
            raise ValueError(f"Phone {phone} not found.")
        self.phones.remove(p)

    def edit_phone(self, old_phone, new_phone):
        p = self.find_phone(old_phone)
        if p is None:
            raise ValueError(f"Phone {old_phone} not found.")
        new_p = Phone(new_phone)      # спершу перевіряємо новий номер
        index = self.phones.index(p)
        self.phones[index] = new_p

    # --- інші поля (по одному на контакт) ---
    def set_email(self, email):
        self.email = Email(email)

    def set_address(self, address):
        self.address = Address(address)

    def set_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def remove_email(self):
        if self.email is None:
            raise ValueError(f"{self.name} has no email.")
        self.email = None

    def remove_address(self):
        if self.address is None:
            raise ValueError(f"{self.name} has no address.")
        self.address = None

    def remove_birthday(self):
        if self.birthday is None:
            raise ValueError(f"{self.name} has no birthday saved.")
        self.birthday = None

    def matches(self, query):
        """
        Чи містить контакт текст query (в імені, телефоні, email чи адресі).
        Великі й малі літери не важливі.
        """
        query = query.lower()
        if query in self.name.value.lower():
            return True
        for p in self.phones:
            # "38" + 0971234567 = 380971234567,
            # тому знайдеться і "0971...", і "+38097..."
            if query.lstrip("+") in "38" + p.value:
                return True
        if self.email and query in self.email.value.lower():
            return True
        if self.address and query in self.address.value.lower():
            return True
        return False

    def short_info(self):
        """Коротко про контакт: 'Anna (2 phones, email)'."""
        parts = []
        if self.phones:
            parts.append(f"{len(self.phones)} phone(s)")
        if self.email:
            parts.append("email")
        if self.address:
            parts.append("address")
        if self.birthday:
            parts.append("birthday")
        if not parts:
            return self.name.value
        return f"{self.name.value} ({', '.join(parts)})"

    def card(self):
        """Усі поля контакту, кожне з нового рядка."""
        phones = "; ".join(p.value for p in self.phones) or "-"
        return (
            f"Name:     {self.name}\n"
            f"Phones:   {phones}\n"
            f"Email:    {self.email or '-'}\n"
            f"Address:  {self.address or '-'}\n"
            f"Birthday: {self.birthday or '-'}"
        )

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones) or "-"
        email = self.email or "-"
        address = self.address or "-"
        birthday = self.birthday or "-"
        return (
            f"{self.name.value} | phones: {phones} | email: {email} | "
            f"address: {address} | birthday: {birthday}"
        )


# ---------- Адресна книга ----------

def get_birthday_in_year(birthday, year):
    """День народження в заданому році (29.02 у невисокосний рік -> 01.03)."""
    try:
        return birthday.replace(year=year)
    except ValueError:
        return birthday.replace(year=year, month=3, day=1)


class AddressBook(UserDict):
    """Адресна книга: ключ — ім'я, значення — Record."""

    def add_record(self, record):
        if self.find(record.name.value):
            raise ValueError(f"Contact {record.name} already exists.")
        self.data[record.name.value] = record

    def find(self, name):
        """Шукає контакт за іменем. 'dima' і 'Dima' — той самий контакт."""
        name = " ".join(name.split()).lower()
        for record in self.data.values():
            if record.name.value.lower() == name:
                return record
        return None

    def similar_name(self, name):
        """Найближче за написанням ім'я (для підказки) або None."""
        names = {record.name.value.lower(): record.name.value
                 for record in self.data.values()}
        matches = get_close_matches(name.lower(), list(names), n=1, cutoff=0.6)
        if matches:
            return names[matches[0]]
        return None

    def find_by_phone(self, phone):
        """Контакт, у якого є такий номер, або None."""
        for record in self.data.values():
            if record.find_phone(phone):
                return record
        return None

    def rename(self, record, new_name):
        new_name = Name(new_name)     # перевіряємо нове ім'я
        other = self.find(new_name.value)
        if other is not None and other is not record:
            raise ValueError(f"Contact {new_name} already exists.")
        del self.data[record.name.value]
        record.name = new_name
        self.data[record.name.value] = record

    def delete(self, name):
        record = self.find(name)
        if record is None:
            raise KeyError("Contact not found.")
        del self.data[record.name.value]

    def search(self, query):
        """Повертає список контактів, у яких є текст query."""
        return [rec for rec in self.data.values() if rec.matches(query)]

    def all_sorted(self):
        """Усі контакти за абеткою."""
        return sorted(self.data.values(),
                      key=lambda record: record.name.value.lower())

    def get_upcoming_birthdays(self, days):
        """
        Контакти, у яких день народження від сьогодні до +days днів.
        Повертає список пар (record, дата_дня_народження),
        відсортований за датою.
        """
        today = datetime.today().date()
        upcoming = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = record.birthday.value
            next_birthday = get_birthday_in_year(birthday, today.year)
            if next_birthday < today:
                next_birthday = get_birthday_in_year(birthday, today.year + 1)

            if (next_birthday - today).days <= days:
                upcoming.append((record, next_birthday))

        # Сортуємо за датою — найближчі першими
        upcoming.sort(key=lambda item: item[1])
        return upcoming
