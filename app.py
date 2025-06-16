
import tkinter as tk
from tkinter import colorchooser, filedialog, simpledialog
from PIL import ImageTk, Image, ImageGrab
import os
import random
import time

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Grafika Komputer - Advanced Drawing App")

        self.brush_color = "black"
        self.brush_size = 3
        self.tool = "pencil"

        self.last_x, self.last_y = None, None
        self.temp_shape = None
        self.start_time = 0

        self.icon_images = {}
        self.tool_buttons = {}
        self.tools = ["color", "pencil", "crayon", "eraser", "line", "rect", "oval", "text", "clear", "save", "undo", "redo"]

        self.undo_stack = []
        self.redo_stack = []

        self.setup_ui()

    def setup_ui(self):
        self.toolbar = tk.Frame(self.root, bd=2, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        for tool in self.tools:
            img_path = os.path.join("icons", f"{tool}.png")
            if not os.path.exists(img_path):
                img_path = os.path.join("icons", f"{tool}.jpg")
            if not os.path.exists(img_path):
                img_path = os.path.join("icons", f"{tool}.jpeg")
            if os.path.exists(img_path):
                img = Image.open(img_path).resize((32, 32))
                self.icon_images[tool] = ImageTk.PhotoImage(img)
                btn = tk.Button(self.toolbar, image=self.icon_images[tool],
                                command=lambda t=tool: self.select_tool(t))
                btn.pack(side=tk.LEFT, padx=4, pady=2)
                self.tool_buttons[tool] = btn
            else:
                btn = tk.Button(self.toolbar, text=tool.capitalize(), command=lambda t=tool: self.select_tool(t))
                btn.pack(side=tk.LEFT, padx=4, pady=2)
                self.tool_buttons[tool] = btn

        tk.Label(self.toolbar, text="Thickness:").pack(side=tk.LEFT, padx=(10, 2))
        self.slider = tk.Scale(self.toolbar, from_=1, to=20, orient=tk.HORIZONTAL, command=self.change_thickness)
        self.slider.set(self.brush_size)
        self.slider.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(self.root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset)

    def select_tool(self, tool):
        if tool == "color":
            color = colorchooser.askcolor()[1]
            if color:
                self.brush_color = color
        elif tool == "clear":
            self.canvas.delete("all")
            self.undo_stack.clear()
        elif tool == "save":
            self.save_canvas()
        elif tool == "undo":
            if self.undo_stack:
                item = self.undo_stack.pop()
                self.canvas.delete(item)
                self.redo_stack.append(item)
        elif tool == "redo":
            if self.redo_stack:
                item = self.redo_stack.pop()
                self.canvas.itemconfigure(item, state='normal')
                self.undo_stack.append(item)
        else:
            self.tool = tool
            for t, btn in self.tool_buttons.items():
                btn.config(relief=tk.SUNKEN if t == tool else tk.RAISED)

    def change_thickness(self, val):
        self.brush_size = int(val)

    def start_draw(self, event):
        self.last_x, self.last_y = event.x, event.y
        self.start_time = time.time()
        self.temp_shape = None

    def draw(self, event):
        if self.tool == "pencil":
            item = self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                           fill=self.brush_color, width=self.brush_size,
                                           capstyle=tk.ROUND, smooth=True)
            self.undo_stack.append(item)
            self.last_x, self.last_y = event.x, event.y

        elif self.tool == "crayon":
            for _ in range(3):
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
                item = self.canvas.create_line(
                    self.last_x + offset_x, self.last_y + offset_y,
                    event.x + offset_x, event.y + offset_y,
                    fill=self.brush_color, width=max(1, self.brush_size - 1),
                    capstyle=tk.ROUND, smooth=True, stipple="gray50"
                )
                self.undo_stack.append(item)
            self.last_x, self.last_y = event.x, event.y

        elif self.tool == "eraser":
            item = self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                           fill="white", width=self.brush_size,
                                           capstyle=tk.ROUND, smooth=True)
            self.undo_stack.append(item)
            self.last_x, self.last_y = event.x, event.y

        elif self.tool in ["line", "rect", "oval"]:
            if self.temp_shape:
                self.canvas.delete(self.temp_shape)
            if self.tool == "line":
                self.temp_shape = self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                                          fill=self.brush_color, width=self.brush_size)
            elif self.tool == "rect":
                self.temp_shape = self.canvas.create_rectangle(self.last_x, self.last_y, event.x, event.y,
                                                               outline=self.brush_color, width=self.brush_size)
            elif self.tool == "oval":
                self.temp_shape = self.canvas.create_oval(self.last_x, self.last_y, event.x, event.y,
                                                          outline=self.brush_color, width=self.brush_size)

    def reset(self, event):
        if self.tool in ["line", "rect", "oval"] and self.temp_shape:
            coords = self.canvas.coords(self.temp_shape)
            self.canvas.delete(self.temp_shape)
            if time.time() - self.start_time > 1:
                item = self.canvas.create_rectangle(*coords, fill=self.brush_color)
            else:
                if self.tool == "line":
                    item = self.canvas.create_line(*coords, fill=self.brush_color, width=self.brush_size)
                elif self.tool == "rect":
                    item = self.canvas.create_rectangle(*coords, outline=self.brush_color, width=self.brush_size)
                elif self.tool == "oval":
                    item = self.canvas.create_oval(*coords, outline=self.brush_color, width=self.brush_size)
            self.undo_stack.append(item)
            self.temp_shape = None
        elif self.tool == "text":
            text = simpledialog.askstring("Input Text", "Masukkan teks:")
            if text:
                item = self.canvas.create_text(event.x, event.y, text=text, fill=self.brush_color, font=("Arial", 14), anchor=tk.NW)
                self.undo_stack.append(item)

        self.last_x, self.last_y = None, None

    def save_canvas(self):
        self.root.update()
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        x1 = x + self.canvas.winfo_width()
        y1 = y + self.canvas.winfo_height()
        filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if filepath:
            ImageGrab.grab().crop((x, y, x1, y1)).save(filepath)
            print(f"Saved to {filepath}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()
