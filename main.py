import pygame
import sys
GAME_W=320
GAME_H=320
SCALE_FACTOR=2
SCREEN_W=GAME_W*SCALE_FACTOR
SCREEN_H=GAME_H*SCALE_FACTOR
FPS=60
def main():
    pygame.init()
    surf=pygame.Surface((GAME_W,GAME_H))
    clock=pygame.time.Clock()
    screen=pygame.display.set_mode((SCREEN_W,SCREEN_H))
    pygame.display.set_caption("GONG")
    running=True
    while running:
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                running=False
                break
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()
main()
