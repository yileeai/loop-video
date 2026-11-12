"""Split-screen explainer style: paper graphic panel on top, talking head below, pill captions.

This is a per-project template: copy it, then rewrite the scene painters (sc_*), SCENES and CAPS
for the new narration. The sample content below is the 2026-11-12 LOOP sample (23 s talking head).
Usage: python render_split.py SOURCE.mp4 OUT.mp4 [--preview t1,t2,...]
SOURCE is the talking-head video with its own narration track; any portrait size, scaled to 1080x1920.
"""
import math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
SPLIT = 960
PAPER = (240, 239, 235)
TAG = os.environ.get("SPLIT_TAG", "LOOP · AI 获客观察")  # 顶部栏目名，换成你的
INK = (26, 26, 26)
GREEN = (31, 92, 70)        # LOOP 松绿（浅底）
GREEN_D = (60, 196, 142)    # LOOP 松绿（深底）
GREY = (150, 150, 145)
DOT = (205, 204, 198)
WHITE = (255, 255, 255)
def _first(*paths):
    return next((p for p in paths if os.path.exists(p)), paths[0])
# Windows 微软雅黑 / macOS 苹方·冬青黑体; override with env SPLIT_FONT_BOLD / SPLIT_FONT_REGULAR
FONT_B = os.environ.get("SPLIT_FONT_BOLD") or _first(
    "C:/Windows/Fonts/msyhbd.ttc", "/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc")
FONT_R = os.environ.get("SPLIT_FONT_REGULAR") or _first(
    "C:/Windows/Fonts/msyh.ttc", "/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc")
_fonts = {}

def F(size, bold=True):
    k = (size, bold)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(FONT_B if bold else FONT_R, size)
    return _fonts[k]

def prog(t, a, d=.35):
    return min(1.0, max(0.0, (t - a) / d))

def ease(p):
    return 1 - (1 - p) ** 3

def A(p):
    return round(255 * p)

def text(d, xy, s, size, rgb=INK, p=1.0, anchor="mm", bold=True, dy=0):
    if p <= 0: return
    q = ease(p)
    x, y = xy
    d.text((x, y + round((1 - q) * (dy or 18))), s, font=F(size, bold), fill=(*rgb, A(q)), anchor=anchor)

