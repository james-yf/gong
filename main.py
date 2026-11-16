import pygame
import sys
from pathlib import Path

GAME_W=320
GAME_H=240
SCALE_FACTOR=2
SCREEN_W=GAME_W*SCALE_FACTOR
SCREEN_H=GAME_H*SCALE_FACTOR
FPS=60
MALLET_SIZE=16
MALLET_SPEED=5
GONG_W=10
GONG_H=50
GONG_SPEED=5
SCORE_PADDING=5
WIN_SCORE=10

ASSETS=Path(__file__).parent / "assets"
IMGS=ASSETS / "imgs"
SOUNDS=ASSETS / "sounds"

THEMES = {
    "red": {
        "bg": (172,50,50),
        "layers": [
            { 
                "img": IMGS / "tree-white.png", 
                "alpha": 120
            },
            {
                "img": IMGS / "luo.png"
            },
            {
                "img": IMGS / "frame-brown.png"
            }
        ],
        "mallet": IMGS / "mallet-white.png",
        "gong": (0,0,0),
        "score": (255,255,0),
        "start": (255,255,0),
        "win": (255,255,0),
        "replay": (255,255,0),
    },
    "white": {
        "bg": (255,255,255),
        "layers": [
            { 
                "img": IMGS / "tree-pink.png", 
                "alpha": 120
            },
            {
                "img": IMGS / "luo.png"
            },
            {
                "img": IMGS / "frame-black-dec.png"
            }
        ],
        "mallet": IMGS / "mallet-red.png",
        "gong": (0,0,0),
        "score": (255,0,0),
        "start": (255,0,0),
        "win": (255,0,0),
        "replay": (255,0,0),
    },
}

def load_layer(layer):
    img=pygame.image.load(layer["img"]).convert_alpha()
    if "alpha" in layer:
        img.set_alpha(layer["alpha"])
    return img

def load_themes():
    themes={}
    for name, theme in THEMES.items():
        themes[name]={
            "bg": theme["bg"],
            "layers": [load_layer(l) for l in theme["layers"]],
            "mallet": pygame.image.load(theme["mallet"]).convert_alpha(),
            "gong": theme["gong"],
            "score": theme["score"],
            "start": theme["start"],
            "win": theme["win"],
            "replay": theme["replay"],
        }
    return themes

class Gong:
    def __init__(self, x, y, color):
        self.rect=pygame.Rect(x, y, GONG_W, GONG_H)
        self.start_y=y
        self.color=color
    def move_up(self):
        self.rect.y-=GONG_SPEED
    def move_down(self):
        self.rect.y+=GONG_SPEED
    def reset(self):
        self.rect.y=self.start_y
    def change_color(self, color):
        self.color=color
    def draw(self, surf):
        pygame.draw.rect(surf, self.color, self.rect)

class Mallet:
    def __init__(self, x, y, img):
        self.img=img
        self.rect=pygame.Rect(x,y,MALLET_SIZE,MALLET_SIZE)
        self.start_x=x
        self.start_y=y
        self.vx=5
        self.vy=5
        self.trail=[]

    def update(self):
        self.trail.append(self.rect.copy())
        if len(self.trail)>=5:
            self.trail.pop(0)
        self.rect.x+=self.vx
        self.rect.y+=self.vy

    def bounce_x(self):
        self.vx=-self.vx

    def bounce_y(self):
        self.vy=-self.vy

    def reset(self):
        self.rect.x=self.start_x
        self.rect.y=self.start_y

    def change_img(self, img):
        self.img=img

    #the mallet asset is drawn at 45(CCW),
    #so rot is relative to that fact.
    def rot_angle(self):
        if self.vx>0 and self.vy>0:
            angle=-180
        elif self.vx>0 and self.vy<0:
            angle=-90
        elif self.vx<0 and self.vy>0:
            angle=90
        elif self.vx<0 and self.vy<0:
            angle=0
        return angle

    #extracted this so I can easily debug without the trail by just
    #commenting the function call.
    def draw_trail(self, surf):
        n=len(self.trail)
        if n:
            step=200//n
            rot=pygame.transform.rotate(self.img, self.rot_angle())
            for i, r in enumerate(self.trail):
                rot.set_alpha(step*i+step)
                surf.blit(rot, (r.x, r.y))

    def draw(self, surf):
        self.draw_trail(surf)
        rot=pygame.transform.rotate(self.img, self.rot_angle())
        surf.blit(rot, (self.rect.x,self.rect.y))

def clamp_gong(gong):
    if gong.rect.top < 0:
        gong.rect.top=0
    elif gong.rect.bottom > GAME_H:
        gong.rect.bottom=GAME_H

