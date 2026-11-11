import pygame
import sys
GAME_W=320
GAME_H=320
SCALE_FACTOR=2
SCREEN_W=GAME_W*SCALE_FACTOR
SCREEN_H=GAME_H*SCALE_FACTOR
BG=(255,0,0)
FPS=60
MALLET_SIZE=16
MALLET_SPEED=5
GONG_W=10
GONG_H=50
GONG_SPEED=5
GONG_COLOR=(232,215,149)

class Gong:
    def __init__(self, x, y):
        self.rect=pygame.Rect(x, y, GONG_W, GONG_H)

    def move_up(self):
        dy=-GONG_SPEED
        if not self.move_in_bounds(dy): return
        self.rect.y+=dy

    def move_down(self):
        dy=GONG_SPEED
        if not self.move_in_bounds(dy): return
        self.rect.y+=dy

    def move_in_bounds(self, dy):
        return self.rect.top+dy>=0 and self.rect.bottom+dy<=GAME_H

    def draw(self, surf):
        pygame.draw.rect(surf, GONG_COLOR, self.rect)

class Mallet:
    def __init__(self, x, y):
        self.mall=pygame.image.load("mallet.png").convert_alpha()
        self.rect=pygame.Rect(x,y,MALLET_SIZE,MALLET_SIZE)
        self.vert_dir="up"
        self.horz_dir="left"

    def update(self):
        if   self.rect.x      <= 0      : self.horz_dir="right"
        elif self.rect.right  >= GAME_W : self.horz_dir="left"
        if   self.rect.y      <= 0      : self.vert_dir="down"
        elif self.rect.bottom >= GAME_H : self.vert_dir="up"

        if self.horz_dir=="left" : self.rect.x -= MALLET_SPEED
        else                     : self.rect.x += MALLET_SPEED

        if self.vert_dir=="up"   : self.rect.y -= MALLET_SPEED
        else                     : self.rect.y += MALLET_SPEED

    def draw(self, surf):
        surf.blit(self.mall, (self.rect.x,self.rect.y))

def main():
    pygame.init()
    surf=pygame.Surface((GAME_W,GAME_H))
    clock=pygame.time.Clock()
    screen=pygame.display.set_mode((SCREEN_W,SCREEN_H))
    pygame.display.set_caption("GONG")
    font=pygame.font.Font(None,24)
    start_txt=font.render("Press SPACE to start", True, (255,255,255))
    start_txt_w, start_txt_h=start_txt.get_size()
    mallet=Mallet(x=GAME_W//2-MALLET_SIZE//2, y=GAME_H//2)
    player_gong=Gong(x=GONG_W, y=GAME_H//2-GONG_H//2) 
    cpu_gong=Gong(x=GAME_W-GONG_W, y=GAME_H//2-GONG_H//2) 
    started=False
    running=True
    while running:
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                running=False
                break
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_SPACE:
                    started=True
        if started:
            keys=pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                player_gong.move_up()
            elif keys[pygame.K_DOWN]:
                player_gong.move_down()
        surf.fill(BG)
        if started:
            mallet.update()
            if player_gong.rect.colliderect(mallet.rect):
                mallet.horz_dir="right"
            if cpu_gong.rect.colliderect(mallet.rect):
                mallet.horiz_dir="left"
            cpu_gong.rect.y=mallet.rect.y
        if not started:
            surf.blit(start_txt, (GAME_W//2-start_txt_w//2, GAME_H-1.5*start_txt_h))
        mallet.draw(surf)
        player_gong.draw(surf)
        cpu_gong.draw(surf)
        pygame.transform.scale(surf, (SCREEN_W,SCREEN_H), screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()
main()
