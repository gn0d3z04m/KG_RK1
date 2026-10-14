from PIL import Image, ImageDraw
import math

def flood_fill(image, x, y, fill_color, border_color=None):
    pixels = image.load()
    w, h = image.size

    if not (0 <= x < w and 0 <= y < h):
        return

    target = pixels[x, y]
    if target == fill_color:
        return
    if border_color is not None and target == border_color:
        return

    stack = [(x, y)]
    while stack:
        px, py = stack.pop()
        if not (0 <= px < w and 0 <= py < h):
            continue

        cur = pixels[px, py]
        if border_color is not None:
            if cur == border_color or cur == fill_color:
                continue
        else:
            if cur != target:
                continue

        pixels[px, py] = fill_color

        stack.append((px + 1, py))
        stack.append((px - 1, py))
        stack.append((px, py + 1))
        stack.append((px, py - 1))
        # stack.append((px + 1, py + 1))
        # stack.append((px - 1, py - 1))
        # stack.append((px - 1, py + 1))
        # stack.append((px + 1, py - 1))

def bresenham_line(image, x0, y0, x1, y1, color=(255, 255, 255)):
    pixels = image.load()
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        pixels[x0, y0] = color
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def bresenham_circle(image, xc, yc, r, color=(255, 255, 255)):
    pixels = image.load()

    def put_symmetry(x, y):
        pixels[xc + x, yc + y] = color
        pixels[xc - x, yc + y] = color
        pixels[xc + x, yc - y] = color
        pixels[xc - x, yc - y] = color
        pixels[xc + y, yc + x] = color
        pixels[xc - y, yc + x] = color
        pixels[xc + y, yc - x] = color
        pixels[xc - y, yc - x] = color

    x = 0
    y = r
    d = 3 - 2 * r

    while x <= y:
        put_symmetry(x, y)
        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1

def cyrus_beck_clip(p0, p1, polygon):
    x0, y0 = p0
    x1, y1 = p1
    dx = x1 - x0
    dy = y1 - y0
    cx = sum(v[0] for v in polygon) / len(polygon)
    cy = sum(v[1] for v in polygon) / len(polygon)
    t_enter = 0.0
    t_exit = 1.0
    n = len(polygon)
    for i in range(n):
        ax, ay = polygon[i]
        bx, by = polygon[(i + 1) % n]
        ex = bx - ax
        ey = by - ay
        nx, ny = ey, -ex
        if nx * (cx - ax) + ny * (cy - ay) > 0:
            nx, ny = -nx, -ny
        num = nx * (x0 - ax) + ny * (y0 - ay)
        den = nx * dx + ny * dy
        if den == 0:
            if num > 0:
                return None
        else:
            t = -num / den
            if den > 0:
                if t < t_exit:
                    t_exit = t
            else:
                if t > t_enter:
                    t_enter = t
        if t_enter > t_exit:
            return None
    q0 = (round(x0 + t_enter * dx), round(y0 + t_enter * dy))
    q1 = (round(x0 + t_exit * dx),  round(y0 + t_exit * dy))
    return q0, q1


def draw_polygon(image, polygon, color=(255, 255, 0)):
    n = len(polygon)
    for i in range(n):
        x0, y0 = polygon[i]
        x1, y1 = polygon[(i + 1) % n]
        bresenham_line(image, x0, y0, x1, y1, color)

def scanline_polygon_fill(image, polygon, color=(255, 255, 255)):
    pixels = image.load()
    W, H = image.size

    if len(polygon) < 3:
        return

    ys = [p[1] for p in polygon]
    y_min = max(0, min(ys))
    y_max = min(H - 1, max(ys))

    n = len(polygon)

    for y in range(y_min, y_max + 1):
        xs = []
        for i in range(n):
            x0, y0 = polygon[i]
            x1, y1 = polygon[(i + 1) % n]

            if y0 == y1:
                continue

            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y - y0) / (y1 - y0)
                x = x0 + t * (x1 - x0)
                xs.append(x)

        xs.sort()

        for i in range(0, len(xs) - 1, 2):
            x_start = int(round(xs[i]))
            x_end   = int(round(xs[i + 1]))
            if x_start > x_end:
                x_start, x_end = x_end, x_start

            x_start = max(0, x_start)
            x_end   = min(W - 1, x_end)

            for x in range(x_start, x_end + 1):
                pixels[x, y] = color


def bresenham_line_clipped(image, x0, y0, x1, y1, polygon, color=(255, 255, 255)):
    result = cyrus_beck_clip((x0, y0), (x1, y1), polygon)
    if result is None:
        return
    (qx0, qy0), (qx1, qy1) = result
    bresenham_line(image, qx0, qy0, qx1, qy1, color)



def main():
    W, H = 500, 500
    img = Image.new("RGB", (W, H), (0, 0, 0))

    cx, cy, R = 250, 250, 150
    polygon = []
    for k in range(5):
        a = -math.pi / 2 + 2 * math.pi * k / 5
        polygon.append((round(cx + R * math.cos(a)),
                        round(cy + R * math.sin(a))))

    cx2, cy2, R2 = 350, 350, 50
    polygon2 = []
    for k in range(5):
        a = -math.pi / 2 + 2 * math.pi * k / 5
        polygon2.append((round(cx2 + R2 * math.cos(a)),
                        round(cy2 + R2 * math.sin(a))))
    draw_polygon(img, polygon, (120, 120, 0))
    # draw_polygon(img, polygon2, (120, 120, 0))
    # flood_fill(img, 365, 365, (0, 120, 120))
    # bresenham_line(img,20, 20, 480, 480, (0, 120, 120))
    # bresenham_circle(img, 100, 100, 100, (0, 120, 120))
    # flood_fill(img, 135, 130, (0, 120, 0))
    # bresenham_line_clipped(img,20, 20, 480, 480, polygon)
    scanline_polygon_fill(img, polygon, (0, 120, 0))
    img.save("cyrus_beck.png")
    img.show()


if __name__ == "__main__":
    main()














# # --- Набор тестовых отрезков ---
    # segments = [
    #     ((20, 20),  (480, 480)),   # диагональ
    #     ((20, 250), (480, 250)),   # горизонталь через центр
    #     ((250, 20), (250, 480)),   # вертикаль через центр
    #     ((0, 0),    (100, 100)),   # вне многоугольника
    #     ((50, 400), (450, 100)),   # диагональ
    #     ((200, 100), (300, 400)),  # почти вертикальный
    #     ((480, 20), (20, 480)),    # обратная диагональ
    # ]
    #
    # for (x0, y0), (x1, y1) in segments:
    #     # Исходный отрезок — тускло-красным (видно, что было отсечено)
    #     bresenham_line(img, x0, y0, x1, y1, (90, 0, 0))
    #     # Отсечённая часть — ярко-белым
    #     bresenham_line_clipped(img, x0, y0, x1, y1, polygon, (255, 255, 255))

    # --- Демонстрация: круг, отсечённый тем же многоугольником ---
    # (рисуем сегменты касательных/радиусов, чтобы показать работу)
    # for k in range(24):
    #     a = 2 * math.pi * k / 24
    #     x1 = round(cx + 220 * math.cos(a))
    #     y1 = round(cy + 220 * math.sin(a))
    #     bresenham_line(img, cx, cy, x1, y1, (0, 60, 0))
    #     bresenham_line_clipped(img, cx, cy, x1, y1, polygon, (0, 200, 255))
