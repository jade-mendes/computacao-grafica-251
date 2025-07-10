import pygame
import math
import colorsys

LARGURA, ALTURA = 800, 800

def hsv_to_rgb(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h / 360, s, v)
    return (int(r * 255), int(g * 255), int(b * 255))

def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def dot(a, b): return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]
def cross(a, b):
    return (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - a[0]*b[2], a[0]*b[1] - a[1]*b[0])
def normalize(v):
    n = math.sqrt(dot(v, v))
    return (v[0]/n, v[1]/n, v[2]/n) if n else (0, 0, 0)

def reflect(incidente, normal):
    return normalize((
        incidente[0] - 2 * dot(incidente, normal) * normal[0],
        incidente[1] - 2 * dot(incidente, normal) * normal[1],
        incidente[2] - 2 * dot(incidente, normal) * normal[2]
    ))

def projeta_isometrica(p):
    x, y, z = p
    ang = math.radians(30)
    x_iso = (x - y) * math.cos(ang)
    y_iso = (x + y) * math.sin(ang) - z
    escala = 60
    return int(x_iso * escala + round(LARGURA / 2)), int(y_iso * escala + round(ALTURA / 2))

def cria_prisma_hexagonal(z_base, z_topo, raio, cx, cy):
    def rotaciona_x(p, ang):
        x, y, z = p
        cos_a = math.cos(ang)
        sin_a = math.sin(ang)
        y_novo = y * cos_a - z * sin_a
        z_novo = y * sin_a + z * cos_a
        return (x, y_novo, z_novo)

    base = []
    topo = []
    for i in range(6):
        ang = math.radians(i * 60)
        x = cx + raio * math.cos(ang)
        y = cy + raio * math.sin(ang)
        base.append((x, y, z_base))
        topo.append((x, y, z_topo))

    base = [rotaciona_x(v, math.radians(90)) for v in base]
    topo = [rotaciona_x(v, math.radians(90)) for v in topo]

    altura_cilindro = 4.0
    base = [(x, y, z + altura_cilindro) for x, y, z in base]
    topo = [(x, y, z + altura_cilindro) for x, y, z in topo]

    vertices = base + topo
    faces = []
    for i in range(6):
        a, b = i, (i + 1) % 6
        faces.append([a, b, b + 6, a + 6])
    faces.append([i + 6 for i in range(6)])

    return vertices, faces

def cria_cilindro(z_base, z_topo, cx, cy, raio, segmentos=32):
    vertices, faces = [], []
    for i in range(segmentos):
        ang = 2 * math.pi * i / segmentos
        x = cx + raio * math.cos(ang)
        y = cy + raio * math.sin(ang)
        vertices.append((x, y, z_base))
    for i in range(segmentos):
        ang = 2 * math.pi * i / segmentos
        x = cx + raio * math.cos(ang)
        y = cy + raio * math.sin(ang)
        vertices.append((x, y, z_topo))
    for i in range(segmentos):
        a, b = i, (i+1)%segmentos
        faces.append([a, b, b+segmentos, a+segmentos])
    return vertices, faces

def centraliza(vs):
    cx = sum(v[0] for v in vs) / len(vs)
    cy = sum(v[1] for v in vs) / len(vs)
    cz = sum(v[2] for v in vs) / len(vs)
    return [(x - cx, y - cy, z - cz) for x, y, z in vs]

def transforma(vs, pos):
    return [(x+pos[0], y+pos[1], z+pos[2]) for x, y, z in centraliza(vs)]


cor_cilindro = (230, 230, 230) 
luz_amarela = normalize((-1.5, -1, 0.5))  
cor_luz = (255, 255, 100)        
especular_exp = 48
intensidade_especular = 2.5

def calcular_cor_phong(normal, posicao):
    ambiente = (30, 30, 30)
    
    reflect_dir = reflect(luz_amarela, normal)
    view_dir = normalize((0, 0, 1))
    especular_intensidade = math.pow(max(0, dot(reflect_dir, view_dir)), especular_exp)
    
    hotspot = max(0, 1 - 2 * math.sqrt((posicao[0] - 1.4)**2 + (posicao[2] - 2.5)**2))
    hotspot_intensity = math.pow(hotspot, 8) * 255
    
    brilho_phong = tuple(min(255, int(especular_intensidade * intensidade_especular * c)) for c in cor_luz)
    brilho_hotspot = (int(hotspot_intensity), int(hotspot_intensity * 0.9), int(hotspot_intensity * 0.4))
    
    return tuple(min(255, ambiente[i] + brilho_phong[i] + brilho_hotspot[i]) for i in range(3))

def face_na_frente(face_normal):
    return face_normal[0] > 0.25  


vertices1 = [
    (3,0,0), (3,4,0), (0,4,0), (0,0,0),
    (2,1,1), (2,3,1), (1,3,1), (1,1,1)
]
faces1 = [
    [1,0,4,5], [1,2,6,5], [2,3,7,6], [0,3,7,4], [1,2,3,0], [5,6,7,4]
]
v1 = transforma(vertices1, (-3, 0, 0))

v_cil, f_cil = cria_cilindro(0.5, 4.28, 1.4, 0.67, 0.3)
v_hex, f_hex = cria_prisma_hexagonal(0, 0.5, 1.0, 0.5, 0.25)
offset = len(v_cil)
v2 = v_cil + v_hex
f2 = f_cil + [[i + offset for i in face] for face in f_hex]


light_dir = normalize((-2, -1, -3))
cor_piramide = (200, 50, 200)
cor_hexagono = (80, 80, 180)

pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
clock = pygame.time.Clock()

running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
    tela.fill((0, 0, 0))
    
    for face in sorted(faces1, key=lambda f: sum(v1[i][2] for i in f)/len(f)):
        p0, p1, p2 = v1[face[0]], v1[face[1]], v1[face[2]]
        n = normalize(cross(sub(p1, p0), sub(p2, p0)))
        intensidade = max(0.3, min(1, 0.4 + 0.6 * dot(n, light_dir)))
        cor = tuple(int(cor_piramide[i] * intensidade) for i in range(3))
        pygame.draw.polygon(tela, cor, [projeta_isometrica(v1[i]) for i in face])
    
    for face in f_hex:
        p0, p1, p2 = v2[face[0] + offset], v2[face[1] + offset], v2[face[2] + offset]
        n = normalize(cross(sub(p1, p0), sub(p2, p0)))
        intensidade = max(0.6, min(1, 0.7 + 0.3 * dot(n, light_dir)))
        cor = tuple(int(cor_hexagono[i] * intensidade) for i in range(3))
        pygame.draw.polygon(tela, cor, [projeta_isometrica(v2[i + offset]) for i in face])
    
    for face in f_cil:
        if len(face) == 4:
            p0, p1, p2 = v2[face[0]], v2[face[1]], v2[face[2]]
            normal = normalize(cross(sub(p1, p0), sub(p2, p0)))
            
            if face_na_frente(normal):
                pos_media = (
                    sum(v2[i][0] for i in face)/4,
                    sum(v2[i][1] for i in face)/4,
                    sum(v2[i][2] for i in face)/4
                )
                cor = calcular_cor_phong(normal, pos_media)
            else:
                cor = (180, 180, 180)
            
            pygame.draw.polygon(tela, cor, [projeta_isometrica(v2[i]) for i in face])
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
