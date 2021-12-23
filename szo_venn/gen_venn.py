import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn3, venn3_circles
import argparse
from collections import Counter, defaultdict
import pprint
import math

pp = pprint.PrettyPrinter(indent=2)
canPrint = True

#generate set of all unique ngrams and ngram->individuals mapping for a group
#parameters:
##  data: master data map
##  group: group {MW, Ver, Vis, etc.}
##  prefix: group prefix
##  suffix: group suffix
##  inds: indices of individuals
##  t: type {clock, event, peak}
def gen_set( data, group, prefix, suffix, inds, t, n ):
    ret = set()
    ngram_ind_map = defaultdict(lambda:[])
    gsuffs = [''] if (group == 'ec' or group == 'eo') else suffix
    prefix = '3' if (group == 'ec' or group == 'eo') else prefix
    for i in inds:
        pad = "" if int(i) >= 10 else "0"
        for s in gsuffs:
            key = f"C{pad}{i}_R{prefix}_{group}{s}_{t}"
            if key in data:
                ret.update( data[key][n] )
                for ngram in data[key][n]:
                    ngram_ind_map[ ngram ].append( i )
    return ret, ngram_ind_map

#generate set of ngrams existent in all groups for at least one individual
#parameters:
##  set1 ngram set of group 1
##  set2: ngram sets of groups 2
##  set3: ngram sets of groups 3
##  map1: ngram->individual map for gruop 1
##  map2: ngram->individual map for gruop 2
##  map3: ngram->individual map for gruop 3
##  inds: indices of individuals
def all_set_count( set1, set2, set3, map1, map2, map3, inds ):
    all_set = set1.union( set2.union( set3 ) )

    #get count of each ngram where it appears in all 3 groups
    counts = Counter()
    for ngram in all_set:
        #for each ngram, check if it exists in all inds; if so, update count
        for i in inds:
            if ngram not in map1 or ngram not in map2 or ngram not in map3:
                continue
            if i in map1[ngram] and i in map2[ngram] and i in map3[ngram]:
                counts[ngram] += 1
    return counts, set(counts.keys())

#generate set of ngrams existent in exactly 2 groups for at least one individual
#parameters:
##  set1 ngram set of group 1
##  set2: ngram sets of groups 2
##  map1: ngram->individual map for gruop 1
##  map2: ngram->individual map for gruop 2
##  three_set: set containing ngrams existent in all 3 groups
##  inds: indices of individuals
def two_set_count( set1, set2, map1, map2, three_set, inds):
    all_set = set1.union( set2 )
    #remove ngrams in all 3 sets
    all_set = all_set.difference( three_set )
    counts = Counter()
    for ngram in all_set:
        #for each ngram, check if it exists in all inds; if so, update count
        for i in inds:
            if ngram not in map1 or ngram not in map2: continue
            if i in map1[ngram] and i in map2[ngram]:
                counts[ngram] += 1
    return counts, set(counts.keys())

#generate set of ngrams existent in exactly 1 group for at least one individual
##  set1 ngram set of group 1
##  three_set: set containing ngrams existent in all 3 groups
##  two_set1: set containing ngrams existent in this and one other set
##  two_set2: set containing ngrams existent in this and the other set
##  inds: indices of individuals
def one_set_count( set1, map1, three_set, two_set1, two_set2 ):
    all_set = set1.difference( three_set.union( two_set1.union( two_set2 ) ) )
    counts = Counter()
    for ngram in all_set:
        for i in inds:
            if ngram in map1 and i in map1[ngram]:
                counts[ngram] += 1
    return counts, set(counts.keys())

#return top n occurring ngrams in list of ngrams
def top( grams_cnt, q ):
    if q == 0:
        return [ t[0] for t in grams_cnt.most_common()]
    return [ t[0] for t in grams_cnt.most_common()][:q]

def PRINT( s ):
    if canPrint:
        print(s)

def PPRINT( el ):
    if canPrint:
        pp.pprint(el)

#parse args
parser = argparse.ArgumentParser(description='Process SZO data into Venn Diagrams. Given a specific ngram length N, 3 groups to inspect G={MW, Ver, Vis, ec/eo}, a specific type type to inspect T in {clock, event, peak}, and optionally a prefix spec, suffix spec, and top presenting results R. Then generates the corresponding venn diagram, taking the top R common Ngrams between the groups in G of type T.')
parser.add_argument('N', metavar='N', help='Length of ngram')
parser.add_argument('G1', metavar='G1', help='Group 1 of groups {MW, Ver, Vis, ec/eo}')
parser.add_argument('G2', metavar='G2', help='Group 2 of groups {MW, Ver, Vis, ec/eo}')
parser.add_argument('G3', metavar='G3', help='Group 3 of groups {MW, Ver, Vis, ec/eo}')
parser.add_argument('T', metavar='T', help='Type of type {clock, event, peak}')
parser.add_argument('F', metavar='F', help='File containing SZO data')
parser.add_argument('-Q', metavar='TopQ', type=int, help='Present top Q occuring (default: 5)', default=0)
parser.add_argument('-R', metavar='Run', help='Specify run of the data to use {1, 2, 3} (default: 1)', default=1)
parser.add_argument('-S', metavar='Suffix', help='Specify suffix of the data to use {1, 2} (default: *)', default='*')
parser.add_argument('-I', metavar='Inds', help='Specify individuals {1,...,26} (default: *)', nargs='+', default='*')
args = parser.parse_args()

