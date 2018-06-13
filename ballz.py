import pygame
import math
import random
import colorsys
from copy import copy
from vector import *

backgroundColor = (0, 0, 0)
ballColor = (255, 255, 255)

dimension = 600.0
size = [int(dimension), int(dimension)]

sizeOfOneBlock = 50.0
blockNumberInLine = int(dimension/sizeOfOneBlock)

# eg. probability(1/3)
def probability(chance):
    return random.random() <= chance
    
def text(Surface, text, pos):
    myfont = pygame.font.Font('andika.ttf', 30)
    textsurface = myfont.render(text, False, (255, 255, 255))
    Surface.blit(textsurface, pos)

# the classes used:
# Block, BlockHandler, Ball, Player

class Block():
    def __init__(self, strength, i, j):
        self.strength = strength
        self.isSpecial = False
        # i and j are numbers between 0 and blockNumberInLine-1
        self.i, self.j = i, j
        self.refreshStats()
    
    def refreshStats(self):
        if self.isSpecial:
            # white
            self.color = (255, 255, 255)
            self.strength = 1
        else:
            self.color = colorsys.hls_to_rgb((self.strength*10/360)%1, 0.5, 1)
            self.color = (int(self.color[0]*255), int(self.color[1]*255), int(self.color[2]*255))
        
    def display(self, Surface):
        pygame.draw.rect(Surface, self.color, (self.i*sizeOfOneBlock, self.j*sizeOfOneBlock, sizeOfOneBlock, sizeOfOneBlock), 0)
        # display the strength of the block
        # text(Surface, str(self.strength), (self.i*sizeOfOneBlock, self.j*sizeOfOneBlock))
        
class BlockHandler():
    def __init__(self):
        self.blockList = []
        self.blockPositions = []
        
    def resetPositionArray(self):
        self.blockPositions = []
        for block in self.blockList:
            self.blockPositions.append([block.i*sizeOfOneBlock, block.j*sizeOfOneBlock])
        
    def addNewLayer(self, level):
        # move every existing block down
        for block in self.blockList:
            block.j += 1
        # add new layer
        for i in range(blockNumberInLine):
            if probability(1/3):
                # level determines the strength of the block
                block = Block(level, i, 0)
                # this makes the blocks Special
                if probability(1/4):
                    block.isSpecial = True
                self.blockList.append(block)
                    
        # after all blocks are loaded, update the positions of the blocks
        self.resetPositionArray()
        
    def breakBrokenBlocks(self, player):
        for block in self.blockList:
            if block.strength <= 0:
                if block.isSpecial:
                    player.numberOfBalls += 1
                
                blockIndex = self.blockList.index(block)
                self.blockList.remove(block)
                self.blockPositions.pop(blockIndex)
                
    def displayBlocks(self, Surface):
        for block in self.blockList:
            block.refreshStats()
            block.display(Surface)
        
