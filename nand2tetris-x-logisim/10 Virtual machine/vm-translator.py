#!/usr/bin/env python3
from pathlib import Path


class Segment:

    def __init__(self, Label):
        self.Label = Label

    def check_index(self, index):
        pass

    def load_addr(self, index):

        self.check_index(index)

        commands = [
            '@%d' % index,
            'D=A',
            '@%s' % self.Label,
            'AD=D+M',  # Sometimes A is for addressing, sometimes D is store address
        ]

        return commands

    def load(self, index):
        commands = self.load_addr(index)

        commands += [
            'D=M',
            ]

        return commands

    def store(self):

        return ['M=D']


class StaticSegment(Segment):

    def __init__(self, vm_name):
        self.vm_name = vm_name

    def load_addr(self, index):
        commands = [
            '@%s.%d' % (self.vm_name, index),
            'D=A',
        ]

        return commands


class ConstantSegment(Segment):

    def load(self, index):
        commands = [
            '@%d' % index,
            'D=A',
        ]

        return commands

    def store(self):
        raise Exception('Constant segment is virtual.')


class TempSegment(Segment):

    def load_addr(self, index):

        self.check_index(index)

        commands = [
            '@%d' % index,
            'D=A',
            '@%s' % self.Label,
            'AD=D+A',
        ]

        return commands

    def check_index(self, index):
        if index > 7:
            raise Exception('Temporary segment overflow')


class PointerSegment(Segment):

    def load_addr(self, index):

        self.check_index(index)

        commands = [
            '@%d' % index,
            'D=A',
            '@%s' % self.Label,
            'AD=D+A',
        ]

        return commands

    def check_index(self, index):
        if index > 2:
            raise Exception('Pointer segment overflow')


class Stack:

    MAX = 2057
    MIN = 256

    def __init__(self):
        self.top = self.MIN
        self.constant = ConstantSegment('constant')
        self.local = Segment('LCL')
        self.argument = Segment('ARG')
        self.this = Segment('THIS')
        self.that = Segment('THAT')
        self.temp = TempSegment('R5')
        self.pointer = PointerSegment('R3')

        self.static = None

    def set_static_segment(self, filename):
        self.static = StaticSegment(filename)

    def push(self, segment, index):

        if self.top > self.MAX:
            raise Exception('Stackoverflow')

        segment = getattr(self, segment)

        commands = segment.load(index)
        commands += [
            '@SP',
            'AM=M+1',
            'A=A-1',
            'M=D',
        ]

        self.top += 1

        return commands

    def pop(self, segment, index):
        if self.top < self.MIN:
            raise Exception('Stackoverflow')

        segment = getattr(self, segment)

        commands = segment.load_addr(index)

        commands += [
            '@R15',
            'M=D',
        ]

        commands += [
            '@SP',
            'AM=M-1',
            'D=M',
            '@R15',
            'A=M',
        ]

        commands += segment.store()

        self.top -= 1

        return commands


class Function:

    def __init__(self):
        self.call_num = 0

    @property
    def return_address(self):
        return 'return-address.%d' % self.call_num

    def push_return_addr(self):
        commands = [
            '@%s' % self.return_address,
            'D=A',
            '@SP',
            'AM=M+1',
            'A=A-1',
            'M=D',
        ]

        return commands

    def push_context(self, label):
        commands = [
            '@%s' % label,
            'D=M',
            '@SP',
            'AM=M+1',
            'A=A-1',
            'M=D',
        ]

        return commands

    def set_arg(self, numArgs):
        commands = [
            # ARG = SP-n-5
            '@%d' % numArgs,
            'D=A',
            '@5',
            'D=D+A',
            '@SP',
            'D=M-D',
            '@ARG',
            'M=D',
        ]

        return commands

    def set_lcl(self):
        commands = [
            '@SP',
            'D=M',
            '@LCL',
            'M=D',
        ]

        return commands

    def goto_f(self, functionName):
        commands = [
            '@%s' % functionName,
            '0;JMP',
        ]

        return commands

    def set_return_addr(self):
        commands = [
            '(%s)' % self.return_address,
        ]

        self.call_num += 1

        return commands

    def restore_frame(self):
        # FRAME = LCL
        commands = [
            '@LCL',
            'D=M',
            '@R13',
            'M=D',
        ]

        return commands

    def restore_return_addr(self):
        commands = [
            # RET = *(FRAME-5)
            '@5',
            'A=D-A',
            'D=M',
            '@R14',
            'M=D',
        ]

        return commands

    def save_return_value(self):
        commands = [
            # *ARG = pop()
            '@SP',
            'AM=M-1',
            'D=M',
            '@ARG',
            'A=M',
            'M=D',
        ]
        return commands

    def restore_sp(self):
        commands = [
            # SP = ARG+1
            '@ARG',
            'D=M+1',
            '@SP',
            'M=D',
        ]

        return commands

    def restore_context(self, segment, index):
        commands = [
            '@R13',
            'AM=M-1',
            'D=M',
            '@%s' % segment,
            'M=D',
        ]

        return commands

    def return_to_caller(self):
        commands = [
            # goto RET
            '@R14',
            'A=M',
            '0;JMP',
        ]

        return commands


