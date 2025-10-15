# py_casino_blackjack.py
# A small arcade-y casino: character enters, lobby music (optional), then blackjack.
# Run: python py_casino_blackjack.py
import sys
import random
import pygame

# ------------- Config -------------
WIDTH, HEIGHT = 900, 600
FPS = 60
TABLE_COLOR = (7, 105, 57)
BG_COLOR = (18, 18, 22)
GOLD = (240, 200, 60)
WHITE = (245, 245, 245)
RED = (220, 60, 60)
GRAY = (120, 120, 130)
BLACK = (0, 0, 0)
ACCENT = (160, 90, 255)

STARTING_BANKROLL = 200
MIN_BET = 10
MAX_BET = 500
NUM_DECKS = 6

MUSIC_FILE = "lobby_music.mp3"  # optional; put any mp3 with this name near the script

# --- RIGGING ---
DEALER_LOSS_RATE = 0.95  # dealer will lose this fraction of rounds where they'd otherwise win

# ------------- Pygame init -------------
pygame.init()
pygame.display.set_caption("PY Casino — Blackjack")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

try:
    pygame.mixer.init()
    MUSIC_ENABLED = True
except pygame.error:
    MUSIC_ENABLED = False

# Fonts
FONT_BIG = pygame.font.SysFont("arialblack", 48)
FONT_MED = pygame.font.SysFont("arial", 28, bold=True)
FONT = pygame.font.SysFont("arial", 22)
FONT_SMALL = pygame.font.SysFont("arial", 18)

# ------------- Cards / Blackjack Logic -------------
SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
VALUES = {**{str(i): i for i in range(2, 11)}, "J": 10, "Q": 10, "K": 10, "A": 11}

def build_shoe(num_decks=6):
    shoe = []
    for _ in range(num_decks):
        for s in SUITS:
            for r in RANKS:
                shoe.append((r, s))
    random.shuffle(shoe)
    return shoe

def hand_total(cards):
    # cards: list of (rank, suit)
    total = 0
    aces = 0
    for r, _ in cards:
        total += VALUES[r]
        if r == "A":
            aces += 1
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total

def is_blackjack(cards):
    return len(cards) == 2 and hand_total(cards) == 21

def is_bust(cards):
    return hand_total(cards) > 21

# ------------- UI Helpers -------------
def draw_text(text, font, color, x, y, center=False, shadow=False):
    if shadow:
        sh = font.render(text, True, BLACK)
        rect = sh.get_rect()
        rect.topleft = (x + 2, y + 2)
        if center:
            rect.center = (x + 2, y + 2)
        screen.blit(sh, rect)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)
    return rect

