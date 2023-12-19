import sys
import re
from os import path

# token types
INTEGER = 'INTEGER'
PLUS = 'PLUS'
MINUS = 'MINUS'
MUL = 'MUL'
LPAREN = '('
RPAREN = ')'
EOF = 'EOF'


class Tokenization:
    # initialize a token instance with a type and value
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
    # string representation of the object     
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


class Lexer:
    def __init__(self, text):
        self.text = text
        self.indx = 0 # track cur index
        self.curr_char = self.text[self.indx] #hold cur char
        
    def check_next_char(self):
        self.indx += 1
        if self.indx > len(self.text) - 1:
            self.curr_char = None
        else:
            self.curr_char = self.text[self.indx]

    def skip_whitespace(self):
        while self.curr_char is not None and self.curr_char.isspace():
            self.check_next_char()
            
    def integer(self):
        # accumulate consecutive digits and check if it matches the re
        pattern = re.compile(r'(0){1}|([1-9])\d*')
        result = ''
        while self.curr_char is not None and self.curr_char.isdigit():
            result += self.curr_char
            self.check_next_char()

        if pattern.fullmatch(result) is not None:
            return int(result)
        else:
            print("error")
            sys.exit(0)


    def get_next_token(self):
        while self.curr_char is not None:

            if self.curr_char.isspace():
                self.skip_whitespace()
                continue

            if self.curr_char.isdigit():
                return Tokenization(INTEGER, self.integer()) 

            if self.curr_char == '+':
                self.check_next_char()
                return Tokenization(PLUS, '+')

            if self.curr_char == '-':
                self.check_next_char()
                return Tokenization(MINUS, '-')

            if self.curr_char == '*':
                self.check_next_char()
                return Tokenization(MUL, '*')

            if self.curr_char == '(':
                self.check_next_char()
                return Tokenization(LPAREN, '(')

            if self.curr_char == ')':
                self.check_next_char()
                return Tokenization(RPAREN, ')')

            print("Syntax error at " , self.curr_char)
            sys.exit(1)

        return Tokenization(EOF, None)


class Operator:
    def __init__(self, left, op, right):
        self.left = left 
        self.token = self.op = op 
        self.right = right 
class Num:
    def __init__(self, token):
        self.token = token
        self.value = token.value
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.curr_token = self.lexer.get_next_token()

    def eat_token(self, token_type):
        if self.curr_token.type == token_type:
            self.curr_token = self.lexer.get_next_token()
        else:
            print("error")
            sys.exit(0)

    def factor(self):
        token = self.curr_token
        if token.type == INTEGER:
            self.eat_token(INTEGER)
            return Num(token)
        elif token.type == LPAREN:
            self.eat_token(LPAREN)
            node = self.expr()
            self.eat_token(RPAREN)
            return node

    def term(self):
        node = self.factor()
        while self.curr_token.type == MUL:
            token = self.curr_token
            if token.type == MUL:
                self.eat_token(MUL)
            node = Operator(left=node, op=token, right=self.factor())

        return node

    def expr(self):
        node = self.term()

        while self.curr_token.type in (PLUS, MINUS):
            token = self.curr_token
            if token.type == PLUS:
                self.eat_token(PLUS)
            elif token.type == MINUS:
                self.eat_token(MINUS)

            node = Operator(left=node, op=token, right=self.term())

        return node

    def parse(self):
        return self.expr()

class Interpreter:
    def __init__(self, parser):
        self.parser = parser

    def visit_Operator(self, node):
        if node.op.type == PLUS: 
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        
    def visit_Num(self, node):
        return node.value

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)
    def visit(self, node):
        if  type(node).__name__ == "Num":
            return self.visit_Num(node)
        elif  type(node).__name__ == "Operator":
            return self.visit_Operator(node)
        else:
            print("error")
            sys.exit()

def read_file(file_name):
    if(path.exists(file_name) == False ):
        print('file not found')
        sys.exit(0)
    f = open(file_name, "r")
    lines = f.readlines()
    f.close()
    return lines

def check_semicolon(lines):
    for i in lines:
        if (i[-1:]) != ';':
            print('error')
            sys.exit(0)
    return True

def split_lines(lines):
    for i in range (len(lines)):
        lines[i]= lines[i].replace("\n","")
        lines[i] = lines[i].split("=")
        
        if len(lines[i]) != 2:
            print('error')
            sys.exit(0)
    return lines

def check_identifier(i):
    if re.match('^[_a-z]\w*' , i) is not None:
        return True
    return False

variables = {}

def split_exp(exp):
    global variables
    values = {}
    vars = re.findall('[_a-z]\w*' , exp)
  
    for i in  range(len(vars)):
    
        if vars[i] not in variables:
            print('error')
            sys.exit(0)
        values[vars[i]] = variables[vars[i]]
    
    for i in vars:
        exp = exp.replace(i ,str( variables[i] ))
    
    if re.match('[a-z]|[A-Z]|_' , exp) is not None:
        sys.exit(0)
    return exp

def calculate_value(text):    
    lexer = Lexer(text)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret()
    return result

def get_minus_plus(lis):
    ret = []
    for i in range(len(lis)):
        lis[i] = lis[i][0]
        if  '-' in lis[i]:
            ret.append( '-')
        else:
            ret.append ('+')
    return ret

def parse_line(line):
    global variables
    exp = split_exp(line)
    exp = exp.replace(';' , '')
    plus_minus = re.findall(r'(((\++)|(-+))+)' , exp)

    plus_minus_2 = get_minus_plus(plus_minus)
    for i in range (len(plus_minus)):
        exp = exp.replace(plus_minus[i] , plus_minus_2[i])
    
    mul = 1
    exp = exp.strip()
    if exp[0] == '+':
        exp = exp[1:]
        
    if exp[0] == '-':
        exp = exp[1:]
        mul = -1
    
    return calculate_value(exp) * mul

def remove_white_spaces(lines):
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()
    return lines

def run():
    global variables
    file_name = input("Enter the file name: ")
    lines = read_file(file_name)
    lines = remove_white_spaces(lines)
    check_semicolon(lines)
    lines = split_lines(lines)
    for i in lines:
        
        i[0] = i[0].replace(" " , "")
        check_identifier(i[0])
        variables[i[0]]  = parse_line(i[1])

        
    for i in sorted(variables):
        print("{}  = {}".format(i , variables[i]))

run()
