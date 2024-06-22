br = "\n"
br2 = br*2
br3 = br*3


def hd(text: str, x: int = 1) -> str:
    '''
    Markdown header formatter
    args:
        text (str): unicode string, not bytestring
        x (int): header level, start from 1
    '''
    return f"{x * '#'} {text}".rstrip() + "\n"


def hd1(text: str) -> str: return hd(text, 1)
def hd2(text: str) -> str: return hd(text, 2)
def hd3(text: str) -> str: return hd(text, 3)
def hd4(text: str) -> str: return hd(text, 4)
def hd5(text: str) -> str: return hd(text, 5)


def idt(text: str, x: str = 1, o: str = 2) -> str:
    '''
    Markdown indent formatter
    args:
        text (str): unicode string, not bytestring
        x (int): intentation level, 0 means no indentation
        o (int): space per intentation
    '''
    lines = text.split("\n")
    indented_lines = [f"{x * o * ' '}{l}".rstrip() for l in lines]
    return "\n".join(indented_lines)


def idt1(text: str) -> str: return idt(text, 1)
def idt2(text: str) -> str: return idt(text, 2)
def idt3(text: str) -> str: return idt(text, 3)
def idt4(text: str) -> str: return idt(text, 4)
def idt5(text: str) -> str: return idt(text, 5)


def ul(text, x=1, o=2):
    '''
    Markdown bullet "-" formatter
    args:
        text (str): unicode string, not bytestring
        x (int): intentation level (2 spaces), 0 means no indentation
        o (int): space per intentation
    '''
    return f"{x * o * ' '}- {text}".rstrip()


def ul0(text: str) -> str: return ul(text, 0)
def ul1(text: str) -> str: return ul(text, 1)
def ul2(text: str) -> str: return ul(text, 2)
def ul3(text: str) -> str: return ul(text, 3)
def ul4(text: str) -> str: return ul(text, 4)
def ul5(text: str) -> str: return ul(text, 5)


def ol(text: str, n: int = 1, x: int = 1, o: int = 2) -> str:
    '''
    Markdown number list formatter
    args:
        text (str): unicode string, not bytestring
        n (int): numbering
        x (int): intentation level (2 spaces), 0 means no indentation
        o (int): space per intentation
    '''
    return f"{x * o * ' '}{n}. {text}".rstrip()
