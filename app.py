import os
import sqlite3
import tkinter as tk
import urllib.request
import threading
from io import BytesIO
from PIL import Image, ImageTk
import customtkinter as ctk

DB_NAME = "quindiohost.db"

# Set theme and color palette
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  # Use blue as standard, we will customize elements

# Custom palette for telemetry look
COLOR_BG = "#0B0C10"        # Very dark black/blue
COLOR_PANEL = "#1F2833"     # Dark slate
COLOR_BORDER = "#45A29E"    # Cyan/teal border
COLOR_ACCENT = "#66FCF1"    # Bright cyan glowing
COLOR_EXCELLENT = "#00FF66" # Glowing green
COLOR_WARNING = "#FFA500"   # Glowing orange
COLOR_ALERT = "#FF3366"     # Glowing red
COLOR_TEXT_MUTED = "#8B9BB4"

class QuindioHostApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("QUINDÍOHOST BENCHMARKER // TELEMETRÍA DE PRECIOS V1.0")
        self.geometry("1300x820")
        self.configure(fg_color=COLOR_BG)
        
        # Current active owned listing
        self.selected_property_id = None
        self.category_filter = "All"
        self.image_cache = {}
        
        # Setup UI layout
        self.create_header()
        self.create_main_layout()
        
        # Load initial data
        self.refresh_all_data()

    def create_header(self):
        # Top bar with a terminal/industrial look
        header_frame = ctk.CTkFrame(self, height=60, fg_color=COLOR_PANEL, corner_radius=0, border_width=1, border_color=COLOR_BORDER)
        header_frame.pack(fill="x", side="top", padx=10, pady=(10, 0))
        
        # System title
        title_label = ctk.CTkLabel(
            header_frame, 
            text="▲ QUINDÍOHOST // CORE BENCHMARK ENGINE", 
            font=("Consolas", 18, "bold"), 
            text_color=COLOR_ACCENT
        )
        title_label.pack(side="left", padx=20)
        
        # Category Selector (Toggle Switch Hub)
        self.filter_var = tk.StringVar(value="All")
        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.pack(side="right", padx=20)
        
        lbl_filter = ctk.CTkLabel(filter_frame, text="SECTOR FILTER:", font=("Consolas", 12), text_color=COLOR_TEXT_MUTED)
        lbl_filter.pack(side="left", padx=10)
        
        for cat in ["All", "design", "cabins", "trending"]:
            btn = ctk.CTkRadioButton(
                filter_frame, 
                text=cat.upper(), 
                value=cat, 
                variable=self.filter_var,
                command=self.on_filter_changed,
                font=("Consolas", 11, "bold"),
                text_color=COLOR_ACCENT,
                fg_color=COLOR_BORDER,
                hover_color=COLOR_ACCENT
            )
            btn.pack(side="left", padx=10)

    def create_main_layout(self):
        # Container for layout
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Col 1: Owned Portfolio List (Left)
        self.left_panel = ctk.CTkFrame(self.body_frame, width=320, fg_color=COLOR_PANEL, border_width=1, border_color=COLOR_BORDER)
        self.left_panel.pack(side="left", fill="both", expand=False, padx=(0, 5))
        self.left_panel.pack_propagate(False)
        
        lbl_portfolio = ctk.CTkLabel(self.left_panel, text="[INVENTARIO CAFETERO STAYS]", font=("Consolas", 14, "bold"), text_color=COLOR_ACCENT)
        lbl_portfolio.pack(pady=10)
        
        self.scroll_portfolio = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.scroll_portfolio.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Col 2: Telemetry + Price Simulator (Center)
        self.center_panel = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        self.center_panel.pack(side="left", fill="both", expand=True, padx=5)
        
        # Center Top: Telemetry overview meters
        self.metrics_panel = ctk.CTkFrame(self.center_panel, height=130, fg_color=COLOR_PANEL, border_width=1, border_color=COLOR_BORDER)
        self.metrics_panel.pack(fill="x", side="top", pady=(0, 5))
        self.metrics_panel.pack_propagate(False)
        self.setup_global_metrics()
        
        # Center Bottom: Main Simulator panel
        self.simulator_panel = ctk.CTkFrame(self.center_panel, fg_color=COLOR_PANEL, border_width=1, border_color=COLOR_BORDER)
        self.simulator_panel.pack(fill="both", expand=True, pady=5)
        self.setup_simulator_view()
        
        # Col 3: Competitor Benchmark Grid (Right)
        self.right_panel = ctk.CTkFrame(self.body_frame, width=350, fg_color=COLOR_PANEL, border_width=1, border_color=COLOR_BORDER)
        self.right_panel.pack(side="right", fill="both", expand=False, padx=(5, 0))
        self.right_panel.pack_propagate(False)
        
        lbl_comps = ctk.CTkLabel(self.right_panel, text="[SISTEMA DE BENCHMARK AIRBNB]", font=("Consolas", 14, "bold"), text_color=COLOR_ACCENT)
        lbl_comps.pack(pady=10)
        
        self.scroll_competitors = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        self.scroll_competitors.pack(fill="both", expand=True, padx=5, pady=5)

    def setup_global_metrics(self):
        # Digital readout meters
        metrics_title = ctk.CTkLabel(self.metrics_panel, text="[ TELEMETRÍA GLOBAL DE PORTAFOLIO ]", font=("Consolas", 11), text_color=COLOR_TEXT_MUTED)
        metrics_title.pack(anchor="w", padx=10, pady=5)
        
        container = ctk.CTkFrame(self.metrics_panel, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.meter_total = self.create_meter(container, "PROPIEDADES", "00", 0)
        self.meter_avg_price = self.create_meter(container, "PROM. TARIFA", "$0.00", 1)
        self.meter_ratio = self.create_meter(container, "COMPETITIVIDAD", "00.0%", 2)
        self.meter_alerts = self.create_meter(container, "ALERTAS CRÍTICAS", "00", 3)

    def create_meter(self, parent, label, value, col):
        frame = ctk.CTkFrame(parent, fg_color=COLOR_BG, border_width=1, border_color="#333333", width=140, height=80)
        frame.grid(row=0, column=col, padx=10, sticky="nsew")
        parent.grid_columnconfigure(col, weight=1)
        frame.pack_propagate(False)
        
        lbl = ctk.CTkLabel(frame, text=label, font=("Consolas", 9), text_color=COLOR_TEXT_MUTED)
        lbl.pack(pady=(5, 0))
        
        val_lbl = ctk.CTkLabel(frame, text=value, font=("Consolas", 20, "bold"), text_color=COLOR_ACCENT)
        val_lbl.pack(pady=5)
        
        # A tiny neon indicator strip
        strip = ctk.CTkFrame(frame, height=3, fg_color=COLOR_ACCENT)
        strip.pack(fill="x", side="bottom")
        
        return val_lbl

    def setup_simulator_view(self):
        self.sim_container = ctk.CTkFrame(self.simulator_panel, fg_color="transparent")
        self.sim_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Message if no property is selected
        self.lbl_no_selection = ctk.CTkLabel(
            self.sim_container,
            text="▲ ACCESO REQUERIDO // SELECCIONE UN NODO DEL INVENTARIO",
            font=("Consolas", 14),
            text_color=COLOR_BORDER
        )
        self.lbl_no_selection.pack(expand=True)
        
        # Real layout of simulator (initially hidden)
        self.sim_content_frame = ctk.CTkFrame(self.sim_container, fg_color="transparent")
        
        # Row 1: Header Info & Status LED
        info_header = ctk.CTkFrame(self.sim_content_frame, fg_color="transparent")
        info_header.pack(fill="x", pady=(0, 10))
        
        self.lbl_sim_name = ctk.CTkLabel(info_header, text="SKY TOP LOFTS", font=("Consolas", 18, "bold"), text_color=COLOR_ACCENT)
        self.lbl_sim_name.pack(side="left")
        
        # STATUS INDICATOR BOX
        self.status_box = ctk.CTkFrame(info_header, width=150, height=35, fg_color=COLOR_BG, border_width=1, border_color=COLOR_BORDER)
        self.status_box.pack(side="right")
        self.status_box.pack_propagate(False)
        
        self.lbl_status_led = ctk.CTkLabel(self.status_box, text="EXCELLENT", font=("Consolas", 12, "bold"), text_color=COLOR_EXCELLENT)
        self.lbl_status_led.pack(expand=True)

        # Row 2: Vector wireframe canvas (representing 3D CAD draft) and Specs
        middle_row = ctk.CTkFrame(self.sim_content_frame, fg_color="transparent")
        middle_row.pack(fill="both", expand=True, pady=10)
        
        # Blueprint Wireframe Canvas
        self.canvas_blueprint = tk.Canvas(middle_row, width=280, height=180, bg=COLOR_BG, highlightthickness=1, highlightbackground=COLOR_BORDER)
        self.canvas_blueprint.pack(side="left", padx=(0, 15))
        self.draw_vector_blueprint("design")
        
        # Specs Form
        specs_frame = ctk.CTkFrame(middle_row, fg_color="transparent")
        specs_frame.pack(side="left", fill="both", expand=True)
        
        self.create_spec_row(specs_frame, "ZONA:", "self.lbl_spec_zona", 0)
        self.create_spec_row(specs_frame, "CATEGORÍA:", "self.lbl_spec_cat", 1)
        self.create_spec_row(specs_frame, "CALIFICACIÓN:", "self.lbl_spec_rating", 2)
        self.create_spec_row(specs_frame, "COMPETENCIA PROMEDIO:", "self.lbl_spec_avg_comp", 3)
        
        # Row 3: REACTOR SLIDER Control
        control_frame = ctk.CTkFrame(self.sim_content_frame, fg_color=COLOR_BG, border_width=1, border_color=COLOR_BORDER)
        control_frame.pack(fill="x", pady=10, padx=2)
        
        lbl_reactor = ctk.CTkLabel(control_frame, text="CONTROL DE REACTOR - TARIFA BASE (COP)", font=("Consolas", 12, "bold"), text_color=COLOR_ACCENT)
        lbl_reactor.pack(pady=5)
        
        slider_row = ctk.CTkFrame(control_frame, fg_color="transparent")
        slider_row.pack(fill="x", padx=10, pady=5)
        
        self.slider_price = ctk.CTkSlider(
            control_frame,
            from_=50000,
            to=500000,
            number_of_steps=90,
            command=self.on_slider_move,
            button_color=COLOR_ACCENT,
            progress_color=COLOR_BORDER
        )
        self.slider_price.pack(fill="x", padx=20, pady=10)
        
        # Price Display Label
        self.lbl_sim_price = ctk.CTkLabel(control_frame, text="$280,000 COP", font=("Consolas", 24, "bold"), text_color=COLOR_EXCELLENT)
        self.lbl_sim_price.pack(pady=5)
        
        # Row 4: CRUD Form Operations
        crud_frame = ctk.CTkFrame(self.sim_content_frame, fg_color="transparent")
        crud_frame.pack(fill="x", pady=10)
        
        btn_update = ctk.CTkButton(
            crud_frame, 
            text="ACTUALIZAR TARIFA EN DB", 
            fg_color=COLOR_BORDER,
            hover_color=COLOR_ACCENT,
            text_color=COLOR_BG,
            font=("Consolas", 12, "bold"),
            command=self.update_property_price
        )
        btn_update.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        btn_edit = ctk.CTkButton(
            crud_frame, 
            text="EDITAR PROPIEDAD", 
            fg_color=COLOR_PANEL,
            border_width=1,
            border_color=COLOR_BORDER,
            hover_color="#2c3e50",
            font=("Consolas", 12, "bold"),
            command=self.open_edit_dialog
        )
        btn_edit.pack(side="left", fill="x", expand=True, padx=5)
        
        btn_delete = ctk.CTkButton(
            crud_frame, 
            text="ELIMINAR PROPIEDAD", 
            fg_color="#3a111a",
            hover_color=COLOR_ALERT,
            font=("Consolas", 12, "bold"),
            command=self.delete_property
        )
        btn_delete.pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Add property button at bottom
        btn_add = ctk.CTkButton(
            self.sim_content_frame, 
            text="+ REGISTRAR NUEVA PROPIEDAD PROPIA (CRUD)", 
            fg_color="#006622",
            hover_color=COLOR_EXCELLENT,
            font=("Consolas", 12, "bold"),
            command=self.open_add_dialog
        )
        btn_add.pack(fill="x", pady=(15, 0))

    def create_spec_row(self, parent, label_text, widget_var_name, row):
        r_frame = ctk.CTkFrame(parent, fg_color="transparent")
        r_frame.pack(fill="x", pady=4)
        
        lbl = ctk.CTkLabel(r_frame, text=label_text, font=("Consolas", 11), text_color=COLOR_TEXT_MUTED, width=160, anchor="w")
        lbl.pack(side="left")
        
        val = ctk.CTkLabel(r_frame, text="--", font=("Consolas", 12, "bold"), text_color=COLOR_ACCENT)
        val.pack(side="left")
        
        # Set dynamic attribute on class so we can update it
        exec(f"{widget_var_name} = val")

    def draw_vector_blueprint(self, category):
        self.canvas_blueprint.delete("all")
        
        # Draw background grid lines (CRT monitor style)
        for x in range(0, 280, 20):
            self.canvas_blueprint.create_line(x, 0, x, 180, fill="#122c2a", width=1)
        for y in range(0, 180, 20):
            self.canvas_blueprint.create_line(0, y, 280, y, fill="#122c2a", width=1)
            
        # Draw wireframe house schematic based on category
        color = COLOR_ACCENT
        if category == "cabins":
            # A cabin with high pitched roof
            self.canvas_blueprint.create_polygon(140, 30, 70, 90, 210, 90, outline=color, fill="", width=2)
            self.canvas_blueprint.create_rectangle(80, 90, 200, 160, outline=color, fill="", width=2)
            self.canvas_blueprint.create_rectangle(125, 110, 155, 160, outline=color, fill="", width=2)
            self.canvas_blueprint.create_oval(145, 135, 150, 140, outline=color, fill="", width=1)
            self.canvas_blueprint.create_rectangle(95, 105, 115, 125, outline=color, fill="", width=1)
            self.canvas_blueprint.create_rectangle(165, 105, 185, 125, outline=color, fill="", width=1)
            
            # Diagonal structural lines
            self.canvas_blueprint.create_line(70, 90, 200, 160, fill="#1c4e4b", dash=(3,3))
            self.canvas_blueprint.create_line(210, 90, 80, 160, fill="#1c4e4b", dash=(3,3))
        elif category == "design":
            # A modern angular loft
            self.canvas_blueprint.create_polygon(60, 40, 160, 20, 220, 60, 60, 60, outline=color, fill="", width=2)
            self.canvas_blueprint.create_rectangle(60, 60, 220, 150, outline=color, fill="", width=2)
            # Big floor to ceiling glass
            self.canvas_blueprint.create_rectangle(70, 70, 130, 140, outline=color, fill="", width=1)
            self.canvas_blueprint.create_rectangle(140, 70, 210, 120, outline=color, fill="", width=1)
            self.canvas_blueprint.create_line(70, 70, 130, 140, fill="#1c4e4b", dash=(3,3))
            # Text layout overlay
            self.canvas_blueprint.create_text(140, 165, text="MODEL // LOFT-D3D", fill="#1c4e4b", font=("Consolas", 8))
        else:
            # Trending generic flat
            self.canvas_blueprint.create_rectangle(70, 40, 210, 140, outline=color, fill="", width=2)
            self.canvas_blueprint.create_rectangle(80, 50, 135, 90, outline=color, fill="", width=1)
            self.canvas_blueprint.create_rectangle(145, 50, 200, 90, outline=color, fill="", width=1)
            self.canvas_blueprint.create_rectangle(110, 100, 170, 140, outline=color, fill="", width=1)
            self.canvas_blueprint.create_line(70, 40, 210, 140, fill="#1c4e4b", dash=(3,3))

        # Glowing circles at structural nodes
        self.canvas_blueprint.create_oval(138, 28, 142, 32, outline=COLOR_EXCELLENT, fill=COLOR_EXCELLENT)
        self.canvas_blueprint.create_oval(68, 88, 72, 92, outline=COLOR_EXCELLENT, fill=COLOR_EXCELLENT)
        self.canvas_blueprint.create_oval(208, 88, 212, 92, outline=COLOR_EXCELLENT, fill=COLOR_EXCELLENT)

    # DATA MANIPULATION & INTERACTION LÓGICA
    def run_query(self, query, params=()):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(query, params)
        res = cursor.fetchall()
        conn.commit()
        conn.close()
        return res

    def refresh_all_data(self):
        # Read owned properties
        cat_filter = self.filter_var.get()
        if cat_filter == "All":
            owned_query = "SELECT id_propiedad, nombre_alojamiento, categoria_propia, precio_actual_cop, calificacion_interna, estado_competitivo, zona_armenia, url_imagen_cover FROM alojamientos_propios ORDER BY id_propiedad ASC"
            owned_data = self.run_query(owned_query)
        else:
            owned_query = "SELECT id_propiedad, nombre_alojamiento, categoria_propia, precio_actual_cop, calificacion_interna, estado_competitivo, zona_armenia, url_imagen_cover FROM alojamientos_propios WHERE categoria_propia = ? ORDER BY id_propiedad ASC"
            owned_data = self.run_query(owned_query, (cat_filter,))
            
        # Clear owned portfolio frame
        for child in self.scroll_portfolio.winfo_children():
            child.destroy()
            
        # Re-populate owned list with retro panels
        for row in owned_data:
            prop_id, name, cat, price, rating, status, zone, img = row
            
            card = ctk.CTkFrame(self.scroll_portfolio, fg_color="#181e28", border_width=1, border_color="#334455", height=90)
            card.pack(fill="x", pady=5)
            card.pack_propagate(False)
            
            # Left LED status line
            led_color = COLOR_EXCELLENT
            if status == "Precio Alto":
                led_color = COLOR_WARNING
            elif status in ["Alerta de Reseñas", "Crítico"]:
                led_color = COLOR_ALERT
                
            led = ctk.CTkFrame(card, width=6, fg_color=led_color)
            led.pack(side="left", fill="y")
            
            # Content
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
            
            lbl_name = ctk.CTkLabel(info_frame, text=name, font=("Consolas", 12, "bold"), text_color="#FFFFFF", anchor="w")
            lbl_name.pack(fill="x")
            
            lbl_sub = ctk.CTkLabel(
                info_frame, 
                text=f"{cat.upper()} // {zone} // COP {price:,}", 
                font=("Consolas", 10), 
                text_color=COLOR_TEXT_MUTED, 
                anchor="w"
            )
            lbl_sub.pack(fill="x")
            
            # Configure hover and click events for the entire box (including internal raw widgets)
            def on_click(event, pid=prop_id):
                self.select_property(pid)
                
            def on_enter(event):
                card.configure(border_color=COLOR_ACCENT)
                
            def on_leave(event):
                card.configure(border_color="#334455")
                
            for w in [card, led, info_frame, lbl_name, lbl_sub]:
                w.bind("<Button-1>", on_click)
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
                
                # Bind underlying tkinter primitives for proper event targeting
                if hasattr(w, "_canvas") and w._canvas:
                    w._canvas.bind("<Button-1>", on_click)
                    w._canvas.bind("<Enter>", on_enter)
                    w._canvas.bind("<Leave>", on_leave)
                if hasattr(w, "_label") and w._label:
                    w._label.bind("<Button-1>", on_click)
                    w._label.bind("<Enter>", on_enter)
                    w._label.bind("<Leave>", on_leave)

            
        # Refresh Global Metrics
        self.update_global_metrics_display()
        
        # If active selected property is not visible anymore, clear simulator
        if self.selected_property_id:
            # check if still exists
            check = self.run_query("SELECT count(*) FROM alojamientos_propios WHERE id_propiedad = ?", (self.selected_property_id,))
            if check[0][0] == 0:
                self.selected_property_id = None
                self.sim_content_frame.pack_forget()
                self.lbl_no_selection.pack(expand=True)
            else:
                self.select_property(self.selected_property_id)

    def on_filter_changed(self):
        self.refresh_all_data()

    def update_global_metrics_display(self):
        # Total listings
        c_tot = self.run_query("SELECT count(*), avg(precio_actual_cop) FROM alojamientos_propios")
        tot = c_tot[0][0] or 0
        avg = c_tot[0][1] or 0
        
        # Competitiveness Ratio (Excellent or Competitivo vs total)
        c_comp = self.run_query("SELECT count(*) FROM alojamientos_propios WHERE estado_competitivo = 'Excellent'")
        comp = c_comp[0][0] or 0
        ratio = (comp / tot * 100) if tot > 0 else 0
        
        # Critical alerts
        c_alert = self.run_query("SELECT count(*) FROM alojamientos_propios WHERE estado_competitivo IN ('Alerta de Reseñas', 'Crítico')")
        alerts = c_alert[0][0] or 0
        
        self.meter_total.configure(text=f"{tot:02d}")
        self.meter_avg_price.configure(text=f"${int(avg):,}")
        self.meter_ratio.configure(text=f"{ratio:.1f}%")
        self.meter_alerts.configure(text=f"{alerts:02d}")
        
        # Dynamic warning on alerts
        if alerts > 0:
            self.meter_alerts.configure(text_color=COLOR_ALERT)
        else:
            self.meter_alerts.configure(text_color=COLOR_ACCENT)

    def select_property(self, property_id):
        self.selected_property_id = property_id
        
        # Query property
        data = self.run_query("SELECT nombre_alojamiento, categoria_propia, precio_actual_cop, calificacion_interna, estado_competitivo, zona_armenia FROM alojamientos_propios WHERE id_propiedad = ?", (property_id,))
        if not data:
            return
            
        name, cat, price, rating, status, zone = data[0]
        
        # Calculate Competitors Average for this category
        avg_comp_data = self.run_query("SELECT avg(precio_base_cop) FROM competidores_scraper WHERE categoria_scraper = ?", (cat,))
        avg_comp = int(avg_comp_data[0][0]) if avg_comp_data[0][0] else 160000
        
        # Show Simulator panel content
        self.lbl_no_selection.pack_forget()
        self.sim_content_frame.pack(fill="both", expand=True)
        
        # Update simulator values
        self.lbl_sim_name.configure(text=name.upper())
        self.lbl_spec_zona.configure(text=zone)
        self.lbl_spec_cat.configure(text=cat.upper())
        self.lbl_spec_rating.configure(text=f"{rating:.2f} ★")
        self.lbl_spec_avg_comp.configure(text=f"COP {avg_comp:,}")
        
        # Update Slider & Price display
        self.slider_price.set(price)
        self.lbl_sim_price.configure(text=f"COP {price:,}")
        
        # Update LED Status Badge
        self.update_status_led_badge(status)
        
        # Re-draw vector CAD blueprint based on category
        self.draw_vector_blueprint(cat)
        
        # Load linked competitor node lists on right
        self.load_competitor_nodes(cat, avg_comp)

    def on_slider_move(self, value):
        price = int(value)
        self.lbl_sim_price.configure(text=f"COP {price:,}")
        
        # Recalculate status in real-time dynamically (< 2s) without DB write
        cat = self.lbl_spec_cat.cget("text").lower()
        rating_str = self.lbl_spec_rating.cget("text").replace(" ★", "")
        rating = float(rating_str)
        
        avg_comp_data = self.run_query("SELECT avg(precio_base_cop) FROM competidores_scraper WHERE categoria_scraper = ?", (cat,))
        avg_comp = int(avg_comp_data[0][0]) if avg_comp_data[0][0] else 160000
        
        # Temp local status formula
        if rating < 4.5 and price > avg_comp * 1.15:
            new_status = "Crítico"
        elif rating < 4.5:
            new_status = "Alerta de Reseñas"
        elif price > avg_comp * 1.15:
            new_status = "Precio Alto"
        else:
            new_status = "Excellent"
            
        self.update_status_led_badge(new_status)

    def update_status_led_badge(self, status):
        self.lbl_status_led.configure(text=status.upper())
        if status == "Excellent":
            self.lbl_status_led.configure(text_color=COLOR_EXCELLENT)
            self.status_box.configure(border_color=COLOR_EXCELLENT)
        elif status == "Precio Alto":
            self.lbl_status_led.configure(text_color=COLOR_WARNING)
            self.status_box.configure(border_color=COLOR_WARNING)
        else:
            self.lbl_status_led.configure(text_color=COLOR_ALERT)
            self.status_box.configure(border_color=COLOR_ALERT)

    def update_property_price(self):
        if not self.selected_property_id:
            return
            
        new_price = int(self.slider_price.get())
        
        # Recalculate status for database persistence
        cat = self.lbl_spec_cat.cget("text").lower()
        rating_str = self.lbl_spec_rating.cget("text").replace(" ★", "")
        rating = float(rating_str)
        
        avg_comp_data = self.run_query("SELECT avg(precio_base_cop) FROM competidores_scraper WHERE categoria_scraper = ?", (cat,))
        avg_comp = int(avg_comp_data[0][0]) if avg_comp_data[0][0] else 160000
        
        if rating < 4.5 and new_price > avg_comp * 1.15:
            new_status = "Crítico"
        elif rating < 4.5:
            new_status = "Alerta de Reseñas"
        elif new_price > avg_comp * 1.15:
            new_status = "Precio Alto"
        else:
            new_status = "Excellent"
            
        # Update database
        self.run_query(
            "UPDATE alojamientos_propios SET precio_actual_cop = ?, estado_competitivo = ? WHERE id_propiedad = ?", 
            (new_price, new_status, self.selected_property_id)
        )
        
        # Reload owned sidebar and indicators
        self.refresh_all_data()
        self.select_property(self.selected_property_id)
        
        # Display feedback message
        self.show_transient_terminal_log(f"SYS_ALERT // PROPERTY {self.selected_property_id} RE-CALIBRATED BASE PRICE TO COP {new_price:,}")

    def show_transient_terminal_log(self, text):
        log_window = ctk.CTkLabel(self, text=text, font=("Consolas", 10), text_color=COLOR_EXCELLENT, fg_color=COLOR_BG)
        log_window.pack(fill="x", side="bottom", py=2)
        self.after(3000, log_window.destroy)

    def load_competitor_nodes(self, category, avg_comp):
        # Query 15 competitors for this category
        comps = self.run_query(
            "SELECT nombre_competidor, precio_base_cop, calificacion_global, total_resenas, url_imagen_competidor, url_airbnb_referencia FROM competidores_scraper WHERE categoria_scraper = ? LIMIT 10", 
            (category,)
        )
        
        # Clear right frame
        for child in self.scroll_competitors.winfo_children():
            child.destroy()
            
        for comp in comps:
            name, price, rating, reviews, img_url, ref_url = comp
            
            comp_card = ctk.CTkFrame(self.scroll_competitors, fg_color="#131922", border_width=1, border_color="#2c3a47")
            comp_card.pack(fill="x", pady=6)
            
            # Rating Indicator Color
            rat_color = COLOR_EXCELLENT if rating >= 4.8 else (COLOR_WARNING if rating >= 4.5 else COLOR_ALERT)
            
            # Content layout
            c_info = ctk.CTkFrame(comp_card, fg_color="transparent")
            c_info.pack(fill="x", padx=10, pady=8)
            
            lbl_comp_name = ctk.CTkLabel(c_info, text=name, font=("Consolas", 11, "bold"), text_color="#e0e0e0", anchor="w", wraplength=310)
            lbl_comp_name.pack(fill="x")
            
            # Stats row
            stats_frame = ctk.CTkFrame(c_info, fg_color="transparent")
            stats_frame.pack(fill="x", pady=3)
            
            lbl_comp_price = ctk.CTkLabel(stats_frame, text=f"COP {price:,}", font=("Consolas", 11, "bold"), text_color=COLOR_ACCENT)
            lbl_comp_price.pack(side="left")
            
            # Delta percentage comparison
            delta = ((price - avg_comp) / avg_comp) * 100
            delta_color = COLOR_EXCELLENT if delta < 0 else COLOR_ALERT
            delta_sign = "" if delta < 0 else "+"
            lbl_delta = ctk.CTkLabel(stats_frame, text=f" ({delta_sign}{delta:.1f}%)", font=("Consolas", 9), text_color=delta_color)
            lbl_delta.pack(side="left")
            
            lbl_comp_rating = ctk.CTkLabel(stats_frame, text=f"{rating:.2f}★ ({reviews} res)", font=("Consolas", 10), text_color=rat_color)
            lbl_comp_rating.pack(side="right")

            # Asynchronous Image loading placeholder
            img_canvas = tk.Canvas(c_info, width=310, height=80, bg="#111111", highlightthickness=0)
            img_canvas.pack(pady=4)
            img_canvas.create_text(155, 40, text="[ TELEMETRY PREVIEW IMAGE ]", fill="#333333", font=("Consolas", 8))
            
            # Start a thread to load the image online and draw it
            threading.Thread(target=self.async_load_image, args=(img_url, img_canvas), daemon=True).start()

    def async_load_image(self, url, canvas):
        if url in self.image_cache:
            img_tk = self.image_cache[url]
            self.draw_image_on_canvas(canvas, img_tk)
            return
            
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=3) as response:
                data = response.read()
            img = Image.open(BytesIO(data))
            # Resize
            img = img.resize((310, 80), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)
            self.image_cache[url] = img_tk
            self.draw_image_on_canvas(canvas, img_tk)
        except Exception as e:
            # Silent fail, will keep showing placeholder text
            pass

    def draw_image_on_canvas(self, canvas, img_tk):
        try:
            canvas.delete("all")
            canvas.create_image(0, 0, anchor="nw", image=img_tk)
            # Prevent garbage collection
            canvas.image = img_tk
        except Exception:
            pass

    # CRUD INTERACTION DIALOGS
    def open_add_dialog(self):
        self.open_property_dialog("REGISTRAR PROPIEDAD", is_edit=False)
        
    def open_edit_dialog(self):
        if not self.selected_property_id:
            return
        self.open_property_dialog("EDITAR PROPIEDAD", is_edit=True)

    def open_property_dialog(self, title, is_edit=False):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x480")
        dialog.configure(fg_color=COLOR_PANEL)
        dialog.grab_set() # Focus lock
        
        lbl_head = ctk.CTkLabel(dialog, text=f"// {title} //", font=("Consolas", 14, "bold"), text_color=COLOR_ACCENT)
        lbl_head.pack(pady=15)
        
        # Fields
        fields_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=20)
        
        # ID (Disabled if editing)
        lbl_id = ctk.CTkLabel(fields_frame, text="ID DE PROPIEDAD (ej: prop-loft-xxx):", font=("Consolas", 10), text_color=COLOR_TEXT_MUTED, anchor="w")
        lbl_id.pack(fill="x", pady=(5,0))
        entry_id = ctk.CTkEntry(fields_frame, fg_color=COLOR_BG, border_color=COLOR_BORDER)
        entry_id.pack(fill="x", pady=5)
        if is_edit:
            entry_id.insert(0, self.selected_property_id)
            entry_id.configure(state="disabled")
            
        # Nombre
        lbl_name = ctk.CTkLabel(fields_frame, text="NOMBRE DE ALOJAMIENTO:", font=("Consolas", 10), text_color=COLOR_TEXT_MUTED, anchor="w")
        lbl_name.pack(fill="x", pady=(5,0))
        entry_name = ctk.CTkEntry(fields_frame, fg_color=COLOR_BG, border_color=COLOR_BORDER)
        entry_name.pack(fill="x", pady=5)
        
        # Categoria (OptionMenu)
        lbl_cat = ctk.CTkLabel(fields_frame, text="CATEGORÍA:", font=("Consolas", 10), text_color=COLOR_TEXT_MUTED, anchor="w")
        lbl_cat.pack(fill="x", pady=(5,0))
        menu_cat = ctk.CTkOptionMenu(fields_frame, values=["design", "cabins", "trending"], fg_color=COLOR_BG, button_color=COLOR_BORDER, dropdown_fg_color=COLOR_PANEL)
        menu_cat.pack(fill="x", pady=5)
        
        # Precio
        lbl_price = ctk.CTkLabel(fields_frame, text="TARIFA BASE (COP):", font=("Consolas", 10), text_color=COLOR_TEXT_MUTED, anchor="w")
        lbl_price.pack(fill="x", pady=(5,0))
        entry_price = ctk.CTkEntry(fields_frame, fg_color=COLOR_BG, border_color=COLOR_BORDER)
        entry_price.pack(fill="x", pady=5)
        
        # Calificacion
        lbl_rating = ctk.CTkLabel(fields_frame, text="CALIFICACIÓN INTERNA (0.0 a 5.0):", font=("Consolas", 10), text_color=COLOR_TEXT_MUTED, anchor="w")
        lbl_rating.pack(fill="x", pady=(5,0))
        entry_rating = ctk.CTkEntry(fields_frame, fg_color=COLOR_BG, border_color=COLOR_BORDER)
        entry_rating.pack(fill="x", pady=5)
        
        # Zona
        lbl_zone = ctk.CTkLabel(fields_frame, text="ZONA (Armenia, Colombia):", font=("Consolas", 10), text_color=COLOR_TEXT_MUTED, anchor="w")
        lbl_zone.pack(fill="x", pady=(5,0))
        entry_zone = ctk.CTkEntry(fields_frame, fg_color=COLOR_BG, border_color=COLOR_BORDER)
        entry_zone.pack(fill="x", pady=5)
        
        # Populate if editing
        if is_edit:
            data = self.run_query("SELECT nombre_alojamiento, categoria_propia, precio_actual_cop, calificacion_interna, zona_armenia FROM alojamientos_propios WHERE id_propiedad = ?", (self.selected_property_id,))
            if data:
                name, cat, price, rating, zone = data[0]
                entry_name.insert(0, name)
                menu_cat.set(cat)
                entry_price.insert(0, str(price))
                entry_rating.insert(0, str(rating))
                entry_zone.insert(0, zone)
                
        def save_changes():
            pid = entry_id.get().strip()
            name = entry_name.get().strip()
            cat = menu_cat.get()
            price_str = entry_price.get().strip()
            rating_str = entry_rating.get().strip()
            zone = entry_zone.get().strip()
            
            # Validation
            if not pid or not name or not price_str or not rating_str or not zone:
                tk.messagebox.showerror("Error", "Todos los campos de telemetría son requeridos.")
                return
                
            try:
                price = int(price_str)
                rating = float(rating_str)
            except ValueError:
                tk.messagebox.showerror("Error", "Tarifa o Calificación no válida.")
                return
                
            # Default Unsplash images
            img_list = CATEGORY_IMAGES.get(cat, [DEFAULT_IMAGE])
            img_url = img_list[0]
            
            # Calculate status
            avg_comp_data = self.run_query("SELECT avg(precio_base_cop) FROM competidores_scraper WHERE categoria_scraper = ?", (cat,))
            avg_comp = int(avg_comp_data[0][0]) if avg_comp_data[0][0] else 160000
            
            if rating < 4.5 and price > avg_comp * 1.15:
                status = "Crítico"
            elif rating < 4.5:
                status = "Alerta de Reseñas"
            elif price > avg_comp * 1.15:
                status = "Precio Alto"
            else:
                status = "Excellent"
                
            if is_edit:
                self.run_query("""
                UPDATE alojamientos_propios 
                SET nombre_alojamiento = ?, categoria_propia = ?, precio_actual_cop = ?, calificacion_interna = ?, estado_competitivo = ?, zona_armenia = ?
                WHERE id_propiedad = ?
                """, (name, cat, price, rating, status, zone, pid))
            else:
                # Check for duplicates
                dup = self.run_query("SELECT count(*) FROM alojamientos_propios WHERE id_propiedad = ?", (pid,))
                if dup[0][0] > 0:
                    tk.messagebox.showerror("Error", "El ID de propiedad ya se encuentra registrado.")
                    return
                self.run_query("""
                INSERT INTO alojamientos_propios (id_propiedad, nombre_alojamiento, categoria_propia, precio_actual_cop, calificacion_interna, estado_competitivo, zona_armenia, url_imagen_cover)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (pid, name, cat, price, rating, status, zone, img_url))
                
            # Recalculate benchmark relationships
            self.recalc_single_property_benchmark(pid, cat, price)
            
            # Refresh dashboard
            self.refresh_all_data()
            self.select_property(pid)
            dialog.destroy()
            self.show_transient_terminal_log(f"SYS_ALERT // NODE {pid} SAVED SUCCESSFULY")

        btn_save = ctk.CTkButton(dialog, text="GUARDAR CAMBIOS", fg_color=COLOR_BORDER, text_color=COLOR_BG, font=("Consolas", 12, "bold"), command=save_changes)
        btn_save.pack(pady=15, side="bottom")

    def recalc_single_property_benchmark(self, prop_id, cat, price):
        # Delete old benchmark links
        self.run_query("DELETE FROM relacion_benchmark WHERE id_propiedad_propia = ?", (prop_id,))
        # Get competitors
        comps = self.run_query("SELECT id_competidor, precio_base_cop FROM competidores_scraper WHERE categoria_scraper = ?", (cat,))
        if comps:
            sorted_comps = sorted(comps, key=lambda x: abs(x[1] - price))
            for i, (comp_id, comp_price) in enumerate(sorted_comps[:5]):
                rel_id = f"rel-{prop_id}-{i}"
                self.run_query("""
                INSERT OR REPLACE INTO relacion_benchmark (id_relacion, id_propiedad_propia, id_competidor_scraper)
                VALUES (?, ?, ?)
                """, (rel_id, prop_id, comp_id))

    def delete_property(self):
        if not self.selected_property_id:
            return
            
        confirm = tk.messagebox.askyesno("Confirmar", f"¿Desea dar de baja permanentemente el nodo {self.selected_property_id} de Cafetero Stays?")
        if confirm:
            pid = self.selected_property_id
            self.run_query("DELETE FROM alojamientos_propios WHERE id_propiedad = ?", (pid,))
            self.run_query("DELETE FROM relacion_benchmark WHERE id_propiedad_propia = ?", (pid,))
            
            self.selected_property_id = None
            self.refresh_all_data()
            self.show_transient_terminal_log(f"SYS_ALERT // NODE {pid} DECOMMISSIONED FROM DATABASE")

# Categorías y URLs de imágenes Unsplash
CATEGORY_IMAGES = {
    "cabins": [
        "https://images.unsplash.com/photo-1510798831971-661eb04b3739?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1549693578-d683be217e58?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=600&auto=format&fit=crop&q=80",
    ],
    "design": [
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600&auto=format&fit=crop&q=80",
    ],
    "trending": [
        "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600&auto=format&fit=crop&q=80",
        "https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=600&auto=format&fit=crop&q=80",
    ]
}
DEFAULT_IMAGE = "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600&auto=format&fit=crop&q=80"

if __name__ == "__main__":
    app = QuindioHostApp()
    app.mainloop()
