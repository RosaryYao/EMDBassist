import random


class Container:
    def __init__(self, items):
        self.items = list()
        for item in items:
            self.items.append(Item(*item))

    def __str__(self):
        return f"Container with {len(self.items)} items"

    def __bytes__(self):
        print("i'm being called")
        return str(self).encode('utf-8')

    def __getitem__(self, item):
        return self.items[item]

    def __setitem__(self, item, value):
        self.items[item] = value


class Item:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return f"Item with name={self.name}, value={self.value}"


items = [
    ('a', random.randint(0, 100)),
    ('b', random.randint(0, 100)),
    ('c', random.randint(0, 100)),
    ('d', random.randint(0, 100)),
    ('e', random.randint(0, 100)),
    ('f', random.randint(0, 100)),
    ('g', random.randint(0, 100)),
    ('h', random.randint(0, 100)),
    ('i', random.randint(0, 100)),
]

container = Container(items)

print(f"container: {container}")

print(bytes(container))

print(f"item no 3: {container[3]}")
print(f"changing item no 3 to 6:")
container[3] = 6
print(container.items)

item = Item(*items[0])  # unpack a tuple
print(f"{item}")

an_item = container[7]
print(an_item)