class VM:

    COMMANDTYPE = {
        'add':      'C_ARITHMETIC',
        'sub':      'C_ARITHMETIC',
        'neg':      'C_ARITHMETIC',
        'eq':       'C_ARITHMETIC',
        'gt':       'C_ARITHMETIC',
        'lt':       'C_ARITHMETIC',
        'and':      'C_ARITHMETIC',
        'or':       'C_ARITHMETIC',
        'not':      'C_ARITHMETIC',
        'push':     'C_PUSH',
        'pop':      'C_POP',
        'label':    'C_LABEL',
        'goto':     'C_GOTO',
        'if-goto':  'C_IF',
        'function': 'C_FUNCTION',
        'return':   'C_RETURN',
        'call':     'C_CALL',
    }

    SECOND_ARG = [
        'C_PUSH',
        'C_POP',
        'C_FUNCTION',
        'C_CALL',
    ]

    def __init__(self):
        self.stack = Stack()
        self.op_eq_label = 0
        self.op_lt_label = 0
        self.op_gt_label = 0
        self.func = Function()

    def op_add(self):
        commands = [
            '@SP',
            'AM=M-1',
            'D=M',
            'A=A-1',
            'M=M+D',
        ]

        return commands

    def op_sub(self):

        commands = [
            '@SP',
            'AM=M-1',
            'D=M',
            'A=A-1',
            'M=M-D',
        ]

        return commands

    def op_neg(self):
        commands = [
            '@SP',
            'A=M',
            'A=A-1',
            'M=-M',
        ]

        return commands

    def op_eq(self):
        commands = [
            '@SP',
            'AM=M-1',
            'D=M',
            'A=A-1',
            'D=M-D',
            'M=-1',
            ('@OP_EQ_%d' % self.op_eq_label),
            'D;JEQ',
            '@SP',
            'A=M-1',
            'M=0',
            ('(OP_EQ_%d)' % self.op_eq_label),
        ]

        self.op_eq_label += 1

        return commands

    def op_gt(self):
        commands = [
            '@SP',
            'AM=M-1',
            'D=M',
            'A=A-1',
            'D=M-D',
            'M=-1',
            ('@OP_GT_%d' % self.op_gt_label),
            'D;JGT',
            '@SP',
            'A=M-1',
            'M=0',
            ('(OP_GT_%d)' % self.op_gt_label),
        ]

        self.op_gt_label += 1

        return commands

    def op_lt(self):
        commands = [
            '@SP',
            'AM=M-1',
            'D=M',
            'A=A-1',
            'D=M-D',
            'M=-1',
            ('@OP_LT_%d' % self.op_lt_label),
            'D;JLT',
            '@SP',
            'A=M-1',
            'M=0',
            ('(OP_LT_%d)' % self.op_lt_label),
        ]

        self.op_lt_label += 1

        return commands

    def op_and(self):
        commands = [
            '@SP',
            'AM=M-1',
            'D=M',
            'A=A-1',
            'M=M&D',
        ]

        return commands

    def op_or(self):
        commands = [
            '@SP',
            'AM=M-1',
            'D=M',
            'A=A-1',
            'M=M|D',
        ]

        return commands

    def op_not(self):
        commands = [
            '@SP',
            'A=M',
            'A=A-1',
            'M=!M',
        ]

        return commands


class Parser:

    def __init__(self, source_file):
        self.filename = source_file.stem
        self.vm_code = source_file.open()
        self.line_command = None
        self.current_command = None
        # self.line_no = -1

    @property
    def hasMoreCommands(self):
        # in python '' means EOF, any line would have \n
        if self.line_command == '':
            return False
        else:
            return True

    def advance(self):

        self.line_command = self.vm_code.readline()

        self._clean_command()

    @property
    def is_command(self):
        if self.current_command == '':
            return False
        else:
            return True

    def _clean_command(self):
        comment_position = self.line_command.find('//')

        command = self.line_command[:comment_position]

        self.current_command = command.strip()

    @property
    def commandType(self):
        op_code = self.current_command.split()[0]

        return VM.COMMANDTYPE[op_code]

    @property
    def arg1(self):

        if self.commandType == 'C_RETURN':
            raise Exception("No argument")

        return self.current_command.split()[1]

    @property
    def arg2(self):

        if self.commandType not in VM.SECOND_ARG:
            raise Exception("No second argument")

        return int(self.current_command.split()[2])


