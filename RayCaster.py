import pygame, multiprocessing, threading
from pygame.locals import *
from math import cos, sin, pi

RAY_AMOUNT = 100

wallTextures = {
    '1': pygame.image.load('textures/wall2.png'),
    '2': pygame.image.load('textures/wall1.png'),
    '3': pygame.image.load('textures/wall3.png'),
    '4': pygame.image.load('textures/METAL.png'),
    '5': pygame.image.load('textures/MARBLOD1.png')
}

class Raycaster(object):
    def __init__(self, screen):
        self.screen = screen
        _, _, self.width, self.height = screen.get_rect()

        self.map = []
        self.blocksize = 50
        self.wallheight = 50

        self.maxdistance = 300

        self.stepSize = 3
        self.turnSize = 5

        self.player = {
           'x' : 100,
           'y' : 175,
           'fov': 60,
           'angle': 180 }


    def load_map(self, filename):
        with open(filename) as file:
            for line in file.readlines():
                self.map.append( list(line.rstrip()) )

    def drawBlock(self, x, y, id):
        tex = wallTextures[id].convert()
        tex = pygame.transform.scale(tex, (self.blocksize, self.blocksize))
        rect = tex.get_rect()
        rect = rect.move((x,y))
        self.screen.blit(tex, rect)


    def drawPlayerIcon(self, color):
        if self.player['x'] < self.width / 2:
            rect = (self.player['x'] - 2, self.player['y'] - 2, 5,5)
            self.screen.fill(color, rect )

    def castRay(self, angle):
        rads = angle * pi / 180
        dist = 0
        stepSize = 1
        stepX = stepSize * cos(rads)
        stepY = stepSize * sin(rads)

        playerPos = (self.player['x'],self.player['y'] )

        x = playerPos[0]
        y = playerPos[1]

        while True:
            dist += stepSize      

            x += stepX
            y += stepY

            i = int(x/self.blocksize)
            j = int(y/self.blocksize)

            if j < len(self.map):
                if i < len(self.map[j]):
                    if self.map[j][i] != ' ':

                        hitX = x - i*self.blocksize
                        hitY = y - j*self.blocksize

                        hit = 0

                        if 1 < hitX < self.blocksize-1:
                            if hitY < 1:
                                hit = self.blocksize - hitX
                            elif hitY >= self.blocksize-1:
                                hit = hitX
                        elif 1 < hitY < self.blocksize-1:
                            if hitX < 1:
                                hit = hitY
                            elif hitX >= self.blocksize-1:
                                hit = self.blocksize - hitY

                        tx = hit / self.blocksize

                        pygame.draw.line(self.screen,pygame.Color('white'), playerPos, (x,y))
                        return dist, self.map[j][i], tx

    def render(self):
        halfWidth = int(self.width / 2)
        halfHeight = int(self.height / 2)

        for x in range(0, halfWidth, self.blocksize):
            for y in range(0, self.height, self.blocksize):

                i = int(x/self.blocksize)
                j = int(y/self.blocksize)

                if j < len(self.map):
                    if i < len(self.map[j]):
                        if self.map[j][i] != ' ':
                            self.drawBlock(x, y, self.map[j][i])

        self.drawPlayerIcon(pygame.Color('black'))

        for column in range(RAY_AMOUNT):
            angle = self.player['angle'] - (self.player['fov'] / 2) + (self.player['fov'] * column / RAY_AMOUNT)
            dist, id, tx = self.castRay(angle)

            rayWidth = int(( 1 / RAY_AMOUNT) * halfWidth)

            startX = halfWidth + int(( (column / RAY_AMOUNT) * halfWidth))
            h = self.height / (dist * cos( (angle - self.player["angle"]) * pi / 180)) * self.wallheight
            startY = int(halfHeight - h/2)
            endY = int(halfHeight + h/2)

            color_k = (1 - min(1, dist / self.maxdistance)) * 255

            tex = wallTextures[id].convert()
            tex = pygame.transform.scale(tex, (tex.get_width() * rayWidth, int(h)))
            # tex.fill((color_k,color_k,color_k), special_flags=pygame.BLEND_MULT)
            tx = int(tx * tex.get_width())
            self.screen.blit(tex, (startX, startY), (tx,0,rayWidth,tex.get_height()))

        # Columna divisora
        for i in range(self.height):
            self.screen.set_at( (halfWidth, i), pygame.Color('black'))
            self.screen.set_at( (halfWidth+1, i), pygame.Color('black'))
            self.screen.set_at( (halfWidth-1, i), pygame.Color('black'))


