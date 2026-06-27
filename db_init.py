import os
import glob
import sqlite3
import pandas as pd
import numpy as np

DB_NAME = "quindiohost.db"

# Categorías y URLs de imágenes Unsplash premium para diseño visual
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

OWNED_PROPERTIES_DATA = [
    {"id": "prop-loft-001", "nombre": "Sky Top - Suite con Jacuzzi Privado", "categoria": "design", "precio": 280000, "calificacion": 4.87, "zona": "Norte - Av. Centenario", "img": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600&auto=format&fit=crop&q=80"},
    {"id": "prop-loft-002", "nombre": "Eco-Cabin Coffee Valley View", "categoria": "cabins", "precio": 165000, "calificacion": 4.95, "zona": "Norte - Vía Circasia", "img": "https://images.unsplash.com/photo-1510798831971-661eb04b3739?w=600&auto=format&fit=crop&q=80"},
    {"id": "prop-loft-003", "nombre": "Urban Design Loft Laureles", "categoria": "design", "precio": 220000, "calificacion": 4.75, "zona": "Laureles - Armenia Norte", "img": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600&auto=format&fit=crop&q=80"},
    {"id": "prop-loft-004", "nombre": "Premium Cabin Mountain Retreat", "categoria": "cabins", "precio": 310000, "calificacion": 4.91, "zona": "Norte - Vía Circasia", "img": "https://images.unsplash.com/photo-1549693578-d683be217e58?w=600&auto=format&fit=crop&q=80"},
    {"id": "prop-loft-005", "nombre": "Trending Studio Apartment Centro", "categoria": "trending", "precio": 125000, "calificacion": 4.42, "zona": "Centro - Calle 21", "img": "https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600&auto=format&fit=crop&q=80"},
    {"id": "prop-loft-006", "nombre": "Coffee Design Loft & Terrace", "categoria": "design", "precio": 240000, "calificacion": 4.88, "zona": "Norte - Av. Centenario", "img": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600&auto=format&fit=crop&q=80"},
    {"id": "prop-loft-007", "nombre": "Rustik Cabin Bamboo Forest", "categoria": "cabins", "precio": 190000, "calificacion": 4.60, "zona": "Sur - Vía El Caimo", "img": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=600&auto=format&fit=crop&q=80"},
    {"id": "prop-loft-008", "nombre": "Sunset View Penthouse", "categoria": "trending", "precio": 290000, "calificacion": 4.79, "zona": "Norte - Av. Centenario", "img": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600&auto=format&fit=crop&q=80"},
    {"id": "prop-loft-009", "nombre": "Industrial Minimalist Loft", "categoria": "design", "precio": 205000, "calificacion": 4.69, "zona": "Laureles - Armenia Norte", "img": "https://images.unsplash.com/photo-1505691938895-1758d7feb511?w=600&auto=format&fit=crop&q=80"},
    {"id": "prop-loft-010", "nombre": "Chalet Cafetero Tradicional", "categoria": "cabins", "precio": 350000, "calificacion": 4.98, "zona": "Sur - Vía El Caimo", "img": "https://images.unsplash.com/photo-1510798831971-661eb04b3739?w=600&auto=format&fit=crop&q=80"},
    {"id": "prop-loft-011", "nombre": "Cozy Nordic Loft Armenia", "categoria": "design", "precio": 180000, "calificacion": 4.35, "zona": "Centro - Calle 21", "img": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600&auto=format&fit=crop&q=80"},
    {"id": "prop-loft-012", "nombre": "Modernist View Studio", "categoria": "trending", "precio": 155000, "calificacion": 4.81, "zona": "Norte - Av. Centenario", "img": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600&auto=format&fit=crop&q=80"},
    {"id": "prop-loft-013", "nombre": "Forest View Cabin", "categoria": "cabins", "precio": 210000, "calificacion": 4.70, "zona": "Norte - Vía Circasia", "img": "https://images.unsplash.com/photo-1549693578-d683be217e58?w=600&auto=format&fit=crop&q=80"},
    {"id": "prop-loft-014", "nombre": "Luxury Design Loft Loft", "categoria": "design", "precio": 395000, "calificacion": 4.92, "zona": "Norte - Av. Centenario", "img": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600&auto=format&fit=crop&q=80"},
    {"id": "prop-loft-015", "nombre": "Urban Oasis Studio", "categoria": "trending", "precio": 160000, "calificacion": 4.65, "zona": "Laureles - Armenia Norte", "img": "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=600&auto=format&fit=crop&q=80"},
]

def clean_category_name(filename):
    base = os.path.basename(filename)
    category = base.replace("reporte_Armenia_Colombia_", "").replace(".xlsx", "")
    if "cabins" in category:
        return "cabins"
    elif "design" in category:
        return "design"
    elif "trending" in category:
        return "trending"
    return category

def init_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS alojamientos_propios;")
    cursor.execute("""
    CREATE TABLE alojamientos_propios (
        id_propiedad TEXT PRIMARY KEY,
        nombre_alojamiento TEXT NOT NULL,
        categoria_propia TEXT NOT NULL,
        precio_actual_cop INTEGER NOT NULL,
        calificacion_interna REAL NOT NULL,
        estado_competitivo TEXT NOT NULL,
        zona_armenia TEXT NOT NULL,
        url_imagen_cover TEXT NOT NULL
    );
    """)

    cursor.execute("DROP TABLE IF EXISTS competidores_scraper;")
    cursor.execute("""
    CREATE TABLE competidores_scraper (
        id_competidor TEXT PRIMARY KEY,
        nombre_competidor TEXT NOT NULL,
        categoria_scraper TEXT NOT NULL,
        precio_base_cop INTEGER NOT NULL,
        calificacion_global REAL NOT NULL,
        total_resenas INTEGER NOT NULL,
        zona_armenia TEXT,
        url_airbnb_referencia TEXT,
        url_imagen_competidor TEXT NOT NULL
    );
    """)

    cursor.execute("DROP TABLE IF EXISTS relacion_benchmark;")
    cursor.execute("""
    CREATE TABLE relacion_benchmark (
        id_relacion TEXT PRIMARY KEY,
        id_propiedad_propia TEXT NOT NULL,
        id_competidor_scraper TEXT NOT NULL,
        FOREIGN KEY (id_propiedad_propia) REFERENCES alojamientos_propios(id_propiedad),
        FOREIGN KEY (id_competidor_scraper) REFERENCES competidores_scraper(id_competidor)
    );
    """)
    
    conn.commit()
    conn.close()
    print("Database schema created.")

def import_scraped_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    files = glob.glob("Datos AirBnB Armenia/*.xlsx")
    competitors_added = 0
    
    for file in files:
        category = clean_category_name(file)
        print(f"Processing file: {file} as category '{category}'")
        
        try:
            df_inmuebles = pd.read_excel(file, sheet_name="Inmuebles")
        except Exception as e:
            print(f"Error reading Inmuebles sheet in {file}: {e}")
            continue
            
        try:
            df_prices = pd.read_excel(file, sheet_name="Precios por Fecha")
        except Exception as e:
            df_prices = None
            print(f"Error reading Precios sheet in {file}: {e}")
            
        for _, row in df_inmuebles.iterrows():
            id_inm = str(row["ID Inmueble"])
            nombre = row["Nombre"]
            ubicacion = row["Ubicación Escrita"]
            calificacion = float(row["Calificación Promedio"])
            total_res = int(row["Total Reseñas"])
            
            avg_price = 160000
            if df_prices is not None:
                listing_prices = df_prices[df_prices["ID Inmueble"] == row["ID Inmueble"]]
                if not listing_prices.empty:
                    cols_to_avg = [c for c in df_prices.columns if c not in ["ID Inmueble", "Nombre"]]
                    prices = listing_prices[cols_to_avg].values.flatten()
                    prices = prices[~np.isnan(prices)]
                    if len(prices) > 0:
                        avg_price = int(np.mean(prices))
            
            img_list = CATEGORY_IMAGES.get(category, [DEFAULT_IMAGE])
            img_url = img_list[competitors_added % len(img_list)]
            ref_url = f"https://www.airbnb.com.co/rooms/{id_inm}"
            
            cursor.execute("""
            INSERT OR REPLACE INTO competidores_scraper 
            (id_competidor, nombre_competidor, categoria_scraper, precio_base_cop, calificacion_global, total_resenas, zona_armenia, url_airbnb_referencia, url_imagen_competidor)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_inm, nombre, category, avg_price, calificacion, total_res, ubicacion, ref_url, img_url))
            competitors_added += 1

    conn.commit()
    conn.close()
    print(f"Imported {competitors_added} competitors to SQLite.")

def insert_owned_properties():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    for p in OWNED_PROPERTIES_DATA:
        cursor.execute("""
        INSERT OR REPLACE INTO alojamientos_propios 
        (id_propiedad, nombre_alojamiento, categoria_propia, precio_actual_cop, calificacion_interna, estado_competitivo, zona_armenia, url_imagen_cover)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (p["id"], p["nombre"], p["categoria"], p["precio"], p["calificacion"], "Excellent", p["zona"], p["img"]))
        
    conn.commit()
    conn.close()
    print("Inserted 15 owned listings.")

def calculate_status_and_links():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id_propiedad, categoria_propia, precio_actual_cop, calificacion_interna FROM alojamientos_propios")
    owned = cursor.fetchall()
    
    for prop_id, cat, precio, calif in owned:
        cursor.execute("SELECT id_competidor, precio_base_cop FROM competidores_scraper WHERE categoria_scraper = ?", (cat,))
        comps = cursor.fetchall()
        
        if comps:
            avg_comp_price = np.mean([c[1] for c in comps])
            sorted_comps = sorted(comps, key=lambda x: abs(x[1] - precio))
            for i, (comp_id, comp_price) in enumerate(sorted_comps[:5]):
                rel_id = f"rel-{prop_id}-{i}"
                cursor.execute("""
                INSERT OR REPLACE INTO relacion_benchmark (id_relacion, id_propiedad_propia, id_competidor_scraper)
                VALUES (?, ?, ?)
                """, (rel_id, prop_id, comp_id))
            
            if calif < 4.5 and precio > avg_comp_price * 1.15:
                estado = "Crítico"
            elif calif < 4.5:
                estado = "Alerta de Reseñas"
            elif precio > avg_comp_price * 1.15:
                estado = "Precio Alto"
            else:
                estado = "Excellent"
        else:
            estado = "Excellent"
            
        cursor.execute("UPDATE alojamientos_propios SET estado_competitivo = ? WHERE id_propiedad = ?", (estado, prop_id))
        
    conn.commit()
    conn.close()
    print("Calculated status and benchmark associations.")

if __name__ == "__main__":
    init_database()
    import_scraped_data()
    insert_owned_properties()
    calculate_status_and_links()
    print("Ingestion script completed successfully.")
