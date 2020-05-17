import pygame
import math
import random
import copy

WIDTH = 720
HEIGHT = 600
PLANET_X = 342
PLANET_Y = 503
DIAMETER = 36
RADIUS = 18
SPEED = 15
ROWS = 17
COLUMNS = 20
STEPS = 20
ROCKET_CENTER_Y = 520
GAME_OVER_LINE = 490
WHITE = (255, 255, 255)
FONT_1 = 'comicsansms'
FONT_2 = 'helvetica'
BLANK = ' '

# Initialize all imported pygame modules
pygame.init()

# Create the window
win = pygame.display.set_mode((WIDTH, HEIGHT))

# Title and Icon
pygame.display.set_caption("Planet Shooter")
icon = pygame.image.load("logo.png")
pygame.display.set_icon(icon)

# Background
backgroundImg = pygame.image.load("background.png")

# Planets
red = pygame.image.load("red.png")
blue = pygame.image.load("blue.png")
green = pygame.image.load("green.png")
yellow = pygame.image.load("yellow.png")
purple = pygame.image.load("purple.png")

# Colors
Colors = [red, blue, green, yellow, purple]

# Rocket
rocketImg = pygame.image.load("rocket.png")
rocketImg.convert_alpha()   # Changes the pixel format

# Sounds
collisionSound = pygame.mixer.Sound('collisionSound.ogg')
popSound = pygame.mixer.Sound('popSound.ogg')
popSound.set_volume(0.05)   # Takes values from 0.0 to 1.0


# Planet
class Planet:
    def __init__(self, color, row=0, column=0):

        self.rect = pygame.Rect(PLANET_X, PLANET_Y, DIAMETER, DIAMETER)
        self.color = color
        self.row = row
        self.column = column
        self.angle = get_angle()*math.pi/180
        self.speed = SPEED
        self.radius = RADIUS
        self.dx = math.cos(self.angle) * self.speed
        self.dy = -math.sin(self.angle) * self.speed

    def update(self):

        if self.rect.left <= 0:
            self.dx *= -1
        elif self.rect.right >= WIDTH:
            self.dx *= -1

        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self):
        win.blit(self.color, (self.rect.x, self.rect.y))


# Score
class Score:
    def __init__(self):
        self.total = 0
        self.font = pygame.font.SysFont(FONT_1, 25)
        self.render = self.font.render('Score: ' + str(self.total), True, WHITE)
        self.rect = self.render.get_rect()
        self.rect.left = 10
        self.rect.bottom = HEIGHT - 10

    def update(self, deleteList):
        self.total += ((len(deleteList)) * 10)
        self.render = self.font.render('Score: ' + str(self.total), True, WHITE)

    def draw(self):
        win.blit(self.render, self.rect)


# Angle
def get_angle():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    x, y = mouse_x - PLANET_X - RADIUS, mouse_y - PLANET_Y - RADIUS
    angle = (180 / math.pi) * -math.atan2(y, x)
    if 10 > angle >= -90:
        angle = 10
    if angle < -90 or 170 < angle <= 180:
        angle = 170
    return angle


# Making Blank Board
def make_blank_board():
    array = []

    for row in range(ROWS):
        column = []
        for i in range(COLUMNS):
            column.append(BLANK)
        array.append(column)

    return array


# Setting Positions of the Planets
def set_array_pos(array):
    for row in range(ROWS):
        for column in range(len(array[row])):
            if array[row][column] != BLANK:
                array[row][column].rect.x = (DIAMETER * column)
                array[row][column].rect.y = (DIAMETER * row)

    for row in range(1, ROWS, 2):
        for column in range(len(array[row])):
            if array[row][column] != BLANK:
                array[row][column].rect.x += RADIUS

    for row in range(1, ROWS):
        for column in range(len(array[row])):
            if array[row][column] != BLANK:
                array[row][column].rect.y -= RADIUS * (2 - math.sqrt(3)) * row

    delete_extra_planets(array)


# Deleting Last Planets in the Even Rows
def delete_extra_planets(array):
    for row in range(ROWS):
        for column in range(len(array[row])):
            if array[row][column] != BLANK:
                if array[row][column].rect.right > WIDTH:
                    array[row][column] = BLANK


