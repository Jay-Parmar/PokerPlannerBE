PLAYER = 0
SPECTATOR = 1

ROLE_CHOICES = (
    (PLAYER, 'PLAYER'),
    (SPECTATOR, 'SPECTATOR'),
)
PENDING = 0
ACCEPTED = 1
DECLINED = 2

MESSAGE_TYPES = ["estimate", "skip", "vote", "initialise_game", "start_timer"]
