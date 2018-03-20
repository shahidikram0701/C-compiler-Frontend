import os
import ply.yacc as yacc

#import lexer and tokens from the lexer
from myLex import MyLexer
m = MyLexer()
tokens = m.tokens

print(tokens)

class MyParser():
    def p_EPSILON(self, p):
        'EPSILON                            :'
        pass

    def p_PROGRAM(self, p):
        '''PROGRAM                          : GLOBAL_STATEMENT MAIN GLOBAL_STATEMENT'''

    def p_GLOBAL_STATEMENT(self, p):
        '''GLOBAL_STATEMENT                 : EXPRESSION_STATEMENT
                                            | DECLARATION_STATEMENT
                                            | EPSILON'''

    def p_MAIN(self, p):
        '''MAIN                             : int main '(' ')' '{' STATEMENT return 0 ';' '}' '''   # tokens to be added here for int main return 0 ; and braces

    def p_STATEMENT(self,p):
        '''STATEMENT                        : EXPRESSION_STATEMENT
                                            | DECLARATION_STATEMENT
                                            | SELECTION_STATEMENT
                                            | JUMP_STATEMENT
                                            | ITERATION_STATEMENT
                                            | LOCAL_DECLARATION_STATEMENT'''

    def p_LOCAL_DECLARATION_STATEMENT(self, p):
        '''LOCAL_DECLARATION_STATEMENT      : LOCAL_DECLARATION'''

    def p_EXPRESSION_STATEMENT(self, p):
        '''EXPRESSION_STATEMENT             : EXPRESSION ;
                                            | ';' ''' # add token for semicolon

    def p_COMPOUND_STATEMENT(self, p):
        '''COMPOUND_STATEMENT               : '{' STATEMENT_LIST '}'
                                            | '{' '}' ''' # add tokens for braces

    def p_STATEMENT_LIST(self, p):
        '''STATEMENT_LIST                   : STATEMENT
                                            | STATEMENT_LIST STATEMENT'''

    def p_ITERATION_STATEMENT(self,p):
        '''ITERATION_STATEMENT              : while '(' EXPRESSION ')' STATEMENT
                                            | for '(' FOR_INIT_STATEMENT ';' EXPRESSION ';' EXPRESSION ')' STATEMENT
                                            | for '(' FOR_INIT_STATEMENT ';' EXPRESSION ')' STATEMENT
                                            | for '(' FOR_INIT_EXPRESSION ';' ')' STATEMENT
                                            | for '(' FOR_INIT_STATEMENT ';' ')' STATEMENT''' #add tokens for for, while, small brackets

    def p_SELECTION_STATEMENT(self,p):
        '''SELECTION_STATEMENT              : if '(' EXPRESSION ')' STATEMENT
                                            | if '(' EXPRESSION ')' STATEMENT else STATEMENT ''' #add tokens for if, else

    def p_FOR_INIT_STATEMENT(self,p):
        '''FOR_INIT_STATEMENT               : EXPRESSION_STATEMENT
                                            | DECLARATION_STATEMENT'''

    def p_JUMP_STATEMENT(self,p):
        '''JUMP_STATEMENT                   : break ';'
                                            | continue ';'
                                            | return EXPRESSION ';'
                                            | return ';' ''' #add tokens for break, return, continue
    def p_DECLARATION_STATEMENT(self,p):
        '''DECLARATION_STATEMENT            : DECLARATION'''

    def p_CLASS_NAME(self, p):
        '''CLASS_NAME                       : identifier''' # token for identifier

    # simple escape sequence check out later

    #***************************************************EXPRSSION**********************************************************************

    def p_EXPRESSION(self,p):   # see this   what here??
        '''EXPRESSION                       : ASSIGNMENT_EXPRESSION
                                            | EXPRESSION ',' ASSIGNMENT_EXPRESSION'''
    def p_ASSIGNMENT_EXPRESSION(self,p):
        '''ASSIGNMENT_EXPRESSION            : CONDITIONAL_EXPRESSION
                                            | UNARY_EXPRESSION ASSIGNMENT_OPERATOR ASSIGNMENT_EXPRESSION'''

    def p_ASSIGNMENT_OPERATOR(self,p):
        '''ASSIGNMENT_OPERATOR              : equal
                                            | star_equal
                                            | slash_equal
                                            | mod_equal
                                            | plus_equal
                                            | minus_equal
                                            | left_shift_equal
                                            | right_shift_equal
                                            | ampersand_equal
                                            | cap_equal
                                            | pipe_equal''' # tokens for these

    def p_CONDITIONAL_EXPRESSION(self,p):
        '''CONDITIONAL_EXPRESSION           : LOGICAL_OR_EXPRESSION
                                            | LOGICAL_OR_EXPRESSION '?' EXPRESSION ':' CONDITIONAL_EXPRESSION'''
    def p_LOGICAL_OR_EXPRESSION(self,p):
        '''LOGICAL_OR_EXPRESSION            : LOGICAL_AND_EXPRESSION
                                            | LOGICAL_OR_EXPRESSION pipe_pipe LOGICAL_AND_EXPRESSION''' # add token for or
    def p_LOGICAL_AND_EXPRESSION(self,p):
        '''LOGICAL_AND_EXPRESSION           : INCLUSIVE_OR_EXPRESSION
                                            | LOGICAL_AND_EXPRESSION ampersand_ampersand INCLUSIVE_OR_EXPRESSION''' # add token for and

    def p_INCLUSIVE_OR_EXPRESSION(self,p):
        '''INCLUSIVE_OR_EXPRESSION          : EXCLUSIVE_OR_EXPRESSION
                                            | INCLUSIVE_OR_EXPRESSION '|' EXCLUSIVE_OR_EXPRESSION''' #check with '|' token

    def p_EXCLUSIVE_OR_EXPRESSION(self,p):
        '''EXCLUSIVE_OR_EXPRESSION          : AND_EXPRESSION
                                            | EXCLUSIVE_OR_EXPRESSION '^' AND_EXPRESSION''' # check with '^' token


    def p_AND_EXPRESSION(self,p):
        '''AND_EXPRESSION                   : EQUALITY_EXPRESSION
                                            | AND_EXPRESSION '&' EQUALITY_EXPRESSION'''
    def p_EQUALITY_EXPRESSION(self,p):
        '''EQUALITY_EXPRESSION              : RELATIONAL_EXPRESSION
                                            | EQUALITY_EXPRESSION equal_equal RELATIONAL_EXPRESSION
                                            | EQUALITY_EXPRESSION notequal RELATIONAL_EXPRESSION''' # add tokens for equal_equal(==) and notequal(!=)
    def p_RELATIONAL_EXPRESSION(self,p):
        '''RELATIONAL_EXPRESSION            : SHIFT_EXPRESSION
                                            | RELATIONAL_EXPRESSION lt  SHIFT_EXPRESSION
                                            | RELATIONAL_EXPRESSION gt  SHIFT_EXPRESSION
                                            | RELATIONAL_EXPRESSION lte SHIFT_EXPRESSION
                                            | RELATIONAL_EXPRESSION gte SHIFT_EXPRESSION''' # add tokens lt(<),gt(>), lte(<=), gte(>=)
    def p_SHIFT_EXPRESSION(self,p):
        '''SHIFT_EXPRESSION                 : ADDITIVE_EXPRESSION
                                            | SHIFT_EXPRESSION left_shift ADDITIVE_EXPRESSION
                                            | SHIFT_EXPRESSION right_shift ADDITIVE_EXPRESSION''' # add token for left_shift(<<), right_shift(>>)


    def p_ADDITIVE_EXPRESSION(self,p):
        '''ADDITIVE_EXPRESSION              : MULTIPLICATIVE_EXPRESSION
                                            | ADDITIVE_EXPRESSION '+' MULTIPLICATIVE_EXPRESSION
                                            | ADDITIVE_EXPRESSION '-' MULTIPLICATIVE_EXPRESSION'''

    def p_MULTIPLICATIVE_EXPRESSION(self,p):
        '''MULTIPLICATIVE_EXPRESSION        : CAST_EXPRESSION
                                            | MULTIPLICATIVE_EXPRESSION '*' CAST_EXPRESSION
                                            | MULTIPLICATIVE_EXPRESSION '/' CAST_EXPRESSION
                                            | MULTIPLICATIVE_EXPRESSION '%' CAST_EXPRESSION'''

    def p_CAST_EXPRESSION(self,p):
        '''CAST_EXPRESSION                  : UNARY-EXPRESSION
                                            | '(' TYPE_NAME ')' CAST_EXPRESSION'''

    def p_UNARY_OPERATOR(self,p):
        ''' UNARY_OPERATOR                  : '*'
                                            | '&'
                                            | '+'
                                            | '-'
                                            | '!'
                                            | '~' '''

    def p_POSTFIX_EXPRESSION(self,p):
        '''POSTFIX-EXPRESSION               : PRIMARY_EXPRESSION
                                            | POSTFIX_EXPRESSION '[' EXPRESSION ']'
                                            | POSTFIX_EXPRESSION '(' EXPRESSION_LIST ')'
                                            | POSTFIX_EXPRESSION '(' ')'
                                            | SIMPLE_TYPE_NAME '(' EXPRESSION_LIST ')'
                                            | SIMPLE_TYPE_NAME '(' ')'
                                            | POSTFIX_EXPRESSION '.' NAME
                                            | POSTFIX_EXPRESSION arrow NAME
                                            | POSTFIX_EXPRESSION plus_plus
                                            | POSTFIX_EXPRESSION minus_minus''' #add tokens for arrow(->), plusplus(++), minusminus(--)



    def p_EXPRESSION_LIST(self,p):
        '''EXPRESSION-LIST                  : ASSIGNMENT_EXPRESSION
                                            | EXPRESSION_LIST ',' ASSIGNMENT_EXPRESSION'''

    def p_PRIMARY_EXPRESSION(self,p):
        '''PRIMARY-EXPRESSION               : LITERAL
                                            | this
                                            | colon_colon IDENTIFIER
                                            | colon_colon OPERATOR_FUNCTION_NAME
                                            | colon_colon QUALIFIED_NAME
                                            | '(' EXPRESSION ')'
                                            | NAME'''  #add token for this, colon_colon

    def p_NAME(self,p):
        '''NAME                             : identifier
                                            | '~' CLASS_NAME''' # token identifier



    def p_LITERAL(self,p):
        '''LITERAL                          : integer_constant
                                            | character_constant
                                            | floating_constant
                                            | string_literal''' #tokens for each

    #***************************************************DECLARATIONS**********************************************************************
    def p_DECLARATION(self,p):
        '''DECLARATION                      : DECL_SPECIFIERS DECLARATOR_LIST ';'
                                            | FUNCTION_DEFINITION'''

    def p_LOCAL_DECLARATION(self, p):
        '''LOCAL_DECLARATION                : LOCAL_DECL_SPECIFIERS LOCAL_DECLARATOR_LIST ';' '''

    def p_LOCAL_DECL_SPECIFIER(self, p):
        '''LOCAL_DECL_SPECIFIER             : STORAGE_CLASS_SPECIFIER
                                            | LOCAL_TYPE_SPECIFIER'''

    def p_LOCAL_DECL_SPECIFIERS(self,p):
        '''LOCAL-DECL-SPECIFIERS            : LOCAL_DECL_SPECIFIERS LOCAL_DECL_SPECIFIER
                                            | LOCAL_DECL_SPECIFIER'''

    def p_DECL_SPECIFIER(self,p):
        '''DECL_SPECIFIER                   : STORAGE_CLASS_SPECIFIER
                                            | TYPE_SPECIFIER
                                            | typedef''' #add token for typedef

    def p_DECL_SPECIFIERS(self,p):
        '''DECL_SPECIFIERS                  : DECL_SPECIFIERS DECL_SPECIFIER
                                            | DECL_SPECIFIER'''

    def p_STORAGE_CLASS_SPECIFIER(self, p):
        '''STORAGE_CLASS_SPECIFIER          : auto
                                            | register
                                            | static
                                            | extern''' # tokens for each

    def p_LOCAL_TYPE_SPECIFIER(self,p):
        '''LOCAL_TYPE_SPECIFIER             : SIMPLE_TYPE_NAME
                                            | const
                                            | volatile''' #add tokens for const, volatile

    def p_TYPE_SPECIFIER(self, p):
        '''TYPE_SPECIFIER                   : SIMPLE_TYPE_NAME
                                            | CLASS_SPECIFIER
                                            | ELABORATED_TYPE_SPECIFIER
                                            | const
                                            | volatile''' # tokens for last 2

    def p_SIMPLE_TYPE_NAME(self,p):
        '''SIMPLE_TYPE_NAME                 : CLASS_NAME
                                            | TYPEDEF_NAME
                                            | char
                                            | short
                                            | int
                                            | long
                                            | signed
                                            | unsigned
                                            | float
                                            | double
                                            | void''' #add tokens for long, signed, unsigned, double, void and others if not added like int, float, char

    def p_ELABORATED_TYPE_SPECIFIER(self,p):
        '''ELABORATED_TYPE_SPECIFIER        : CLASS_KEY identifier
                                            | CLASS_KEY CLASS_NAME''' #token for identifier

    def p_CLASS_KEY(self,p):
        '''CLASS_KEY                        : class
                                            | struct''' #add tokens for class and struct

    def p_CONSTANT_EXPRESSION(self,p):
        '''CONSTANT_EXPRESSION             : CONDITIONAL_EXPRESSION'''



