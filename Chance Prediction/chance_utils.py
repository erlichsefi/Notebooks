
def count_match(spades_guess=None,Diamonds_guess=None,Hearts_guess=None,Clubs_guess=None,Spades=None,Diamonds=None,Hearts=None,Clubs=None):
    matchs = 0
    if spades_guess and spades_guess == Spades:
        matchs+=1
    if Hearts_guess and Hearts_guess == Hearts:
        matchs+=1
    if Clubs_guess and Clubs == Spades:
        matchs+=1
    if Diamonds_guess and Diamonds_guess == Diamonds:
        matchs+=1
    return matchs

def compute_winning_amount(amount,Spades_guess=None,Diamonds_guess=None,Hearts_guess=None,Clubs_guess=None,Spades=None,Diamonds=None,Hearts=None,Clubs=None):
    card_filled = len(list(filter(lambda x:x!=None,[Spades_guess,Diamonds_guess,Hearts_guess,Clubs_guess])))
    match_count = count_match(Spades_guess,Diamonds_guess,Hearts_guess,Clubs_guess,Spades,Diamonds,Hearts,Clubs)
    if card_filled == 1 and match_count == 1 :
        return amount*5
    elif card_filled == 2:
        if match_count == 1:
            return amount*0.5
        elif match_count == 2:
            return amount*30
    elif card_filled == 3:
        if match_count == 1:
            return amount*(3/10)
        elif match_count == 2:
            return amount*(7/10)
        elif match_count == 3:
            return amount*300
    elif card_filled == 4:
        if match_count == 1:
            return amount*(2/10)
        elif match_count == 2:
            return amount*(5/10)
        elif match_count == 3:
            return amount*(8/10)
        elif match_count == 4:
            return amount*2000
    return 0
    
def compute_statistics(predictions_cards,true_cards,gambel_amount=100,name=None):
    import locale,uuid
    locale.setlocale( locale.LC_ALL, '' )

    invested = 0
    earned = 0
    won = 0
    for spades_gamble,spades in zip(predictions_cards,true_cards):
        invested += gambel_amount
        current_earned = compute_winning_amount(gambel_amount,Spades=spades,Spades_guess=spades_gamble)
        if current_earned > gambel_amount:
            won+=1
        earned += current_earned
    
    return {
        "name": name if name else uuid.uuid4(),
        "invested":locale.currency(invested, grouping=True),
        "single_bet_amount":locale.currency(gambel_amount, grouping=True),
        "total_invested":locale.currency(invested, grouping=True),
        "total_won":won,
        "precentage_won":(won/len(predictions_cards))*100,
        "expected_won":(1/8)*100,
        "eraned":locale.currency(earned, grouping=True),
        "revenue":locale.currency(earned-invested, grouping=True)   
    }
