

def stack_push():
    commands = [
        '@SP',      # load stack pointer (SP)
        'AM=M+1',   # SP + 1, store in SP, change memory
        'A=A-1',    # previous slot
        'M=D',      # assign value
    ]

    # alternative
    commands = [
        '@SP',
        'A=M'
        'M=D',
        '@SP',
        'M=M+1',
    ]

    return commands
