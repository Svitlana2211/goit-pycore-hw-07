from collections import UserDict
from datetime import datetime, timedelta
import re
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, name):
        if not name:
            raise ValueError("Name cannot be empty.")
        super().__init__(name)


class Phone(Field):
    def __init__(self, number):
        number = re.sub(r'\D', '', number)
        if not self.is_valid(number):
            raise ValueError("Phone number must contain exactly 10 digits.")
        super().__init__(number)
    
    def is_valid(self, number):
        return len(number) == 10
    
class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)
    
		
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)
    
    def remove_phone(self, phone_number):
        clean_number = re.sub(r'\D', '', phone_number)
        self.phones = [phone for phone in self.phones if phone.value != clean_number]

    def edit_phone(self, old_number, new_number):
        clean_old = re.sub(r'\D', '', old_number)
        for idx, phone in enumerate(self.phones):
            if phone.value == clean_old:
                self.phones[idx] = Phone(new_number)
                return True
        raise ValueError("Old phone number not found.")

    def find_phone(self, phone_number):
        clean_number = re.sub(r'\D', '', phone_number)
        for phone in self.phones:
            if phone.value == clean_number:
                return phone
        return None
    
    def add_birthday(self, date_str):
        self.birthday = Birthday(date_str)


    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        bday = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones}{bday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_str = record.birthday.date.strftime("%d.%m.%Y")
                birthday = datetime.strptime(birthday_str, "%d.%m.%Y").date()
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_diffrence = (birthday_this_year - today).days

                if 0 <= days_diffrence <= 7:
                    congratulation_date = birthday_this_year

                    if congratulation_date.weekday() == 5:
                        congratulation_date += timedelta(days=2)
                    elif congratulation_date.weekday() == 6:
                        congratulation_date += timedelta(days=1)

                    upcoming_birthdays.append({"name": record.name.value, "congratulation_date": congratulation_date.strftime("%d.%m.%Y")})

        return upcoming_birthdays

        
# ---------------- Функції команд ----------------

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError) as e:
            return f"Error: {e}"
    return wrapper


@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book):
    name, old, new = args
    record = book.find(name)
    if not record:
        return "Contact not found."
    record.edit_phone(old, new)
    return "Phone number updated."


@input_error
def show_phones(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return f"Phone numbers for {name}: " + ', '.join(p.value for p in record.phones)
    return "Contact not found."


@input_error
def show_all(book):
    return "\n".join(str(record) for record in book.values()) or "Address book is empty."


@input_error
def add_birthday(args, book):
    name, date_str = args
    record = book.find(name)
    if not record:
        return "Contact not found."
    record.add_birthday(date_str)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if not record:
        return "Contact not found."
    if not record.birthday:
        return "Birthday not set."
    return f"{name}'s birthday: {record.birthday.value}"


@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays this week."
    result = "Upcoming birthdays:\n"
    for user in upcoming:
        result += f"{user['name']} - {user['congratulation_date']}\n"
    return result.strip()


# ---------------- Головна логіка ----------------

def parse_input(user_input):
    parts = user_input.strip().split()
    return parts[0], parts[1:]


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phones(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()



