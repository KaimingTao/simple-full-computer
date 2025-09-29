from functools import wraps
from io import StringIO
import pprint

from SymbolTable import SymbolTable
from VMWriter import VMWriter


pp = pprint.PrettyPrinter(indent=4)


def block(block_name):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            obj = args[0]

            obj.write_start_block(block_name)
            func(*args, **kwargs)
            obj.write_end_block(block_name)
        
        return wrapper
    
    return decorator


def identifier_collector(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        obj = args[0]

        current_handler = func.__name__

        if current_handler == 'compileClass':
            category = 'class'
            kind = None
        elif current_handler == 'compileClassVarDec':
            obj.next_token()

            category = obj.tokenizer.keyWord
            kind = category.upper()

            obj.put_token_back()
        elif current_handler == 'compileSubroutine':
            category = 'subroutine'
            kind = None
        elif current_handler == 'compileVarDec':
            category = 'var'
            kind = 'VAR'
        elif current_handler == 'compileParameterList':
            category = 'argument'
            kind = 'ARG'
        else:
            obj.SemanticsError()

        obj.tokenizer.identifier_info['category'] = category
        obj.tokenizer.identifier_info['kind'] = kind

        func(*args, **kwargs)

        obj.tokenizer.identifier_info = {}
    
    return wrapper


class CompilationEngine:

    def __init__(self, tokenizer, output):
        self.tokenizer = tokenizer

        if output.suffix == '.xml':
            self.output = output.open('w')
        else:
            self.output = StringIO()            
        self._indent = 0

        self.ast = []
        self.ast_cursor = self.ast
        self.ast_frame = []
        
        self.simple_ident = True
        self.symbol_table = SymbolTable()

        self.vm_writer = VMWriter(output)

    def work(self):
        # self.output_token()
        self.compileClass()

    def output_token(self):

        self.write_start_tag('tokens')
        self.write_newline()

        while self.tokenizer.hasMoreTokens():

            self.tokenizer.advance()

            if self.tokenizer.current_token is None:
                continue
            
            if self.tokenizer.tokenType == 'KEYWORD':
                self.write('keyword', self.tokenizer.keyWord)
            
            if self.tokenizer.tokenType == 'SYMBOL':
                self.write('symbol', self.tokenizer.symbol)
            
            if self.tokenizer.tokenType == 'IDENTIFIER':
                self.write('identifier', self.tokenizer.identifier)
            
            if self.tokenizer.tokenType == 'INT_CONST':
                self.write('integerConstant', self.tokenizer.intVal)
            
            if self.tokenizer.tokenType == 'STRING_CONST':
                self.write('stringConstant', self.tokenizer.stringVal)

            # print(self.tokenizer.current_token, self.tokenizer.tokenType)
    
        self.write_end_tag('tokens')
        self.write_newline()

    def SyntaxError(self):
        raise Exception(
            'Jack Syntax Error, File: %s, line: %d, token: %s' % (
                self.tokenizer.file.name,
                self.tokenizer.line_no,
                self.tokenizer.current_token
                )
        )
    
    def SemanticsError(self):
        raise Exception(
            'Jack Semantics Error, File: %s, line: %d, token: %s' % (
                self.tokenizer.file.name,
                self.tokenizer.line_no,
                self.tokenizer.current_token
                )
        )

    def write(self, tag, content):

        self.ast_cursor.append(
            (tag, content)
        )

        self.write_indent()
        self.write_start_tag(tag)

        if tag == 'symbol':
            content = self.convert_symbol(content)

        self.write_content(content)
        self.write_end_tag(tag)
        self.write_newline()
    
    def write_start_block(self, block_name):
        self.write_indent()
        self.write_start_tag(block_name)
        self.write_newline()
        self.indent()

        self.ast_frame.append(self.ast_cursor)
        next_cursor = []
        self.ast_cursor.append(
            (block_name, next_cursor)
        )
        self.ast_cursor = next_cursor

        # pp.pprint(self.ast)

    def write_end_block(self, block_name):
        self.unindent()
        self.write_indent()
        self.write_end_tag(block_name)
        self.write_newline()

        self.ast_cursor = self.ast_frame.pop()

        # pp.pprint(self.ast)
        
    def write_indent(self):
        self.output.write(' ' * self._indent * 2)

    def write_start_tag(self, tag):
        self.output.write('<%s>' % tag)

    def write_content(self, content):
        self.output.write(' %s ' % content)

    def write_end_tag(self, tag):
        self.output.write('</%s>' % tag)

    def write_newline(self):
        self.output.write('\r\n')

    def convert_symbol(self, symbol):
        if symbol == '<': symbol = '&lt;'
        if symbol == '>': symbol = '&gt;'
        if symbol == '"': symbol = '&quot;'
        if symbol == '&': symbol = '&amp;'

        return symbol

    def indent(self):
        self._indent += 1

    def unindent(self):
        if self._indent == 0:
            return
        self._indent -= 1

    def next_token(self):

        self.tokenizer.save_current_position()

        while self.tokenizer.hasMoreTokens():
            self.tokenizer.advance()

            if self.tokenizer.current_token is None:
                continue
            else:
                break
    
    def put_token_back(self):

        self.tokenizer.reload_previous_position()

    def write_keyword(self):
        self.next_token()
        if self.tokenizer.tokenType == 'KEYWORD':
            self.write('keyword', self.tokenizer.keyWord)
        else:
            self.SyntaxError()
    
    def write_symbol(self):
        self.next_token()
        if self.tokenizer.tokenType == 'SYMBOL':
            self.write('symbol', self.tokenizer.symbol)
        else:
            self.SyntaxError()
        
    def write_identifier(self):
        self.next_token()

        if self.tokenizer.tokenType == 'IDENTIFIER':

            name = self.tokenizer.identifier
            
            category = self.tokenizer.identifier_info.get('category')
            if not category:
                defined = self.tokenizer.identifier_info['defined'] = 'used'
            else:
                defined = self.tokenizer.identifier_info['defined'] = 'defined'
            
            kind = self.tokenizer.identifier_info.get('kind')
            _type = self.tokenizer.identifier_info.get('type')

            if kind and _type: 
                self.symbol_table.Define(name, _type, kind)
            else:
                kind = self.symbol_table.KindOf(name)
                _type = self.symbol_table.TypeOf(name)

            index = self.symbol_table.IndexOf(name)

            # print(
            #     name,
            #     category,
            #     defined,
            #     kind, 
            #     _type, 
            #     index)            

            if self.simple_ident:
                self.write('identifier', name)
            else:
                self.write_start_block('identifier')
                self.write('name', name)
                self.write('category', category)
                self.write('defined', defined)
                self.write('kind', kind)
                self.write('type', _type)
                self.write('index', index)

                self.write_end_block('identifier')
        else:
            self.SyntaxError()

    def write_int(self):
        self.next_token()
        if self.tokenizer.tokenType == 'INT_CONST':
            self.write('integerConstant', self.tokenizer.intVal)
        else:
            self.SyntaxError()

    def write_string(self):
        self.next_token()
        if self.tokenizer.tokenType == 'STRING_CONST':
            self.write('stringConstant', self.tokenizer.stringVal)
        else:
            self.SyntaxError()

    def get_class(self, attribute):
        # class name
        if attribute == 'name':
            attribute = 'identifier'

        for (tag, _class) in self.ast:
            for (tag, value) in _class:
                if tag == attribute:
                    break

        return value
    
    def find_func_frame(self):
        current_frame = self.ast_cursor

        first_token = current_frame[0]

        if first_token[0] == 'keyword' and first_token[1] in self.tokenizer.FUNC_TYPE:
            return current_frame
        
        frame_num = len(self.ast_frame)
        while True:
            if frame_num == 0:
                raise self.SemanticsError()

            current_frame = self.ast_frame[frame_num - 1]
            first_token = current_frame[0]

            if first_token[0] == 'keyword' and first_token[1] in self.tokenizer.FUNC_TYPE:
                break      
            else:
                frame_num -= 1
        
        return current_frame

    def get_func(self, attribute):
        func_frame = self.find_func_frame()

        if attribute == 'name':
            (_, name) = func_frame[2]
            return name
        if attribute == 'return_type':
            (_, return_type) = func_frame[1]
            return return_type
        if attribute == 'func_type':
            (_, func_type) = func_frame[0]
            return func_type
        else:
            raise self.SemanticsError()

    @identifier_collector
    @block('class')
    def compileClass(self):
        # class keyword
        self.write_keyword()

        # className
        self.write_identifier()

        # class body
        self.compileClassBody()

    def compileClassBody(self):
        # {
        self.write_symbol()

        # classVarDec* subroutineDec*
        while True:
            self.next_token()

            # }, detector
            if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == '}':
                self.put_token_back()
                break
            
            # classVarDec
            if self.tokenizer.keyWord in (
                        'static',
                        'field',
                    ):
                self.put_token_back()
                self.compileClassVarDec()
                continue

            # subroutineDec
            if self.tokenizer.keyWord in self.tokenizer.FUNC_TYPE:
                self.put_token_back()
                self.compileSubroutine()
                continue

        # }
        self.write_symbol()

    @identifier_collector
    @block('classVarDec')
    def compileClassVarDec(self):
        # static | field
        self.write_keyword()

        # type
        self.compileType()

        # varNamevarName (',' varName)* 
        while True:
            self.next_token()

            # ; detector
            if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == ';':
                self.put_token_back()
                break
            
            # ,
            if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == ',':
                self.put_token_back()
                self.write_symbol()
                continue
            
            # varName
            self.put_token_back()
            self.write_identifier()
        
        # ;
        self.write_symbol()
    
    def compileType(self):
        self.next_token()

        if self.tokenizer.tokenType == 'KEYWORD' and self.tokenizer.keyWord in self.tokenizer.TYPE_KEYWORDS:
            self.put_token_back()
            self.write_keyword()

            self.tokenizer.identifier_info['type'] = self.tokenizer.keyWord
        elif self.tokenizer.tokenType == 'IDENTIFIER':
            self.put_token_back()
            self.write_identifier()

            self.tokenizer.identifier_info['type'] = self.tokenizer.identifier
        else:
            self.SyntaxError()
        
    def TypeOrVoid(self):
        self.next_token()
        
        if self.tokenizer.tokenType == 'KEYWORD' and self.tokenizer.keyWord == 'void':
            self.put_token_back()
            self.write_keyword()
        else:
            self.put_token_back()
            self.compileType()

    @identifier_collector
    @block('subroutineDec')
    def compileSubroutine(self):
        self.symbol_table.startSubroutine()

        # constructor | function | method
        self.write_keyword()

        # 'void' | type
        self.TypeOrVoid()

        # subroutinename
        self.write_identifier()

        # ( parameterList )
        self.compileParameter()

        # subroutineBody
        self.compileSubroutineBody()        

    def compileParameter(self):
        # (
        self.write_symbol()

        # ((type varName) (',' type varName)*))?
        self.compileParameterList()

        # )
        self.write_symbol()

    @identifier_collector
    @block('parameterList')
    def compileParameterList(self):
        
        while True:
            self.next_token()

            # ) detector
            if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == ')':
                self.put_token_back()
                break
            
            # ,
            if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == ',':
                self.put_token_back()
                self.write_symbol()
                continue
            
            # type
            self.put_token_back()
            self.compileType()

            # varName
            self.write_identifier()

    @block('subroutineBody')
    def compileSubroutineBody(self):
        # {
        self.write_symbol()

        # varDec*
        while True:
            self.next_token()
            # var detector
            if self.tokenizer.tokenType != 'KEYWORD' or self.tokenizer.keyWord != 'var':
                self.put_token_back()
                break
            else:
                # varDec
                self.put_token_back()
                self.compileVarDec()

        # VM Code
        real_func_name = '%s.%s' % (
            self.get_class('name'),
            self.get_func('name')
            )
        self.vm_writer.writeFunction(
            real_func_name,
            self.symbol_table.VarCount('VAR')
        )

        # VM Code
        func_type = self.get_func('func_type')
        if func_type == 'constructor':
            self.vm_writer.writePush("CONST", self.symbol_table.VarCount('field'))
            self.vm_writer.writeCall('Memory.alloc', 1)
            self.vm_writer.writePop('POINTER', 0)
        elif func_type == 'method':
            self.vm_writer.writePush('ARG', 0)
            self.vm_writer.writePop('POINTER', 0)
        else:
            pass
        
        # statements
        self.compileStatements()

        # }
        self.write_symbol()

    def compileSubroutineCall(self, identifier_ok=False):
        # subroutineName | className | varName
        if not identifier_ok:
            self.write_identifier()

        # .subroutineName
        self.next_token()
        if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == '.':
            self.put_token_back()
            self.write_symbol()
            self.write_identifier()
        else:
            self.put_token_back()

        # VM Code
        call_name = []
        argument_num = 0
        for (tag, value) in self.ast_cursor:
            if tag == 'identifier':
                call_name.append(value)
                continue

        # Method call Class | Object
        if len(call_name) == 2:
            first_name = call_name[0]
            _type = self.symbol_table.TypeOf(first_name)
            # Local object method call, find class
            if _type:
                call_name[0] = _type
                # this
                self.vm_writer.writePush(
                    self.symbol_table.KindOf(first_name),
                    self.symbol_table.IndexOf(first_name)
                    )
                argument_num += 1
            else:  # Global Class method call
                pass
        
        # Call this.methods
        if len(call_name) == 1:
            class_name = self.get_class('name')
            call_name.insert(0, class_name)
            self.vm_writer.writePush('POINTER', 0)
            argument_num += 1


        # (
        self.write_symbol()

        # expressionList
        self.compileExpressionList()

        # )
        self.write_symbol()

        # VM Code
        for (tag, value) in self.ast_cursor:
            if tag == 'expressionList':
                expressionList = value
                for (t, v) in expressionList:
                    if t == 'expression':
                        argument_num += 1


        self.vm_writer.writeCall('.'.join(call_name) , argument_num)

    @identifier_collector
    @block('varDec')
    def compileVarDec(self):
        # var keyword
        self.write_keyword()

        # type
        self.compileType()

        while True:
            self.next_token()

            # ; detector
            if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == ';':
                self.put_token_back()
                break
            
            # ,
            if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == ',':
                self.put_token_back()
                self.write_symbol()
                continue

            # varName
            self.put_token_back()
            self.write_identifier()
        
        # ;
        self.write_symbol()

    @block('statements')
    def compileStatements(self):

        # statements
        while True:
            self.next_token()

            # } detector
            if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == '}':
                self.put_token_back()
                break
            
            # statement
            self.put_token_back()
            self.compileOneStatement()

    def compileOneStatement(self):
        self.next_token()

        # letStatement
        if self.tokenizer.keyWord == 'let':
            self.put_token_back()
            self.compileLet()
            return
        
        # ifStatement
        if self.tokenizer.keyWord == 'if':
            self.put_token_back()
            self.compileIf()
            return
        
        # whileStatement
        if self.tokenizer.keyWord == 'while':
            self.put_token_back()
            self.compileWhile()
            return
        
        # doStatement
        if self.tokenizer.keyWord == 'do':
            self.put_token_back()
            self.compileDo()
            return
        
        # returnStatement
        if self.tokenizer.keyWord == 'return':
            self.put_token_back()
            self.compileReturn()
            return

    @block('doStatement')
    def compileDo(self):
        # do

        self.write_keyword()

        # subroutineCall
        self.compileSubroutineCall()

        # ;
        self.write_symbol()

        # VM Code
        self.vm_writer.writePop('TEMP', 0)

    @block('letStatement')
    def compileLet(self):
        # let
        self.write_keyword()

        # varName
        self.write_identifier()

        ## VM Code
        varName = self.tokenizer.identifier
        is_array = False

        # ([ expression ])?
        self.next_token()
        if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == '[':
            self.put_token_back()
            # [
            self.write_symbol()

            # VM Code
            is_array = True

            kind = self.symbol_table.KindOf(varName)
            index = self.symbol_table.IndexOf(varName)
            self.vm_writer.writePush(kind, index)

            # expression
            self.compileExpression()

            # VM Code
            self.vm_writer.writeArithmetic('ADD')
            self.vm_writer.writePop('POINTER', 1)

            # ]
            self.write_symbol()
        else:
            self.put_token_back()
        
        # = 
        self.write_symbol()

        # expression
        self.compileExpression()

        # ;
        self.write_symbol()

        # VM Code
        if is_array:
            self.vm_writer.writePop('THAT', 0)
        else:
            kind = self.symbol_table.KindOf(varName)
            index = self.symbol_table.IndexOf(varName)
            self.vm_writer.writePop(kind, index)
    
    @block('whileStatement')
    def compileWhile(self):
        # VM Code
        while_start_label = 'WHILE_START_%d' % self.tokenizer.while_counter
        while_end_label = 'WHILE_END_%d' % self.tokenizer.while_counter
        self.tokenizer.while_counter += 1

        # while
        self.write_keyword()

        # VM Code
        self.vm_writer.writeLabel(while_start_label)

        # (
        self.write_symbol()

        # expression
        self.compileExpression()

        # )
        self.write_symbol()

        # VM Code
        self.vm_writer.writeArithmetic('NOT')
        self.vm_writer.writeIf(while_end_label)

        # {
        self.write_symbol()

        # statements
        self.compileStatements()

        # )
        self.write_symbol()

        # VM Code
        self.vm_writer.writeGoto(while_start_label)
        self.vm_writer.writeLabel(while_end_label)

    @block('returnStatement')
    def compileReturn(self):
        # return
        self.write_keyword()

        # expression?

        self.next_token()
        if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == ';':
            self.put_token_back()
        else:
            self.put_token_back()
            self.compileExpression()

        # ;
        self.write_symbol()

        # VM Code
        return_type = self.get_func('return_type')
        if return_type == 'void':
            self.vm_writer.writePush('CONST', 0)
        else:
            pass
        self.vm_writer.writeReturn()

    @block('ifStatement')
    def compileIf(self):
        # VM Code
        true_label = 'IF_TRUE_%d' % self.tokenizer.if_counter
        else_label = 'IF_ELSE_%d' % self.tokenizer.if_counter
        end_label = 'IF_END_%d' % self.tokenizer.if_counter
        self.tokenizer.if_counter += 1

        # if
        self.write_keyword()

        # (
        self.write_symbol()

        # expression
        self.compileExpression()

        # )
        self.write_symbol()

        # VM Code
        self.vm_writer.writeIf(true_label)
        self.vm_writer.writeGoto(else_label)

        # VM Code
        self.vm_writer.writeLabel(true_label)

        # {
        self.write_symbol()

        # statements
        self.compileStatements()

        # }
        self.write_symbol()

        # VM Code
        self.vm_writer.writeGoto(end_label)
        self.vm_writer.writeLabel(else_label)

        # ('else' '{' statements '}')?
        self.next_token()
        if self.tokenizer.tokenType == 'KEYWORD' and self.tokenizer.keyWord == 'else':
            self.put_token_back()

            # else
            self.write_keyword()

            # {
            self.write_symbol()

            # statements
            self.compileStatements()

            # }
            self.write_symbol()
        else:
            self.put_token_back()
        
        # VM Code
        self.vm_writer.writeLabel(end_label)

    @block('expressionList')
    def compileExpressionList(self):
        while True:
            self.next_token()

            # } detector, end of expression list
            if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == ')':
                self.put_token_back()
                break

            if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == ',':
                self.put_token_back()
                self.write_symbol()
                continue
            
            self.put_token_back()
            self.compileExpression()

    @block('expression')
    def compileExpression(self):
        # term
        self.compileTerm()

        # (op term)*
        while True:
            self.next_token()

            # end of expression detector
            # ')', ']', ';', ','
            if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol in (')', ']', ';', ','):
                self.put_token_back()
                break

            # op 
            if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol in self.tokenizer.OP.keys():
                self.put_token_back()
                self.write_symbol()

                # VM Code
                symbol = self.tokenizer.symbol

                self.compileTerm()

                # VM Code
                if symbol in ('*', '/'):
                    self.vm_writer.writeCall(self.tokenizer.OP[symbol], 2)
                else:
                    self.vm_writer.writeArithmetic(self.tokenizer.OP[symbol])

    @block('term')
    def compileTerm(self):
        self.next_token()

        # integerConstant
        if self.tokenizer.tokenType == 'INT_CONST':
            self.put_token_back()
            self.write_int()

            # VM Code
            self.vm_writer.writePush('CONST', self.tokenizer.intVal)

            return
        
        # stringConstant
        if self.tokenizer.tokenType == 'STRING_CONST':
            self.put_token_back()
            self.write_string()

            # VM Code
            string_literal = self.tokenizer.stringVal
            self.vm_writer.writePush('CONST', len(string_literal))
            self.vm_writer.writeCall('String.new', 1)
            for char in string_literal:
                self.vm_writer.writePush('CONST', ord(char))
                self.vm_writer.writeCall('String.appendChar', 2)

            return

        # keywordConstant
        if self.tokenizer.tokenType == 'KEYWORD' and self.tokenizer.keyWord in self.tokenizer.KEYWORD_CONSTANT:
            self.put_token_back()
            self.write_keyword()

            # VM Code
            keyword = self.tokenizer.keyWord

            if keyword == 'true':
                self.vm_writer.writePush('CONST', 0)
                self.vm_writer.writeArithmetic('NOT')
            elif keyword == 'false':
                self.vm_writer.writePush('CONST', 0)
            elif keyword == 'null':
                self.vm_writer.writePush('CONST', 0)
            elif keyword == 'this':
                self.vm_writer.writePush('POINTER', 0)
            else:
                raise self.SemanticsError()
            return
        
        # varName | varName '[' expression ']' | subroutineCall
        if self.tokenizer.tokenType == 'IDENTIFIER':
            self.put_token_back()
            self.write_identifier()

            # VM Code
            ident_name = self.tokenizer.identifier

            # '[' expression ']' 
            self.next_token()
            if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == '[':
                self.put_token_back()

                # [
                self.write_symbol()

                # VM Code
                kind = self.symbol_table.KindOf(ident_name)
                index = self.symbol_table.IndexOf(ident_name)
                if kind == 'ARG' and self.get_func('func_type') == 'method':
                    index += 1
                self.vm_writer.writePush(kind, index)

                # expression
                self.compileExpression()

                # VM Code
                self.vm_writer.writeArithmetic('ADD')
                self.vm_writer.writePop('POINTER', 1)
                self.vm_writer.writePush('THAT', 0)

                # ]
                self.write_symbol()
            elif self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == '.':
                # subroutineCall
                self.put_token_back()
                self.compileSubroutineCall(True)
            else:
                # VM Code
                kind = self.symbol_table.KindOf(ident_name)
                index = self.symbol_table.IndexOf(ident_name)
                if kind == 'ARG' and self.get_func('func_type') == 'method':
                    index += 1
                self.vm_writer.writePush(kind, index)

                self.put_token_back()
            return

        # '(' expression ')'
        if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol == '(':
            self.put_token_back()

            # (
            self.write_symbol()

            # expression
            self.compileExpression()

            # )
            self.write_symbol()
            return

        # unaryOp term
        if self.tokenizer.tokenType == 'SYMBOL' and self.tokenizer.symbol in self.tokenizer.UNARY_OP.keys():
            self.put_token_back()
            self.write_symbol()

            # VM Code
            symbol = self.tokenizer.symbol

            self.compileTerm()

            # VM Code
            self.vm_writer.writeArithmetic(self.tokenizer.UNARY_OP[symbol])

            return