from io import StringIO

class VMWriter:

    SEGMENTS = {
        'CONST': 'constant',
        'ARG': 'argument',
        'VAR': 'local',
        'STATIC': 'static',
        'FIELD': 'this',
        'THAT': 'that',
        'POINTER': 'pointer',
        'TEMP': 'temp',
    }

    def __init__(self, output):
        if output.suffix == '.vm':
            self.output = output.open('w')
        else:
            self.output = StringIO()
        
    def writePush(self, segment, index):
        vm_code = 'push %s %s\n' % (self.SEGMENTS.get(segment), index)

        self.output.write(vm_code)

    def writePop(self, segment, index):
        vm_code = 'pop %s %s\n' % (self.SEGMENTS.get(segment), index)

        self.output.write(vm_code)

    def writeArithmetic(self, command):
        vm_code = '%s\n' % command.lower()

        self.output.write(vm_code)

    def writeLabel(self, label):
        vm_code = 'label %s\n' % label

        self.output.write(vm_code)

    def writeGoto(self, label):
        vm_code = 'goto %s\n' % label

        self.output.write(vm_code)

    def writeIf(self, label):
        vm_code = 'if-goto %s\n' % label

        self.output.write(vm_code)

    def writeCall(self, name, nArgs):
        vm_code = 'call %s %s\n' % (name, nArgs)

        self.output.write(vm_code)

    def writeFunction(self, name, nLocals):
        vm_code = 'function %s %s\n' % (name, nLocals)
        
        self.output.write(vm_code)
    
    def writeReturn(self):
        self.output.write('return\n')
    
    def close(self):
        self.output.close()