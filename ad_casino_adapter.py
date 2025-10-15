# ad_casino_adapter.py
# Adapter to integrate the advanced blackjack game from ad_casino.py into main.py
import pygame
import sys
import random

# Import all the game logic from ad_casino but adapt it for integration
# Copy over the essential constants and functions
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

# Fonts - will be initialized when pygame is ready
FONT_BIG = None
FONT_MED = None
FONT = None
FONT_SMALL = None

def init_fonts():
    """Initialize fonts after pygame is initialized"""
    global FONT_BIG, FONT_MED, FONT, FONT_SMALL
    if FONT_BIG is None:
        FONT_BIG = pygame.font.SysFont("arial", 48, bold=True)
        FONT_MED = pygame.font.SysFont("arial", 28, bold=True)
        FONT = pygame.font.SysFont("arial", 22)
        FONT_SMALL = pygame.font.SysFont("arial", 18)

# Cards / Blackjack Logic
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

# UI Helpers
def draw_text(surface, text, font, color, x, y, center=False, shadow=False):
    if shadow:
        sh = font.render(text, True, BLACK)
        rect = sh.get_rect()
        rect.topleft = (x + 2, y + 2)
        if center:
            rect.center = (x + 2, y + 2)
        surface.blit(sh, rect)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(surf, rect)
    return rect

