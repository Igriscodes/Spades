import pygame
import random
import math
import sys

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 800
FPS = 60

GREEN_FELT = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 20, 20)
BLUE = (30, 30, 180)
GOLD = (255, 215, 0)
GRAY = (180, 180, 180)
LIGHT_GRAY = (220, 220, 220)
DARK_GRAY = (100, 100, 100)
HIGHLIGHT_GREEN = (50, 205, 50)
SHADOW_COLOR = (0, 0, 0, 100)

CARD_WIDTH = 90
CARD_HEIGHT = 130
CORNER_RADIUS = 8

POPUP_HEIGHT = 20
HOVER_SCALE = 1.08
ANIMATION_SPEED = 8.0

SUITS = ["Spades", "Hearts", "Diamonds", "Clubs"]
VALUES = list(range(2, 15))
VALUE_NAMES = {11: "J", 12: "Q", 13: "K", 14: "A"}

STATE_MENU = "menu"
STATE_NAME_SELECT = "name_select"
STATE_DEAL = "dealing"
STATE_BID = "bidding"
STATE_PLAY = "playing"
STATE_TRICK_END = "trick_end"
STATE_ROUND_END = "round_end"
STATE_GAME_OVER = "game_over"

INDIAN_NAMES = ["Arjun", "Rohan", "Aditya", "Vikram", "Rahul", "Karan", "Rajesh", "Amit", 
                "Priya", "Anjali", "Neha", "Pooja", "Kavya", "Sanya", "Riya"]

def ease_out_cubic(t):
    return 1 - pow(1 - t, 3)

def ease_in_out_quad(t):
    return 2 * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2

def ease_out_bounce(t):
    if t < 1 / 2.75:
        return 7.5625 * t * t
    elif t < 2 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375