##dump args into vars
N = args.N                   #length of ngram
Q = args.Q                  #top frequent results (based on a heuristic)
pref = args.R                   #prefix
suff = list(range(1,3)) if args.S == '*' else args.S        #suffix
groups = [args.G1, args.G2, args.G3]    #study groups
T = args.T      #types in a group
file = args.F
inds = list(range(1,27)) if args.I == '*' else args.I

if math.factorial(int(N))*len(inds) >= 100:
    canPrint = False    #printing will be expensive

print("===============================")
print("NGRAM VISUALIZATION START")
print("===============================")
print(f"NGram length: {N}, Groups: ({groups[0]},{groups[1]},{groups[2]})")
print(f"Individuals: {args.I}\n")

#get file
with open(file) as f:
    data = json.load(f)

#generate total unique elements sets and ngram->individual mappings
set1, map1 = gen_set( data, groups[0], pref, suff, inds, T, N )
set2, map2 = gen_set( data, groups[1], pref, suff, inds, T, N )
set3, map3 = gen_set( data, groups[2], pref, suff, inds, T, N )

print("\nAGGREGATE SETS FOR EACH GROUP:")
print("===============================")
PRINT(f"Group: {groups[0]}")
PPRINT(map1)
PRINT(f"\nGroup: {groups[1]}")
PPRINT(map2)
PRINT(f"\nGroup: {groups[2]}")
PPRINT(map3)

print(f"\nGroup Lengths -  {groups[0]}:{ len(map1.keys()) }, {groups[1]}:{ len(map2.keys()) }, {groups[2]}:{ len(map3.keys()) } \n")

#get set of ngrams between all 3 sets
all_set_cnt, all_set = all_set_count( set1, set2, set3, map1, map2, map3, inds )

#get set of ngrams between 2 sets
set12_cnt, set12 = two_set_count( set1, set2, map1, map2, all_set, inds )
set13_cnt, set13 = two_set_count( set1, set3, map1, map3, all_set, inds )
set23_cnt, set23 = two_set_count( set2, set3, map2, map3, all_set, inds )

#get set of ngrams in only a single set
set1_cnt, set1 = one_set_count( set1, map1, all_set, set12, set13 )
set2_cnt, set2 = one_set_count( set2, map2, all_set, set12, set23 )
set3_cnt, set3 = one_set_count( set3, map3, all_set, set13, set23 )

print("COMMON AGGREGATE NGRAM SETS BETWEEN GROUPS")
print("===============================")
PRINT(f"Groups ({groups[0]},{groups[1]},{groups[2]})")
PPRINT(all_set)

PRINT(f"\nGroups ({groups[0]},{groups[1]})")
PPRINT(set12)
PRINT(f"\nGroups ({groups[0]},{groups[2]})")
PPRINT(set13)
PRINT(f"\nGroups ({groups[1]},{groups[2]})")
PPRINT(set23)

PRINT(f"\nGroups ({groups[0]})")
PPRINT(set1)
PRINT(f"\nGroups ({groups[1]})")
PPRINT(set2)
PRINT(f"\nGroups ({groups[2]})")
PPRINT(set3)

print(f"\nCommon Groups Lengths - ({groups[0]},{groups[1]},{groups[2]}):{len(all_set)}, ({groups[0]},{groups[1]}):{len(set12)}, ({groups[0]},{groups[2]}):{len(set13)}, ({groups[1]},{groups[2]}):{len(set23)}, ({groups[0]}):{len(set1)}, ({groups[1]}):{len(set2)}, ({groups[2]}):{len(set3)}")

#scratch sets to init venn diagram
s1 = set(['A', 'B', 'C'])
s2 = set(['A', 'B', 'D'])
s3 = set(['A', 'E', 'F'])

plt.figure(figsize=(10, 12), dpi=80)

v = venn3([s1, s2, s3], (groups[0], groups[1], groups[2]))
#label sets with actual elements
v.get_label_by_id('100').set_text('\n'.join( top(set1_cnt,Q) ))
v.get_label_by_id('010').set_text('\n'.join( top(set2_cnt,Q) ))
v.get_label_by_id('001').set_text('\n'.join( top(set3_cnt,Q) ))
v.get_label_by_id('110').set_text('\n'.join( top(set12_cnt,Q) ))
v.get_label_by_id('101').set_text('\n'.join( top(set13_cnt,Q) ))
v.get_label_by_id('011').set_text('\n'.join( top(set23_cnt,Q) ))
v.get_label_by_id('111').set_text('\n'.join( top(all_set_cnt,Q) ))

plt.title(f"Venn Diagram for groups {groups[0]}, {groups[1]}, {groups[2]}, type: {T}, n={N}" )

fname = f"{N}_{groups[0]}_{groups[1]}_{groups[2]}_{T}"

#save figure to file
plt.savefig(f"out/{fname}.pdf")

#create csv with data
d = {
    f"{groups[0]}_{groups[1]}_{groups[2]}": list(all_set),
    f"{groups[0]},{groups[1]}": list(set12),
    f"{groups[0]},{groups[2]}": list(set13),
    f"{groups[1]},{groups[2]}": list(set23),
    f"{groups[0]}":  list(set1),
    f"{groups[1]}": list(set2),
    f"{groups[2]}": list(set3)
}
#pad extra spaces with 0
max_len = 0
for ngrams in d.values():
    max_len = max( max_len, len(ngrams) )
for k,v in d.items():
    v.extend([""] * (max_len-len(v)))

df = pd.DataFrame(data=d)
print("\nSUMMARY OF VENN DIAGRAM")
print("===============================")
print(df)
df.to_csv(f'out/{fname}.csv', index=False)

#display graph
plt.show()
