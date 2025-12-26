import pickle
import random
import pygame
import math
import numpy as np
from NeuralNetwork import NeuralNetwork


class Paddle:
    """Thanh paddle cho AI"""

    def __init__(self, x, y, is_top=False):
        self.length = 120
        self.height = 16
        self.x = x
        self.y = y
        self.center_x = self.x + self.length / 2
        self.center_y = self.y + self.height / 2
        self.is_top = is_top
        self.brain = NeuralNetwork(9, 8, 2)  # Tăng input lên 9 để có thêm thông tin
        self.score = 0

    def show(self, screen, color):
        pygame.draw.rect(screen, color, [self.x, self.y, self.length, self.height])

    def predict(self, ball, game_width, game_height):
        """AI dự đoán hướng di chuyển dựa trên vị trí và vận tốc bóng"""
        # Khoảng cách đến bóng (chuẩn hóa)
        dist_x = (ball.x - self.center_x) / game_width
        dist_y = (ball.y - self.center_y) / game_height

        # Vận tốc bóng (chuẩn hóa)
        vel_x = ball.vel_x / 20
        vel_y = ball.vel_y / 20

        # Vị trí của paddle (chuẩn hóa)
        pos_x = self.x / game_width

        # Khoảng cách đến tường trái/phải
        dist_left = self.x / game_width
        dist_right = (game_width - (self.x + self.length)) / game_width

        # Hướng bóng bay (về phía mình hay không)
        ball_coming = 1 if (self.is_top and ball.vel_y < 0) or (not self.is_top and ball.vel_y > 0) else -1

        inputs = np.array([dist_x, dist_y, vel_x, vel_y, pos_x, dist_left, dist_right, ball_coming, 1])
        inputs = np.reshape(inputs, (9, 1))

        output = self.brain.feedforward(inputs)

        # Quyết định di chuyển
        if output[0] > output[1]:
            self.move_right(game_width)
        else:
            self.move_left()

    def move_left(self):
        if self.x > 0:
            self.x -= 10  # Tăng tốc độ di chuyển
            self.center_x = self.x + self.length / 2

    def move_right(self, game_width):
        if self.x < game_width - self.length:
            self.x += 10  # Tăng tốc độ di chuyển
            self.center_x = self.x + self.length / 2