class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value
        self.display_value = VALUE_NAMES.get(value, str(value))
        self.color = RED if suit in ["Hearts", "Diamonds"] else BLACK
        self.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
        self.pos = [0.0, 0.0]
        self.target_pos = [0.0, 0.0]
        self.is_moving = False
        self.face_up = False
        self.hovered = False
        self.is_playable = False

        self.hover_offset = 0.0
        self.target_hover_offset = 0.0
        self.scale = 1.0
        self.target_scale = 1.0
        self.rotation = 0.0
        self.target_rotation = 0.0
        self.arc_height = 0.0
        self.animation_progress = 1.0
        self.start_pos = [0.0, 0.0]
        self.shake_offset = 0.0
        self.shake_timer = 0.0

        self.shadow_offset = 3
        self.draw_order = 0

    def update(self, dt):
        if self.is_moving:
            speed = ANIMATION_SPEED * dt
            self.animation_progress = min(1.0, self.animation_progress + speed)

            t = ease_out_cubic(self.animation_progress)

            self.pos[0] = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * t
            base_y = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * t

            arc_progress = math.sin(self.animation_progress * math.pi)
            self.pos[1] = base_y - self.arc_height * arc_progress

            if self.animation_progress >= 1.0:
                self.pos = list(self.target_pos)
                self.is_moving = False
                self.arc_height = 0.0
                self.animation_progress = 1.0

        hover_speed = 15.0 * dt
        if abs(self.hover_offset - self.target_hover_offset) > 0.5:
            diff = self.target_hover_offset - self.hover_offset
            self.hover_offset += diff * hover_speed
        else:
            self.hover_offset = self.target_hover_offset

        scale_speed = 10.0 * dt
        if abs(self.scale - self.target_scale) > 0.01:
            diff = self.target_scale - self.scale
            self.scale += diff * scale_speed
        else:
            self.scale = self.target_scale

        if abs(self.rotation - self.target_rotation) > 0.1:
            diff = self.target_rotation - self.rotation
            self.rotation += diff * 10.0 * dt
        else:
            self.rotation = self.target_rotation

        if self.shake_timer > 0:
            self.shake_timer -= dt
            self.shake_offset = math.sin(self.shake_timer * 50) * 10 * self.shake_timer
        else:
            self.shake_offset = 0.0

        final_y = int(self.pos[1] - self.hover_offset)
        final_x = int(self.pos[0] + self.shake_offset)
        self.rect.topleft = (final_x, final_y)

    def set_target(self, x, y, arc_height=0):
        self.start_pos = list(self.pos)
        self.target_pos = [float(x), float(y)]
        self.is_moving = True
        self.animation_progress = 0.0
        self.arc_height = arc_height

    def shake(self):
        self.shake_timer = 0.3

    def set_playable(self, playable):
        self.is_playable = playable
        if playable:
            self.target_hover_offset = POPUP_HEIGHT
        else:
            self.target_hover_offset = 0

    def get_hover_rect(self):
        scaled_width = int(CARD_WIDTH * self.scale)
        scaled_height = int(CARD_HEIGHT * self.scale)
        center_x = self.rect.centerx
        center_y = self.rect.centery
        hover_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
        hover_rect.center = (center_x, center_y)
        return hover_rect

    def draw(self, surface, font_large, font_small):
        scaled_width = int(CARD_WIDTH * self.scale)
        scaled_height = int(CARD_HEIGHT * self.scale)
        center_x = self.rect.centerx
        center_y = self.rect.centery

        scaled_rect = pygame.Rect(0, 0, scaled_width, scaled_height)
        scaled_rect.center = (center_x, center_y)

        shadow_offset = self.shadow_offset + int(self.hover_offset * 0.3)
        shadow_rect = scaled_rect.copy()
        shadow_rect.x += shadow_offset
        shadow_rect.y += shadow_offset

        shadow_surf = pygame.Surface((scaled_width + 10, scaled_height + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 80), 
                        pygame.Rect(5, 5, scaled_width, scaled_height), 
                        border_radius=CORNER_RADIUS)
        surface.blit(shadow_surf, (shadow_rect.x - 5, shadow_rect.y - 5))

        if not self.face_up:
            pygame.draw.rect(surface, BLUE, scaled_rect, border_radius=CORNER_RADIUS)
            pygame.draw.rect(surface, GOLD, scaled_rect, 3, border_radius=CORNER_RADIUS)

            for i in range(3):
                for j in range(4):
                    x = scaled_rect.x + 15 + i * 25
                    y = scaled_rect.y + 15 + j * 28
                    pygame.draw.circle(surface, GOLD, (x, y), 6, 2)
                    pygame.draw.circle(surface, WHITE, (x, y), 3, 1)
        else:
            if self.hovered and self.is_playable:
                bg_color = HIGHLIGHT_GREEN
                border_color = GOLD
                border_width = 4
            elif self.is_playable:
                bg_color = (240, 255, 240)
                border_color = HIGHLIGHT_GREEN
                border_width = 3
            else:
                bg_color = WHITE
                border_color = BLACK
                border_width = 2

            pygame.draw.rect(surface, bg_color, scaled_rect, border_radius=CORNER_RADIUS)
            pygame.draw.rect(surface, border_color, scaled_rect, border_width, border_radius=CORNER_RADIUS)

            scale_factor = self.scale

            label = font_large.render(self.display_value, True, self.color)
            label = pygame.transform.scale(label, 
                (int(label.get_width() * scale_factor), int(label.get_height() * scale_factor)))
            surface.blit(label, (scaled_rect.x + 8, scaled_rect.y + 5))

            self.draw_suit(surface, scaled_rect.x + 20, scaled_rect.y + 45, int(12 * scale_factor))

            self.draw_suit(surface, scaled_rect.centerx, scaled_rect.centery, int(20 * scale_factor))

            bottom_label = font_large.render(self.display_value, True, self.color)
            bottom_label = pygame.transform.scale(bottom_label,
                (int(bottom_label.get_width() * scale_factor), int(bottom_label.get_height() * scale_factor)))
            bottom_label = pygame.transform.rotate(bottom_label, 180)
            surface.blit(bottom_label, 
                        (scaled_rect.right - bottom_label.get_width() - 8, 
                         scaled_rect.bottom - bottom_label.get_height() - 5))

            self.draw_suit_rotated(surface, scaled_rect.right - 20, scaled_rect.bottom - 45, 
                                  int(12 * scale_factor))

    def draw_suit(self, surface, x, y, size):
        if self.suit == "Hearts":
            self.draw_heart(surface, x, y, size, self.color)
        elif self.suit == "Spades":
            self.draw_spade(surface, x, y, size, self.color)
        elif self.suit == "Diamonds":
            self.draw_diamond(surface, x, y, size, self.color)
        elif self.suit == "Clubs":
            self.draw_club(surface, x, y, size, self.color)

    def draw_suit_rotated(self, surface, x, y, size):
        temp_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
        self.draw_suit(temp_surf, size * 1.5, size * 1.5, size)
        rotated = pygame.transform.rotate(temp_surf, 180)
        surface.blit(rotated, (x - size * 1.5, y - size * 1.5))

    def draw_heart(self, surface, x, y, size, color):
        points = []
        for i in range(360):
            angle = math.radians(i)
            hx = size * (16 * math.sin(angle) ** 3) / 16
            hy = -size * (13 * math.cos(angle) - 5 * math.cos(2 * angle) - 
                         2 * math.cos(3 * angle) - math.cos(4 * angle)) / 16
            points.append((x + hx, y + hy))

        if len(points) > 2:
            pygame.draw.polygon(surface, color, points)

    def draw_spade(self, surface, x, y, size, color):
        points = []
        for i in range(360):
            angle = math.radians(i)
            sx = size * (16 * math.sin(angle) ** 3) / 16
            sy = size * (13 * math.cos(angle) - 5 * math.cos(2 * angle) - 
                        2 * math.cos(3 * angle) - math.cos(4 * angle)) / 16
            points.append((x + sx, y - sy))

        if len(points) > 2:
            pygame.draw.polygon(surface, color, points)

        stem_width = size // 3
        stem_height = size // 2
        stem_points = [
            (x - stem_width // 2, y + size // 4),
            (x + stem_width // 2, y + size // 4),
            (x + stem_width // 3, y + size // 2 + stem_height // 2),
            (x - stem_width // 3, y + size // 2 + stem_height // 2)
        ]
        pygame.draw.polygon(surface, color, stem_points)

    def draw_diamond(self, surface, x, y, size, color):
        points = [
            (x, y - size),
            (x + int(size * 0.7), y),
            (x, y + size),
            (x - int(size * 0.7), y)
        ]
        pygame.draw.polygon(surface, color, points)

    def draw_club(self, surface, x, y, size, color):
        r = size // 2
        pygame.draw.circle(surface, color, (int(x), int(y - r * 0.7)), r)
        pygame.draw.circle(surface, color, (int(x - r * 0.9), int(y + r * 0.4)), r)
        pygame.draw.circle(surface, color, (int(x + r * 0.9), int(y + r * 0.4)), r)

        stem_points = [
            (x, y + r),
            (x - r * 0.4, y + r * 1.6),
            (x + r * 0.4, y + r * 1.6)
        ]
        pygame.draw.polygon(surface, color, stem_points)

class Deck:
    def __init__(self):
        self.cards = [Card(suit, value) for suit in SUITS for value in VALUES]

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num_players):
        hands = [[] for _ in range(num_players)]
        for i, card in enumerate(self.cards):
            hands[i % num_players].append(card)
        return hands

class Player:
    def __init__(self, name, position, is_human=False):
        self.name = name
        self.position = position
        self.is_human = is_human
        self.hand = []
        self.bid = None
        self.tricks_won = 0
        self.score = 0
        self.bags = 0
        self.team = 0 if position in [0, 2] else 1

    def sort_hand(self):
        suit_order = {"Spades": 0, "Hearts": 1, "Clubs": 2, "Diamonds": 3}
        self.hand.sort(key=lambda c: (suit_order[c.suit], c.value))

    def get_valid_moves(self, lead_suit, spades_broken):
        if lead_suit is None:
            if spades_broken:
                return self.hand[:]
            else:
                non_spades = [c for c in self.hand if c.suit != "Spades"]
                return non_spades if non_spades else self.hand
        else:
            follow = [c for c in self.hand if c.suit == lead_suit]
            return follow if follow else self.hand

    def make_ai_bid(self):
        spades = [c for c in self.hand if c.suit == "Spades"]
        high_cards = [c for c in self.hand if c.value >= 12]
        bid = len([c for c in spades if c.value >= 10])
        bid += len([c for c in high_cards if c.suit != "Spades"])
        bid = max(1, min(bid, 7))
        return bid

    def make_ai_play(self, valid_cards, lead_suit, trick_pile, spades_broken):
        if not trick_pile:
            valid_cards.sort(key=lambda c: c.value)
            return valid_cards[0]
        else:
            current_winner = self.get_winning_card(trick_pile, lead_suit)
            can_beat = [c for c in valid_cards if self.card_beats(c, current_winner, lead_suit)]
            if can_beat:
                can_beat.sort(key=lambda c: c.value)
                return can_beat[0]
            else:
                valid_cards.sort(key=lambda c: c.value)
                return valid_cards[0]

    def get_winning_card(self, trick_pile, lead_suit):
        if not trick_pile:
            return None
        winner_card = trick_pile[0][1]
        for player, card in trick_pile[1:]:
            if self.card_beats(card, winner_card, lead_suit):
                winner_card = card
        return winner_card

    def card_beats(self, card, current_best, lead_suit):
        if current_best is None:
            return True
        if card.suit == "Spades" and current_best.suit != "Spades":
            return True
        if card.suit != "Spades" and current_best.suit == "Spades":
            return False
        if card.suit == current_best.suit:
            return card.value > current_best.value
        return False

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Spades - Professional Edition")
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("Arial", 60, bold=True)
        self.font_large = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.font_card = pygame.font.SysFont("Arial", 28, bold=True)

        self.state = STATE_MENU
        self.players = []
        self.deck = None
        self.current_player_idx = 0
        self.dealer_idx = 0

        self.trick_pile = []
        self.lead_suit = None
        self.spades_broken = False
        self.trick_winner = None

        self.team_scores = [0, 0]
        self.team_bags = [0, 0]

        self.timer = 0
        self.message = ""
        self.message_timer = 0

        self.button_hover = None
        self.available_names = []
        random_initial_names = self.get_random_names()
        self.selected_names = ["You", random_initial_names[0], random_initial_names[1], random_initial_names[2]]
        self.name_buttons = []

    def get_random_names(self):
        names = random.sample(INDIAN_NAMES, 3)
        return names

    def start_game(self):
        self.state = STATE_NAME_SELECT
        self.setup_name_buttons()

    def setup_name_buttons(self):
        self.name_buttons = []
        y_start = 300
        for i in range(3):
            btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, y_start + i * 80, 300, 60)
            self.name_buttons.append(btn_rect)

    def finalize_game_start(self):
        self.players = [
            Player(self.selected_names[0], 0, is_human=True),
            Player(self.selected_names[1], 1),
            Player(self.selected_names[2], 2),
            Player(self.selected_names[3], 3)
        ]
        self.dealer_idx = 0
        self.team_scores = [0, 0]
        self.team_bags = [0, 0]
        self.start_round()

    def start_round(self):
        for p in self.players:
            p.hand = []
            p.bid = None
            p.tricks_won = 0

        self.deck = Deck()
        self.deck.shuffle()
        hands = self.deck.deal(4)

        for i, player in enumerate(self.players):
            player.hand = hands[i]
            player.sort_hand()

        self.position_cards()
        self.state = STATE_DEAL
        self.timer = pygame.time.get_ticks()

    def position_cards(self):
        for player in self.players:
            self.position_player_hand(player)

    def position_player_hand(self, player):
        hand_len = len(player.hand)
        spacing = min(30, (SCREEN_WIDTH - 200) // max(hand_len, 1))

        if player.position == 0:
            start_x = SCREEN_WIDTH // 2 - (hand_len * spacing) // 2
            for i, card in enumerate(player.hand):
                card.set_target(start_x + i * spacing, SCREEN_HEIGHT - CARD_HEIGHT - 10)
                card.face_up = True
                card.target_rotation = 0
                card.draw_order = i
        elif player.position == 1:
            start_y = SCREEN_HEIGHT // 2 - (hand_len * 25) // 2
            for i, card in enumerate(player.hand):
                card.set_target(10, start_y + i * 25)
                card.face_up = False
                card.draw_order = i
        elif player.position == 2:
            start_x = SCREEN_WIDTH // 2 - (hand_len * spacing) // 2
            for i, card in enumerate(player.hand):
                card.set_target(start_x + i * spacing, 10)
                card.face_up = False
                card.draw_order = i
        elif player.position == 3:
            start_y = SCREEN_HEIGHT // 2 - (hand_len * 25) // 2
            for i, card in enumerate(player.hand):
                card.set_target(SCREEN_WIDTH - CARD_WIDTH - 10, start_y + i * 25)
                card.face_up = False
                card.draw_order = i

    def show_message(self, msg, duration=2000):
        self.message = msg
        self.message_timer = pygame.time.get_ticks() + duration

    def update_valid_cards(self):
        human = self.players[0]
        if self.state == STATE_PLAY and self.current_player_idx == 0:
            valid_moves = human.get_valid_moves(self.lead_suit, self.spades_broken)
            for card in human.hand:
                card.set_playable(card in valid_moves)
        else:
            for card in human.hand:
                card.set_playable(False)

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()

        if self.state == STATE_PLAY and self.current_player_idx == 0:
            human = self.players[0]
            any_hovered = False

            for card in reversed(human.hand):
                if card.is_playable:
                    hover_rect = card.get_hover_rect()
                    if hover_rect.collidepoint(mouse_pos) and not any_hovered:
                        card.hovered = True
                        card.target_scale = HOVER_SCALE
                        any_hovered = True
                    else:
                        card.hovered = False
                        card.target_scale = 1.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if self.state == STATE_MENU:
                    btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 60)
                    if btn_rect.collidepoint(mx, my):
                        self.start_game()

                elif self.state == STATE_NAME_SELECT:
                    start_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 150, 200, 60)
                    if start_btn.collidepoint(mx, my):
                        self.finalize_game_start()

                    for i, btn_rect in enumerate(self.name_buttons):
                        if btn_rect.collidepoint(mx, my):
                            self.selected_names[i + 1] = random.choice(INDIAN_NAMES)

                elif self.state == STATE_BID:
                    human = self.players[0]
                    if self.current_player_idx == 0 and human.bid is None:
                        for bid in range(1, 8):
                            btn_x = SCREEN_WIDTH // 2 - 250 + (bid - 1) * 75
                            btn_rect = pygame.Rect(btn_x, SCREEN_HEIGHT // 2 + 80, 60, 50)
                            if btn_rect.collidepoint(mx, my):
                                human.bid = bid
                                self.show_message(f"You bid {bid} tricks")
                                self.advance_bidding()

                elif self.state == STATE_PLAY:
                    if self.current_player_idx == 0:
                        human = self.players[0]
                        valid_moves = human.get_valid_moves(self.lead_suit, self.spades_broken)

                        for card in reversed(human.hand):
                            hover_rect = card.get_hover_rect()
                            if hover_rect.collidepoint(mx, my):
                                if card in valid_moves:
                                    self.play_card(human, card)
                                else:
                                    card.shake()
                                break

                elif self.state == STATE_GAME_OVER:
                    self.state = STATE_MENU

        return True

    def advance_bidding(self):
        self.current_player_idx = (self.current_player_idx + 1) % 4

        if all(p.bid is not None for p in self.players):
            total_bids = sum(p.bid for p in self.players)
            self.show_message(f"Total bids: {total_bids}/13 tricks")
            self.start_play()
        else:
            current = self.players[self.current_player_idx]
            if not current.is_human:
                self.timer = pygame.time.get_ticks()

    def start_play(self):
        self.state = STATE_PLAY
        self.current_player_idx = (self.dealer_idx + 1) % 4
        self.trick_pile = []
        self.lead_suit = None
        self.timer = pygame.time.get_ticks()
        self.update_valid_cards()

    def play_card(self, player, card):
        player.hand.remove(card)

        if not self.trick_pile:
            self.lead_suit = card.suit
            if card.suit == "Spades":
                self.spades_broken = True

        offsets = [(0, -80), (-100, 0), (0, 80), (100, 0)]
        offset = offsets[player.position]
        target_x = SCREEN_WIDTH // 2 - CARD_WIDTH // 2 + offset[0]
        target_y = SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2 + offset[1]

        card.set_target(target_x, target_y, arc_height=100)
        card.face_up = True
        card.set_playable(False)
        card.target_scale = 1.0
        card.hovered = False
        card.draw_order = 1000

        self.trick_pile.append((player, card))

        if len(self.trick_pile) == 4:
            self.end_trick()
        else:
            self.current_player_idx = (self.current_player_idx + 1) % 4
            self.timer = pygame.time.get_ticks()
            self.update_valid_cards()

        self.position_player_hand(player)

    def end_trick(self):
        winner_player = self.trick_pile[0][0]
        winner_card = self.trick_pile[0][1]

        for player, card in self.trick_pile[1:]:
            if player.card_beats(card, winner_card, self.lead_suit):
                winner_player = player
                winner_card = card

        winner_player.tricks_won += 1
        self.trick_winner = winner_player
        self.show_message(f"{winner_player.name} wins the trick!")
        self.state = STATE_TRICK_END
        self.timer = pygame.time.get_ticks()

    def update(self):
        dt = self.clock.tick(FPS) / 1000.0

        for player in self.players:
            for card in player.hand:
                card.update(dt)

        for player, card in self.trick_pile:
            card.update(dt)

        if self.state == STATE_DEAL:
            if pygame.time.get_ticks() - self.timer > 1000:
                all_dealt = all(not c.is_moving for p in self.players for c in p.hand)
                if all_dealt:
                    self.state = STATE_BID
                    self.current_player_idx = (self.dealer_idx + 1) % 4
                    self.show_message("Bidding starts! Bid 1-7 tricks.")
                    self.timer = pygame.time.get_ticks()

        elif self.state == STATE_BID:
            current = self.players[self.current_player_idx]
            if not current.is_human and current.bid is None:
                if pygame.time.get_ticks() - self.timer > 800:
                    current.bid = current.make_ai_bid()
                    self.show_message(f"{current.name} bids {current.bid}")
                    self.advance_bidding()

        elif self.state == STATE_PLAY:
            current = self.players[self.current_player_idx]
            if not current.is_human:
                if pygame.time.get_ticks() - self.timer > 800:
                    valid_moves = current.get_valid_moves(self.lead_suit, self.spades_broken)
                    if valid_moves:
                        card = current.make_ai_play(valid_moves, self.lead_suit,
                                                   self.trick_pile, self.spades_broken)
                        self.play_card(current, card)

        elif self.state == STATE_TRICK_END:
            if pygame.time.get_ticks() - self.timer > 1500:
                self.trick_pile = []
                self.lead_suit = None

                if all(len(p.hand) == 0 for p in self.players):
                    self.end_round()
                else:
                    self.current_player_idx = self.players.index(self.trick_winner)
                    self.state = STATE_PLAY
                    self.timer = pygame.time.get_ticks()
                    self.update_valid_cards()

        elif self.state == STATE_ROUND_END:
            if pygame.time.get_ticks() - self.timer > 3000:
                if max(self.team_scores) >= 500:
                    self.state = STATE_GAME_OVER
                else:
                    self.dealer_idx = (self.dealer_idx + 1) % 4
                    self.start_round()

    def end_round(self):
        for team_idx in range(2):
            team_players = [p for p in self.players if p.team == team_idx]
            total_bid = sum(p.bid for p in team_players)
            total_won = sum(p.tricks_won for p in team_players)

            if total_won >= total_bid:
                points = total_bid * 10
                bags = total_won - total_bid
                self.team_bags[team_idx] += bags

                if self.team_bags[team_idx] >= 10:
                    points -= 100
                    self.team_bags[team_idx] -= 10
                    self.show_message(f"Team {team_idx + 1} bagged out! -100 points")

                self.team_scores[team_idx] += points + bags
            else:
                self.team_scores[team_idx] -= total_bid * 10

        self.state = STATE_ROUND_END
        self.timer = pygame.time.get_ticks()

    def draw(self):
        self.screen.fill(GREEN_FELT)

        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_NAME_SELECT:
            self.draw_name_select()
        elif self.state == STATE_GAME_OVER:
            self.draw_game_over()
        else:
            self.draw_game()

        if pygame.time.get_ticks() < self.message_timer and self.message:
            alpha = min(255, (self.message_timer - pygame.time.get_ticks()) // 2)
            msg_surf = self.font_medium.render(self.message, True, WHITE)
            msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))

            bg_surf = pygame.Surface((msg_rect.width + 40, msg_rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (*DARK_GREEN, min(200, alpha)), 
                           bg_surf.get_rect(), border_radius=10)
            self.screen.blit(bg_surf, (msg_rect.x - 20, msg_rect.y - 10))

            msg_surf.set_alpha(alpha)
            self.screen.blit(msg_surf, msg_rect)

        pygame.display.flip()

    def draw_menu(self):
        title = self.font_title.render("SPADES", True, GOLD)
        shadow = self.font_title.render("SPADES", True, BLACK)
        self.screen.blit(shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, 153))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))

        subtitle = self.font_medium.render("Professional Edition", True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, 230))

        mouse_pos = pygame.mouse.get_pos()
        btn_rect = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 60)
        is_hover = btn_rect.collidepoint(mouse_pos)

        btn_color = WHITE if is_hover else GOLD
        pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=10)
        pygame.draw.rect(self.screen, GOLD if is_hover else WHITE, btn_rect, 3, border_radius=10)

        btn_text = self.font_large.render("START", True, BLACK)
        self.screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width()//2,
                                    btn_rect.centery - btn_text.get_height()//2))

        rules = [
            "Rules:",
            "• Bid number of tricks you'll win",
            "• Spades are always trump",
            "• Must follow suit if possible",
            "• First to 500 points wins",
            "• 10 bags = -100 points"
        ]
        y = SCREEN_HEIGHT//2 + 120
        for rule in rules:
            text = self.font_small.render(rule, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y))
            y += 25

    def draw_name_select(self):
        title = self.font_title.render("SELECT PLAYER NAMES", True, GOLD)
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 100))

        positions = ["West", "North", "East"]
        mouse_pos = pygame.mouse.get_pos()

        for i, btn_rect in enumerate(self.name_buttons):
            is_hover = btn_rect.collidepoint(mouse_pos)

            btn_color = HIGHLIGHT_GREEN if is_hover else GOLD
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, btn_rect, 3, border_radius=10)

            label_text = self.font_small.render(f"{positions[i]}:", True, WHITE)
            self.screen.blit(label_text, (btn_rect.x + 10, btn_rect.y + 10))

            name_text = self.font_medium.render(self.selected_names[i + 1], True, BLACK)
            self.screen.blit(name_text, (btn_rect.centerx - name_text.get_width()//2,
                                        btn_rect.centery - name_text.get_height()//2 + 5))

        start_btn = pygame.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 150, 200, 60)
        is_hover = start_btn.collidepoint(mouse_pos)

        btn_color = WHITE if is_hover else GOLD
        pygame.draw.rect(self.screen, btn_color, start_btn, border_radius=10)
        pygame.draw.rect(self.screen, GOLD if is_hover else WHITE, start_btn, 3, border_radius=10)

        btn_text = self.font_large.render("START GAME", True, BLACK)
        self.screen.blit(btn_text, (start_btn.centerx - btn_text.get_width()//2,
                                    start_btn.centery - btn_text.get_height()//2))

        hint = self.font_small.render("Click on names to randomize", True, GRAY)
        self.screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 80))

    def draw_game_over(self):
        title = self.font_title.render("GAME OVER", True, GOLD)
        shadow = self.font_title.render("GAME OVER", True, BLACK)
        self.screen.blit(shadow, (SCREEN_WIDTH//2 - title.get_width()//2 + 3, 203))
        self.screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 200))

        winner = f"{self.players[0].name} & {self.players[2].name}" if self.team_scores[0] > self.team_scores[1] else f"{self.players[1].name} & {self.players[3].name}"
        winner_text = self.font_large.render(f"{winner} WIN!", True, WHITE)
        self.screen.blit(winner_text, (SCREEN_WIDTH//2 - winner_text.get_width()//2, 300))

        score_text = self.font_medium.render(
            f"{self.players[0].name} & {self.players[2].name}: {self.team_scores[0]} | {self.players[1].name} & {self.players[3].name}: {self.team_scores[1]}",
            True, WHITE)
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, 370))

        click_text = self.font_small.render("Click anywhere to return to menu", True, GRAY)
        self.screen.blit(click_text, (SCREEN_WIDTH//2 - click_text.get_width()//2, 500))

    def draw_game(self):
        pygame.draw.rect(self.screen, DARK_GREEN, (0, 0, SCREEN_WIDTH, 40))
        score_text = f"{self.players[0].name} & {self.players[2].name}: {self.team_scores[0]} (Bags: {self.team_bags[0]}) | "                     f"{self.players[1].name} & {self.players[3].name}: {self.team_scores[1]} (Bags: {self.team_bags[1]})"
        score_surf = self.font_small.render(score_text, True, GOLD)
        self.screen.blit(score_surf, (10, 10))

        for player in self.players:
            self.draw_player_info(player)

        all_cards = []
        for player in self.players:
            all_cards.extend(player.hand)
        for player, card in self.trick_pile:
            all_cards.append(card)

        all_cards.sort(key=lambda c: (c.draw_order, c.hover_offset))

        for card in all_cards:
            card.draw(self.screen, self.font_card, self.font_small)

        if self.state == STATE_BID:
            human = self.players[0]
            if self.current_player_idx == 0 and human.bid is None:
                mouse_pos = pygame.mouse.get_pos()

                bg_rect = pygame.Rect(SCREEN_WIDTH//2 - 280, SCREEN_HEIGHT//2 + 30, 560, 110)
                pygame.draw.rect(self.screen, DARK_GREEN, bg_rect, border_radius=10)
                pygame.draw.rect(self.screen, GOLD, bg_rect, 3, border_radius=10)

                prompt = self.font_medium.render("Choose your bid:", True, WHITE)
                self.screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2,
                                         SCREEN_HEIGHT//2 + 45))

                for bid in range(1, 8):
                    btn_x = SCREEN_WIDTH // 2 - 250 + (bid - 1) * 75
                    btn_rect = pygame.Rect(btn_x, SCREEN_HEIGHT // 2 + 80, 60, 50)
                    is_hover = btn_rect.collidepoint(mouse_pos)

                    btn_color = WHITE if is_hover else GOLD
                    pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=5)
                    pygame.draw.rect(self.screen, GOLD if is_hover else WHITE, btn_rect, 2, border_radius=5)

                    bid_text = self.font_large.render(str(bid), True, BLACK)
                    self.screen.blit(bid_text, (btn_rect.centerx - bid_text.get_width()//2,
                                               btn_rect.centery - bid_text.get_height()//2))

    def draw_player_info(self, player):
        positions = {
            0: (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 180),
            1: (80, SCREEN_HEIGHT // 2),
            2: (SCREEN_WIDTH // 2, 150),
            3: (SCREEN_WIDTH - 80, SCREEN_HEIGHT // 2)
        }

        x, y = positions[player.position]

        info_rect = pygame.Rect(x - 70, y - 25, 140, 70)
        is_current = self.current_player_idx == player.position

        if is_current:
            glow_surf = pygame.Surface((160, 90), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*GOLD, 100), glow_surf.get_rect(), border_radius=10)
            self.screen.blit(glow_surf, (info_rect.x - 10, info_rect.y - 10))

        color = GOLD if is_current else DARK_GREEN
        pygame.draw.rect(self.screen, color, info_rect, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, info_rect, 2, border_radius=5)

        name_surf = self.font_small.render(player.name, True, WHITE)
        bid_text = f"Bid: {player.bid if player.bid else '?'}"
        bid_surf = self.font_small.render(bid_text, True, WHITE)
        tricks_surf = self.font_small.render(f"Won: {player.tricks_won}", True, WHITE)

        self.screen.blit(name_surf, (x - name_surf.get_width()//2, y - 15))
        self.screen.blit(bid_surf, (x - bid_surf.get_width()//2, y + 5))
        self.screen.blit(tricks_surf, (x - tricks_surf.get_width()//2, y + 25))

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
