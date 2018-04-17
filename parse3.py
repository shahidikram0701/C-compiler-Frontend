import os
import ply.yacc as yacc
from copy import deepcopy

#import lexer and tokens from the lexer
from myLex2 import MyLexer
m = MyLexer()
tokens = m.tokens

print(tokens)

class Node:
    def __init__(self, value = None, left = None, right = None, visited = False):
        self.value = value
        self.left = left
        self.right = right
        self.visited = visited

    def __str__(self, depth=0):
        ret = ""

        # Print right branch
        if self.right != None:
            ret += self.right.__str__(depth + 1)

        # Print own value
        ret += "\n" + ("\t"*depth) + str(self.value) + '\n'

        # Print left branch
        if self.left != None:
            ret += self.left.__str__(depth + 1)

        return ret

'''
class StackEntry:
    def __init__(self, value=None, node=None):
        self.value = value
        if node not None:
            self.node = Node(node.type,node.left,node.right)
'''
#symbol table
symbol = []

array_variables = {}
# symbol table entry
symbol_entry = {"name": None, "type": None, "value": None, "width": None, "scope": None}

ast_stack = []
ast_stack_copy = []

t_num = 1
label_num = 1

code = ""

def print_symbol_table():
    print("*" * 50)
    for i in symbol:
        print("Variable name = ", i['name'])
        print("Type = ", i['type'])
        print("Value = ", i['value'])
        print("width = ", i['width'])
        print("scope = ", i['scope'])
        print("*" * 25)
    print("*" * 50)

def query(variable):
    #val = -1
    for i in symbol:
        if(i["name"] == variable):
            return i["value"]
    return -1

def variableError(variable):
    print("\n\nReference to undeclared variable - ", variable, "\n\n")
    exit(0)

def gimme2values(p):
    value1 = 0
    value2 = 0
    if(type(p[1]) == str):
        value = query(p[1])
        if(value != -1):
            #p[0]["value"] = value + p[3]["value"]
            value1 = value
        else:
            variableError(p[1])
    else:
        value1 = p[1]["value"]

    if(type(p[3]) == str):
        value = query(p[3])
        if(value != -1):
            value2 = value
        else:
            variableError(p[3])
    else:
        value2 = p[3]["value"]
    return (value1, value2)

def inorder(tree):
    if(tree != None):
        inorder(tree.left)
        print(tree.value)
        inorder(tree.right)

def postorder(tree):
    if(tree != None):
        postorder(tree.left)
        postorder(tree.right)
        print(tree.value)

def gimme2nodes():
    right_child = ast_stack.pop()
    left_child = ast_stack.pop()
    if(type(right_child) != Node):
        # make a leaf Node
        right_child = Node(value = right_child)
    if(type(left_child) != Node):
        left_child = Node(value = left_child)
    return(right_child, left_child)

def reduce():
    # see if ast_stack[-1] and ast_stack[-2] are both of Node type
    # if so reduce it into one node indicating a sequence of statements
    try:
        if(type(ast_stack[-1]) == Node and type(ast_stack[-2]) == Node):
            (right_child, left_child) = gimme2nodes()
            sequence_node = Node(value = "sequence", left = left_child, right = right_child)
            ast_stack.append(sequence_node)
        else:
            pass
    except:
        pass

def gimme2sequences(tree):
    current = tree
    previous = None
    while(current.value == "sequence"):
        previous = current
        current = current.left

    #print("Condition\n")
    #inorder(previous.left)
    x = previous.left
    previous.left = previous.right
    previous.right = None
    #print("Body\n")
    #inorder(tree)
    return(x, tree)

def traverse(root):
    current_level = [root]
    while current_level:
        print('  ', end = '')
        print('  '.join(str(node.value) for node in current_level))
        next_level = list()
        for n in current_level:
            if n.left:
                next_level.append(n.left)
            if n.right:
                next_level.append(n.right)
            current_level = next_level

def get_temp():
    global t_num
    r = "t" + str(t_num)
    t_num += 1
    return r

def generate_label():
    global label_num
    r = "L" + str(label_num)
    label_num += 1
    return r

def code_gen_if(node):
    if_code = ""
    node.left.visited = True
    (cond_code, cond_temp) = code_gen_expression(node.left)
    lab = generate_label()
    print(cond_code)
    print("\nifFalse" + " " + cond_temp + " goto" + " " + lab)
    ICG(node.right)
    print(lab + ":\n")


def code_gen_if_else(node):
    node.left.visited = True
    node.left.left.visited = True
    (cond_code, cond_temp) = code_gen_expression(node.left.left)
    lab = generate_label()
    lab2 = generate_label()
    print(cond_code)
    print("\nifFalse" + " " + cond_temp + " goto" + " " + lab)
    node.left.right.visited = True
    ICG(node.left.right.left)
    print("goto", lab2)
    print("\n" + lab + ":")
    node.right.visited = True
    node.right.left.visited = True
    ICG(node.right.left.left)
    print('\n' + lab2 + ":\n")

