# -*- coding: utf-8 -*-

import random
import json
import Tkinter as tk
import tkMessageBox

GAMES = {
    "SNAKE": "./snakearbol.ast",
    "TETRIS": "./tetrisarbol.ast",
}

class Juego():
    def __init__(self, data):
        self.data = data
        game_name = self.data["name"].encode()
        if "snake" in game_name.lower():
            self.game = "snake"
        board_size = self.data.get("board_size", [10, 20])
        self.width = board_size[0]       
        self.height = board_size[1]
        # Grid para tetris
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height) ]
        
        
        # 25 pixels per cell
        self.cell_size = 25
        self.canvas_width = self.cell_size * self.width
        self.canvas_height = self.cell_size * self.height

        #---- GUI config
        self.root = tk.Tk()
        self.root.title("BrickScript")

        #---- Canvas del juego
        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, bg="black")
        self.canvas.pack(side=tk.LEFT)#, padx=10, pady=10)

        # Menu con la puntuación
        self.lateral_menu = tk.Frame(self.root, width=7*self.cell_size, height=self.canvas_height)
        self.lateral_menu.pack(side=tk.RIGHT, padx=10)

        self.text_title = tk.Label(self.lateral_menu, text=self.game.upper(), font=("Arial", 14, "bold"))
        self.text_title.pack(pady=10)

        self.text_title_score = tk.Label(self.lateral_menu, text="Puntuación")
        self.text_title_score.pack()

        # Actualizar texto
        self.points = 0
        self.score_var = tk.StringVar()
        self.score_var.set("0")

        self.text_score = tk.Label(self.lateral_menu, textvariable=self.score_var, font=("Arial", 20))
        self.text_score.pack()

        # Velocidad del juego
        snake_speed = self.data["snake"].get("speed", 2)

        if snake_speed <= 0:    # Evita div por 0
            snake_speed = 1
        
        self.tick_delay = int(200 / snake_speed)

        # Re/inicia el estado del juego
        self.reset_game_state()
    
        #---- Eventos
        self.root.bind('<Key>', self.handle_input)


    def reset_game_state(self):
        self.game_over = False
        self.points = 0
        self.score_var.set("0")
        self.canvas.delete("all")


        # ----- Juego Tetris ----
        # TODO: Implementar tetris


        # ----- Juego Snake ----
        if "snake" in self.game:
            start_x = self.width / 2
            start_y = self.height / 2

            # Tamaño de la serpiente
            snake_size = self.data["snake"].get("size", 3)
            self.snake = []     # Snake is an array of cells
            for i in range(snake_size):
                self.snake.append((start_x - i, start_y))
            
            self.snake_dir = (1,0)  # Default is to the right ->
            self.gen_food()

        
    def run(self):
        self.game_loop()
        self.root.mainloop()


    def game_loop(self):
        # Checks for game over
        if self.game_over:
            #self.display_game_over()
            return 

        # TODO: Case for Tetris

        # Case for Snake
        if self.game == "snake":
            self.snake_mov()

        # Dibuja el estado del juego
        self.draw()

        # Sobrepone el gameover screen
        if self.game_over:
            self.display_game_over()
            return

        # El denominador incrementa la tasa de refresco 
        # haciendolo mas rapido
        self.root.after((self.tick_delay), self.game_loop)


    def display_game_over(self):
        cw = self.canvas_width
        ch = self.canvas_height

        # Dibuja fondo para mostrar el Game Over
        self.canvas.create_rectangle(0,0, cw, ch, fill="black", stipple="gray50", tags="gameover")

        self.canvas.create_text(cw/2, ch/2 - 20, text="GAME OVER", fill="white", font=("Arial", 20, "bold"), tags="gameover")
        self.canvas.create_text(cw/2, ch/2 + 20, text="Presiona 'R' para reiniciar", fill="gray", font=("Arial", 12), tags="gameover")

        # Para que quede encima de los objetos del juego
        self.canvas.tag_raise("gameover")

    def draw(self):
        # ----- Draws for Snake ----
        # Deletes after each tick
        self.canvas.delete("snake")
        self.canvas.delete("food")

        # Get food coordinates
        fx, fy = self.food
        x1 = fx * self.cell_size
        y1 = fy * self.cell_size

        # Draw food
        self.canvas.create_rectangle(x1, y1, x1 + self.cell_size, y1 + self.cell_size, fill="#FF2222", tags="food")

        colors = ["#5CFF5C", "#2EFF2E"]

        # Draw snake
        for i, (sx, sy) in enumerate(self.snake):
            x1 = sx * self.cell_size
            y1 = sy * self.cell_size
            if i < len(colors):
                color = colors[i]
                #self.canvas.create_rectangle(x1, y1, x1 + self.cell_size, y1 + self.cell_size, fill=colors[i], tags="snake")    
            else:
                color = "green"
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size, y1 + self.cell_size, fill=color, tags="snake")


    def gen_food(self):
        # Validamos que no tenga las coor. de la serpiente
        while True:
            foodx = random.randint(0, self.width - 1)
            foody = random.randint(0, self.height - 1)
            if (foodx, foody) not in self.snake:
                self.food = (foodx, foody)
                break


    def snake_change_dir(self, direction):
        if direction == 'UP'  and self.snake_dir != (0,1):
            self.snake_dir = (0, -1)
        elif direction == 'DOWN' and self.snake_dir != (0,-1):
            self.snake_dir = (0, 1)
        elif direction == 'LEFT' and self.snake_dir != (1,0):
            self.snake_dir = (-1, 0)
        elif direction == 'RIGHT' and self.snake_dir != (-1,0):
            self.snake_dir = (1, 0)   


    def handle_input(self, event):
        key = event.keysym.upper()

        if self.game_over and key == 'R':
            self.reset_game_state()
            self.game_loop()
            return

        # TODO: Caso tetris

        controls = self.data.get("controls", {})

        action = None

        for act, k_val in controls.items():
            if k_val == key:
                actino = act
                break

        if action is None:
            if key == 'UP':
                action = 'mov_u'
            elif key == 'DOWN': 
                action = 'mov_d'
            elif key == 'LEFT': 
                action = 'mov_l'
            elif key == 'RIGHT': 
                action = 'mov_r'

        
        if self.game == "snake":
            if action == 'mov_u':
                self.snake_change_dir('UP')
            elif action == 'mov_d': 
                self.snake_change_dir('DOWN')
            elif action == 'mov_l': 
                self.snake_change_dir('LEFT')
            elif action == 'mov_r': 
                self.snake_change_dir('RIGHT')


    # ---- Logica de los juegos ----
    # ---- Snake
    def snake_mov(self):
        if not self.snake: 
            return
        headx, heady = self.snake[0]
        dirx, diry = self.snake_dir
        new_head = (headx + dirx, heady + diry)

        game_over_events = self.data["game_over"]["event"]

        if "touch_edge_screen" in game_over_events:
            # Collisions
            if not (0 <= new_head[0] < self.width and 0 <= new_head[1] < self.height):
                self.game_over = True
                return

        if "touch_itself" in game_over_events:
            if new_head in self.snake[:-1]:
                self.game_over = True
                return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            # Eat food event
            eat_actions = self.data["eat_fruit"]["action"]

            if "regenerate_fruit" in eat_actions:
                self.gen_food()

            if "increase_snake" in eat_actions:
                self.points += 1
                self.score_var.set(str(self.points))

            else:
                self.snake.pop()
        else:
            self.snake.pop()
            

if __name__ == "__main__":
    # Game data
    with open("./snakearbol.ast") as f:
        game_data = json.load(f)

    game = Juego(game_data)
    game.run()
