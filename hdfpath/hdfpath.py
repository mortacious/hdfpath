from .jsonpath_ng import Fields, DatumInContext, auto_id_field, AutoIdForDatum, NOT_SET, Child
from .jsonpath_ng.ext.parser import ExtentedJsonPathParser
from .jsonpath_ng.ext.string import DefinitionInvalid
import re
from itertools import chain


class AttributedFields(Fields):
    """
    Support for Fields with additional (metadata) attributes in a dict-like structure.

    Parameters
    ----------
    fields: list(str) or str
        The fields to consider. If "*" is passed, all fields at this specific level are used.
    attribute: str
        Additional attribute of the objects at this level to also consider (default: 'attrs'). HDF-Files
        usually have metadata attached at each group or dataset, which can be used for queries this way.
    """
    def __init__(self, *fields, attribute='attrs'):
        super().__init__(*fields)
        self.attribute = attribute

    def get_field_datum(self, datum, field, create):
        if field == auto_id_field:
            return AutoIdForDatum(datum)
        try:
            if field.startswith("_"):
                try:
                    field = field[1:]
                    attr = getattr(datum.value, self.attribute)
                    field_value = attr.get(field, NOT_SET)
                except AttributeError:
                    field_value = NOT_SET
            else:
                field_value = datum.value.get(field, NOT_SET)

            if field_value is NOT_SET:
                if create:
                    datum.value[field] = field_value = {}
                else:
                    return None
            return DatumInContext(field_value, path=Fields(field), context=datum)
        except (TypeError, AttributeError):
            return None

    def reified_fields(self, datum):
        if '*' not in self.fields:
            return self.fields
        else:
            try:
                iterables = [datum.value.keys()]
                try:
                    attr = getattr(datum.value, self.attribute)
                    iterables.append(("_" + k for k in attr.keys()))
                except AttributeError:
                    pass

                fields = tuple(chain(*iterables))
                return fields if auto_id_field is None else fields + (auto_id_field,)
            except AttributeError:
                return ()


REGEX = re.compile("regex\((.*)\)")


class Regex(AttributedFields):
    """
    Only consider fields that match the given regular expression. Different from the Fields-class only
    one expression is allowed here.

    Parameters
    ----------
    method: str
        String containing a regular expression in the form: 'regex(<regex>)'.
        Backslashes an other regex-specific characters ('\', etc.) have to be escaped properly.
    """
    def __init__(self, method=None):
        m = REGEX.match(method)
        if m is None:
            raise DefinitionInvalid("%s is not valid" % method)
        expr = m.group(1).strip()
        self.regex = re.compile(expr)
        super().__init__("*")

    def reified_fields(self, datum):
        fields = [field for field in super().reified_fields(datum) if self.regex.fullmatch(field)]
        return tuple(fields)

    def __str__(self):
        return f'regex({self.regex.pattern})'

    def __repr__(self):
        return f'{self.__class__.__name__}({self.regex.pattern})'

    def __eq__(self, other):
        return isinstance(other, Regex) and self.regex == other.regex


class HDFPathParser(ExtentedJsonPathParser):
    """Custom LALR-parser for HDF5 files based on JsonPath"""
    def __init__(self, metadata_attribute='attrs', debug=False, lexer_class=None):
        super().__init__(debug=debug, lexer_class=lexer_class)
        self.metadata_attribute = metadata_attribute

    def p_jsonpath_named_operator(self, p):
        "jsonpath : NAMED_OPERATOR"
        if p[1].startswith("regex("):
            p[0] = Regex(p[1])
        else:
            super().p_jsonpath_named_operator(p)

    def p_jsonpath_fields(self, p):
        "jsonpath : fields_or_any"
        p[0] = AttributedFields(*p[1], attribute=self.metadata_attribute)

    def p_jsonpath_fieldbrackets(self, p):
        "jsonpath : '[' fields ']'"
        p[0] = AttributedFields(*p[2], attribute=self.metadata_attribute)

    def p_jsonpath_child_fieldbrackets(self, p):
        "jsonpath : jsonpath '[' fields ']'"
        p[0] = Child(p[1], AttributedFields(*p[3], attribute=self.metadata_attribute))


def parse(path, metadata_attribute='attrs', debug=False):
    return HDFPathParser(metadata_attribute=metadata_attribute, debug=debug).parse(path)