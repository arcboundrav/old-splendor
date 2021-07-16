from ontology import *
from itertools import combinations, permutations, chain, product
from time import time

#####################
# Auxillary Functions
#####################
def compute_n_joker():
    return MAX_N_JOKER


def compute_n_token(n_player):
    if (n_player == 2):
        return (MAX_N_TOKEN - 3)
    elif (n_player == 3):
        return (MAX_N_TOKEN - 2)
    else:
        return MAX_N_TOKEN


def compute_n_noble(n_player):
    result = n_player + 1
    return min(MAX_N_NOBLE, result)


def avoid_subzero(number):
    return max(0, number)


##################
# Game State Class
##################
class GameState(Base):
    def __init__(self, n_player, **kwargs):
        self.n_player = n_player

        self.active_player_idx = 0
        self.is_final_turn = False
        self.subphase = START_PLY

        self.n_tokens_drawn_this_ply = 0
        self.tier_to_refill = -1

        self.player_list = list([])
        self.token_list = list([])
        self.noble_list = list([])
        self.card_list = list([])

        self.tier_0_cards = list([])
        self.tier_1_cards = list([])
        self.tier_2_cards = list([])

        self.initial_construction()
        super().__init__(**kwargs)

    def refresh_ply_variables(self):
        self.subphase = START_PLY
        self.n_tokens_drawn_this_ply = 0
        self.tier_to_refill = -1


    def refresh_state(self):
        self.active_player_idx = 0
        self.is_final_turn = False
        self.subphase = START_PLY

        self.n_tokens_drawn_this_ply = 0
        self.tier_to_refill = -1

        self.player_list.clear()
        self.token_list.clear()
        self.noble_list.clear()
        self.card_list.clear()

        self.tier_0_cards.clear()
        self.tier_1_cards.clear()
        self.tier_2_cards.clear()
        self.initial_construction()


    def construct_players(self):
        if not(self.player_list):
            for i in range(self.n_player):
                p = Player(pid=i)
                self.player_list.append(p)

    def construct_tokens(self):
        if not(self.token_list):
            n_joker = compute_n_joker()
            n_token = compute_n_token(self.n_player)
            for i in range(n_token):
                self.token_list.extend([Onyx(), Ruby(), Emerald(), Sapphire(), Diamond()])
            for j in range(n_joker):
                self.token_list.append(Joker())

    def construct_nobles(self):
        if not(self.noble_list):
            for i in range(MAX_N_NOBLE):
                self.noble_list.append(Noble(noble_id=i,
                                             victory_points=N_VP_PER_NOBLE,
                                             card_cost=list(NOBLE_SPECS_LIST[i])))
    def construct_cards(self):
        if not(self.card_list):
            for i, card_specs in enumerate(CARD_SPECS_LIST):
                self.card_list.append(Card(card_id=i, card_spec_list=list(card_specs)))

    def filter_by_boolean_attribute(self, bool_attr, list_of_objects, negate=False):
        return list(filter(lambda card: (getattr(card, bool_attr) != negate), list_of_objects))

    def filter_by_tier(self, tier):
        return list(filter(lambda card: (card.tier == tier), self.card_list))

    def filter_by_pid(self, pid, tokens=False):
        list_of_objects = self.token_list if tokens else self.card_list
        return list(filter(lambda obj: (obj.cpid == pid), list_of_objects))

    def initial_construction(self):
        # Instantiate players
        self.construct_players()
        # Instantiate tokens
        self.construct_tokens()
        # Instantiate nobles
        self.construct_nobles()
        # Instantiate cards
        self.construct_cards()

    def partition_cards_by_tier(self):
        # NOTE #
        # Assumes initial_construction() has been called prior to ensure the relevant objects
        # are instantiated and already populating the relevant state lists.
        self.tier_0_cards = self.filter_by_tier(tier=0)
        self.tier_1_cards = self.filter_by_tier(tier=1)
        self.tier_2_cards = self.filter_by_tier(tier=2)

    def shuffle(self, list_of_objects):
        ''' Shuffle a list of objects in place using NumPy's random module. '''
        np.random.shuffle(list_of_objects)

    def return_undealt_cards(self, list_of_cards):
        ''' A card is considered dealt when card.is_visible == True. '''
        return self.filter_by_boolean_attribute(bool_attr='is_visible',
                                                list_of_objects=list_of_cards,
                                                negate=True)

    def deal(self, deck_of_cards):
        ''' A card is considered dealt when card.is_visible == True. '''
        undealt = self.return_undealt_cards(list_of_cards=deck_of_cards)
        n_undealt = len(undealt)
        # Case: There's at least 1 undealt card to deal in deck
        if n_undealt:
            setattr(undealt[0], "is_visible", True)

    def deal_n(self, n_to_deal, deck_of_cards):
        for i in range(n_to_deal):
            self.deal(deck_of_cards=deck_of_cards)

    def shuffle_decks(self):
        # Assumes partition_cards_by_tier() has been called prior to ensure the distinct decks exist.
        self.shuffle(self.tier_0_cards)
        self.shuffle(self.tier_1_cards)
        self.shuffle(self.tier_2_cards)

    def prepare_initial_deal(self):
        ''' Split the card objects into three lists based on their tier. '''
        self.partition_cards_by_tier()
        self.shuffle_decks()

    def initial_deal(self):
        ''' Make visible the first four cards of each of the development card decks. '''
        decks_to_deal = [self.tier_0_cards, self.tier_1_cards, self.tier_2_cards]
        for deck_to_deal in decks_to_deal:
            self.deal_n(n_to_deal=4, deck_of_cards=deck_to_deal)

    def arrive_at_initial_state(self):
        # Split the cards in self.card_list into the three tier decks
        # self.tier_0_cards, self.tier_1_cards, and self.tier_2_cards;
        # then, shuffle each.
        self.prepare_initial_deal()
        # Deal the top four cards of each deck.
        self.initial_deal()
        # Determine how many nobles will be available this game.
        n_noble = compute_n_noble(self.n_player)
        # Shuffle the constructed nobles
        self.shuffle(self.noble_list)
        # 'Deal' the n_noble top nobles from the shuffled list
        self.deal_n(n_to_deal=n_noble, deck_of_cards=self.noble_list)

    def return_objects_by_symbol(self, symbol, list_of_objects):
        ''' Self-documenting. '''
        return list(filter(lambda obj: (obj.symbol == symbol), list_of_objects))

    def filter_by_pid(self, pid, list_of_objects):
        ''' Self-documenting. '''
        return list(filter(lambda obj: (obj.cpid == pid), list_of_objects))

    def return_objects_by_symbol_and_pid(self, symbol, pid, list_of_objects):
        ''' Self-documenting. '''
        symbol_match = self.return_objects_by_symbol(symbol=symbol, list_of_objects=list_of_objects)
        return self.filter_by_pid(pid=pid, list_of_objects=symbol_match)


    def count_tokens_by_symbol_and_pid(self, symbol, pid):
        '''\
            Return the number of tokens with the given symbol and pid.
        '''
        token_match = self.return_objects_by_symbol_and_pid(symbol=symbol,
                                                            pid=pid,
                                                            list_of_objects=self.token_list)
        return len(token_match)

    def return_reserved_cards_by_pid(self, pid):
        ''' Self-documenting. '''
        cards_controlled_by_pid = self.filter_by_pid(pid=pid, list_of_objects=self.card_list)
        return self.filter_by_boolean_attribute(bool_attr="is_reserved",
                                                list_of_objects=cards_controlled_by_pid)

    def count_reserved_cards_by_pid(self, pid):
        ''' Self-documenting. '''
        cards_reserved_by_pid = self.return_reserved_cards_by_pid(pid=pid)
        return len(cards_reserved_by_pid)


    def return_purchased_cards_by_pid(self, pid):
        ''' Self-documenting. '''
        cards_controlled_by_pid = self.filter_by_pid(pid=pid, list_of_objects=self.card_list)
        return self.filter_by_boolean_attribute(bool_attr="is_reserved",
                                                list_of_objects=cards_controlled_by_pid,
                                                negate=True)


    def return_bonus_by_symbol_and_pid(self, symbol, pid):
        '''\
            Return the discount on cost components of a given symbol for a given player
            based on their purchased cards.
        '''
        cards_purchased_by_pid = self.return_purchased_cards_by_pid(pid=pid)
        cards_purchased_by_pid_with_given_bonus = list(filter(lambda card: (card.bonus == symbol), cards_purchased_by_pid))
        return len(cards_purchased_by_pid_with_given_bonus)

    def solve_wide_draw_combinations(self):
        '''\
            Return the set of 3-combinations of uncontrolled non-Joker tokens
            the active_player might choose to draw.
        '''
        result = []
        symbols_for_wide_draw = []
        for token_symbol in NON_JOKER_TOKEN_SYMBOLS:
            token_count = self.count_tokens_by_symbol_and_pid(symbol=token_symbol,
                                                              pid=-1)
            # Case: There are enough tokens with this symbol to participate in a wide draw.
            if (token_count >= MIN_N_TOKEN_FOR_WIDE_DRAW):
                symbols_for_wide_draw.append(token_symbol)

        # Case: There are enough available unique tokens to perform a wide draw.
        if (len(symbols_for_wide_draw) >= N_TOKEN_PER_WIDE_DRAW):
            result = list(combinations(symbols_for_wide_draw, N_TOKEN_PER_WIDE_DRAW))
        return result


    def solve_double_draw_combinations(self):
        '''\
            Return the set of non-Joker token types which have enough remaining
            uncontrolled members to qualify for a double draw.
        '''
        symbols_for_double_draw = []
        for token_symbol in NON_JOKER_TOKEN_SYMBOLS:
            token_count = self.count_tokens_by_symbol_and_pid(symbol=token_symbol,
                                                              pid=-1)
            # Case: There are enough tokens with this symbol to participate in a wide draw.
            if (token_count >= MIN_N_TOKEN_FOR_DOUBLE_DRAW):
                symbols_for_double_draw.append(token_symbol)

        return [(symbol, symbol) for symbol in symbols_for_double_draw]


    def convert_token_symbol_combination(self, combo):
        '''\
            A wide draw combination is a tuple of symbols. This method returns
            a list of uncontrolled Tokens with the same symbol composition.
        '''
        result = []
        token_ids_so_far = []
        for symbol in combo:
            match_tokens = self.return_objects_by_symbol_and_pid(symbol=symbol,
                                                                 pid=-1,
                                                                 list_of_objects=self.token_list)
            for token in match_tokens:
                token_id = id(token)
                # Case: We haven't used this token yet.
                if not(token_id in token_ids_so_far):
                    token_ids_so_far.append(token_id)
                    result.append(token)
                    break
        return list(result)


    def player_can_reserve_card(self, pid):
        '''\
            Predicate concerning whether a player is permitted to reserve a card
            given how many they currently have reserved.
        '''
        return (self.count_reserved_cards_by_pid(pid=pid) < MAX_N_RESERVED_CARD)

    def determine_joker_reward(self):
        '''\
            Existential predicate for uncontrolled Joker tokens.
        '''
        uncontrolled_jokers = self.return_objects_by_symbol_and_pid(symbol="j",
                                                                    pid=-1,
                                                                    list_of_objects=self.token_list)
        if uncontrolled_jokers:
            # Make the active player the controller of an uncontrolled Joker token
            attain_joker_consequent = Consequent(ref_obj=uncontrolled_jokers[0],
                                                 ref_attr="cpid",
                                                 new_value=self.active_player_idx)

            # Alert the state to reflect n_tokens_drawn_this_ply to 1
            n_token_drawn_consequent = Consequent(ref_obj=GAMESTATE,
                                                  ref_attr="n_tokens_drawn_this_ply",
                                                  new_value=1)
            return [attain_joker_consequent, n_token_drawn_consequent]
        return None

    def return_eligible_cards_to_purchase_by_pid(self, pid):
        '''\
            Return the list of cards which are eligible for purchasing.
        '''
        visible_cards = self.filter_by_boolean_attribute(bool_attr="is_visible",
                                                         list_of_objects=self.card_list)
        uncontrolled_visible_cards = self.filter_by_pid(pid=-1,
                                                        list_of_objects=visible_cards)
        cards_reserved_by_pid = self.return_reserved_cards_by_pid(pid=pid)
        eligible_cards_to_purchase_for_player_with_given_pid = cards_reserved_by_pid + uncontrolled_visible_cards
        return eligible_cards_to_purchase_for_player_with_given_pid


    def return_eligible_cards_to_reserve_by_pid(self, pid):
        ''' Self-documenting. '''
        visible_cards = self.filter_by_boolean_attribute(bool_attr="is_visible",
                                                         list_of_objects=self.card_list)
        uncontrolled_visible_cards = self.filter_by_pid(pid=-1,
                                                        list_of_objects=visible_cards)

        undealt_t0 = self.return_undealt_cards(list_of_cards=self.tier_0_cards)
        undealt_t1 = self.return_undealt_cards(list_of_cards=self.tier_1_cards)
        undealt_t2 = self.return_undealt_cards(list_of_cards=self.tier_2_cards)

        decks_to_check = [undealt_t0, undealt_t1, undealt_t2]
        for deck_to_check in decks_to_check:
            if deck_to_check:
                uncontrolled_visible_cards.append(deck_to_check[0])
        return uncontrolled_visible_cards


    def apparent_cost_analysis(self, pid, card):
        '''\
            Return the true cost of a card otherwise eligible for purchasing,
            in view of the bonus resource values afforded to them by their
            currently owned cards.
        '''
        discount_diamond = avoid_subzero(card.cost_diamond - self.return_bonus_by_symbol_and_pid(symbol="w", pid=pid))
        discount_sapphire = avoid_subzero(card.cost_sapphire - self.return_bonus_by_symbol_and_pid(symbol="b", pid=pid))
        discount_emerald = avoid_subzero(card.cost_emerald - self.return_bonus_by_symbol_and_pid(symbol="g", pid=pid))
        discount_ruby = avoid_subzero(card.cost_ruby - self.return_bonus_by_symbol_and_pid(symbol="r", pid=pid))
        discount_onyx = avoid_subzero(card.cost_onyx - self.return_bonus_by_symbol_and_pid(symbol="o", pid=pid))
        return {"w":discount_diamond, "b":discount_sapphire, "g":discount_emerald, "r":discount_ruby, "o":discount_onyx}

    def cost_payable(self, cd, pcd):
        excess = 0
        for component in cd:
            n_component = cd[component]
            if n_component:
                n_available = pcd[component]
                delta_n = n_component - n_available
                if delta_n:
                    excess += delta_n
        excess -= pcd['j']
        if (excess < 1):
            return True
        else:
            return False

    def determine_purchase_choices(self, pid):
        '''\
            Return the list of cards which are:
                eligible for purchasing; AND,
                have a cost, after taking bonus resource values into account, which can be
                paid with or without Tokens.
        '''
        jokers_by_pid = self.return_objects_by_symbol_and_pid(symbol="j",
                                                              pid=pid,
                                                              list_of_objects=self.token_list)
        n_jokers_by_pid = len(jokers_by_pid)

        affordable_cards = []
        final_analysis_excess = 0

        # 1) Start with cards the player with given pid can purchase
        eligible_cards_to_purchase_by_pid = self.return_eligible_cards_to_purchase_by_pid(pid=pid)

        # 2) For each of these eligible cards, compute the apparent_cost_analysis
        for eligible_card in eligible_cards_to_purchase_by_pid:
            final_analysis_excess = 0
            cost_analysis_dict = self.apparent_cost_analysis(pid=pid, card=eligible_card)

        # 3) Given an apparent cost analysis, for each key that has a value > zero,
        #    subtract the number of tokens of the corresponding symbol controlled by player with given pid
            for symbol_qua_key in cost_analysis_dict:
                symbol_value = cost_analysis_dict[symbol_qua_key]
                if symbol_value:
                    n_tokens_to_pay_excess = self.count_tokens_by_symbol_and_pid(symbol=symbol_qua_key,
                                                                                 pid=pid)
                    final_analysis_excess += avoid_subzero(symbol_value - n_tokens_to_pay_excess)

        # 4) Subtract n_jokers_by_pid from final_analysis_excess
            final_analysis_excess -= n_jokers_by_pid
            final_analysis_excess = avoid_subzero(final_analysis_excess)

            if not(final_analysis_excess):
                affordable_cards.append(eligible_card)

        return list(affordable_cards)


    def gather_tokens_given_pid(self, pid):
        result = {}
        for symbol in ALL_TOKEN_SYMBOLS:
            result[symbol] = list(self.return_objects_by_symbol_and_pid(symbol=symbol,
                                                                        pid=pid,
                                                                        list_of_objects=self.token_list))
        return dict(list(result.items()))

    def tally_victory_points(self, pid):
        vp_result = 0
        n_purchased_result = 0
        player_cards = self.return_purchased_cards_by_pid(pid)
        player_nobles = self.filter_by_pid(pid, self.noble_list)
        for card in player_cards:
            vp_result += card.victory_points
            n_purchased_result += 1
        for noble in player_nobles:
            vp_result += noble.victory_points
        return (vp_result, n_purchased_result, pid)

    def determine_winner(self):
        victory_tuples = []
        for i in range(self.n_player):
            this_player_victory_tuple = self.tally_victory_points(pid=i)
            victory_tuples.append(this_player_victory_tuple)

        sorted_victory_tuples = sorted(victory_tuples, key=lambda t: t[0], reverse=True)
        print("sorted_victory_tuples: {}".format(sorted_victory_tuples))
        best_vp = sorted_victory_tuples[0][0]
        print("best_vp: {}".format(best_vp))
        victory_tuples = list(filter(lambda t: (t[0] == best_vp), sorted_victory_tuples))
        print("victory_tuples: {}".format(victory_tuples))
        sorted_victory_tuples = sorted(victory_tuples, key=lambda t: t[1])
        print("sorted_victory_tuples: {}".format(sorted_victory_tuples))
        best_n_purchased = sorted_victory_tuples[0][1]
        print("best_n_purchased: {}".format(best_n_purchased))
        victory_tuples = list(filter(lambda t: (t[1] == best_n_purchased), sorted_victory_tuples))
        print("victory_tuples: {}".format(victory_tuples))
        winning_pids = [t[2] for t in victory_tuples]
        print("winning_pids: {}".format(winning_pids))
        winning_players = [self.player_list[winning_pid] for winning_pid in winning_pids]
        print("Winning Players:")
        for winning_player in winning_players:
            print(winning_player)

    def advance_active_player_idx(self):
        if (self.active_player_idx < (self.n_player - 1)):
            self.active_player_idx += 1
        else:
            self.active_player_idx = 0

    def advance_subphase(self):
        ''' Called by the enactment of the ADVANCE_SUBPHASE_CONSEQUENT. '''
        # Case: We're completed the final subphase
        if (self.subphase == WINNER_CHECK):
            # Case: It's the final turn.
            if self.is_final_turn:
                self.determine_winner()
            # Case: More turns to go.
            else:
                self.refresh_ply_variables()
                self.advance_active_player_idx()
        # Case: Otherwise
        else:
            self.subphase += 1


    def view_player(self, pid):
        player_object = self.player_list[pid]
        player_tokens = self.filter_by_pid(pid, self.token_list)
        player_tokens = sorted(player_tokens, key=lambda t: t.symbol)
        player_cards = self.filter_by_pid(pid, self.card_list)
        player_nobles = self.filter_by_pid(pid, self.noble_list)
        result = "___________________________________________________________________________\n"
        result += player_object.__repr__()
        if player_tokens:
            result += "\n________\n"
            result += "Tokens"
            result += "\n________\n"
            for token in player_tokens:
                result += token.__repr__()
        if player_cards:
            result += "\n________\n"
            result += "Cards"
            result += "\n________\n"
            for card in player_cards:
                result += card.__repr__()
        if player_nobles:
            result += "\n________\n"
            result += "Nobles"
            result += "\n________\n"
            for noble in player_nobles:
                result += noble.__repr__()

        result += "\n___________________________________________________________________________"
        print(result)


    def verify_product(self, product_to_verify):
        keepers = []
        flat_item = list(chain.from_iterable(product_to_verify))
        obj_as_ids = [id(obj) for obj in flat_item]
        n_original = len(obj_as_ids)
        obj_as_ids_as_set = list(set(obj_as_ids))
        n_after_set = len(obj_as_ids_as_set)
        return bool(n_original == n_after_set)


    def combo_into_player_bank_dict(self, combo):
        base_dict = {}
        for symbol in ALL_TOKEN_SYMBOLS:
            base_dict[symbol] = []
        for object in combo:
            base_dict[object.symbol].append(object)
        return dict(list(base_dict.items()))

    def return_player_count_dict(self, player_bank_dict):
        base_dict = {}
        for key in ALL_TOKEN_SYMBOLS:
            base_dict[key] = len(player_bank_dict[key])
        return dict(list(base_dict.items()))

    def validate_combos(self, combos, cost_dict):
        result = []
        for combo in combos:
            pbd = self.combo_into_player_bank_dict(combo)
            pcd = self.return_player_count_dict(pbd)
            if self.cost_payable(cost_dict, pcd):
                result.append(combo)
        return list(result)

    def combo_to_signature(self, combo):
        return "".join(sorted([obj.symbol for obj in combo]))

    def unique_signatures(self, combos):
        signatures = set([])
        keepers = []
        for combo in combos:
            sig = self.combo_to_signature(combo)
            if not(sig in signatures):
                keepers.append(combo)
                signatures.add(sig)
        return keepers

    def brute_force_ways_to_pay(self, ref_card, ref_pid):
        cost_analysis_dict = self.apparent_cost_analysis(pid=ref_pid, card=ref_card)
        player_bank_dict = self.gather_tokens_given_pid(pid=ref_pid)
        player_count_dict = self.return_player_count_dict(player_bank_dict)

        total_cost = 0
        new_substrate = list(player_bank_dict['j'])
        all_tokens = self.filter_by_pid(pid=0, list_of_objects=self.token_list)

        # Save a little time by removing from consideration all tokens whose symbol
        # does not appear in the cost, and by removing excess tokens.
        for key, val in cost_analysis_dict.items():
            if not(val):
                all_tokens = list(filter(lambda token: not(token.symbol == key), all_tokens))
            else:
                total_cost += val
                new_substrate.extend(player_bank_dict[key][:val+1])
        all_tokens = list(new_substrate)
        combos = list(combinations(all_tokens, total_cost))
        valid_combos = self.validate_combos(combos, cost_analysis_dict)
        return self.unique_signatures(valid_combos)


    def verify_intact_tiers(self):
        '''\
            Handle needing to replace cards that are purchased or reserved (except when
            they are reserved from the top of a tier deck directly.
        '''
        pass

    def determine_legal_actions_(self):
        legal_actions = []

        wide_draw_combos = self.solve_wide_draw_combinations()
        for wd_combo in wide_draw_combos:
            wide_draw_action = WideDraw(symbols=wd_combo,
                                        actor_pid=self.active_player_idx)
            wide_draw_action.generate_consequents()
            legal_actions.append(wide_draw_action)

        double_draw_combos = self.solve_double_draw_combinations()
        for dd_combo in double_draw_combos:
            double_draw_action = DoubleDraw(symbols=dd_combo,
                                            actor_pid=self.active_player_idx)
            double_draw_action.generate_consequents()
            legal_actions.append(double_draw_action)

        n_cards_reserved_by_active_player = self.count_reserved_cards_by_pid(pid=self.active_player_idx)
        # Case: Player hasn't hit the limit on number of reserved cards.
        if self.player_can_reserve_card(pid=self.active_player_idx):
            # This will return either a list of two consequents, one for attaining a joker token,
            # the other for updating the state that 1 token was drawn this ply. OR;
            # None, if there are no free joker tokens left.
            extra_joker_consequents = self.determine_joker_reward()
            cards_eligible_to_reserve = self.return_eligible_cards_to_reserve_by_pid(pid=self.active_player_idx)
            for card_to_reserve in cards_eligible_to_reserve:
                reservation_action = ReserveCard(ref_card=card_to_reserve,
                                                 actor_id=self.active_player_idx)
                reservation_action.generate_consequents()
                if (extra_joker_consequents is not None):
                    reservation_action.consequents.extend(extra_joker_consequents)

                # Case: Was this card reserved directly from the top of a deck?
                if not(card_to_reserve.is_visible):
                    reservation_action.consequents.append(Consequent(ref_obj=card_to_reserve,
                                                                     ref_attr="is_visible",
                                                                     new_value=True))
                    reservation_action.consequents.append(Consequent(ref_obj=GAMESTATE,
                                                                     ref_attr="tier_to_refill",
                                                                     new_value=card_to_reserve.tier))
                legal_actions.append(reservation_action)


        cards_eligible_to_purchase = self.return_eligible_cards_to_purchase_by_pid(pid=self.active_player_idx)
        # A contract is a 2-tuple of the form:
        #   (<Card>, <List[Token]>) where:
        #       contract[0] is the Card to purchase; and,
        #       contract[1] is a list of Tokens constituting a unique method of payment.
        contracts = []
        for card_to_purchase in cards_eligible_to_purchase:
            ways_to_pay = self.brute_force_ways_to_pay(ref_card=card_to_purchase,
                                                       ref_pid=self.active_player_idx)
            for way in ways_to_pay:
                contracts.append((card_to_purchase, way))

            for contract in contracts:
                purchase_action = PurchaseCard(ref_card=contract[0],
                                               actor_id=self.active_player_idx,
                                               way_to_pay=contract[1])
                purchase_action.generate_consequents()
                legal_actions.append(purchase_action)

        for legal_action in legal_actions:
            legal_action.consequents.append(ADVANCE_SUBPHASE_CONSEQUENT)


        # Following a choice and execution of a Fundamental Action, State Based Actions take place.
        # First:
        #   NOBLE_CHECK
        #       Daemon determines the subset(noble_list) S such that:
        #           For each noble in S, the active player possesses adequate cards to pay their card costs.
        #           If (|S| > 1):
        #               NOBLE_CHOICE
        #                   Active player chooses which noble they attain.
        #           Elif (|S| == 1):
        #                   Active player attains S[0].
        #           Else
        #               Nothing happens w.r.t. noble control.
        #   # NOTE # Unlike cards, once a noble visits someone, there's no replacement of the tiles.
        #
        # Second:
        #   MAX_N_TOKEN_CHECK
        #       Daemon determines whether the active player currently has > MAX_N_TOKEN_PER_PLAYER.
        #       If they do:
        #           TOKEN_CLEAN_UP
        #               current_n_token_controlled := # of tokens controlled by the active player at this point
        #               minimum_delta    := (current_n_token_controlled - 10)
        #               maximum_delta    := max(minimum_delta, n_tokens_drawn_this_ply(active player))
        #               Active player chooses to discard a subset of their tokens with cardinality
        #               in the closed interval [minimum_delta, maximum_delta].
        #       Else:
        #           FORCE_TOKEN_CLEAN_UP
        #               # NOTE # If we want symmetry in tree depth, then we silently force player
        #                        to choose to discard 0 tokens this turn.
        # Third:
        #   If a card was purchased this ply:
        #       Daemon deals a single card from the corresponding tier deck, if any remain within.
        #
        # Fourth:
        #   Daemon determines whether the active player's n_victory_points >= MIN_VP_TO_WIN.
        #   If it does:
        #       If !STATE.is_final_turn:
        #           STATE.is_final_turn := TRUE
        #       active_player.final_score = active_player.n_victory_points
        #   Else:
        #       void()
        #
        # Fifth:
        #   Daemon determines whether this was the final ply in a turn.
        #   If it is:
        #       If STATE.is_final_turn:
        #           The winner is determined.
        #       Else:
        #           We increment the n_turns counter and set STATE.active_player_idx to 0.
        #   Else:
        #       We increment STATE.active_player_idx by 1.
        #

        # Determining the Winner
        #   Sort players by n_victory_points (we know >0 players have n_victory_points >= MIN_VP_TO_WIN).
        #   If there are any ties:
        #       From among the tied players, compare number of purchased lands among them.
        #       If there are any ties:
        #           It's a tie, no winner.
        #       Else:
        #           The player with fewer number of purchased lands wins.
        #   Else:
        #       The player with the highest n_victory_points is the winner.
        return list(legal_actions)


    def noble_visit(self, noble, pid):
        noble_cost = noble.card_cost
        non_zero_costs = list(filter(lambda i: i, noble_cost))
        costs_met = 0
        for i in range(len(noble_cost)):
            this_cost = noble_cost[i]
            this_symbol = NON_JOKER_TOKEN_SYMBOLS[i]
            player_bonus = self.return_bonus_by_symbol_and_pid(this_symbol, pid)
            if (player_bonus >= this_cost):
                costs_met += 1
        return (costs_met == non_zero_costs)


    def noble_check_actions(self):
        visitors = []
        for noble in self.noble_list:
            if (noble.is_visible):
                if (noble.cpid == -1):
                    if self.noble_visit(noble, self.active_player_idx):
                        visitors.append(noble)
        visit_actions = []
        for visitor in visitors:
            visit_action = AttainNoble(ref_noble=visitor,
                                       ref_pid=self.active_player_idx)
        if not(visitors):
            visit_actions.append(NULL_SUBPHASE_ACTION)

        return list(visit_actions)


    def get_deck_by_tier(self, tier):
        if (tier == 0):
            return self.tier_0_cards
        elif (tier == 1):
            return self.tier_1_cards
        elif (tier == 2):
            return self.tier_2_cards


    def refill_check_actions(self):
        refill_actions = []
        # Case: None of the tiers need to refill a card
        if (self.tier_to_refill == -1):
            refill_actions.append(NULL_SUBPHASE_ACTION)
        else:
            # Case: Tier needs to refill a card, but it's empty.
            tier_to_refill = self.get_deck_by_tier(self.tier_to_refill)
            undealt_cards = self.return_undealt_cards(tier_to_refill)
            if not(undealt_cards):
                refill_actions.append(NULL_SUBPHASE_ACTION)
            else:
                refill_actions.append(RefillAction(ref_tier=self.tier_to_refill))
        return list(refill_actions)


    def winner_check_actions(self):
        return [WinnerCheckAction(ref_pid=self.active_player_idx)]

    def simplify_tokens(self, list_of_tokens, max_n_token):
        counter = {}
        for symbol in ALL_TOKEN_SYMBOLS:
            counter[symbol] = 0

        keepers = []
        for token in list_of_tokens:
            n_token_so_far = counter[token.symbol]
            if (n_token_so_far < max_n_token):
                counter[token.symbol] += 1
                keepers.append(token)
        return list(keepers)


    def max_n_token_check_actions(self):
        return_extra_token_actions = []
        active_player_tokens = self.filter_by_pid(self.active_player_idx,
                                                  self.token_list)
        n_active_player_tokens = len(active_player_tokens)

        # Case: We need to return some tokens.
        if (n_active_player_tokens > MAX_N_TOKEN_PER_PLAYER):
            token_delta = MAX_N_TOKEN_PER_PLAYER - n_active_player_tokens
            simplified_tokens = self.simplify_tokens(active_player_tokens, token_delta)
            token_return_combos = list(combinations(simplified_tokens, token_delta))
            for combo in token_return_combos:
                return_extra_token_actions.append(ReturnTokensAction(ref_tokens=combo))

        # Case: No tokens to return
        else:
            return_extra_token_actions.append(NULL_SUBPHASE_ACTION)
        return list(return_extra_token_actions)


    def determine_legal_actions(self):
        # Case: Start of a player's ply
        if (self.subphase == START_PLY):
            return self.determine_legal_actions_()
        # Case: Noble visit check
        elif (self.subphase == NOBLE_CHECK):
            return self.noble_check_actions()
        # Case: Max n_token cleanup
        elif (self.subphase == N_TOKEN_CHECK):
            return self.max_n_token_check_actions()
        # Case: Refill the board if necessary
        elif (self.subphase == REFILL_CHECK):
            return self.refill_check_actions()
        # Case: Check to see if active_player's victory points
        #       imply that this is the final turn.
        elif (self.subphase == WINNER_CHECK):
            return self.winner_check_actions()


    def heartbeat(self):
        pass



