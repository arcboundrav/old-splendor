# Colour Constants for Terminal Formatting
RESET = "\033[0;0m"
BOLD = "\033[;1m"

RED = RESET+"\033[0;31m"
HIR = RESET+"\033[1;31m"

GRN = RESET+"\033[0;32m"
HIG = RESET+"\033[1;32m"

YEL = RESET+"\033[0;33m"
HIY = RESET+"\033[1;33m"

BLU = RESET+"\033[0;34m"
HIB = RESET+"\033[1;34m"

MAG = RESET+"\033[0;35m"
HIM = RESET+"\033[1;35m"

CYN = RESET+"\033[0;36m"
HIC = RESET+"\033[1;36m"

DEF = RESET+"\033[0;37m"
HIK = RESET+"\033[1;30m"
WHITE = "\033[1:37m"
HIW = RESET+BOLD+WHITE

REVERSE = "\033[;7m"

buffer_line = HIK+'________________________________________________________________________________\n'+RESET+''

def buffer():
    print(buffer_line)

test_string = RED+'RED ' +HIR+'HIR '+GRN+'GRN '+HIG+'HIG '+YEL+'YEL '+HIY+'HIY '+BLU+'BLU '+HIB+'HIB '+MAG+'MAG '+HIM+'HIM '+CYN+'CYN '+HIC+'HIC '+DEF+'DEF '+HIK+'HIK '+HIW+'-!-' +RESET + RESET
