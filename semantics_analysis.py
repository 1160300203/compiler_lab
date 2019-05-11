from grammer_analysis import grm_trans, lexAna, code

class SymTbl:
    def __init__(self):
        self.symbols = {}
        self.offset = 0

    def addId(self, id, type, size, start_loc):
        self.symbols[id] = (type, size, start_loc)

class Node:
    def __init__(self, name, childs, idx):
        self.name = name
        self.childs = childs
        self.attrs = None
        self.prod_idx = idx

    def setAtt(self, attr, val):
        if self.attrs is None:
            self.attrs = {}
        self.attrs[attr] = val

    def haveSetAtt(self, attr):
        if self.attrs is not None and attr in self.attrs:
            return True
        return False

    def setRgtBro(self, rgt_bro):
        self.rgt_bro = rgt_bro

    def setFather(self, father):
        self.father = father

class Helper:
    def __init__(self):
        self.temp_num = 0

    def newTemp(self):
        res = 't'+str(self.temp_num)
        self.temp_num += 1
        return res

class Func:
    def __init__(self):
        self.PC = 0

    def s_act(self, tree, idx, i):
        if tree.childs[0].haveSetAtt('code'):
            tree.setAtt('code', tree.childs[0].attrs['code'])

    def dec_act(self, tree, idx, i):
        id = symbols[tree.childs[1].name[1]]
        if id in sym_tbl.symbols:
            raise Exception("重复声明变量")
        type = tree.childs[0].attrs['type']
        size = sizes[type]
        startloc = sym_tbl.offset
        sym_tbl.offset += size
        sym_tbl.addId(id, type, size, startloc)

    def type_act_int(self, tree, idx, i):
        tree.setAtt('type', 'int')

    def type_act_float(self, tree, idx, i):
        tree.setAtt('type', 'float')

    def ass_act(self, tree, idx, i):
        if symbols[tree.childs[0].name[1]] not in sym_tbl.symbols:
            raise Exception("变量名未声明")
        ss = [] if not tree.childs[2].haveSetAtt('code') else tree.childs[2].attrs['code']
        prev_count = tree.attrs['count'] if tree.attrs is not None else 0
        s = []
        for x in ss:
            s.append((prev_count+1, x))
            prev_count += 1
        s.append((prev_count+1, ('=', tree.childs[2].attrs['val'], '-', symbols[tree.childs[0].name[1]])))
        tree.setAtt('count', prev_count+1)
        tree.setAtt('code', s)

    def add_act(self, tree, idx, i):
        temp = helper.newTemp()
        s = []
        if tree.childs[0].haveSetAtt('code'):
            for code in tree.childs[0].attrs['code']:
                s.append(code)
        if tree.childs[2].haveSetAtt('code'):
            for code in tree.childs[2].attrs['code']:
                s.append(code)
        s.append(('+', tree.childs[0].attrs['val'], tree.childs[2].attrs['val'], temp))
        tree.setAtt('code', s)
        tree.setAtt('val', temp)

    def transfer_attr_act(self, tree, idx, i):
        if tree.childs[0].haveSetAtt('code'):
            tree.setAtt('code', tree.childs[0].attrs['code'])
        tree.setAtt('val', tree.childs[0].attrs['val'])

    def mul_act_num(self, tree, idx, i):
        temp = helper.newTemp()
        s = []
        if tree.childs[0].haveSetAtt('code'):
            for code in tree.childs[0].attrs['code']:
                s.append(code)
        s.append(('*', tree.childs[0].attrs['val'], tree.childs[2].attrs['val'], temp))
        tree.setAtt('code',s)
        tree.setAtt('val', temp)

    def mul_act_var(self, tree, idx, i):
        if symbols[tree.childs[2].name[1]] not in sym_tbl.symbols:
            raise Exception("变量名未声明")
        temp = helper.newTemp()
        s = []
        if tree.childs[0].haveSetAtt('code'):
            for code in tree.childs[0].attrs['code']:
                s.append(code)
        s.append(('*', tree.childs[0].attrs['val'], symbols[tree.childs[2].name[1]], temp))
        tree.setAtt('code',s)
        tree.setAtt('val', temp)

    def mul_act_unit(self, tree, idx, i):
        temp = helper.newTemp()
        s = []
        if tree.childs[0].haveSetAtt('code'):
            for code in tree.childs[0].attrs['code']:
                s.append(code)
        if tree.childs[1].haveSetAtt('code'):
            for code in tree.childs[3].attrs['code']:
                s.append(code)
        s.append(('*', tree.childs[0].attrs['val'], tree.childs[3].attrs['val'], temp))
        tree.setAtt('code', s)
        tree.setAtt('val', temp)

    def unit_act(self, tree, idx, i):
        tree.setAtt('val', tree.childs[1].attrs['val'])
        if tree.childs[1].haveSetAtt('code'):
            tree.setAtt('code', tree.childs[1].attrs['code'])

    def num_act(self, tree, idx, i):
        tree.setAtt('val', str(tree.childs[0].attrs['val']))

    def array_act(self, tree, idx, i):
        var = helper.newTemp()
        tree.setAtt('val', var)
        id = symbols[tree.childs[0].name[1]]
        if id not in sym_tbl.symbols:
            raise Exception("变量名未声明")
        pos = tree.childs[2].name[1]
        id = symbols[tree.childs[0].name[1]]
        type = sym_tbl.symbols[id][0]
        if (pos+1) * sizes[type[:len(type)-2]] > sym_tbl.symbols[id][1]:
            raise Exception("数组越界")
        tree.setAtt('code', [('ld', id, tree.childs[2].name[1], var)])

    def var_act(self, tree, idx, i):
        if symbols[tree.childs[0].name[1]] not in sym_tbl.symbols:
            raise Exception("变量名未声明")
        tree.setAtt('val', symbols[tree.childs[0].name[1]])

    def states_dec_act(self, tree, idx, i):
        if tree.childs[0].haveSetAtt('code'):
            tree.setAtt('code', tree.childs[0].attrs['code'])
        tree.setAtt('count', tree.childs[1].attrs['count'])

    def states_ass_act(self, tree, idx, i):
        s = [] if not tree.childs[0].haveSetAtt('code') else tree.childs[0].attrs['code']
        for x in tree.childs[1].attrs['code']:
            s.append(x)
        tree.setAtt('code', s)
        tree.setAtt('count', tree.childs[1].attrs['count'])

    def const_act(self, tree, idx, i):
        tree.setAtt('val', tree.childs[0].name[1])

    def count_instrs(self, tree, idx, i):
        tree.childs[1].setAtt('count', tree.childs[0].attrs['count'])

    def count_sg_instr(self, tree, idx, i):
        tree.setAtt('count', 0)

    def states_sg_dec_act(self, tree, idx, i):
        tree.setAtt('count', 0)

    def states_sg_ass_act(self, tree, idx, i):
        s = [] if not tree.childs[0].haveSetAtt('code') else tree.childs[0].attrs['code']
        tree.setAtt('code', s)
        tree.setAtt('count', tree.childs[0].attrs['count'])

    # def states_sg_cond_act(self, tree, idx, i):

    # def states_sg_loop_act(self, tree, idx, i):

    def cond_act(self, tree, idx, i):
        prev_count = tree.attrs['count']
        ss = tree.childs[2].attrs['code']
        s = []
        for x in ss:
            s.append((prev_count+1,x))
            prev_count += 1
        states1_code = [] if not tree.childs[6].haveSetAtt('code') else tree.childs[6].attrs['code']
        states2_code = [] if not tree.childs[10].haveSetAtt('code') else tree.childs[10].attrs['code']
        states1_count = len(states1_code)
        states2_count = len(states2_code)
        l1 = prev_count + 1 + states1_count + 1 + 1
        l2 = l1 + states2_count
        val = tree.childs[2].attrs['val']
        s.append((prev_count+1,('j'+type_mapping[tree.childs[2].attrs['type']], val[0], val[1], str(l1))))
        prev_count += 1
        for x in states1_code:
            s.append((prev_count+1, (x[1])))
            prev_count += 1
        s.append((prev_count+1, ('j', '-', '-', str(l2))))
        prev_count += 1
        for x in states2_code:
            s.append((prev_count+1, (x[1])))
            prev_count += 1
        tree.setAtt('code', s)
        tree.setAtt('count', prev_count)

    def loop_dw_act(self, tree, idx, i):
        prev_count = tree.attrs['count']
        l1 = prev_count+1
        s = []
        ss = tree.childs[2].attrs['code']
        for x in ss:
            s.append((prev_count+1, x[1]))
            prev_count += 1
        ss = tree.childs[6].attrs['code']
        for x in ss:
            s.append((prev_count+1, x[1]))
            prev_count += 1
        type = tree.childs[6].attrs['type']
        s.append((prev_count+1,('j'+type, tree.childs[6].attrs['val'][0], tree.childs[6].attrs['val'][1], str(l1))))
        prev_count += 1
        tree.setAtt('code', s)
        tree.setAtt('count', prev_count)

    def rop_act(self, tree, idx, i):
        tree.setAtt('type', tree.childs[1].attrs['type'])
        tree.setAtt('code', [] if not tree.childs[0].haveSetAtt('code') else tree.childs[0].attrs['code']
                         + [] if not tree.childs[2].haveSetAtt('code') else tree.childs[2].attrs['code'])
        tree.setAtt('val', (tree.childs[0].attrs['val'], tree.childs[2].attrs['val']))

    # def not_act(self, tree, idx, i):
    #
    # def rop_band_act(self, tree, idx, i):
    #
    # def rop_bor_act(self, tree, idx, i):
    #
    # def true_act(self, tree, idx, i):
    #
    # def false_act(self, tree, idx, i):
    #

    def equ_act(self, tree, idx, i):
        tree.setAtt('type', '==')

    def neq_act(self, tree, idx, i):
        tree.setAtt('type', '!=')

    def ge_act(self, tree, idx, i):
        tree.setAtt('type', '>=')

    def le_act(self, tree, idx, i):
        tree.setAtt('type', '<=')

    def g_act(self, tree, idx, i):
        tree.setAtt('type', '>')

    def l_act(self, tree, idx, i):
        tree.setAtt('type', '<')

    def states_cond_act(self, tree, idx, i):
        s = [] if not tree.childs[0].haveSetAtt('code') else tree.childs[0].attrs['code']
        for x in tree.childs[1].attrs['code']:
            s.append(x)
        tree.setAtt('code', s)
        tree.setAtt('count', tree.childs[1].attrs['count'])

    def states_loop_act(self, tree, idx, i):
        s = [] if not tree.childs[0].haveSetAtt('code') else tree.childs[0].attrs['code']
        for x in tree.childs[1].attrs['code']:
            s.append(x)
        tree.setAtt('code', s)
        tree.setAtt('count', tree.childs[1].attrs['count'])

    def dec_array_act(self, tree, idx, i):
        id = symbols[tree.childs[1].name[1]]
        if id in sym_tbl.symbols:
            raise Exception("重复声明变量")
        type = tree.childs[0].attrs['type']
        size = sizes[type] * tree.childs[3].name[1]
        startloc = sym_tbl.offset
        sym_tbl.offset += size
        sym_tbl.addId(id, type+'[]', size, startloc)
        tree.setAtt('count', 0)

    def ass_array_act(self, tree, idx, i):
        if symbols[tree.childs[0].name[1]] not in sym_tbl.symbols:
            raise Exception("变量名未声明")
        ss = [] if not tree.childs[5].haveSetAtt('code') else tree.childs[5].attrs['code']
        prev_count = tree.attrs['count']
        s = []
        for x in ss:
            s.append((prev_count+1, x))
            prev_count += 1
        pos = tree.childs[2].name[1]
        id = symbols[tree.childs[0].name[1]]
        type = sym_tbl.symbols[id][0]
        if (pos+1) * sizes[type[:len(type)-2]] > sym_tbl.symbols[id][1]:
            raise Exception("数组越界")
        s.append((prev_count+1, ('=', tree.childs[5].attrs['val'], '-', symbols[tree.childs[0].name[1]]+'['+str(tree.childs[2].name[1])+']')))
        tree.setAtt('count', prev_count+1)
        tree.setAtt('code', s)

    def states_sg_array_dec_act(self, tree, idx, i):
        tree.setAtt('count', 0)

    def states_dec_array_act(self, tree, idx, i):
        if tree.childs[0].haveSetAtt('code'):
            tree.setAtt('code', tree.childs[0].attrs['code'])
        tree.setAtt('count', tree.childs[0].attrs['count'])

