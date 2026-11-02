"""Production entrypoint; HTTP workers never start the table clock."""
import os
from pathlib import Path
import time
from app import app
from release_info import PUBLIC_VERSION
from blackjack_store import ACCOUNT_CURRENCY
from workshop_buttons import register_workshop_buttons

app.config.update(
    DEBUG=False, TESTING=False, LOCAL_DEVELOPMENT=False, OFFLINE_VERSION='',
    PUBLIC_RELEASE=PUBLIC_VERSION, DEPLOYMENT_ID=f'{PUBLIC_VERSION}-server.1', BUTTON_RUNTIME_ENABLED=True,
    BLACKJACK_FIXED_STAKE=500, BLACKJACK_CURRENCY=ACCOUNT_CURRENCY,
    BLACKJACK_DEALER_PEEK=False,
)
register_workshop_buttons(app)

def clock():
    import fcntl
    from blackjack_clock import tick_clock
    lock = open(Path(app.config['DATABASE']).parent / 'blackjack-clock.lock', 'a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit('Another Blackjack clock already owns this database.')
    while True:
        try:
            tick_clock(app)
        except Exception:
            app.logger.exception('Blackjack clock tick failed')
            time.sleep(5)
        time.sleep(.5)

if __name__ == '__main__':
    clock()
