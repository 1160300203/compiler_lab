from lex_analysis import lexAna, code

class ItemSet:
    def __init__(self, krn_items, V_to_prods_idx, P):
        self.krn_items = krn_items

        # print('e1')
        # print("krn_items: ",krn_items)
        # input()

        self.non_krn_items = []
        self.next_symbs = {}
        p = 0
        visited = set()
        for item in krn_items:
            if item[1] == 0:
                visited.add(P[item[0]][0])
        for item in krn_items:
            idx, pos = item
            if pos == len(P[idx])-1:
                continue
            v_next = P[idx][pos+1]
            if v_next in self.next_symbs:
                self.next_symbs[v_next].append((item[0], item[1]+1))
            else:
                self.next_symbs[v_next] = [(item[0], item[1]+1)]
            if v_next in V_to_prods_idx and v_next not in visited:
                visited.add(v_next)
                for idx in V_to_prods_idx[v_next]:
                    self.non_krn_items.append((idx, 0))
        while p < len(self.non_krn_items):
            item = self.non_krn_items[p]
            idx, pos = item
            if pos == len(P[idx])-1:
                continue
            v_next = P[idx][pos+1]
            if v_next in self.next_symbs:
                self.next_symbs[v_next].append((item[0], item[1]+1))
            else:
                self.next_symbs[v_next] = [(item[0], item[1]+1)]
            if v_next in V_to_prods_idx and v_next not in visited:
                visited.add(v_next)
                for idx in V_to_prods_idx[v_next]:
                    self.non_krn_items.append((idx, 0))
            p += 1

        # print("e2")
        # print("non_krn_items:", self.non_krn_items)
        # input()

    def getNextSymbs(self):
        return self.next_symbs

    def equ(self, krn_items):
        for item in krn_items:
            if item not in self.krn_items:
                return False
        return len(krn_items) == len(self.krn_items)

def read(grammer_file):
    with open(grammer_file) as f:
        lines = f.readlines()
        V = lines[0].strip('\n')[3:].split(", ")
        V = [x[1:len(x)-1] for x in V]
        T = lines[1].strip('\n')[3:].split(", ")
        T = [x[1:len(x)-1] for x in T]
        P = []
        for i in range(3, len(lines)):
            x = lines[i].strip("\n").split(' ')
            x = [s[1:len(s)-1] for s in x]
            y = [x[0]] + x[2:]
            P.append(y)
        return V, T, P

def build_item_sets(P, V_to_prods):
    # find 'S'
    idx = 0
    while idx < len(P):
        if P[idx][0] == 'S':
            break
        idx += 1
    if idx >= len(P):
        raise Exception("No 'S' Production is found")

    # build goto
    init_items = [(idx, 0)]
    item_sets = [ItemSet(init_items, V_to_prods, P)]
    p = 0
    goto = {}
    while p < len(item_sets):
        item_set = item_sets[p]
        nxt_symbs = item_set.getNextSymbs()
        for nxt_v in nxt_symbs:
            idx = 0
            while idx < len(item_sets):
                if item_sets[idx].equ(nxt_symbs[nxt_v]):
                    break
                idx += 1
            if idx < len(item_sets):
                goto[(p, nxt_v)] = idx
            else:
                item_sets.append(ItemSet(nxt_symbs[nxt_v], V_to_prods, P))
                goto[(p, nxt_v)] = len(item_sets) - 1
        p += 1

    # for i, item_set in enumerate(item_sets):
    #     # items = item_set.krn_items + item_set.non_krn_items
    #     # for item in items:
    #     #     print(item, P[item[0]])
    #     if len(item_set.krn_items) > 1:
    #         print("No.",i)
    #         print(len(item_set.krn_items))
    #     # print(item_set.getNextSymbs())
    # input()

    return item_sets, goto

def getFirst(s, P, V_to_prods_idx, V, T, first):
    first[s] = set()
    for idx in V_to_prods_idx[s]:
        if P[idx][1] in first:
            for val in first[P[idx][1]]:
                first[s].add(val)
        else:
            for val in getFirst(P[idx][1], P, V_to_prods_idx, V, T, first):
                first[s].add(val)
    return first[s]

