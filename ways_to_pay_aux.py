I = {}
I[1] = [(1,0), (0,1)]
I[2] = [(2,0), (0,2), (1,1)]
I[3] = [(3,0), (2,1), (1,2), (0,3)]
I[4] = [(4,0), (3,1), (2,2), (1,3), (0,4)]
I[5] = [(5,0), (4,1), (3,2), (2,3), (1,4), (0,5)]
I[6] = [(6,0), (5,1), (4,2), (3,3), (2,4), (1,5), (0,6)]
I[7] = [(7,0), (6,1), (5,2), (4,3), (3,4), (2,5), (1,6), (0,7)]

# Now filter the tuples leaving only those which have no greater than 3 in the second entry.
for key in I.keys():
    val = I[key]
    new_val = list(filter(lambda tup: (tup[1] < 4), val))
    I[key] = list(new_val)

def I_filter_0(max_0, list_to_filter):
    return list(filter(lambda t: (t[0] <= max_0), list_to_filter))

def I_filter_1(max_1, list_to_filter):
    return list(filter(lambda t: (t[1] <= max_1), list_to_filter))

def constrained_partition_dict(max_0, max_1):
    new_src = dict(list(I.items()))
    for key in new_src:
        val = new_src[key]
        new_val = I_filter_0(max_0, val)
        new_val = I_filter_1(max_1, new_val)
        new_src[key] = list(new_val)
    return dict(list(new_src.items()))


