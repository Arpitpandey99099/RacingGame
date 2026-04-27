import pygame
import cv2
import mediapipe as mp
import random
import sys

# ==========================================
# 1. SETUP
# ==========================================
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gesture Pro: Debug Mode")
clock = pygame.time.Clock()

# MediaPipe Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=1)

# Camera Setup (Try index 0, if not works try 1)
cap = cv2.VideoCapture(0)

def count_fingers(hand_landmarks):
    tip_ids = [8, 12, 16, 20]
    fingers_up = 0
    for tip in tip_ids:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            fingers_up += 1
    return fingers_up

# ==========================================
# 2. CLASSES
# ==========================================
class Player:
    def __init__(self):
        self.width, self.height = 50, 80
        self.x = WIDTH // 2
        self.y = HEIGHT - 120
        self.target_x = self.x

    def move(self, tx):
        self.target_x = max(20, min(tx - self.width//2, WIDTH - self.width - 20))
        self.x += (self.target_x - self.x) * 0.15

    def draw(self, surf, is_boosting):
        color = (255, 215, 0) if is_boosting else (0, 200, 255)
        pygame.draw.rect(surf, color, (self.x, self.y, self.width, self.height), border_radius=8)

class Obstacle:
    def __init__(self, speed):
        self.w, self.h = 50, 80
        self.x = random.randint(50, WIDTH - 100)
        self.y = -100
        self.speed = speed
    def update(self): self.y += self.speed
    def draw(self, surf): pygame.draw.rect(surf, (255, 50, 50), (self.x, self.y, self.w, self.h), border_radius=8)

# ==========================================
# 3. MAIN ENGINE
# ==========================================
def main():
    player = Player()
    enemies = []
    score = 0
    game_speed = 7
    is_boosting = False
    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        if not game_over:
            # --- CAMERA & GESTURE ---
            success, frame = cap.read()
            if not success or frame is None:
                # Agar camera nahi chal raha, toh background black rakho aur skip karo
                screen.fill((0,0,0))
                error_msg = pygame.font.SysFont("Arial", 24).render("CAMERA NOT FOUND!", True, (255,0,0))
                screen.blit(error_msg, (WIDTH//2 - 100, HEIGHT//2))
            else:
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)
                
                if results.multi_hand_landmarks:
                    hand = results.multi_hand_landmarks[0]
                    player.move(int(hand.landmark[8].x * WIDTH))
                    f_count = count_fingers(hand)
                    
                    if f_count >= 3:
                        game_speed, is_boosting = 15, True
                    elif f_count == 0:
                        game_speed, is_boosting = 3, False
                    else:
                        game_speed, is_boosting = 7, False
                
                cv2.imshow("Debug View", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'): break

            # --- GAME LOGIC ---
            if random.random() < 0.02: # Spawn enemy
                enemies.append(Obstacle(game_speed + 2))
            
            p_rect = pygame.Rect(player.x, player.y, player.width, player.height)
            for e in enemies[:]:
                e.update()
                if e.y > HEIGHT: 
                    enemies.remove(e)
                    score += 1
                if p_rect.colliderect(pygame.Rect(e.x, e.y, e.w, e.h)):
                    game_over = True

        # --- DRAWING ---
        screen.fill((40, 40, 40))
        player.draw(screen, is_boosting)
        for e in enemies: e.draw(screen)
        
        status_text = pygame.font.SysFont("Arial", 24).render(f"Score: {score} | Speed: {game_speed}", True, (255,255,255))
        screen.blit(status_text, (10, 10))
        
        if game_over:
            over_msg = pygame.font.SysFont("Arial", 48).render("CRASHED! Press R", True, (255,255,255))
            screen.blit(over_msg, (WIDTH//2 - 150, HEIGHT//2))
            if pygame.key.get_pressed()[pygame.K_r]:
                game_over, enemies, score, game_speed = False, [], 0, 7

        pygame.display.flip()
        clock.tick(60)

    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()

if __name__ == "__main__":
    main()