#***************************************************DECLARATORS**********************************************************************

    def p_DECLARATOR_LIST(self,p):
        '''DECLARATOR_LIST                  : INIT_DECLARATOR
                                            | DECLARATOR_LIST ',' INIT_DECLARATOR''' #token for ,
    def p_LOCAL_DECLARATOR_LIST(self,p):
        '''LOCAL_DECLARATOR_LIST            : LOCAL_INIT_DECLARATOR
                                            | LOCAL_DECLARATOR_LIST ',' LOCAL_INIT_DECLARATOR''' #token for ,
    def p_INIT_DECLARATOR(self,p):
        '''INIT_DECLARATOR                  : DECLARATOR INITIALIZER
                                            | DECLARATOR'''
    def p_LOCAL_INIT_DECLARATOR(self,p):
        '''LOCAL_INIT_DECLARATOR            : LOCAL_DECLARATOR INITIALIZER
                                            | LOCAL_DECLARATOR'''
    def p_DECLARATOR(self,p):
        '''DECLARATOR                       : DNAME
                                            | PTR_OPERATOR DECLARATOR
                                            | DECLARATOR '(' ARG_DECLARATION_LIST ')'
                                            | DECLARATOR '[' CONSTANT_EXPRESSION ']'
                                            | DECLARATOR '[' ']'
                                            | '(' DECLARATOR ')' '''
    def p_LOCAL_DECLARATOR(self,p):
        '''LOCAL_DECLARATOR                 : LOCAL_DNAME
                                            | PTR_OPERATOR DECLARATOR
                                            | LOCAL_DECLARATOR '(' ARG_DECLARATION_LIST ')'
                                            | LOCAL_DECLARATOR '[' CONSTANT_EXPRESSION ']'
                                            | LOCAL_DECLARATOR '[' ']'
                                            | '(' LOCAL_DECLARATOR ')' '''
    def p_PTR_OPERATOR(self,p):
        '''PTR_OPERATOR                     : '*'
                                            | '&' ''' # check for *, & in lex
    def p_DNAME(self,p):
        '''DNAME                            : NAME
                                            | CLASS_NAME
                                            | '~' CLASS_NAME
                                            | TYPEDEF_NAME'''
    def p_LOCAL_DNAME(self,p):
        '''LOCAL_DNAME                      : NAME'''

    def p_TYPE_NAME(self,p):
        '''TYPE_NAME                        : TYPE_SPECIFIER_LIST'''

    def p_TYPE_SPECIFIER_LIST(self,p):
        '''TYPE_SPECIFIER_LIST              : TYPE_SPECIFIER TYPE_SPECIFIER_LIST
                                            | TYPE_SPECIFIER'''

    def p_ARG_DECLARATION_LIST(self,p):
        '''ARG_DECLARATION_LIST             : ARGUMENT_DECLARATION
                                            | ARG_DECLARATION_LIST ',' ARGUMENT_DECLARATION'''

    def p_ARGUMENT_DECLARATION(self,p):
        '''ARGUMENT_DECLARATION             : DECL_SPECIFIERS DECLARATOR
                                            | DECL_SPECIFIERS DECLARATOR '=' EXPRESSION
                                            | DECL_SPECIFIERS''' # token for =

    def p_FUNCTION_DEFINITION(self,p):
        '''FUNCTION_DEFINITION              : DECL_SPECIFIERS DECLARATOR CTOR_INITIALIZER FCT_BODY
                                            | DECLARATOR CTOR_INITIALIZER FCT_BODY
                                            | DECL_SPECIFIERS DECLARATOR FCT_BODY
                                            | DECLARATOR FCT_BODY'''
    def p_FCT_BODY(self,p):
        '''FCT_BODY                         : COMPOUND_STATEMENT'''

    def p_INITIALIZER(self,p):
        '''INITIALIZER                      : '=' ASSIGNMENT_EXPRESSION
                                            | '(' EXPRESSION_LIST ')' '''

