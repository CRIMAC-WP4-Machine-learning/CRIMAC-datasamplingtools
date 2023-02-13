class SomeClass:
    _attr1: list[int, ...]

    def __init__(self) -> None:
        self._attr1.extend([1, 2, 3])

    def get_attr1(self) -> list[int, ...]:
        return self._attr1


c = SomeClass()
print(c.get_attr1())

d = SomeClass()
print(d.get_attr1())