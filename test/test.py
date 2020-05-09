import pygame

pygame.init()
pygame.display.set_mode((640, 480))
while True:
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                print(event)
