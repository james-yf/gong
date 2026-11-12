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
        self.rect.y-=GONG_SPEED

    def move_down(self):
        self.rect.y+=GONG_SPEED

    def draw(self, surf):
        pygame.draw.rect(surf, GONG_COLOR, self.rect)

class Mallet:
    def __init__(self, x, y):
        self.mall=pygame.image.load("mallet.png").convert_alpha()
        self.rect=pygame.Rect(x,y,MALLET_SIZE,MALLET_SIZE)
        self.vx=5
        self.vy=5

    def update(self):
        self.rect.x+=self.vx
        self.rect.y+=self.vy

    def bounce_x(self):
        self.vx=-self.vx

    def bounce_y(self):
        self.vy=-self.vy

    def draw(self, surf):
        surf.blit(self.mall, (self.rect.x,self.rect.y))

def clamp_gong(gong):
    if gong.rect.top < 0:
        gong.rect.top=0
    elif gong.rect.bottom > GAME_H:
        gong.rect.bottom=GAME_H

def handle_wall_collision(mallet):
    if mallet.rect.top <= 0 or mallet.rect.bottom >= GAME_H:      
        mallet.bounce_y()

def which_scorer(mallet):
    if mallet.rect.left <= 0:
        return "cpu"
    elif mallet.rect.right >= GAME_W:
        return "player"
    return None
    
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
    cpu_gong=Gong(x=GAME_W-GONG_W*2, y=GAME_H//2-GONG_H//2) 
    player_score=0
    cpu_score=0
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
            handle_wall_collision(mallet)
            scorer=which_scorer(mallet)
            if scorer=="player":
                mallet.bounce_x()
                player_score+=1
            elif scorer=="cpu":
                mallet.bounce_x()
                cpu_score+=1
            clamp_gong(player_gong)
            if player_gong.rect.colliderect(mallet.rect) or cpu_gong.rect.colliderect(mallet.rect):
                mallet.bounce_x()
            cpu_gong.rect.y=mallet.rect.y
            clamp_gong(cpu_gong)
        if not started:
            surf.blit(start_txt, (GAME_W//2-start_txt_w//2, GAME_H-1.5*start_txt_h))
        mallet.draw(surf)
        player_gong.draw(surf)
        cpu_gong.draw(surf)
        player_score_txt=font.render(f"{player_score}", True, (255,255,255))
        cpu_score_txt=font.render(f"{cpu_score}", True, (255,255,255))
        surf.blit(player_score_txt, (GAME_W//2-player_score_txt.get_width(), 0))
        surf.blit(cpu_score_txt, (GAME_W//2+cpu_score_txt.get_width(), 0))
        pygame.transform.scale(surf, (SCREEN_W,SCREEN_H), screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()
main()
