import pickle
import random
import pygame
import math
from NeuralNetwork import NeuralNetwork
import numpy as np


class Bar:
    """Thanh paddle cho training mode"""

    def __init__(self):
        self.length = 120
        self.height = 16
        self.bar_x = (Game.width - self.length) / 2
        self.bar_y = Game.height - self.height
        self.center_x = (Game.width / 2)
        self.center_y = Game.height - (self.height / 2)
        self.radius = 15
        self.ball_x = self.center_x
        self.ball_y = self.bar_x + (self.length) / 2 - (2 * self.radius)

        # Khởi tạo bóng ngẫu nhiên
        self.ball_center_x = random.randrange(15, Game.width - 15)
        self.ball_center_y = random.randrange(50, Game.height // 2)
        self.ball_vel_x = random.choice([-10, 10])
        self.ball_vel_y = 10

        self.bar_vel = 0
        self.score = 0
        self.fitness = 0
        self.distance = 0
        self.brain = NeuralNetwork(9, 8, 2)

    def showBar(self, x, y):
        pygame.draw.rect(Game.gameDisplay, Game.black, [x, y, self.length, self.height])

    def showBall(self, x, y):
        pygame.draw.circle(Game.gameDisplay, Game.gray, (int(x), int(y)), self.radius)

    def predict(self):
        """AI dự đoán hướng di chuyển"""
        # Khoảng cách đến bóng theo các góc phần tư
        if self.ball_center_x > self.center_x:
            dis1 = self.calculateDistance(self.ball_center_x, self.ball_center_y + self.radius)
        else:
            dis1 = -1
        dis1 /= 1000

        if self.ball_center_x < self.center_x:
            dis2 = self.calculateDistance(self.ball_center_x, self.ball_center_y + self.radius)
        else:
            dis2 = -1
        dis2 /= 1000

        if self.ball_center_x == self.center_x:
            dis3 = self.calculateDistance(self.ball_center_x, self.ball_center_y + self.radius)
        else:
            dis3 = -1
        dis3 /= 1000

        # Vận tốc bóng
        vel_x = self.ball_vel_x / 1000
        vel_y = self.ball_vel_y / 1000

        # Khoảng cách đến tường
        dis_wall1 = self.bar_x / Game.width
        dis_wall2 = (Game.width - self.bar_x) / Game.width

        # Khoảng cách đến bóng từ 2 đầu paddle
        dis_ball1 = math.sqrt((self.ball_center_x - self.bar_x) ** 2 +
                              (self.ball_center_y + self.radius - (Game.height - self.height)) ** 2)
        dis_ball2 = math.sqrt((self.ball_center_x - (self.bar_x + self.length)) ** 2 +
                              (self.ball_center_y + self.radius - (Game.height - self.height)) ** 2)
        dis_ball1 /= 1000
        dis_ball2 /= 1000

        # Tạo input vector
        inputs = np.array([dis1, dis2, dis3, dis_wall1, dis_wall2, dis_ball1, dis_ball2, vel_x, vel_y])
        inputs = np.reshape(inputs, (9, 1))

        output = self.brain.feedforward(inputs)

        if output[0] > output[1]:
            self.moveRight()
        else:
            self.moveLeft()

    def moveLeft(self):
        if self.bar_x > 0:
            self.bar_x -= 10
            self.center_x -= 10
            self.distance += 1

    def moveRight(self):
        if self.bar_x < (Game.width - self.length):
            self.bar_x += 10
            self.center_x += 10
            self.distance += 1

    def updateVelocity(self):
        self.ball_center_x += self.ball_vel_x
        self.ball_center_y += self.ball_vel_y

    def isColliding(self):
        """Kiểm tra va chạm với paddle"""
        if (self.ball_center_y + self.radius) >= (Game.height - self.height):
            if self.ball_center_x >= self.bar_x and self.ball_center_x <= (self.bar_x + self.length):
                return True
        return False

    def isCollidingSide(self):
        """Kiểm tra va chạm với tường 2 bên"""
        if self.ball_center_x >= Game.width or self.ball_center_x - self.radius <= 0:
            return True
        return False

    def isCollidingAbove(self):
        """Kiểm tra va chạm với tường trên"""
        if self.ball_center_y <= 0:
            return True
        return False

    def calculateDistance(self, x, y):
        return math.sqrt((self.center_x - x) ** 2 + (self.center_y - y) ** 2)


class Game():
    """Game training với genetic algorithm"""
    width = 900
    height = 600
    black = (0, 0, 0)
    gray = (70, 70, 70)
    gameDisplay = pygame.display.set_mode((width, height))

    population = 100  # Số lượng AI trong mỗi thế hệ
    generation = 1
    bars = []
    savedBars = []
    highscore = []  # Lưu điểm cao nhất mỗi thế hệ
    score = []
    bestBar = None  # Lưu brain tốt nhất
    all_time_best_score = 0  # ĐIỂM CAO NHẤT MỌI THỜI ĐẠI

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Ping Pong AI - Training Mode")
        self.clock = pygame.time.Clock()

        # Load best AI nếu đã có
        try:
            with open('best_ai.pkl', 'rb') as f:
                self.bestBar = f.read()
                print("✓ Loaded previous best AI")
        except:
            print("○ No previous best AI found, starting fresh")

        self.gameLoop()

    def gameLoop(self):
        """Vòng lặp chính của training"""
        gameExit = False
        font_large = pygame.font.SysFont('arial', 30, bold=True)
        font_small = pygame.font.SysFont('arial', 20)

        # Khởi tạo population ban đầu
        for i in range(Game.population):
            self.bars.append(Bar())

        while not gameExit:
            # Xóa màn hình
            self.gameDisplay.fill((135, 206, 250))

            # Hiển thị thông tin thế hệ
            gen_text = font_large.render(f'Generation: {self.generation}', True, (0, 0, 0))
            self.gameDisplay.blit(gen_text, [10, 10])

            # Hiển thị số AI còn sống
            alive_text = font_small.render(f'Alive: {len(self.bars)}/{Game.population}', True, (0, 0, 0))
            self.gameDisplay.blit(alive_text, [10, 45])

            # Hiển thị best score hiện tại
            if len(self.highscore) > 0:
                current_best = max(self.highscore)
                best_text = font_small.render(f'Gen Best: {current_best}', True, (0, 100, 0))
                self.gameDisplay.blit(best_text, [10, 70])

            # HIỂN thị BEST SCORE MỌI THỜI ĐẠI
            alltime_text = font_small.render(
                f'All-Time Best: {self.all_time_best_score}',
                True, (255, 0, 0)
            )
            self.gameDisplay.blit(alltime_text, [10, 95])

            # Hướng dẫn
            help_text = font_small.render('Press S: Show best AI | ESC: Quit', True, (50, 50, 50))
            self.gameDisplay.blit(help_text, [10, Game.height - 30])

            # Cập nhật từng AI
            for bar in self.bars[:]:  # Copy list để có thể remove
                bar.predict()
                bar.updateVelocity()

                # Xử lý va chạm
                if bar.isColliding():
                    bar.ball_vel_y = -bar.ball_vel_y
                    bar.score += 10  # Cộng điểm khi đỡ được bóng

                # Phạt khi đâm vào tường
                if bar.bar_x == 0 or bar.bar_x == Game.width - bar.length:
                    bar.score -= 1

                # Cập nhật best score mọi thời đại
                if bar.score > self.all_time_best_score:
                    self.all_time_best_score = bar.score
                    self.bestBar = bar.brain.serialize()
                    # LƯU NGAY KHI CÓ BEST SCORE MỚI
                    with open('best_ai.pkl', 'wb') as f:
                        f.write(self.bestBar)
                    print(f"★ NEW RECORD: {self.all_time_best_score} (Gen {self.generation})")

                if bar.isCollidingSide():
                    bar.ball_vel_x = -bar.ball_vel_x

                if bar.isCollidingAbove():
                    bar.ball_vel_y = -bar.ball_vel_y

                # AI chết khi bóng rơi xuống đất
                if bar.ball_center_y > Game.height:
                    self.savedBars.append(bar)
                    self.score.append(bar.score)
                    self.bars.remove(bar)

                    # Khi tất cả AI đã chết → Chuyển sang thế hệ mới
                    if len(self.bars) == 0:
                        self.generation += 1
                        current_gen_best = max(self.score)
                        self.highscore.append(current_gen_best)

                        print(f"Gen {self.generation - 1}: Best = {current_gen_best}, "
                              f"Avg = {sum(self.score) // len(self.score)}")

                        self.score = []

                        # Tạo thế hệ mới bằng genetic algorithm
                        ga = GA(self)
                        ga.nextGen()

                # Vẽ paddle và bóng
                bar.showBar(bar.bar_x, bar.bar_y)
                bar.showBall(bar.ball_center_x, bar.ball_center_y)

            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameExit = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        if self.bestBar:
                            self.showBest()
                    if event.key == pygame.K_ESCAPE:
                        gameExit = True

            pygame.display.update()
            self.clock.tick(60)

        # Lưu best AI trước khi thoát
        if self.bestBar:
            with open('best_ai.pkl', 'wb') as f:
                f.write(self.bestBar)
            print(f"✓ Saved best AI (score: {self.all_time_best_score})")

        pygame.quit()

    def showBest(self):
        """Demo AI tốt nhất"""
        if not self.bestBar:
            print("No best AI to show yet!")
            return

        self.gameDisplay.fill((135, 206, 250))
        bar = Bar()
        bar.brain = pickle.loads(self.bestBar)

        font = pygame.font.SysFont('arial', 25)
        score_display = 0

        demo_running = True
        while demo_running:
            self.gameDisplay.fill((135, 206, 250))

            # Hiển thị tiêu đề
            title_text = font.render('BEST AI DEMO - Press ESC to return', True, (255, 0, 0))
            self.gameDisplay.blit(title_text, [Game.width // 2 - 200, 10])

            # Hiển thị điểm
            score_text = font.render(f'Score: {score_display}', True, (0, 0, 0))
            self.gameDisplay.blit(score_text, [10, 50])

            bar.predict()
            bar.updateVelocity()

            if bar.isColliding():
                bar.ball_vel_y = -bar.ball_vel_y
                score_display += 1

            if bar.isCollidingSide():
                bar.ball_vel_x = -bar.ball_vel_x

            if bar.isCollidingAbove():
                bar.ball_vel_y = -bar.ball_vel_y

            # Kết thúc demo nếu bóng rơi
            if bar.ball_center_y > Game.height:
                return

            bar.showBar(bar.bar_x, bar.bar_y)
            bar.showBall(bar.ball_center_x, bar.ball_center_y)

            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return

            pygame.display.update()
            self.clock.tick(60)


class GA(Game):
    """Genetic Algorithm để tạo thế hệ mới"""

    def __init__(self, game):
        self.game = game

    def nextGen(self):
        """Tạo thế hệ mới từ các AI tốt nhất"""
        self.calculateFitness()

        # Tạo 100 AI mới từ các AI tốt nhất
        for i in range(len(self.savedBars)):
            self.game.bars.append(self.pickOne())

        self.game.savedBars = []
        self.savedBars = []

    def calculateFitness(self):
        """Tính fitness cho mỗi AI"""
        sum_fitness = 0
        self.savedBars = self.game.savedBars

        for i in range(len(self.savedBars)):
            # Fitness = (điểm)^2 + khoảng cách di chuyển
            self.savedBars[i].fitness = (self.savedBars[i].score) ** 2 + pow(1.5, self.savedBars[i].distance)
            sum_fitness += self.savedBars[i].fitness

        # Normalize fitness
        if sum_fitness > 0:
            for i in range(len(self.savedBars)):
                self.savedBars[i].fitness /= sum_fitness

    def pickOne(self):
        """Chọn 2 AI cha mẹ và tạo AI con"""
        # Chọn cha
        r = random.uniform(0, 1)
        index = 0
        while r > 0 and index < len(self.savedBars) - 1:
            r = r - self.savedBars[index].fitness
            index += 1
        index = max(0, index - 1)

        # Chọn mẹ
        r2 = random.uniform(0, 1)
        index2 = 0
        while r2 > 0 and index2 < len(self.savedBars) - 1:
            r2 = r2 - self.savedBars[index2].fitness
            index2 += 1
        index2 = max(0, index2 - 1)

        # Tạo con bằng crossover
        child = Bar()
        bar = self.savedBars[index]
        bar2 = self.savedBars[index2]

        child.brain.in_hidden1_weights = bar.brain.crossover(
            bar.brain.in_hidden1_weights,
            bar2.brain.in_hidden1_weights
        )
        child.brain.in_hidden1_biases = bar.brain.crossover(
            bar.brain.in_hidden1_biases,
            bar2.brain.in_hidden1_biases
        )
        child.brain.hidden1_output_weights = bar.brain.crossover(
            bar.brain.hidden1_output_weights,
            bar2.brain.hidden1_output_weights
        )
        child.brain.hidden1_output_biases = bar.brain.crossover(
            bar.brain.hidden1_output_biases,
            bar2.brain.hidden1_output_biases
        )

        # Mutation
        child.brain.mutate(child.brain.in_hidden1_weights, 0.1)
        child.brain.mutate(child.brain.in_hidden1_biases, 0.1)
        child.brain.mutate(child.brain.hidden1_output_weights, 0.1)
        child.brain.mutate(child.brain.hidden1_output_biases, 0.1)

        return child


if __name__ == '__main__':
    game = Game()