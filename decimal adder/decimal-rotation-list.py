SYMBOLS = [
    str(i)
    for i in range(10)
]


def half_adder(n1, n2):
    carry = '0'

    while n2 != '0':
        n2, borrow = one_digit_decrement(n2)

        c1, n1 = one_digit_increment(n1)
        if c1 != '0':
            carry = c1

    return carry, n1


def full_adder(n1, n2, n3):

    c0, d0 = half_adder(n1, n2)
    c1, d1 = half_adder(d0, n3)

    # carry will be 0 , need proof
    _, d2 = half_adder(c0, c1)

    return d2, d1


def one_digit_increment(n):

    assert (n in SYMBOLS)

    index = SYMBOLS.index(n)

    next_index = (index + 1) % len(SYMBOLS)

    carry = '0'
    if next_index == 0:
        carry = '1'

    return carry, SYMBOLS[next_index]


def one_digit_decrement(n):
    assert (n in SYMBOLS)

    index = SYMBOLS.index(n)

    next_index = (index - 1) % len(SYMBOLS)

    borrow = '0'
    if next_index == len(SYMBOLS) - 1:
        borrow = '1'

    return SYMBOLS[next_index], borrow


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
    calc_length = max(len(n1), len(n2))
    n1 = n1.zfill(calc_length)
    n2 = n2.zfill(calc_length)

    carry = '0'
    d0 = []

    for i in range(calc_length):
        n1_digit = n1[calc_length - i - 1]
        n2_digit = n2[calc_length - i - 1]
        carry, d0_digit = full_adder(n1_digit, n2_digit, carry)

        d0.append(d0_digit)

    if carry != '0':
        return carry + ''.join(d0[::-1])
    else:
        return ''.join(d0[::-1])
