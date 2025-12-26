"""
PING PONG AI - MATCH MODE
2 AI doi dien nhau, 1 bong duy nhat
AI co the dof hut de game co diem dung
Choi Best of 3
"""
import pygame
import random
import math
import numpy as np
import pickle
from NeuralNetwork import NeuralNetwork

# Mau sac
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 100)
RED = (255, 100, 100)
BLUE = (20, 30, 50)
GRAY = (100, 100, 100)


class Paddle:
    """Thanh paddle - 1 o TREN, 1 o DUOI"""
    def __init__(self, x, y, is_top=False):
        self.width = 120
        self.height = 16
        self.x = x
        self.y = y
        self.center_x = self.x + self.width / 2
        self.is_top = is_top
        self.brain = NeuralNetwork(9, 8, 2)

        # DO KHO: Dieu chinh de AI co the dof hut
        self.reaction_delay = 0
        self.max_reaction_delay = random.randint(1, 3)
        self.accuracy = 0.85  # 85% chinh xac
        self.speed_multiplier = random.uniform(0.8, 1.0)
        self.tired_counter = 0

    def draw(self, screen, color):
        """Ve thanh paddle"""
        pygame.draw.rect(screen, color, [self.x, self.y, self.width, self.height])
        pygame.draw.rect(screen, WHITE, [self.x, self.y, self.width, self.height], 2)

    def predict(self, ball, screen_width):
        """AI tu dong di chuyen theo bong - CO THE DOF HUT"""
        # DELAY PHAN UNG
        self.reaction_delay += 1
        if self.reaction_delay < self.max_reaction_delay:
            return
        self.reaction_delay = 0

        paddle_center = self.x + self.width / 2

        # DU DOAN vi tri bong se den
        if self.is_top and ball.vel_y < 0:
            time_to_reach = abs((ball.y - self.y) / ball.vel_y) if ball.vel_y != 0 else 1
            predicted_x = ball.x + ball.vel_x * time_to_reach

            while predicted_x < 0 or predicted_x > screen_width:
                if predicted_x < 0:
                    predicted_x = -predicted_x
                if predicted_x > screen_width:
                    predicted_x = 2 * screen_width - predicted_x

            target_x = predicted_x

        elif not self.is_top and ball.vel_y > 0:
            time_to_reach = abs((ball.y - self.y) / ball.vel_y) if ball.vel_y != 0 else 1
            predicted_x = ball.x + ball.vel_x * time_to_reach

            while predicted_x < 0 or predicted_x > screen_width:
                if predicted_x < 0:
                    predicted_x = -predicted_x
                if predicted_x > screen_width:
                    predicted_x = 2 * screen_width - predicted_x

            target_x = predicted_x

        else:
            target_x = screen_width / 2

        # THEM SAI SO
        error = random.uniform(-50, 50) * (1 - self.accuracy)
        target_x += error

        # HIEU UNG MET MOI
        if self.tired_counter > 10:
            self.speed_multiplier *= 0.95
            self.tired_counter = 0

        # CO HOI DOF HUT NGAU NHIEN: 5%
        if random.random() < 0.05:
            target_x = random.randint(0, screen_width)

        # DI CHUYEN
        diff = target_x - paddle_center

        if abs(diff) > 5:
            if diff < 0:
                self.move_left()
            else:
                self.move_right(screen_width)

    def move_left(self):
        speed = int(12 * self.speed_multiplier)
        if self.x > 0:
            self.x -= speed
            self.center_x = self.x + self.width / 2

    def move_right(self, screen_width):
        speed = int(12 * self.speed_multiplier)
        if self.x < screen_width - self.width:
            self.x += speed
            self.center_x = self.x + self.width / 2

    def on_hit_ball(self):
        """Duoc goi khi dof duoc bong"""
        self.tired_counter += 1
        if random.random() < 0.3:
            self.speed_multiplier = min(1.0, self.speed_multiplier + 0.05)


class Ball:
    """Bong ping pong - CHI CO 1 QUA"""
    def __init__(self, x, y):
        self.radius = 12
        self.x = x
        self.y = y
        self.vel_x = random.choice([-8, 8])
        self.vel_y = random.choice([-8, 8])

    def draw(self, screen):
        """Ve bong"""
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, GRAY, (int(self.x), int(self.y)), self.radius, 2)

    def update(self):
        """Cap nhat vi tri"""
        self.x += self.vel_x
        self.y += self.vel_y

    def reset(self, x, y):
        """Reset ve giua san"""
        self.x = x
        self.y = y
        self.vel_x = random.choice([-8, 8])
        self.vel_y = random.choice([-8, 8])


