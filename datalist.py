import json


class Datalist:
    def __init__(self, filename):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Файл не найден.")
            return None

    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    @property
    def datalist(self):
        return self.data.get('directories', [])

    @datalist.setter
    def datalist(self, value):
        self.data['directories'] = value

    def get_datalist(self, name):
        for datalist in self.datalist:
            if datalist['name'] == name:
                return datalist
        print("Дисциплина не найдена.")
        return None

    def add_datalist(self, name, directories):
        new_datalist = {
            "name": name,
            "directories": directories
        }
        self.datalist.append(new_datalist)
        self.save_data()

    def remove_datalist(self, name):
        datalist = self.get_datalist(name)
        if datalist:
            self.datalist.remove(datalist)
            self.save_data()

    def get_directories(self, name):
        for datalist in self.data:
            if datalist['name'] == name:
                return datalist['directories']
        print("Дисциплина не найдена.")
        return None

    # итератор__iter__
    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def items(self):
        yield from self.data.items()

    def values(self):
        for value in self.data.values():
            if isinstance(value, list):
                yield from value
            else:
                yield value

    # итератор для дисциплин
    def datalist_iterator(self):
        return iter(self.datalist)

    def get_datalist_iter(self):
        for datalist in self.datalist:
            yield datalist