#***************************************************CLASSES**************************************************************************
#CLASS DECLARATIONS

    def p_CLASS_SPECIFIER(self,p):
        '''CLASS_SPECIFIER                  : CLASS_HEAD '{' MEMBER_LIST '}'
                                            | CLASS_HEAD '{' '}' '''

    def p_CLASS_HEAD(self,p):
        '''CLASS_HEAD                       : CLASS_KEY
                                            | CLASS_KEY CLASS_NAME'''

    def MEMBER_LIST(self,p):
        '''MEMBER_LIST                      : MEMBER_DECLARATION MEMBER_LIST
                                            | MEMBER_DECLARATION
                                            | ACCESS_SPECIFIER ':' MEMBER_LIST
                                            | ACCESS_SPECIFIER ':' '''

    def p_MEMBER_DECLARATION(self,p):
        '''MEMBER_DECLARATION               : DECL_SPECIFIERS MEMBER_DECLARATOR_LIST ';'
                                            | MEMBER_DECLARATOR_LIST ';'
                                            | FUNCTION_DEFINITION ;
                                            | FUNCTION_DEFINITION
                                            | qualified_name ';' ''' #add token for qualified_name

    def p_MEMBER_DECLARATOR_LIST(self,p):
        '''MEMBER_DECLARATOR_LIST           : MEMBER_DECLARATOR
                                            | MEMBER_DECLARATOR_LIST ',' MEMBER_DECLARATOR''' #token alert



    def p_MEMBER_DECLARATOR(self,p):
        '''MEMBER_DECLARATOR                : DECLARATOR PURE_SPECIFIER
                                            | DECLARATOR'''

    def p_PURE_SPECIFIER(self,p):
        '''PURE_SPECIFIER                   : '=' integer_constant'''

    def p_ACCESS_SPECIFIER(self,p):
        '''ACCESS_SPECIFIER                 : private
                                            | protected
                                            | public''' #add token for private, protected, public

    def p_CTOR_INITIALIZER(self,p):
        '''CTOR_INITIALIZER                 : ':' MEM_INITIALIZER_LIST'''

    def p_MEM_INITIALIZER_LIST(self,p):
        '''MEM_INITIALIZER_LIST             : MEM_INITIALIZER
                                            | MEM_INITIALIZER ',' MEM_INITIALIZER_LIST'''

    def p_MEM_INITIALIZER(self,p):
        '''MEM_INITIALIZER                  : CLASS_NAME '(' EXPRESSION_LIST ')'
                                            | CLASS_NAME '(' ')'
                                            | identifier '(' EXPRESSION-LIST ')'
                                            | identifier '(' ')' '''