GAMESTATE = GameState(n_player=2)
X = GAMESTATE

###########################
# Actions and Consequents #
###########################
class Consequent(Base):
    '''\
        Encode an intended change to a specific attribute of a specific reference object.

        ref_obj     <GameObject>        Object to modify.
        ref_attr    <str>               Attribute of the object to modify.
        new_value   <Any>               The new value to assign to the attribute of the reference object
                                        when this consequent is enacted by its superordinate Action.
    '''
    def __init__(self,
                 ref_obj,
                 ref_attr,
                 new_value,
                 **kwargs):
        self.ref_obj = ref_obj
        self.ref_attr = ref_attr
        self.new_value = new_value
        super().__init__(**kwargs)

    def enact(self):
        setattr(self.ref_obj, self.ref_attr, self.new_value)

class SubphaseConsequent(Consequent):
    def __init__(self):
        pass

    def enact(self):
        GAMESTATE.advance_subphase()

ADVANCE_SUBPHASE_CONSEQUENT = SubphaseConsequent()

class Action(Base):
    '''\
        Represent a bundle of related modifications to the state.

        antecedents <List[Antecedent]>  Currently unused, but typically encodes preconditions which
                                        must be verified for this Action to be cleared to enact its
                                        consequents.

        consequents <List[Consequent]>  Collection of related intended modifications to the state
                                        enacted 'simultaneously' from the Daemon's PoV when this
                                        Action is under-taken.
    '''
    def __init__(self,
                 antecedents=[],
                 consequents=[],
                 **kwargs):
        self.antecedents = list(antecedents)
        self.consequents = list(consequents)
        super().__init__(**kwargs)

    def generate_consequents(self):
        ''' Method to over-ride in subclasses. Transforms parameters into consequents. '''
        pass

    def enact_consequents(self):
        for consequent in self.consequents:
            consequent.enact()

