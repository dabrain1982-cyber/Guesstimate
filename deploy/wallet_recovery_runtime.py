"""Wallet-compatible 1.1 recovery; keep the current database, pause Blackjack."""
if __name__ == '__main__':
    raise SystemExit(0)
import account_wallet
import app as application
from flask import current_app,request
from workshop_buttons import register_workshop_buttons

app=application.app
application.player_currency_balance=lambda uid:account_wallet.balance(
    application.get_db(),uid,current_app.config.get('PREVIEW_CURRENCY_BONUS',0))
app.config.update(DEBUG=False,TESTING=False,LOCAL_DEVELOPMENT=False,OFFLINE_VERSION='',
    PUBLIC_RELEASE='1.1',DEPLOYMENT_ID='1.1-wallet-recovery.1',BUTTON_RUNTIME_ENABLED=True)
register_workshop_buttons(app)

@app.before_request
def pause_blackjack():
    if request.path.startswith('/karten/blackjack'):
        return 'Black Jack ist voruebergehend pausiert. Deine iKuehe-Buchungen bleiben erhalten.',503

@app.after_request
def recovery_version(response):
    if response.mimetype=='text/html' and not response.direct_passthrough:
        response.set_data(response.get_data(as_text=True).replace('</title>',' · V 1.1 (Wiederherstellung)</title>',1))
    return response
