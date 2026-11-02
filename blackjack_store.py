"""Transactional bridge between the unchanged rule engine and the account wallet."""
import json
from uuid import uuid4
from flask import current_app
import account_wallet
import blackjack_game as game

ACCOUNT_CURRENCY = 'account-ikuehe'

def account_mode(state):
    return game.table_rules(state).get('currency') == ACCOUNT_CURRENCY

def wants_accounts():
    return current_app.config.get('BLACKJACK_CURRENCY') == ACCOUNT_CURRENCY

def joining_blocked(state):
    return wants_accounts() and not account_mode(state)

class AccountBalances(dict):
    def __init__(self, values, revision, session):
        super().__init__(values)
        self.original = dict(values)
        self.revision = revision
        self.session = session
        self.entries = []

    def __setitem__(self, uid, amount):
        before = self[uid]
        super().__setitem__(uid,amount)
        if amount != before:
            self.entries.append((uid,amount-before))

def balances_for(db,state,revision):
    if not account_mode(state):
        return {str(row['user_id']):row['balance'] for row in db.execute('SELECT * FROM blackjack_balances')}
    amounts = account_wallet.balances(db,current_app.config.get('PREVIEW_CURRENCY_BONUS',0))
    return AccountBalances({str(uid):value for uid,value in amounts.items()},revision,state['account_session'])

def load(db):
    state,legacy,revision = game.load(db)
    return state,balances_for(db,state,revision) if account_mode(state) else legacy,revision

def configure_rules(db,state):
    stake = current_app.config.get('BLACKJACK_FIXED_STAKE')
    if not stake:
        return
    account = account_mode(state)
    if wants_accounts() and not account:
        occupied = db.execute('SELECT COUNT(*) FROM blackjack_seats').fetchone()[0]
        if occupied or state['bets'] or state['phase'] not in ('betting','result'):
            state['currency_change_pending'] = True
            return
        # An old test hand/bet is never converted into an account wager.
        game.begin_betting(state)
        state['account_session'] = uuid4().hex
        account = True
    state.pop('currency_change_pending',None)
    state['table_rules'] = dict(fixed_bet=stake,
        currency=ACCOUNT_CURRENCY if account else 'test-ikuehe',
        test_refill=0 if account else current_app.config.get('BLACKJACK_TEST_START_BALANCE',10000),
        dealer_peek=current_app.config.get('BLACKJACK_DEALER_PEEK',True))

def save(db,state,amounts,*,command='clock'):
    if not isinstance(amounts,AccountBalances):
        return game.save(db,state,amounts)
    if not db.in_transaction:
        raise game.GameError('Die Kontobuchung benötigt eine gesperrte Tischtransaktion.')
    revision = db.execute('SELECT revision FROM blackjack_game WHERE id=1').fetchone()[0]
    if revision != amounts.revision:
        raise game.GameError('Der Tisch hat sich geändert. Bitte aktualisiere die Ansicht.')
    try:
        for index,(uid,delta) in enumerate(amounts.entries):
            reference = f'blackjack:{amounts.session}:{revision+1}:{index}'
            detail = json.dumps(dict(round=state['round'],phase=state['phase'],action=command),sort_keys=True)
            account_wallet.post_entry(db,int(uid),delta,reference,detail,
                bonus=current_app.config.get('PREVIEW_CURRENCY_BONUS',0))
        for uid in {uid for uid,_ in amounts.entries}:
            if account_wallet.balance(db,int(uid),current_app.config.get('PREVIEW_CURRENCY_BONUS',0)) != amounts[uid]:
                raise account_wallet.WalletError('Der Kontostand stimmt nicht mit der Tischbuchung überein.')
        game.save(db,state,amounts,persist_balances=False)
    except account_wallet.WalletError as error:
        raise game.GameError(str(error)) from error
