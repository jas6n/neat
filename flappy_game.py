import pygame
import os
import neat
import random
pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

GEN = 0

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  # in degrees, angle of the tilt of the bird
    ROT_VEL = 20  # how much we rotate the bird on each frame that it moves
    ANIMATION_TIME = 5  # how long we show each bird animation

    def __init__(self, x, y):
        self.x = x  # starting x coordinate of bird
        self.y = y  # starting y coordinate of bird
        self.tilt = 0  # how much the bird is tilted, starts off at 0 because it is looking straight ahead at start
        self.tick_count = 0  # used for physics of bird
        self.vel = 0  # velocity starts at 0 since the bird isn't moving
        self.height = self.y
        self.img_count = 0  # we know which image we are showing for the bird
        self.img = self.IMGS[0]  # our first image is the first bird image

    def jump(self):
        self.vel = -10.5  # negative velocity because the 0, 0 coordinate is at the top left of the window
        self.tick_count = 0  # allows us to know when we last jumped, resets to 0, so we can know when we change
        # direction/velocity
        self.height = self.y  # keeps track of where the bird started jumping from

    def move(self):
        self.tick_count += 1  # each frame we move, the tick count goes up, and when we jump, it resets to 0

        d = self.vel*self.tick_count + 1.5*self.tick_count**2  # how many pixels moved up/down this frame,
        # d = displacement, as the tick count goes up and velocity goes down, d starts to increase

        if d >= 16:
            d = 16  # makes sure that the max velocity is 16 moving down

        if d < 0:
            d -= 2  # fine-tunes movement by allowing movement upwards to be 2 more pixels per frame

        self.y = self.y + d  # sets y value of bird to equal its y value plus the displacement

        if d < 0 or self.y < self.height + 50:  # if the bird has a positive displacement, meaning it is moving up,
            # or the bird's y position is above where it jumped from, tilt the bird upwards
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION  # tilts the bird to the MAX_ROTATION angle
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL  # tilts bird down slowly towards 90 degrees

    def draw(self, win):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:  # rotates between images each frame
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0  # resets image count to 0

        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)  # rotates image around top left
        new_rectangle = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)  # makes it
        # so image is rotated around the center
        win.blit(rotated_image, new_rectangle.topleft)  # draws rotated image on window

    def get_mask(self):
        return pygame.mask.from_surface(self.img)  # returns a 2d array that tells which pixels are part of image


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.top = 0  # where top pipe will be drawn
        self.bottom = 0  # where bottom pipe will be drawn
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)  # image of top pipe
        self.PIPE_BOTTOM = PIPE_IMG  # image of bottom pipe

        self.passed = False  # determines if the bird has already passed the pipe
        self.set_height()  # determines the height of the pipe based on where it starts and where it ends

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()  # refers to y coordinate of top left corner of top pipe
        self.bottom = self.height + self.GAP  # refers to y coordinate of top left corner of bottom pipe

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))  # distance between top left
        # coordinates of bird and top
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)  # first point of overlap between bird mask and bottom
        # pipe using the bottom offset, returns none if they don't collide
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:  # if they are not None
            return True  # they did collide
        else:
            return False  # they didn't collide


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen):
    win.blit(BG_IMAGE, (0, 0))  # draws the background image

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), True, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    text = STAT_FONT.render("Gen: " + str(gen), True, (255, 255, 255))
    win.blit(text, (10, 10))
    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()  # updates the window


def main(genomes, config):
    global GEN
    GEN += 1
    nets = []  # tracks neural network
    ge = []  # tracks genome
    birds = []  # tracks bird

    for _, g in genomes:  # describes each individual genome that is in the population, genomes is a tuple and we only
        # want the second part of each element so we must to _,
        net = neat.nn.FeedForwardNetwork.create(g, config)  # sets up neural network and assigns it to net variable
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0  # initializes fitness to 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    go = True
    while go:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                go = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1

        else:  # breaks out of loop and new generation starts
            go = False
            break

        for x, bird in enumerate(birds):  # moves bird, determines if it should jump from nn
            bird.move()
            # ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height),  # holds output value of nn
                                       abs(bird.y - pipes[pipe_ind].bottom)))  # 3 parameters are the three inputs to
            # the nn

            if output[0] > 0.5:  # output is a list that contains all the possible outputs, since we only have one
                # output, we only need to access the first element of the output list
                bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):  # gives back both count and value of the list at each element
                if pipe.collide(bird):
                    ge[x].fitness -= 1  # allows for birds to stay away from hitting pipe
                    birds.pop(x)  # removes bird, nn, genome at x
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 1
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score, GEN)


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