def build_first(P, V_to_prods_idx, V, T):
    first = {}
    for t in T:
        first[t] = set()
        first[t].add(t)
    for v in V:
        if v in first:
            continue
        prods_idx = V_to_prods_idx[v]
        first[v] = set()
        for idx in prods_idx:
            if P[idx][1] in first:
                for val in first[P[idx][1]]:
                    first[v].add(val)
            else:
                for val in getFirst(P[idx][1], P, V_to_prods_idx, V, T, first):
                    first[v].add(val)
    return first

def getFollow(v, dep, follow, fol):
    follow[v] = set() if v not in fol else fol[v]
    for v_dep in dep[v]:
        if v_dep in follow:
            for vv in follow[v_dep]:
                follow[v].add(vv)
        else:
            for vv in getFollow(v_dep, dep, follow, fol):
                follow[v].add(vv)
    return follow[v]

def build_follow(P, V_to_prods_idx, V, T):
    first = build_first(P, V_to_prods_idx, V, T)
    follow = {}
    follow['S'] = set('$')
    fol = {}
    dep = {}
    for p in P:
        if p[len(p)-1] in V and p[len(p)-1] != p[0]:
            if p[len(p)-1] not in dep:
                dep[p[len(p)-1]] = set()
            dep[p[len(p)-1]].add(p[0])
        for i in range(1, len(p)-1):
            if p[i] in V:
                if p[i] in fol:
                    for vv in first[p[i+1]]:
                        fol[p[i]].add(vv)
                else:
                    fol[p[i]] = first[p[i+1]]

    for v in V:
        if v not in dep and v != 'S':
            follow[v] = fol[v] if v in fol else set()
    for v in dep:
        follow[v] = fol[v] if v in fol else set()
        v_deps = dep[v]
        for v_dep in v_deps:
            if v_dep in follow:
                for vv in follow[v_dep]:
                    follow[v].add(vv)
            else:
                for vv in getFollow(v_dep, dep, follow, fol):
                    follow[v].add(vv)

    # print(follow)

    return follow

def grm_trans(V, T, P):
    V_to_prods = {}
    for i, p in enumerate(P):
        v = p[0]
        if v in V_to_prods:
            V_to_prods[v].append(i)
        else:
            V_to_prods[v] = [i]
    item_sets, goto = build_item_sets(P, V_to_prods)
    follow = build_follow(P, V_to_prods, V, T)
    action = {}
    for i, item_set in enumerate(item_sets):
        for item in item_set.krn_items + item_set.non_krn_items:
            idx, pos = item
            if len(P[idx])-1 == pos:
                for t in follow[P[idx][0]]:
                    if (i, t) in goto:
                        raise Exception("移入与归约冲突")
                    tgt_prod = idx
                    if (i, t) in action and action[(i, t)] != tgt_prod:
                        raise Exception("归约与归约冲突")
                    action[(i, t)] = tgt_prod
    return action, goto, P

def analyze(action, goto, token_seq, P, lines_idx):
    stk = [0]
    token_seq.append('$')
    lines_idx.append(lines_idx[len(lines_idx)-1])
    i = 0
    while i < len(token_seq):
        state = stk[len(stk)-1]
        token = token_seq[i]
        # print('e', state, token, i)
        if (state, token) in goto:
            state = goto[(state, token)]
            stk.append(state)
            i += 1
        elif (state, token) in action:
            idx = action[(state, token)]
            for k in range(len(P[idx])-1):
                stk.pop()
            print(P[idx][0], ' -> ', P[idx][1:])
            state = stk[len(stk)-1]
            if (state, P[idx][0]) in goto:
                stk.append(goto[(state, P[idx][0])])
            else:
                if state == 0 and token == '$' and P[idx][0] == 'S':
                    return True
                raise Exception("Error when handling '"+token+"' at "+str(lines_idx[i])+"th Line")
        else:
            raise Exception("Error when handling '"+token+"' at "+str(lines_idx[i])+"th Line")

if __name__ == '__main__':
    V, T, P = read('grammer.txt')
    action, goto, P = grm_trans(V, T, P)
    token_seq, str_units, symbols, lines_idx = lexAna('src.txt')
    code_to_str = {code[x]:x for x in code}
    token_seq = [code_to_str[x[0]] for x in token_seq]
    analyze(action, goto, token_seq, P, lines_idx)