# Setting Planets When Starting the Game
def set_planets(array, Colors):
    for row in range(6):
        for column in range(len(array[row])):
            random.shuffle(Colors)
            planet = Planet(Colors[0], row, column)
            array[row][column] = planet

    set_array_pos(array)


# Drawing Planets to the Game Window
def draw_planet_array(array):
    for row in range(ROWS):
        for column in range(len(array[row])):
            if array[row][column] != BLANK:
                array[row][column].draw()


# Adding 2 rows to the top
def add_2_rows(planetArray):
    arr = make_blank_board()
    for row in range(2):
        for column in range(COLUMNS):
            arr[row][column] = Planet(Colors[random.randint(0, 4)])

    for row in range(2, ROWS):
        for column in range(COLUMNS):
            arr[row][column] = planetArray[row-2][column]
    return arr


# Finding the Floating Planets
def find_lonely_planets(planetArray):
    first_row_planets = [column for column in range(len(planetArray[0])) if planetArray[0][column] != BLANK]

    new_list = []

    for i in range(len(first_row_planets)):
        if i == 0:
            new_list.append(first_row_planets[i])
        elif first_row_planets[i] > first_row_planets[i - 1] + 1:
            new_list.append(first_row_planets[i])

    copyOfBoard = make_blank_board()

    for row in range(len(planetArray)):
        for column in range(len(planetArray[0])):
            copyOfBoard[row][column] = planetArray[row][column]
            planetArray[row][column] = BLANK

    for column in new_list:
        pop_lonely_planets(planetArray, copyOfBoard, column)


# Pop the Floating Planets
def pop_lonely_planets(planetArray, copyOfBoard, column, row=0):
    if (row < 0 or row > (len(planetArray) - 1)
            or column < 0 or column > (len(planetArray[0]) - 1)):
        return

    elif copyOfBoard[row][column] == BLANK:
        return

    elif planetArray[row][column] == copyOfBoard[row][column]:
        return

    planetArray[row][column] = copyOfBoard[row][column]

    if row == 0:
        pop_lonely_planets(planetArray, copyOfBoard, column + 1, row)
        pop_lonely_planets(planetArray, copyOfBoard, column - 1, row)
        pop_lonely_planets(planetArray, copyOfBoard, column, row + 1)
        pop_lonely_planets(planetArray, copyOfBoard, column - 1, row + 1)

    elif row % 2 == 0:
        pop_lonely_planets(planetArray, copyOfBoard, column + 1, row)
        pop_lonely_planets(planetArray, copyOfBoard, column - 1, row)
        pop_lonely_planets(planetArray, copyOfBoard, column, row + 1)
        pop_lonely_planets(planetArray, copyOfBoard, column - 1, row + 1)
        pop_lonely_planets(planetArray, copyOfBoard, column, row - 1)
        pop_lonely_planets(planetArray, copyOfBoard, column - 1, row - 1)

    else:
        pop_lonely_planets(planetArray, copyOfBoard, column + 1, row)
        pop_lonely_planets(planetArray, copyOfBoard, column - 1, row)
        pop_lonely_planets(planetArray, copyOfBoard, column, row + 1)
        pop_lonely_planets(planetArray, copyOfBoard, column + 1, row + 1)
        pop_lonely_planets(planetArray, copyOfBoard, column, row - 1)
        pop_lonely_planets(planetArray, copyOfBoard, column + 1, row - 1)