width = 1000
height = 500

pygame.init()
flags = HWSURFACE and DOUBLEBUF
screen = pygame.display.set_mode((width,height), flags, 16)
screen.set_alpha(None)

pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, MOUSEBUTTONDOWN])

rCaster = Raycaster(screen)
rCaster.load_map("map.txt")

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 25)

def updateFPS():
    fps = str(int(clock.get_fps()))
    fps = font.render(fps, 1, pygame.Color("white"))
    return fps

def gaem():
    isRunning = True
    isPressing = True
    while isRunning:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                isRunning = False
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    isRunning = False
        keys = pygame.key.get_pressed()
        newX = rCaster.player['x']
        newY = rCaster.player['y']
        forward = rCaster.player['angle'] * pi / 180
        right = (rCaster.player['angle'] + 90) * pi / 180
        if keys[K_w]:
            newX += cos(forward) * rCaster.stepSize + 0.5
            newY += sin(forward) * rCaster.stepSize + 0.5
        elif keys[K_s]:
            newX -= cos(forward) * rCaster.stepSize + 0.5
            newY -= sin(forward) * rCaster.stepSize + 0.5
        elif keys[K_a]:
            newX -= cos(right) * rCaster.stepSize + 0.5
            newY -= sin(right) * rCaster.stepSize + 0.5
        elif keys[K_d]:
            newX += cos(right) * rCaster.stepSize + 0.5
            newY += sin(right) * rCaster.stepSize + 0.5
        elif keys[K_q]:
            rCaster.player['angle'] -= rCaster.turnSize + 0.5
        elif keys[K_e]:
            rCaster.player['angle'] += rCaster.turnSize + 0.5

        i = int(newX/rCaster.blocksize)
        j = int(newY/rCaster.blocksize)
        if rCaster.map[j][i] == ' ':
            rCaster.player['x'] = newX
            rCaster.player['y'] = newY

        screen.fill(pygame.Color("gray"))
        # Techo
        screen.fill(pygame.Color("saddlebrown"), (int(width / 2), 0,  int(width / 2), int(height / 2)))
        # Piso
        screen.fill(pygame.Color("dimgray"), (int(width / 2), int(height / 2),  int(width / 2), int(height / 2)))
        rCaster.render()

        #FPS
        screen.fill(pygame.Color("black"), (0,0,30,30) )
        screen.blit(updateFPS(), (0,0))
        clock.tick(100)
        pygame.display.update()

def newText(text, font):
    textSurface = font.render(text, True, pygame.Color("gray"))
    return textSurface, textSurface.get_rect()

def menu():
    flag = True

    while flag:
        for ev in pygame.event.get():
            if ev.type == pygame.MOUSEBUTTONDOWN:
                flag = False
                return True
            elif ev.type == pygame.QUIT:
                flag = False
                return False
            else:
                #screen fill
                screen.fill(pygame.Color(62, 86, 181))
                #title text
                titleFont = pygame.font.Font("pixfont.ttf", 90)
                surface, tr = newText("HoopAh's RayCaster", titleFont)
                tr.center = ((width/2),(height/2))
                screen.blit(surface, tr)
                #click to continue text
                ctcText = pygame.font.Font('pixfont.ttf', 30)
                cs, ctr = newText("CLICK ANYWHERE TO CONTINUE", ctcText)
                ctr.center = ((width/2), 300)
                screen.blit(cs, ctr)
                pygame.display.update()
                clock.tick(60)

if __name__ == '__main__':
    threads = []
    for x in range(1, multiprocessing.cpu_count()):
        thread = threading.Thread(target= pygame.display.update)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if(menu()):
    gaem()
else:
    pass

pygame.quit()