def line(d, a, b, p, rgb=INK, w=4, dash=0):
    if p <= 0: return
    q = ease(p)
    e = (a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q)
    if not dash:
        d.line((a, e), fill=(*rgb, 255), width=w); return
    L = math.dist(a, e); n = int(L // (dash * 2)) + 1
    for i in range(n):
        s0, s1 = i * 2 * dash / max(L, 1), min(1, (i * 2 + 1) * dash / max(L, 1))
        if s0 >= 1: break
        d.line(((a[0] + (e[0] - a[0]) * s0, a[1] + (e[1] - a[1]) * s0),
                (a[0] + (e[0] - a[0]) * s1, a[1] + (e[1] - a[1]) * s1)), fill=(*rgb, 255), width=w)

def polyline(d, pts, p, rgb, w=6):
    """Draw a polyline grown to fraction p of its length; return the head point."""
    if p <= 0: return None
    segs = list(zip(pts, pts[1:])); Ls = [math.dist(a, b) for a, b in segs]
    rem = sum(Ls) * ease(p); out = [pts[0]]
    for (a, b), L in zip(segs, Ls):
        if rem >= L: out.append(b); rem -= L
        else:
            k = rem / L; out.append((a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)); break
    d.line(out, fill=(*rgb, 255), width=w, joint="curve")
    return out[-1]

def dot(d, c, r, rgb, alpha=255, ring=0):
    x, y = c
    if ring: d.ellipse((x - r, y - r, x + r, y + r), outline=(*rgb, alpha), width=ring)
    else: d.ellipse((x - r, y - r, x + r, y + r), fill=(*rgb, alpha))

def card(d, box, p, outline=DOT, fill=WHITE, r=22, w=2):
    if p <= 0: return 0
    q = ease(p); dy = round((1 - q) * 22)
    x0, y0, x1, y1 = box
    d.rounded_rectangle((x0, y0 + dy, x1, y1 + dy), r, fill=(*fill, A(q)), outline=(*outline, A(q)), width=w)
    return dy

def pill(d, xy, s, size, bg, fg, p=1.0, anchor_center=True):
    if p <= 0: return
    q = ease(p); f = F(size)
    tw = d.textlength(s, font=f); x, y = xy
    pad_x, pad_y = size * .45, size * .28
    box = (x - tw / 2 - pad_x, y - size / 2 - pad_y, x + tw / 2 + pad_x, y + size / 2 + pad_y + 4)
    d.rounded_rectangle(box, 10, fill=(*bg, A(q)))
    d.text((x, y), s, font=f, fill=(*fg, A(q)), anchor="mm")

# ---------------------------------------------------------------- scenes
def sc_hook(d, t):
    pill(d, (540, 300), "震惊", 40, GREEN, WHITE, prog(t, 0.0, .2))
    text(d, (540, 470), "又一行业", 120, INK, prog(t, 0.7, .35))
    # "被颠覆" drops in with an overshoot rotation feel (scale via size steps)
    p = prog(t, 1.2, .3)
    if p:
        size = round(150 * (1.25 - .25 * ease(p)))
        text(d, (540, 650), "被颠覆", size, GREEN, p, dy=1)
    line(d, (290, 478), (790, 478), prog(t, 1.45, .3), GREEN, 10)   # strike through the old industry

CAL0 = (270, 300)  # first dot centre
def cal_pos(r, c):
    return (CAL0[0] + c * 90, CAL0[1] + r * 78)
HOLIDAY_MID = [(0, 6), (1, 0), (1, 1)]                        # 9/15-9/17 中秋
HOLIDAY_NAT = [(3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (4, 0)]  # 10/1-10/7 国庆
MAKEUP = [(0, 5), (2, 6), (4, 5)]                              # 9/14 9/29 10/12 调休上班

def sc_calendar(d, t):
    s = 1.96
    text(d, (540, 150), "9月 — 10月", 34, GREY, prog(t, s, .3), bold=False)
    for c, w in enumerate("一二三四五六日"):
        text(d, (CAL0[0] + c * 90, 225), w, 28, GREY, prog(t, s + .05 * c, .3), bold=False)
    for r in range(6):
        for c in range(7):
            p = ease(prog(t, s + .1 + .012 * (r * 7 + c), .25))
            if not p: continue
            pos = cal_pos(r, c)
            hol = (r, c) in HOLIDAY_MID and t >= 2.9 + .06 * HOLIDAY_MID.index((r, c)) or \
                  (r, c) in HOLIDAY_NAT and t >= 3.26 + .05 * HOLIDAY_NAT.index((r, c))
            if hol:
                dot(d, pos, 22, GREEN)
            elif (r, c) in MAKEUP and t >= 3.58:
                q = ease(prog(t, 3.58 + .1 * MAKEUP.index((r, c)), .25))
                dot(d, pos, 22, INK, A(q), ring=4)
                d.text(pos, "班", font=F(22), fill=(*INK, A(q)), anchor="mm")
            else:
                dot(d, pos, 9 if c < 5 else 7, DOT if c < 5 else (222, 221, 216), A(p))
    # labels
    text(d, (895, cal_pos(0, 0)[1]), "中秋", 30, GREEN, prog(t, 2.95, .3))
    text(d, (895, cal_pos(3, 0)[1]), "国庆", 30, GREEN, prog(t, 3.5, .3))
    text(d, (895, cal_pos(2, 0)[1]), "调休", 30, INK, prog(t, 3.7, .3))
    text(d, (540, 820), "调休，怎么弄？", 52, INK, prog(t, 3.98, .3))

def row(d, t, i, start, tag, title, extra=None, active_until=99):
    y = 230 + i * 190
    act = start <= t < active_until
    dy = card(d, (100, y, 980, y + 160), prog(t, start, .35), GREEN if act else DOT, WHITE, 22, 4 if act else 2)
    if t < start: return
    q = ease(prog(t, start, .35)); y += dy
    dot(d, (160, y + 80), 28, GREEN if act else INK, A(q))
    d.text((160, y + 80), str(i + 1), font=F(30), fill=(*WHITE, A(q)), anchor="mm")
    d.text((215, y + 52), tag, font=F(28, False), fill=(*GREY, A(q)), anchor="lm")
    d.text((215, y + 108), title, font=F(48), fill=(*INK, A(q)), anchor="lm")
    if extra: extra(d, t, y)

def ex_fed(d, t, y):
    p = ease(prog(t, 7.16, .6))
    if p:
        d.text((935, y + 92), f"-{round(50 * p)}", font=F(84), fill=(*GREEN, 255), anchor="rm")
        d.text((935, y + 30), "基点 bp", font=F(24, False), fill=(*GREY, 255), anchor="rm")

def ex_cost(d, t, y):
    p = ease(prog(t, 8.82, .7))
    if prog(t, 8.82, .2) <= 0: return
    x0, x1 = 700, 935
    d.text((x0, y + 40), "成本", font=F(24, False), fill=(*GREY, 255), anchor="lm")
    d.rounded_rectangle((x0, y + 70, x1, y + 98), 14, fill=(*DOT, 255))
    d.rounded_rectangle((x0, y + 70, x0 + (x1 - x0) * (1 - .45 * p), y + 98), 14, fill=(*GREEN, 255))

def ex_grok(d, t, y):
    pill(d, (850, y + 80), "Grok-2", 40, INK, WHITE, prog(t, 10.46, .3))

def sc_news(d, t):
    text(d, (540, 150), "世界变天了 · 本周", 34, GREY, prog(t, 6.18, .3), bold=False)
    row(d, t, 0, 6.18, "美联储", "降息 50 个点", ex_fed, 7.78)
    row(d, t, 1, 7.78, "老板们", "用 AI 降本增效", ex_cost, 9.66)
    row(d, t, 2, 9.66, "马斯克", "新模型推出", ex_grok)

def curve(fn, x0, x1, n=60):
    return [(x0 + (x1 - x0) * i / n, fn(i / n)) for i in range(n + 1)]

def sc_chart(d, t):
    X0, X1, Y0, Y1 = 150, 940, 230, 780
    text(d, (540, 150), "流量规则 · 示意", 34, GREY, prog(t, 11.66, .3), bold=False)
    line(d, (X0, Y1), (X1, Y1), prog(t, 11.66, .3), INK, 3)
    line(d, (X0, Y1), (X0, Y0), prog(t, 11.66, .3), INK, 3)
    text(d, (X1, Y1 + 40), "时间 →", 26, GREY, prog(t, 11.8, .3), anchor="rm", bold=False)
    text(d, (X0 + 10, Y0 - 20), "获客效率 ↑", 26, GREY, prog(t, 11.8, .3), anchor="lm", bold=False)
    # influencer economy: high then crash
    fall = curve(lambda u: Y0 + 90 + (Y1 - Y0 - 160) * (1 / (1 + math.exp(-12 * (u - .55)))), X0, X1)
    h = polyline(d, fall, prog(t, 11.75, 1.3), GREY, 6)
    if h: dot(d, h, 9, GREY)
    text(d, (300, Y0 + 50), "网红经济", 32, GREY, prog(t, 12.0, .3))
    pill(d, (800, Y1 - 120), "重创", 32, INK, WHITE, prog(t, 12.88, .25))
    # rule rewrite line
    xm = X0 + (X1 - X0) * .55
    line(d, (xm, Y1), (xm, Y0), prog(t, 13.26, .5), INK, 3, dash=12)
    text(d, (xm, Y0 - 20), "规则改写", 30, INK, prog(t, 13.6, .3))
    # robot rising
    rise = curve(lambda u: Y1 - 30 - (Y1 - Y0 - 70) * (1 / (1 + math.exp(-11 * (u - .62)))), X0, X1)
    h = polyline(d, rise, prog(t, 14.54, 1.0), GREEN, 8)
    if h: dot(d, h, 13, GREEN)
    pill(d, (835, Y0 + 70), "获客机器人 崛起", 32, GREEN, WHITE, prog(t, 15.36, .25))

def sc_robot(d, t):
    text(d, (540, 150), "一套组合", 34, GREY, prog(t, 15.76, .3), bold=False)
    dy = card(d, (130, 210, 470, 330), prog(t, 15.76, .35), DOT, WHITE, 20)
    text(d, (300, 270 + dy), "小助理", 46, INK, prog(t, 15.76, .35), dy=1)
    text(d, (540, 270), "+", 60, GREY, prog(t, 16.42, .25))
    dy = card(d, (610, 210, 950, 330), prog(t, 16.6, .35), GREEN, GREEN, 20)
    text(d, (780, 270 + dy), "AI智能体", 46, WHITE, prog(t, 16.6, .35), dy=1)
    # connectors converge on the lead grid
    line(d, (300, 335), (300, 380), prog(t, 17.2, .2), INK, 3)
    line(d, (780, 335), (780, 380), prog(t, 17.2, .2), INK, 3)
    line(d, (300, 380), (780, 380), prog(t, 17.3, .25), INK, 3)
    line(d, (540, 380), (540, 420), prog(t, 17.45, .15), INK, 3)
    cols, rows, gx, gy = 20, 7, 40, 40
    x0 = 540 - (cols - 1) * gx / 2; y0 = 450
    total = cols * rows
    fill = ease(prog(t, 17.38, 1.45)) * total
    for k in range(total):
        r, c = divmod(k, cols)
        p = ease(prog(t, 17.0 + .004 * k, .2))
        if not p: continue
        on = k < fill
        dot(d, (x0 + c * gx, y0 + r * gy), 11 if on else 6, GREEN if on else DOT, A(p))
    n = round(fill)
    text(d, (540, 770), "每日客资", 32, GREY, prog(t, 17.38, .3), bold=False)
    if t >= 18.24:
        text(d, (540, 835), "数千", 76, GREEN, prog(t, 18.24, .3))

def sc_cta(d, t):
    text(d, (540, 150), "评论区", 34, GREY, prog(t, 19.22, .3), bold=False)
    dy = card(d, (110, 230, 970, 520), prog(t, 19.22, .35), DOT, WHITE, 26)
    if t >= 19.22:
        q = ease(prog(t, 19.22, .35)); y = 230 + dy
        dot(d, (180, y + 75), 34, DOT, A(q))
        d.text((235, y + 55), "对这套打法感兴趣？", font=F(34), fill=(*INK, A(q)), anchor="lm")
        d.text((235, y + 100), "回复下方口令领取", font=F(26, False), fill=(*GREY, A(q)), anchor="lm")
        # input box with typed 888
        d.rounded_rectangle((170, y + 160, 910, y + 250), 45, fill=(*PAPER, A(q)))
        typed = "8" * min(3, max(0, int((t - 20.94) / .15) + 1)) if t >= 20.94 else ""
        if typed:
            d.text((220, y + 205), typed, font=F(52), fill=(*GREEN, 255), anchor="lm")
        if not typed or (int(t * 2) % 2 == 0):
            cx = 222 + d.textlength(typed, font=F(52))
            d.line((cx, y + 180, cx, y + 230), fill=(*INK, 255), width=3)
        pill(d, (850, y + 205), "发送", 30, GREEN if typed == "888" else GREY, WHITE, 1)
    text(d, (540, 650), "888", 150, GREEN, prog(t, 21.1, .3))
    text(d, (540, 790), "免费送你秘籍", 52, INK, prog(t, 21.6, .3))

# (start, end, layout, painter)
SCENES = [
    (0.00, 1.96, "split", sc_hook),
    (1.96, 4.70, "split", sc_calendar),
    (4.70, 6.18, "full", None),
    (6.18, 11.66, "split", sc_news),
    (11.66, 15.76, "split", sc_chart),
    (15.76, 19.22, "split", sc_robot),
    (19.22, 99, "split", sc_cta),
]
# captions: list of (text, accent?) pieces
CAPS = [
    (0.00, 1.96, [("震惊！又一行业", 0), ("被颠覆", 1)]),
    (1.96, 2.90, [("当你还在纠结", 0)]),
    (2.90, 4.70, [("中秋国庆", 0), ("调休怎么弄", 1)]),
    (4.70, 6.18, [("世界已经", 0), ("变天了", 1)]),
    (6.18, 7.78, [("美联储降息", 0), ("50个点", 1)]),
    (7.78, 9.66, [("老板们用AI", 0), ("降本增效", 1)]),
    (9.66, 11.66, [("马斯克", 0), ("Grok-2", 1), ("模型推出", 0)]),
    (11.66, 13.26, [("网红经济遭遇", 0), ("重创", 1)]),
    (13.26, 14.54, [("流量规则", 0), ("改写", 1)]),
    (14.54, 15.76, [("获客机器人", 0), ("崛起", 1)]),
    (15.76, 17.38, [("小助理 + ", 0), ("AI智能体", 1)]),
    (17.38, 19.22, [("每日轻松", 0), ("数千客资", 1)]),
    (19.22, 20.66, [("对这套", 0), ("打法", 1), ("感兴趣", 0)]),
    (20.66, 99, [("评论", 0), ("888", 1), ("免费送你秘籍", 0)]),
]

def caption(d, t, cy):
    for a, b, parts in CAPS:
        if a <= t < b:
            f = F(46); ws = [d.textlength(s, font=f) for s, _ in parts]
            tw = sum(ws); q = ease(prog(t, a, .1))
            d.rounded_rectangle((540 - tw / 2 - 22, cy - 38, 540 + tw / 2 + 22, cy + 38), 10, fill=(32, 32, 32, A(q * .94)))
            x = 540 - tw / 2
            for (s, acc), w in zip(parts, ws):
                d.text((x, cy + 1), s, font=f, fill=(*(GREEN_D if acc else WHITE), A(q)), anchor="lm")
                x += w
            return

def frame(src, t):
    """src: PIL RGB 1080x1920 of the talking head."""
    scene = next(s for s in SCENES if s[0] <= t < s[1])
    if scene[2] == "full":
        img = src.convert("RGBA")
        ov = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(ov)
        caption(d, t, 1290)
        return Image.alpha_composite(img, ov)
    img = Image.new("RGBA", (W, H), (*PAPER, 255))
    # head crop: zoom 1.08, keep head and shoulders in the lower panel
    z = src.resize((round(W * 1.08), round(H * 1.08)), Image.BILINEAR)
    ox = (z.width - W) // 2; oy = 300
    img.paste(z.crop((ox, oy, ox + W, oy + (H - SPLIT))), (0, SPLIT))
    ov = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(ov)
    d.text((540, 80), TAG, font=F(26, False), fill=(*GREY, 255), anchor="mm")
    scene[3](d, t)
    caption(d, t, SPLIT)
    return Image.alpha_composite(img, ov)

def main():
    src_path, out = sys.argv[1], sys.argv[2]
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "csv=p=0", src_path]).decode())
    if "--preview" in sys.argv:
        for ts in sys.argv[sys.argv.index("--preview") + 1].split(","):
            t = float(ts)
            raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", ts, "-i", src_path, "-frames:v", "1",
                                           "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
            frame(Image.frombytes("RGB", (W, H), raw), t).convert("RGB").resize((540, 960)).save(f"{out}_{ts}.png")
        return
    n = int(dur * FPS)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src_path, "-vf", f"scale={W}:{H},fps={FPS}",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "pipe:0", "-i", src_path, "-map", "0:v", "-map", "1:a",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out],
                           stdin=subprocess.PIPE)
    size = W * H * 3
    for i in range(n):
        raw = dec.stdout.read(size)
        if len(raw) < size: break
        enc.stdin.write(frame(Image.frombytes("RGB", (W, H), raw), i / FPS).tobytes())
    enc.stdin.close(); enc.wait(); dec.kill()
    print("done", out)

if __name__ == "__main__":
    main()
