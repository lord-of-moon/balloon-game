# Import
import pygame
import numpy as np
import random
import cv2
from cvzone.HandTrackingModule import HandDetector
import time


# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
BALLOON_COLORS = ['/Users/demongod/Documents/baloon/Blue.png']            
FONT_PATH = '/Users/demongod/Documents/baloon/Marcellus-Regular.ttf'
SOUND_POP_PATH = '/Users/demongod/Documents/baloon/pop.mp3'

# Initialize
pygame.init()


# Create Window/Display
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Balloon Pop")

# Initialize Clock for FPS
fps = 30
clock = pygame.time.Clock()

# Webcam
cap = cv2.VideoCapture(0)
cap.set(3, SCREEN_WIDTH)  # width
cap.set(4, SCREEN_HEIGHT)  # height

# Images
balloon_colors = [pygame.image.load(color).convert_alpha() for color in BALLOON_COLORS]
rectBalloon = balloon_colors[0].get_rect()
rectBalloon.x, rectBalloon.y = random.randint(100, SCREEN_WIDTH - 100), SCREEN_HEIGHT + 50

# Variables
speed = 10
score = 0
level = 1
startTime = time.time()
totalTime = 60
pop_sound = pygame.mixer.Sound(SOUND_POP_PATH)

# Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Functions
def reset_balloon():
    rectBalloon.x = random.randint(100, SCREEN_WIDTH - 100)
    rectBalloon.y = SCREEN_HEIGHT + 50

def draw_text(text, size, color, x, y):
    font = pygame.font.Font(FONT_PATH, size)
    text_surface = font.render(text, True, color)
    window.blit(text_surface, (x, y))

# Main loop
while True:
    # Get Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Apply Logic
    time_remaining = int(totalTime - (time.time() - startTime))
    if time_remaining < 0:
        window.fill((255, 255, 255))
        draw_text(f'Your Score: {score}', 50, (50, 50, 255), 450, 350)
        draw_text('Time UP', 50, (50, 50, 255), 530, 275)
    else:
        # OpenCV
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)

        rectBalloon.y -= speed  # Move the balloon up
        # Check if balloon has reached the top without popping
        if rectBalloon.y < 0:
            reset_balloon()
            speed += 1

        if hands:
            hand = hands[0]
            x, y = hand['lmList'][8][0:2]
            if rectBalloon.collidepoint(x, y):
                reset_balloon()
                score += 10
                speed += 1
                pop_sound.play()

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imgRGB = np.rot90(imgRGB)
        frame = pygame.surfarray.make_surface(imgRGB).convert()
        frame = pygame.transform.flip(frame, True, False)
        window.blit(frame, (0, 0))

        # Draw balloon with a random color
        color_index = random.randint(0, len(balloon_colors) - 1)
        window.blit(balloon_colors[color_index], rectBalloon)

        draw_text(f'Score: {score} | Level: {level}', 50, (50, 50, 255), 35, 35)
        draw_text(f'Time: {time_remaining}', 50, (50, 50, 255), 1000, 35)

        # Increase level every 100 points
        if score >= level * 100:
            level += 1
            speed += 2
            totalTime += 10  # Add more time for each new level

    # Update Display
    pygame.display.update()
    # Set FPS
    clock.tick(fps)
