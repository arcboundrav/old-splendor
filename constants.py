import numpy as np
RNG_SEED = 112358
np.random.seed(RNG_SEED)

from tc import *
from ways_to_pay_aux import *

##################################
### Game Preparation Constants ###
##################################
MAX_N_NOBLE = 10
MAX_N_TOKEN = 7
MAX_N_JOKER = 5
MAX_N_RESERVED_CARD = 3

########################
### Daemon Constants ###
########################
MIN_VP_TO_WIN = 15
N_TOKEN_PER_WIDE_DRAW = 3
N_TOKEN_PER_DOUBLE_DRAW = 2
MIN_N_TOKEN_FOR_WIDE_DRAW = 1
MIN_N_TOKEN_FOR_DOUBLE_DRAW = 4
MAX_N_ACTION_PER_PLY = 1
MAX_N_NOBLE_PER_PLY = 1
MAX_N_TOKEN_PER_PLAYER = 10

START_PLY = 0
NOBLE_CHECK = 1
N_TOKEN_CHECK = 2
REFILL_CHECK = 3
WINNER_CHECK = 4

#####################################
### Noble Instantiation Constants ###
#####################################
N_VP_PER_NOBLE = 3


# diamond, emerald,  onyx,    ruby, sapphire
# diamond, sapphire, emerald, ruby, onyx

NOBLE_DIAMOND_IDX = 0
NOBLE_EMERALD_IDX = 1
NOBLE_ONYX_IDX = 2
NOBLE_RUBY_IDX = 3
NOBLE_SAPPHIRE_IDX = 4

NOBLE_0_SPECS = [0, 4, 0, 4, 0]
NOBLE_1_SPECS = [3, 0, 3, 3, 0]
NOBLE_2_SPECS = [4, 0, 0, 0, 4]
NOBLE_3_SPECS = [4, 0, 4, 0, 0]
NOBLE_4_SPECS = [0, 4, 0, 0, 4]
NOBLE_5_SPECS = [0, 3, 0, 3, 3]
NOBLE_6_SPECS = [3, 3, 0, 0, 3]
NOBLE_7_SPECS = [0, 0, 4, 4, 0]
NOBLE_8_SPECS = [3, 0, 3, 0, 3]
NOBLE_9_SPECS = [0, 3, 3, 3, 0]

OLD_NOBLE_SPECS_LIST = [NOBLE_0_SPECS,
                        NOBLE_1_SPECS,
                        NOBLE_2_SPECS,
                        NOBLE_3_SPECS,
                        NOBLE_4_SPECS,
                        NOBLE_5_SPECS,
                        NOBLE_6_SPECS,
                        NOBLE_7_SPECS,
                        NOBLE_8_SPECS,
                        NOBLE_9_SPECS
]

def unify_sequencing(source_list):
    src_list = list(source_list)
    new_list = []
    new_list.append(src_list[0])
    new_list.append(src_list[-1])
    new_list.append(src_list[1])
    new_list.append(src_list[-2])
    new_list.append(src_list[2])
    return list(new_list)

NOBLE_SPECS_LIST = []
for old_specs in OLD_NOBLE_SPECS_LIST:
    NOBLE_SPECS_LIST.append(unify_sequencing(old_specs))

NOBLE_DIAMOND_IDX = 0
NOBLE_SAPPHIRE_IDX = 1
NOBLE_EMERALD_IDX = 2
NOBLE_RUBY_IDX = 3
NOBLE_ONYX_IDX = 4

####################################
### Card Instantiation Constants ###
####################################
CARD_TIER_IDX = 0
CARD_BONUS_IDX = 1
CARD_VP_IDX = 2
CARD_DIAMOND_IDX = 3
CARD_SAPPHIRE_IDX = 4
CARD_EMERALD_IDX = 5
CARD_RUBY_IDX = 6
CARD_ONYX_IDX = 7

DIAMOND_STR = 'w'
SAPPHIRE_STR = 'b'
EMERALD_STR = 'g'
RUBY_STR = 'r'
ONYX_STR = 'o'
JOKER_STR = 'j'

DIAMOND_CSTR = DEF+HIW+'W'+DEF
SAPPHIRE_CSTR = DEF+HIB+'B'+DEF
EMERALD_CSTR = DEF+HIG+'G'+DEF
RUBY_CSTR = DEF+HIR+'R'+DEF
ONYX_CSTR = DEF+HIK+'O'+DEF
JOKER_CSTR = DEF+HIY+'J'+DEF


NON_JOKER_TOKEN_SYMBOLS = ['w', 'b', 'g', 'r', 'o']
ALL_TOKEN_SYMBOLS = ['w', 'b', 'g', 'r', 'o', 'j']
ALL_TOKEN_CSYMBOLS = [DIAMOND_CSTR, SAPPHIRE_CSTR, EMERALD_CSTR, RUBY_CSTR, ONYX_CSTR, JOKER_CSTR]