def code_gen_while(node):
    #while_code = ""
    node.left.visited = True
    node.left.left.visited = True
    (cond_code, cond_temp) = code_gen_expression(node.left.left)
    lab = generate_label() #equal to begin
    lab2 = generate_label()
    print(lab + ":")
    print(cond_code)
    print("\nifFalse" + " " + cond_temp + " goto" + " " + lab2)
    node.right.visited = True
    ICG(node.right.left)
    print("goto", lab)
    print(lab2 + ":")


def code_gen_declaration(node):
    # Handle array declarations!!!

    declaration_code = ""
    var_type = node.left.value
    node.left.visited = True

    node.right.visited = True
    var_name = node.right.left.value
    node.right.left.visited = True

    node.right.right.visited = True

    if(node.right.right.value not in ['+', '-', '*', '/', '%']):
        declaration_code = declaration_code + var_name + " = " + str(node.right.right.value)
    else:
        (exp_code, temp) = code_gen_expression(node.right.right)
        print(exp_code)
        declaration_code = declaration_code + var_name + " = " + temp # wait i'll test

    return declaration_code

def code_gen_assignment(node):
    assignment_code = ''
    node.left.visited = True

    var_name = node.left.value

    node.right.visited = True
    if(node.right.value not in ['+', '-', '*', '/', '%']):
        assignment_code = assignment_code + var_name + " = " + str(node.right.value)
    else:
        (expr_code, expr_temp) = code_gen_expression(node.right)
        print(expr_code)
        assignment_code = assignment_code + var_name + " = " + expr_temp

    return assignment_code

def code_gen_expression(node):
    expression_code = ""
    exp_stack = []
    #print(node)
    # exp_code
    def postorder2(node2):
        nonlocal expression_code
        if(node2 != None):
            postorder2(node2.left)
            postorder2(node2.right)
            #print(node2.value)

            if(node2.value in ['+', '-', '*', '/', '%', '<', '>', '==', '>=', '<=', '!=']):
                t = get_temp()
                right = str(exp_stack.pop())
                left = str(exp_stack.pop())
                expression_code = expression_code + "\n" + t + " = " + left + " " + node2.value + " " + right
                exp_stack.append(t)
            else:
                exp_stack.append(node2.value)
            node2.visited = True
    postorder2(node)

    return (expression_code, exp_stack[0])

def process_node(node):
    #print("process_node")
    #print(node)
    if(node.visited == False):
        if(node.value == "Declaration"):
            #print(node)
            # Code for generating declaration statements
            print(code_gen_declaration(node))
        elif(node.value in ['+', '-', '*', '/', '%']):
            # Code for generating expressions
            print(code_gen_expression(node)[0])
        elif(node.value == "="):
            # Code for generating assignment expressions
            print(code_gen_assignment(node))
        elif(node.value == "if"):
            # Code for generating if expressions
            print(code_gen_if(node))
        elif(node.value == "if-else"):
            print(code_gen_if_else(node))
        elif(node.value == "while"):
            print(code_gen_while(node))
        node.visited = True


def ICG(tree):
    if(tree != None):
        process_node(tree)
        ICG(tree.left)
        ICG(tree.right)


def p_PROGRAM(p):
  '''PROGRAM                          : GLOBAL_STATEMENT_LIST MAIN '''
  #p[0]['type'] = p[1]

  print("\n\n\nACCEPTED!!\n\n")
  print("*" * 50)
  print("Symbol_Table\n") # why p[1]??
  print_symbol_table()
  print("\n\nAST\n\n")
  print("AST - stack\n\n", ast_stack)
  i = 0
  while(i < len(ast_stack) and type(ast_stack[i]) != Node):
      i += 1
  while(i < len(ast_stack)):
      inorder(ast_stack[i])
      i += 1
      print("*" * 50)
  print("\n\nDISPLAYING THE TREE YO!!\n\n")
  print(ast_stack[0])

  '''
  print("\n\nICG YO!!\n\n")
  ICG(ast_stack[0])
  print()
  '''

def p_EPSILON(p):
  '''EPSILON                          : '''


def p_GLOBAL_STATEMENT(p):
  '''GLOBAL_STATEMENT                 : EXPRESSION_STATEMENT
                                      | DECLARATION_STATEMENT
                                      | EPSILON'''
  ##print("Outta Global")

def p_MAIN(p):
  '''MAIN                             : Int Main l_paren r_paren l_brace STATEMENT_LIST Return integer_constant semicolon r_brace '''   # tokens to be added here for Int main return 0 ; and braces


def p_STATEMENT(p):
  '''STATEMENT                        : EXPRESSION_STATEMENT
                                      | SELECTION_STATEMENT
                                      | JUMP_STATEMENT
                                      | ITERATION_STATEMENT
                                      | LOCAL_DECLARATION_STATEMENT
                                      | PRINT_STATEMENT'''

