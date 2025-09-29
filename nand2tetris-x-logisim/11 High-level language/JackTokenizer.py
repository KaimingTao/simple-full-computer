class JackTokenizer:

    TOKEN_TYPE = [
        'KEYWORD',
        'SYMBOL',
        'IDENTIFIER',
        'INT_CONST',
        'STRING_CONST',
    ]

    KEYWORD_CONSTANT = [
        'true',
        'false',
        'null',
        'this',
    ]

    TYPE_KEYWORDS = [
        'int',
        'char',
        'boolean',
        ]

    FUNC_TYPE = (
            'constructor',
            'function',
            'method'
        )

    KEYWORDS = [
        'CLASS',
        'METHOD',
        'FUNCTION',
        'CONSTRUCTOR',
        'INT',
        'BOOLEAN',
        'CHAR',
        'VOID',
        'VAR',
        'STATIC',
        'FIELD',
        'LET',
        'DO',
        'IF',
        'ELSE',
        'WHILE',
        'RETURN',
        'TRUE',
        'FALSE',
        'NULL',
        'THIS',
    ]

    OP = {
        '+': 'ADD',
        '-': 'SUB',
        '*': 'Math.multiply',
        '/': 'Math.divide',
        '&': 'AND',
        '|': 'OR',
        '<': 'LT',
        '>': 'GT',
        '=': 'EQ',
    }

    UNARY_OP = {
        '-': 'NEG',
        '~': 'NOT',
    }

    SYMBOL = [
        '{',
        '}',
        '(',
        ')',
        '[',
        ']',
        '.',
        ',',
        ';',
        '+',
        '-',
        '*',
        '/',
        '&',
        '|',
        '<',
        '>',
        '=',
        '~',
    ]

    WHITE_CHARS = [
        " ",
        "\n",
        "\r\n",
        '\r',
    ]

    def __init__(self, input_file):
        self.file = input_file.open()
        self.current_token = None
        self.string_stat = 'NOT_STRING'
        self.line_no = 0


        self.reload = False
        self.previous_position = 0
        self.previous_string_stat = 'NOT_STRING'
        self.previous_line_no = 1

        self.identifier_info = {}

        self.if_counter = 0
        self.while_counter = 0

    def hasMoreTokens(self):
        position = self.file.tell()
        char = self.file.read(1)
        self.file.seek(position)

        if char == '':
            return False
        else:
            return True

    def save_current_position(self):
        self.previous_position = self.file.tell()
        self.previous_string_stat = self.string_stat
        self.previous_line_no = self.line_no

    def reload_previous_position(self):
        if self.reload:
            raise Exception('Can\' reload a token twice')

        self.file.seek(self.previous_position)
        self.string_stat = self.previous_string_stat
        self.line_no = self.previous_line_no

        self.reload = True

    def read_char(self):
        char = self.file.read(1)

        if char == '\n':
            self.line_no += 1
        
        return char

    def advance(self):
        self.reload = False

        characters = []

        while self.hasMoreTokens():

            char = self.read_char()

            # comment, a special case of symbol
            if char == '/':
                if self.string_stat == 'NOT_STRING':
                    next_char = self.read_char()

                    if next_char == '/':
                        self.skip_slash_comment()
                        characters = []
                        break
                    elif next_char == '*':
                        self.skip_star_comment()
                        characters = []
                        break

            # String
            if char == '\"':
                if self.string_stat == 'NOT_STRING':
                    self.string_stat = 'IS_STRING'
                    characters.append(char)
                    continue
                else: # self.string_stat == 'IS_STRING':
                    if characters[-1] == '\\':
                        characters.append(char)
                        continue

                    next_char = self.read_char()
                    if (next_char not in self.WHITE_CHARS) and (next_char not in self.SYMBOL):
                        characters.append(next_char)
                        raise Exception("String is not valid %s" % ''.join(characters))
                    else:
                        pos = self.file.tell() - 1
                        self.file.seek(pos)
                        self.string_stat = 'NOT_STRING'
                        characters.append(char)
                        break

            if self.string_stat == 'IS_STRING':
                characters.append(char)
                continue

            # symbol
            if char in self.SYMBOL:

                if len(characters) > 0:
                    # handle symbol next loop
                    pos = self.file.tell() - 1
                    self.file.seek(pos)
                    break
                else:
                    characters.append(char)
                    break


            if char not in self.WHITE_CHARS:
                characters.append(char)
            else:
                break

        token = ''.join(characters).strip()

        if token != '':
            # print(repr(token))
            self.current_token = token
        else:
            self.current_token = None

    def skip_slash_comment(self):

        comments = []

        while self.hasMoreTokens():
            char = self.read_char()

            if char == '\n':
                break

            comments.append(char)

        comments = ''.join(comments).strip()
        # print(self.line_no, comments)
    
    def skip_star_comment(self):
        comments = []

        char = self.read_char()
        if char != '*':
            comments.append(char)

        while self.hasMoreTokens():
            char = self.read_char()

            if char == '*':
                next_char = self.read_char()
                if next_char != '/':
                    comments.append(char)
                    comments.append(next_char)
                    continue
                else:
                    break
                
            comments.append(char)

        comments = ''.join(comments).strip()
        # print(self.line_no, comments)

    @property
    def tokenType(self):
        token = self.current_token

        if token in self.SYMBOL:
            return 'SYMBOL'
        
        if token.upper() in self.KEYWORDS:
            return 'KEYWORD'

        if token.isdigit():
            return 'INT_CONST'

        if token.startswith('"') and token.endswith('"'):
            return 'STRING_CONST'
        
        return 'IDENTIFIER'

    @property
    def keyWord(self):
        if self.tokenType == 'KEYWORD':
            return self.current_token

    @property
    def symbol(self):
        if self.tokenType == 'SYMBOL':
            return self.current_token
    
    @property
    def identifier(self):
        if self.tokenType == 'IDENTIFIER':
            return self.current_token

    @property
    def intVal(self):
        if self.tokenType == 'INT_CONST':
            return int(self.current_token)
    
    @property
    def stringVal(self):
        if self.tokenType == 'STRING_CONST':
            return self.current_token[1:-1]