def handle_wall_collision(mallet, sfx):
    if mallet.rect.top <= 0 or mallet.rect.bottom >= GAME_H:      
        mallet.bounce_y()
        sfx.play()

def handle_gong_collision(mallet, gong, sfx):
    if not gong.rect.colliderect(mallet.rect):
        return
    mallet.bounce_x()
    sfx.play()

def which_scorer(mallet):
    if mallet.rect.left <= 0:
        return "cpu"
    elif mallet.rect.right >= GAME_W:
        return "player"
    return None

def main():
    pygame.init()

    pygame.mixer.init()
    hit_sfx=pygame.mixer.Sound(SOUNDS / "hit.wav")
    won_sfx=pygame.mixer.Sound(SOUNDS / "gong.wav")

    surf=pygame.Surface((GAME_W, GAME_H))
    clock=pygame.time.Clock()
    screen=pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("GONG")

    themes=load_themes() 
    theme_names=list(themes)
    theme_i=0
    theme=themes[theme_names[theme_i]]
    
    font=pygame.font.Font(None,24)

    mallet=Mallet(x=GAME_W//2-MALLET_SIZE//2, y=GAME_H//2, img=theme["mallet"])
    player_gong=Gong(x=GONG_W, y=GAME_H//2-GONG_H//2, color=theme["gong"]) 
    cpu_gong=Gong(x=GAME_W-GONG_W*2, y=GAME_H//2-GONG_H//2, color=theme["gong"]) 
    
    player_score=0
    cpu_score=0
    time_scored=None

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
                if state in ("start", "won") and e.key==pygame.K_t:
                    theme_i=(theme_i+1) % len(theme_names)
                    theme=themes[theme_names[theme_i]]
                    mallet.change_img(theme["mallet"])
                    player_gong.change_color(theme["gong"])
                    cpu_gong.change_color(theme["gong"])

        if state != "won":
            keys=pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                player_gong.move_up()
                clamp_gong(player_gong)
            elif keys[pygame.K_DOWN]:
                player_gong.move_down()
                clamp_gong(player_gong)

        if state in ("play", "scored"):
            mallet.update()

        if state=="play":
            handle_wall_collision(mallet, hit_sfx)

            scorer=which_scorer(mallet)
            if scorer:
                if scorer=="player":
                    player_score+=1
                elif scorer=="cpu":
                    cpu_score+=1
                
                if player_score>=WIN_SCORE:
                    winner="player"
                    state="won"
                    won_sfx.play()
                elif cpu_score>=WIN_SCORE:
                    winner="cpu"
                    state="won"
                    won_sfx.play()
                else:
                    state="scored"
                    time_scored=pygame.time.get_ticks()
            else:
                handle_gong_collision(mallet, player_gong, hit_sfx)
                handle_gong_collision(mallet, cpu_gong, hit_sfx)
                cpu_gong.rect.y=mallet.rect.y
                clamp_gong(cpu_gong)

        if state=="scored":
            if pygame.time.get_ticks() - time_scored >= 500:
                mallet.reset()
                state="play"

        surf.fill(theme["bg"])
        for l in theme["layers"]:
            surf.blit(l, (0,0))

        if state=="start": 
            start_txt=font.render("Press SPACE to start", True, theme["start"])
            start_txt_w, start_txt_h=start_txt.get_size()
            surf.blit(start_txt, (GAME_W//2-start_txt_w//2, GAME_H-1.5*start_txt_h))

        mallet.draw(surf)
        player_gong.draw(surf)
        cpu_gong.draw(surf)

        if state=="won":
            if winner=="player":
                winner_txt=font.render("Bang. U Won!", True, theme["win"])
            elif winner=="cpu":
                winner_txt=font.render("Bang. CPU Won!", True, theme["win"])
            replay_txt=font.render("Press R to replay", True, theme["replay"])
            surf.blit(winner_txt, (GAME_W//2-winner_txt.get_width()//2, GAME_H//2))
            surf.blit(replay_txt, (GAME_W//2-replay_txt.get_width()//2, GAME_H//2+winner_txt.get_height()))

        player_score_txt=font.render(f"{player_score}", True, theme["score"])
        cpu_score_txt=font.render(f"{cpu_score}", True, theme["score"])
        surf.blit(player_score_txt, (GAME_W//2-player_score_txt.get_width()-SCORE_PADDING, 0))
        surf.blit(cpu_score_txt, (GAME_W//2+SCORE_PADDING, 0))
        
        pygame.transform.scale(surf, (SCREEN_W,SCREEN_H), screen)

        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
    sys.exit()

main()
