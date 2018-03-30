
import pygame, sys, os, time
from pygame.locals import *
import pygame.surfarray
import numpy as np

# Game Initialization
pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=4096)
pygame.init()

# Center the Game Application
os.environ['SDL_VIDEO_CENTERED']='1'


# Game Resolution
screen_width=800
screen_height=600
screen=pygame.display.set_mode((screen_width, screen_height))

# Initialize Sound Files
# sound=pygame.mixer.Sound('sounds/sound.wav')
# sound.set_volume(.5)

# Color
black=(0, 0, 0)
white=(255, 255, 255)
blue=(0, 0, 255)

# Fonts
# font="font/Arcade Future.otf"

# Framerate
clock=pygame.time.Clock()
fps=2000

# Initial Variables
lineWidth=10
paddleSize=50
paddleOffset=20



def text_format(text, textSize, textColor):
    font=pygame.font.SysFont('arial', textSize)
    newText=font.render(text, 0, textColor)
    return newText

def BackgroundGameplay():
    screen.fill(black)
    pygame.draw.line(screen, white, ((screen_width / 2), 0), ((screen_width / 2), screen_height), 2)
    pygame.draw.rect(screen, blue, ((0, 0), (screen_width, screen_height)), lineWidth)

def Paddle(paddle):
    if paddle.bottom > screen_height - lineWidth:
        paddle.bottom = screen_height - lineWidth
    elif paddle.top < lineWidth:
        paddle.top = lineWidth

    pygame.draw.rect(screen, white, paddle)

def Ball(ball):
    pygame.draw.rect(screen, white, ball)

def BallMovement(ball, ballDirX, ballDirY):
    ball.x += ballDirX
    ball.y += ballDirY
    return ball

def WallCollision(ball, ballDirX, ballDirY):
    over = ""
    if ball.top <= (lineWidth) or ball.bottom >= (screen_height - lineWidth):
        ballDirY = ballDirY * -1
    if ball.left <= (lineWidth) or ball.right >= (screen_width - lineWidth):
        ballDirX = ballDirX * -1
        if ball.left <= (lineWidth):
            over = "L"
        if ball.right >= (screen_width - lineWidth):
            over = "R"
    return ballDirX, ballDirY, over



def BallCollision(ball, paddle1, paddle2, ballDirX):
    if ballDirX < 0 and paddle1.right >= ball.left and paddle1.top < ball.top and paddle1.bottom > ball.bottom:
        return -1
    elif ballDirX > 0 and paddle2.left <= ball.right and paddle2.top < ball.top and paddle2.bottom > ball.bottom:
        return -1
    else:
        return 1


def UpdateScore_2(score_update, score1, score2):
    if score_update == "":
        return score1,score2
    elif score_update == "L":
        score2 += 1
    elif score_update == "R":
        score1 += 1
    return score1,score2

def ScoreHandler(score1, score2):
    text1=text_format("Score 1: %s" % (score1), 24, white)
    text2=text_format("Score 2: %s" % (score2), 24, white)
    textRect1=text1.get_rect()
    textRect2=text2.get_rect()
    textRect1.topleft=(50, 25)
    textRect2.topleft=(450, 25)
    screen.blit(text1, textRect1)
    screen.blit(text2, textRect2)

def timeHandler(start):
    end = time.time()
    elap = end - start
    text1=text_format("Time: %d" % (elap), 24, white)
    textRect1=text1.get_rect()
    textRect1.topleft=(50, 25)
    screen.blit(text1, textRect1)


def EnemyMovement(ball, ballDirX, ballDirY, paddle2):
    if ballDirX < 0:
        if paddle2.centery < (screen_height / 2):
            paddle2.y += abs(ballDirY)
        elif paddle2.centery > (screen_height / 2):
            paddle2.y -= abs(ballDirY)
            # if ball moving towards bat, track its movement.
    elif ballDirX > 0:
        if paddle2.centery < ball.centery:
            paddle2.y += abs(ballDirY)
        else:
            paddle2.y -= abs(ballDirY)
    return paddle2



# sound.play(loops=-1)
max_score = 5
max_time = 30







class pong:
    def __init__(self, game_type):
        self.game_type = game_type
        self.start()
        pass


    def start(self):
        self.time = 0
        self.score1 = 0
        self.score2 = 0
        self.over = False
        self.start_time = time.time()
        self.ballPosX=screen_width/2 - lineWidth/2
        self.ballPosY=screen_height/2 - lineWidth/2

        self.playerPos=(screen_height-paddleSize)/2
        self.enemyPos=(screen_height-paddleSize)/2

        self.ballDirX = -8
        self.ballDirY = -8

        self.paddle1=pygame.Rect(paddleOffset, self.playerPos, lineWidth, paddleSize)
        self.paddle2 = pygame.Rect(screen_width - paddleOffset - lineWidth, self.enemyPos, lineWidth, paddleSize)
        self.ball=pygame.Rect(self.ballPosX,self. ballPosY, lineWidth, lineWidth)

        self.end_round = ""
        BackgroundGameplay()
        Paddle(self.paddle1)
        Paddle(self.paddle2)
        Ball(self.ball)
        pygame.mouse.set_visible(0)




    def get_pixels(self):
        return self.pixels



    def iterate(self, action):
        elapsed = time.time() - self.start_time
        if self.game_type == "Score":
            if  self.score1 == max_score or self.score2 == max_score:
                self.over = True
        elif self.game_type == "Time":
            if elapsed > max_time or self.end_round == "L" or self.end_round =="R":
                self.over = True

        if action == 1:
            self.paddle1.y= self.paddle1.y - 5
        elif action == 2:
            self.paddle1.y= self.paddle1.y + 5

        if self.paddle1.y < 0:
            self.paddle1.y = 0 + lineWidth
        elif self.paddle1.y > screen_height - lineWidth:
            self.paddle1.y = screen_height - lineWidth


        BackgroundGameplay()
        Paddle(self.paddle1)
        Paddle(self.paddle2)
        Ball(self.ball)

        self.ball=BallMovement(self.ball, self.ballDirX, self.ballDirY)
        self.ballDirX, self.ballDirY, self.end_round = WallCollision(self.ball, self.ballDirX, self.ballDirY)
        ball_coll = BallCollision(self.ball, self.paddle1,self.paddle2, self.ballDirX)
        ballDirX = self.ballDirX * ball_coll
        if self.game_type == "Score":
            self.score1,self.score2 = UpdateScore_2(self.end_round,self.score1,self.score2)
            ScoreHandler(self.score1,self.score2)
        elif self.game_type == "Time":
            timeHandler(self.start_time)
        self.paddle2 = EnemyMovement(self.ball, self.ballDirX, self.ballDirY self.paddle2)
        pygame.display.set_caption('Python - Pygame Simple Arcade Game')
        # pygame.display.update()
        pygame.display.update()
        surface = pygame.display.get_surface()
        self.pixels = pygame.surfarray.array3d(surface)
        clock.tick(fps)
        if self.game_type == "Score":
            return self.score1
        else:
            return elapsed, self.over


    def quit_game(self):
        pygame.quit()
        sys.exit()


# if __name__=='__main__':
#     main()
