from random import shuffle
class Card():
  SUITS = ['S', 'H', 'D', 'C']
  SUITS_UNI = {'S': u'\u2660', 'H': u'\u2665', 'D': u'\u2666', 'C': u'\u2663'}
  A = 100
  J = 101
  Q = 102
  K = 103
  VALUES = [A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K]
  FACE_CARDS = {A: 'A', J: 'J', Q: 'Q', K: 'K'}
  def __init__(self, value, suit):
    self.value = value
    self.suit = suit
    self.face_down = False

  def set_face_down(self, is_face_down):
    self.face_down = is_face_down

  def int_value(self):
    if self.value in self.FACE_CARDS:
      if self.value == self.A:
        return [1, 11]
      return 10
    return self.value

  def str_value(self):
    if self.value in self.FACE_CARDS:
      return self.FACE_CARDS[self.value]
    return str(self.value)

  def str_suit(self):
    return (self.SUITS_UNI[self.suit]).encode('utf-8')


  def _suit(self):
    return self.suit

  def is_ace(self):
    return self.value == self.A

  def __str__(self):
    if self.face_down:
      return '??'
    return self.str_suit() + ' ' + str(self.str_value())

class Blackjack():
  # possible states
  NEW_GAME = 0
  PLAYERS_TURN = 1
  DEALERS_TURN = 2
  END_GAME = 3
  NEW_ROUND = 4
  def __init__(self, starting_bal = 500):
    self.state = self.NEW_GAME
    self.player_wins = 0
    self.player_losses = 0
    self.total_rounds = 0
    self.player_busted = False
    self.players_hand = []
    self.dealers_hand = []
    self.deck = []
    self.player_bal = starting_bal

    self.best_player_val = -1
    self.best_dealer_val = -1
    self.player_values = []
    self.dealer_values = []
    self.player_bet = 0
    # init deck
    for suit in Card.SUITS:
      for value in Card.VALUES:
        self.deck.append(Card(value, suit))
        pass
    self.round_num = 0

  def new_game_state(self):
    shuffle(self.deck)
    self.new_round_state()

  def __update_hand(self, player):
    if player:
      hand = self.players_hand
    else:
      hand = self.dealers_hand
    values = self.__get_hand_value(hand)
    busted = values[0] > 21
    best_val = -1
    for value in values:
      if value <= 21 and value > best_val:
        best_val = value

    if player:
      self.player_values = values
      self.player_busted = busted
      self.player_best_val = best_val
    else:
      self.dealer_values = values
      self.dealer_busted = busted
      self.dealer_best_val = best_val


  def players_turn_state(self, should_print_info = True, must_stand = False):
    if should_print_info:
      self.__print_player_info()
    else:
      print 'Your turn'
    if self.player_busted:
      return self.end_game_state()
    # ask for either hit, stand, or double down (if allowed)
    can_dd = self.player_bal >= self.player_bet

    HIT = 0
    STAND = 1
    DD = 2

    while True:
      if must_stand:
        action = STAND
        break
      if can_dd:
        print 'Would you like to hit (h), stand (s), or double down (d)?'
      else:
        print 'Would you like to hit (h) or stand (s)?'
      inp = raw_input('--> ')
      inp = inp.lower()
      if len(inp) > 0:
        if inp[0] == 'h':
          action = HIT
          break
        elif inp[0] == 's':
          action = STAND
          break
        elif inp[0] == 'd' and can_dd:
          action = DD
          break
    if action == HIT:
      # deal to player
      self.players_hand.append(self.deck.pop())
      self.__update_hand(True)
      print 'Hit'
      return self.players_turn_state()
    elif action == STAND:
      # stand, dealer's turn
      print 'Stand'
      return self.dealers_turn_state(False)
    elif action == DD:
      # player chose to double down
      self.player_bal -= self.player_bet
      self.player_bet += self.player_bet
      self.players_hand.append(self.deck.pop())
      self.__update_hand(True)
      self.__shuffle_deck()
      print 'Double down'
      print 'Balance: $' + str(self.player_bal)
      return self.players_turn_state(must_stand = True)

    return NotImplementedError

  def dealers_turn_state(self, subsequent_round = True):
    # dealer's cards can now be face up.
    self.dealers_hand[1].set_face_down(False)
    # ask for either hit, stand, or double down (if allowed)

    if not subsequent_round:
      print
      print 'Dealers turn'

    self.__print_dealer_info()

    soft_17 = False
    if len(self.dealer_values) > 1:
      # This is to avoid the extreme case of where the
      # Aces are being considered 1
      # eg A 6 10
      # values = [17, 27]
      for i in range(1, len(self.dealer_values)):
        if self.dealer_values[i] == 17:
          soft_17 = True

    if self.dealer_busted:
      return self.end_game_state()
    elif self.dealer_best_val < 17 or soft_17:
      # dealer hits
      self.dealers_hand.append(self.deck.pop())
      self.__update_hand(False)
      return self.dealers_turn_state()
    else:
      # dealer stands
      return self.end_game_state()


  def end_game_state(self):
    PW = 0
    PL = 1
    PU = 2
    result = -1
    if self.player_busted:
      print 'YOU BUSTED'
      result = PL
    elif self.dealer_busted:
      print 'DEALER BUSTED'
      result = PW
    else:
      # see who won
      player_vals = self.__get_hand_value(self.players_hand)
      player_vals = player_vals[::-1]
      best_player_val = -1
      for val in player_vals:
        if val <= 21:
          best_player_val = val
          break
      dealer_vals = self.__get_hand_value(self.dealers_hand)
      dealer_vals = dealer_vals[::-1]
      best_dealer_val = -1
      for val in dealer_vals:
        if val <= 21:
          best_dealer_val = val
          break
      if best_dealer_val > best_player_val:
        result = PL
      elif best_player_val > best_dealer_val:
        result = PW
      else:
        # push
        # we'll just say player wins
        # TODO what should we do?
        result = PW

    if result == PW:
      self.player_wins += 1
      self.player_bal += 2 * self.player_bet
      print 'You win!'
    elif result == PL:
      self.player_losses += 1
      print 'You lose!'
    elif result == PU:
      print 'Push'

    print ''
    # find out if they want to play again
    play_again = False
    while True:
      print 'Do you want to play again? (y/n)'
      inp = raw_input('--> ')
      inp = inp.lower()
      if len(inp) > 0:
        if inp[0] == 'y':
          play_again = True
          break
        elif inp[0] == 'n':
          play_again = False
          break
    if play_again:
      return self.new_round_state()
    else:
      print 'Goodbye!'
      return

  def new_round_state(self):
    self.round_num += 1
    print
    print '-----------------------------------------------------------------------'
    print 'Round ' + str(self.round_num)
    print 'Wins: ' + str(self.player_wins)
    print 'Losses: ' + str(self.player_losses)
    total_played = self.player_wins + self.player_losses
    if total_played > 0:
      print 'Win percentage: ' + str(100.0 * self.player_wins / total_played) + '%'
    # determine whether we need to shuffle the deck
    if self.round_num % 6 == 0:
      # shuffle
      print 'Shuffling deck...'
      self.__shuffle_deck()
    print 'Balance: $' + str(self.player_bal)
    # reset player / dealer hands
    # put used cards on the bottom
    self.deck = self.players_hand + self.dealers_hand + self.deck
    self.players_hand = []
    self.dealers_hand = []
    self.best_player_val = -1
    self.best_dealer_val = -1
    self.player_values = []
    self.dealer_values = []
    self.player_bet = 0

    # ask for player to bet
    while True:
      print 'How much would you like to bet? (integer value)'
      inp = raw_input('--> ')
      try:
        inp = int(float(inp))
        if inp < self.player_bal:
          self.player_bet = inp
          self.player_bal -= inp
          break
        else:
          print 'Invalid input. You must enter something you can afford'
      except:
        print 'Please enter an integer'

    # deal to player and dealer
    card = self.deck.pop()
    self.dealers_hand.append(card)

    card = self.deck.pop()
    self.players_hand.append(card)

    card = self.deck.pop()
    card.set_face_down(True)
    self.dealers_hand.append(card)

    card = self.deck.pop()
    self.players_hand.append(card)

    # update player / dealer values
    self.__update_hand(True)
    self.__update_hand(False)
    self.__print_game_state()

    # players turn
    self.players_turn_state(False)


  def __shuffle_deck(self):
    shuffle(self.deck)

  def __get_hand_value(self, hand):
    values = [0]
    for card in hand:
      values_length = len(values)
      if card.is_ace():
        # adding two versions, where ace is 1 or 11
        ace_values = card.int_value()
        for i in range(values_length):
          values.append(values[i] + ace_values[1])
          values[i] += card.int_value()[0]
      else:
        for i in range(values_length):
          values[i] += card.int_value()
    values.sort()
    return values

  def __print_game_state(self):
    print 'Balance: $' + str(self.player_bal)
    self.__print_dealer_info()
    self.__print_player_info()
    print ''

  def __print_dealer_info(self):
    print 'Dealers hand:'
    print self.__hand_str(self.dealers_hand)

  def __print_player_info(self):
    print 'Players hand:'
    print self.__hand_str(self.players_hand)

  def __hand_str(self, hand):
    s = ''
    for card in hand:
      s += str(card) + '  '
    return s


if __name__ == '__main__':
  print "Playing blackjack"
  blackjack = Blackjack()
  blackjack.new_game_state()