class NullSubphaseAction(Action):
    def __init__(self):
        self.consequents = []

    def generate_consequents(self):
        self.consequents = [ADVANCE_SUBPHASE_CONSEQUENT]

    def enact_consequents(self):
        self.generate_consequents()
        for consequent in self.consequents:
            consequent.enact()

NULL_SUBPHASE_ACTION = NullSubphaseAction()



class TokenDraw(Action):
    '''\
        Represent the primitive action of drawing >=1 uncontrolled Tokens.

        symbols     <Tuple[str in ALL_TOKEN_SYMBOLS]>
                    each element of the tuple is a symbol representing
                    one of the Tokens to draw.

        actor_pid   <int>
                    used to identify the player who is drawing the tokens.
    '''
    def __init__(self,
                 symbols,
                 actor_pid,
                 **kwargs):
        self.symbols = symbols
        self.actor_pid = actor_pid
        super().__init__(**kwargs)


    def generate_consequents(self):
        self.consequents.clear()
        token_objects_to_draw = GAMESTATE.convert_token_symbol_combination(self.symbols)
        for token_object in token_objects_to_draw:
            self.consequents.append(Consequent(ref_obj=token_object,
                                               ref_attr='cpid',
                                               new_value=self.actor_pid))

        # Add a consequent that allows us to tell the State how many tokens were drawn
        # by the active player this ply, to support token clean up state based action.
        self.consequents.append(Consequent(ref_obj=GAMESTATE,
                                           ref_attr='n_tokens_drawn_this_ply',
                                           new_value=len(self.symbols)))


