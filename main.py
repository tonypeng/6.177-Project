import pygame
import os
import random

WIDTH = 10
HEIGHT = 10
DIRECTIONS = [(0,1),(0,-1),(1,0),(-1,0)] #toward (row, col)
# Corresponds to ["East", "West", "South", "North"]
DIR_KEYS_1 = [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP]
DIR_KEYS_2 = [pygame.K_d, pygame.K_a, pygame.K_s, pygame.K_w]
FOOD_COLOR = (0,0,255)
### CHRISTINE ###
class Arena:
    # To be full screen and should have a border
    def __init__(self, x, y, border_width, grid_size, points):
        self.x = x
        self.y = y
        self.border_width = border_width
        self.grid_size = grid_size # tuple of (row, col)
        self.points = points
        self.snakes = self.initialize_snakes(10, ((255,0,0), (0,255,0)), ("RED", "GREEN"), points)
        self.food = []
        self.components = pygame.sprite.RenderPlain()
        self.initialize_food()
        for snake in self.snakes:
            for parts in snake.body_parts:
                self.components.add(parts)

    def initialize_food(self):
        for _ in xrange(len(self.snakes)):
            self.make_food()

    def initialize_snakes(self, length, colors, names, points):
        snakes = []
        for i in xrange(len(colors)):
            s = Snake(self, length, colors[i], DIRECTIONS[i], names[i], points[i])
            snakes.append(s)
        return snakes

    def space_occupied(self, row, col):
        for sprite in self.components.sprites():
            if sprite.row == row and sprite.col == col:
                return True
        return False

    def make_food(self):
        temp_row = random.randrange(self.grid_size[0])
        temp_col = random.randrange(self.grid_size[1])
        while self.space_occupied(temp_row, temp_col):
            temp_row = random.randrange(self.grid_size[0])
            temp_col = random.randrange(self.grid_size[1])
        new_food = Body(self, temp_row, temp_col, FOOD_COLOR)
        self.food.append(new_food)
        self.components.add(new_food)

    def remove_food(self, bite):
        self.components.remove(bite)
        self.food.remove(bite)

    def move_snakes(self, directions):
        for snake, direction in zip(self.snakes, directions):
            snake.move(direction)

    """
    Checks each snake to see if it has eaten food or collided with another snake or the boundary
    Returns the Snake that loses or None if the game continues
    """

    def detect_collisions(self):
        for snake in self.snakes:
            head = snake.body_parts[0]
            for bite in self.food:
                if head.collided_with(bite):
                    snake.eat_food(bite)
            if self.check_boundary(head):
                return snake
            for snake in self.snakes:
                for body in snake.body_parts:
                    if head.collided_with(body):
                        return snake
        return None

    """
    Receives a Body object representing the head of a Snake
    Returns true if the head is out of bounds of the Arena (i.e. if the Snake has hit the wall) and false otherwise
    """
    def check_boundary(self, head):
        max_rows = self.grid_size[0]
        max_cols = self.grid_size[1]
        return head.row < 0 or head.row > max_rows or head.col < 0 or head.col > max_cols

    def get_col_left_loc(self, col, width=WIDTH):
        return self.x + self.border_width + col * width
        pass

    def get_row_top_loc(self, row, height=HEIGHT):
        return self.y + self.border_width + row * height
        pass

    def draw_border(self, screen, color):
        mid = self.border_width / 2
        width = self.grid_size[0] * WIDTH
        height = self.grid_size[1] * HEIGHT
        pygame.draw.line(screen, color, (self.x-mid, self.y-self.border_width), (self.x-mid, self.y+width+self.border_width), self.border_width)
        pygame.draw.line(screen, color, (self.x-self.border_width, self.y-mid), (self.x+height+self.border_width, self.y-mid), self.border_width)
        pygame.draw.line(screen, color, (self.x+height+mid, self.y-self.border_width), (self.x+height+mid, self.y+width+self.border_width), self.border_width)
        pygame.draw.line(screen, color, (self.x-self.border_width, self.y+width+mid), (self.x+height+self.border_width, self.y+width+mid), self.border_width)
        return

    pass


