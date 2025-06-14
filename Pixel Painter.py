import tkinter as tk
from tkinter import colorchooser, filedialog
from PIL import Image, ImageDraw

# Constants
CANVAS_SIZE = 400
GRID_SIZE = 20
PIXEL_SIZE = CANVAS_SIZE // GRID_SIZE
PALETTE_COLORS = ['red', 'green', 'blue', 'yellow', 'black', 'white']
PALETTE_BOX_SIZE = 20

class PixelPainter:
    def __init__(self, root):
        self.root = root
        self.root.title("Pixel Painter")

        self.canvas = tk.Canvas(root, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white")
        self.canvas.grid(row=1, column=0, columnspan=6)

        self.color = 'black'
        self.brush_size = 1
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.undo_stack = []
        self.redo_stack = []

        self.create_palette()
        self.create_buttons()
        self.draw_grid()
        self.canvas.bind("<Button-1>", self.paint)

    def create_palette(self):
        for i, color in enumerate(PALETTE_COLORS):
            btn = tk.Button(self.root, bg=color, width=2, command=lambda c=color: self.set_color(c))
            btn.grid(row=0, column=i)
        custom_color_btn = tk.Button(self.root, text="Custom", command=self.choose_color)
        custom_color_btn.grid(row=0, column=len(PALETTE_COLORS))

    def create_buttons(self):
        tk.Button(self.root, text="Save", command=self.save_image).grid(row=2, column=0)
        tk.Button(self.root, text="Load", command=self.load_image).grid(row=2, column=1)
        tk.Button(self.root, text="Eraser", command=lambda: self.set_color("white")).grid(row=2, column=2)
        tk.Button(self.root, text="Undo", command=self.undo).grid(row=2, column=3)
        tk.Button(self.root, text="Redo", command=self.redo).grid(row=2, column=4)

        brush_menu = tk.Menubutton(self.root, text="Brush Size", relief="raised")
        menu = tk.Menu(brush_menu, tearoff=0)
        for size in [1, 2, 3]:
            menu.add_command(label=str(size), command=lambda s=size: self.set_brush_size(s))
        brush_menu.configure(menu=menu)
        brush_menu.grid(row=2, column=5)

    def set_color(self, color):
        self.color = color

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.set_color(color)

    def set_brush_size(self, size):
        self.brush_size = size

    def draw_grid(self):
        for i in range(GRID_SIZE):
            x = i * PIXEL_SIZE
            self.canvas.create_line(x, 0, x, CANVAS_SIZE, fill='lightgray')
            self.canvas.create_line(0, x, CANVAS_SIZE, x, fill='lightgray')

    def paint(self, event):
        col = event.x // PIXEL_SIZE
        row = event.y // PIXEL_SIZE
        pixels = []
        for r in range(row, min(row + self.brush_size, GRID_SIZE)):
            for c in range(col, min(col + self.brush_size, GRID_SIZE)):
                if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                    old_color = self.grid[r][c]
                    self.grid[r][c] = self.color
                    self.draw_pixel(r, c, self.color)
                    pixels.append((r, c, old_color))
        self.undo_stack.append(pixels)
        self.redo_stack.clear()  # Clear redo stack after new action

    def draw_pixel(self, row, col, color):
        x1 = col * PIXEL_SIZE
        y1 = row * PIXEL_SIZE
        x2 = x1 + PIXEL_SIZE
        y2 = y1 + PIXEL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='lightgray')

    def undo(self):
        if self.undo_stack:
            action = self.undo_stack.pop()
            redo_action = []
            for row, col, old_color in action:
                new_color = self.grid[row][col]
                self.grid[row][col] = old_color
                self.draw_pixel(row, col, old_color)
                redo_action.append((row, col, new_color))
            self.redo_stack.append(redo_action)

    def redo(self):
        if self.redo_stack:
            action = self.redo_stack.pop()
            undo_action = []
            for row, col, new_color in action:
                old_color = self.grid[row][col]
                self.grid[row][col] = new_color
                self.draw_pixel(row, col, new_color)
                undo_action.append((row, col, old_color))
            self.undo_stack.append(undo_action)

    def save_image(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".png")
        if not filepath:
            return
        img = Image.new("RGB", (GRID_SIZE, GRID_SIZE), "white")
        draw = ImageDraw.Draw(img)
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                color = self.grid[r][c] if self.grid[r][c] else "white"
                draw.point((c, r), fill=color)
        img = img.resize((CANVAS_SIZE, CANVAS_SIZE), resample=Image.NEAREST)
        img.save(filepath)
        print("Saved to", filepath)

    def load_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
        if not filepath:
            return
        img = Image.open(filepath).resize((GRID_SIZE, GRID_SIZE))
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                color = '#%02x%02x%02x' % img.getpixel((c, r))
                self.grid[r][c] = color
                self.draw_pixel(r, c, color)
        print("Loaded", filepath)

if __name__ == "__main__":
    root = tk.Tk()
    app = PixelPainter(root)
    root.mainloop()