def button(surface, rect, label, enabled=True):
    x, y, w, h = rect
    color = ACCENT if enabled else (80, 80, 90)
    pygame.draw.rect(surface, color, rect, border_radius=12)
    pygame.draw.rect(surface, (255, 255, 255, 40), (x, y, w, h), width=2, border_radius=12)
    draw_text(surface, label, FONT_MED, WHITE if enabled else GRAY, x + w//2, y + h//2, center=True)
    return rect if enabled else None

def point_in_rect(pos, rect):
    if rect is None:
        return False
    x, y = pos
    rx, ry, rw, rh = rect
    return (rx <= x <= rx+rw) and (ry <= y <= ry+rh)

def draw_card(surface, x, y, rank, suit, face_up=True):
    w, h = 80, 112
    r = pygame.Rect(x, y, w, h)
    if face_up:
        pygame.draw.rect(surface, WHITE, r, border_radius=10)
        pygame.draw.rect(surface, BLACK, r, width=2, border_radius=10)
        col = RED if suit in ("♥", "♦") else BLACK
        draw_text(surface, rank, FONT_SMALL, col, x + 8, y + 6)
        draw_text(surface, suit, FONT_MED, col, x + w//2, y + h//2, center=True)
        draw_text(surface, rank, FONT_SMALL, col, x + w - 8, y + h - 20)
    else:
        pygame.draw.rect(surface, (30, 60, 130), r, border_radius=10)
        pygame.draw.rect(surface, WHITE, r, width=3, border_radius=10)
        pygame.draw.circle(surface, (200, 220, 255), (x + w//2, y + h//2), 18)
    return r


class BlackjackTable:
    """Adapter class that wraps the ad_casino.py blackjack game for use in main.py"""
    
    def __init__(self, pos):
        # Initialize fonts if needed
        init_fonts()
        
        self.pos = pos
        self.bankroll = STARTING_BANKROLL
        self.bet = MIN_BET
        self.message = ""
        self.shoe = build_shoe(NUM_DECKS)
        self.player = []
        self.dealer = []
        self.revealed = False
        self.hand_phase = "betting"  # betting -> dealing -> player -> dealer -> settle -> done
        self.anim_cards = []  # list of dicts with animation info
        self.state = 'waiting'  # Interface compatibility with main.py
        
        # For compatibility with main.py interface
        self.player_money = self.bankroll
        
    def start_game(self):
        """Called when player interacts with the table"""
        self.state = 'betting'
        self.hand_phase = "betting"
        self.message = ""
        
    def adjust_bet(self, amount):
        """Adjust the current bet amount"""
        if self.hand_phase == "betting":
            self.bet = max(MIN_BET, min(MAX_BET, min(self.bankroll, self.bet + amount)))
    
    def place_bet(self):
        """Place the bet and start dealing"""
        if self.bet > 0 and self.bet <= self.bankroll and self.hand_phase == "betting":
            self.start_hand()
    
    def restart(self):
        """Restart for a new hand"""
        if self.bankroll > 0:
            self.message = ""
            self.player, self.dealer = [], []
            self.revealed = False
            self.hand_phase = "betting"
            self.state = 'betting'
    
    def reshoe_if_needed(self):
        if len(self.shoe) < 20:
            self.shoe = build_shoe(NUM_DECKS)

    def start_hand(self):
        self.message = ""
        self.player = []
        self.dealer = []
        self.revealed = False
        self.reshoe_if_needed()
        # dealing animation
        self.hand_phase = "dealing"
        self.state = 'playing'
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

    def hit(self):
        """Player hits"""
        if self.hand_phase == "player":
            self.player.append(self.shoe.pop())
            self.reshoe_if_needed()
            if is_bust(self.player):
                self.revealed = True
                self.hand_phase = "settle"
    
    def stand(self):
        """Player stands"""
        if self.hand_phase == "player":
            self.hand_phase = "dealer"

    def dealer_play(self):
        """Dealer plays automatically"""
        if self.hand_phase == "dealer":
            if hand_total(self.dealer) < 17:
                self.dealer.append(self.shoe.pop())
                self.reshoe_if_needed()
            else:
                self.revealed = True
                self.hand_phase = "settle"

    def handle_game_over(self):
        """Handle the end of the game"""
        if self.hand_phase == "settle":
            self.settle_hand()

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

        self.bankroll += delta
        self.player_money = self.bankroll  # Keep sync for main.py interface
        self.hand_phase = "done"
        self.state = 'game_over'

    def update(self):
        """Update game state - called each frame"""
        if self.hand_phase == "dealing":
            self.update_deal_anim()
        elif self.hand_phase == "dealer":
            # Dealer auto-plays with some pacing
            pygame.time.delay(350)
            self.dealer_play()
        elif self.hand_phase == "settle":
            self.settle_hand()

    def handle_click(self, mouse_pos):
        """Handle mouse clicks on the blackjack interface"""
        mx, my = mouse_pos
        # We'll implement this to work with the button rectangles
        rects = self.get_button_rects()
        
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
                self.hit()
            elif point_in_rect((mx, my), rects["stand"]):
                self.stand()
        elif self.hand_phase == "done":
            # next hand or end
            if self.bankroll <= 0:
                self.state = 'game_over'
            else:
                if point_in_rect((mx, my), rects["next"]):
                    self.restart()

    def get_button_rects(self):
        """Get button rectangles for click detection"""
        rects = {"minus": None, "plus": None, "deal": None, "hit": None, "stand": None, "next": None}
        
        # Betting controls
        if self.hand_phase == "betting":
            rects["minus"] = (300, 190, 60, 36)
            rects["plus"] = (370, 190, 60, 36)
            rects["deal"] = (450, 186, 140, 44)
        
        # Player action buttons
        if self.hand_phase == "player":
            screen_width = WIDTH
            screen_height = HEIGHT
            rects["hit"] = (screen_width-260, screen_height-180, 90, 48)
            rects["stand"] = (screen_width-160, screen_height-180, 90, 48)
        elif self.hand_phase == "done":
            screen_width = WIDTH
            screen_height = HEIGHT
            rects["next"] = (screen_width-200, screen_height-180, 140, 48)
        
        return rects

    def draw(self, surface):
        """Draw the blackjack table interface"""
        # Background
        surface.fill((14, 70, 50))
        pygame.draw.rect(surface, TABLE_COLOR, (60, 80, WIDTH-120, HEIGHT-160), border_radius=30)
        pygame.draw.rect(surface, GOLD, (60, 80, WIDTH-120, HEIGHT-160), width=4, border_radius=30)
        draw_text(surface, "Blackjack Table", FONT_BIG, WHITE, WIDTH//2, 110, center=True)

        # Bankroll and bet
        draw_text(surface, f"Bankroll: ${self.bankroll}", FONT_MED, WHITE, 80, 160)
        draw_text(surface, f"Bet: ${self.bet}", FONT_MED, WHITE, 80, 200)

        rects = self.get_button_rects()

        # Betting controls
        if self.hand_phase == "betting":
            button(surface, rects["minus"], "-")
            button(surface, rects["plus"], "+")
            button(surface, rects["deal"], "Deal", enabled=(self.bet>0 and self.bet<=self.bankroll))
            draw_text(surface, "Adjust your bet, then Deal.", FONT, WHITE, 80, 240)

        # Dealer area
        draw_text(surface, "Dealer", FONT_MED, WHITE, 80, 270)
        self.draw_hand(surface, self.dealer, x0=160, y0=300, hide_first=(not self.revealed and self.hand_phase in ("player","dealing")))

        # Player area
        draw_text(surface, "You", FONT_MED, WHITE, 80, HEIGHT-230)
        self.draw_hand(surface, self.player, x0=160, y0=HEIGHT-200, hide_first=False)

        # Buttons for actions
        if self.hand_phase == "player":
            button(surface, rects["hit"], "Hit", enabled=True)
            button(surface, rects["stand"], "Stand", enabled=True)
        elif self.hand_phase == "done":
            button(surface, rects["next"], "Next Hand", enabled=(self.bankroll>0))

        # Message/status
        if self.message:
            draw_text(surface, self.message, FONT_MED, GOLD if "win" in self.message.lower() else WHITE, WIDTH//2, 170, center=True)

    def draw_hand(self, surface, cards, x0, y0, hide_first=False):
        # live cards
        for i, (r, s) in enumerate(cards):
            face_up = not (hide_first and i == 0)
            draw_card(surface, x0 + i*90, y0, r, s, face_up=face_up)
        # animating "in-flight" cards preview
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
                draw_card(surface, int(x), int(y), a["card"][0], a["card"][1], face_up=False)