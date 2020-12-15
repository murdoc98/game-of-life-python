# Load and initialize Modules here
import pygame, sys, random
import numpy as np
pygame.init()
base_font = pygame.font.SysFont('Helvetica', 16)

# Colors
color = {
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'dark blue': (26, 82, 118),
    'light blue': (84, 153, 199),
    'purple': (179, 136, 235)
}

# Main Class
class MainRun(object):
    global color
    def __init__(self, initialState=None):
        # Main settings of window
        self.scSize = (1280, 720)
        self.sc = pygame.display.set_mode(self.scSize)
        self.windowclock = pygame.time.Clock()
        pygame.font.init()
        # Multiple surfaces
        self.populationScreen = pygame.Surface((180, 360))
        self.varianceScreen = pygame.Surface((180, 360))
        # Initial state of game of life
        self.gol = GameOfLife(pygame.Surface((1100, 550)))
        self.dashboard = Dashboard(pygame.Surface((180, 550)))
        if initialState == None:
            self.gol.setGenesis()
        else:
            self.gol.bornCells = initialState
        self.gol.graphNewState()
        self.generation = 1
        self.Main()

    def Main(self):
        while True:
            # Keyboard events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        if(self.gol.cellSize > 1):
                            self.gol.cellSize -= 1
                            self.gol.relocateUniverse()
                    if event.key == pygame.K_o:
                        if(self.gol.cellSize < 20):
                            self.gol.cellSize += 1
                            self.gol.relocateUniverse()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if 5 < event.pos[0] < 85 and 82 < event.pos[1] < 112:
                        self.gol.status = 'run'
                    if 90 < event.pos[0] < 175 and 82 < event.pos[1] < 112:
                        self.gol.evolve()
                        self.dashboard.update(self.gol.generation, len(self.gol.cellsAlive), 3)
                    if 5 < event.pos[0] < 85 and 122 < event.pos[1] < 152:
                        self.gol.reset()
                    if 90 < event.pos[0] < 175 and 122 < event.pos[1] < 152:
                        self.gol.status = 'pause'
                    if 5 < event.pos[0] < 175 and 250 < event.pos[1] < 280:
                        self.gol.setGenesis()
                        self.gol.graphNewState()
                    if 5 < event.pos[0] < 175 and 290 < event.pos[1] < 320:
                        print('Select file')
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                if self.gol.view[0] < 1280 * self.gol.cellSize:
                    self.gol.view[0] += self.gol.cellSize
                    self.gol.relocateUniverse()
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                if self.gol.view[0] > 0:
                    self.gol.view[0] -= self.gol.cellSize
                    self.gol.relocateUniverse()
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                if self.gol.view[1] < 720 * self.gol.cellSize:
                    self.gol.view[1] += self.gol.cellSize
                    self.gol.relocateUniverse()
            if pygame.key.get_pressed()[pygame.K_UP]:
                if self.gol.view[1] > 0:
                    self.gol.view[1] -= self.gol.cellSize
                    self.gol.relocateUniverse()
            if self.gol.status == 'run':
                self.gol.evolve()
                self.dashboard.update(self.gol.generation, len(self.gol.cellsAlive), 3)

            # Update all screens
            self.sc.blit(self.dashboard.surface, (0, 0))
            self.sc.blit(self.gol.surface, (180, 0))
            pygame.display.update()
            self.windowclock.tick(60)