class Ball:
    """Bóng ping pong"""

    def __init__(self, x, y):
        self.radius = 12
        self.x = x
        self.y = y
        self.vel_x = random.choice([-10, 10])  # Tăng tốc độ bóng
        self.vel_y = random.choice([-10, 10])

    def show(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def reset(self, x, y):
        """Reset bóng về giữa sân"""
        self.x = x
        self.y = y
        self.vel_x = random.choice([-10, 10])
        self.vel_y = random.choice([-10, 10])


class MatchGame:
    """Trận đấu giữa 2 AI - giống ping pong thật"""

    def __init__(self, screen, brain1=None, brain2=None):
        self.width = 900
        self.height = 600
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Tạo 2 paddle ĐỐI DIỆN NHAU (trên và dưới)
        self.paddle_top = Paddle((self.width - 120) / 2, 20, is_top=True)  # AI ở trên
        self.paddle_bottom = Paddle((self.width - 120) / 2, self.height - 36, is_top=False)  # AI ở dưới

        # Load trained brain nếu có
        if brain1:
            try:
                self.paddle_top.brain = pickle.loads(brain1)
                print("✓ Loaded brain for AI 1 (Green)")
            except:
                print("✗ Failed to load brain for AI 1, using random")

        if brain2:
            try:
                self.paddle_bottom.brain = pickle.loads(brain2)
                print("✓ Loaded brain for AI 2 (Red)")
            except:
                print("✗ Failed to load brain for AI 2, using random")

        # Bóng bắt đầu ở giữa
        self.ball = Ball(self.width / 2, self.height / 2)

        # Điểm số
        self.score_top = 0  # Điểm của AI trên (xanh)
        self.score_bottom = 0  # Điểm của AI dưới (đỏ)
        self.win_score = 5  # Điểm để thắng một ván

        self.font_large = pygame.font.SysFont('arial', 40, bold=True)
        self.font_small = pygame.font.SysFont('arial', 25)

        # Đếm số lần chạm bóng liên tiếp (để tăng độ khó)
        self.rally_count = 0

    def check_collision(self):
        """Kiểm tra va chạm với paddle và tường"""

        # Va chạm với PADDLE TRÊN (AI xanh)
        if (self.ball.y - self.ball.radius <= self.paddle_top.y + self.paddle_top.height and
                self.ball.vel_y < 0 and  # Bóng đang bay lên
                self.ball.x >= self.paddle_top.x and
                self.ball.x <= self.paddle_top.x + self.paddle_top.length):
            self.ball.vel_y = abs(self.ball.vel_y)  # Đổi hướng xuống
            self.ball.y = self.paddle_top.y + self.paddle_top.height + self.ball.radius
            self.rally_count += 1

            # Thêm hiệu ứng spin dựa trên vị trí chạm
            relative_x = (self.ball.x - self.paddle_top.center_x) / (self.paddle_top.length / 2)
            self.ball.vel_x += relative_x * 2

        # Va chạm với PADDLE DƯỚI (AI đỏ)
        if (self.ball.y + self.ball.radius >= self.paddle_bottom.y and
                self.ball.vel_y > 0 and  # Bóng đang bay xuống
                self.ball.x >= self.paddle_bottom.x and
                self.ball.x <= self.paddle_bottom.x + self.paddle_bottom.length):
            self.ball.vel_y = -abs(self.ball.vel_y)  # Đổi hướng lên
            self.ball.y = self.paddle_bottom.y - self.ball.radius
            self.rally_count += 1

            # Thêm hiệu ứng spin
            relative_x = (self.ball.x - self.paddle_bottom.center_x) / (self.paddle_bottom.length / 2)
            self.ball.vel_x += relative_x * 2

        # Va chạm với TƯỜNG TRÁI/PHẢI
        if self.ball.x - self.ball.radius <= 0:
            self.ball.vel_x = abs(self.ball.vel_x)
            self.ball.x = self.ball.radius
        elif self.ball.x + self.ball.radius >= self.width:
            self.ball.vel_x = -abs(self.ball.vel_x)
            self.ball.x = self.width - self.ball.radius

        # ĐIỂM DỪNG: Bóng ra ngoài phía TRÊN → AI dưới (đỏ) ghi điểm
        if self.ball.y - self.ball.radius <= 0:
            self.score_bottom += 1
            self.rally_count = 0
            self.ball.reset(self.width / 2, self.height / 2)
            pygame.time.wait(500)  # Dừng 0.5 giây

        # ĐIỂM DỪNG: Bóng ra ngoài phía DƯỚI → AI trên (xanh) ghi điểm
        if self.ball.y + self.ball.radius >= self.height:
            self.score_top += 1
            self.rally_count = 0
            self.ball.reset(self.width / 2, self.height / 2)
            pygame.time.wait(500)  # Dừng 0.5 giây

    def draw(self):
        """Vẽ toàn bộ game lên màn hình"""
        # Nền
        self.screen.fill((20, 30, 50))

        # Vẽ đường giữa sân (net)
        for i in range(0, self.width, 20):
            pygame.draw.rect(self.screen, (100, 100, 100),
                             [i, self.height // 2 - 2, 10, 4])

        # Vẽ 2 paddle (trên = xanh, dưới = đỏ)
        self.paddle_top.show(self.screen, (0, 255, 100))  # AI 1 - Xanh
        self.paddle_bottom.show(self.screen, (255, 100, 100))  # AI 2 - Đỏ

        # Vẽ bóng
        self.ball.show(self.screen)

        # Vẽ điểm số TO và RÕ RÀNG
        score_text = self.font_large.render(
            f"{self.score_top}  :  {self.score_bottom}",
            True, (255, 255, 255)
        )
        score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2))

        # Vẽ nền cho điểm số để dễ nhìn
        pygame.draw.rect(self.screen, (0, 0, 0, 128),
                         [score_rect.x - 10, score_rect.y - 5,
                          score_rect.width + 20, score_rect.height + 10])
        self.screen.blit(score_text, score_rect)

        # Hiển thị thông tin rally
        if self.rally_count > 3:
            rally_text = self.font_small.render(
                f"Rally: {self.rally_count}!",
                True, (255, 255, 0)
            )
            self.screen.blit(rally_text, (self.width // 2 - 60, self.height // 2 + 50))

        # Hiển thị tên AI
        name_top = self.font_small.render("AI XANH", True, (0, 255, 100))
        name_bottom = self.font_small.render("AI ĐỎ", True, (255, 100, 100))
        self.screen.blit(name_top, (10, 10))
        self.screen.blit(name_bottom, (10, self.height - 35))

    def play_match(self):
        """Chơi MỘT VÁN đấu cho đến khi có người thắng"""
        game_exit = False

        while not game_exit:
            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT", None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "MENU", None

            # AI TỰ ĐỘNG di chuyển (không cần người chơi)
            self.paddle_top.predict(self.ball, self.width, self.height)
            self.paddle_bottom.predict(self.ball, self.width, self.height)

            # Cập nhật vị trí bóng
            self.ball.update()

            # Kiểm tra va chạm và tính điểm
            self.check_collision()

            # Vẽ lên màn hình
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS

            # ĐIỀU KIỆN THẮNG: Đạt đủ điểm
            if self.score_top >= self.win_score:
                pygame.time.wait(1000)  # Dừng 1 giây để người xem thấy
                return "WIN", "AI_1"  # AI xanh (trên) thắng

            if self.score_bottom >= self.win_score:
                pygame.time.wait(1000)
                return "WIN", "AI_2"  # AI đỏ (dưới) thắng

        return "QUIT", None