class SymbolTable:

    KINDS = [
        'STATIC',
        'FIELD',
        'ARG',
        'VAR',
        'NONE',
    ]

    def __init__(self):
        self.class_scope = {
            '_static_index': 0,
            '_field_index': 0,
        }
        self.func_scope = None

        self.top_scope = self.class_scope
        self.current_scope = self.top_scope

    def startSubroutine(self):
        self.func_scope = {
            '_arg_index': 0,
            '_var_index': 0,
            }
        self.current_scope = self.func_scope

    def Define(self, name, _type, kind):
        scope = self.current_scope

        index_name = '_%s_index' % kind.lower()

        scope[name] = {
            'type': _type,
            'kind': kind,
            'index': scope[index_name]
        }
        
        scope[index_name] += 1
    
    def VarCount(self, kind):
        scope = self.current_scope

        index_name = '_%s_index' % kind.lower()

        count = scope.get(index_name, self.top_scope.get(index_name))

        return count

    def KindOf(self, name):
        scope = self.current_scope
        
        ident = scope.get(name, self.top_scope.get(name))

        if not ident:
            return None
        else:
            return ident.get('kind')
    
    def TypeOf(self, name):
        scope = self.current_scope
        
        ident = scope.get(name, self.top_scope.get(name))

        if not ident:
            return None
        else:
            return ident.get('type')

    def IndexOf(self, name):
        scope = self.current_scope
        
        ident = scope.get(name, self.top_scope.get(name))

        if not ident:
            return None
        else:
            return ident.get('index')