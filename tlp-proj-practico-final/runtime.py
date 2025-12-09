# -*- coding: utf-8 -*-

from __future__ import division
import random
import json
import sys
try:
    import Tkinter as tk
    import tkMessageBox
except ImportError:
    import tkinter as tk
    from tkinter import messagebox as tkMessageBox

# formas de piezas Tetris (matrices de rotación)
TETRIS_SHAPES = {
    'I': [
        [[1, 1, 1, 1]],
        [[1], [1], [1], [1]]
    ],
    'O': [
        [[1, 1], [1, 1]]
    ],
    'T': [
        [[0, 1, 0], [1, 1, 1]],
        [[1, 0], [1, 1], [1, 0]],
        [[1, 1, 1], [0, 1, 0]],
        [[0, 1], [1, 1], [0, 1]]
    ],
    'S': [
        [[0, 1, 1], [1, 1, 0]],
        [[1, 0], [1, 1], [0, 1]]
    ],
    'Z': [
        [[1, 1, 0], [0, 1, 1]],
        [[0, 1], [1, 1], [1, 0]]
    ],
    'L': [
        [[1, 0], [1, 0], [1, 1]],
        [[1, 1, 1], [1, 0, 0]],
        [[1, 1], [0, 1], [0, 1]],
        [[0, 0, 1], [1, 1, 1]]
    ],
    'J': [
        [[0, 1], [0, 1], [1, 1]],
        [[1, 0, 0], [1, 1, 1]],
        [[1, 1], [1, 0], [1, 0]],
        [[1, 1, 1], [0, 0, 1]]
    ]
}

SHAPE_COLORS = {
    'I': '#00FFFF', 
    'O': '#FFFF00',  
    'T': '#FF00FF',  
    'S': '#00FF00',  
    'Z': '#FF0000',  
    'L': '#FF8800',  
    'J': '#0000FF'   
}


