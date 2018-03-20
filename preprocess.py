import re
import ply.lex as lex


with open("hello_world.cpp", "r") as f:
	x = f.readlines()

o = open("processed hello_world.cpp", "w")

macros = {}

tokens = ("IDENTIFIER", "COMMENTS")

def t_IDENTIFIER(t):
	# This checks if the lexeme is an identifier or a keyword and returns accordingly
    r'[a-zA-Z_][a-zA-Z0-9_\-]*'
    if(t.value in list(macros.keys())):
    	return t

def t_COMMENTS(t):
    # Match and ignore comments
    # Just handling single line comments for now!
    r"(/\*.*?\*/|//[^\r\n]*$)"
    return t

def t_error(t):
    #print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

for i in range(len(x)):
	line = x[i]
	line = line.strip()
	y = re.findall("#define .+", line)
	if(y):
		y = y[0][8:]
		z = re.search("[a-zA-Z_][a-zA-Z_0-9]*", y)
		val = (y[z.end()+1:])
		macros[z.group()] = val
	else:
		#print(line)
		lexer = lex.lex()
		lexer.input(line)

		new_line = ""
		# Tokenize
		while True:
			lexer.input(line)
			tok = lexer.token()
			#print(line)
			if not tok:
				break      # No more input
			#print(tok)
			if(tok.type == "COMMENTS"):
				#print(tok)
				#print(line[:line.find('/')])
				new_line = " "
				break
			else:
				#print(line)
				new_line = line[:tok.lexpos] + macros[line[tok.lexpos]] + line[tok.lexpos+1:]
				line = new_line

		if(new_line):
			pass
			#print(new_line)
			o.write(line[:line.find('/')].strip())
		else:
			#print(line)
			o.write(line)
o.close()