def read(grammer_file):
    with open(grammer_file) as f:
        lines = f.readlines()
        V = lines[0].strip('\n')[3:].split(", ")
        V = [x[1:len(x)-1] for x in V]
        T = lines[1].strip('\n')[3:].split(", ")
        T = [x[1:len(x)-1] for x in T]
        P,Z = [],[]
        for i in range(3, len(lines)):
            x = lines[i].strip("\n").split(' ')
            y,z = [],{}
            idx = 0
            for s in x:
                if s[0] == '<':
                    y.append(s[1:len(s)-1])
                    idx += 1
                elif s[0] == '{':
                    z[idx] = s[1:len(s)-1]
            P.append(y)
            Z.append(z)
        return V, T, P, Z

def analyze(action, goto, token_seq, P, lines_idx, Z):
    stk = [0]
    token_seq.append('$')
    lines_idx.append(lines_idx[len(lines_idx)-1])
    i = 0
    nodes = []
    while i < len(token_seq):
        state = stk[len(stk)-1]
        token_tuple = token_seq[i]
        token = token_tuple[0]
        if (state, token) in goto:
            node = Node(token_tuple, None, None)
            if len(nodes) > 0:
                nodes[len(nodes)-1].setRgtBro(node)
            nodes.append(node)
            state = goto[(state, token)]
            stk.append(state)
            i += 1
        elif (state, token) in action:
            idx = action[(state, token)]
            childs = []
            for k in range(len(P[idx])-1):
                childs.append(nodes.pop())
                stk.pop()
            childs.reverse()
            node = Node(P[idx][0], childs, idx)
            if len(nodes) > 0:
                nodes[len(nodes)-1].setRgtBro(node)
            nodes.append(node)
            print(P[idx][0], ' -> ', P[idx][1:])
            state = stk[len(stk)-1]
            if (state, P[idx][0]) in goto:
                stk.append(goto[(state, P[idx][0])])
            else:
                if state == 0 and token == '$' and P[idx][0] == 'S':
                    return nodes[0]
                raise Exception("Error when handling '"+token+"' at "+str(lines_idx[i])+"th Line")
        else:
            raise Exception("Error when handling '"+token+"' at "+str(lines_idx[i])+"th Line")

def trans(tree, Z):
    if tree.prod_idx is None: #终端结点
        print(tree.name)
        return
    idx = tree.prod_idx
    for i,child in enumerate(tree.childs):
        trans(child, Z)
        # print(Z[idx])
        if i+2 in Z[idx]:
            getattr(func, Z[idx][i+2])(tree, idx, i)


helper = Helper()
sym_tbl = SymTbl()
func = Func()
sizes = {'int':4, 'float':4}
type_mapping = {'!=':'==', '==':'!=', '>':'<=', '<':'>=', '>=':'<', '<=':'>'}
if __name__ == '__main__':
    V, T, P, Z = read("trans_grammer.txt")
    action, goto, P = grm_trans(V, T, P)
    token_seq, str_units, symbols, lines_idx = lexAna('src.txt')
    code_to_str = {code[x]:x for x in code}
    token_seq = [(code_to_str[x[0]],x[1]) for x in token_seq]
    tree = analyze(action, goto, token_seq, P, lines_idx, Z)
    trans(tree, Z)
    # print(tree.attrs['code'] if tree.haveSetAtt('code') else 'e')
    for code in tree.attrs['code']:
        print(code)
    print(symbols)
    print(sym_tbl.symbols)

