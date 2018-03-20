import ply.lex as lex

class MyLexer(object):

    reserved = {
        'if'        : 'IF',
        'then'      : 'THEN',
        'else'      : 'ELSE',
        'while'     : 'WHILE',
        'include'   : 'INCLUDE',
        'iostream'  : 'IOSTREAM',
        'int'       : 'INTEGER',
        'float'     : 'FLOAT',
        'char'      : 'CHARACTER',
        'double'    : 'DOUBLE',
        'main'      : 'MAIN',
        'return'    : 'RETURN',
        'using'     : 'USING',
        'namespace' : 'NAMESPACE',
        'std'       : 'STD'
    }

    # List of token names.   This is always required
    tokens = (
        'EQUALS',
        'NUMBER',
        'PLUS',
        'MINUS',
        'TIMES',
        'DIVIDE',
        'LPAREN',
        'RPAREN',
        'LANGULAR',
        'RANGULAR',
        'IDENTIFIER',
        'KEYWORD',
        'HASH',
        'BLOCKOPEN',
        'BLOCKCLOSE',
        'SEMICOLON',
        'COMMA'
    )

    # Regular expression rules for simple tokens
    t_PLUS      = r'\+'
    t_MINUS     = r'-'
    t_TIMES     = r'\*'
    t_DIVIDE    = r'/'
    t_LPAREN    = r'\('
    t_RPAREN    = r'\)'
    t_LANGULAR  = r'<'
    t_RANGULAR  = r'>'
    t_HASH      = r'\#'
    t_BLOCKOPEN = r'{'
    t_BLOCKCLOSE= r'}'
    t_SEMICOLON = r';'
    t_COMMA = r','
    
    # A regular expression rule with some action code
    # Note addition of self parameter since we're in a class
    def t_NUMBER(self,t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_IDENTIFIER(self, t):
        # This checks if the lexeme is an identifier or a keyword and returns accordingly
        r'[a-zA-Z_][a-zA-Z0-9_\-]*'

        if(t.value in list(self.reserved.keys())):
            t.type = "KEYWORD"

        return(t)

    def t_COMMENTS(self, t):
        # Match and ignore comments
        # Just handling single line comments for now!
        r'//.*'
        print("Comment = ", t.value, "----> Token not generated!!")

    # Define a rule so we can track line numbers
    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # A string containing ignored characters (spaces and tabs)
    t_ignore  = ' \t'

    # Error handling rule
    def t_error(self,t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Build the lexer
    def build(self,**kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    # Test it output
    def test(self,data):
        self.lexer.input(data)
        while True:
             tok = self.lexer.token()
             if not tok:
                 break
             print(tok)

# create the lexer
m = MyLexer()

# Build the lexer
m.build()


if __name__ == "__main__":
    # Build the lexer and try it out
    m = MyLexer()

    # Build the lexer
    m.build()

    with open("processed hello_world.cpp", "r") as f:
        data = f.read().strip()


    print("C++ CODE\n")
    print(data)
    print("\n")
    print("TOKENS\n\n")
    m.test(data)     # Test it