def p_PRINT_STATEMENT(p):
  '''PRINT_STATEMENT                  : Cout CASCADE semicolon'''
  #print("Print statement")
  '''
  print("AST_stack = ", ast_stack)
  print(ast_stack[0])
  print("*" * 50)
  print(ast_stack[1])
  print("*" * 50)
  print(ast_stack[2])
  print("*" * 50)
  '''
  for i in range(len(ast_stack)):
      if(type(ast_stack[i]) != Node):
          if(type(ast_stack[i]) == str):
              j = 0
              while( j < len(symbol)):
                  if(symbol[j]['name'] == ast_stack[i]):
                      break
                  j += 1
              if(j >= len(symbol)):
                  print("\n\nERROR!! Printing an undeclared variable", ast_stack[i], "\n\n")
                  exit(0)
          ast_stack[i] = Node(value = ast_stack[i])
  while(len(ast_stack) != 2):
      reduce()
  print_node = Node(value = "print", left = ast_stack.pop())
  ast_stack.append(print_node)
  reduce()

def p_CASCADE(p):
  '''CASCADE                          : left_shift EXPRESSION
                                      | left_shift EXPRESSION CASCADE'''
  #print("CASCADE")
  #print("AST_stack = ", ast_stack)

def p_LOCAL_DECLARATION_STATEMENT(p):
  '''LOCAL_DECLARATION_STATEMENT      : LOCAL_DECLARATION'''

def p_EXPRESSION_STATEMENT(p):
  '''EXPRESSION_STATEMENT             : EXPRESSION semicolon
                                      | semicolon''' # add token for semicolon

def p_COMPOUND_STATEMENT(p):
  '''COMPOUND_STATEMENT               : l_brace STATEMENT_LIST r_brace
                                      | l_brace r_brace ''' # add tokens for braces

def p_GLOBAL_STATEMENT_LIST(p):
  '''GLOBAL_STATEMENT_LIST            : GLOBAL_STATEMENT
                                      | GLOBAL_STATEMENT_LIST GLOBAL_STATEMENT'''

def p_STATEMENT_LIST(p):
  '''STATEMENT_LIST                   : STATEMENT
                                      | STATEMENT_LIST STATEMENT'''

  #print("STATEMENT-LIST")
  #print("AST-Stack - ", ast_stack)
  reduce()
  '''
  if(len(p) == 2):
      print("len(p) == 2\nAST-stack = ", ast_stack)
  else:
      print("len(p) != 2\nAST-stack = ", ast_stack)

  inorder(ast_stack[0])
  print("*" * 50)
  try:
      inorder(ast_stack[1])
      print("*" * 50)
  except:
      pass
  '''
def p_ITERATION_STATEMENT(p):
  '''ITERATION_STATEMENT              : While l_paren EXPRESSION r_paren COMPOUND_STATEMENT''' #add tokens for for, while, small brackets
  #print("Iteration Statement")
  #print("WHILE")
  while_shit = ast_stack.pop()
  (cond_node, body_node) = gimme2sequences(while_shit)


  #cond_node = if_shit.left
  #body_node = if_shit.right

  # right_child = body
  # left_child = condition
  #cond_node = Node(value = "cond", left = left_child)
  #body_node = Node(value = "if_body", left = right_child)
  while_node = Node(value = "while", left = Node(value = "cond", left = cond_node), right = Node(value = "while_body", left = body_node))
  ast_stack.append(while_node)

def p_SELECTION_STATEMENT(p):
  '''SELECTION_STATEMENT              : If l_paren EXPRESSION r_paren COMPOUND_STATEMENT
                                      | If l_paren EXPRESSION r_paren COMPOUND_STATEMENT TEMP Else COMPOUND_STATEMENT ''' #add tokens for if, else
  #print("SELECTION_STATEMENT")
  if(len(p) == 6):
      # only if
      #print("IF")
      '''
      print("AST stack -", ast_stack)
      inorder(ast_stack[1])
      print("*" * 50)
      '''

      #inorder(ast_stack[0])
      if_shit = ast_stack.pop()
      (cond_node, body_node) = gimme2sequences(if_shit)


      #cond_node = if_shit.left
      #body_node = if_shit.right

      # right_child = body
      # left_child = condition
      #cond_node = Node(value = "cond", left = left_child)
      #body_node = Node(value = "if_body", left = right_child)
      if_node = Node(value = "if", left = Node(value = "cond", left = cond_node), right = Node(value = "if_body", left = body_node))
      ast_stack.append(if_node)
      #reduce()
  else:
      # if - else
      print("IF_ELSE")

      print("AST stack - ", ast_stack)
      #inorder(ast_stack[1].left)
      #inorder(ast_stack[1].right)
      #if_else_shit = ast_stack.pop()
      #(cond_node, body_node) = gimme2sequences(if_else_shit)

      #body_node = if_body + else_body
      #inorder(body_node)
      '''
      for i in ast_stack_copy:
          print(i)
          print("*" * 50)
      '''

      else_body = ast_stack.pop()

      else_node = Node(value = "else", left = Node(value = "else_body", left = else_body))

      if_else_node = Node(value = "if-else", left = ast_stack_copy.pop(), right = else_node)

      ast_stack.insert(0, ast_stack_copy.pop())
      ast_stack.append(if_else_node)
      #reduce()

