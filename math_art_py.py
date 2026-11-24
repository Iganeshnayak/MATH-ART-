import tkinter as tk
import math
import colorsys

class MathVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Parametric Harmonics & Rose Curve Visualizer")
        self.root.geometry("1050x700")
        self.root.configure(bg="#0f111a")
        self.root.resizable(False, False)

        # Mathematical parameters
        self.k_num = 5.0
        self.k_den = 3.0
        self.petals_mod = 1.0
        self.resolution = 2500
        self.phase = 0.0
        self.animating = True
        self.hue_offset = 0.0

        self.setup_ui()
        self.animate()

    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg="#0f111a")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Left Panel: Mathematical Canvas
        canvas_frame = tk.Frame(
            main_frame, bg="#161925", highlightbackground="#292d3e", highlightthickness=2
        )
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame, width=650, height=650, bg="#0b0d14", highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Right Panel: Control Dashboard
        control_panel = tk.Frame(main_frame, width=320, bg="#161925", padx=20, pady=20)
        control_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        control_panel.pack_propagate(False)

        # Header
        tk.Label(
            control_panel, text="HARMONIC GEOMETRY", font=("Segoe UI", 14, "bold"),
            fg="#82aaff", bg="#161925"
        ).pack(anchor="w")

        tk.Label(
            control_panel, text="r(θ) = cos( (n / d) · θ ) + mod", font=("Consolas", 10),
            fg="#a6accd", bg="#161925"
        ).pack(anchor="w", pady=(2, 20))

        # Sliders
        self.num_slider = self.create_slider(
            control_panel, "Numerator (n)", 1, 20, self.k_num, self.update_params
        )
        self.den_slider = self.create_slider(
            control_panel, "Denominator (d)", 1, 20, self.k_den, self.update_params
        )
        self.mod_slider = self.create_slider(
            control_panel, "Radial Offset (mod)", 0.0, 1.5, 0.0, self.update_params, res=0.05
        )
        self.res_slider = self.create_slider(
            control_panel, "Curve Resolution", 500, 5000, self.resolution, self.update_params, res=100
        )

        # Buttons Frame
        btn_frame = tk.Frame(control_panel, bg="#161925")
        btn_frame.pack(fill=tk.X, pady=(25, 10))

        self.toggle_btn = tk.Button(
            btn_frame, text="⏸ Pause Rotation", font=("Segoe UI", 10, "bold"),
            bg="#82aaff", fg="#0f111a", activebackground="#a6c1ff",
            relief=tk.FLAT, cursor="hand2", pady=8, command=self.toggle_animation
        )
        self.toggle_btn.pack(fill=tk.X, pady=(0, 10))

        # Presets Section
        tk.Label(
            control_panel, text="MATHEMATICAL PRESETS", font=("Segoe UI", 10, "bold"),
            fg="#c792ea", bg="#161925"
        ).pack(anchor="w", pady=(15, 8))

        presets = [
            ("Maurer Rose (7/3)", 7, 3, 0.0),
            ("Quantum Star (11/4)", 11, 4, 0.25),
            ("Lotus Mandala (8/5)", 8, 5, 0.45),
            ("Hypocycloid Web (13/7)", 13, 7, 0.15),
        ]

        for name, n, d, mod in presets:
            btn = tk.Button(
                control_panel, text=name, font=("Segoe UI", 9),
                bg="#232738", fg="#eeffff", activebackground="#32374d",
                activeforeground="#82aaff", relief=tk.FLAT, cursor="hand2",
                anchor="w", padx=12, pady=6,
                command=lambda n=n, d=d, mod=mod: self.apply_preset(n, d, mod)
            )
            btn.pack(fill=tk.X, pady=3)

    def create_slider(self, parent, label_text, min_val, max_val, default, command, res=1):
        frame = tk.Frame(parent, bg="#161925")
        frame.pack(fill=tk.X, pady=8)

        tk.Label(
            frame, text=label_text, font=("Segoe UI", 9, "bold"),
            fg="#eeffff", bg="#161925"
        ).pack(anchor="w")

        slider = tk.Scale(
            frame, from_=min_val, to=max_val, orient=tk.HORIZONTAL,
            resolution=res, bg="#161925", fg="#89ddff",
            troughcolor="#232738", highlightthickness=0,
            activebackground="#82aaff", command=command
        )
        slider.set(default)
        slider.pack(fill=tk.X)
        return slider

    def apply_preset(self, n, d, mod):
        self.num_slider.set(n)
        self.den_slider.set(d)
        self.mod_slider.set(mod)
        self.update_params()

    def update_params(self, _=None):
        self.k_num = float(self.num_slider.get())
        self.k_den = float(self.den_slider.get())
        self.petals_mod = float(self.mod_slider.get())
        self.resolution = int(self.res_slider.get())
        if not self.animating:
            self.draw_curve()

    def toggle_animation(self):
        self.animating = not self.animating
        self.toggle_btn.config(
            text="⏸ Pause Rotation" if self.animating else "▶ Resume Rotation",
            bg="#82aaff" if self.animating else "#c3e88d"
        )
        if self.animating:
            self.animate()

    def draw_grid(self, cx, cy, max_r):
        # Subtle polar coordinate rings
        for factor in [0.25, 0.5, 0.75, 1.0]:
            r = max_r * factor
            self.canvas.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                outline="#1a1e2e", width=1
            )
        # Crosshairs
        self.canvas.create_line(cx - max_r, cy, cx + max_r, cy, fill="#1a1e2e")
        self.canvas.create_line(cx, cy - max_r, cx, cy + max_r, fill="#1a1e2e")

    def draw_curve(self):
        self.canvas.delete("all")
        w, h = 650, 650
        cx, cy = w / 2, h / 2
        scale = 270 / (1 + self.petals_mod)

        self.draw_grid(cx, cy, 285)

        k = self.k_num / self.k_den
        # Complete period for rational k = n/d
        max_theta = 2 * math.pi * self.k_den
        steps = self.resolution
        dt = max_theta / steps

        prev_x, prev_y = None, None
        chunk_size = 40 # Batch segments for smooth color gradient

        for i in range(steps + 1):
            theta = i * dt
            r = (math.cos(k * theta) + self.petals_mod) * scale

            # Polar to Cartesian + phase rotation
            x = cx + r * math.cos(theta + self.phase)
            y = cy + r * math.sin(theta + self.phase)

            if prev_x is not None:
                # Smooth HSV rainbow cycle along the curve
                hue = ((i / steps) + self.hue_offset) % 1.0
                rgb = colorsys.hsv_to_rgb(hue, 0.78, 1.0)
                hex_color = "#{:02x}{:02x}{:02x}".format(
                    int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255)
                )
                self.canvas.create_line(
                    prev_x, prev_y, x, y, fill=hex_color, width=1.6, smooth=True
                )

            prev_x, prev_y = x, y

    def animate(self):
        if self.animating:
            self.phase += 0.015
            self.hue_offset = (self.hue_offset + 0.003) % 1.0
            self.draw_curve()
            self.root.after(20, self.animate)

if __name__ == "__main__":
    root = tk.Tk()
    app = MathVisualizerApp(root)
    root.mainloop()