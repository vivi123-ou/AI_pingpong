import pygame
import sys
from menu import Menu
from pingpongMatch import MatchGame
from pingpongAI import Game as TrainingGame


def main():
    """Chương trình chính - Menu game Ping Pong AI"""
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("Ping Pong AI Championship")

    menu = Menu(screen)

    # Load trained AI (nếu có)
    try:
        with open('best_ai.pkl', 'rb') as f:
            trained_brain = f.read()
        print("✓ Loaded trained AI successfully!")
    except:
        trained_brain = None
        print("✗ No trained AI found. Please train first!")

    while True:
        choice = menu.show_main_menu()

        if choice == "QUIT":
            pygame.quit()
            sys.exit()

        elif choice == "TRAIN":
            # Chạy training mode (genetic algorithm)
            print("\n=== STARTING TRAINING MODE ===")
            print("Tips:")
            print("- Press S to see best AI demo")
            print("- Press ESC to quit training")
            print("- AI will be saved automatically")
            print("================================\n")

            training = TrainingGame()  # Sẽ tự động lưu best AI

            # Reload brain sau khi training
            try:
                with open('best_ai.pkl', 'rb') as f:
                    trained_brain = f.read()
                print("✓ Reloaded updated AI")
            except:
                pass

        elif choice == "MATCH":
            # Kiểm tra xem đã có AI trained chưa
            if trained_brain is None:
                print("⚠ No trained AI! Please train first.")
                # Hiển thị cảnh báo
                screen.fill((20, 30, 50))
                font = pygame.font.SysFont('arial', 30)
                warning = font.render("Please TRAIN AI first!", True, (255, 100, 100))
                screen.blit(warning, (250, 280))
                pygame.display.flip()
                pygame.time.wait(2000)
                continue

            # Chơi BEST OF 3 (3 ván)
            print("\n=== STARTING MATCH MODE (Best of 3) ===")
            final_scores = {'AI_1': 0, 'AI_2': 0}

            for round_num in range(1, 4):  # Tối đa 3 ván
                # Thông báo ván đấu
                screen.fill((20, 30, 50))
                font_large = pygame.font.SysFont('arial', 50, bold=True)
                font_small = pygame.font.SysFont('arial', 25)

                round_text = font_large.render(f"VÁN {round_num}/3", True, (255, 255, 255))
                score_text = font_small.render(
                    f"Tỉ số: {final_scores['AI_1']} - {final_scores['AI_2']}",
                    True, (200, 200, 200)
                )

                screen.blit(round_text, (350, 250))
                screen.blit(score_text, (360, 320))
                pygame.display.flip()
                pygame.time.wait(1500)

                # Chơi một ván (5 điểm để thắng)
                print(f"\n--- Round {round_num} ---")
                match = MatchGame(screen, trained_brain, trained_brain)
                result, winner = match.play_match()

                if result == "QUIT":
                    pygame.quit()
                    sys.exit()
                elif result == "MENU":
                    break  # Quay về menu

                # Cập nhật điểm
                if winner:
                    final_scores[winner] += 1
                    print(f"Winner: {winner}")
                    print(f"Current score: AI_1 {final_scores['AI_1']} - {final_scores['AI_2']} AI_2")
                    menu.show_match_result(winner, final_scores)

                # Kiểm tra xem đã có người thắng 2 ván chưa (best of 3)
                if final_scores['AI_1'] == 2:
                    print("\n🏆 AI XANH (Green) WINS THE MATCH! 🏆")
                    break
                elif final_scores['AI_2'] == 2:
                    print("\n🏆 AI ĐỎ (Red) WINS THE MATCH! 🏆")
                    break

            # Hiển thị kết quả cuối cùng
            if result != "MENU":
                action = menu.show_final_result(final_scores)
                if action == "QUIT":
                    pygame.quit()
                    sys.exit()


if __name__ == '__main__':
    main()