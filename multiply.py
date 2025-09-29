# Only reply on memory and and operation

def multiply(x, y, bit_length=16):
    sum = 0
    shifted_x = x
    for i in range(bit_length):
        if bit(y, i):
            sum += shifted_x
        shifted_x = shifted_x + shifted_x
    return sum


def bit(x, i):
    twoToThe = []
    value = 1
    for _ in range(16):
        twoToThe.append(value)
        value += value

    # print(twoToThe)
    # print(x, twoToThe[i])
    return (x & twoToThe[i])
