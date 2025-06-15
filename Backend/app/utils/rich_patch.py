import builtins
from rich.console import Console # type: ignore

_original_print = print  # save original print to restore if needed

def enable_rich_print():
    builtins.print = Console().print

def disable_rich_print():
    builtins.print = _original_print
