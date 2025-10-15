# py_openworld_casino.py
# 2D top-down "open-world-ish" -> enter casino -> sit and play blackjack (with sprite support)
import sys, os, random, pygame

# ---------------- Config ----------------
WIN_W, WIN_H = 960, 540
FPS = 60

TILE = 32
WORLD_W, WORLD_H = 64, 48  # tiles
PLAYER_SPEED = 3.2

TABLE_COLOR = (7, 105, 57)
BG_COLOR = (18, 18, 22)
GOLD = (240, 200, 60)
WHITE = (245, 245, 245)
RED = (220, 60, 60)
BLACK = (0, 0, 0)
ACCENT = (160, 90, 255)
FLOOR = (40, 48, 58)
WALL = (24, 28, 34)
GRASS = (34, 72, 44)
ROAD = (60, 60, 60)
NEON = (120, 40, 140)

STARTING_BANKROLL = 200
MIN_BET = 10
MAX_BET = 500
NUM_DECKS = 6

MUSIC_FILE = "lobby_music.mp3"  # optional
CARDS_DIR = "cards"
CARD_W, CARD_H = 80, 112  # blackjack render size

# ---------------- Pygame init ----------------
pygame.init()
pygame.display.set_caption("Open-World Casino (Top-Down)")
screen = pygame.display.set_mode((WIN_W, WIN_H))
clock = pygame.time.Clock()

try:
    pygame.mixer.init()
    MUSIC_ENABLED = True
except pygame.error:
    MUSIC_ENABLED = False

FONT_BIG = pygame.font.SysFont("arialblack", 42)
FONT_HUD = pygame.font.SysFont("arial", 22, bold=True)
FONT = pygame.font.SysFont("arial", 20)
FONT_SMALL = pygame.font.SysFont("arial", 16)

# ---------------- Blackjack Logic ----------------
SUITS = ["♠", "♥", "♦", "♣"]
RANKS = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
VALUES = {**{str(i): i for i in range(2, 11)}, "J":10, "Q":10, "K":10, "A":11}
SUIT_LETTER = {"♠":"S","♥":"H","♦":"D","♣":"C"}

def build_shoe(num_decks=6):
    shoe=[]
    for _ in range(num_decks):
        for s in SUITS:
            for r in RANKS:
                shoe.append((r,s))
    random.shuffle(shoe)
    return shoe

def hand_total(cards):
    t, aces = 0, 0
    for r,_ in cards:
        t += VALUES[r]
        if r=="A": aces+=1
    while t>21 and aces:
        t -= 10; aces -= 1
    return t

def is_blackjack(cards): return len(cards)==2 and hand_total(cards)==21
def is_bust(cards): return hand_total(cards)>21

# ---------------- Card Sprites (fallback-safe) ----------------
CARD_IMAGES = {}
CARD_BACK = None
SPRITES_OK = False

def try_load_image(path):
    img = pygame.image.load(path).convert_alpha()
    return pygame.transform.smoothscale(img, (CARD_W, CARD_H))

def load_card_sprites():
    global SPRITES_OK, CARD_BACK, CARD_IMAGES
    if not os.path.isdir(CARDS_DIR):
        SPRITES_OK = False; return
    try:
        CARD_BACK = try_load_image(os.path.join(CARDS_DIR, "back.png"))
        for r in RANKS:
            for s in SUITS:
                name = f"{r}{SUIT_LETTER[s]}.png"
                CARD_IMAGES[(r,s)] = try_load_image(os.path.join(CARDS_DIR, name))
        SPRITES_OK = (len(CARD_IMAGES)==52 and CARD_BACK is not None)
    except Exception:
        SPRITES_OK = False

load_card_sprites()

