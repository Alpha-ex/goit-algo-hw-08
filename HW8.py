# В даному коді використовуються наступні команди:

# add [ім'я] [телефон]: Додати новий контакт з іменем та телефонним номером.
# delete [ім'я] : Видалити контакт за іменем.
# change [ім'я] [новий телефон]: Змінити телефонний номер для вказаного контакту.
# phone [ім'я]: Показати телефонний номер для вказаного контакту.
# all: Показати всі контакти в адресній книзі.
# add-birthday [ім'я] [дата народження]: Додати дату народження для вказаного контакту.
# show-birthday [ім'я]: Показати дату народження для вказаного контакту.
# birthdays: Показати дні народження, які відбудуться протягом наступного тижня.
# hello: Отримати вітання від бота.
# close або exit: Закрити програму.

import re
import pickle
from datetime import datetime, timedelta
import sys

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not re.match(r'^\d{10}$', value):
            raise ValueError("Phone number must contain 10 digits")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise ValueError("Invalid birthday format. Use DD.MM.YYYY")
        super().__init__(value)

class Record:
    def __init__(self, name, phone):
        self.name = Name(name)
        self.phones = [Phone(phone)]
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        for p in self.phones:
            if str(p) == old_phone:
                p.value = new_phone

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        output = f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}"
        if self.birthday:
            output += f", birthday: {self.birthday.value}"
        return output

class AddressBook:
    def __init__(self):
        self.data = {}

    def add_record(self, record):
        self.data[record.name.value] = record

    def remove_record(self, name):
        del self.data[name]

    def delete_record(self, name):
        if name in self.data:
            del self.data[name]
            print(f"Contact {name} deleted successfully.")
        else:
            print("Contact not found.")
    
    def lookup_record(self, name):
        return self.data.get(name)

    def search_records_by_name(self, name):
        return [record for record in self.data.values() if record.name.value == name]

    def get_upcoming_birthdays(self):
        today = datetime.now()
        next_week = today + timedelta(days=7)
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, '%d.%m.%Y')
                if today <= birthday_date <= next_week:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

    def save_to_file(self, filename="addressbook.pkl"):
        with open(filename, 'wb') as f:
            pickle.dump(self.data, f)

    def load_from_file(self, filename="addressbook.pkl"):
        try:
            with open(filename, 'rb') as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            print("File not found. Creating new address book.")

    def process_command(self, command):
        command_parts = command.split()
        if not command_parts:
            print("Empty command.")
            return
    
        if command_parts[0] == "add":
            if len(command_parts) != 3:
                print("Invalid command format. Usage: add [ім'я] [телефон]")
                return
            name = command_parts[1]
            phone = command_parts[2]
            try:
                self.add_record(Record(name, phone))
                print(f"Contact {name} with phone {phone} added successfully.")
            except ValueError as e:
                print(f"Error: {e}")
        elif command_parts[0] == "change":
            if len(command_parts) != 3:
                print("Invalid command format. Usage: change [ім'я] [новий телефон]")
                return
            name = command_parts[1]
            new_phone = command_parts[2]
            if name in self.data:
                self.data[name].edit_phone(self.data[name].phones[0].value, new_phone)
            else:
                print("Contact not found.")
        elif command_parts[0] == "delete":
            if len(command_parts) != 2:
                print("Invalid command format. Usage: delete [ім'я]")
                return
            name = command_parts[1]
            self.delete_record(name)

        elif command_parts[0] == "phone":
            if len(command_parts) != 2:
                print("Invalid command format. Usage: phone [ім'я]")
                return
            name = command_parts[1]
            if name in self.data:
                print(self.data[name].phones[0])
            else:
                print("Contact not found.")
        elif command_parts[0] == "all":
            for record in self.data.values():
                print(record)
        elif command_parts[0] == "add-birthday":
            if len(command_parts) != 3:
                print("Invalid command format. Usage: add-birthday [ім'я] [дата народження]")
                return
            name = command_parts[1]
            birthday = command_parts[2]
            if name in self.data:
                self.data[name].add_birthday(birthday)
            else:
                print("Contact not found.")
        elif command_parts[0] == "show-birthday":
            if len(command_parts) != 2:
                print("Invalid command format. Usage: show-birthday [ім'я]")
                return
            name = command_parts[1]
            if name in self.data and self.data[name].birthday:
                print(self.data[name].birthday)
            else:
                print("Contact not found or no birthday set.")
        elif command_parts[0] == "birthdays":
            upcoming_birthdays = self.get_upcoming_birthdays()
            if not upcoming_birthdays:
                print("No upcoming birthdays.")
            else:
                print("Upcoming birthdays:")
                for record in upcoming_birthdays:
                    print(f"{record.name}: {record.birthday}")
        elif command_parts[0] == "hello":
            print("Hello!")
        elif command_parts[0] == "close" or command_parts[0] == "exit":
            self.save_to_file("address_book.pkl")
            print("Address book saved. Goodbye!")
            sys.exit()
        else:
            print("Invalid command.")

def main():
    book = AddressBook()
    book.load_from_file("address_book.pkl")
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        book.process_command(user_input)

if __name__ == "__main__":
    main()