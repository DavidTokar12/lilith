from __future__ import annotations

import re


class CoreError(Exception):
    pass


def get_function_definition(func_str: str):

    func_str = func_str.strip()

    # remove def
    func_str = func_str[4:]

    first_parentheses = func_str.find("(")
    number_of_parentheses = 1

    result = None

    for i, char in enumerate(
        func_str[(first_parentheses + 1) :], start=first_parentheses + 1
    ):

        if char == "(":
            number_of_parentheses += 1

        if char == ")":
            number_of_parentheses -= 1

        if number_of_parentheses == 0:
            result = i
            break

    pattern = re.compile(r"\s+")
    return re.sub(pattern, "", func_str[: result + 1])


def get_class_definition(class_str: str):

    class_str = class_str.strip()[6:]

    first_par = class_str.find("(")
    first_dots = class_str.find(":")

    if first_par == -1:
        return class_str[:first_dots]

    if first_dots == -1:
        return class_str[:first_par]

    if first_par < first_dots:
        closing_par = class_str.find(")")
        return class_str[:closing_par + 1]

    return class_str[:first_dots]
