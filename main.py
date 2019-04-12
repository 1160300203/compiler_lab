
def read_src(src):
    with open(src) as f:
        return f.read()

def recId(src_code, i, code):
    curState = 0
    string = ""
    while i < len(src_code):
        x = src_code[i]
        if curState == 0 and x in chars or curState == 1 and x in chars+digs:
            curState = 1
            string += x
        elif curState == 1:
            return code[string] if string in keywords else code['id'], (None if string in keywords else string), i, string
        else:
            raise Exception('Input error at '+str(i)+'th character '+x)
        i += 1

def delCom(src_code, i):
    curState = 0
    string = ''
    while i < len(src_code):
        x = src_code[i]
        if curState == 0 and x == '/':
            curState = 1
        elif curState == 1 and x == '*':
            curState = 2
        elif curState == 2 and x != '*':
            curState = 2
        elif curState == 2 and x == '*':
            curState = 3
        elif curState == 3 and x == '*':
            curState = 3
        elif curState == 3 and x != '/':
            curState = 2
        elif curState == 3 and x == '/':
            string += x
            return i+1, string
        else:
            raise Exception('Input error at '+str(i)+'th character '+x)
        string += x
        i += 1

def recNum(src_code, i, code):
    string = ''
    curState = 0
    value = 0
    dec = 0
    dec_bits = 0
    exp = 0
    exp_sign = 1
    while i < len(src_code):
        x = src_code[i]
        v = ord(x) - ord('0')
        if curState == 0 and x in digs:
            curState = 1
            value = value * 10 + v
        elif curState == 1 and x in digs:
            curState = 1
            value = value * 10 + v
        elif curState == 1 and x == '.':
            curState = 2
        elif curState == 1 and (x == 'e' or x == 'E'):
            curState = 4
        elif curState == 2 and x in digs:
            curState = 3
            dec += dec*10 + v
            dec_bits += 1
        elif curState == 3 and x in digs:
            curState = 3
            dec += dec*10 + v
            dec_bits += 1
        elif curState == 3 and (x == 'e' or x == 'E'):
            curState = 4
        elif curState == 4 and (x == '+' or x == '-'):
            curState = 5
            if x == '-':
                exp_sign = -1
        elif curState == 4 and x in digs:
            curState = 6
            exp = exp * 10 + v
        elif curState == 5 and x in digs:
            curState = 6
            exp = exp * 10 + v
        elif curState == 6 and x in digs:
            curState = 6
            exp = exp * 10 + v
        else:
            if curState == 1:
                token = code['iConst']
                return token, value, i, string
            elif curState == 3 or curState == 6:
                token = code['fConst']
                value = pow(10, exp*exp_sign) * value
                return token, value, i, string
            else:
                raise Exception('Input error at '+str(i)+'th character '+x)
        string += x
        i += 1

def lexAna(src):
    src_code = read_src(src)
    tokens = []
    str_units = []
    print(src_code)

    i = 0
    while i < len(src_code):
        ch = src_code[i]
        # print(i,ch)
        if ch not in chars + digs + others:
            i += 1
            continue
        if i < len(src_code) - 1:
            ch_nxt = src_code[i+1]
        if ch in chars:
            token, value, i, string = recId(src_code, i, code)
            str_units.append(string)
        elif ch == '/':
            i, string = delCom(src_code, i)
            #str_units.append(string)
            continue
        elif ch in digs:
            token, value, i, string = recNum(src_code, i, code)
            str_units.append(string)
        elif i < len(src_code) - 1 and ch == '=' and ch_nxt == '=':
            token = code[ch+ch_nxt]
            value = None
            i += 2
            str_units.append('==')
        elif i < len(src_code) - 1 and ch == '!' and ch_nxt == '=':
            token = code[ch+ch_nxt]
            value = None
            i += 2
            str_units.append('!=')
        elif ch in "+*=;(){}":
            token = code[ch]
            value = None
            i += 1
            str_units.append(ch)
        else:
            i += 1
            print('encounter illegal character ' + ch + " at " + str(i) + "th character")
            continue
        tokens.append((token, value))
    return tokens, str_units

def display(str_units, tokens):
    for i,token in enumerate(tokens):
        print(str_units[i] + ' ' + ' <' + codeToStr[token[0]] + ' ' +
              ('---' if token[1] is None else str(token[1])) + '>')


keywords = ["int", "float", "bool","struct", "if", "else","do", "while"]
code = {'id': 1, 'int': 2, 'float': 3, 'bool': 4, 'struct': 5, 'if': 6, 'else':7,
        'do': 8, 'while': 9, '+': 10, '*': 11, '==': 12, '!=': 13, '=': 14, ';': 15,
        '(': 16, ')': 17, '{': 18, '}': 19, 'iConst':20, 'fConst':21}
codeToStr = ['', 'IDN', 'INT', 'FLOAT', 'BOOL', 'STRUCT', 'IF', 'ELSE', 'DO', 'WHILE',
             'ADD', 'MUL', 'EQ', 'NE', 'ASSIGN', 'SEMI', 'SLP', 'SRP', 'LP', 'RP', 'iConst', 'fConst']
chars = [chr(ord('a')+x) for x in range(26)] + [chr(ord('A')+x) for x in range(26)] \
        + ['_']
digs = [chr(ord('0')+x) for x in range(10)]
others = ['+','*','=','!',';','(',')','{','}','-','/']
if __name__ == "__main__":
    tokens, str_units = lexAna("./src.txt")
    display(str_units, tokens)