def draw_card(surface, x, y, r, s, face_up=True):
    if SPRITES_OK:
        surface.blit(CARD_BACK if not face_up else CARD_IMAGES[(r,s)], (x,y))
    else:
        rect = pygame.Rect(x,y,CARD_W,CARD_H)
        if face_up:
            pygame.draw.rect(surface, WHITE, rect, border_radius=10)
            pygame.draw.rect(surface, BLACK, rect, 2, border_radius=10)
            col = RED if s in ("♥","♦") else BLACK
            surface.blit(FONT_SMALL.render(r, True, col), (x+8, y+6))
            surface.blit(FONT.render(s, True, col), (x+CARD_W//2-6, y+CARD_H//2-12))
            surface.blit(FONT_SMALL.render(r, True, col), (x+CARD_W-18, y+CARD_H-22))
        else:
            pygame.draw.rect(surface, (30,60,130), rect, border_radius=10)
            pygame.draw.rect(surface, WHITE, rect, 3, border_radius=10)
            pygame.draw.circle(surface, (200,220,255), (x+CARD_W//2, y+CARD_H//2), 18)

# ---------------- Game States ----------------
STATE_WORLD   = "world"     # outside top-down
STATE_CASINO  = "casino"    # inside lobby top-down
STATE_TABLE   = "table"     # blackjack UI
STATE_GAMEOVER = "gameover"

# ---------------- World Map ----------------
# Tiles:
# ' ' grass, '.' road, '#' wall, 'C' casino building door outside, 'T' table spot (inside)
WORLD_MAP = []
for y in range(WORLD_H):
    row = []
    for x in range(WORLD_W):
        if y in (0, WORLD_H-1) or x in (0, WORLD_W-1):
            row.append('#')  # border walls
        elif 18<=y<=22 and 6<=x<=56:
            row.append('.')  # road stripe
        else:
            row.append(' ')  # grass
    WORLD_MAP.append(row)

# Place a casino block with a door 'C'
cx, cy = 30, 12
for yy in range(cy, cy+8):
    for xx in range(cx-6, cx+6):
        WORLD_MAP[yy][xx] = '#'
# Door
WORLD_MAP[cy+7][cx] = 'C'
# Add a little sidewalk
for xx in range(cx-3, cx+4):
    WORLD_MAP[cy+8][xx] = '.'

# Inside casino (simple room), separate tile grid:
CASINO_W, CASINO_H = 26, 18
CASINO_MAP = [['#' if y in (0,CASINO_H-1) or x in (0,CASINO_W-1) else FLOOR for x in range(CASINO_W)] for y in range(CASINO_H)]
# Door back to outside at bottom center
CASINO_MAP[CASINO_H-1][CASINO_W//2] = '.'  # exit tile line
# Table area: glowing ellipse center, place interaction tile 'T'
table_x, table_y = CASINO_W//2, CASINO_H//2
CASINO_MAP[table_y][table_x] = 'T'

def is_solid(tile):
    return tile == '#'  # walls are solid

# ---------------- Entities ----------------
class Player:
    def __init__(self, x, y):
        self.x = x; self.y = y  # world pixels
        self.w = 22; self.h = 28
        self.color = (60, 170, 255)
        self.vx = self.vy = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def input_move(self):
        keys = pygame.key.get_pressed()
        self.vx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        self.vy = (keys[pygame.K_DOWN]  or keys[pygame.K_s]) - (keys[pygame.K_UP]   or keys[pygame.K_w])
        if self.vx and self.vy:
            # normalize diagonal
            self.vx *= 0.7071; self.vy *= 0.7071
        self.vx *= PLAYER_SPEED
        self.vy *= PLAYER_SPEED

    def move_and_collide(self, tilemap):
        # Horizontal
        new_x = self.x + self.vx
        if not self.collides_at(new_x, self.y, tilemap):
            self.x = new_x
        # Vertical
        new_y = self.y + self.vy
        if not self.collides_at(self.x, new_y, tilemap):
            self.y = new_y

    def collides_at(self, px, py, tilemap):
        rect = pygame.Rect(int(px), int(py), self.w, self.h)
        # check nearby tiles
        tx0, ty0 = rect.left//TILE, rect.top//TILE
        tx1, ty1 = rect.right//TILE, rect.bottom//TILE
        h = len(tilemap); w = len(tilemap[0])
        for ty in range(max(0,ty0), min(h, ty1+1)):
            for tx in range(max(0,tx0), min(w, tx1+1)):
                t = tilemap[ty][tx]
                if is_solid(t):
                    tile_rect = pygame.Rect(tx*TILE, ty*TILE, TILE, TILE)
                    if rect.colliderect(tile_rect):
                        return True
        return False

    def draw(self, surf, camx, camy):
        pygame.draw.rect(surf, BLACK, (self.x-camx-2, self.y-camy-2, self.w+4, self.h+4), border_radius=6)
        pygame.draw.rect(surf, self.color, (self.x-camx, self.y-camy, self.w, self.h), border_radius=6)

# ---------------- Blackjack Table Screen ----------------
class BlackjackTable:
    def __init__(self):
        self.bankroll = STARTING_BANKROLL
        self.bet = MIN_BET
        self.shoe = build_shoe(NUM_DECKS)
        self.player=[]
        self.dealer=[]
        self.revealed=False
        self.phase="betting"  # betting, dealing, player, dealer, settle, done
        self.message=""
        self.anim=[]

    def reshoe(self):
        if len(self.shoe)<20:
            self.shoe = build_shoe(NUM_DECKS)

    def card_to(self, who, idx):
        if who=="player":
            return (160 + idx*(CARD_W+10), 340)
        else:
            return (160 + idx*(CARD_W+10), 120)

    def start_hand(self):
        self.message=""; self.player=[]; self.dealer=[]; self.revealed=False; self.reshoe()
        self.phase="dealing"; self.anim=[]
        order=[("player",0),("dealer",0),("player",1),("dealer",1)]
        t=0
        for who,idx in order:
            self.anim.append({
                "who":who,"idx":idx,
                "t_start":pygame.time.get_ticks()+t,
                "from":(WIN_W//2,-140),
                "to":self.card_to(who,idx),
                "arrived":False,
                "card":self.shoe.pop()
            })
            t+=220

    def update_deal_anim(self):
        now = pygame.time.get_ticks()
        moving=False
        for a in self.anim:
            if a["arrived"] or now<a["t_start"]: continue
            dt = (now - a["t_start"]) / 220.0
            if dt>=1.0:
                a["arrived"]=True
                (self.player if a["who"]=="player" else self.dealer).append(a["card"])
            else:
                moving=True
        self.anim=[x for x in self.anim if not x["arrived"] or now<x["t_start"]]
        if not moving and all(x["arrived"] or now>=x["t_start"] for x in self.anim):
            self.anim.clear()
            if is_blackjack(self.player) or is_blackjack(self.dealer):
                self.phase="settle"; self.revealed=True
            else:
                self.phase="player"

    def settle(self):
        p,d = hand_total(self.player), hand_total(self.dealer)
        if is_blackjack(self.player) and is_blackjack(self.dealer):
            self.message="Both blackjack — Push."; delta=0
        elif is_blackjack(self.player):
            win=int(self.bet*1.5); self.message=f"Blackjack! You win ${win}."; delta=win
        elif is_blackjack(self.dealer):
            self.message="Dealer blackjack. You lose."; delta=-self.bet
        else:
            if is_bust(self.player): self.message="You bust."; delta=-self.bet
            elif is_bust(self.dealer): self.message="Dealer busts. You win!"; delta=self.bet
            else:
                if p>d: self.message="You win!"; delta=self.bet
                elif p<d: self.message="Dealer wins."; delta=-self.bet
                else: self.message="Push."; delta=0
        self.bankroll += delta
        self.phase = "done"

    def draw(self, surf):
        surf.fill((14,70,50))
        pygame.draw.rect(surf, TABLE_COLOR, (40,40, WIN_W-80, WIN_H-80), border_radius=28)
        pygame.draw.rect(surf, GOLD, (40,40, WIN_W-80, WIN_H-80), 4, border_radius=28)
        center = (WIN_W//2, 80)
        surf.blit(FONT_BIG.render("Blackjack", True, WHITE), (center[0]-120, 50))
        surf.blit(FONT_HUD.render(f"Bankroll: ${self.bankroll}", True, WHITE), (60, 100))
        surf.blit(FONT_HUD.render(f"Bet: ${self.bet}", True, WHITE), (60, 130))
        # Dealer area
        surf.blit(FONT_HUD.render("Dealer", True, WHITE), (60, 160))
        self.draw_hand(surf, self.dealer, 160, 200, hide_first=(not self.revealed and self.phase in ("dealing","player")))
        # Player area
        surf.blit(FONT_HUD.render("You", True, WHITE), (60, 340))
        self.draw_hand(surf, self.player, 160, 380, hide_first=False)

        # Buttons
        btns = {}
        if self.phase=="betting":
            btns["-"] = draw_button(surf, (350, 120, 44, 36), "-")
            btns["+"] = draw_button(surf, (402, 120, 44, 36), "+")
            btns["deal"] = draw_button(surf, (456, 116, 120, 44), "Deal", enabled=(self.bet>0 and self.bet<=self.bankroll))
            draw_center_text(surf, "Adjust your bet then press Deal. [Esc to stand up]", (WIN_W//2, 170))
        elif self.phase=="player":
            btns["hit"] = draw_button(surf, (WIN_W-250, WIN_H-120, 90, 44), "Hit")
            btns["stand"] = draw_button(surf, (WIN_W-150, WIN_H-120, 90, 44), "Stand")
        elif self.phase=="done":
            btns["next"] = draw_button(surf, (WIN_W-190, WIN_H-120, 140, 44), "Next Hand", enabled=(self.bankroll>0))
            draw_center_text(surf, "[Esc to stand up]", (WIN_W//2, 170))
        if self.message:
            color = GOLD if "win" in self.message.lower() else WHITE
            draw_center_text(surf, self.message, (WIN_W//2, 135), color=color)
        return btns

    def draw_hand(self, surf, cards, x0, y0, hide_first=False):
        for i,(r,s) in enumerate(cards):
            face = not(hide_first and i==0)
            draw_card(surf, x0+i*(CARD_W+10), y0, r, s, face_up=face)
        now = pygame.time.get_ticks()
        for a in self.anim:
            if now < a["t_start"]: continue
            fx,fy = a["from"]; tx,ty = a["to"]
            dt = (now - a["t_start"])/220.0
            if dt<1.0:
                x = fx+(tx-fx)*dt; y = fy+(ty-fy)*dt
                draw_card(surf, int(x), int(y), a["card"][0], a["card"][1], face_up=False)

    def update(self):
        if self.phase=="dealing":
            self.update_deal_anim()
        elif self.phase=="dealer":
            pygame.time.delay(350)
            if hand_total(self.dealer)<17:
                self.dealer.append(self.shoe.pop()); self.reshoe()
            else:
                self.revealed=True; self.phase="settle"
        elif self.phase=="settle":
            self.settle()

    def click(self, pos, btns):
        if self.phase=="betting":
            if point_in_rect(pos, btns.get("-")): self.bet=max(MIN_BET, self.bet-MIN_BET)
            elif point_in_rect(pos, btns.get("+")): self.bet=min(MAX_BET, min(self.bankroll, self.bet+MIN_BET))
            elif point_in_rect(pos, btns.get("deal")):
                if MIN_BET<=self.bet<=min(MAX_BET,self.bankroll): self.start_hand()
        elif self.phase=="player":
            if point_in_rect(pos, btns.get("hit")):
                self.player.append(self.shoe.pop()); self.reshoe()
                if is_bust(self.player):
                    self.revealed=True; self.phase="settle"
            elif point_in_rect(pos, btns.get("stand")):
                self.phase="dealer"
        elif self.phase=="done":
            if self.bankroll>0 and point_in_rect(pos, btns.get("next")):
                self.message=""; self.player=[]; self.dealer=[]; self.revealed=False; self.phase="betting"

# ---------------- UI helpers ----------------
def point_in_rect(pos, rect):
    return rect and pygame.Rect(rect).collidepoint(pos)

def draw_button(surf, rect, label, enabled=True):
    x,y,w,h = rect
    color = ACCENT if enabled else (80,80,90)
    pygame.draw.rect(surf, color, rect, border_radius=10)
    pygame.draw.rect(surf, (255,255,255), rect, 2, border_radius=10)
    txt = FONT_HUD.render(label, True, WHITE if enabled else (200,200,200))
    surf.blit(txt, (x + (w-txt.get_width())//2, y + (h-txt.get_height())//2))
    return rect if enabled else None

def draw_center_text(surf, text, center, color=WHITE):
    t = FONT.render(text, True, color)
    surf.blit(t, (center[0]-t.get_width()//2, center[1]-t.get_height()//2))

# ---------------- Render tiles ----------------
def draw_tilemap(surf, tilemap, camx, camy, palette):
    h = len(tilemap); w = len(tilemap[0])
    for ty in range(h):
        for tx in range(w):
            ch = tilemap[ty][tx]
            x = tx*TILE - camx
            y = ty*TILE - camy
            if ch == '#':
                pygame.draw.rect(surf, WALL, (x,y,TILE,TILE))
            elif ch == '.':
                pygame.draw.rect(surf, ROAD, (x,y,TILE,TILE))
            elif ch == 'T':
                pygame.draw.rect(surf, FLOOR if isinstance(FLOOR,tuple) else FLOOR, (x,y,TILE,TILE))
                # glowing table cue
                pygame.draw.ellipse(surf, NEON, (x-12,y-6, TILE+24, TILE+12), 2)
            elif ch == 'C':
                pygame.draw.rect(surf, WALL, (x,y,TILE,TILE))
                pygame.draw.rect(surf, NEON, (x+4,y+6,TILE-8,TILE-12), 2)
            else:
                pygame.draw.rect(surf, GRASS, (x,y,TILE,TILE))

# ---------------- Main Game Controller ----------------
class Game:
    def __init__(self):
        self.state = STATE_WORLD
        # outside spawn
        self.player = Player((cx*TILE), (cy+10)*TILE)  # near casino
        self.bankroll = STARTING_BANKROLL
        self.table = BlackjackTable()
        self.camera_x = 0; self.camera_y = 0
        self.inside_player = Player((CASINO_W//2 * TILE), (CASINO_H-3)*TILE)
        self.music_loaded=False
        if MUSIC_ENABLED and os.path.exists(MUSIC_FILE):
            try:
                pygame.mixer.music.load(MUSIC_FILE)
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
                self.music_loaded=True
            except Exception:
                self.music_loaded=False

    def world_events(self, ev):
        if ev.type==pygame.KEYDOWN and ev.key==pygame.K_e:
            # interact if near casino door 'C'
            if self.near_world_door():
                self.state = STATE_CASINO
                # enter inside at bottom door
                self.inside_player.x = (CASINO_W//2)*TILE
                self.inside_player.y = (CASINO_H-3)*TILE

    def casino_events(self, ev):
        if ev.type==pygame.KEYDOWN:
            if ev.key==pygame.K_e:
                # interact: near table? start blackjack; near exit? go outside
                if self.near_inside_table():
                    self.table.phase="betting"
                    self.state=STATE_TABLE
                elif self.near_inside_exit():
                    self.state=STATE_WORLD
            if ev.key==pygame.K_ESCAPE:
                self.state=STATE_WORLD

    def table_events(self, ev):
        if ev.type==pygame.KEYDOWN and ev.key==pygame.K_ESCAPE:
            self.state=STATE_CASINO  # stand up
        if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
            btns = self.table.draw(screen)  # get same geometry
            self.table.click(pygame.mouse.get_pos(), btns)

    # ----------- Proximity checks -----------
    def near_world_door(self):
        # if player's rect overlaps tile 'C'
        rect = self.player.rect
        tx0,ty0 = rect.centerx//TILE, rect.centery//TILE
        return WORLD_MAP[ty0][tx0]=='C'

    def near_inside_exit(self):
        # bottom doorway (row CASINO_H-1 is pass-through line)
        return self.inside_player.rect.centery//TILE >= CASINO_H-2 and abs(self.inside_player.rect.centerx//TILE - CASINO_W//2) <= 1

    def near_inside_table(self):
        tx = self.inside_player.rect.centerx//TILE
        ty = self.inside_player.rect.centery//TILE
        return CASINO_MAP[ty][tx] == 'T'

    # ----------- Updates -----------
    def update_world(self):
        self.player.input_move()
        self.player.move_and_collide(WORLD_MAP)
        # camera centers on player
        self.camera_x = int(self.player.x + self.player.w/2 - WIN_W/2)
        self.camera_y = int(self.player.y + self.player.h/2 - WIN_H/2)
        self.camera_x = max(0, min(self.camera_x, WORLD_W*TILE - WIN_W))
        self.camera_y = max(0, min(self.camera_y, WORLD_H*TILE - WIN_H))

    def update_casino(self):
        self.inside_player.input_move()
        self.inside_player.move_and_collide(CASINO_MAP)

    def update_table(self):
        self.table.update()
        if self.table.bankroll <= 0 and self.state==STATE_TABLE:
            self.state = STATE_GAMEOVER

    # ----------- Draws -----------
    def draw_world(self):
        draw_tilemap(screen, WORLD_MAP, self.camera_x, self.camera_y, None)
        self.player.draw(screen, self.camera_x, self.camera_y)
        draw_center_text(screen, "Find the neon door and press [E] to enter.", (WIN_W//2, 24))

    def draw_casino(self):
        # simple tiled room; no camera needed
        # draw floor/walls
        for y in range(CASINO_H):
            for x in range(CASINO_W):
                ch = CASINO_MAP[y][x]
                px, py = x*TILE + (WIN_W - CASINO_W*TILE)//2, y*TILE + (WIN_H - CASINO_H*TILE)//2
                if ch=='#':
                    pygame.draw.rect(screen, WALL, (px,py,TILE,TILE))
                else:
                    pygame.draw.rect(screen, FLOOR, (px,py,TILE,TILE))
                if ch=='T':
                    pygame.draw.ellipse(screen, (90,180,120), (px-20,py-10, TILE+40, TILE+20), 3)
                if y==CASINO_H-1 and x==CASINO_W//2:
                    pygame.draw.rect(screen, ROAD, (px,py,TILE,TILE))
        # offset player the same way
        offx = (WIN_W - CASINO_W*TILE)//2
        offy = (WIN_H - CASINO_H*TILE)//2
        pygame.draw.rect(screen, BLACK, (offx+4, offy+4, CASINO_W*TILE-8, 36), 0)
        screen.blit(FONT_HUD.render("Inside Casino: walk to the glowing table and press [E]. Exit at bottom. [Esc to leave]", True, WHITE), (offx+12, offy+8))
        # draw player
        pygame.draw.rect(screen, BLACK, (offx-2 + self.inside_player.x, offy-2 + self.inside_player.y, self.inside_player.w+4, self.inside_player.h+4), border_radius=6)
        pygame.draw.rect(screen, (60,170,255), (offx + self.inside_player.x, offy + self.inside_player.y, self.inside_player.w, self.inside_player.h), border_radius=6)

    def draw_table(self):
        self.table.draw(screen)

    def draw_gameover(self):
        screen.fill(BG_COLOR)
        draw_center_text(screen, "You went broke. GAME OVER", (WIN_W//2, WIN_H//2-16), color=RED)
        draw_center_text(screen, "Press R to respawn outside", (WIN_W//2, WIN_H//2+18))

    # ----------- Event loop -----------
    def run(self):
        while True:
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT:
                    pygame.quit(); sys.exit(0)
                if self.state==STATE_WORLD:
                    if ev.type==pygame.KEYDOWN and ev.key==pygame.K_r:
                        self.__init__()  # restart
                    self.world_events(ev)
                elif self.state==STATE_CASINO:
                    self.casino_events(ev)
                elif self.state==STATE_TABLE:
                    self.table_events(ev)
                elif self.state==STATE_GAMEOVER:
                    if ev.type==pygame.KEYDOWN and ev.key==pygame.K_r:
                        self.__init__()

            # update
            if self.state==STATE_WORLD: self.update_world()
            elif self.state==STATE_CASINO: self.update_casino()
            elif self.state==STATE_TABLE: self.update_table()

            # draw
            if self.state==STATE_WORLD: self.draw_world()
            elif self.state==STATE_CASINO: self.draw_casino()
            elif self.state==STATE_TABLE: self.draw_table()
            elif self.state==STATE_GAMEOVER: self.draw_gameover()

            pygame.display.flip()
            clock.tick(FPS)

# -------------- Run --------------
if __name__ == "__main__":
    Game().run()