CARD_SPECS_LIST = [[0,'o',0,1,1,1,1,0],
[0,'o',0,1,2,1,1,0],
[0,'o',0,2,2,0,1,0],
[0,'o',0,0,0,1,3,1],
[0,'o',0,0,0,2,1,0],
[0,'o',0,2,0,2,0,0],
[0,'o',0,0,0,3,0,0],
[0,'o',1,0,4,0,0,0],
[0,'b',0,1,0,1,1,1],
[0,'b',0,1,0,1,2,1],
[0,'b',0,1,0,2,2,0],
[0,'b',0,0,1,3,1,0],
[0,'b',0,1,0,0,0,2],
[0,'b',0,0,0,2,0,2],
[0,'b',0,0,0,0,0,3],
[0,'b',1,0,0,0,4,0],
[0,'w',0,0,1,1,1,1],
[0,'w',0,0,1,2,1,1],
[0,'w',0,0,2,2,0,1],
[0,'w',0,3,1,0,0,1],
[0,'w',0,0,0,0,2,1],
[0,'w',0,0,2,0,0,2],
[0,'w',0,0,3,0,0,0],
[0,'w',1,0,0,4,0,0],
[0,'g',0,1,1,0,1,1],
[0,'g',0,1,1,0,1,2],
[0,'g',0,0,1,0,2,2],
[0,'g',0,1,3,1,0,0],
[0,'g',0,2,1,0,0,0],
[0,'g',0,0,2,0,2,0],
[0,'g',0,0,0,0,3,0],
[0,'g',1,0,0,0,0,4],
[0,'r',0,1,1,1,0,1],
[0,'r',0,2,1,1,0,1],
[0,'r',0,2,0,1,0,2],
[0,'r',0,1,0,0,1,3],
[0,'r',0,0,2,1,0,0],
[0,'r',0,2,0,0,2,0],
[0,'r',0,3,0,0,0,0],
[0,'r',1,4,0,0,0,0],
[1,'o',1,3,2,2,0,0],
[1,'o',1,3,0,3,0,2],
[1,'o',2,0,1,4,2,0],
[1,'o',2,0,0,5,3,0],
[1,'o',2,5,0,0,0,0],
[1,'o',3,0,0,0,0,6],
[1,'b',1,0,2,2,3,0],
[1,'b',1,0,2,3,0,3],
[1,'b',2,5,3,0,0,0],
[1,'b',2,2,0,0,1,4],
[1,'b',2,0,5,0,0,0],
[1,'b',3,0,6,0,0,0],
[1,'w',1,0,0,3,2,2],
[1,'w',1,2,3,0,3,0],
[1,'w',2,0,0,1,4,2],
[1,'w',2,0,0,0,5,3],
[1,'w',2,0,0,0,5,0],
[1,'w',3,6,0,0,0,0],
[1,'g',1,3,0,2,3,0],
[1,'g',1,2,3,0,0,2],
[1,'g',2,4,2,0,0,1],
[1,'g',2,0,5,3,0,0],
[1,'g',2,0,0,5,0,0],
[1,'g',3,0,0,6,0,0],
[1,'r',1,2,0,0,2,3],
[1,'r',1,0,3,0,2,3],
[1,'r',2,1,4,2,0,0],
[1,'r',2,3,0,0,0,5],
[1,'r',2,0,0,0,0,5],
[1,'r',3,0,0,0,6,0],
[2,'o',3,3,3,5,3,0],
[2,'o',4,0,0,0,7,0],
[2,'o',4,0,0,3,6,3],
[2,'o',5,0,0,0,7,3],
[2,'b',3,3,0,3,3,5],
[2,'b',4,7,0,0,0,0],
[2,'b',4,6,3,0,0,3],
[2,'b',5,7,3,0,0,0],
[2,'w',3,0,3,3,5,3],
[2,'w',4,0,0,0,0,7],
[2,'w',4,3,0,0,3,6],
[2,'w',5,3,0,0,0,7],
[2,'g',3,5,3,0,3,3],
[2,'g',4,0,7,0,0,0],
[2,'g',4,3,6,3,0,0],
[2,'g',5,0,7,3,0,0],
[2,'r',3,3,5,3,0,3],
[2,'r',4,0,0,7,0,0],
[2,'r',4,0,3,6,3,0],
[2,'r',5,0,0,7,3,0]]

# VP_PER_TIER
#   0 = 5 * 1 = 5
#   1 = 5 * (11) = 55
#   2 = 5 * (16) = 80
#   total VP = 160
#   32 per color
#   
