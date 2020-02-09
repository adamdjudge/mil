#!/usr/bin/env python3

'''
Interpreter for the mil (Minimal Lisp) programming language
By Adam Judge
Last modified: 7 Feb 2020
'''

# Cons cell, which makes up lists.
class Cons:
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def __str__(self):
        if self.car is None and self.cdr is None:
            return '()'
        s = '(' + str(self.car)
        cur = self.cdr
        while cur is not nil:
            s += ' '
            if type(cur) is Cons:
                s += str(cur.car)
                cur = cur.cdr
            else:
                s += str(cur)
                break
        return s + ')'

# The empty list '()'
nil = Cons(None, None)

# Takes text and separates out the items inside.
def tokenize(text):
    token, tokens = '', []
    state, pl = 'start', 0
    for c in text:
        if state == 'start':
            if c in ' \n\t':
                continue
            elif c == '\"':
                token = '\"'
                state = 'string'
            elif c == '(':
                token = '('
                state = 'list'
            elif c == '#':
                state = 'comment'
            else:
                token += c
                state = 'item'
        elif state == 'comment':
            if c == '\n':
                state = 'start'
        elif state == 'item':
            if c in ' \n\t':
                tokens.append(token)
                token = ''
                state = 'start'
            elif c == '\"':
                token += '\"'
                state = 'string'
            elif c == '#':
                tokens.append(token)
                token = ''
                state = 'comment'
            elif c == '(':
                token += c
                state = 'list'
            else:
                token += c
        elif state == 'string':
            if c == '\"':
                token += c
                state = 'item'
            elif c == '\\':
                state = 'esc_char'
            else:
                token += c
        elif state == 'esc_char':
            if c == 'n': token += '\n'
            elif c == 't': token += '\t'
            elif c == '\"': token += '\"'
            else:
                raise Exception("Tokenizer error: unknown escape sequence '\\"+c+"'")
            state = 'string'
        elif state == 'list':
            if c == '(':
                pl += 1
                token += c
            elif c == ')' and pl == 0:
                token += c
                state = 'item'
            elif c == ')':
                pl -= 1
                token += c
            else:
                token += c
    if state == 'string': raise Exception("Tokenizer error: unclosed string")
    if state == 'list': raise Exception("Tokenizer error: unclosed list")
    if token != '': tokens.append(token)
    return tokens

# Takes raw text and returns a data item, as either a number, list, or atom.
def convert(item):
    if item[0] == '\'':
        return Cons('quote', Cons(convert(item[1:]), nil))

    try:
        num_f = float(item)
        num_i = int(item)
        return (num_i if num_i == num_f else num_f)
    except: pass
    try:
        return int(item, 0)
    except: pass

    if item[0] == '(' and item[-1] == ')':
        items = tokenize(item[1:-1])
        if len(items) == 0:
            return nil
        l = Cons(convert(items.pop()), nil)
        for i in reversed(items):
            l = Cons(convert(i), l)
        return l
    
    return item

# Returns an atom representing the type of the item passed to it.
def typeof(item):
    try:
        x = float(item)
        return 'number'
    except: pass
    if type(item) is Cons:
        return 'list'
    return 'atom'

# Returns t if both items are equal, () otherwise
def eq(x, y, env):
    if evaluate(x, env) == evaluate(y, env):
        return 't'
    else:
        return nil

# Iterates through pairs until its car evaluates to true, and returns the
# evaluation of its cdr.
def cond(c, env):
    if evaluate(c.car.car, env) not in [nil, 0]:
        return evaluate(c.car.cdr.car, env)
    else:
        return cond(c.cdr, env)

# Returns the evaluation of the item passed in.
# Also takes an environment dictionary.
def evaluate(exp, env):
    if typeof(exp) == 'number':
        return exp
    elif typeof(exp) == 'list':
        if exp.car == 'quote':
            return exp.cdr.car
        elif exp.car == 'type':
            return typeof(evaluate(exp.cdr.car, env))
        elif exp.car == 'eq':
            return eq(exp.cdr.car, exp.cdr.cdr.car, env)
        elif exp.car == 'car':
            return evaluate(exp.cdr.car, env).car
        elif exp.car == 'cdr':
            return evaluate(exp.cdr.car, env).cdr
        elif exp.car == 'cond':
            return cond(exp.cdr, env)
    else:
        return env[exp]

if __name__ == '__main__':
    while True:
        l = convert(input('> '))
        r = evaluate(l, {'x': 5})
        print(str(r))