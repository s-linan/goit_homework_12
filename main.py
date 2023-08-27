import json
from collections import UserDict
from datetime import datetime, date
import re

"""Class Field is parent class for value classes, here is some methods to override data format
and to compare some data of values."""


class Field:

    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self) -> str:
        return self.value

    def __eq__(self, input) -> bool:
        if type(input) == self.__class__:
            return self.value == input.value


"""Class Name take name value and check the data format,
if format wrong raise error."""


class Name(Field):
    def __init__(self, value):
        super().__init__(value)

    @staticmethod
    def valid_name(name: str) -> None:
        if type(name) != str:
            raise ValueError("Name must be a string")

    @Field.value.setter
    def value(self, value: str) -> None:
        self.valid_name(value)
        self._value = value


"""Class Phone take phone value and check the data format,
if format wrong raise error."""


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

    @staticmethod
    def valid_phone(phone: str) -> None:
        if type(phone) != str:
            raise ValueError("Phone must be a string of numbers")
        if not phone.isdigit():
            raise ValueError("Phone must be a string of numbers")

    @Field.value.setter
    def value(self, value):
        self.valid_phone(value)
        self._value = value


"""
Class Birthday take birthday value and check the data format,
if format wrong raise error.
"""


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)

    @staticmethod
    def valid_birthday(b_day):
        try:
            return str(datetime.strptime(str(b_day), '%Y-%m-%d').date())
        except Exception:
            raise ValueError('Input date format YYYY-MM-DD')

    @Field.value.setter
    def value(self, new_value):
        self._value = self.valid_birthday(new_value)


"""Class Record are like main class, he take values and spread it all to their places also edit or delete phone numbers.
Also here are the days_to_birthday method which can return the number of days until the birthday.
Also here are the __str__ method which make f-strings to output data"""


class Record:
    def __init__(self, name: Name, phone: Phone = None, birthday: Birthday = None):
        self.name = name
        self.phones = [phone] if phone else []
        self.birthday = birthday

    def add_phone(self, phone: Phone):
        if phone.value not in [ph.value for ph in self.phones]:
            self.phones.append(phone)

    def delete_phone(self, phone: Phone):
        if phone.value in [ph.value for ph in self.phones]:
            self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        if old_phone.value in [ph.value for ph in self.phones]:
            self.phones.remove(old_phone)
            self.phones.append(new_phone)

    def days_to_birthday(self):
        if self.birthday is not None:
            current_day = date.today()
            current_birthday = self.birthday.value.replace(
                year=datetime.today().year)
            if current_day > current_birthday:
                current_birthday = current_birthday.replace(year=date.today().year + 1)
            return (current_birthday - current_day).days
        return 'Birthday info not recorded!'

    def __str__(self) -> str:
        if self.birthday is None:
            b_day = 'Not recorded'
        else:
            b_day = self.birthday
        phones = ", ".join([str(ph) for ph in self.phones])
        return f"name: {str(self.name)}, phones: {phones}, birthday: {b_day};\n"


"""Class AddressBook record all values in self data, can find records and output pages with data for the entered
number of records for pages or for 1 per page if number was not entered or input wrong"""


class AddressBook(UserDict):
    N = None
    filename = 'contacts.txt'

    def recovery_data(self, filename):
        recovery_dict = self.read_contacts_from_file(filename)
        for name, value in recovery_dict.items():
            replace_list = ['[', ']', "'"]
            b_day = str(value.get('birthday'))
            phones = str(value.get('phones'))
            for ch in replace_list:
                phones = phones.replace(ch, '')
            phones = phones.split(', ')
            if b_day.find('Not recorded') != -1:
                temp_record = Record(Name(name), Phone(phones[0]))
            else:
                temp_record = Record(Name(name), Phone(phones[0]), Birthday(b_day))
            self.add_record(temp_record)
            iter = 1
            while iter < len(phones):
                temp_record.add_phone(Phone(phones[iter]))
                iter += 1
        for i in self.data.values():
            print(i)

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find_record(self, value):
        match_list = list()
        for record in self.data.values():
            phone_number = ", ".join([str(ph) for ph in record.phones])
            if record.name.value.find(value.title()) != -1 or phone_number.find(value) != -1:
                match_list.append(str(record))

        if len(match_list) < 1:
            return 'There are no matches'
        else:
            return match_list

    def iterator(self, num=None):
        if type(num) == int and num > 0:
            AddressBook.N = num
        else:
            print('Number must be positive integer.\nNumber is automatically set to 1.')
            AddressBook.N = 1
        return self.__next__()

    # iterate in AddressBook and make strings with data
    def __iter__(self):
        result = ""
        counter = 0
        len_counter = 0
        for record in self.data.values():
            counter += 1
            len_counter += 1
            result += str(record)
            if counter == AddressBook.N:
                yield result
                result = ""
                counter = 0
            if len_counter == len(self.data):
                yield result
                result = ""
                counter = 0

    # generate pages and output it until all data will be outputted
    def __next__(self):
        generator = self.__iter__()
        page = 1
        while True:
            try:
                result = next(generator)
                if result:
                    print(f'{"-" * 10} Page {page} {"-" * 10}')
                    print(result)
                    page += 1
            except StopIteration:
                print(f'{"-" * 12} END {"-" * 13}')
                break

    def prepare_to_write(self):
        return_dict = dict()
        for record in self.data.values():
            if record.birthday is None:
                b_day = 'Not recorded'
            else:
                b_day = record.birthday
            return_dict.update({
                record.name.value: {
                    'phones': [", ".join([str(ph) for ph in record.phones])],
                    'birthday': str(b_day)}
            })
        return return_dict

    def write_contacts_to_file(self, filename):
        with open(filename, 'w') as fh:
            json.dump(AddressBook.prepare_to_write(self), fh, indent=4)

    def read_contacts_from_file(self, filename):
        with open(filename, 'r') as fh:
            unpacked = json.load(fh)
            return unpacked


if __name__ == "__main__":
    # if len(AddressBook().data) < 1:
    #     AddressBook().recovery_data('contacts.txt')

    name_1 = Name('Bill_1')
    phone_1 = Phone('123456789')
    name_2 = Name('Bill_2')
    phone_2 = Phone('123456789')
    name_3 = Name('Bill_3')
    phone_3 = Phone('1234567890')
    name_4 = Name('Bill_4')
    phone_4 = Phone('1234567890')
    name_5 = Name('Bill_5')
    phone_5 = Phone('1234567890')
    birthday = Birthday('2000-08-19')
    rec_1 = Record(name_1, phone_1, birthday)
    rec_2 = Record(name_2, phone_2)
    rec_3 = Record(name_3, phone_3)
    rec_4 = Record(name_4, phone_4)
    rec_5 = Record(name_5, phone_5)
    rec_1.add_phone(phone_3)
    rec_1.edit_phone(Phone('123456789'), Phone('0454054'))
    ab = AddressBook()
    ab.add_record(rec_1)
    ab.add_record(rec_2)
    ab.add_record(rec_3)
    ab.add_record(rec_4)
    ab.add_record(rec_5)
    # ab.iterator()
    # print(ab.data)
    # print(ab.prepare_to_write())
    # ab.write_contacts_to_file('contacts.txt')
    # print(ab.read_contacts_from_file('contacts.txt'))
    # ab.iterator()
    # ab.iterator()
    # print('All Ok)')
    print(ab.find_record('bil'))