# Where the New Planet Needs to Stop
def stop_planet(planetArray, newPlanet, launchPlanet, score):
    deleteList = []

    for row in range(len(planetArray)):
        for column in range(len(planetArray[row])):

            if (planetArray[row][column] != BLANK and newPlanet != None):
                if (pygame.sprite.collide_rect(newPlanet, planetArray[row][column])) or newPlanet.rect.top < 0:
                    if newPlanet.rect.top < 0:
                        newRow, newColumn = add_planet_to_top(planetArray, newPlanet)

                    elif newPlanet.rect.centery >= planetArray[row][column].rect.centery:

                        if newPlanet.rect.centerx >= planetArray[row][column].rect.centerx:
                            if row % 2 == 0:
                                newRow = row + 1
                                newColumn = column
                                planetArray[newRow][newColumn] = copy.copy(newPlanet)
                                planetArray[newRow][newColumn].row = newRow
                                planetArray[newRow][newColumn].column = newColumn

                            else:
                                newRow = row + 1
                                newColumn = column + 1
                                planetArray[newRow][newColumn] = copy.copy(newPlanet)
                                planetArray[newRow][newColumn].row = newRow
                                planetArray[newRow][newColumn].column = newColumn

                        elif newPlanet.rect.centerx < planetArray[row][column].rect.centerx:
                            if row % 2 == 0:
                                newRow = row + 1
                                newColumn = column - 1
                                if newColumn < 0:
                                    newColumn = 0
                                planetArray[newRow][newColumn] = copy.copy(newPlanet)
                                planetArray[newRow][newColumn].row = newRow
                                planetArray[newRow][newColumn].column = newColumn
                            else:
                                newRow = row + 1
                                newColumn = column
                                planetArray[newRow][newColumn] = copy.copy(newPlanet)
                                planetArray[newRow][newColumn].row = newRow
                                planetArray[newRow][newColumn].column = newColumn


                    elif newPlanet.rect.centery < planetArray[row][column].rect.centery:
                        if newPlanet.rect.centerx >= planetArray[row][column].rect.centerx:
                            if row == 0 or row % 2 == 0:
                                newRow = row - 1
                                newColumn = column
                                planetArray[newRow][newColumn] = copy.copy(newPlanet)
                                planetArray[newRow][newColumn].row = newRow
                                planetArray[newRow][newColumn].column = newColumn
                            else:
                                newRow = row - 1
                                newColumn = column + 1
                                planetArray[newRow][newColumn] = copy.copy(newPlanet)
                                planetArray[newRow][newColumn].row = newRow
                                planetArray[newRow][newColumn].column = newColumn

                        elif newPlanet.rect.centerx <= planetArray[row][column].rect.centerx:
                            if row % 2 == 0:
                                newRow = row - 1
                                newColumn = column - 1
                                planetArray[newRow][newColumn] = copy.copy(newPlanet)
                                planetArray[newRow][newColumn].row = newRow
                                planetArray[newRow][newColumn].column = newColumn

                            else:
                                newRow = row - 1
                                newColumn = column
                                planetArray[newRow][newColumn] = copy.copy(newPlanet)
                                planetArray[newRow][newColumn].row = newRow
                                planetArray[newRow][newColumn].column = newColumn

                    pop_planets(planetArray, newRow, newColumn, newPlanet.color, deleteList)
                    collisionSound.play()

                    if len(deleteList) >= 3:
                        popSound.play()
                        for pos in deleteList:
                            row = pos[0]
                            column = pos[1]
                            planetArray[row][column] = BLANK
                        find_lonely_planets(planetArray)

                        score.update(deleteList)

                    launchPlanet = False
                    newPlanet = None

    return launchPlanet, newPlanet, score


# Adding Planets to the First Row
def add_planet_to_top(planetArray, planet):
    leftSidex = planet.rect.left

    columnDivision = math.modf(float(leftSidex) / float(DIAMETER))
    column = int(columnDivision[1])

    if columnDivision[0] < 0.5:
        planetArray[0][column] = copy.copy(planet)
    else:
        column += 1
        planetArray[0][column] = copy.copy(planet)

    row = 0

    return row, column


