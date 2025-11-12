def add(n1: str, n2: str) -> str:
    """
    Adds two numbers and returns the result.

    >>> add('2', '3')
    '5'
    >>> add('4', '5')
    '9'
    >>> add('1000', '999')
    '1999'
    >>> add('9999', '9999')
    '19998'
    """

    n1 = int(n1)
    n2 = int(n2)

    return str(n1 + n2)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
