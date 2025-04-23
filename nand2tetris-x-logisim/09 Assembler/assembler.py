#!/usr/bin/env python3
from pathlib import Path
import re


class Instruction:

    RE_SYMBOL = r'[a-zA-Z_\.\$\:][a-zA-Z_\.\$\:0-9]*'
    RE_L_INSTR = r'^\([a-zA-Z_\.\$\:][a-zA-Z_\.\$\:0-9]*\)$'
    RE_A_INSTR = r'^@([a-zA-Z_\.\$\:][a-zA-Z_\.\$\:0-9]*|[0-9]{1,5})$'

    def __init__(self, instruction):
        self.original = instruction
        self.asm_line_ofst = None
        self.hack_line_ofst = None

    @property
    def code(self):
        code = self.original

        comment_position = code.find('//')

        code = code[:comment_position]

        code = code.strip()

        return code

    @property
    def is_instruction(self):
        return self.code != ''

    @property
    def is_comment(self):
        return self.original.startswith('//')

    @property
    def is_blank(self):
        return self.original.strip() == ''

    @property
    def is_valid(self):
        if not self.is_instruction:
            return True

        if self.type == 'A_INSTRUCTION':
            if not re.match(self.RE_A_INSTR, self.code):
                return False
            return True

        if self.type == 'L_INSTRUCTION':
            if not re.match(self.RE_L_INSTR, self.code):
                return False
            return True

        # C instruction
        return True

    @property
    def type(self):

        if self.code.startswith('@'):
            return 'A_INSTRUCTION'
        elif self.code.startswith('('):
            return 'L_INSTRUCTION'
        else:
            return 'C_INSTRUCTION'

    @property
    def symbol(self):

        if self.type == 'A_INSTRUCTION':
            return self.code[1:]
        elif self.type == 'L_INSTRUCTION':
            return self.code[1:-1]
        else:
            raise Exception('Not a symbol.')

    @property
    def dest(self):
        if self.type != 'C_INSTRUCTION':
            raise Exception('Not a C instruction.')

        if '=' not in self.code:
            return ''
        else:
            return self.code.split('=', 1)[0]

    @property
    def comp(self):
        if self.type != 'C_INSTRUCTION':
            raise Exception('Not a C instruction.')

        code = self.code

        if '=' in code:
            code = code.split('=')[1]

        if ';' in code:
            return code.split(';', 1)[0]
        else:
            return code

    @property
    def jump(self):

        if self.type != 'C_INSTRUCTION':
            raise Exception('Not a C instruction.')

        if ';' in self.code:
            return self.code.split(';', 1)[-1]
        else:
            return ''

    def __str__(self):
        return f'Line: {self.asm_line_ofst + 1}, Type: {self.type}, Code: {self.original}.'


class Parser:

    def __init__(self, file_path):
        self.asm_file_path = file_path
        self.hack_line_ofst = -1
        self.asm_line_ofst = -1

    def advance(self):
        with open(self.asm_file_path) as fd:
            for line in fd.readlines():
                self.asm_line_ofst += 1

                instr = Instruction(line)
                if not instr.is_instruction:
                    continue

                instr.asm_line_ofst = self.asm_line_ofst

                # print(instr, instr.is_valid)
                if not instr.is_valid:
                    raise Exception(f'Invalid code: {instr}')

                if instr.type == 'L_INSTRUCTION':
                    instr.hack_line_ofst = self.hack_line_ofst + 1
                else:
                    self.hack_line_ofst += 1
                    instr.hack_line_ofst = self.hack_line_ofst

                yield instr


class MicroCode:

    DEST = {
        '':     0b000,
        'M':    0b001,
        'D':    0b010,
        'MD':   0b011,
        'A':    0b100,
        'AM':   0b101,
        'AD':   0b110,
        'AMD':  0b111,
    }

    JUMP = {
        '':     0b000,
        'JGT':  0b001,
        'JEQ':  0b010,
        'JGE':  0b011,
        'JLT':  0b100,
        'JNE':  0b101,
        'JLE':  0b110,
        'JMP':  0b111,
    }

    COMP = {
        '0':    0b0101010,
        '1':    0b0111111,
        '-1':   0b0111010,
        'D':    0b0001100,
        'A':    0b0110000,
        '!D':   0b0001101,
        '!A':   0b0110001,
        '-D':   0b0001111,
        '-A':   0b0110011,
        'D+1':  0b0011111,
        'A+1':  0b0110111,
        'D-1':  0b0001110,
        'A-1':  0b0110010,
        'D+A':  0b0000010,
        'D-A':  0b0010011,
        'A-D':  0b0000111,
        'D&A':  0b0000000,
        'D|A':  0b0010101,
        'M':    0b1110000,
        '!M':   0b1110001,
        '-M':   0b1110011,
        'M+1':  0b1110111,
        'M-1':  0b1110010,
        'D+M':  0b1000010,
        'D-M':  0b1010011,
        'M-D':  0b1000111,
        'D&M':  0b1000000,
        'D|M':  0b1010101,
    }

    @classmethod
    def dest(cls, mnemonic):
        return cls.DEST[mnemonic]

    @classmethod
    def comp(cls, mnemonic):
        return cls.COMP[mnemonic]

    @classmethod
    def jump(cls, mnemonic):
        return cls.JUMP[mnemonic]


