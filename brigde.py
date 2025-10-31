import pygame
import sys

# --- Setup ---
pygame.init()

# Load your image
image = pygame.image.load(r"images\Crossroad.png")

# Get image size for window
image_width, image_height = image.get_size()
screen = pygame.display.set_mode((image_width, image_height))
pygame.display.set_caption("Bridge Cover Example")

# Define the river color (same as the blue area)
RIVER_BLUE = (0, 162, 230)  # Adjust if slightly different in your image

# Define rectangle (position + size)
# You can tweak these numbers to match the bridge area visually
bridge_cover_rect = pygame.Rect(image_width - 345, image_height // 2 - 180, 250, 340)

# --- Main loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw background image
    screen.blit(image, (0, 0))

    # Draw the blue rectangle (bridge cover)
    pygame.draw.rect(screen, RIVER_BLUE, bridge_cover_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()