# Pop Planets After Shooting
def pop_planets(planetArray, row, column, color, deleteList):
    if row < 0 or column < 0 or row > (len(planetArray) - 1) or column > (len(planetArray[0]) - 1):
        return

    elif planetArray[row][column] == BLANK:
        return

    elif planetArray[row][column].color != color:
        return

    for planet in deleteList:
        if planetArray[planet[0]][planet[1]] == planetArray[row][column]:
            return

    deleteList.append((row, column))

    if row == 0:
        pop_planets(planetArray, row, column - 1, color, deleteList)
        pop_planets(planetArray, row, column + 1, color, deleteList)
        pop_planets(planetArray, row + 1, column, color, deleteList)
        pop_planets(planetArray, row + 1, column - 1, color, deleteList)

    elif row % 2 == 0:

        pop_planets(planetArray, row + 1, column, color, deleteList)
        pop_planets(planetArray, row + 1, column - 1, color, deleteList)
        pop_planets(planetArray, row - 1, column, color, deleteList)
        pop_planets(planetArray, row - 1, column - 1, color, deleteList)
        pop_planets(planetArray, row, column + 1, color, deleteList)
        pop_planets(planetArray, row, column - 1, color, deleteList)

    else:
        pop_planets(planetArray, row - 1, column, color, deleteList)
        pop_planets(planetArray, row - 1, column + 1, color, deleteList)
        pop_planets(planetArray, row + 1, column, color, deleteList)
        pop_planets(planetArray, row + 1, column + 1, color, deleteList)
        pop_planets(planetArray, row, column + 1, color, deleteList)
        pop_planets(planetArray, row, column - 1, color, deleteList)


# Screen After Winning / Losing
def end_screen(score, winorlose):
    font1 = pygame.font.SysFont(FONT_1, 70)
    message1 = font1.render('GAME OVER', True, WHITE)
    font2 = pygame.font.SysFont(FONT_1, 30)
    message2 = font2.render('You {}! Your Score is {}.'.format(winorlose, str(score)), True, WHITE)
    font3 = pygame.font.SysFont(FONT_2, 20)
    message3 = font3.render('Press Enter to Play Again', True, WHITE)

    message1Rect = message1.get_rect()
    message1Rect.center = (WIDTH / 2, 200)
    message2Rect = message2.get_rect()
    message2Rect.center = (WIDTH / 2, 300)
    message3Rect = message3.get_rect()
    message3Rect.center = (WIDTH / 2, 500)

    win.blit(backgroundImg, (0, 0))
    win.blit(message1, message1Rect)
    win.blit(message2, message2Rect)
    win.blit(message3, message3Rect)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    return


# Game Loop
def game_loop():

    launchPlanet = False
    newPlanet = None

    rocket_copy = pygame.transform.rotate(rocketImg, int(get_angle() - 90)).copy()

    planetArray = make_blank_board()
    set_planets(planetArray, Colors)

    nextPlanet = Planet(Colors[0])
    nextPlanet.rect.left = PLANET_X
    nextPlanet.rect.top = PLANET_Y

    score = Score()

    count = 0
    adding_rows = False

    run = True
    while run:
        win.blit(backgroundImg, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEMOTION:
                rocket_copy = pygame.transform.rotate(rocketImg, int(get_angle() - 90)).copy()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                count += 1
                launchPlanet = True
                if count % STEPS == 0 and count is not 0:
                    adding_rows = True

        if launchPlanet:
            if newPlanet is None:
                newPlanet = Planet(nextPlanet.color)

            newPlanet.update()
            newPlanet.draw()

            launchPlanet, newPlanet, score = stop_planet(planetArray, newPlanet, launchPlanet, score)

            finalPlanetList = []
            for row in range(len(planetArray)):
                for column in range(len(planetArray[0])):
                    if planetArray[row][column] != BLANK:
                        finalPlanetList.append(planetArray[row][column])
                        if planetArray[row][column].rect.bottom > GAME_OVER_LINE:
                            return score.total, 'lose'

            if len(finalPlanetList) == 0:
                return score.total, 'win'

            random.shuffle(Colors)

            if not launchPlanet:
                nextPlanet = Planet(Colors[0])
                nextPlanet.rect.left = PLANET_X
                nextPlanet.rect.top = PLANET_Y

        rocket_x = WIDTH / 2 - int(rocket_copy.get_width() / 2)
        rocket_y = ROCKET_CENTER_Y - int(rocket_copy.get_height() / 2)
        win.blit(rocket_copy, (rocket_x, rocket_y))

        nextPlanet.draw()

        while adding_rows:
            planetArray = add_2_rows(planetArray)
            adding_rows = False

        set_array_pos(planetArray)
        draw_planet_array(planetArray)

        score.draw()

        pygame.display.update()


while True:
    score, winorlose = game_loop()
    end_screen(score, winorlose)

pygame.quit()
