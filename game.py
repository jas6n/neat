import pygame
import os
import random
import neat
pygame.font.init()


WIN_WIDTH = 1024
WIN_HEIGHT = 768
BG_IMG = pygame.image.load(os.path.join("imgs", "pong_background.png"))
PADDLE_IMG = pygame.transform.scale2x(pygame.transform.scale2x(pygame.image.load(os.path.join
                                                                                 ("imgs", "pong_paddle.png"))))
BALL_IMG = pygame.image.load(os.path.join("imgs", "white_square.png"))
BALL_IMG = pygame.transform.scale(BALL_IMG, (20, 20))

STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Paddle:
    IMG = PADDLE_IMG
    VEL = 30

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move_up(self):
        self.y -= self.VEL

    def move_down(self):
        self.y += self.VEL

    def draw(self, win):
        win.blit(self.IMG, (self.x, self.y))


class Ball:
    DIRECTIONS = [-1, 1]
    IMG = BALL_IMG

    def __init__(self):
        self.x = (1024 - BALL_IMG.get_width()) / 2
        self.y = random.randrange(100, 600)
        self.x_direction = -1  # random.choice(self.DIRECTIONS)
        self.y_direction = -1  # random.choice(self.DIRECTIONS)
        self.x_vel = random.randrange(3, 10)
        self.y_vel = random.randrange(3, 10)

    def move(self):
        if self.hit_ground():
            self.y_direction = -1 * self.y_direction
        if self.hit_ceiling():
            self.y_direction = -1 * self.y_direction
        self.x += self.x_vel * self.x_direction
        self.y += self.y_vel * self.y_direction

    def hit_ground(self):
        if self.y >= 768 - self.IMG.get_height():
            return True

    def hit_ceiling(self):
        if self.y <= 0:
            return True

    def draw(self, win):
        win.blit(BALL_IMG, (self.x, self.y))

    def collide(self, paddle1):  # why does this work instead of making collide its own function?
        if paddle1.x + paddle1.IMG.get_width() >= self.x:
            if paddle1.y <= self.y <= paddle1.y + paddle1.IMG.get_height():
                return True
            # else:  # not because of these
            #     pass
        elif WIN_WIDTH <= self.x + self.IMG.get_width():
            # if paddle2.y <= self.y <= paddle2.y + paddle2.IMG.get_height():
            return True
        #     else:
        #         pass
        # else:
        #     pass


# def collide(ball, paddle1, paddle2):  # why doesn't this work and the above one does?
#     x1 = paddle1.x
#     y1 = paddle1.y
#     x2 = paddle2.x
#     y2 = paddle2.y
#     if x1 + paddle1.IMG.get_width() <= ball.x:
#         if y1 <= ball.y <= y1 + paddle1.IMG.get_height():
#             ball.x_direction = ball.x_direction * -1
#     elif ball.x >= x2:
#         if y2 <= ball.y <= y2 + paddle2.IMG.get_height():
#             ball.x_direction = ball.x_direction * -1


def draw_window(win, paddle1, ball, score):
    win.blit(BG_IMG, (0, 0))
    for p in paddle1:
        p.draw(win)
    # paddle2.draw(win)
    text = STAT_FONT.render("Deaths: " + str(score), True, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    for b in ball:
        b.draw(win)
    pygame.display.update()


def main(genomes, config):
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    paddle1 = []
    ge = []
    nn = []
    # paddle2 = Paddle(1024 - PADDLE_IMG.get_width(), (768 - PADDLE_IMG.get_height()) / 2)
    balls = []  # append this list each time the score increases or something
    score = 0
    clock = pygame.time.Clock()

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nn.append(net)
        paddle1.append(Paddle(0, (WIN_HEIGHT - PADDLE_IMG.get_height()) / 2))
        balls.append(Ball())
        g.fitness = 0
        ge.append(g)

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        if len(balls) == 0:
            break
            # if event.type == pygame.KEYDOWN:
            #     # if event.key == pygame.K_UP:
            #     #     if paddle2.y >= -15:
            #     #         paddle2.move_up()
            #     # elif event.key == pygame.K_DOWN:
            #     #     if paddle2.y <= 800 - PADDLE_IMG.get_height():
            #     #         paddle2.move_down()
            #     if event.key == pygame.K_w:
            #         if paddle1.y >= -15:
            #             paddle1.move_up()
            #     elif event.key == pygame.K_s:
            #         if paddle1.y <= 790 - PADDLE_IMG.get_height():
            #             paddle1.move_down()
        for p, paddle in enumerate(paddle1):
            output = nn[p].activate((paddle.y, abs(paddle.x - balls[p].x), abs(paddle.y - balls[p].y)))
            if output[0] > 0.5:
                if paddle.y >= -15:
                    paddle.move_up()
            else:
                if paddle.y <= 800 - PADDLE_IMG.get_height():
                    paddle.move_down()
        for b in balls:
            b.move()
        for x, b in enumerate(balls):
            if b.x < paddle1[x].x + paddle1[x].IMG.get_width() - 20:  #
                # or ball[c].x + ball[c].IMG.get_width() > paddle2.x + 20:
                ge[x].fitness -= 1
                balls.pop(x)
                paddle1.pop(x)
                nn.pop(x)
                ge.pop(x)

                score += 1

            else:
                check = b.collide(paddle1[x])
                if check:
                    ge[x].fitness += 1
                    b.x_direction = b.x_direction * -1
                    b.x_vel = 20
                    b.y_vel = random.randrange(-10, 10)

        draw_window(win, paddle1, balls, score)


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_file)  # defines all necessary subheadings that are
    # mentioned in the configuration file, looks at and reads in configuration file to variable config
    p = neat.Population(config)  # creates population from config file

    p.add_reporter(neat.StdOutReporter(True))  # gives us statistics about each generation and stuff to see how the
    # algorithm works
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    p.run(main, 50)  # runs fitness function, second parameter is how many generations the algorithm will run


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)  # gives path to current directory
    config_path = os.path.join(local_dir, "config-feedforward.txt")  # joins local directory with configuration file
    run(config_path)
