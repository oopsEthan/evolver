import pygame
from config import MAX_X, MAX_Y, FPS, CELL_SIZE

class Window():
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((MAX_X, MAX_Y))
        self.clock = pygame.time.Clock()
    
    def run(self):
        self.is_running = True

        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False

            self.screen.fill("#5FF46F")
            self.draw_grid()
            pygame.display.flip()

            self.clock.tick(FPS)
        
        pygame.quit()
    
    def draw_grid(self):
        for x in range(0, MAX_X, CELL_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), (x, 0), (x, MAX_Y))
        for y in range(0, MAX_Y, CELL_SIZE):
            pygame.draw.line(self.screen, (40, 40, 40), (0, y), (MAX_X, y))