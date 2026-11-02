"""Persistent Blackjack rules. Table points are separate from account currency."""
import json
import time
from random import SystemRandom

RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K')
SUITS = ('S', 'H', 'D', 'C')


class GameError(ValueError):
    pass


def clock_now():
    return time.time()


def initial_state():
    return dict(phase='betting', round=0, shoe=[], dealer=[], players=[], bets={}, pending_leaves=[])


def table_rules(state):
    return state.get('table_rules', {})


def dealer_peeks(state):
    # Preserve the rule of an already dealt round while table settings change.
    return state.get('round_rules', {}).get('dealer_peek', True)


def minimum_bet(state):
    return table_rules(state).get('fixed_bet', 10)


def init_game_db(db):
    db.executescript('''
        CREATE TABLE IF NOT EXISTS blackjack_balances (
            user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
            balance INTEGER NOT NULL CHECK(balance >= 0)
        );
        CREATE TABLE IF NOT EXISTS blackjack_game (
            id INTEGER PRIMARY KEY CHECK(id = 1), revision INTEGER NOT NULL,
            state_json TEXT NOT NULL
        );
        INSERT OR IGNORE INTO blackjack_balances SELECT user_id, 1000 FROM blackjack_seats;
    ''')
    db.execute('INSERT OR IGNORE INTO blackjack_game VALUES (1, 0, ?)', (json.dumps(initial_state()),))
    db.commit()


def load(db):
    row = db.execute('SELECT revision, state_json FROM blackjack_game WHERE id=1').fetchone()
    balances = {str(r['user_id']): r['balance'] for r in db.execute('SELECT * FROM blackjack_balances')}
    return json.loads(row['state_json']), balances, row['revision']


def save(db, state, balances):
    if state['phase'] == 'result':
        for uid in state['pending_leaves']:
            state['bets'].pop(uid, 0)
            db.execute('DELETE FROM blackjack_seats WHERE user_id=?', (int(uid),))
        state['pending_leaves'] = []
    seats = {str(row['user_id']): row['seat'] for row in db.execute('SELECT * FROM blackjack_seats')}
    sync_clock(state, seats)
    for uid, amount in balances.items():
        db.execute('UPDATE blackjack_balances SET balance=? WHERE user_id=? AND balance<>?', (amount, int(uid), amount))
    db.execute('UPDATE blackjack_game SET revision=revision+1,state_json=? WHERE id=1', (json.dumps(state),))


def sync_clock(state, seats, now=None):
    clock = state.get('clock')
    if not clock or not clock['automatic']:
        return
    now = clock_now() if now is None else now
    phase = state['phase']
    key = f"{phase}:{state['round']}"
    kind = phase if seats and phase in ('betting', 'result') else None
    if kind is None or (kind == 'betting' and len(seats) == 1):
        deadline = None
    elif clock.get('phase_key') != key:
        deadline = now + clock[kind+'_seconds']
    else:
        deadline = clock.get('deadline')
        # After an empty window, only an explicit bet or a new participant
        # opens another window. There is never an automatic repeat wager.
        if deadline is None and (state['bets'] or len(seats) > clock.get('seat_count', 0)):
            deadline = now + clock[kind+'_seconds']
    clock.update(kind=kind, deadline=deadline, phase_key=key, seat_count=len(seats))


def begin_betting(state):
    # Bets entered while another hand was running already belong here.
    state.update(phase='betting', players=[], dealer=[])


def start_if_ready(state, balances, seats):
    if (state.get('clock', {}).get('automatic') and state['phase'] == 'betting'
            and seats and all(uid in state['bets'] for uid in seats)):
        start(state, balances, seats)
        return True
    return False


def value(cards):
    total = sum(11 if c[:-1] == 'A' else min(10, RANKS.index(c[:-1])+1) for c in cards)
    aces = sum(c[:-1] == 'A' for c in cards)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total, bool(aces)


def rank_value(card):
    return 11 if card[:-1] == 'A' else min(10, RANKS.index(card[:-1])+1)


def draw(state):
    if not state['shoe']:
        raise GameError('Der Kartenstapel ist leer. Die Aktion wurde nicht ausgeführt.')
    return state['shoe'].pop()


def participant(state, uid):
    return next((p for p in state['players'] if p['uid'] == str(uid)), None)