class GameOfLife(object):
    def __init__(self, surface):
        self.surface = surface
        self.cellsAlive = set()
        self.deathCells = set()
        self.bornCells = set()
        self.neighborsChecked = set()
        self.width = 1100
        self.heigth = 1100
        self.view = [0, 0]
        self.minSurvive = 2 # Modify to crwate new gen rule
        self.maxSurvive = 3 # Modify to crwate new gen rule 
        self.minBorn = 3 # Modify to crwate new gen rule
        self.maxBorn = 3 # Modify to crwate new gen rule
        self.surface.fill(color['white'])
        self.cellSize = 1
        self.status = 'pause'
        self.generation = 1
        self.popVariance = 0
    
    def setGenesis(self):
        seed = random.randint(0, np.floor(self.width * self.heigth * 0.4))
        for i in range(0, seed):
            while True:
                cellCoord = (random.randint(0, self.width - 1), random.randint(0, self.heigth - 1))
                if not cellCoord in self.cellsAlive:
                    self.cellsAlive.add(cellCoord)
                    break
    
    def reset(self):
        self.cellsAlive.clear()
        self.deathCells.clear()
        self.bornCells.clear()
        self.neighborsChecked.clear()
        self.surface.fill(color['white'])
        self.generation = 1

    def evolve(self):
        for cell in self.cellsAlive:
            self.evaluateSector(cell)
        self.cellsAlive = self.cellsAlive.union(self.bornCells)
        self.cellsAlive = self.cellsAlive.difference(self.deathCells)
        self.neighborsChecked.clear()
        self.graphNewState()
        self.deathCells.clear()
        self.bornCells.clear()
        self.generation += 1
    
    def evaluateCell(self, cell):
        count = 0
        x_start, x_end, y_start, y_end = self.getCellRange(cell)
        for i in range(x_start, x_end):
            for j in range(y_start, y_end):
                if not (i, j) == cell and (i, j) in self.cellsAlive:
                    count += 1
        return count
    
    def evaluateSector(self, cell):
        x_start, x_end, y_start, y_end = self.getCellRange(cell)
        for i in range (x_start, x_end):
            for j in range(y_start, y_end):
                if(cell == (i, j)):
                    totalNeighbors = self.evaluateCell(cell)
                    if not self.minSurvive <= totalNeighbors <= self.maxSurvive:
                        self.deathCells.add((i, j))
                else:
                    if not (i, j) in self.neighborsChecked and not (i, j) in self.cellsAlive:
                        totalNeighbors = self.evaluateCell((i, j))
                        if self.minBorn <= totalNeighbors <= self.maxBorn:
                            self.bornCells.add((i, j))
                        self.neighborsChecked.add((i, j))

    def getCellRange(self, cell):
        if cell[0] == 0:
            x_start = 0
        else:
            x_start = cell[0] - 1
        if cell[0] == self.width - 1:
            x_end = cell[0] + 1
        else:
            x_end = cell[0] + 2
        if cell[1] == 0:
            y_start = 0
        else:
            y_start = cell[1] - 1
        if cell[1] == self.heigth - 1:
            y_end = cell[1] + 1
        else:
            y_end = cell[1] + 2
        return x_start, x_end, y_start, y_end
    
    def graphNewState(self):
        for cell in self.bornCells:
            posx = cell[0] * self.cellSize;
            posy = cell[1] * self.cellSize;
            pygame.draw.rect(self.surface, color['black'],(posx - self.view[0], posy - self.view[1], self.cellSize, self.cellSize))
        for cell in self.deathCells:
            posx = cell[0] * self.cellSize;
            posy = cell[1] * self.cellSize;
            pygame.draw.rect(self.surface, color['light blue'],(posx - self.view[0], posy - self.view[1], self.cellSize, self.cellSize))

    def relocateUniverse(self):
        self.surface.fill(color['white'])
        for cell in self.cellsAlive:
            posx = cell[0] * self.cellSize;
            posy = cell[1] * self.cellSize;
            pygame.draw.rect(self.surface, color['black'], (posx - self.view[0], posy - self.view[1], self.cellSize, self.cellSize))