def p_TEMP(p):
    '''TEMP                           : EPSILON '''
    print("Else handle")
    print("AST - stack ")
    print(ast_stack)
    (cond_node, body_node) = gimme2sequences(ast_stack.pop())
    if_node = Node(value = "if", left = Node(value = "cond", left = cond_node), right = Node(value = "if_body", left = body_node))
    ast_stack.append(if_node)
    ast_stack_copy.insert(0, ast_stack.pop())
    ast_stack_copy.insert(0, ast_stack.pop())


def p_JUMP_STATEMENT(p):
  '''JUMP_STATEMENT                   : Break semicolon
                                      | Continue semicolon
                                      | Return EXPRESSION semicolon
                                      | Return semicolon ''' #add tokens for break, return, continue
def p_DECLARATION_STATEMENT(p):
  '''DECLARATION_STATEMENT            : DECLARATION'''


# simple escape sequence check out later

#***************************************************EXPRSSION**********************************************************************

def p_EXPRESSION(p):
  '''EXPRESSION                       : ASSIGNMENT_EXPRESSION
                                      | EXPRESSION comma ASSIGNMENT_EXPRESSION'''
  #print("Expression")
def p_ASSIGNMENT_EXPRESSION(p):
  '''ASSIGNMENT_EXPRESSION            : CONDITIONAL_EXPRESSION
                                      | UNARY_EXPRESSION ASSIGNMENT_OPERATOR ASSIGNMENT_EXPRESSION'''
  #print("ASSIGNMENT_EXPRESSION")
  if(len(p) > 2):
      #print("Assignment Expression")
      i = 0
      while( i < len(symbol)):
          if(symbol[i]["name"] == p[1]):
              if(symbol[i]["type"] == "int"):
                  symbol[i]["value"] = int(p[3]["value"]) # updating symbol table for declared variables after assignment
              elif(symbol[i]["type"] == "float"):
                  symbol[i]["value"] = float(p[3]["value"] * 1.0) # updating symbol table for declared variables after assignment
              elif(symbol[i]["type"] == "short"):
                  symbol[i]["value"] = int(p[3]["value"]) # updating symbol table for declared variables after assignment
              elif(symbol[i]["type"] == "long"):
                  symbol[i]["value"] = int(p[3]["value"]) # updating symbol table for declared variables after assignment
              elif(symbol[i]["type"] == "double"):
                  symbol[i]["value"] = float(p[3]["value"]) # updating symbol table for declared variables after assignment
              elif(symbol[i]["type"] == "char"):
                  symbol[i]["value"] = chr(int(p[3]["value"])) # updating symbol table for declared variables after assignment
              break
          i += 1
      if(i == len(symbol)):
          print("\n\nError!!! Declare variable", p[1], "first\n\n")
          exit(0)
      (right_child, left_child) = gimme2nodes()
      ast_stack.append(Node(value = p[2], left = left_child, right = right_child))
      #reduce()
  else:
      p[0] = p[1]

def p_ASSIGNMENT_OPERATOR(p):
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
  p[0] = p[1]


def p_CONDITIONAL_EXPRESSION(p):
  '''CONDITIONAL_EXPRESSION           : LOGICAL_OR_EXPRESSION'''
  #print("CONDITIONAL EXPRESSION")
  p[0] = p[1]

def p_LOGICAL_OR_EXPRESSION(p):
  '''LOGICAL_OR_EXPRESSION            : LOGICAL_AND_EXPRESSION
                                      | LOGICAL_OR_EXPRESSION pipe_pipe LOGICAL_AND_EXPRESSION''' # add token for or
  #print("LOGICAL_OR_EXPRESSION")
  if(len(p) > 2):
      p[0] = deepcopy(symbol_entry)
      (value1, value2) = gimme2values(p)
      if(p[2] == "||"):
          p[0]["value"] = (value1 or value2)

      (right_child, left_child) = gimme2nodes()
      ast_stack.append(Node(value = p[2], left = left_child, right = right_child))
      #reduce()
  else:
      p[0] = p[1]

def p_LOGICAL_AND_EXPRESSION(p):
  '''LOGICAL_AND_EXPRESSION           : INCLUSIVE_OR_EXPRESSION
                                      | LOGICAL_AND_EXPRESSION ampersand_ampersand INCLUSIVE_OR_EXPRESSION''' # add token for and
  #print("LOGICAL_AND_EXPRESSION")
  if(len(p) > 2):
      p[0] = deepcopy(symbol_entry)
      (value1, value2) = gimme2values(p)
      if(p[2] == "&&"):
          p[0]["value"] = (value1 and value2)

      (right_child, left_child) = gimme2nodes()
      ast_stack.append(Node(value = p[2], left = left_child, right = right_child))
      #reduce()
  else:
      p[0] = p[1]

def p_INCLUSIVE_OR_EXPRESSION(p):
  '''INCLUSIVE_OR_EXPRESSION          : EXCLUSIVE_OR_EXPRESSION
                                      | INCLUSIVE_OR_EXPRESSION pipe EXCLUSIVE_OR_EXPRESSION''' #check with pipe token
  #print("INCLUSIVE_OR_EXPRESSION")

  if(len(p) > 2):
      p[0] = deepcopy(symbol_entry)
      (value1, value2) = gimme2values(p)
      if(p[2] == "|"):
          p[0]["value"] = (value1 | value2)

      (right_child, left_child) = gimme2nodes()
      ast_stack.append(Node(value = p[2], left = left_child, right = right_child))
      #reduce()
  else:
      p[0] = p[1]

