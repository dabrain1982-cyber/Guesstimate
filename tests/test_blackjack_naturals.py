import unittest
import blackjack_game as game


class BlackjackNaturalTests(unittest.TestCase):
    def deal(self, cards, count=1):
        state=game.initial_state()
        balances={str(i):1000 for i in range(1,count+1)}
        seats={str(i):i for i in range(1,count+1)}
        for uid in seats:game.action(state,balances,seats,uid,'bet',50)
        state['shoe']=['2C']*156+list(reversed(cards))
        game.action(state,balances,seats,'1','deal')
        return state,balances,seats

    def test_natural_does_not_require_dealer_to_draw_from_sixteen(self):
        state,balances,_=self.deal(['AS','6H','KD','10C'])
        self.assertEqual(state['phase'],'result')
        self.assertEqual(state['dealer'],['6H','10C'])
        self.assertEqual(balances['1'],1075)

    def test_other_player_still_plays_and_dealer_three_card_twenty_one_loses_to_natural(self):
        state,balances,seats=self.deal(['AS','10S','6H','KD','8D','10C','5S'],2)
        self.assertEqual(game.current(state)[0]['uid'],'2')
        self.assertEqual(game.legal_actions(state,balances,'1'),[])
        game.action(state,balances,seats,'2','stand')
        self.assertEqual(state['dealer'],['6H','10C','5S'])
        self.assertEqual(balances,{'1':1075,'2':950})

    def test_both_naturals_push_after_insurance_decision(self):
        state,balances,seats=self.deal(['AS','AH','KD','10C'])
        self.assertEqual(state['phase'],'insurance')
        game.action(state,balances,seats,'1','no-insurance')
        self.assertEqual(state['phase'],'result')
        self.assertEqual(balances['1'],1000)
        self.assertEqual(state['players'][0]['hands'][0]['result'],'Gleichstand')

    def test_natural_against_dealer_ace_wins_after_negative_blackjack_check(self):
        state,balances,seats=self.deal(['AS','AH','KD','6C'])
        self.assertEqual(state['phase'],'insurance')
        game.action(state,balances,seats,'1','no-insurance')
        self.assertEqual(state['dealer'],['AH','6C'])
        self.assertEqual(balances['1'],1075)

    def split_aces(self, bank, extra=None):
        state,balances,seats=self.deal(['AH',bank[0],'AC',bank[1],'6H','JS']+(extra or []))
        if state['phase']=='insurance':game.action(state,balances,seats,'1','no-insurance')
        game.action(state,balances,seats,'1','split')
        return state,balances

    def test_user_image_split_aces_are_complete_and_both_win_against_bust(self):
        state,balances=self.split_aces(['7H','7C'],['8D'])
        self.assertEqual(state['phase'],'result')
        self.assertEqual(state['dealer'],['7H','7C','8D'])
        hands=state['players'][0]['hands']
        self.assertEqual([h['cards'] for h in hands],[['AH','6H'],['AC','JS']])
        self.assertEqual([h['status'] for h in hands],['stood','stood'])
        self.assertEqual([h['net'] for h in hands],[50,50])
        self.assertEqual(game.legal_actions(state,balances,'1'),[])
        self.assertEqual(balances['1'],1100)

    def test_split_ace_seventeen_loses_against_twenty_but_split_twenty_one_wins_one_to_one(self):
        state,balances=self.split_aces(['10H','QC'])
        hands=state['players'][0]['hands']
        self.assertEqual([h['result'] for h in hands],['Verloren','Gewonnen'])
        self.assertEqual([h['net'] for h in hands],[-50,50])
        self.assertEqual(balances['1'],1000)

    def test_dealer_blackjack_with_ten_up_ends_before_any_player_decision(self):
        state,balances,seats=self.deal(['9S','10H','7D','AC'])
        self.assertEqual(state['phase'],'result')
        self.assertEqual(game.legal_actions(state,balances,'1'),[])
        self.assertEqual(balances['1'],950)
        self.assertRaises(game.GameError,game.action,state,balances,seats,'1','hit')

    def test_dealer_ace_offers_insurance_before_blackjack_ends_round(self):
        state,balances,seats=self.deal(['9S','AH','7D','KC'])
        self.assertEqual(state['phase'],'insurance')
        self.assertEqual(game.legal_actions(state,balances,'1'),['insurance','no-insurance'])
        game.action(state,balances,seats,'1','no-insurance')
        self.assertEqual(state['phase'],'result')
        self.assertEqual(game.legal_actions(state,balances,'1'),[])
        self.assertEqual(balances['1'],950)

    def test_unsplit_player_soft_seventeen_still_has_a_choice(self):
        state,balances,_=self.deal(['AH','10H','6D','7C'])
        self.assertEqual(state['phase'],'turn')
        self.assertIn('hit',game.legal_actions(state,balances,'1'))
        self.assertIn('stand',game.legal_actions(state,balances,'1'))


if __name__=='__main__':unittest.main()