class Body(pygame.sprite.Sprite):
    def __init__(self,arena, row, col, color):
        pygame.sprite.Sprite.__init__(self)
        self.row = row
        self.col = col
        self.arena = arena
        self.image = pygame.Surface([WIDTH, HEIGHT])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = self.arena.get_col_left_loc(col)
        self.rect.y = self.arena.get_row_top_loc(row)
        self.color = color

    """
    Receives two Body Objects
    Returns true if the occupy the same space and are not the same object
    """
    def collided_with(self, other):
        if self == other:
            return False
        elif self.row == other.row and self.col == other.col:
            return True
        return False

    def get_loc(self):
        return (self.row, self.col)

    def update(self):
        self.rect.x = self.arena.get_col_left_loc(self.col)
        self.rect.y = self.arena.get_row_top_loc(self.row)

    pass

class Snake:

    def __init__(self, arena, length, color, direction, name, points):
        self.arena = arena
        self.length = length
        self.color = color
        self.direction = direction
        self.points = points
        self.name = name

        # Create body parts depending on initial direction
        start_row = self.arena.grid_size[0] * self.direction[1] / 2
        start_col = self.arena.grid_size[1] * self.direction[0] / 2
        if start_row < 0:
            start_row = start_row*-1
            start_col = self.arena.grid_size[1] - 1
        elif start_col < 0:
            start_row = self.arena.grid_size[0] - 1
            start_col = start_col * -1
        parts = []
        for j in reversed(range(self.length)):
            row_n = start_row + j*self.direction[0]
            col_n = start_col + j*self.direction[1]
            b = Body(self.arena, row_n, col_n, self.color)
            parts.append(b)
        self.body_parts = parts

    def is_head(self, part):
        return self.body_parts[0] == part

    def eat_food(self, bite):
        self.add_unit()
        self.arena.remove_food(bite)
        self.arena.make_food()
        self.points += 10

    def move(self, direction):
        self.direction = direction
        for i in reversed(range(len(self.body_parts))):
            part = self.body_parts[i]
            if i == 0:
                part.row += self.direction[0]
                part.col += self.direction[1]
            else:
                previous = self.body_parts[i-1]
                part.row = previous.row
                part.col = previous.col
            part.update()

    """adds to body part to end of Snake"""
    def add_unit(self):
        previous = self.body_parts[-1]
        unit = Body(self.arena, previous.row, previous.col, self.color)
        self.body_parts.append(unit)
        self.arena.components.add(unit)

def opposite_direction(dir1, dir2):
    for i in xrange(len(dir1)):
        if dir1[i] != -1*dir2[i]:
            return False
    return True


### KEVIN ###
class Game():
    def __init__(self):
        """
        Set up the components to start a game
        """
        size = (50, 50)
        pygame.init()

        width = pygame.display.Info().current_w
        height = pygame.display.Info().current_h
        screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN, 32)

        pygame.display.set_caption("Snake")
        arena = Arena(screen.get_rect().centerx-size[0]*WIDTH/2, screen.get_rect().centery-size[1]*HEIGHT/2, 20, size, (0,0))

        clock = pygame.time.Clock()
        self.main_loop(screen, arena, clock)
        pygame.quit()

    def update_text(self, screen, arena):
        self.screen = screen
        self.arena = arena
        font = pygame.font.SysFont('Couriernew', 50)
        texts = []
        if len(arena.snakes) == 1:
            texts.append(font.render("POINTS: "+str(arena.snakes[0].points), True, arena.snakes[0].color))
        else:
            texts.append(font.render("RED: "+str(arena.snakes[0].points), True, arena.snakes[0].color))
            texts.append(font.render("GREEN: "+str(arena.snakes[1].points), True, arena.snakes[1].color))

        textX = [screen.get_rect().centerx - arena.grid_size[0]*WIDTH, screen.get_rect().centerx + arena.grid_size[0]*HEIGHT]

        for i in range(len(texts)):
            textpos = texts[i].get_rect()
            textpos.centery = screen.get_rect().centery
            textpos.centerx = textX[i]
            self.screen.blit(texts[i], textpos)
        pygame.display.flip()

    def main_loop(self, screen, arena, clock):
        directions = [DIRECTIONS[0], DIRECTIONS[1]]
        stop = False
        loser = Snake(arena, 0, (0,0,0), (1,0), "temp", 0)
        winner = None
        while stop == False:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # user clicks close
                    stop = True
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key in DIR_KEYS_1:
                        new_dir = DIRECTIONS[DIR_KEYS_1.index(event.key)]
                        if not opposite_direction(new_dir, directions[0]):
                            directions[0] = new_dir
                    if event.key in DIR_KEYS_2:
                        new_dir = DIRECTIONS[DIR_KEYS_2.index(event.key)]
                        if not opposite_direction(new_dir, directions[1]):
                            directions[1] = new_dir
            if stop == False:
                screen.fill((0,0,0))
                arena.components.draw(screen)
                arena.draw_border(screen, (0,255,255))
                arena.move_snakes(directions)
                self.update_text(screen, arena)
                pygame.display.flip()
                loser = arena.detect_collisions()
                if loser != None:
                    print loser.color
                    index = arena.snakes.index(loser)
                    if len(arena.snakes)>1 and index == 0:
                        winner = arena.snakes[1]
                    elif len(arena.snakes)>1:
                        winner = arena.snakes[0]
                    stop = True
                clock.tick(10)

        if winner != None:
            winner.points += 1000
            menu = Game_Over_Menu_Multi(screen, arena.snakes, winner)
            menu.run()
        else:
            menu = Game_Over_Menu_Single(screen, arena.snakes)
            menu.run()
        points = []
        for snake in arena.snakes:
            points.append(snake.points)

        event = pygame.event.wait()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                pygame.quit()
            elif event.key == pygame.K_RETURN:
                print 'yes'
                arena = Arena(screen.get_rect().centerx-arena.grid_size[0]*WIDTH/2, screen.get_rect().centery-arena.grid_size[1]*HEIGHT/2, 20, arena.grid_size, points)
                clock = pygame.time.Clock()
                self.main_loop(screen, arena, clock)


