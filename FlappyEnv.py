import pygame
import random
import csv
import numpy as np


# -- Global constants
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (50, 50, 255)
LIGHTBLUE = (0, 200, 255)
GREEN = (0, 150, 0)
YELLOW = (255, 200, 0)

# Screen dimensions
SCREEN_WIDTH = 450
SCREEN_HEIGHT = 800


class Player(pygame.sprite.Sprite):
    """ This class represents the bird that the player controls. """

    # Constructor function
    def __init__(self, x, y):
        # Call the parent's constructor
        super().__init__()

        # Set height, width
        self.image = pygame.Surface([30, 30])
        self.image.fill(YELLOW)

        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x

        # Set speed vector
        self.change_x = 0
        self.change_y = 0
        self.pipes = None

        self.score = 0

        # List of sprites we can bump against
        self.level = None
        self.hit = False

    def changespeed(self, x, y):
        """ Change the speed of the player. """
        self.change_x += x
        self.change_y += y

    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .20

        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height
            self.hit = True
        elif self.rect.y <= 0:
            self.hit = True

    def jump(self):
        """ Called when user hits 'jump' button. """
        self.change_y = -6

    def update(self):
        # Gravity
        self.calc_grav()

        """ Update the player position. """
        # Move left/right
        self.rect.x += self.change_x

        # Move up/down
        self.rect.y += self.change_y

        block_hit_list = pygame.sprite.spritecollide(self, self.pipes, False)
        for block in block_hit_list:

            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right
            self.rect.y = 50
            self.rect.x = 50
            self.score = 0
            self.hit = True


class Pipe(pygame.sprite.Sprite):
    """ Pipe the player can fly into. """

    def __init__(self, x, y, width, height):
        """ Constructor for the pipe that the player can run into. """
        # Call the parent's constructor
        super().__init__()

        # Make a green pipe, of the size specified in the parameters
        self.image = pygame.Surface([width, height])
        self.image.fill(GREEN)
        self.top_image = pygame.Surface([width, SCREEN_HEIGHT - height - 50])
        self.top_image.fill(GREEN)

        self.rect = self.image.get_rect()
        self.rect.y = y
        self.rect.x = x

        self.top_rect = self.top_image.get_rect()
        self.top_rect.y = 0
        self.top_rect.x = x

        self.change_x = 2

    def update(self):
        """ Update the pipe position. """
        self.rect.x -= self.change_x
        self.top_rect.x -= self.change_x


class Env:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption('FlappySquare')

        self.all_pipes = []
        self.state = None
        self.pipe_count = 0
        self.reward = 0.
        self.done = False

        self.reset()

    def reset(self):
        self.all_pipes = []
        self.state = None
        self.pipe_count = 0
        self.all_sprite_list = pygame.sprite.Group()
        self.pipe_list = pygame.sprite.Group()
        self.player = Player(50, 300)

        self.pipe_count = 0

        self.all_sprite_list.add(self.player)

        self.pipecreation()

        self.font = pygame.font.SysFont('Calibri', 25, True, False)

        self.clock = pygame.time.Clock()

    def step(self, action):
        self.reward = 0
        if action == 1:
            self.player.jump()
        self.all_sprite_list.update()

        if self.all_pipes[-1].rect.x <= random.randrange(50, 100, 2):
            self.pipecreation()

        if self.all_pipes[self.pipe_count].rect.x + 70 <= self.player.rect.x:  # +70 -> pipe width
            self.player.score += 1
            self.pipe_count += 1
            self.reward = self.player.score

        # self.clock.tick(60)
        # self.clock.tick()
        self.render()

        if not self.player.hit:
            done = False
        else:
            done = True

        player_x = self.player.rect.x
        player_y = self.player.rect.y
        pipe_x = self.all_pipes[self.pipe_count].rect.x + 70  # pipe x position + 70 (pipe width)
        pipe_y_bot = self.all_pipes[self.pipe_count].rect.y - player_y  # range to bot pipe
        pipe_y_top = pipe_y_bot - self.pipe_hole  # range to top pipe
        player_to_pipe_distance = pipe_x - player_x
        player_y_vel = self.player.change_y / 10
        # TODO make normal list
        self.state = (player_y / 1000, player_to_pipe_distance / 1000, pipe_y_bot / 1000, pipe_y_top / 1000)
        return np.array(self.state), self.reward, done, {}
        # self.state = [player_y / 1000, player_to_pipe_distance / 1000, pipe_y_bot / 1000, pipe_y_top / 1000]
        # return self.state, self.reward, done, {}

    def render(self, fps=60):
        self.all_sprite_list.update()
        self.screen.fill(LIGHTBLUE)
        self.all_sprite_list.draw(self.screen)
        self.text = self.font.render("Score: " + str(self.player.score), True, WHITE)
        self.screen.blit(self.text, [50, 50])

        pygame.display.flip()
        self.clock.tick(fps)

    def pipecreation(self):
        self.pipe_hole = 200
        self.h = random.randrange(200, 700)
        self.pipe = Pipe(SCREEN_WIDTH, self.h, 70, SCREEN_HEIGHT - self.h)
        self.pipe_list.add(self.pipe)
        self.player.pipes = self.pipe_list
        self.all_sprite_list.add(self.pipe)

        self.all_pipes.append(self.pipe)

        self.pipe = Pipe(SCREEN_WIDTH, 0, 70, self.h - self.pipe_hole)
        self.pipe_list.add(self.pipe)
        self.player.pipes = self.pipe_list
        self.all_sprite_list.add(self.pipe)


if __name__ == "__main__":
    env = Env()
    game_over = False
    action = 0
    hand_made_observation = []
    data_line = []
    while not game_over:
        # if random.randint(0, 100) > 98:
        #     action = 1
        # else:
        #     action = 0
        ##
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    action = 1
            else:
                action = 0

        new_observation, reward, game_over, info = env.step(action)
        # env.step(action)

        env.render()

        # Handmade
        # new_observation.append(action)
        # hand_made_observation.append(new_observation)
        # if reward == 10:
        #     with open("training_data_handmade.csv", "w", newline='') as csv_file:
        #         writer = csv.writer(csv_file, delimiter=',')
        #         for line in hand_made_observation:
        #             for element in line:
        #                 data_line.append(element)
        #             writer.writerow(data_line)
        #             data_line.clear()

        if game_over:
            game_over = False
            env.reset()