class GameEngine(object):
    def __init__(self, ast_file):
        with open(ast_file, 'r') as f:
            self.data = json.load(f)
        
        game_name = self.data.get("name", "").lower()
        if "snake" in game_name:
            self.game_type = "snake"
        elif "tetris" in game_name:
            self.game_type = "tetris"
        else:
            print("Tipo de juego no reconocido")
            sys.exit(1)
        
        board_size = self.data.get("board_size", [20, 10])
        if self.game_type == "tetris":
            self.board_height = board_size[0]
            self.board_width = board_size[1]
        else:
            self.board_width = board_size[0]
            self.board_height = board_size[1]
        
        self.cell_size = 25
        self.board_pixel_width = self.board_width * self.cell_size
        self.board_pixel_height = self.board_height * self.cell_size
        self.sidebar_width = 200
        
        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        
        self.root = tk.Tk()
        self.root.title("BrickScript - {}".format(self.data.get("name", "Game")))
        self.root.resizable(False, False)
        
        main_frame = tk.Frame(self.root)
        main_frame.pack()
        
        self.canvas = tk.Canvas(
            main_frame,
            width=self.board_pixel_width,
            height=self.board_pixel_height,
            bg="black",
            highlightthickness=0
        )
        self.canvas.pack(side=tk.LEFT)
        
        self.sidebar = tk.Frame(main_frame, width=self.sidebar_width, bg="#1a1a1a")
        self.sidebar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.sidebar.pack_propagate(False)
        
        self.title_label = tk.Label(
            self.sidebar,
            text=self.data.get("name", "Game"),
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#1a1a1a"
        )
        self.title_label.pack(pady=10)
        
        tk.Label(
            self.sidebar,
            text="Score",
            font=("Arial", 10),
            fg="gray",
            bg="#1a1a1a"
        ).pack()
        
        self.score_var = tk.StringVar()
        self.score_var.set("0")
        self.score_label = tk.Label(
            self.sidebar,
            textvariable=self.score_var,
            font=("Arial", 24, "bold"),
            fg="white",
            bg="#1a1a1a"
        )
        self.score_label.pack()
        
        if self.game_type == "tetris":
            tk.Label(
                self.sidebar,
                text="Next",
                font=("Arial", 10),
                fg="gray",
                bg="#1a1a1a"
            ).pack(pady=(20, 5))
            
            self.next_canvas = tk.Canvas(
                self.sidebar,
                width=100,
                height=100,
                bg="#0a0a0a",
                highlightthickness=1,
                highlightbackground="gray"
            )
            self.next_canvas.pack()
        
        controls_frame = tk.Frame(self.sidebar, bg="#1a1a1a")
        controls_frame.pack(pady=20)
        
        tk.Label(
            controls_frame,
            text="Controls",
            font=("Arial", 10, "bold"),
            fg="white",
            bg="#1a1a1a"
        ).pack()
        
        controls_text = ["P - Pause", "R - Restart"]
        
        for text in controls_text:
            tk.Label(
                controls_frame,
                text=text,
                font=("Arial", 8),
                fg="gray",
                bg="#1a1a1a"
            ).pack()
        
        self.root.bind('<Key>', self.handle_input)
        self.root.bind('<KeyPress-r>', self.restart_game)
        self.root.bind('<KeyPress-R>', self.restart_game)
        self.root.bind('<KeyPress-p>', self.toggle_pause)
        self.root.bind('<KeyPress-P>', self.toggle_pause)
        
        if self.game_type == "snake":
            self.init_snake()
        elif self.game_type == "tetris":
            self.init_tetris()
        
        self.game_loop()
    
    def init_snake(self):
        snake_config = self.data.get("snake", {})
        snake_size = snake_config.get("size", 3)
        self.snake_speed = snake_config.get("speed", 2)
        
        start_x = self.board_width // 2
        start_y = self.board_height // 2
        
        self.snake = [(start_x - i, start_y) for i in range(snake_size)]
        self.snake_dir = (1, 0)
        self.next_dir = (1, 0)
        
        self.food = None
        self.generate_food()
        
        if self.snake_speed <= 0:
            self.snake_speed = 1
        self.tick_delay = int(500 / self.snake_speed)
    
    def init_tetris(self):
        self.grid = [[None for _ in range(self.board_width)] for _ in range(self.board_height)]
        
        pieces_config = self.data.get("pieces", {})
        self.piece_types = pieces_config.get("types", ["O", "I", "S", "Z", "L", "J", "T"])
        self.base_speed = pieces_config.get("speed", 1)
        spawn_pos = pieces_config.get("spawn_position", [0, 5])
        self.spawn_row = spawn_pos[0]
        self.spawn_col = spawn_pos[1]
        
        scoring = self.data.get("scoring", {})
        self.line_scores = {
            1: scoring.get("single_line", 100),
            2: scoring.get("double_line", 300),
            3: scoring.get("triple_line", 500),
            4: scoring.get("tetris", 800)
        }

        
        self.current_piece = None
        self.current_shape = None
        self.current_rotation = 0
        self.piece_x = 0
        self.piece_y = 0
        self.piece_color = "white"
        
        self.next_piece = None
        self.next_shape = None
        
        self.next_piece = random.choice(self.piece_types)
        self.next_shape = TETRIS_SHAPES[self.next_piece][0]
        self.spawn_piece()
        
        self.fall_speed = 500
        self.fast_drop = False
        
        self.schedule_fall()
    
    def generate_food(self):
        while True:
            x = random.randint(0, self.board_width - 1)
            y = random.randint(0, self.board_height - 1)
            if (x, y) not in self.snake:
                self.food = (x, y)
                break
    
    def spawn_piece(self):
        self.current_piece = self.next_piece
        self.current_shape = TETRIS_SHAPES[self.current_piece][0]
        self.current_rotation = 0
        self.piece_x = self.spawn_col
        self.piece_y = self.spawn_row
        self.piece_color = SHAPE_COLORS[self.current_piece]
        
        self.next_piece = random.choice(self.piece_types)
        self.next_shape = TETRIS_SHAPES[self.next_piece][0]
        
        if self.check_collision(self.piece_x, self.piece_y, self.current_shape):
            self.game_over = True
    
    def check_collision(self, x, y, shape):
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = x + col_idx
                    new_y = y + row_idx
                    
                    if new_x < 0 or new_x >= self.board_width:
                        return True
                    if new_y < 0 or new_y >= self.board_height:
                        return True
                    
                    if new_y >= 0 and self.grid[new_y][new_x] is not None:
                        return True
        return False
    
    def lock_piece(self):
        for row_idx, row in enumerate(self.current_shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    new_x = self.piece_x + col_idx
                    new_y = self.piece_y + row_idx
                    if 0 <= new_y < self.board_height and 0 <= new_x < self.board_width:
                        self.grid[new_y][new_x] = self.piece_color
        
        self.check_lines()
        self.spawn_piece()
    
    def check_lines(self):
        lines_cleared = 0
        row = self.board_height - 1
        
        while row >= 0:
            if all(cell is not None for cell in self.grid[row]):
                del self.grid[row]
                self.grid.insert(0, [None for _ in range(self.board_width)])
                lines_cleared += 1
            else:
                row -= 1
        
        if lines_cleared > 0:
            points = self.line_scores.get(lines_cleared, 100 * lines_cleared)
            self.score += points
            self.score_var.set(str(self.score))
    
    def rotate_piece(self):
        shapes = TETRIS_SHAPES[self.current_piece]
        new_rotation = (self.current_rotation + 1) % len(shapes)
        new_shape = shapes[new_rotation]
        
        if not self.check_collision(self.piece_x, self.piece_y, new_shape):
            self.current_rotation = new_rotation
            self.current_shape = new_shape
            return True
        
        for offset in [1, -1, 2, -2]:
            if not self.check_collision(self.piece_x + offset, self.piece_y, new_shape):
                self.piece_x += offset
                self.current_rotation = new_rotation
                self.current_shape = new_shape
                return True
        
        return False
    
    def handle_input(self, event):
        if self.game_over or self.paused:
            return
        
        controls = self.data.get("controls", {})
        key_name = event.keysym.upper()
        
        if self.game_type == "snake":
            mov_up = controls.get("mov_u", "UP")
            mov_down = controls.get("mov_d", "DOWN")
            mov_left = controls.get("mov_l", "LEFT")
            mov_right = controls.get("mov_r", "RIGHT")
            
            if key_name == mov_up:
                if self.snake_dir != (0, 1):
                    self.next_dir = (0, -1)
            elif key_name == mov_down:
                if self.snake_dir != (0, -1):
                    self.next_dir = (0, 1)
            elif key_name == mov_left:
                if self.snake_dir != (1, 0):
                    self.next_dir = (-1, 0)
            elif key_name == mov_right:
                if self.snake_dir != (-1, 0):
                    self.next_dir = (1, 0)
        
        elif self.game_type == "tetris":
            mov_left = controls.get("mov_l", "LEFT_ARROW").replace("_ARROW", "")
            mov_right = controls.get("mov_r", "RIGHT_ARROW").replace("_ARROW", "")
            rotate_key = controls.get("rotate", "UP_ARROW").replace("_ARROW", "")
            drop_key = controls.get("drop", "DOWN_ARROW").replace("_ARROW", "")
            
            if key_name == mov_left or key_name == "LEFT":
                if not self.check_collision(self.piece_x - 1, self.piece_y, self.current_shape):
                    self.piece_x -= 1
            elif key_name == mov_right or key_name == "RIGHT":
                if not self.check_collision(self.piece_x + 1, self.piece_y, self.current_shape):
                    self.piece_x += 1
            elif key_name == rotate_key or key_name == "UP":
                self.rotate_piece()
            elif key_name == drop_key or key_name == "DOWN":
                while not self.check_collision(self.piece_x, self.piece_y + 1, self.current_shape):
                    self.piece_y += 1
                self.lock_piece()
    
    def toggle_pause(self, event=None):
        self.paused = not self.paused
    
    def restart_game(self, event=None):
        if not self.game_over:
            return
        
        self.score = 0
        self.score_var.set("0")
        self.level = 1
        self.game_over = False
        self.paused = False
        
        if self.game_type == "snake":
            self.init_snake()
        elif self.game_type == "tetris":
            self.init_tetris()
    
    def update_snake(self):
        if self.game_over or self.paused:
            self.root.after(self.tick_delay, self.update_snake)
            return
        
        self.snake_dir = self.next_dir
        
        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.snake_dir
        new_head = (head_x + dir_x, head_y + dir_y)
        
        game_over_events = self.data.get("game_over", {}).get("event", [])
        
        if "touch_edge_screen" in game_over_events:
            if not (0 <= new_head[0] < self.board_width and 0 <= new_head[1] < self.board_height):
                self.game_over = True
                self.root.after(self.tick_delay, self.update_snake)
                return
        else:
            new_head = (new_head[0] % self.board_width, new_head[1] % self.board_height)
        
        if "touch_itself" in game_over_events:
            if new_head in self.snake[:-1]:
                self.game_over = True
                self.root.after(self.tick_delay, self.update_snake)
                return
        self.snake.insert(0, new_head)
        
        if new_head == self.food:
            eat_actions = self.data.get("eat_fruit", {}).get("action", [])
            
            if "increase_snake" in eat_actions:
                self.score += 10
                self.score_var.set(str(self.score))
            else:
                self.snake.pop()
            
            if "regenerate_fruit" in eat_actions:
                self.generate_food()
        else:
            self.snake.pop()
        
        self.root.after(self.tick_delay, self.update_snake)
    
    def schedule_fall(self):
        if self.game_over or self.paused:
            self.root.after(self.fall_speed, self.schedule_fall)
            return
        
        if not self.check_collision(self.piece_x, self.piece_y + 1, self.current_shape):
            self.piece_y += 1
        else:
            self.lock_piece()
        
        self.root.after(self.fall_speed, self.schedule_fall)
    
    def draw(self):
        self.canvas.delete("all")
        
        if self.game_type == "snake":
            self.draw_snake()
        elif self.game_type == "tetris":
            self.draw_tetris()
        
        if self.game_over:
            self.draw_game_over()
        
        if self.paused:
            self.draw_pause()
    
    def draw_snake(self):
        if self.food:
            fx, fy = self.food
            self.canvas.create_rectangle(
                fx * self.cell_size,
                fy * self.cell_size,
                (fx + 1) * self.cell_size - 2,
                (fy + 1) * self.cell_size - 2,
                fill="#FF2222",
                outline=""
            )
        
        for i, (sx, sy) in enumerate(self.snake):
            if i == 0:
                color = "#5CFF5C"
            else:
                color = "#2EFF2E"
            
            self.canvas.create_rectangle(
                sx * self.cell_size,
                sy * self.cell_size,
                (sx + 1) * self.cell_size - 2,
                (sy + 1) * self.cell_size - 2,
                fill=color,
                outline=""
            )
    
    def draw_tetris(self):
        for y in range(self.board_height):
            for x in range(self.board_width):
                if self.grid[y][x] is not None:
                    self.canvas.create_rectangle(
                        x * self.cell_size,
                        y * self.cell_size,
                        (x + 1) * self.cell_size - 1,
                        (y + 1) * self.cell_size - 1,
                        fill=self.grid[y][x],
                        outline="#333333"
                    )
        
        if self.current_shape:
            for row_idx, row in enumerate(self.current_shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = self.piece_x + col_idx
                        y = self.piece_y + row_idx
                        
                        if 0 <= y < self.board_height:
                            self.canvas.create_rectangle(
                                x * self.cell_size,
                                y * self.cell_size,
                                (x + 1) * self.cell_size - 1,
                                (y + 1) * self.cell_size - 1,
                                fill=self.piece_color,
                                outline="white"
                            )
        
        for x in range(self.board_width + 1):
            self.canvas.create_line(
                x * self.cell_size, 0,
                x * self.cell_size, self.board_pixel_height,
                fill="#222222"
            )
        for y in range(self.board_height + 1):
            self.canvas.create_line(
                0, y * self.cell_size,
                self.board_pixel_width, y * self.cell_size,
                fill="#222222"
            )
        
        self.draw_next_piece()
    
    def draw_next_piece(self):
        if not hasattr(self, 'next_canvas'):
            return
        
        self.next_canvas.delete("all")
        
        if self.next_shape:
            next_color = SHAPE_COLORS[self.next_piece]
            cell_size = 20
            
            shape_width = len(self.next_shape[0]) * cell_size
            shape_height = len(self.next_shape) * cell_size
            offset_x = (100 - shape_width) // 2
            offset_y = (100 - shape_height) // 2
            
            for row_idx, row in enumerate(self.next_shape):
                for col_idx, cell in enumerate(row):
                    if cell:
                        x = offset_x + col_idx * cell_size
                        y = offset_y + row_idx * cell_size
                        
                        self.next_canvas.create_rectangle(
                            x, y,
                            x + cell_size - 1,
                            y + cell_size - 1,
                            fill=next_color,
                            outline="white"
                        )
    
    def draw_game_over(self):
        self.canvas.create_rectangle(
            0, 0,
            self.board_pixel_width,
            self.board_pixel_height,
            fill="black",
            stipple="gray50"
        )
        
        self.canvas.create_text(
            self.board_pixel_width // 2,
            self.board_pixel_height // 2 - 30,
            text="GAME OVER",
            fill="red",
            font=("Arial", 24, "bold")
        )
        
        self.canvas.create_text(
            self.board_pixel_width // 2,
            self.board_pixel_height // 2 + 20,
            text="Press R to restart",
            fill="white",
            font=("Arial", 12)
        )
    
    def draw_pause(self):
        self.canvas.create_rectangle(
            0, 0,
            self.board_pixel_width,
            self.board_pixel_height,
            fill="black",
            stipple="gray50"
        )
        
        self.canvas.create_text(
            self.board_pixel_width // 2,
            self.board_pixel_height // 2,
            text="PAUSED",
            fill="yellow",
            font=("Arial", 24, "bold")
        )
    
    def game_loop(self):
        self.draw()
        
        self.root.after(16, self.game_loop)
        
        if self.game_type == "snake" and not hasattr(self, '_snake_started'):
            self._snake_started = True
            self.update_snake()
    
    def run(self):
        self.root.mainloop()


def main():
    if len(sys.argv) > 1:
        ast_file = sys.argv[1]
    else:
        print("Uso: python runtime-test.py <archivo.ast>")
        print("Ejemplo: python runtime-test.py snakearbol.ast")
        print("\nSelecciona un juego:")
        print("1. Snake")
        print("2. Tetris")
        
        try:
            choice = raw_input("Opcion (1-2): ").strip()
        except NameError:
            choice = input("Opcion (1-2): ").strip()
        
        if choice == "1":
            ast_file = "./snakearbol.ast"
        elif choice == "2":
            ast_file = "./tetrisarbol.ast"
        else:
            print("Opcion invalida")
            return
    
    try:
        game = GameEngine(ast_file)
        game.run()
    except Exception as e:
        print("Error: {}".format(e))
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()