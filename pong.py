
import pygame, sys, os, time
from pygame.locals import *
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

def UpdateScore(paddle1, ball, score, ballDirX):
    if ball.left == lineWidth:
        return 0
    elif ballDirX == -1 and paddle1.right == ball.left and paddle1.top < ball.top and paddle1.bottom > ball.bottom:
        score += 1
        return score
    elif ball.right == screen_width - lineWidth:
        score=0
        return score
    else:
        return score

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
    text1=text_format("Time 1: %d" % (elap), 24, white)
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



def main():
    game_type = "Time"
    ballPosX=screen_width/2 - lineWidth/2
    ballPosY=screen_height/2 - lineWidth/2

    playerPos=(screen_height-paddleSize)/2
    enemyPos=(screen_height-paddleSize)/2
    score1=0
    score2=0

    ballDirX = -8
    ballDirY = -8

    paddle1=pygame.Rect(paddleOffset, playerPos, lineWidth, paddleSize)
    paddle2 = pygame.Rect(screen_width - paddleOffset - lineWidth, enemyPos, lineWidth, paddleSize)
    ball=pygame.Rect(ballPosX, ballPosY, lineWidth, lineWidth)

    BackgroundGameplay()
    Paddle(paddle1)
    Paddle(paddle2)
    Ball(ball)
    pygame.mouse.set_visible(0)

    # sound.play(loops=-1)
    over = False
    max_score = 5
    max_time = 30

    end_round = ""
    start = time.time()

    while not over:
        pygame.image.save(screen, "screenshot.jpeg")
        elapsed = time.time() - start
        if game_type == "Score":
            if  score1 == max_score or score2 == max_score:
                pygame.quit()
                sys.exit()
        elif game_type == "Time":
            if elapsed > max_time or end_round == "L" or end_round =="R":
                pygame.quit()
                sys.exit()

        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
            elif event.type==MOUSEMOTION:
                mousex, mousey=event.pos
                paddle1.y=mousey


        BackgroundGameplay()
        Paddle(paddle1)
        Paddle(paddle2)
        Ball(ball)

        ball=BallMovement(ball, ballDirX, ballDirY)
        ballDirX, ballDirY, end_round = WallCollision(ball, ballDirX, ballDirY)
        ball_coll = BallCollision(ball, paddle1, paddle2, ballDirX)
        ballDirX = ballDirX * ball_coll
        if game_type == "Score":
            score1,score2 = UpdateScore_2(end_round,score1,score2)
            ScoreHandler(score1,score2)
        elif game_type == "Time":
            timeHandler(start)
        # score = UpdateScore(paddle1, ball, score, ballDirX)
        paddle2 = EnemyMovement(ball, ballDirX, ballDirY, paddle2)
        pygame.display.set_caption('Python - Pygame Simple Arcade Game')
        pygame.display.update()
        pixels = pygame.surfarray.array2d(pygame.display.get_surface())
        clock.tick(fps)

if __name__=='__main__':
    main()
