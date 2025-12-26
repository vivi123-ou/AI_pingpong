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
        self.brain = NeuralNetwork(7, 8, 2)
        self.score = 0

    def show(self, screen, color):
        pygame.draw.rect(screen, color, [self.x, self.y, self.length, self.height])

    def predict(self, ball, game_width, game_height):
        """AI dự đoán hướng di chuyển"""
        # Khoảng cách đến bóng
        dist_x = (ball.x - self.center_x) / game_width
        dist_y = (ball.y - self.center_y) / game_height

        # Vận tốc bóng
        vel_x = ball.vel_x / 20
        vel_y = ball.vel_y / 20

        # Vị trí của paddle
        pos_x = self.x / game_width

        # Khoảng cách đến tường
        dist_left = self.x / game_width
        dist_right = (game_width - (self.x + self.length)) / game_width

        inputs = np.array([dist_x, dist_y, vel_x, vel_y, pos_x, dist_left, dist_right])
        inputs = np.reshape(inputs, (7, 1))

        output = self.brain.feedforward(inputs)

        if output[0] > output[1]:
            self.move_right(game_width)
        else:
            self.move_left()

    def move_left(self):
        if self.x > 0:
            self.x -= 8
            self.center_x = self.x + self.length / 2

    def move_right(self, game_width):
        if self.x < game_width - self.length:
            self.x += 8
            self.center_x = self.x + self.length / 2


class Ball:
    """Bóng ping pong"""

    def __init__(self, x, y):
        self.radius = 12
        self.x = x
        self.y = y
        self.vel_x = random.choice([-8, 8])
        self.vel_y = random.choice([-8, 8])

    def show(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = random.choice([-8, 8])
        self.vel_y = random.choice([-8, 8])


class MatchGame:
    """Trận đấu giữa 2 AI"""

    def __init__(self, screen, brain1=None, brain2=None):
        self.width = 900
        self.height = 600
        self.screen = screen
        self.clock = pygame.time.Clock()

        # Tạo 2 paddle
        self.paddle_top = Paddle((self.width - 120) / 2, 20, is_top=True)
        self.paddle_bottom = Paddle((self.width - 120) / 2, self.height - 36, is_top=False)

        # Load brain nếu có
        if brain1:
            self.paddle_top.brain = pickle.loads(brain1)
        if brain2:
            self.paddle_bottom.brain = pickle.loads(brain2)

        # Bóng
        self.ball = Ball(self.width / 2, self.height / 2)

        # Điểm số
        self.score_top = 0
        self.score_bottom = 0
        self.win_score = 5  # Ai đạt 5 điểm trước thắng

        self.font = pygame.font.SysFont('arial', 30)

    def check_collision(self):
        """Kiểm tra va chạm"""
        # Va chạm với paddle trên
        if (self.ball.y - self.ball.radius <= self.paddle_top.y + self.paddle_top.height and
                self.ball.x >= self.paddle_top.x and
                self.ball.x <= self.paddle_top.x + self.paddle_top.length):
            self.ball.vel_y = abs(self.ball.vel_y)
            self.ball.y = self.paddle_top.y + self.paddle_top.height + self.ball.radius

        # Va chạm với paddle dưới
        if (self.ball.y + self.ball.radius >= self.paddle_bottom.y and
                self.ball.x >= self.paddle_bottom.x and
                self.ball.x <= self.paddle_bottom.x + self.paddle_bottom.length):
            self.ball.vel_y = -abs(self.ball.vel_y)
            self.ball.y = self.paddle_bottom.y - self.ball.radius

        # Va chạm với tường trái/phải
        if self.ball.x - self.ball.radius <= 0 or self.ball.x + self.ball.radius >= self.width:
            self.ball.vel_x = -self.ball.vel_x

        # Ghi điểm
        if self.ball.y - self.ball.radius <= 0:
            self.score_bottom += 1
            self.ball.reset(self.width / 2, self.height / 2)

        if self.ball.y + self.ball.radius >= self.height:
            self.score_top += 1
            self.ball.reset(self.width / 2, self.height / 2)

    def draw(self):
        """Vẽ game"""
        self.screen.fill((20, 30, 50))

        # Vẽ đường giữa sân
        pygame.draw.line(self.screen, (100, 100, 100), (0, self.height // 2),
                         (self.width, self.height // 2), 2)

        # Vẽ paddle và bóng
        self.paddle_top.show(self.screen, (0, 255, 100))  # Xanh
        self.paddle_bottom.show(self.screen, (255, 100, 100))  # Đỏ
        self.ball.show(self.screen)

        # Vẽ điểm số
        score_text = self.font.render(f"{self.score_top}  -  {self.score_bottom}",
                                      True, (255, 255, 255))
        self.screen.blit(score_text, (self.width // 2 - 40, self.height // 2 - 50))

    def play_match(self):
        """Chơi một ván"""
        game_exit = False

        while not game_exit:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT", None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "MENU", None

            # AI di chuyển
            self.paddle_top.predict(self.ball, self.width, self.height)
            self.paddle_bottom.predict(self.ball, self.width, self.height)

            # Cập nhật bóng
            self.ball.update()
            self.check_collision()

            # Vẽ
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

            # Kiểm tra thắng thua
            if self.score_top >= self.win_score:
                return "WIN", "AI_1"
            if self.score_bottom >= self.win_score:
                return "WIN", "AI_2"