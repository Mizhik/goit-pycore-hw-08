from collections import UserDict

from abc import ABC, abstractmethod
from datetime import datetime as dtdt
import pickle


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as ve:
            return f"Value error: {ve}"
        except KeyError:
            return "No such name found"
        except IndexError:
            return "Not found"

    return inner


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


class Field(ABC):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
    @abstractmethod
    def is_valid(self):
        pass

class Name(Field):
    def __init__(self, name):
        super().__init__(name)
        if not self.is_valid():
            raise ValueError("Invalid name format. Name must not be empty.")
    
    def is_valid(self):
        return self.value.strip()
    
class Phone(Field):
    def __init__(self, phone):
        super().__init__(phone)
        if not self.is_valid():
            raise ValueError("Invalid phone  format. Phone must be 10 digits.")
    
    def is_valid(self):
        return len(self.value) == 10 and self.value.isdigit()

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        if not self.is_valid(value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
    def is_valid(self,value):
        try:
            self.value = dtdt.strptime(value, "%d.%m.%Y").date()
            return True
        except ValueError:
            return False
        
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Phone not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
    
    def add_birthday(self, bdate):
        birthday = Birthday(bdate)
        if not self.birthday:
            self.birthday = birthday
            return "Birthday added."
        else:
            return "Already have"

    def __str__(self):
        formatted_date = self.birthday.value.strftime("%d.%m.%Y") if self.birthday else "N/A"
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {formatted_date}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if not self.data.pop(name, None):
            raise NameError("Contact not found")
    
    def get_upcoming_birthdays(self):
        tdate = dtdt.today().date()
        birthdays = []

        for record in self.values():
            bdate = record.birthday
            if bdate:
                bdate_this_year = bdate.value.replace(year=tdate.year)
                days_between = (bdate_this_year - tdate).days

                if 0 <= days_between <= 7:
                    birthdays.append({'name': record.name.value, 'birthday': bdate_this_year.strftime("%A, %d.%m.%Y")})
        return birthdays
    
    def __str__(self):
        result = ""
        for record in self.values():
            result += f"{str(record)}\n"
        return result.strip()



@input_error
def add_contact(args, book):
    name, phone = args
    if name not in book:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    else:
        return "Already have"

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return record
    return "Not found"

@input_error
def change_contact(args, book):
    name, phone = args
    record = book.find(name)
    if record:
        record.edit_phone(record.phones[0].value, phone)
        return "Contact changed."
    return "Not found"

@input_error
def all_contact(book):
   return str(book) if book else "Not found"


@input_error
def add_birthday(args, book):
    name, bdate = args
    record = book.find(name)
    if record:
        return record.add_birthday(bdate)
    else:
        return "Contact not found"

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return record.birthday.value.strftime("%d.%m.%Y")
    return "Not found"

@input_error
def birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        result = ""
        for birthday_info in upcoming_birthdays:
            result += f"{birthday_info['name']}'s birthday is on {birthday_info['birthday']}.\n"
        return result.strip()
    else:
        return 'Not upcoming birthdays'
    
@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

class UserInterface(ABC):
    @abstractmethod
    def display_contact(self, contact):
        pass

    @abstractmethod
    def all_command(self, prompt):
        pass
    
    @abstractmethod
    def display_message(self,message):
        pass
  
            
class ConsoleInterface(UserInterface):
    def all_command(self, list_command):
        dict_command = {number: command for number, command in enumerate(list_command)}
        for key, value in dict_command.items():
            print(f"{key}: {value[0]} -> {value[1]}")

    def display_contact(self, contacts):
        print(str(contacts) if contacts else "Not found")
    
    def display_message(self,message):
        print(message)
            
    
def main(interface:UserInterface):
    list_command = [['hello','Display welcome message.'],
                    ['add','[name] [phone]: Add a new contact.'], 
                    ['change','[name] [phone]: Add a new contact.'],
                    ['phone','[name]: Display the phone number of a contact.'],
                    ['all','Display all contacts.'],
                    ['add-birthday','[name] [date]: Add birthday to a contact.'],
                    ['show-birthday','[name]: Show birthday of a contact.'],
                    ['birthdays','Show upcoming birthdays.'],
                    ['exit or close','Show upcoming birthdays.']]
    book = load_data()
    print("Welcome to the assistant bot! --all command -> command 'help'-- ")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == 'help':
            interface.all_command(list_command)

        elif command == "hello":
            interface.display_message("How can I help you?")

        elif command == "add":
            interface.display_message(add_contact(args, book))

        elif command == "change":
            interface.display_message(change_contact(args, book))

        elif command == "phone":
            interface.display_message(show_phone(args, book))

        elif command == "all":
            contact = all_contact(book)
            interface.display_contact(contact)

        elif command == "add-birthday":
            interface.display_message(add_birthday(args,book))

        elif command == "show-birthday":
            interface.display_message(show_birthday(args, book))

        elif command == "birthdays":
            interface.display_message(birthdays(book))
        else:
            interface.display_message("Invalid command.")

if __name__ == "__main__":
    main(ConsoleInterface())