def p_EXCLUSIVE_OR_EXPRESSION(p):
  '''EXCLUSIVE_OR_EXPRESSION          : AND_EXPRESSION
                                      | EXCLUSIVE_OR_EXPRESSION cap AND_EXPRESSION''' # check with cap token
  #print("EXCLUSIVE_OR_EXPRESSION")
  if(len(p) > 2):
     p[0] = deepcopy(symbol_entry)
     (value1, value2) = gimme2values(p)
     if(p[2] == "^"):
         p[0]["value"] = (value1 ^ value2)
     (right_child, left_child) = gimme2nodes()
     ast_stack.append(Node(value = p[2], left = left_child, right = right_child))
     #reduce()
  else:
      p[0] = p[1]

def p_AND_EXPRESSION(p):
  '''AND_EXPRESSION                   : EQUALITY_EXPRESSION
                                      | AND_EXPRESSION ampersand EQUALITY_EXPRESSION'''
  #print("AND_EXPRESSION")

  if(len(p) > 2):
      p[0] = deepcopy(symbol_entry)
      (value1, value2) = gimme2values(p)
      if(p[2] == "&"):
          p[0]["value"] = (value1 & value2)
      (right_child, left_child) = gimme2nodes()
      ast_stack.append(Node(value = p[2], left = left_child, right = right_child))
      #reduce()
  else:
      p[0] = p[1]

def p_EQUALITY_EXPRESSION(p):
  '''EQUALITY_EXPRESSION              : RELATIONAL_EXPRESSION
                                      | EQUALITY_EXPRESSION equal_equal RELATIONAL_EXPRESSION
                                      | EQUALITY_EXPRESSION notequal RELATIONAL_EXPRESSION''' # add tokens for equal_equal(==) and notequal(!=)
  #print("EQUALITY_EXPRESSION")

  if(len(p) > 2):
      p[0] = deepcopy(symbol_entry)
      (value1, value2) = gimme2values(p)
      if(p[2] == "=="):
          p[0]["value"] = (value1 == value2)
      elif(p[2] == "!="):
          p[0]["value"] = (value1 != value2)

      (right_child, left_child) = gimme2nodes()
      ast_stack.append(Node(value = p[2], left = left_child, right = right_child))
      #reduce()
  else:
      p[0] = p[1]

def p_RELATIONAL_EXPRESSION(p):
  '''RELATIONAL_EXPRESSION            : SHIFT_EXPRESSION
                                      | RELATIONAL_EXPRESSION lt  SHIFT_EXPRESSION
                                      | RELATIONAL_EXPRESSION gt  SHIFT_EXPRESSION
                                      | RELATIONAL_EXPRESSION lte SHIFT_EXPRESSION
                                      | RELATIONAL_EXPRESSION gte SHIFT_EXPRESSION''' # add tokens lt(<),gt(>), lte(<=), gte(>=)
  #print('RELATIONAL_EXPRESSION')

  if(len(p) > 2):
      p[0] = deepcopy(symbol_entry)
      (value1, value2) = gimme2values(p)
      if(p[2] == "<"):
          p[0]["value"] = (value1 < value2)
      elif(p[2] == ">"):
          p[0]["value"] = (value1 > value2)
      elif(p[2] == "<="):
          p[0]["value"] = (value1 <= value2)
      else:
          p[0]["value"] = (value1 >= value2)

      (right_child, left_child) = gimme2nodes()
      ast_stack.append(Node(value = p[2], left = left_child, right = right_child))
      #reduce()
  else:
      p[0] = p[1]
  #print("Here")

def p_SHIFT_EXPRESSION(p):
  '''SHIFT_EXPRESSION                 : ADDITIVE_EXPRESSION''' # add token for left_shift(<<), right_shift(>>)
  #print('SHIFT_EXPRESSION')

  if(len(p) > 2):
      p[0] = deepcopy(symbol_entry)
      (value1, value2) = gimme2values(p)
      if(p[2] == "<<"):
          p[0]["value"] = (value1 << value2)
      elif(p[2] == ">>"):
          p[0]["value"] = (value1 >> value2)

      (right_child, left_child) = gimme2nodes()
      ast_stack.append(Node(value = p[2], left = left_child, right = right_child))
      #reduce()
  else:
      p[0] = p[1]

def p_ADDITIVE_EXPRESSION(p):
  '''ADDITIVE_EXPRESSION              : MULTIPLICATIVE_EXPRESSION
                                      | ADDITIVE_EXPRESSION plus MULTIPLICATIVE_EXPRESSION
                                      | ADDITIVE_EXPRESSION minus MULTIPLICATIVE_EXPRESSION'''
  #print('ADDITIVE_EXPRESSION')

  if(len(p) > 2):
      p_copy = p
      p[0] = deepcopy(symbol_entry)
      (value1, value2) = gimme2values(p)
      if(p[2] == "+"):
          p[0]["value"] = value1 + value2
      elif(p[2] == "-"):
          p[0]["value"] = value1 - value2
      #(left_child, right_child) = gimme2nodes(p_copy)
      #ast_stack.append(Node(type = "operator", value = p_copy[2], left = left_child, right = right_child))
      #print("AST-stack = ", ast_stack)
      (right_child, left_child) = gimme2nodes()
      ast_stack.append(Node(value = p[2], left = left_child, right = right_child))
      #print("AST-stack = ", ast_stack)
      #reduce()
  else:
      p[0] = p[1]

