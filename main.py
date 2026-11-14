import pygame
import sys

GAME_W=320
GAME_H=240
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
SCORE_PADDING=5
WIN_SCORE=10

class Gong:
    def __init__(self, x, y):
        self.rect=pygame.Rect(x, y, GONG_W, GONG_H)
        self.start_y=y
    def move_up(self):
        self.rect.y-=GONG_SPEED
    def move_down(self):
        self.rect.y+=GONG_SPEED
    def reset(self):
        self.rect.y=self.start_y
    def draw(self, surf):
        pygame.draw.rect(surf, GONG_COLOR, self.rect)

class Mallet:
    def __init__(self, x, y):
        self.mall=pygame.image.load("mallet.png").convert_alpha()
        self.rect=pygame.Rect(x,y,MALLET_SIZE,MALLET_SIZE)
        self.start_x=x
        self.start_y=y
        self.vx=5
        self.vy=5

    def update(self):
        self.rect.x+=self.vx
        self.rect.y+=self.vy

    def bounce_x(self):
        self.vx=-self.vx

    def bounce_y(self):
        self.vy=-self.vy

    def reset(self):
        self.rect.x=self.start_x
        self.rect.y=self.start_y

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

def handle_gong_collision(mallet, gong):
    if not gong.rect.colliderect(mallet.rect):
        return
    mallet.bounce_x()

def which_scorer(mallet):
    if mallet.rect.left <= 0:
        return "cpu"
    elif mallet.rect.right >= GAME_W:
        return "player"
    return None

def main():
    pygame.init()
    surf=pygame.Surface((GAME_W, GAME_H))
    clock=pygame.time.Clock()
    screen=pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("GONG")
    
    font=pygame.font.Font(None,24)
    start_txt=font.render("Press SPACE to start", True, (255,255,255))
    start_txt_w, start_txt_h=start_txt.get_size()

    mallet=Mallet(x=GAME_W//2-MALLET_SIZE//2, y=GAME_H//2)
    player_gong=Gong(x=GONG_W, y=GAME_H//2-GONG_H//2) 
    cpu_gong=Gong(x=GAME_W-GONG_W*2, y=GAME_H//2-GONG_H//2) 
    
    player_score=0
    cpu_score=0
    time_scored=None

    player_won_txt=font.render("Bang. U Won!", True, (255,255,255))
    player_won_txt_w, won_txt_h=player_won_txt.get_size()
    cpu_won_txt=font.render("Bang. CPU Won!", True, (255,255,255))
    cpu_won_txt_w=cpu_won_txt.get_width()
    replay_txt=font.render("Press R to replay", True, (255,255,255))
    replay_txt_w, replay_txt_h=replay_txt.get_size()
    
    winner=None
    state="start"
    running=True

    while running:
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                running=False
                break
            if e.type==pygame.KEYDOWN:
                if state=="start" and e.key==pygame.K_SPACE:
                    state="play"
                if state=="won" and e.key==pygame.K_r:
                    mallet.reset()
                    player_gong.reset()
                    cpu_gong.reset()
                    cpu_score=0
                    player_score=0
                    state="play"

        if state=="play":
            keys=pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                player_gong.move_up()
                clamp_gong(player_gong)
            elif keys[pygame.K_DOWN]:
                player_gong.move_down()
                clamp_gong(player_gong)

            mallet.update()
            handle_wall_collision(mallet)

            scorer=which_scorer(mallet)
            if scorer:
                if scorer=="player":
                    player_score+=1
                elif scorer=="cpu":
                    cpu_score+=1
                
                if player_score>=WIN_SCORE:
                    winner="player"
                    state="won"
                elif cpu_score>=WIN_SCORE:
                    winner="cpu"
                    state="won"
                else:
                    state="scored"
                    time_scored=pygame.time.get_ticks()
            else:
                handle_gong_collision(mallet, player_gong)
                handle_gong_collision(mallet, cpu_gong)
                cpu_gong.rect.y=mallet.rect.y
                clamp_gong(cpu_gong)

        if state=="scored":
            if pygame.time.get_ticks() - time_scored >= 500:
                mallet.reset()
                state="play"

        surf.fill(BG)

        if state=="start": 
            surf.blit(start_txt, (GAME_W//2-start_txt_w//2, GAME_H-1.5*start_txt_h))

        mallet.draw(surf)
        player_gong.draw(surf)
        cpu_gong.draw(surf)

        if state=="won":
            if winner=="player":
                surf.blit(player_won_txt, (GAME_W//2-player_won_txt_w//2, GAME_H//2))
            elif winner=="cpu":
                surf.blit(cpu_won_txt, (GAME_W//2-cpu_won_txt_w//2, GAME_H//2))
            surf.blit(replay_txt, (GAME_W//2-replay_txt_w//2, GAME_H//2+won_txt_h))

        player_score_txt=font.render(f"{player_score}", True, (255,255,255))
        cpu_score_txt=font.render(f"{cpu_score}", True, (255,255,255))
        surf.blit(player_score_txt, (GAME_W//2-player_score_txt.get_width()-SCORE_PADDING, 0))
        surf.blit(cpu_score_txt, (GAME_W//2+SCORE_PADDING, 0))
        
        pygame.transform.scale(surf, (SCREEN_W,SCREEN_H), screen)

        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()

main()