def can_place_bet(state, uid):
    uid = str(uid)
    return (uid not in state['bets'] and uid not in state['pending_leaves']
            and not (state['phase'] in ('turn', 'insurance') and participant(state, uid)))


def current(state):
    if state['phase'] != 'turn':
        return None
    return next(((p, i, h) for p in state['players'] for i, h in enumerate(p['hands']) if h['status'] == 'playing'), None)


def settle(state, balances):
    if state['phase'] == 'result':
        return
    dealer = value(state['dealer'])[0]
    dealer_blackjack = dealer == 21 and len(state['dealer']) == 2
    for player in state['players']:
        insurance = player['insurance'] or 0
        insurance_payout = insurance * 3 if dealer_blackjack and not player.get('forfeited') else 0
        balances[player['uid']] += insurance_payout
        player['insurance_net'] = insurance_payout - insurance
        original_left = player.get('original_bet', player['hands'][0]['bet'])
        for hand in player['hands']:
            total = value(hand['cards'])[0]
            natural = not hand['split'] and len(hand['cards']) == 2 and total == 21
            if hand['status'] == 'forfeit':
                payout, result = 0, 'Tisch verlassen'
            elif dealer_blackjack:
                if natural:
                    payout, result = hand['bet'], 'Gleichstand'
                elif not dealer_peeks(state):
                    # No early check: collect the original wager once, return
                    # all additions for splitting/doubling (MGC 10(b), 11(d)).
                    lost = min(original_left, hand['bet'])
                    original_left -= lost
                    payout = hand['bet'] - lost
                    result = 'Verloren' if lost else 'Zusatzeinsatz zurück'
                else:
                    payout, result = 0, 'Verloren'
            elif hand['status'] == 'surrender':
                payout, result = hand['bet']//2, 'Aufgegeben'
            elif total > 21:
                payout, result = 0, 'Überkauft'
            elif natural:
                payout, result = hand['bet']*5//2, 'Blackjack'
            elif dealer > 21 or total > dealer:
                payout, result = hand['bet']*2, 'Gewonnen'
            elif total == dealer:
                payout, result = hand['bet'], 'Gleichstand'
            else:
                payout, result = 0, 'Verloren'
            hand.update(payout=payout, net=payout-hand['bet'], result=result)
            balances[player['uid']] += payout
    state['phase'] = 'result'


def advance(state, balances):
    if current(state):
        return
    # When every remaining hand is already lost/surrendered/a natural, reveal
    # the bank without drawing irrelevant extra cards.
    if any(h['status'] == 'stood' for p in state['players'] for h in p['hands']):
        while value(state['dealer'])[0] < 17:
            state['dealer'].append(draw(state))
    settle(state, balances)


def peek(state, balances):
    if dealer_peeks(state) and value(state['dealer'])[0] == 21:
        settle(state, balances)
    else:
        state['phase'] = 'turn'
        advance(state, balances)


def start(state, balances, seats):
    if state['phase'] != 'betting' or not state['bets']:
        raise GameError('Für das Austeilen fehlt noch ein Einsatz.')
    if len(state['shoe']) < 156:
        state['shoe'] = [r+s for _ in range(6) for s in SUITS for r in RANKS]
        SystemRandom().shuffle(state['shoe'])
    state['players'] = [dict(uid=uid, seat=seat, original_bet=state['bets'][uid], hands=[dict(cards=[], bet=state['bets'][uid], status='playing', split=False)], insurance=None)
                        for uid, seat in sorted(seats.items(), key=lambda item:item[1]) if uid in state['bets']]
    if not state['players']:
        raise GameError('Es sitzt niemand mit einem Einsatz am Tisch.')
    state['round_rules'] = dict(dealer_peek=table_rules(state).get('dealer_peek', True))
    state['dealer'] = []
    for _ in range(2):
        for player in state['players']:
            player['hands'][0]['cards'].append(draw(state))
        state['dealer'].append(draw(state))
    state['bets'] = {}
    state['round'] += 1
    for player in state['players']:
        if value(player['hands'][0]['cards'])[0] == 21:
            player['hands'][0]['status'] = 'blackjack'
    if state['dealer'][0][:-1] == 'A':
        state['phase'] = 'insurance'
    else:
        peek(state, balances)