class SymbolTable:

    RESERVED = {
        'SP':       0x0000,
        'LCL':      0x0001,
        'ARG':      0x0002,
        'THIS':     0x0003,
        'THAT':     0x0004,
        'R0':       0x0000,
        'R1':       0x0001,
        'R2':       0x0002,
        'R3':       0x0003,
        'R4':       0x0004,
        'R5':       0x0005,
        'R6':       0x0006,
        'R7':       0x0007,
        'R8':       0x0008,
        'R9':       0x0009,
        'R10':      0x000A,
        'R11':      0x000B,
        'R12':      0x000C,
        'R13':      0x000D,
        'R14':      0x000E,
        'R15':      0x000F,
        'SCREEN':   0x4000,
        'KBD':      0x6000,
    }

    # Code segment addressing
    labels = {}

    # Data segment addressing
    variables = {}

    VARIABLE_START_ADDR = 0x0010

    singleton = None

    def __new__(cls):
        if cls.singleton is None:
            cls.singleton = super().__new__(cls)
        return cls.singleton

    def add_label(self, label, line_ofst):
        if label in self.RESERVED:
            raise Exception(f'{label} is a reserved symbol.')

        if label in self.labels:
            raise Exception(f'{label} is defined previously as label.')

        if label in self.variables:
            raise Exception(f'{label} is defined previously as variable.')

        self.labels[label] = line_ofst

    def add_variable(self, var_name):
        if var_name in self.RESERVED:
            raise Exception(f'{var_name} is a reserved symbol.')

        if var_name in self.labels:
            raise Exception(f'{var_name} is defined previously as label.')

        if var_name in self.variables:
            raise Exception(f'{var_name} is defined previously as variable.')

        offset = len(self.variables)

        self.variables[var_name] = self.VARIABLE_START_ADDR + offset

    def is_reserved(self, symbol):
        return symbol in self.RESERVED.keys()

    def is_label(self, symbol):
        return symbol in self.labels.keys()

    def is_variable(self, symbol):
        return symbol in self.variables.keys()

    def is_symbol(self, symbol):
        return (
            self.is_reserved(symbol)
            or
            self.is_label(symbol)
            or
            self.is_variable(symbol)
        )

    def get_address(self, symbol):
        if not self.is_symbol(symbol):
            raise Exception(f'{symbol} is not defined')

        if symbol in self.RESERVED:
            return self.RESERVED[symbol]

        if symbol in self.variables:
            return self.variables[symbol]

        if symbol in self.labels:
            return self.labels[symbol]

    def add_symbol_from_instruction(self, instruction):

        if not instruction.is_instruction:
            return

        if instruction.type == 'C_INSTRUCTION':
            return

        if instruction.type == 'L_INSTRUCTION':
            self.add_label(
                instruction.symbol, instruction.hack_line_ofst)
            return

        # A instruction
        if instruction.symbol.isdigit():
            return

        if not self.is_variable(instruction.symbol):
            self.add_variable(instruction.symbol)

    def translate_symbol(self, instruction):
        if not instruction.is_instruction:
            return None

        if instruction.type != 'A_INSTRUCTION':
            return None

        symbol = instruction.symbol

        if symbol.isdigit():
            return int(symbol)
        elif not (self.is_label(symbol) or self.is_reserved(symbol)):
            self.add_symbol_from_instruction(instruction)
            return self.get_address(symbol)
        else:
            return self.get_address(symbol)

    def __str__(self):
        string = ''
        # string += 'Reserved:\n'
        # for k, v in self.RESERVED.items():
        #     string += f'\t{k}: {v}\n'

        string += 'Labels:\n'
        for k, v in self.labels.items():
            string += f'\t{k}: (code address) {v}\n'

        string += 'Variables:\n'
        for k, v in self.variables.items():
            string += f'\t{k}: (data address) {v}\n'

        return string


class CodeGen:

    A_INSTRUCTION = '0{addr:0>15b}'
    C_INSTRUCTION = '111{comp:07b}{dest:03b}{jump:03b}'

    def __init__(self, asm_file_path):
        self.file_path = asm_file_path.parent / asm_file_path.name.replace(
            'asm', 'hack')
        self.fd = open(
            self.file_path, mode='w', encoding="UTF-8", newline='\n')

    def save(self, machine_code):
        self.fd.write(machine_code)

    def generate(self, instruction, symbol_table):
        if instruction.type == 'A_INSTRUCTION':
            self.gen_a_instr(instruction, symbol_table)
            return

        if instruction.type == 'C_INSTRUCTION':
            self.gen_c_instr(instruction)
            return

        raise Exception(f'{instruction.code} cannot be translated.')

    def gen_a_instr(self, instruction, symbol_table):
        machine_code = self.A_INSTRUCTION.format(
                addr=symbol_table.translate_symbol(instruction)
                )
        self.fd.write(f'{machine_code}\n')

    def gen_c_instr(self, instruction):
        machine_code = self.C_INSTRUCTION.format(
            comp=MicroCode.comp(instruction.comp),
            dest=MicroCode.dest(instruction.dest),
            jump=MicroCode.jump(instruction.jump)
            )
        self.fd.write(f'{machine_code}\n')


def work(file_path):
    file_path = Path(file_path).resolve()

    symbol_table = SymbolTable()

    for instruction in Parser(file_path).advance():
        if instruction.type == 'L_INSTRUCTION':
            symbol_table.add_symbol_from_instruction(instruction)

    # print(symbol_table)

    code_gen = CodeGen(file_path)

    for instruction in Parser(file_path).advance():

        if instruction.type == 'L_INSTRUCTION':
            continue

        code_gen.generate(instruction, symbol_table)

    # print(symbol_table)


if __name__ == '__main__':
    import sys
    work(sys.argv[1])
