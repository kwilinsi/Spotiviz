import typing
from sqlalchemy.orm.exc import DetachedInstanceError


class ReprModel:
    """
    This class is inherited by all tables defined elsewhere in the structure
    module. It allows for simpler implementation of the __repr__ method.

    This class is adapted from this stackoverflow question:
    https://stackoverflow.com/questions/55713664/sqlalchemy-best-way-to
    -define-repr-for-large-tables
    """

    def __repr__(self) -> str:
        return self._repr()

    def _repr(self, **fields: typing.Dict[str, typing.Any]) -> str:
        """
        Helper for __repr__
        """
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            try:
                field_strings.append(f'{key}={field!r}')
            except DetachedInstanceError:
                field_strings.append(f'{key}=DetachedInstanceError')
            else:
                at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({','.join(field_strings)})>"
        return f"<{self.__class__.__name__} {id(self)}>"
