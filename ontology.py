from constants import *

################################################
# Default Base Class to facilitate subclassing #
################################################
class Base:
    def __init__(self, **kwargs):
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])


#################
# Player Object #
#################
class Player(Base):
    def __init__(self,
                 pid,
                 coins=list([]),
                 cards=list([]),
                 reserved_cards=list([]),
                 patrons=list([]),
                 **kwargs):
        super().__init__(**kwargs)
        self.pid = pid
        self.coins = list(coins)
        self.cards = list(cards)
        self.reserved_cards = list(reserved_cards)
        self.patrons = list(patrons)

    def __repr__(self):
        return "Player {}".format(self.pid)


################
# Game Objects #
################
class GameObject(Base):
    '''\
        Superordinate class shared by Card, Noble, and Token.

        is_visible      <bool>      Flag indicating whether an object is 'in-play'.

                                    Cards use is_visible for inferences concerning whether they've
                                    been dealt. We find the top card of a deck by filtering on
                                    is_visible == False, and taking the first element of the list.

                                    Nobles use is_visible to limit which were dealt randomly from
                                    the full set for use in a given game.


        cpid            <int>       Controller player id, default value == -1.
                                    
                                    The default value of -1 implies the object has no controller.

                                    Cards use cpid for inferences concerning:
                                        availability for purchase;
                                        availability for reservation; AND,
                                        Whether they should contribute to summary statistics about:
                                            victory_points;
                                            bonuses for Noble visits;
                                            bonuses for apparent_cost_analysis().
                                        
    '''
    def __init__(self,
                 is_visible,
                 cpid,
                 **kwargs):
        super().__init__(**kwargs)
        self.is_visible = is_visible
        self.cpid = cpid


class Card(GameObject):
    '''\
        Development card class.

        card_id             <int>                       Ordinal index into CARD_SPECS_LIST

        card_spec_list      <List[Union[Str, Int]]>     constants.py contains a list named CARD_SPECS_LIST.
                                                        Each element of CARD_SPECS_LIST is a sublist of the form:
                                                        list[0]    <int in [0:2]>
                                                                   representing the tier deck the card belongs to
                                                        list[1]    <str in NON_JOKER_TOKEN_SYMBOLS>
                                                                   representing the bonus produced by the card.
                                                                   Used by state to make inferences about bonuses
                                                                   for Noble visits and apparent_cost_analysis().
                                                        list[2]    <int in [1:5]>
                                                                   representing the number of victory_points the
                                                                   card contributes to winning.
                                                        list[3:7]  <int in [0:7]>
                                                                   representing the cost component for each gem.

        is_reserved         <bool>                      Flag indicating reservation status of the card.

        is_purchased        <bool>                      Flag indicating purchse status of the card.
    '''
    def __init__(self,
                 card_id,
                 card_spec_list,
                 is_reserved=False,
                 is_purchased=False,
                 **kwargs):
        self.card_id = card_id
        self.card_spec_list = list(card_spec_list)
        self.tier = self.card_spec_list[CARD_TIER_IDX]
        self.bonus = self.card_spec_list[CARD_BONUS_IDX]
        self.victory_points = self.card_spec_list[CARD_VP_IDX]
        self.cost_diamond = self.card_spec_list[CARD_DIAMOND_IDX]
        self.cost_sapphire = self.card_spec_list[CARD_SAPPHIRE_IDX]
        self.cost_emerald = self.card_spec_list[CARD_EMERALD_IDX]
        self.cost_ruby = self.card_spec_list[CARD_RUBY_IDX]
        self.cost_onyx = self.card_spec_list[CARD_ONYX_IDX]
        self.is_reserved = is_reserved
        self.is_purchased = is_purchased
        super().__init__(is_visible=False, cpid=-1, **kwargs)

    def convert_cost_into_string(self):
        result = ""
        result += str(self.cost_diamond)
        result += DIAMOND_CSTR
        result += " "
        result += str(self.cost_sapphire)
        result += SAPPHIRE_CSTR
        result += " "
        result += str(self.cost_emerald)
        result += EMERALD_CSTR
        result += " "
        result += str(self.cost_ruby)
        result += RUBY_CSTR
        result += " "
        result += str(self.cost_onyx)
        result += ONYX_CSTR
        return result

    def repr_facts(self):
        result = []
        if self.is_reserved:
            result.append(DEF+HIC+"  Reserved  "+DEF)
        else:
            result.append(DEF+CYN+"Not Reserved"+DEF)

        if self.is_purchased:
            result.append(DEF+HIM+"  Purchased  "+DEF)
        else:
            result.append(DEF+MAG+"Not Purchased"+DEF)

        if (self.cpid == -1):
            result.append(DEF+HIY+"Free"+DEF)
        else:
            result.append(DEF+YEL+"Player {}".format(self.cpid)+DEF)

        return tuple(result)


    def __repr__(self):
        cost_string = self.convert_cost_into_string()
        res_str, pur_str, con_str = self.repr_facts()
        result = "Card #{} | Tier {} | {} VP | {} | {} | {} | {} | {} |"
        result = result.format(self.card_id, self.tier, self.victory_points, self.bonus.upper(), cost_string, res_str, pur_str, con_str)
        return result


class Noble(GameObject):
    '''\
        Noble objects.

        victory_points  <int>   number of victory points a Noble contributes to the player they visit.
        card_cost
    '''
    def __init__(self,
                 noble_id,
                 victory_points,
                 card_cost,
                 **kwargs):
        self.noble_id = noble_id
        self.victory_points = victory_points
        self.card_cost = card_cost
        super().__init__(is_visible=False, cpid=-1, **kwargs)

    def convert_card_cost_to_string(self):
        result = ""
        for i in range(5):
            n_this_cost = self.card_cost[i]
            str_this_cost = ALL_TOKEN_CSYMBOLS[i]
            result += str(n_this_cost)
            result += str_this_cost
            if (i < 4):
                result += "|"
        return result

    def __repr__(self):
        cost_string = self.convert_card_cost_to_string()
        return "Noble #{} | {} VP | {} |".format(self.noble_id, self.victory_points, cost_string)


class Token(GameObject):
    '''\
        Superordinate class shared by the various gem and joker tokens.

        symbol  <str in ALL_TOKEN_SYMBOLS>  Facilitates inferences about costs and bonuses by providing
                                            a string to participate in combinatorics functions.
                                            This symbol is also used by card.card_spec_list.
    '''
    def __init__(self, **kwargs):
        self.cstr = ""
        super().__init__(is_visible=False, cpid=-1, **kwargs)

    def __repr__(self):
        return "{}".format(self.cstr)


class Joker(Token):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.symbol = JOKER_STR
        self.cstr = JOKER_CSTR


class Onyx(Token):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.symbol = ONYX_STR
        self.cstr = ONYX_CSTR


class Emerald(Token):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.symbol = EMERALD_STR
        self.cstr = EMERALD_CSTR


class Sapphire(Token):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.symbol = SAPPHIRE_STR
        self.cstr = SAPPHIRE_CSTR


class Ruby(Token):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.symbol = RUBY_STR
        self.cstr = RUBY_CSTR


class Diamond(Token):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.symbol = DIAMOND_STR
        self.cstr = DIAMOND_CSTR