class Dashboard(object):
    def __init__(self, surface):
        title = pygame.font.SysFont('Ubuntu Mono', 26)
        title2 = pygame.font.SysFont('Ubuntu Mono', 20)
        self.subtitle = pygame.font.SysFont('Ubuntu Mono', 18)
        self.surface = surface
        self.surface.fill(color['white'])
        self.generation = 1
        self.cellsAlive = 0
        self.popVariance = 0
        pygame.draw.line(self.surface, color['dark blue'], [178, 0], [178, 550], 3)
        gol = title.render('Game of life', False, (0, 0, 0))
        name = title2.render('Oscar Martinez V.', False, (0, 0, 0))
        subtitle1 = self.subtitle.render('Execution controls', False, (0, 0, 0))
        subtitle2 = self.subtitle.render('World controls', False, (0, 0, 0))
        self.data1 = self.subtitle.render('Generation: {}'.format(self.generation), False, (0, 0, 0))
        self.data2 = self.subtitle.render('Cells alive: {}'.format(self.cellsAlive), False, (0, 0, 0))
        self.data3 = self.subtitle.render('Variance: {}'.format(self.popVariance), False, (0, 0, 0))
        self.surface.blit(gol, (10, 2))
        self.surface.blit(name, (8, 24))
        self.surface.blit(subtitle1, (8, 60))
        self.surface.blit(subtitle2, (26, 228))
        self.surface.blit(self.data1, (8, 350))
        self.surface.blit(self.data2, (8, 370))
        self.surface.blit(self.data3, (8, 390))
        ShortButton(self.surface, 'Start', 5, 82)
        ShortButton(self.surface, 'Step', 90, 82)
        ShortButton(self.surface, 'Reset', 5, 122)
        ShortButton(self.surface, 'Pause', 90, 122)
        LongButton(self.surface, 'Random', 5, 250)
        LongButton(self.surface, 'Select file', 5, 290)
    
    def update(self, generation, cellsAlive, popVariance):
        self.generation = generation
        self.cellsAlive = cellsAlive
        self.popVariance = popVariance
        self.surface.fill(color['white'])
        self.data1 = self.subtitle.render('Generation: {}'.format(self.generation), False, (0, 0, 0))
        self.data2 = self.subtitle.render('Cells alive: {}'.format(self.cellsAlive), False, (0, 0, 0))
        self.data3 = self.subtitle.render('Variance: {}'.format(self.popVariance), False, (0, 0, 0))
        self.surface.blit(self.data1, (8, 350))
        self.surface.blit(self.data2, (8, 370))
        self.surface.blit(self.data3, (8, 390))

class ShortButton(object):
    def __init__(self, surface, text, pos_x, pos_y):
        font = pygame.font.SysFont('Ubuntu Mono', 18)
        string = font.render(text, False, (0, 0, 0))
        pygame.draw.rect(surface, color['dark blue'], pygame.Rect(pos_x, pos_y, 80, 30), 2)
        surface.blit(string, (pos_x + 20, pos_y + 6))

class LongButton(object):
    def __init__(self, surface, text, pos_x, pos_y):
        font = pygame.font.SysFont('Ubuntu Mono', 18)
        string = font.render(text, False, (0, 0, 0))
        pygame.draw.rect(surface, color['dark blue'], pygame.Rect(pos_x, pos_y, 165, 30), 2)
        surface.blit(string, (pos_x + 40, pos_y + 6))

class InputField(object):
    global color
    def __init__(self, sc, wPos, hPos):
        self.sc = sc
        self.wPos = wPos
        self.hPos = hPos
        self.rect_area = pygame.Rect(self.wPos, self.hPos, self.wPos + 15, self.hPos + 20)
        self.active = False
    
    def draw(self):
        if self.active:
            pygame.draw.rect(self.sc, color['dark blue'], self.rect_area, 2)
        else:
            pygame.draw.rect(self.sc, color['light blue'], self.rect_area, 2)

if __name__ == '__main__':
    print('1. Conway\'s classic game')
    print('2. Custom genesis function')
    sel = int(input('Choose one: '))
    gen = {}
    if sel == 1:
        gen['sMin'] = 2
        gen['sMax'] = 3
        gen['bMin'] = 3
        gen['bMax'] = 3
    elif sel == 2:
        gen['sMin'] = int(input('Minimum supervivence coeficient: '))
        gen['sMax'] = int(input('Maximum supervivence coeficient: '))
        gen['bMin'] = int(input('Minimum born coeficient: '))
        gen['bMax'] = int(input('Maximum born coeficient: '))
        for genValue in gen.values():
            print(genValue)
            if 0 >= genValue >= 8:
                print('One or more coeficient values are out of range')
                sys.exit()
        if gen['sMin'] > gen['sMax']:
            print('Supervivence coeficients inconsitents')
            sys.exit()
        if gen['bMin'] > gen['bMax']:
            print('Born coeficients inconsitents')
            sys.exit()
    fileName = input('FileName of universe: ')
    if fileName == '':
        MainRun()
    else:
        file1 = open(fileName, 'r') 
        Lines = file1.readlines()
        initialState = set()
        count = 0
        for line in Lines: 
            if line.strip()[0] == '.' or line.strip()[0] == '*':
                for i in range(0, len(line.strip())):
                    if line.strip()[i] == '*':
                        initialState.add((i + 100, count+ 100))
                count += 1
        MainRun(initialState)