def p_MULTIPLICATIVE_EXPRESSION(p):
  '''MULTIPLICATIVE_EXPRESSION        : UNARY_EXPRESSION
                                      | MULTIPLICATIVE_EXPRESSION star UNARY_EXPRESSION
                                      | MULTIPLICATIVE_EXPRESSION slash UNARY_EXPRESSION
                                      | MULTIPLICATIVE_EXPRESSION mod UNARY_EXPRESSION'''
  #print('MULTIPLICATIVE_EXPRESSION')

  if(len(p) > 2):
      p[0] = deepcopy(symbol_entry)
      (value1, value2) = gimme2values(p)
      if(p[2] == "*"):
          p[0]["value"] = value1 * value2
      elif(p[2] == "/"):
          p[0]["value"] = value1 / value2
      else:
          p[0]["value"] = value1 % value2

      (right_child, left_child) = gimme2nodes()
      ast_stack.append(Node(value = p[2], left = left_child, right = right_child))
      #reduce()
  else:
      p[0] = p[1]


def p_UNARY_EXPRESSION(p):
  '''UNARY_EXPRESSION                 : PRIMARY_EXPRESSION
                                      | UNARY_OPERATOR UNARY_EXPRESSION
                                      | plus_plus UNARY_EXPRESSION
                                      | minus_minus UNARY_EXPRESSION'''
  #print("UNARY_EXPRESSION")
  p[0] = p[1]

def p_UNARY_OPERATOR(p):
  ''' UNARY_OPERATOR                  : star
                                      | ampersand
                                      | plus
                                      | minus
                                      | exclamation
                                      | tilde '''

  #print('POSTFIX_EXPRESSION')
  p[0] = p[1]


def p_EXPRESSION_LIST(p):
  '''EXPRESSION_LIST                  : ASSIGNMENT_EXPRESSION
                                      | EXPRESSION_LIST comma ASSIGNMENT_EXPRESSION'''

def p_PRIMARY_EXPRESSION(p):
  '''PRIMARY_EXPRESSION               : LITERAL
                                      | l_paren EXPRESSION r_paren
                                      | NAME'''
  #print('PRIMARY_EXPRESSION')
  if(len(p) == 2):
      p[0] = p[1]
  else:
      p[0] = p[2]

def p_NAME(p):
  '''NAME                             : identifier''' # token identifier
  #print("NAME")
  #print("identifier") #not printing!!!
  #print("p[1] = ", p[1])
  p[0] = p[1]   # symbol table ...we need to update da
  ast_stack.append(p[1])

def p_LITERAL(p):
  '''LITERAL                          : integer_constant
                                      | character_constant
                                      | floating_constant
                                      | string_literal''' #tokens for each
  #print("LITERAL")
  p[0] = deepcopy(symbol_entry)
  p[0]["value"] = p[1]
  ast_stack.append(p[1])

#***************************************************DECLARATIONS**********************************************************************
def p_DECLARATION(p):
  '''DECLARATION                      : DECL_SPECIFIERS DECLARATOR_LIST semicolon
                                      | FUNCTION_DEFINITION'''
  #print("I am here")
  if(len(p) == 4):
    p[0] = p[2]
    if(p[0]['name'] in  array_variables):
       p[0]["type"] = p[1]['type'] + " array"
       p[0]['width'] = p[1]['width'] * array_variables[p[0]['name']]
    else:
       p[0]["type"] = p[1]['type']
       p[0]['width'] = p[1]['width']

    p[0]["scope"] = "global"
    #print(p[0],p[1])
    symbol.append(p[0])
    Decl_left_child = Node(value = p[0]["type"])
    (right_child, left_child) = gimme2nodes()
    Decl_right_child = Node(value = "=", left = left_child, right = right_child)
    ast_stack.append(Node(value = "Declaration", left = Decl_left_child, right = Decl_right_child))
    #reduce()
  else:
    # Function definition
    pass


def p_LOCAL_DECLARATION(p):
  '''LOCAL_DECLARATION                : LOCAL_DECL_SPECIFIERS LOCAL_DECLARATOR_LIST semicolon'''
  try:
      p[0] = p[2]
      if(p[0]['name'] in  array_variables):
         p[0]["type"] = p[1]['type'] + " array"
         p[0]['width'] = p[1]['width'] * array_variables[p[0]['name']]
      else:
         p[0]["type"] = p[1]['type']
         p[0]['width'] = p[1]['width']
      p[0]['scope'] = "local"
      #print(p[0],p[1])
      symbol.append(p[0])
      #print("AST = ", ast_stack)
      Decl_left_child = Node(value = p[0]["type"])
      (right_child, left_child) = gimme2nodes()
      Decl_right_child = Node(value = "=", left = left_child, right = right_child)
      ast_stack.append(Node(value = "Declaration", left = Decl_left_child, right = Decl_right_child))
      #reduce()
  except:
      pass
  #print("Local Declaration")

