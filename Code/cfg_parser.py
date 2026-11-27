"""Build and evaluate a Lark CFG against labeled strings (requires lark)."""
from lark import Lark
from lark.exceptions import UnexpectedInput


def build_grammar(grammar):
    return Lark(grammar, parser="earley", start="start")


def accepts_input(parser, word):
    try:
        parser.parse(word)
        return True
    except UnexpectedInput:
        return False