class MatchGame:
    """Tran dau giua 2 AI"""
    def __init__(self, difficulty="MEDIUM"):
        pygame.init()
        self.width = 900
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Ping Pong AI - Match Mode")
        self.clock = pygame.time.Clock()

        # Fonts - Ho tro tieng Viet
        try:
            self.font_large = pygame.font.SysFont('segoeui,arial,tahoma', 50, bold=True)
            self.font_medium = pygame.font.SysFont('segoeui,arial,tahoma', 35)
            self.font_small = pygame.font.SysFont('segoeui,arial,tahoma', 20)
        except:
            self.font_large = pygame.font.Font(None, 50)
            self.font_medium = pygame.font.Font(None, 35)
            self.font_small = pygame.font.Font(None, 20)

        # Tao 2 PADDLE DOI DIEN
        self.paddle_top = Paddle(390, 30, is_top=True)
        self.paddle_bottom = Paddle(390, 554, is_top=False)

        # DO KHO
        self.set_difficulty(difficulty)

        # Load AI da train (neu co)
        self.load_trained_ai()

        # CHI CO 1 BONG DUY NHAT
        self.ball = Ball(self.width // 2, self.height // 2)

        # Diem so
        self.score_top = 0
        self.score_bottom = 0

        # GIOI HAN DIEM DE THANG
        self.WIN_SCORE = 5
        self.MATCH_WINS = 2

        # So van thang
        self.wins_top = 0
        self.wins_bottom = 0

        # Rally counter
        self.rally_count = 0

    def set_difficulty(self, difficulty):
        """Thiet lap do kho"""
        if difficulty == "EASY":
            self.paddle_top.accuracy = 0.65
            self.paddle_bottom.accuracy = 0.65
            self.paddle_top.max_reaction_delay = random.randint(3, 6)
            self.paddle_bottom.max_reaction_delay = random.randint(3, 6)
        elif difficulty == "HARD":
            self.paddle_top.accuracy = 0.95
            self.paddle_bottom.accuracy = 0.95
            self.paddle_top.max_reaction_delay = random.randint(0, 1)
            self.paddle_bottom.max_reaction_delay = random.randint(0, 1)
        else:  # MEDIUM
            self.paddle_top.accuracy = 0.80
            self.paddle_bottom.accuracy = 0.80
            self.paddle_top.max_reaction_delay = random.randint(1, 3)
            self.paddle_bottom.max_reaction_delay = random.randint(1, 3)

    def load_trained_ai(self):
        """Load AI da train tu file"""
        try:
            with open('best_ai.pkl', 'rb') as f:
                brain_data = f.read()
                self.paddle_top.brain = pickle.loads(brain_data)
                self.paddle_bottom.brain = pickle.loads(brain_data)
            print("Loaded trained AI for both paddles")
        except:
            print("No trained AI found, using simple logic AI")

    def check_collision(self):
        """Kiem tra va cham"""
        # Va cham voi PADDLE TREN
        if (self.ball.y - self.ball.radius <= self.paddle_top.y + self.paddle_top.height and
            self.ball.vel_y < 0 and
            self.ball.x >= self.paddle_top.x and
            self.ball.x <= self.paddle_top.x + self.paddle_top.width):

            self.ball.vel_y = abs(self.ball.vel_y)
            self.ball.y = self.paddle_top.y + self.paddle_top.height + self.ball.radius
            self.rally_count += 1
            self.paddle_top.on_hit_ball()

            relative_x = (self.ball.x - self.paddle_top.center_x) / (self.paddle_top.width / 2)
            self.ball.vel_x += relative_x * 2

            # TANG TOC DO BONG sau moi 5 lan dof
            if self.rally_count % 5 == 0:
                self.ball.vel_x *= 1.1
                self.ball.vel_y *= 1.1

        # Va cham voi PADDLE DUOI
        if (self.ball.y + self.ball.radius >= self.paddle_bottom.y and
            self.ball.vel_y > 0 and
            self.ball.x >= self.paddle_bottom.x and
            self.ball.x <= self.paddle_bottom.x + self.paddle_bottom.width):

            self.ball.vel_y = -abs(self.ball.vel_y)
            self.ball.y = self.paddle_bottom.y - self.ball.radius
            self.rally_count += 1
            self.paddle_bottom.on_hit_ball()

            relative_x = (self.ball.x - self.paddle_bottom.center_x) / (self.paddle_bottom.width / 2)
            self.ball.vel_x += relative_x * 2

            if self.rally_count % 5 == 0:
                self.ball.vel_x *= 1.1
                self.ball.vel_y *= 1.1

        # Va cham voi TUONG
        if self.ball.x - self.ball.radius <= 0:
            self.ball.vel_x = abs(self.ball.vel_x)
            self.ball.x = self.ball.radius
        elif self.ball.x + self.ball.radius >= self.width:
            self.ball.vel_x = -abs(self.ball.vel_x)
            self.ball.x = self.width - self.ball.radius

        # DIEM DUNG: Bong ra ngoai
        scored = False

        if self.ball.y - self.ball.radius <= 0:
            self.score_bottom += 1
            scored = True
            print(f"Goal! AI DO ghi diem. Ti so: {self.score_top} - {self.score_bottom}")

        if self.ball.y + self.ball.radius >= self.height:
            self.score_top += 1
            scored = True
            print(f"Goal! AI XANH ghi diem. Ti so: {self.score_top} - {self.score_bottom}")

        if scored:
            self.rally_count = 0
            self.ball.reset(self.width // 2, self.height // 2)
            self.paddle_top.tired_counter = 0
            self.paddle_bottom.tired_counter = 0
            self.paddle_top.speed_multiplier = random.uniform(0.8, 1.0)
            self.paddle_bottom.speed_multiplier = random.uniform(0.8, 1.0)
            pygame.time.wait(800)

    def draw(self):
        """Ve toan bo game"""
        self.screen.fill(BLUE)

        # Ve duong giua san
        for i in range(0, self.width, 20):
            pygame.draw.rect(self.screen, GRAY, [i, self.height // 2 - 2, 10, 4])

        # Ve 2 PADDLE DOI DIEN
        self.paddle_top.draw(self.screen, GREEN)
        self.paddle_bottom.draw(self.screen, RED)

        # Ve BONG DUY NHAT
        self.ball.draw(self.screen)

        # Ve DIEM SO TO O GIUA
        score_text = self.font_large.render(
            f"{self.score_top}  :  {self.score_bottom}",
            True, WHITE
        )
        score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2))

        bg_rect = pygame.Rect(score_rect.x - 15, score_rect.y - 10,
                             score_rect.width + 30, score_rect.height + 20)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), bg_rect, border_radius=10)
        self.screen.blit(score_text, score_rect)

        # Ve so van thang
        wins_text = self.font_small.render(
            f"Van thang: {self.wins_top} - {self.wins_bottom}",
            True, (200, 200, 200)
        )
        self.screen.blit(wins_text, (self.width // 2 - 80, self.height // 2 + 60))

        # Hien thi rally
        if self.rally_count > 5:
            rally_text = self.font_medium.render(
                f"Rally: {self.rally_count}!",
                True, (255, 255, 0)
            )
            self.screen.blit(rally_text, (self.width // 2 - 100, 50))

        # Hien thi toc do bong
        ball_speed = math.sqrt(self.ball.vel_x**2 + self.ball.vel_y**2)
        speed_text = self.font_small.render(
            f"Toc do bong: {ball_speed:.1f}",
            True, (200, 200, 200)
        )
        self.screen.blit(speed_text, (self.width - 180, self.height - 30))

        # Ve ten AI
        name_top = self.font_small.render("AI XANH", True, GREEN)
        name_bottom = self.font_small.render("AI DO", True, RED)
        self.screen.blit(name_top, (10, 10))
        self.screen.blit(name_bottom, (10, self.height - 30))

        # Huong dan
        help_text = self.font_small.render("ESC: Thoat | SPACE: Pause", True, (150, 150, 150))
        self.screen.blit(help_text, (self.width - 250, 10))

    def show_round_result(self, winner):
        """Hien thi ket qua van dau"""
        self.screen.fill(BLUE)

        if winner == "TOP":
            text = "AI XANH THANG VAN NAY!"
            color = GREEN
            self.wins_top += 1
        else:
            text = "AI DO THANG VAN NAY!"
            color = RED
            self.wins_bottom += 1

        result_text = self.font_large.render(text, True, color)
        result_rect = result_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(result_text, result_rect)

        wins_text = self.font_medium.render(
            f"Ti so van: {self.wins_top} - {self.wins_bottom}",
            True, WHITE
        )
        wins_rect = wins_text.get_rect(center=(self.width // 2, self.height // 2 + 30))
        self.screen.blit(wins_text, wins_rect)

        pygame.display.flip()
        pygame.time.wait(2000)

        self.score_top = 0
        self.score_bottom = 0
        self.ball.reset(self.width // 2, self.height // 2)

    def show_final_result(self):
        """Hien thi ket qua cuoi cung"""
        self.screen.fill(BLUE)

        if self.wins_top > self.wins_bottom:
            winner_text = "AI XANH CHIEN THANG!"
            color = GREEN
        else:
            winner_text = "AI DO CHIEN THANG!"
            color = RED

        text1 = self.font_large.render(winner_text, True, color)
        rect1 = text1.get_rect(center=(self.width // 2, self.height // 2 - 80))
        self.screen.blit(text1, rect1)

        score_text = self.font_medium.render(
            f"Ti so chung cuoc: {self.wins_top} - {self.wins_bottom}",
            True, WHITE
        )
        rect2 = score_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(score_text, rect2)

        help_text = self.font_small.render(
            "Nhan ENTER de choi lai | ESC de thoat",
            True, (200, 200, 200)
        )
        rect3 = help_text.get_rect(center=(self.width // 2, self.height // 2 + 80))
        self.screen.blit(help_text, rect3)

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "RESTART"
                    if event.key == pygame.K_ESCAPE:
                        return "QUIT"

    def play_match(self):
        """Choi tran dau BEST OF 3"""
        running = True
        paused = False

        print("\n" + "="*50)
        print("PING PONG AI MATCH - BEST OF 3")
        print("="*50)
        print(f"Quy tac: {self.WIN_SCORE} diem = thang 1 van")
        print(f"         {self.MATCH_WINS} van = chien thang")
        print("="*50 + "\n")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                        print("Paused" if paused else "Resumed")

            if not paused:
                self.paddle_top.predict(self.ball, self.width)
                self.paddle_bottom.predict(self.ball, self.width)

                self.ball.update()
                self.check_collision()

                if self.score_top >= self.WIN_SCORE:
                    print(f"\nAI XANH thang van! ({self.score_top} - {self.score_bottom})")
                    self.show_round_result("TOP")

                    if self.wins_top >= self.MATCH_WINS:
                        print("\n" + "="*50)
                        print("AI XANH CHIEN THANG TRAN DAU!")
                        print("="*50)
                        action = self.show_final_result()
                        if action == "RESTART":
                            self.wins_top = 0
                            self.wins_bottom = 0
                            self.score_top = 0
                            self.score_bottom = 0
                        else:
                            running = False

                if self.score_bottom >= self.WIN_SCORE:
                    print(f"\nAI DO thang van! ({self.score_top} - {self.score_bottom})")
                    self.show_round_result("BOTTOM")

                    if self.wins_bottom >= self.MATCH_WINS:
                        print("\n" + "="*50)
                        print("AI DO CHIEN THANG TRAN DAU!")
                        print("="*50)
                        action = self.show_final_result()
                        if action == "RESTART":
                            self.wins_top = 0
                            self.wins_bottom = 0
                            self.score_top = 0
                            self.score_bottom = 0
                        else:
                            running = False

            self.draw()

            if paused:
                pause_text = self.font_large.render("PAUSED", True, (255, 255, 0))
                pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2 - 100))
                bg_rect = pygame.Rect(pause_rect.x - 20, pause_rect.y - 10,
                                     pause_rect.width + 40, pause_rect.height + 20)
                pygame.draw.rect(self.screen, (0, 0, 0), bg_rect, border_radius=15)
                self.screen.blit(pause_text, pause_rect)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        print("\nCam on da choi!")


if __name__ == '__main__':
    print("\n" + "="*50)
    print("PING PONG AI CHAMPIONSHIP")
    print("="*50)
    print("Chon do kho:")
    print("1. EASY   - AI de dof hut (tran nhanh)")
    print("2. MEDIUM - Can bang (khuyen nghi)")
    print("3. HARD   - AI kho dof hut (tran lau hon)")
    print("="*50)

    choice = input("Nhap so (1/2/3) hoac Enter cho MEDIUM: ").strip()

    if choice == "1":
        difficulty = "EASY"
    elif choice == "3":
        difficulty = "HARD"
    else:
        difficulty = "MEDIUM"

    print(f"\nDo kho: {difficulty}")
    print("Dang khoi dong game...\n")

    game = MatchGame(difficulty=difficulty)
    game.play_match()