def p_LOCAL_DECL_SPECIFIERS(p):
  '''LOCAL_DECL_SPECIFIERS            : LOCAL_DECL_SPECIFIERS SIMPLE_TYPE_NAME
                                      | SIMPLE_TYPE_NAME'''
  if(len(p) > 2):
      # to handle = cases like unisigned int
      pass
  else:
      p[0] = p[1]
  #print("LOCAL_DECL_SPECIFIERS")


def p_DECL_SPECIFIERS(p):
  '''DECL_SPECIFIERS                  : DECL_SPECIFIERS TYPE_SPECIFIER
                                      | TYPE_SPECIFIER'''
  p[0] = p[1]


def p_TYPE_SPECIFIER(p):
  '''TYPE_SPECIFIER                   : SIMPLE_TYPE_NAME
                                      | CLASS_SPECIFIER
                                      | ELABORATED_TYPE_SPECIFIER''' #tokens for last 2
  p[0] = p[1]

def p_SIMPLE_TYPE_NAME(p):
  '''SIMPLE_TYPE_NAME                 : NAME
                                      | Char
                                      | Short
                                      | Int
                                      | Long
                                      | Signed
                                      | Unsigned
                                      | Float
                                      | Double''' #add tokens for long, signed, unsigned, double, void and others if not added like Int, float, char
  #print("SIMPLE_TYPE_NAME")
  if(p[1] == "char"):
    p[0] = {'type': 'char', 'width' : 1}
  elif(p[1] == "short"):
    p[0] = {'type': 'short', 'width' : 1}
  elif(p[1] == "int"):
    p[0] = {'type': 'int', 'width': 4}
  elif(p[1] == "long"):
    p[0] = {'type': 'long', 'width' : 8}
  elif(p[1] == "signed"):
    p[0] = {'type': 'signed', 'width' : 4}
  elif(p[1] == "unsigned"):
    p[0] = {'type': 'unsigned', 'width' : 4}
  elif(p[1] == "float"):
    p[0] = {'type': 'float', 'width' : 4}
  elif(p[1] == "double"):
    p[0] = {'type': 'double', 'width' : 8}
  else:
    p[0] = {'type': 'void', 'width' : 0}

def p_ELABORATED_TYPE_SPECIFIER(p):
  '''ELABORATED_TYPE_SPECIFIER        : CLASS_KEY identifier
                                      | CLASS_KEY NAME''' #token for identifier

def p_CLASS_KEY(p):
  '''CLASS_KEY                        : Class''' #add tokens for class and struct

def p_CONSTANT_EXPRESSION(p):
  '''CONSTANT_EXPRESSION             : CONDITIONAL_EXPRESSION'''
  p[0] = p[1]


#***************************************************DECLARATORS**********************************************************************

def p_DECLARATOR_LIST(p):
  '''DECLARATOR_LIST                  : INIT_DECLARATOR ''' #token for ,

  # not handling int i, j, k type    .... this was there in the grammar??
  p[0] = p[1]

def p_LOCAL_DECLARATOR_LIST(p):
  '''LOCAL_DECLARATOR_LIST            : LOCAL_INIT_DECLARATOR ''' #token for ,
   # not handling int i, j, k type
  p[0] = p[1]
  #print("LOCAL_DECLARATOR_LIST")

def p_INIT_DECLARATOR(p):
  '''INIT_DECLARATOR                  : DECLARATOR INITIALIZER
                                      | DECLARATOR'''
  if(len(p) == 3):
      #print("p[0] = ", p[0])
      p[0] = p[2]
      p[0]["name"] = p[1]
      #print("p[0] = ", p[0])
  else:
      p[0] = deepcopy(symbol_entry)
      p[0]["name"] = p[1]
      #p[0]["name"] = p[1]

def p_LOCAL_INIT_DECLARATOR(p):
  '''LOCAL_INIT_DECLARATOR            : LOCAL_DECLARATOR INITIALIZER
                                      | LOCAL_DECLARATOR'''
  #print("LOCAL_INIT_DECLARATOR")
  if(len(p) == 3):
      #print("p[0] = ", p[0])
      p[0] = p[2]
      p[0]["name"] = p[1]
      #print("p[0] = ", p[0])
  else:
      p[0] = deepcopy(symbol_entry)
      p[0]["name"] = p[1]
      #p[0]["name"] = p[1]

def p_DECLARATOR(p):
  '''DECLARATOR                       : DNAME
                                      | DECLARATOR l_paren ARG_DECLARATION_LIST r_paren
                                      | DECLARATOR l_bracket CONSTANT_EXPRESSION r_bracket
                                      | DECLARATOR l_bracket r_bracket
                                      | l_paren DECLARATOR r_paren'''
  #print("DECLARATOR")
  #print(p[1])
  if(len(p) == 2):
      p[0] = p[1]
  else:
      if(len(p) == 5):
          #print("Array name = ", p[1])
          array_variables[p[1]] = p[3]["value"]
          p[0] = p[1]
          #array[p[1]]
          #p[0] = (p[1], "array", p[3]["value"])
      else:
          pass
          #p[0] = (p[1], "array")