class Ball():
    def __init__(self, posVector, moveVector):
        self.posVector = posVector
        self.moveVector = moveVector
        self.radius = 10
        self.x = int(self.posVector.x)
        self.y = int(self.posVector.y)
        
    def move(self):
        self.posVector.add(self.moveVector)
        self.x = int(self.posVector.x)
        self.y = int(self.posVector.y)
        
    def display(self, Surface):
        pygame.draw.circle(Surface, ballColor, (self.x, self.y), self.radius)
        
    def changeDirection(self, tuple):
        # east
        if tuple[0]>0:
            self.moveVector.x = abs(self.moveVector.x)
        # west
        if tuple[0]<0:
            self.moveVector.x = -abs(self.moveVector.x)
        # south
        if tuple[1]>0:
            self.moveVector.y = abs(self.moveVector.y)
        # north
        if tuple[1]<0:
            self.moveVector.y = -abs(self.moveVector.y)
        
    def collisionDetect(self, blockX, blockY, blockSize, circleX, circleY, circleRadius):
        xDeflect, yDeflect = 0, 0
        
        # if in the same column
        if (circleX>=blockX) and (circleX<=(blockX+blockSize)):
            # if touching block from above or below
            distance = circleY-(blockY+0.5*blockSize)
            if abs(distance)<=(0.5*blockSize+circleRadius):
                # either 1 or -1
                if distance!=0:
                    yDeflect = distance/abs(distance)
        # if in the same row
        if (circleY>=blockY) and (circleY<=(blockY+blockSize)):
            # if touching block from left or right
            distance = circleX-(blockX+0.5*blockSize)
            if abs(distance)<=(0.5*blockSize+circleRadius):
                if distance!=0:
                    xDeflect = distance/abs(distance)
                
        return [xDeflect, yDeflect]
    
    def checkForCollisions(self, blockHandler):
        # walls
        if (self.x<=(0+self.radius)):
            # east
            self.changeDirection([1,0])
        if (self.x>=(dimension-self.radius)):
            # west
            self.changeDirection([-1,0])
        if (self.y<=(0+self.radius)):
            # south
            self.changeDirection([0,1])
            
        # blocks
        for k in range(len(blockHandler.blockList)):
            pos = blockHandler.blockPositions[k]
            collision = self.collisionDetect(pos[0], pos[1], sizeOfOneBlock, self.x, self.y, self.radius)
            self.changeDirection(collision)
            
            if collision[0] or collision[1]:
                # every time a block is hit, reduce strength by one
                blockHandler.blockList[k].strength -= 1
            
class Player():
    def __init__(self, posVector):
        self.posVector = posVector
        self.x = int(self.posVector.x)
        self.y = int(self.posVector.y)
        
        self.level = 1
        self.numberOfBalls = 1
        self.balls = []
        
        self.inPlay = False
    
    def resetBalls(self):
        self.balls = []
        for j in range(self.numberOfBalls):
            self.balls.append(Ball(copy(self.posVector), moveVector=Vector(0.0, 0.0)))
                
    def display(self, Surface):
        # possibly change color
        pygame.draw.circle(Surface, ballColor, (self.x, self.y), 20)
        
    def displayBalls(self, Surface):
        for ball in self.balls:
            ball.display(Surface)
            
    def updateBalls(self, blockHandler):
        for ball in self.balls:
            ball.move()
            ball.checkForCollisions(blockHandler)

def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("Ballz")
    done = False
    clock = pygame.time.Clock()
    
    playerPosition = Vector(dimension/2, dimension+10)
    player = Player(posVector=playerPosition)
    player.resetBalls()
    
    blockHandler = BlockHandler()
    blockHandler.addNewLayer(level=player.level)
    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                
            if event.type == pygame.KEYDOWN:
                # JFF
                if event.key == pygame.K_w:
                    blockHandler.addNewLayer(player.level)
                    
                if event.key == pygame.K_s:
                    player.inPlay = False
                    player.resetBalls()
                    player.level += 1
                    blockHandler.addNewLayer(player.level)
                    
            if event.type == pygame.MOUSEBUTTONUP and player.inPlay == False:
                player.inPlay = True
                player.resetBalls()
                mousePos = pygame.mouse.get_pos()
                player.shootVector = Vector(mousePos[0]-player.x, mousePos[1]-player.y).shortenTo(10)
                
                for ball in player.balls:
                    for i in range(player.balls.index(ball)*10):
                        ball.posVector.subtract(player.shootVector)
                    ball.moveVector = copy(player.shootVector)
                    
        # LOGIC
        player.updateBalls(blockHandler)
        for ball in player.balls:
            if ball.moveVector.y>0 and ball.posVector.y>dimension:
                player.balls.remove(ball)
        if len(player.balls) == 0:
            player.inPlay = False
            player.resetBalls()
            player.level += 1
            blockHandler.addNewLayer(player.level)
            
        blockHandler.breakBrokenBlocks(player)
        # this is how the player loses
        for block in blockHandler.blockList:
            if block.j*sizeOfOneBlock >= dimension:
                done = True
        
        # DRAW
        screen.fill(backgroundColor)
        
        blockHandler.displayBlocks(screen)
        player.displayBalls(screen)
        player.display(screen)
        
        text(screen, "SCORE: " + str(player.level), (0, 0))
        
        pygame.display.flip()
        # 60 frames per second
        clock.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    main()