def legal_actions(state, balances, uid):
    uid = str(uid)
    if uid in state['pending_leaves']:
        return []
    player = participant(state, uid)
    if state['phase'] == 'insurance':
        if not player or player['insurance'] is not None:
            return []
        return (['insurance'] if balances[uid] >= player['hands'][0]['bet']//2 else []) + ['no-insurance']
    turn = current(state)
    if not turn or turn[0]['uid'] != uid:
        return []
    _, _, hand = turn
    options = ['hit', 'stand']
    if len(hand['cards']) == 2:
        if balances[uid] >= hand['bet']:
            options.append('double')
            if splittable(player, hand):
                options.append('split')
        if not hand['split']:
            options.append('surrender')
    return options


def splittable(player, hand):
    return (len(player['hands']) == 1 and len(hand['cards']) == 2
            and rank_value(hand['cards'][0]) == rank_value(hand['cards'][1]))


def blocked_actions(state, balances, uid):
    uid = str(uid)
    turn = current(state)
    if turn and turn[0]['uid'] == uid and splittable(turn[0], turn[2]) and balances[uid] < turn[2]['bet']:
        return dict(split=dict(required=turn[2]['bet'], available=balances[uid]))
    return {}


def action(state, balances, seats, uid, command, amount=None):
    uid = str(uid)
    if uid not in seats:
        raise GameError('Nimm zuerst einen Platz am Tisch ein.')
    clock = state.get('clock', {})
    if clock.get('automatic'):
        if command in ('deal', 'next'):
            raise GameError('Der Geber führt den Rundenwechsel automatisch aus.')
        if command not in ('bet','cancel-bet') and clock.get('deadline') is not None and clock_now() >= clock['deadline']:
            raise GameError('Diese Zeit ist abgelaufen. Der Geber wechselt gerade die Phase.')
    if command == 'bet':
        if uid in state['pending_leaves']:
            raise GameError('Du stehst nach dieser Runde auf. Dein Platz erhält keinen neuen Einsatz.')
        if uid in state['bets']:
            raise GameError('Dein Einsatz liegt bereits. Er bleibt für diese Runde fest auf dem Tisch.')
        if not can_place_bet(state, uid):
            raise GameError('Dein Einsatz spielt bereits in der laufenden Hand. Setze erst nach Rundenende neu.')
        fixed = table_rules(state).get('fixed_bet')
        if fixed and (type(amount) is not int or amount != fixed):
            raise GameError(f'Der Einsatz an diesem Tisch beträgt fest {fixed} Test-iKühe.')
        if type(amount) is not int or not 10 <= amount <= 500 or amount % 10:
            raise GameError('Der Einsatz muss zwischen 10 und 500 liegen, in Zehnerschritten.')
        available = balances[uid] + state['bets'].get(uid, 0)
        if amount > available:
            raise GameError('Dafür reicht dein Testguthaben nicht.')
        balances[uid] = available - amount
        state['bets'][uid] = amount
        if clock.get('automatic') and state['phase'] == 'result' and len(seats) == 1:
            begin_betting(state)
        start_if_ready(state, balances, seats)
        return
    if command == 'cancel-bet':
        raise GameError('Ein gelegter Einsatz kann nicht zurückgezogen werden.')
    if command == 'deal':
        if uid not in state['bets']:
            raise GameError('Setze zuerst deinen Einsatz.')
        start(state, balances, seats)
        return
    if command == 'next':
        if state['phase'] != 'result':
            raise GameError('Die laufende Runde ist noch nicht beendet.')
        begin_betting(state)
        return
    if command == 'refill':
        if state['phase'] not in ('betting', 'result') or state['bets'].get(uid) or balances[uid] >= minimum_bet(state):
            raise GameError('Ein neuer Testvorrat ist erst möglich, wenn dein Guthaben für keinen Einsatz mehr reicht.')
        balances[uid] = table_rules(state).get('test_refill', 1000)
        return
    if command not in legal_actions(state, balances, uid):
        raise GameError('Diese Spielaktion ist jetzt nicht möglich.')
    player = participant(state, uid)
    if command in ('insurance', 'no-insurance'):
        wager = player['hands'][0]['bet']//2 if command == 'insurance' else 0
        balances[uid] -= wager
        player['insurance'] = wager
        if all(p['insurance'] is not None for p in state['players']):
            peek(state, balances)
        return
    _, index, hand = current(state)
    if command == 'hit':
        hand['cards'].append(draw(state))
        total = value(hand['cards'])[0]
        if total >= 21:
            hand['status'] = 'bust' if total > 21 else 'stood'
    elif command == 'stand':
        hand['status'] = 'stood'
    elif command == 'surrender':
        hand['status'] = 'surrender'
    elif command == 'double':
        balances[uid] -= hand['bet']
        hand['bet'] *= 2
        hand['cards'].append(draw(state))
        hand['status'] = 'bust' if value(hand['cards'])[0] > 21 else 'stood'
    elif command == 'split':
        balances[uid] -= hand['bet']
        aces = hand['cards'][0][:-1] == 'A'
        player['hands'] = [dict(cards=[card,draw(state)], bet=hand['bet'], split=True, status='playing') for card in hand['cards']]
        for split_hand in player['hands']:
            if aces or value(split_hand['cards'])[0] == 21:
                split_hand['status'] = 'stood'
    advance(state, balances)


def leave_round(state, balances, uid):
    uid = str(uid)
    # Already debited when placed: remove once, never debit or refund again.
    state['bets'].pop(uid, 0)
    if state['phase'] == 'betting':
        return False
    player = participant(state, uid)
    if not player or state['phase'] == 'result':
        return False
    if uid not in state['pending_leaves']:
        state['pending_leaves'].append(uid)
    player['forfeited'] = True
    for hand in player['hands']:
        hand['status'] = 'forfeit'
    if state['phase'] == 'insurance':
        if player['insurance'] is None:
            player['insurance'] = 0
        if all(p['insurance'] is not None for p in state['players']):
            peek(state, balances)
    else:
        advance(state, balances)
    return True


def public_game(state, balances, viewer_id, names, seats):
    uid = str(viewer_id)
    turn = current(state)
    result = state['phase'] == 'result'
    players = []
    for player in state['players']:
        hands = [dict(cards=h['cards'], bet=h['bet'], total=value(h['cards'])[0], soft=value(h['cards'])[1],
                      status=h['status'], result=h.get('result'), net=h.get('net'),
                      active=bool(turn and turn[0]['uid']==player['uid'] and turn[1]==i)) for i,h in enumerate(player['hands'])]
        players.append(dict(seat=player['seat'], name=names.get(player['uid'],'Spieler'), own=player['uid']==uid,
                            split_aces=bool(len(player['hands'])==2 and all(h['split'] and h['cards'][0][:-1]=='A' for h in player['hands'])),
                            hands=hands, insurance=player['insurance'], insurance_net=player.get('insurance_net')))
    dealer = state['dealer'] if result else ([state['dealer'][0], None] if state['dealer'] else [])
    own = participant(state, uid)
    clock = state.get('clock', {})
    peek_rule = table_rules(state).get('dealer_peek', True) if state['phase'] == 'betting' else dealer_peeks(state)
    return dict(phase=state['phase'], round=state['round'], dealer=dealer,
                dealer_peek=peek_rule,
                next_dealer_peek=table_rules(state).get('dealer_peek', True),
                dealer_total=value([c for c in dealer if c])[0] if dealer else None,
                players=players, bets=[dict(seat=seats[key], amount=amount) for key,amount in state['bets'].items() if key in seats],
                own_bet=state['bets'].get(uid,0), bankroll=balances.get(uid),
                own_wager=sum(h['bet'] for h in own['hands']) if own else state['bets'].get(uid,0) if state['phase']=='betting' else 0,
                next_bet=state['bets'].get(uid,0) if state['phase']!='betting' else 0,
                bet_round=state['round']+1, prebet_supported=True,
                can_bet=uid in seats and can_place_bet(state,uid) and balances.get(uid,0)>=minimum_bet(state),
                fixed_bet=table_rules(state).get('fixed_bet'), min_bet=minimum_bet(state),
                currency=table_rules(state).get('currency', 'points'),
                test_refill=table_rules(state).get('test_refill', 1000),
                active_seat=turn[0]['seat'] if turn else None,
                actions=legal_actions(state,balances,uid) if uid in balances else [],
                blocked_actions=blocked_actions(state,balances,uid) if uid in balances else {},
                waiting_next=bool(state['phase'] in ('turn','insurance') and not own),
                leaving=uid in state['pending_leaves'],
                clock={key:clock.get(key) for key in ('automatic','kind','deadline','betting_seconds','result_seconds')})