class WideDraw(TokenDraw):
    '''\
        Represent the Fundamental action of drawing three uncontrolled non-Joker tokens
        of the different colours.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class DoubleDraw(TokenDraw):
    '''\
        Represents the Fundamental action of drawing two uncontrolled non-Joker tokens
        of the same colour.
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ReserveCard(Action):
    '''\
        Represents the action of reserving a development card.
    '''
    def __init__(self,
                 ref_card,
                 actor_id,
                 **kwargs):
        super().__init__(**kwargs)
        self.ref_card = ref_card
        self.actor_id = actor_id

    def generate_consequents(self):
        self.consequents.clear()
        self.consequents.append(Consequent(ref_obj=self.ref_card,
                                           ref_attr='is_reserved',
                                           new_value=True))
        self.consequents.append(Consequent(ref_obj=self.ref_card,
                                           ref_attr='cpid',
                                           new_value=self.actor_id))

class PurchaseCard(Action):
    '''\
        Represents the action of purchasing a development card.
        ref_card    <Card>          card to purchase
        actor_id    <int>           pid of player purchasing card
        way_to_pay  <List[Token]>   tokens used to pay in this method of payment.
    '''
    def __init__(self,
                 ref_card,
                 actor_id,
                 way_to_pay,
                 **kwargs):
        super().__init__(**kwargs)
        self.ref_card = ref_card
        self.actor_id = actor_id
        self.way_to_pay = list(way_to_pay)

    def generate_consequents(self):
        self.consequents.clear()
        # If the card is reserved, it will already have its cpid matching
        # the player who purchased it, since only players who reserved a card
        # can purchase that card.
        # If it isn't reserved, that means it will not have had its cpid matched yet,
        # and the GAMESTATE will need to try to refill a card from its tier.
        if self.ref_card.is_reserved:
            self.consequents.append(Consequent(ref_obj=self.ref_card,
                                               ref_attr='is_reserved',
                                               new_value=False))
        else:
            self.consequents.append(Consequent(ref_obj=self.ref_card,
                                               ref_attr='cpid',
                                               new_value=self.actor_id))
            self.consequents.append(Consequent(ref_obj=GAMESTATE,
                                               ref_attr='tier_to_refill',
                                               new_value=self.ref_card.tier))

        # Send the tokens used to pay back into the communal pool.
        for payment_token in self.way_to_pay:
            self.consequents.append(Consequent(ref_obj=payment_token,
                                               ref_attr='cpid',
                                               new_value=-1))