class Game_Over_Menu_Single:
    def __init__(self, screen, snakes):
        self.screen = screen
        self.snakes = snakes
        self.font1 = pygame.font.SysFont('Couriernew', 75)
        self.font1.set_bold(True)
        self.font2 = pygame.font.SysFont('Couriernew', 50)
        self.font3 = pygame.font.SysFont("Couriernew", 25)
        self.menu = pygame.Rect(self.screen.get_rect().centerx-400, self.screen.get_rect().centery-250, 800, 500)

    def run(self):
        text = []
        text.append(self.font1.render("You lose!!!", True, self.snakes[0].color))
        text.append(self.font2.render("Points: "+str(self.snakes[0].points), True, (0,255,255)))
        text.append(self.font3.render("Press ENTER to play again or", True, (255, 255, 0)))
        text.append(self.font3.render("press Q to quit", True, (255,255,0)))
        vertical_pos = [self.menu.y+50, self.menu.y+250, self.menu.y+400, self.menu.y+425]

        self.screen.fill((0,0,0))
        pygame.draw.rect(self.screen, (0, 0, 255), self.menu, 0)
        for i in range(len(text)):
            textpos = text[i].get_rect()
            textpos.centerx = self.menu.centerx
            textpos.y = vertical_pos[i]
            self.screen.blit(text[i], textpos)
        pygame.display.flip()

class Game_Over_Menu_Multi:

    def __init__(self, screen, snakes, winner):
        self.screen = screen
        self.snakes = snakes
        self.winner = winner
        self.font1 = pygame.font.SysFont('Couriernew', 75)
        self.font1.set_bold(True)
        self.font2 = pygame.font.SysFont('Couriernew', 50)
        self.font3 = pygame.font.SysFont("Couriernew", 25)
        self.menu = pygame.Rect(self.screen.get_rect().centerx-400, self.screen.get_rect().centery-250, 800, 500)

    def run(self):
        text = []
        text.append(self.font1.render(self.winner.name+" wins!!!", True, self.winner.color))
        text.append(self.font2.render(self.snakes[0].name+" has "+str(self.snakes[0].points)+" points!", True, (0,255,255)))
        text.append(self.font2.render(self.snakes[1].name+" has "+str(self.snakes[1].points)+" points!", True, (0,255,255)))
        text.append(self.font3.render("Press ENTER to play again or", True, (255, 255, 0)))
        text.append(self.font3.render("Q to exit the game", True, (255,255,0)))
        vertical_pos = [self.menu.y+50, self.menu.y+200, self.menu.y+250, self.menu.y+400, self.menu.y+425]

        self.screen.fill((0,0,0))
        pygame.draw.rect(self.screen, (0, 0, 255), self.menu, 0)
        for i in range(len(text)):
            textpos = text[i].get_rect()
            textpos.centerx = self.menu.centerx
            textpos.y = vertical_pos[i]
            self.screen.blit(text[i], textpos)
        pygame.display.flip()

game = Game()
