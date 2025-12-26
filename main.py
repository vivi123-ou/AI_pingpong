import pygame
import sys
from menu import Menu
from pingpongMatch import MatchGame
from pingpongAI import Game as TrainingGame


def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("Ping Pong AI Championship")

    menu = Menu(screen)

    # Load trained AI (nếu có)
    try:
        with open('best_ai.pkl', 'rb') as f:
            trained_brain = f.read()
    except:
        trained_brain = None

    while True:
        choice = menu.show_main_menu()

        if choice == "QUIT":
            pygame.quit()
            sys.exit()

        elif choice == "TRAIN":
            # Chạy training mode (code cũ)
            training = TrainingGame()

        elif choice == "MATCH":
            # Chơi 3 ván (best of 3)
            final_scores = {'AI_1': 0, 'AI_2': 0}

            for round_num in range(1, 4):
                # Hiển thị thông tin ván đấu
                screen.fill((20, 30, 50))
                font = pygame.font.SysFont('arial', 40)
                text = font.render(f"VÁN {round_num}/3", True, (255, 255, 255))
                screen.blit(text, (350, 280))
                pygame.display.flip()
                pygame.time.wait(1500)

                # Chơi một ván
                match = MatchGame(screen, trained_brain, trained_brain)
                result, winner = match.play_match()

                if result == "QUIT":
                    pygame.quit()
                    sys.exit()
                elif result == "MENU":
                    break

                # Cập nhật điểm
                if winner:
                    final_scores[winner] += 1
                    menu.show_match_result(winner, final_scores)

                # Nếu đã có người thắng 2 ván, kết thúc
                if final_scores['AI_1'] == 2 or final_scores['AI_2'] == 2:
                    break

            # Hiển thị kết quả cuối
            if result != "MENU":
                action = menu.show_final_result(final_scores)
                if action == "QUIT":
                    pygame.quit()
                    sys.exit()


if __name__ == '__main__':
    main()