class AttainNoble(Action):
    '''\
        Represent the action of choosing a noble to visit you.
    '''
    def __init__(self, ref_noble, ref_pid, **kwargs):
        super().__init__(**kwargs)
        self.ref_noble = ref_noble
        self.ref_pid = ref_pid

    def generate_consequents(self):
        self.consequents.clear()
        self.consequents.append(Consequent(ref_obj=self.ref_noble,
                                           ref_attr='cpid',
                                           new_value=self.ref_pid))

class RefillAction(Action):
    '''\
        Represent the action of replacing a development card that has
        been either reserved or purchased.
    '''
    def __init__(self, ref_tier, **kwargs):
        super().__init__(**kwargs)
        self.ref_tier = ref_tier

    def generate_consequents(self):
        pass

    def enact_consequents(self):
        deck_to_deal_from = GAMESTATE.get_deck_by_tier(self.ref_tier)
        GAMESTATE.deal(deck_to_deal_from)


class WinnerCheckAction(Action):
    '''\
        Daemon action to figure out if we're in the final round or not.
    '''
    def __init__(self, ref_pid):
        self.ref_pid = ref_pid

    def generate_consequents(self):
        self.consequents = [ADVANCE_SUBPHASE_CONSEQUENT]

    def enact_consequents(self):
        victory_tuple = GAMESTATE.tally_victory_points(self.ref_pid)
        if (victory_tuple[0] >= MIN_VP_TO_WIN):
            GAMESTATE.is_final_turn = True
        self.generate_consequents()
        super().enact_consequents()

class ReturnTokensAction(Action):
    '''\
        Represent the action of returning a Token to the communal collection.
    '''
    def __init__(self, ref_tokens):
        self.ref_tokens = ref_tokens

    def generate_consequents(self):
        self.consequents.clear()
        for token in self.ref_tokens:
            self.consequents.append(Consequent(ref_obj=token,
                                               ref_attr="cpid",
                                               new_value=-1))

X.arrive_at_initial_state()

def y():
    legal = X.determine_legal_actions()
    print("Legal Actions: {}".format(legal))
    print("Current Subphase: {}".format(X.subphase))
    print("Active Player Idx: {}".format(X.active_player_idx))
    legal[0].enact_consequents()