def button(rect, label, enabled=True):
    x, y, w, h = rect
    color = ACCENT if enabled else (80, 80, 90)
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, (255, 255, 255, 40), (x, y, w, h), width=2, border_radius=12)
    draw_text(label, FONT_MED, WHITE if enabled else GRAY, x + w//2, y + h//2, center=True)
    return rect if enabled else None

def point_in_rect(pos, rect):
    if rect is None:
        return False
    x, y = pos
    rx, ry, rw, rh = rect
    return (rx <= x <= rx+rw) and (ry <= y <= ry+rh)

def draw_card(x, y, rank, suit, face_up=True):
    w, h = 80, 112
    r = pygame.Rect(x, y, w, h)
    if face_up:
        pygame.draw.rect(screen, WHITE, r, border_radius=10)
        pygame.draw.rect(screen, BLACK, r, width=2, border_radius=10)
        col = RED if suit in ("♥", "♦") else BLACK
        draw_text(rank, FONT_SMALL, col, x + 8, y + 6)
        draw_text(suit, FONT_MED, col, x + w//2, y + h//2, center=True)
        draw_text(rank, FONT_SMALL, col, x + w - 8, y + h - 20)
    else:
        pygame.draw.rect(screen, (30, 60, 130), r, border_radius=10)
        pygame.draw.rect(screen, WHITE, r, width=3, border_radius=10)
        pygame.draw.circle(screen, (200, 220, 255), (x + w//2, y + h//2), 18)
    return r

# ------------- Game States -------------
STATE_INTRO = "intro"
STATE_LOBBY = "lobby"
STATE_TABLE = "table"
STATE_GAMEOVER = "gameover"

class Game:
    def __init__(self):
        self.state = STATE_INTRO
        self.bankroll = STARTING_BANKROLL
        self.bet = MIN_BET
        self.message = ""
        self.shoe = build_shoe(NUM_DECKS)
        self.player = []
        self.dealer = []
        self.revealed = False
        self.hand_phase = "betting"  # betting -> dealing -> player -> dealer -> settle
        self.anim_cards = []  # list of dicts with animation info
        self.character_x = -60
        self.character_y = HEIGHT - 140
        self.music_loaded = False
        if MUSIC_ENABLED:
            try:
                pygame.mixer.music.load(MUSIC_FILE)
                pygame.mixer.music.set_volume(0.5)
                self.music_loaded = True
                pygame.mixer.music.play(-1)
            except Exception:
                self.music_loaded = False

    def reshoe_if_needed(self):
        if len(self.shoe) < 20:
            self.shoe = build_shoe(NUM_DECKS)

    def draw_intro(self):
        screen.fill(BG_COLOR)
        # Casino facade
        pygame.draw.rect(screen, (26, 26, 32), (0, 0, WIDTH, HEIGHT))
        # Neon sign
        pygame.draw.rect(screen, (40, 40, 46), (120, 60, WIDTH-240, 120), border_radius=16)
        draw_text("PY CASINO", FONT_BIG, GOLD, WIDTH//2, 115, center=True, shadow=True)
        draw_text("Press SPACE to enter", FONT, WHITE, WIDTH//2, 165, center=True)

        # Doors
        door_w, door_h = 180, 260
        door_x = WIDTH//2 - door_w//2
        door_y = HEIGHT//2 - 40
        pygame.draw.rect(screen, (60, 40, 30), (door_x, door_y, door_w, door_h))
        pygame.draw.rect(screen, GOLD, (door_x, door_y, door_w, door_h), 4)

        # Character (little adventurer)
        self.character_x = min(self.character_x + 2.5, door_x + door_w//2 - 15)
        pygame.draw.rect(screen, (60, 140, 255), (self.character_x, self.character_y, 30, 40), border_radius=6)  # body
        pygame.draw.circle(screen, (255, 224, 189), (int(self.character_x + 15), self.character_y - 10), 12)  # head
        # feet
        pygame.draw.rect(screen, BLACK, (self.character_x + 2, self.character_y + 38, 10, 6), border_radius=3)
        pygame.draw.rect(screen, BLACK, (self.character_x + 18, self.character_y + 38, 10, 6), border_radius=3)

        draw_text("You approach the casino entrance...", FONT, WHITE, WIDTH//2, HEIGHT - 40, center=True)

    def draw_lobby(self):
        screen.fill((25, 18, 30))
        # Simple lobby floor gradient stripes
        for i in range(10):
            col = (30 + i*4, 20 + i*4, 45 + i*8)
            pygame.draw.rect(screen, col, (0, HEIGHT - (i+1)*40, WIDTH, 40))

        draw_text("Lobby", FONT_BIG, GOLD, 30, 20)
        draw_text(f"Bankroll: ${self.bankroll}", FONT_MED, WHITE, 30, 80)
        draw_text("Click the table to play Blackjack", FONT_MED, WHITE, 30, 120)

        # A glowing blackjack table “portal”
        table_rect = pygame.Rect(WIDTH//2 - 180, HEIGHT//2 - 120, 360, 240)
        pygame.draw.ellipse(screen, (30, 120, 70), table_rect)
        pygame.draw.ellipse(screen, WHITE, table_rect, width=4)
        draw_text("Blackjack", FONT_MED, WHITE, table_rect.centerx, table_rect.centery, center=True)

        return table_rect

    def start_hand(self):
        self.message = ""
        self.player = []
        self.dealer = []
        self.revealed = False
        self.reshoe_if_needed()
        # dealing animation
        self.hand_phase = "dealing"
        self.anim_cards = []
        deal_order = [
            ("player", 0), ("dealer", 0),
            ("player", 1), ("dealer", 1)
        ]
        # animation spawn times
        t = 0
        for who, idx in deal_order:
            self.anim_cards.append({
                "who": who,
                "idx": idx,
                "t_start": pygame.time.get_ticks() + t,
                "from": (WIDTH//2, -140),
                "to": self.card_target_pos(who, idx),
                "arrived": False,
                "card": self.shoe.pop()
            })
            t += 220

    def card_target_pos(self, who, idx):
        # determine where nth card should land
        if who == "player":
            base_x = 160
            base_y = HEIGHT - 240
        else:  # dealer
            base_x = 160
            base_y = 140
        return (base_x + idx * 90, base_y)

    def update_deal_anim(self):
        now = pygame.time.get_ticks()
        still_animating = False
        for c in self.anim_cards:
            if c["arrived"] or now < c["t_start"]:
                continue
            # lerp
            fx, fy = c["from"]
            tx, ty = c["to"]
            dt = (now - c["t_start"]) / 220.0
            if dt >= 1.0:
                c["arrived"] = True
                # actually add the card
                if c["who"] == "player":
                    self.player.append(c["card"])
                else:
                    self.dealer.append(c["card"])
            else:
                still_animating = True
        # remove fully arrived ones from animation list to draw them as real cards
        self.anim_cards = [a for a in self.anim_cards if not a["arrived"] or now < a["t_start"]]

        if not still_animating and all(a["arrived"] or now >= a["t_start"] for a in self.anim_cards):
            # done
            self.anim_cards.clear()
            # next phase
            if is_blackjack(self.player) or is_blackjack(self.dealer):
                self.hand_phase = "settle"
                self.revealed = True
            else:
                self.hand_phase = "player"

    def settle_hand(self):
        p = hand_total(self.player)
        d = hand_total(self.dealer)

        # Natural blackjack first
        if is_blackjack(self.player) and is_blackjack(self.dealer):
            self.message = "Both blackjack — Push."
            delta = 0
        elif is_blackjack(self.player):
            win = int(self.bet * 1.5)
            self.message = f"Blackjack! You win ${win}."
            delta = win
        elif is_blackjack(self.dealer):
            self.message = "Dealer blackjack. You lose."
            delta = -self.bet
        else:
            if is_bust(self.player):
                self.message = "You bust."
                delta = -self.bet
            elif is_bust(self.dealer):
                self.message = "Dealer busts. You win!"
                delta = self.bet
            else:
                if p > d:
                    self.message = "You win!"
                    delta = self.bet
                elif p < d:
                    self.message = "Dealer wins."
                    delta = -self.bet
                else:
                    self.message = "Push."
                    delta = 0

        # --- RIGGING: if player would lose, flip to player win with high probability ---
        if delta < 0:
            if random.random() < DEALER_LOSS_RATE:
                # flip result: player wins instead
                self.message = "Lucky streak! Dealer loses."
                delta = self.bet
        # --- end rigging ---

        self.bankroll += delta
        self.hand_phase = "done"

    def handle_events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            if ev.type == pygame.KEYDOWN:
                if self.state == STATE_INTRO and ev.key == pygame.K_SPACE:
                    self.state = STATE_LOBBY
                elif self.state == STATE_GAMEOVER and ev.key == pygame.K_r:
                    # restart
                    self.__init__()
                    self.state = STATE_INTRO
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = pygame.mouse.get_pos()
                if self.state == STATE_LOBBY:
                    table_rect = self.draw_lobby()  # to get same rect
                    if table_rect.collidepoint((mx, my)):
                        self.state = STATE_TABLE
                        self.hand_phase = "betting"
                elif self.state == STATE_TABLE:
                    self.handle_table_click(mx, my)

    def handle_table_click(self, mx, my):
        # draw once to get button rects consistently
        rects = self.draw_table(get_rects_only=True)
        # Betting controls only during "betting"
        if self.hand_phase == "betting":
            if point_in_rect((mx, my), rects["minus"]):
                self.bet = max(MIN_BET, self.bet - MIN_BET)
            elif point_in_rect((mx, my), rects["plus"]):
                self.bet = min(MAX_BET, min(self.bankroll, self.bet + MIN_BET))
            elif point_in_rect((mx, my), rects["deal"]):
                if self.bet > 0 and self.bet <= self.bankroll:
                    self.start_hand()
                else:
                    self.message = "Adjust your bet."
        elif self.hand_phase == "player":
            if point_in_rect((mx, my), rects["hit"]):
                self.player.append(self.shoe.pop()); self.reshoe_if_needed()
                if is_bust(self.player):
                    self.revealed = True
                    self.hand_phase = "settle"
            elif point_in_rect((mx, my), rects["stand"]):
                self.hand_phase = "dealer"
        elif self.hand_phase == "done":
            # next hand or end
            if self.bankroll <= 0:
                self.state = STATE_GAMEOVER
            else:
                if point_in_rect((mx, my), rects["next"]):
                    self.message = ""
                    self.player, self.dealer = [], []
                    self.revealed = False
                    self.hand_phase = "betting"

    def draw_table(self, get_rects_only=False):
        # Background
        screen.fill((14, 70, 50))
        pygame.draw.rect(screen, TABLE_COLOR, (60, 80, WIDTH-120, HEIGHT-160), border_radius=30)
        pygame.draw.rect(screen, GOLD, (60, 80, WIDTH-120, HEIGHT-160), width=4, border_radius=30)
        draw_text("Blackjack Table", FONT_BIG, WHITE, WIDTH//2, 110, center=True)

        # Bankroll and bet
        draw_text(f"Bankroll: ${self.bankroll}", FONT_MED, WHITE, 80, 160)
        draw_text(f"Bet: ${self.bet}", FONT_MED, WHITE, 80, 200)

        rects = {"minus": None, "plus": None, "deal": None, "hit": None, "stand": None, "next": None}

        # Betting controls
        if self.hand_phase == "betting":
            rects["minus"] = button((300, 190, 60, 36), "-")
            rects["plus"]  = button((370, 190, 60, 36), "+")
            rects["deal"]  = button((450, 186, 140, 44), "Deal", enabled=(self.bet>0 and self.bet<=self.bankroll))
            draw_text("Adjust your bet, then Deal.", FONT, WHITE, 80, 240)

        # Dealer area
        draw_text("Dealer", FONT_MED, WHITE, 80, 270)
        self.draw_hand(self.dealer, x0=160, y0=300, hide_first=(not self.revealed and self.hand_phase in ("player","dealing")))

        # Player area
        draw_text("You", FONT_MED, WHITE, 80, HEIGHT-230)
        self.draw_hand(self.player, x0=160, y0=HEIGHT-200, hide_first=False)

        # Buttons for actions
        if self.hand_phase == "player":
            rects["hit"] = button((WIDTH-260, HEIGHT-180, 90, 48), "Hit", enabled=True)
            rects["stand"] = button((WIDTH-160, HEIGHT-180, 90, 48), "Stand", enabled=True)
        elif self.hand_phase == "done":
            rects["next"] = button((WIDTH-200, HEIGHT-180, 140, 48), "Next Hand", enabled=(self.bankroll>0))

        # Message/status
        if self.message:
            draw_text(self.message, FONT_MED, GOLD if "win" in self.message.lower() else WHITE, WIDTH//2, 170, center=True)

        if get_rects_only:
            return rects

        return rects

    def draw_hand(self, cards, x0, y0, hide_first=False):
        # live cards
        for i, (r, s) in enumerate(cards):
            face_up = not (hide_first and i == 0)
            draw_card(x0 + i*90, y0, r, s, face_up=face_up)
        # animating “in-flight” cards preview
        now = pygame.time.get_ticks()
        for a in self.anim_cards:
            if now < a["t_start"]:
                continue
            # interpolate
            fx, fy = a["from"]
            tx, ty = a["to"]
            dt = (now - a["t_start"]) / 220.0
            if dt < 1.0:
                x = fx + (tx - fx) * dt
                y = fy + (ty - fy) * dt
                # Face down while flying; final orientation when lands handled elsewhere
                draw_card(int(x), int(y), a["card"][0], a["card"][1], face_up=False)

    def update(self):
        # advance animations / phases
        if self.state == STATE_TABLE:
            if self.hand_phase == "dealing":
                self.update_deal_anim()
            elif self.hand_phase == "dealer":
                # Dealer auto-plays, simple pacing
                pygame.time.delay(350)
                if hand_total(self.dealer) < 17:
                    self.dealer.append(self.shoe.pop()); self.reshoe_if_needed()
                else:
                    self.revealed = True
                    self.hand_phase = "settle"
            elif self.hand_phase == "settle":
                self.settle_hand()

    def draw(self):
        if self.state == STATE_INTRO:
            self.draw_intro()
        elif self.state == STATE_LOBBY:
            self.draw_lobby()
        elif self.state == STATE_TABLE:
            self.draw_table()
        elif self.state == STATE_GAMEOVER:
            screen.fill(BG_COLOR)
            draw_text("You’re out of money.", FONT_BIG, RED, WIDTH//2, HEIGHT//2 - 30, center=True, shadow=True)
            draw_text("Press R to restart", FONT_MED, WHITE, WIDTH//2, HEIGHT//2 + 30, center=True)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)

# ------------- Main -------------
if __name__ == "__main__":
    Game().run()
