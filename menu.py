import pygame
import sys


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.width = 900
        self.height = 600
        self.font_large = pygame.font.SysFont('arial', 60, bold=True)
        self.font_medium = pygame.font.SysFont('arial', 40)
        self.font_small = pygame.font.SysFont('arial', 25)

    def draw_text(self, text, font, color, x, y, center=True):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)
        return text_rect

    def show_main_menu(self):
        """Menu chính"""
        clock = pygame.time.Clock()

        while True:
            self.screen.fill((20, 30, 50))

            # Title
            self.draw_text("PING PONG AI", self.font_large, (255, 255, 255),
                           self.width // 2, 100)

            # Buttons
            start_rect = pygame.Rect(300, 250, 300, 60)
            train_rect = pygame.Rect(300, 330, 300, 60)
            quit_rect = pygame.Rect(300, 410, 300, 60)

            mouse_pos = pygame.mouse.get_pos()

            # Draw buttons with hover effect
            for rect, text in [(start_rect, "BẮT ĐẦU TRẬN ĐẤU"),
                               (train_rect, "TRAINING AI"),
                               (quit_rect, "THOÁT")]:
                color = (100, 150, 255) if rect.collidepoint(mouse_pos) else (70, 100, 200)
                pygame.draw.rect(self.screen, color, rect, border_radius=10)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 3, border_radius=10)
                self.draw_text(text, self.font_small, (255, 255, 255),
                               rect.centerx, rect.centery)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if start_rect.collidepoint(mouse_pos):
                        return "MATCH"
                    if train_rect.collidepoint(mouse_pos):
                        return "TRAIN"
                    if quit_rect.collidepoint(mouse_pos):
                        return "QUIT"

            pygame.display.flip()
            clock.tick(60)

    def show_match_result(self, winner, scores):
        """Hiển thị kết quả từng ván"""
        clock = pygame.time.Clock()
        wait_time = 0

        while wait_time < 120:  # Hiện 2 giây
            self.screen.fill((20, 30, 50))

            if winner == "AI_1":
                text = "AI XANH THẮNG VÁN NÀY!"
                color = (0, 255, 100)
            else:
                text = "AI ĐỎ THẮNG VÁN NÀY!"
                color = (255, 100, 100)

            self.draw_text(text, self.font_large, color, self.width // 2, 200)
            self.draw_text(f"Tỉ số: {scores['AI_1']} - {scores['AI_2']}",
                           self.font_medium, (255, 255, 255), self.width // 2, 300)

            pygame.display.flip()
            clock.tick(60)
            wait_time += 1

    def show_final_result(self, final_scores):
        """Hiển thị kết quả cuối cùng"""
        clock = pygame.time.Clock()

        while True:
            self.screen.fill((20, 30, 50))

            if final_scores['AI_1'] > final_scores['AI_2']:
                winner_text = "AI XANH CHIẾN THẮNG!"
                color = (0, 255, 100)
            elif final_scores['AI_2'] > final_scores['AI_1']:
                winner_text = "AI ĐỎ CHIẾN THẮNG!"
                color = (255, 100, 100)
            else:
                winner_text = "HÒA!"
                color = (255, 255, 0)

            self.draw_text(winner_text, self.font_large, color, self.width // 2, 150)
            self.draw_text(f"Tỉ số chung cuộc: {final_scores['AI_1']} - {final_scores['AI_2']}",
                           self.font_medium, (255, 255, 255), self.width // 2, 250)

            # Buttons
            menu_rect = pygame.Rect(250, 400, 180, 50)
            quit_rect = pygame.Rect(470, 400, 180, 50)

            mouse_pos = pygame.mouse.get_pos()

            for rect, text in [(menu_rect, "MENU"), (quit_rect, "THOÁT")]:
                color_btn = (100, 150, 255) if rect.collidepoint(mouse_pos) else (70, 100, 200)
                pygame.draw.rect(self.screen, color_btn, rect, border_radius=10)
                pygame.draw.rect(self.screen, (255, 255, 255), rect, 3, border_radius=10)
                self.draw_text(text, self.font_small, (255, 255, 255),
                               rect.centerx, rect.centery)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if menu_rect.collidepoint(mouse_pos):
                        return "MENU"
                    if quit_rect.collidepoint(mouse_pos):
                        return "QUIT"

            pygame.display.flip()
            clock.tick(60)