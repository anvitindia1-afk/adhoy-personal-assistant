# Контакти: поля (ім'я, телефон, email, адреса, день народження),
# запис контакту (Record) та адресна книга (AddressBook).

import re
from collections import UserDict
from datetime import datetime


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
    """Ім'я контакту — обов'язкове поле."""

    def __init__(self, value):
        if not value:
            raise ValueError("Name is required.")
        super().__init__(value)


class Phone(Field):
    """Номер телефону — рівно 10 цифр."""

    def __init__(self, value):
        if not (value.isdigit() and len(value) == 10):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(value)


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
        try:
            date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        if date > datetime.today().date():
            raise ValueError("Birthday cannot be in the future.")
        super().__init__(date)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


# ---------- Запис контакту ----------
# Record складається з полів (композиція):
# Name, список Phone, Email, Address, Birthday.

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
        if self.find_phone(phone):
            raise ValueError(f"Phone {phone} already exists.")
        self.phones.append(Phone(phone))

    def find_phone(self, phone):
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
        new_p = Phone(new_phone)   # спершу перевіряємо новий номер
        index = self.phones.index(p)
        self.phones[index] = new_p

    # --- інші поля (по одному на контакт) ---
    def set_email(self, email):
        self.email = Email(email)

    def set_address(self, address):
        self.address = Address(address)

    def set_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def matches(self, query):
        """
        Чи містить контакт текст query (в імені, телефоні, email чи адресі).
        Великі й малі літери не важливі.
        """
        query = query.lower()
        if query in self.name.value.lower():
            return True
        for p in self.phones:
            if query in p.value:
                return True
        if self.email and query in self.email.value.lower():
            return True
        if self.address and query in self.address.value.lower():
            return True
        return False

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
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name not in self.data:
            raise KeyError("Contact not found.")
        del self.data[name]

    def search(self, query):
        """Повертає список контактів, у яких є текст query."""
        return [rec for rec in self.data.values() if rec.matches(query)]

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