def p_LOCAL_DECLARATOR(p):
  '''LOCAL_DECLARATOR                 : NAME
                                      | LOCAL_DECLARATOR l_bracket CONSTANT_EXPRESSION r_bracket
                                      | LOCAL_DECLARATOR l_bracket r_bracket
                                      | l_paren LOCAL_DECLARATOR r_paren'''
  #print("LOCAL_DECLARATOR - len(p) = ", len(p))
  if(len(p) == 2):
      p[0] = p[1]
  else:
      if(len(p) == 5):
          #print("Array name = ", p[1])
          array_variables[p[1]] = p[3]["value"]
          p[0] = p[1]
          #array[p[1]]
          #p[0] = (p[1], "array", p[3]["value"])
      else:
          pass
          #p[0] = (p[1], "array")


def p_DNAME(p):
  '''DNAME                            : NAME
                                      | tilde NAME'''
  print("DNAME")
  p[0] = p[1]

def p_ARG_DECLARATION_LIST(p):
  '''ARG_DECLARATION_LIST             : ARGUMENT_DECLARATION
                                      | ARG_DECLARATION_LIST comma ARGUMENT_DECLARATION'''

def p_ARGUMENT_DECLARATION(p):
  '''ARGUMENT_DECLARATION             : DECL_SPECIFIERS DECLARATOR
                                      | DECL_SPECIFIERS DECLARATOR equal EXPRESSION
                                      | DECL_SPECIFIERS
                                      | EPSILON''' # token for =

def p_FUNCTION_DEFINITION(p):
  '''FUNCTION_DEFINITION              : DECL_SPECIFIERS DECLARATOR FCT_BODY'''

def p_FCT_BODY(p):
  '''FCT_BODY                         : COMPOUND_STATEMENT'''

def p_INITIALIZER(p):
  '''INITIALIZER                      : equal ASSIGNMENT_EXPRESSION
                                      | l_paren EXPRESSION_LIST r_paren'''
  #print("INITIALISER")
  #print(p[2])
  p[0] = p[2]

#***************************************************CLASSES**************************************************************************
#CLASS DECLARATIONS

def p_CLASS_SPECIFIER(p):
  '''CLASS_SPECIFIER                  : CLASS_HEAD l_brace MEMBER_LIST r_brace
                                      | CLASS_HEAD l_brace r_brace '''
  #print("In class")

def p_CLASS_HEAD(p):
  '''CLASS_HEAD                       : CLASS_KEY
                                      | CLASS_KEY NAME'''

def p_MEMBER_LIST(p):
  '''MEMBER_LIST                      : MEMBER_DECLARATION MEMBER_LIST
                                      | MEMBER_DECLARATION
                                      | ACCESS_SPECIFIER colon MEMBER_LIST
                                      | ACCESS_SPECIFIER colon '''

def p_MEMBER_DECLARATION(p):
  '''MEMBER_DECLARATION               : DECL_SPECIFIERS MEMBER_DECLARATOR_LIST semicolon
                                      | MEMBER_DECLARATOR_LIST semicolon
                                      | FUNCTION_DEFINITION semicolon
                                      | FUNCTION_DEFINITION''' #add token for qualified_name

def p_MEMBER_DECLARATOR_LIST(p):
  '''MEMBER_DECLARATOR_LIST           : MEMBER_DECLARATOR
                                      | MEMBER_DECLARATOR_LIST comma MEMBER_DECLARATOR''' #token alert



def p_MEMBER_DECLARATOR(p):
  '''MEMBER_DECLARATOR                : DECLARATOR PURE_SPECIFIER
                                      | DECLARATOR'''

def p_PURE_SPECIFIER(p):
  '''PURE_SPECIFIER                   : equal integer_constant'''

def p_ACCESS_SPECIFIER(p):
  '''ACCESS_SPECIFIER                 : Private
                                      | Protected
                                      | Public''' #add token for private, protected, public

def p_MEM_INITIALIZER_LIST(p):
  '''MEM_INITIALIZER_LIST             : MEM_INITIALIZER
                                      | MEM_INITIALIZER comma MEM_INITIALIZER_LIST'''

def p_MEM_INITIALIZER(p):
  '''MEM_INITIALIZER                  : NAME l_paren EXPRESSION_LIST r_paren
                                      | NAME l_paren r_paren
                                      | identifier l_paren EXPRESSION_LIST r_paren
                                      | identifier l_paren r_paren '''


#****************************************************************************************************************

def p_error(p):
    print("\n\nERROR!! at line no. -", p.lineno, "\n")
    print("*" * 50)
    print("SYMBOL TABLE\n")
    print_symbol_table()
    print()
    print()
    exit(0)

print("\n\nBUILDING PARSER\n\n")
parser = yacc.yacc()

o = open("hello_world_final_processed.cpp", 'r')
l = o.read().strip()
o.close()
print(l)
yacc.parse(l)
