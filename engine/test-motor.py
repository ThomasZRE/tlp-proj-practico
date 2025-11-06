import pygame

pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
running = True

while running: 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    
    # Puts work on screen
    pygame.display.flip()

    # Limit to 60fps
    clock.tick(60)

pygame.quit()
