# Нотатки: одна нотатка (Note) і записник нотаток (NoteBook).
# Кожна нотатка має номер (id), текст і теги.


class Note:
    """Одна нотатка: текст і список тегів."""

    def __init__(self, note_id, text, tags=None):
        if not text.strip():
            raise ValueError("Note text cannot be empty.")
        self.id = note_id
        self.text = text.strip()
        self.tags = []
        for tag in tags or []:
            self.add_tag(tag)

    def add_tag(self, tag):
        """Додає тег (без '#' і маленькими літерами), якщо його ще немає."""
        tag = tag.lstrip("#").lower()
        if not tag:
            raise ValueError("Tag cannot be empty.")
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        tag = tag.lstrip("#").lower()
        if tag not in self.tags:
            raise ValueError(f"Tag '{tag}' not found in this note.")
        self.tags.remove(tag)

    def matches(self, query):
        """Чи є текст query у тексті нотатки або в її тегах."""
        query = query.lower()
        if query in self.text.lower():
            return True
        for tag in self.tags:
            if query.lstrip("#") in tag:
                return True
        return False

    def __str__(self):
        tags = " ".join("#" + tag for tag in self.tags) or "-"
        return f"[{self.id}] {self.text} | tags: {tags}"


def split_text_and_tags(words):
    """
    Ділить список слів на текст і теги.
    Теги — це слова, що починаються з '#'.
    ["Buy", "milk", "#shop"] -> ("Buy milk", ["shop"])
    """
    text_words = []
    tags = []
    for word in words:
        if word.startswith("#"):
            tags.append(word)
        else:
            text_words.append(word)
    return " ".join(text_words), tags


class NoteBook:
    """Записник: зберігає нотатки за їх номером (id)."""

    def __init__(self):
        self.notes = {}     # {id: Note}
        self.next_id = 1    # номер для наступної нотатки

    def add_note(self, text, tags=None):
        note = Note(self.next_id, text, tags)
        self.notes[note.id] = note
        self.next_id = self.next_id + 1
        return note

    def find(self, note_id):
        if note_id not in self.notes:
            raise KeyError("Note not found.")
        return self.notes[note_id]

    def edit_note(self, note_id, new_text, new_tags=None):
        """Замінює текст нотатки. Якщо передали нові теги — замінює й теги."""
        note = self.find(note_id)
        if not new_text.strip():
            raise ValueError("Note text cannot be empty.")
        note.text = new_text.strip()
        if new_tags:
            note.tags = []
            for tag in new_tags:
                note.add_tag(tag)

    def delete(self, note_id):
        self.find(note_id)          # якщо нотатки немає — буде KeyError
        del self.notes[note_id]

    def search(self, query):
        """Нотатки, де текст query є в тексті або тегах."""
        return [note for note in self.notes.values() if note.matches(query)]

    def search_by_tag(self, tag):
        """Нотатки з точно таким тегом."""
        tag = tag.lstrip("#").lower()
        return [note for note in self.notes.values() if tag in note.tags]

    def sorted_by_tags(self):
        """
        Нотатки, відсортовані за тегами за абеткою.
        Нотатки без тегів — у кінці.
        """
        with_tags = [note for note in self.notes.values() if note.tags]
        without_tags = [note for note in self.notes.values() if not note.tags]
        with_tags.sort(key=lambda note: sorted(note.tags))
        return with_tags + without_tags

    def all_notes(self):
        return list(self.notes.values())