class CodeWriter:

    def __init__(self, output_file):
        self.vm = VM()
        self.asm = output_file.open('w')
        self.current_file = None
        self.vm_name = None
        self.f_name = None

    def setFileName(self, filename):
        self.vm_name = filename

    def _showcode(self, line):
        print(line)
        self.asm.write(line + '\n')

    def writeArithmetic(self, command):

        commandType = self.vm.COMMANDTYPE.get(command)

        if commandType != 'C_ARITHMETIC':
            raise Exception('Not arithmetic operation')

        op = 'op_' + command
        method = getattr(self.vm, op)

        for line in method():
            self._showcode(line)

    def writePushPop(self, command, segment, index):

        if command not in ('C_POP', 'C_PUSH'):
            raise Exception('Not push or pop operation')

        if command == 'C_PUSH':
            if segment == 'static':
                self.vm.stack.set_static_segment(self.vm_name)
            for line in self.vm.stack.push(segment, index):
                self._showcode(line)
        else:
            if segment == 'static':
                self.vm.stack.set_static_segment(self.vm_name)
            for line in self.vm.stack.pop(segment, index):
                self._showcode(line)

    def writeInit(self):
        # Bootstrap code
        # Just do two things
        # Setup stack, call Sys.init
        asm_code = [
            # SP
            '@256',
            'D=A',
            '@SP',
            'M=D',
        ]

        for line in asm_code:
            self._showcode(line)

        # Sys.init
        self.writeCall('Sys.init', 0)

    def writeLabel(self, label):
        asm_code = [
            '(%s$%s)' % (self.f_name, label)
        ]
        for line in asm_code:
            self._showcode(line)

    def writeGoto(self, label):
        asm_code = [
            '@%s$%s' % (self.f_name, label),
            '0;JMP',
        ]
        for line in asm_code:
            self._showcode(line)

    def writeIf(self, label):
        asm_code = [
            '@SP',
            'AM=M-1',
            'D=M',
            '@%s$%s' % (self.f_name, label),
            'D;JNE',
        ]
        for line in asm_code:
            self._showcode(line)

    def writeCall(self, functionName, numArgs):
        asm_code = []

        asm_code = self.vm.func.push_return_addr()

        asm_code += self.vm.func.push_context('LCL')
        asm_code += self.vm.func.push_context('ARG')
        asm_code += self.vm.func.push_context('THIS')
        asm_code += self.vm.func.push_context('THAT')

        asm_code += self.vm.func.set_arg(numArgs)
        asm_code += self.vm.func.set_lcl()

        asm_code += self.vm.func.goto_f(functionName)
        asm_code += self.vm.func.set_return_addr()

        for line in asm_code:
            self._showcode(line)

    def writeReturn(self):

        asm_code = []

        asm_code += self.vm.func.restore_frame()
        asm_code += self.vm.func.restore_return_addr()
        asm_code += self.vm.func.save_return_value()

        asm_code += self.vm.func.restore_sp()
        asm_code += self.vm.func.restore_context('THAT', 1)
        asm_code += self.vm.func.restore_context('THIS', 2)
        asm_code += self.vm.func.restore_context('ARG', 3)
        asm_code += self.vm.func.restore_context('LCL', 4)

        asm_code += self.vm.func.return_to_caller()

        for line in asm_code:
            self._showcode(line)

    def writeFunction(self, functionName, numLocals):
        self.f_name = functionName

        asm_code = [
            '(%s)' % functionName,
        ]

        for i in range(numLocals):
            asm_code += [
                '@SP',
                'AM=M+1',
                'A=A-1'
                'M=0',
            ]

        for line in asm_code:
            self._showcode(line)

    def close(self):
        asm_code = [
            '(END)',
            '@END',
            '0;JMP',
        ]

        for line in asm_code:
            self._showcode(line)

        self.asm.close()


def process(writer, parser):

    writer.setFileName(parser.filename)

    while parser.hasMoreCommands:
        parser.advance()

        if not parser.is_command:
            continue

        if parser.commandType in ('C_PUSH', 'C_POP'):
            writer.writePushPop(
                parser.commandType,
                parser.arg1,
                parser.arg2)

        if parser.commandType == 'C_ARITHMETIC':
            writer.writeArithmetic(parser.current_command)

        if parser.commandType == 'C_IF':
            writer.writeIf(parser.arg1)

        if parser.commandType == 'C_LABEL':
            writer.writeLabel(parser.arg1)

        if parser.commandType == 'C_GOTO':
            writer.writeGoto(parser.arg1)

        if parser.commandType == 'C_FUNCTION':
            writer.writeFunction(parser.arg1, parser.arg2)

        if parser.commandType == 'C_RETURN':
            writer.writeReturn()

        if parser.commandType == 'C_CALL':
            writer.writeCall(parser.arg1, parser.arg2)


def main(source):

    print("Start Parsing...")

    src = Path(source)
    if not src.is_file() and not src.is_dir():
        raise Exception("Source Code not found.")

    if src.is_file():
        if src.suffix != '.vm':
            raise Exception("Source file is not vm")
        output_file = src.parent / src.name.replace('.vm', '.asm')
    else:
        output_file = src / (src.name + '.asm')

    writer = CodeWriter(output_file)

    writer.writeInit()

    if src.is_file():
        parser = Parser(src)
        process(writer, parser)
    else:
        for item in src.iterdir():
            if item.suffix == '.vm':
                parser = Parser(item)
                process(writer, parser)

    writer.close()

    print('Finish parsing.')


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
