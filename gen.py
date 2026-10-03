import cv2 as cv
import numpy as np
import os
import random

class SyntheticDatasetGenerator:
    def __init__(self, ref_w=800, ref_h=600):
        self.ref_w = ref_w
        self.ref_h = ref_h

    def _get_canvas(self, w, h, bg_color):
        return np.full((h, w, 3), bg_color, dtype=np.uint8)

    def _get_unique_color(self, used_colors, min_dist=35):
        """Genera un color BGR equilibrando al 50% entre tonos oscuros y el espectro completo."""
        while True:
            # 50% probabilidad de tono oscuro / 50% probabilidad de tono libre
            if random.random() < 0.5:
                # Tonos oscuros y profundos (canales restringidos entre 0 y 90)
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            else:
                # Espectro completo (de 0 a 255)
                color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            # Verificar distancia euclidiana BGR con colores ya utilizados en la imagen
            if all(np.linalg.norm(np.array(color) - np.array(c)) >= min_dist for c in used_colors):
                used_colors.append(color)
                return color
    # --------------------------------------------------------------------------
    # MÓDULO 1: GENERADOR ALEATORIO / ESTOCÁSTICO (MÁS DENSIDAD Y DEFORMADOS)
    # --------------------------------------------------------------------------
    def generate_random_image(self, w, h, num_shapes=12):
        used_colors = []
        bg_color = self._get_unique_color(used_colors)
        img = self._get_canvas(w, h, bg_color)
        
        occupancy_mask = np.zeros((h, w), dtype=np.uint8)
        margin = int(min(w, h) * 0.04)

        # Incluye formas regulares, estrellas y polígonos deformados
        shape_pool = [
            "circle", "ellipse",  "square", "rectangle", "triangle", 
            "ngon_regular", "star", "deformed_polygon"
        ]

        for _ in range(num_shapes):
            color = self._get_unique_color(used_colors)
            shape_type = random.choice(shape_pool)
            
            for _ in range(random.randint(25,150)):  # Más reintentos para lograr empaquetar el doble de figuras
                min_dim = int(min(w, h) * 0.08)
                max_dim = int(min(w, h) * 0.35)
                size = random.randint(min_dim, max_dim)
                
                # Permite que el centro se ubique ligeramente fuera del lienzo
                # para que la figura aparezca recortada por los bordes
                overflow = size // 5  # Hasta un tercio del tamaño de la figura puede quedar fuera
                
                cx = random.randint(-overflow, w + overflow)
                cy = random.randint(-overflow, h + overflow)

                temp_mask = np.zeros((h, w), dtype=np.uint8)
                pts = None
                rect_coords = None

                if shape_type == "circle":
                    cv.circle(temp_mask, (cx, cy), size // 2, 255, -1)
                elif shape_type == "ellipse":
                    # Ejes de la elipse con relación de aspecto asimétrica aleatoria
                    axis_major = size // 2
                    axis_minor = max(int(axis_major * random.uniform(0.35, 0.75)), 4)
                    # El ángulo base de la elipse
                    ellipse_angle = random.uniform(0, 180)
                    cv.ellipse(temp_mask, (cx, cy), (axis_major, axis_minor), ellipse_angle, 0, 360, 255, -1)

                elif shape_type == "square":
                    half = size // 2
                    rect_coords = ((cx - half, cy - half), (cx + half, cy + half))
                    cv.rectangle(temp_mask, rect_coords[0], rect_coords[1], 255, -1)

                elif shape_type == "rectangle":
                    aspect = random.uniform(1.3, 2.2)
                    if random.choice([True, False]):
                        rw = int(size * aspect)
                        rh = size
                    else:
                        rw = size
                        rh = int(size * aspect)
                    half_w, half_h = rw // 2, rh // 2
                    rect_coords = ((cx - half_w, cy - half_h), (cx + half_w, cy + half_h))
                    cv.rectangle(temp_mask, rect_coords[0], rect_coords[1], 255, -1)

                elif shape_type == "triangle":
                    # TRIÁNGULOS ALEATORIOS (Escalenos / Isósceles / Cualesquiera)
                    # Divide los 360 grados en 3 sectores aleatorizados con radios independientes
                    angles = [
                        random.uniform(0, 2 * np.pi / 3 - 0.2),
                        random.uniform(2 * np.pi / 3 + 0.2, 4 * np.pi / 3 - 0.2),
                        random.uniform(4 * np.pi / 3 + 0.2, 2 * np.pi - 0.2)
                    ]
                    
                    raw_pts = []
                    for a in angles:
                        # Radio aleatorio entre 40% y 100% del tamaño base
                        r = (size / 2) * random.uniform(0.40, 1.0)
                        px = int(cx + r * np.cos(a))
                        py = int(cy + r * np.sin(a))
                        raw_pts.append([px, py])
                    
                    pts = np.array(raw_pts, dtype=np.int32)
                    cv.fillPoly(temp_mask, [pts], 255)
                elif shape_type == "ngon_regular":
                    n_verts = random.choice([5, 6, 7, 8,9 ,10, 11, 12])
                    angle_offset = random.uniform(0, 2 * np.pi)
                    r = size / 2
                    angles = [angle_offset + i * (2 * np.pi / n_verts) for i in range(n_verts)]
                    raw_pts = [[int(cx + r * np.cos(a)), int(cy + r * np.sin(a))] for a in angles]
                    pts = np.array(raw_pts, dtype=np.int32)
                    cv.fillPoly(temp_mask, [pts], 255)

                elif shape_type == "star":
                    # Soporta estrellas de 3, 4, 5 o 6 puntas
                    points = random.choice([3, 4, 5, 6])
                    r_outer = size / 2
                    # Para 3 o 4 puntas una hendidura un poco menos profunda se ve mejor proporcionalmente
                    inner_factor = 0.35 if points <= 4 else 0.45
                    r_inner = r_outer * inner_factor
                    angle_offset = random.uniform(0, 2 * np.pi)
                    
                    raw_pts = []
                    for i in range(points * 2):
                        r = r_outer if i % 2 == 0 else r_inner
                        a = angle_offset + i * (np.pi / points)
                        raw_pts.append([int(cx + r * np.cos(a)), int(cy + r * np.sin(a))])
                    pts = np.array(raw_pts, dtype=np.int32)
                    cv.fillPoly(temp_mask, [pts], 255)

                elif shape_type == "deformed_polygon":
                    # Polígonos deformados de 4 a 12 vértices
                    num_v = random.randint(4, 12)
                    
                    # 1. División por sectores para garantizar que no haya vértices empalmados
                    sector_size = (2 * np.pi) / num_v
                    angles = []
                    for i in range(num_v):
                        # Ángulo dentro del sector correspondiente con un pequeño margen
                        a_min = i * sector_size + (sector_size * 0.1)
                        a_max = (i + 1) * sector_size - (sector_size * 0.1)
                        angles.append(random.uniform(a_min, a_max))
                    
                    # 2. Asignar radios aleatorios para deformar la figura
                    raw_pts = []
                    for a in angles:
                        r = (size / 2) * random.uniform(0.50, 1.0)
                        px = int(cx + r * np.cos(a))
                        py = int(cy + r * np.sin(a))
                        raw_pts.append([px, py])
                        
                    pts = np.array(raw_pts, dtype=np.int32)
                    cv.fillPoly(temp_mask, [pts], 255)

                # --- ROTACIÓN ALEATORIA UNIVERSAL ---
                angle_deg = random.uniform(0, 360)
                M = cv.getRotationMatrix2D((float(cx), float(cy)), angle_deg, scale=1.0)
                temp_mask = cv.warpAffine(temp_mask, M, (w, h), flags=cv.INTER_NEAREST)
                
                # Verificar overlap contra figuras previas
                if cv.bitwise_and(occupancy_mask, temp_mask).any():
                    continue

                # Si no hay colisión, registrar en occupancy_mask
                occupancy_mask = cv.bitwise_or(occupancy_mask, temp_mask)

                # RENDERIZADO FINAL:
                # Dibujar en 'img' la misma figura que está en 'temp_mask'
                img[temp_mask == 255] = color

                break

        return img

    # --------------------------------------------------------------------------
    # MÓDULO 2: SUITE DE TESTS DETERMINISTAS (26 TESTS)
    # --------------------------------------------------------------------------
    def generate_test_case(self, test_id, w, h):
        sx, sy = w / self.ref_w, h / self.ref_h
        s_min = min(sx, sy)
        used_colors = []
        bg = self._get_unique_color(used_colors)
        img = self._get_canvas(w, h, bg)

        # 1. Tríada base
        if test_id == 1:
            cv.fillPoly(img, [np.array([[150*sx, 400*sy], [250*sx, 200*sy], [350*sx, 400*sy]], dtype=np.int32)], self._get_unique_color(used_colors), lineType=cv.LINE_8)
            cv.rectangle(img, (int(400*sx), int(200*sy)), (int(550*sx), int(350*sy)), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)
            cv.circle(img, (int(650*sx), int(300*sy)), int(75*s_min), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)

        # 2. Monocromo / Alto contraste
        elif test_id == 2:
            img = self._get_canvas(w, h, (255, 255, 255))
            c1, c2 = (0, 0, 0), (80, 80, 80)
            cv.rectangle(img, (int(100*sx), int(100*sy)), (int(300*sx), int(300*sy)), c1, -1, lineType=cv.LINE_8)
            cv.circle(img, (int(500*sx), int(300*sy)), int(100*s_min), c2, -1, lineType=cv.LINE_8)

        # 3. Fondo oscuro
        elif test_id == 3:
            img = self._get_canvas(w, h, (15, 15, 15))
            used_colors = [(15, 15, 15)]
            cv.circle(img, (int(200*sx), int(300*sy)), int(80*s_min), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)
            cv.rectangle(img, (int(450*sx), int(200*sy)), (int(650*sx), int(400*sy)), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)

        # 4. MÚLTIPLES CÍRCULOS DISJUNTOS
        elif test_id == 4:
            centers = [
                (int(150*sx), int(200*sy)),
                (int(380*sx), int(180*sy)),
                (int(630*sx), int(220*sy)),
                (int(240*sx), int(420*sy)),
                (int(520*sx), int(430*sy))
            ]
            radii = [int(65*s_min), int(75*s_min), int(60*s_min), int(80*s_min), int(70*s_min)]
            for (cx, cy), r in zip(centers, radii):
                cv.circle(img, (cx, cy), r, self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)

        # 5. Mapeo completo (2T, 2C, 2O, 2X)
        elif test_id == 5:
            cv.fillPoly(img, [np.array([[50*sx, 150*sy], [120*sx, 50*sy], [190*sx, 150*sy]], dtype=np.int32)], self._get_unique_color(used_colors), lineType=cv.LINE_8)
            cv.fillPoly(img, [np.array([[220*sx, 150*sy], [290*sx, 50*sy], [360*sx, 150*sy]], dtype=np.int32)], self._get_unique_color(used_colors), lineType=cv.LINE_8)
            cv.rectangle(img, (int(400*sx), int(50*sy)), (int(500*sx), int(150*sy)), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)
            cv.rectangle(img, (int(530*sx), int(50*sy)), (int(630*sx), int(150*sy)), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)
            cv.circle(img, (int(120*sx), int(350*sy)), int(50*s_min), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)
            cv.circle(img, (int(290*sx), int(350*sy)), int(50*s_min), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)
            cv.circle(img, (int(500*sx), int(350*sy)), int(50*s_min), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)
            pts_p = np.array([[650*sx + 50*sx*np.cos(a), 350*sy + 50*sy*np.sin(a)] for a in np.linspace(0, 2*np.pi, 6)[:-1]], dtype=np.int32)
            cv.fillPoly(img, [pts_p], self._get_unique_color(used_colors), lineType=cv.LINE_8)

        # 6. Escala extrema (Gigante vs Diminuto)
        elif test_id == 6:
            cv.circle(img, (int(300*sx), int(300*sy)), int(220*s_min), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)
            cv.rectangle(img, (int(650*sx), int(450*sy)), (int(670*sx), int(470*sy)), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)

        # 7. Rombos / Rotaciones
        elif test_id == 7:
            pts_rombo = np.array([[300*sx, 150*sy], [400*sx, 300*sy], [300*sx, 450*sy], [200*sx, 300*sy]], dtype=np.int32)
            cv.fillPoly(img, [pts_rombo], self._get_unique_color(used_colors), lineType=cv.LINE_8)

        # 8. Triángulos escalenos no degenerados
        elif test_id == 8:
            pts_escaleno = np.array([[120*sx, 480*sy], [680*sx, 420*sy], [250*sx, 120*sy]], dtype=np.int32)
            cv.fillPoly(img, [pts_escaleno], self._get_unique_color(used_colors), lineType=cv.LINE_8)

        # 9. Óvalos / Elipses
        elif test_id == 9:
            cv.ellipse(img, (int(400*sx), int(300*sy)), (int(200*sx), int(80*sy)), 0, 0, 360, self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)

        # 10. Aspect Ratio Extremo
        elif test_id == 10:
            cv.rectangle(img, (int(50*sx), int(285*sy)), (int(750*sx), int(315*sy)), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)

        # 11. Fondo Azul
        elif test_id == 11:
            cv.circle(img, (int(300*sx), int(300*sy)), int(100*s_min), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)
            cv.rectangle(img, (int(500*sx), int(200*sy)), (int(650*sx), int(350*sy)), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)

        # 12. Baja diferencia de contraste
        elif test_id == 12:
            base_col = np.array(bg, dtype=np.int16)
            fg_col = tuple(np.clip(base_col + 25, 0, 255).tolist())
            cv.circle(img, (int(400*sx), int(300*sy)), int(120*s_min), fg_col, -1, lineType=cv.LINE_8)

        # 13. Paleta de alta densidad (10 figuras distintas)
        elif test_id == 13:
            for i in range(10):
                cx, cy = int((80 + (i%5)*150)*sx), int((150 + (i//5)*300)*sy)
                col = self._get_unique_color(used_colors)
                if i % 3 == 0: cv.circle(img, (cx, cy), int(40*s_min), col, -1, lineType=cv.LINE_8)
                elif i % 3 == 1: cv.rectangle(img, (cx-30, cy-30), (cx+30, cy+30), col, -1, lineType=cv.LINE_8)
                else: cv.fillPoly(img, [np.array([[cx, cy-40], [cx-30, cy+30], [cx+30, cy+30]], dtype=np.int32)], col, lineType=cv.LINE_8)

        # 14. Colores RGB muy similares entre figuras
        elif test_id == 14:
            c1 = (0, 200, 0)
            c2 = (10, 205, 5)
            cv.rectangle(img, (int(150*sx), int(200*sy)), (int(350*sx), int(400*sy)), c1, -1, lineType=cv.LINE_8)
            cv.circle(img, (int(550*sx), int(300*sy)), int(100*s_min), c2, -1, lineType=cv.LINE_8)

        # 15. Inversión de luminancia
        elif test_id == 15:
            cv.circle(img, (int(400*sx), int(300*sy)), int(120*s_min), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)

        # 16. Figuras adyacentes / pegadas
        elif test_id == 16:
            c1 = self._get_unique_color(used_colors)
            c2 = self._get_unique_color(used_colors)
            cv.rectangle(img, (int(200*sx), int(200*sy)), (int(400*sx), int(400*sy)), c1, -1, lineType=cv.LINE_8)
            pts = np.array([[400*sx, 200*sy], [400*sx, 400*sy], [550*sx, 300*sy]], dtype=np.int32)
            cv.fillPoly(img, [pts], c2, lineType=cv.LINE_8)

        # 17. Cadena de cuadriláteros
        elif test_id == 17:
            for i in range(3):
                col = self._get_unique_color(used_colors)
                cv.rectangle(img, (int((100 + i*150)*sx), int(200*sy)), (int((250 + i*150)*sx), int(400*sy)), col, -1, lineType=cv.LINE_8)

        # 18. Anidamiento / Donut
        elif test_id == 18:
            c_outer = self._get_unique_color(used_colors)
            cv.circle(img, (int(400*sx), int(300*sy)), int(150*s_min), c_outer, -1, lineType=cv.LINE_8)
            cv.circle(img, (int(400*sx), int(300*sy)), int(70*s_min), bg, -1, lineType=cv.LINE_8)

        # 19. Figura Cóncava (Pacman)
        elif test_id == 19:
            c_pacman = self._get_unique_color(used_colors)
            cv.ellipse(img, (int(400*sx), int(300*sy)), (int(120*sx), int(120*sy)), 0, 45, 315, c_pacman, -1, lineType=cv.LINE_8)
            pts_boca = np.array([[400*sx, 300*sy], [550*sx, 200*sy], [550*sx, 400*sy]], dtype=np.int32)
            cv.fillPoly(img, [pts_boca], bg, lineType=cv.LINE_8)

        # 20. Hexágono y Octágono
        elif test_id == 20:
            pts_hex = np.array([[200*sx + 80*sx*np.cos(a), 300*sy + 80*sy*np.sin(a)] for a in np.linspace(0, 2*np.pi, 7)[:-1]], dtype=np.int32)
            pts_oct = np.array([[550*sx + 80*sx*np.cos(a), 300*sy + 80*sy*np.sin(a)] for a in np.linspace(0, 2*np.pi, 9)[:-1]], dtype=np.int32)
            cv.fillPoly(img, [pts_hex], self._get_unique_color(used_colors), lineType=cv.LINE_8)
            cv.fillPoly(img, [pts_oct], self._get_unique_color(used_colors), lineType=cv.LINE_8)

        # 21. Imagen vacía
        elif test_id == 21:
            pass

        # 22. Figuras cortadas en los bordes
        elif test_id == 22:
            cv.rectangle(img, (0, 0), (int(150*sx), int(150*sy)), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)
            cv.circle(img, (w, h), int(150*s_min), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)

        # 23. Ruido de píxeles
        elif test_id == 23:
            cv.circle(img, (int(400*sx), int(300*sy)), int(100*s_min), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)
            for _ in range(40):
                rx, ry = random.randint(0, w-1), random.randint(0, h-1)
                img[ry, rx] = self._get_unique_color(used_colors)

        # 24. Figura gigante (>90% lienzo)
        elif test_id == 24:
            cv.rectangle(img, (int(20*sx), int(20*sy)), (int(780*sx), int(580*sy)), self._get_unique_color(used_colors), -1, lineType=cv.LINE_8)

        # 25. Grid / Matriz
        elif test_id == 25:
            for row in range(4):
                for col in range(4):
                    cx, cy = int((100 + col*180)*sx), int((80 + row*140)*sy)
                    c_elem = self._get_unique_color(used_colors)
                    if (row + col) % 2 == 0:
                        cv.circle(img, (cx, cy), int(35*s_min), c_elem, -1, lineType=cv.LINE_8)
                    else:
                        cv.rectangle(img, (cx-35, cy-35), (cx+35, cy+35), c_elem, -1, lineType=cv.LINE_8)

        # 26. TEST EXTREMO: STRESS TEST CON 50+ FIGURAS
        elif test_id == 26:
            cols, rows = 9, 6
            for r in range(rows):
                for c in range(cols):
                    cx = int((50 + c * 85) * sx)
                    cy = int((45 + r * 95) * sy)
                    shape_choice = (r + c) % 3
                    col = self._get_unique_color(used_colors, min_dist=10)
                    
                    if shape_choice == 0:
                        cv.circle(img, (cx, cy), int(22 * s_min), col, -1, lineType=cv.LINE_8)
                    elif shape_choice == 1:
                        cv.rectangle(img, (cx - int(20*sx), cy - int(20*sy)), (cx + int(20*sx), cy + int(20*sy)), col, -1, lineType=cv.LINE_8)
                    else:
                        pts = np.array([[cx, cy - int(22*sy)], [cx - int(20*sx), cy + int(18*sy)], [cx + int(20*sx), cy + int(18*sy)]], dtype=np.int32)
                        cv.fillPoly(img, [pts], col, lineType=cv.LINE_8)

        return img

def main():
    generator = SyntheticDatasetGenerator()
    
    # Nombres actualizados para los archivos
    resolutions = {
        "800x600": (800, 600),
        "HD": (1920, 1080),
        "4K": (3840, 2160)
    }
    output_base = "dataset_vision_v2"

    dir_4k_controlled = os.path.join(output_base, "controlled_4k")
    dir_random_all = os.path.join(output_base, "random_tests")

    os.makedirs(dir_4k_controlled, exist_ok=True)
    os.makedirs(dir_random_all, exist_ok=True)

    print("Generando dataset final...")

    # 1. 26 Test cases controlados en 4K
    w_4k, h_4k = resolutions["4K"]
    print("\n[1/2] Generando 26 test cases controlados en 4K...")
    for test_id in range(1, 27):
        img = generator.generate_test_case(test_id, w_4k, h_4k)
        cv.imwrite(os.path.join(dir_4k_controlled, f"test_{test_id:02d}_4K.bmp"), img)
    print(" -> Tests controlados guardados en:", dir_4k_controlled)

    # 2. 50 Test cases aleatorios con los nuevos nombres ("800x600" y "HD")
    res_keys = list(resolutions.keys())
    random_resolutions = ["800x600"] * 5 + ["HD"] * 5 + ["4K"] * 5
    random_resolutions += [random.choice(res_keys) for _ in range(35)]
    random.shuffle(random_resolutions)

    print("\n[2/2] Generando 50 test cases aleatorios (incluyendo elipses)...")
    for rand_id, res_name in enumerate(random_resolutions, start=1):
        w, h = resolutions[res_name]
        num_shapes = random.randint(8, 24)
        img_rand = generator.generate_random_image(w, h, num_shapes=num_shapes)
        cv.imwrite(os.path.join(dir_random_all, f"random_{rand_id:02d}_{res_name}.bmp"), img_rand)

    print(" -> Tests aleatorios guardados en:", dir_random_all)
    print(f"\n¡Dataset generado exitosamente en '{output_base}'!")

if __name__ == '__main__':
    main()