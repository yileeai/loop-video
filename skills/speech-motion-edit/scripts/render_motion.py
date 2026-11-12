"""Compose data-driven portrait motion graphics over a prepared B-roll track."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import tempfile
import wave

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1170, 30
GOLD = (249, 207, 73)
CREAM = (244, 242, 234)
MUTED = (164, 161, 149)
DIM = (92, 87, 74)
INK = (21, 21, 21)
FONT = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")
def progress(t, start, length=.38):
    return min(1, max(0, (t-start)/length))

def ease(p):
    return 1 - (1-p)**3

class Graphic:
    def __init__(self, font_file, timeline):
        self.timeline = timeline
        self.font_file = font_file
        self.fonts = {}
        self.canvas = Image.new("RGBA", (W, H))
        shadow = ImageDraw.Draw(self.canvas)
        shadow.rounded_rectangle((58, 356, 1024, 929), 61, fill=(0,0,0,198))
        self.canvas = self.canvas.filter(ImageFilter.GaussianBlur(16))
        self.fixed = ImageDraw.Draw(self.canvas)
        self.fixed.rounded_rectangle((54, 345, 1026, 912), 57, fill=(*INK,255), outline=(57,54,44,255), width=2)
        self.fixed.rounded_rectangle((95,389,105,399),3,fill=(*GOLD,255))
        self.label(self.fixed, (119,383), timeline.get("header", ""), 22, MUTED)
        self.fixed.line((95,425,985,425),fill=(62,56,44,255),width=1)
        self.fixed.line((95,850,985,850),fill=(62,56,44,255),width=1)
        self.label(self.fixed, (97,870), timeline.get("source", ""), 19, MUTED)

    def font(self, size, bold=True):
        key = (size,bold)
        if key not in self.fonts:
            try:
                self.fonts[key] = ImageFont.truetype(str(self.font_file), size, index=int(bold))
            except OSError:
                self.fonts[key] = ImageFont.truetype(str(self.font_file), size)
        return self.fonts[key]

    def label(self, draw, xy, text, size, rgb=CREAM, alpha=255, anchor="lt", bold=True, stroke=0):
        draw.text(xy,text,font=self.font(size,bold),fill=(*rgb,alpha),anchor=anchor,
                  stroke_width=stroke,stroke_fill=(*rgb,alpha))

    def enter_label(self, draw, xy, text, size, rgb, t, start, duration=.42, stroke=0):
        p=ease(progress(t,start,duration))
        if p:
            self.label(draw,(xy[0]+round((1-p)*26),xy[1]),text,size,rgb,round(255*p),stroke=stroke)

    def connector(self, draw, points, p):
        if not p:
            return
        lengths=[math.dist(a,b) for a,b in zip(points,points[1:])]
        remaining=sum(lengths)*p
        end=points[0]
        for a,b,length in zip(points,points[1:],lengths):
            step=min(1,remaining/length)
            end=tuple(round(v+(w-v)*step) for v,w in zip(a,b))
            draw.line((a,end),fill=(*GOLD,255),width=2)
            if step<1:
                break
            remaining-=length
        x,y=end
        draw.ellipse((x-4,y-4,x+4,y+4),fill=(*GOLD,255))

    def tile(self, draw, x,y,w,h, title, detail, p, active=True):
        if not p:
            return
        q=ease(p)
        y+=round((1-q)*19)
        strength=round(q*255)
        fill=(43,37,25) if active else (33,32,28)
        border=(132,109,51) if active else (66,63,52)
        draw.rounded_rectangle((x,y,x+w,y+h),16,fill=(*fill,strength),outline=(*border,strength),width=2)
        self.label(draw,(x+20,y+18),title,31,GOLD if active else CREAM,strength)
        if detail:
            self.label(draw,(x+20,y+62),detail,22,MUTED,strength)

    def counter(self, draw, t, counter):
        p = ease(progress(t, counter["at"], .82))
        if not p:
            return
        value = str(round(counter["value"] * p))
        self.label(draw, (101, 670), value, 98, GOLD, stroke=1)
        unit_x = 128 + round(draw.textlength(value, font=self.font(98)))
        self.label(draw, (unit_x, 704), counter.get("unit", ""), 40, CREAM)
        self.label(draw, (105, 797), counter.get("note", ""), 24, MUTED)

    def chain(self, draw, t, nodes):
        width = 245
        step = (884 - width) / max(1, len(nodes)-1)
        for index, node in enumerate(nodes):
            x = round(98 + index * step)
            if index:
                previous_right = round(98 + (index-1) * step) + width
                self.connector(draw, [(previous_right, 764), (x, 764)], progress(t, node["at"]-.3, .3))
            self.tile(draw, x, 710, width, 108, node["title"], node.get("detail", ""),
                      progress(t, node["at"], .42))

    def stack(self, draw, t, nodes):
        for i, node in enumerate(nodes):
            y = 554 + i * 87
            p = ease(progress(t, node["at"], .39))
            if i:
                self.connector(draw, [(122, y-28), (122, y+28)], progress(t, node["at"]-.21, .30))
            if p:
                alpha = round(255 * p)
                dy = round((1-p)*17)
                draw.rounded_rectangle((153,y+dy,983,y+dy+68),13,
                                       fill=(32,30,25,alpha), outline=(104,87,45,alpha), width=2)
                draw.ellipse((105,y+17,139,y+51), fill=(*GOLD,alpha))
                self.label(draw,(122,y+35),str(i+1),23,INK,alpha,anchor="mm")
                self.label(draw,(175,y+dy+17),node["title"],32,CREAM,alpha)
                self.label(draw,(956,y+dy+22),node.get("detail", ""),25,MUTED,alpha,anchor="rt")

    def tree(self, draw, t, root, nodes):
        root_width = 884 if root.get("wide") else 318
        root_x = round((W-root_width)/2)
        self.tile(draw, root_x, 549, root_width, 102, root["title"], root.get("detail", ""),
                  progress(t, root["at"], .45))
        width = (884 - (len(nodes)-1)*14) // len(nodes)
        for i, node in enumerate(nodes):
            x = 98 + i*(width+14)
            mid = x + width//2
            points = [(540,651),(540,677),(mid,677),(mid,716)] if mid!=540 else [(540,651),(540,716)]
            self.connector(draw, points, progress(t,node["at"]-.20,.46))
            self.tile(draw,x,715,width,108,node["title"],node.get("detail",""),progress(t,node["at"],.43))

    def render(self, t):
        canvas = self.canvas.copy()
        overlay = Image.new("RGBA", canvas.size)
        draw = ImageDraw.Draw(overlay)
        scenes = self.timeline["scenes"]
        chapter = max(i for i, scene in enumerate(scenes) if scene["start"] <= t)
        scene = scenes[chapter]
        for title in scene.get("titles", []):
            self.enter_label(draw, (98, title["y"]), title["text"], title["size"],
                             GOLD if title.get("accent") else CREAM, t, title["at"], stroke=1)
        if "counter" in scene:
            self.counter(draw, t, scene["counter"])
        layout = scene.get("layout")
        if layout == "chain":
            self.chain(draw, t, scene["nodes"])
        elif layout == "stack":
            self.stack(draw, t, scene["nodes"])
        elif layout == "tree":
            self.tree(draw, t, scene["root"], scene["nodes"])
        p = ease(progress(t, scene["start"], .25))
        width = round(887 * (chapter+p) / len(scenes))
        draw.line((96,849,96+width,849),fill=(*GOLD,255),width=2)
        self.label(draw,(981,870),f"{chapter+1:02d} / {len(scenes):02d}",19,MUTED,anchor="rt")
        for cue in self.timeline.get("captions", []):
            if cue["start"] <= t < cue["end"]:
                self.caption(draw, t, cue["start"], cue["text"], cue.get("accent",""))
                break
        return Image.alpha_composite(canvas, overlay)

    def caption(self,d,t,start,plain,emphasis):
        p=ease(progress(t,start,.16))
        size=49
        widths=[d.textlength(piece,font=self.font(size)) for piece in (plain,emphasis)]
        x=round((W-sum(widths))/2)
        y=1060+round(12*(1-p))
        for s,w,color in zip((plain,emphasis),widths,(CREAM,GOLD)):
            if s:
                d.text((x,y),s,font=self.font(size),anchor="lt",fill=(*color,255),
                       stroke_width=6,stroke_fill=(20,20,20,230))
                self.label(d,(x,y),s,size,color,stroke=1)
            x+=round(w)

def make_matte(path):
    """A neutral grid on top, with a lower gradient that reveals B-roll."""
    matte = Image.new("RGBA", (W, 1920))
    draw = ImageDraw.Draw(matte)
    for y in range(1920):
        if y < 905:
            gray, alpha = round(110 - y*.035), 255
        else:
            p = min(1, (y-905)/735)
            gray = round(78*(1-p)**2.6)
            alpha = round(255*(1-p*p*(3-2*p)))
        draw.line((0, y, W, y), fill=(gray, gray, gray, alpha))
    grid = Image.new("RGBA", matte.size)
    draw = ImageDraw.Draw(grid)
    for x in range(16, W, 31):
        draw.line((x, 0, x, 1450), fill=(255,255,255,10))
    for y in range(16, 1450, 31):
        draw.line((0, y, W, y), fill=(255,255,255,10))
    fade = Image.new("L", matte.size)
    draw = ImageDraw.Draw(fade)
    for y in range(1450):
        draw.line((0,y,W,y),fill=round(255*(1-(y/1450)**3)))
    grid.putalpha(ImageChops.multiply(grid.getchannel("A"), fade))
    matte.alpha_composite(grid)
    matte.save(path)

def validate_timeline(timeline, duration):
    starts = [scene["start"] for scene in timeline["scenes"]]
    if not starts or starts[0] != 0 or starts != sorted(set(starts)) or starts[-1] >= duration:
        raise ValueError("Scene starts must increase from zero and stay within the narration")
    limits = {"chain":3, "stack":3, "tree":4}
    for scene in timeline["scenes"]:
        layout = scene.get("layout")
        if layout and (layout not in limits or not 1 <= len(scene["nodes"]) <= limits[layout]):
            raise ValueError(f"Unsupported layout or node count at {scene['start']}s")
    end = 0
    for cue in timeline.get("captions", []):
        if not end <= cue["start"] < cue["end"] <= duration:
            raise ValueError("Caption cues must be ordered, nonoverlapping and within the narration")
        end = cue["end"]

def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True, help="Full-canvas B-roll MP4")
    parser.add_argument("--audio", type=Path, required=True, help="PCM narration WAV")
    parser.add_argument("--timeline", type=Path, required=True, help="Timeline JSON")
    parser.add_argument("--output", type=Path, required=True, help="Output MP4")
    parser.add_argument("--font", type=Path, default=FONT, help="Chinese font TTC/TTF")
    parser.add_argument("--matte", type=Path, help="Optional 1080×1920 alpha PNG")
    parser.add_argument("--speed", type=float, default=1.0, help="Playback rate, from 0.5 to 2.0")
    args = parser.parse_args()
    if not .5 <= args.speed <= 2:
        parser.error("--speed must be between 0.5 and 2.0")
    if args.output.resolve() in {p.resolve() for p in (args.base,args.audio,args.timeline,args.matte) if p}:
        parser.error("Choose a new output path")
    timeline = json.loads(args.timeline.read_text(encoding="utf-8"))
    with wave.open(str(args.audio)) as audio:
        frames = math.ceil(audio.getnframes()*FPS/audio.getframerate())
    duration = frames/FPS
    validate_timeline(timeline, duration)
    graphic = Graphic(args.font, timeline)
    with tempfile.TemporaryDirectory(prefix="speech-motion-") as temp:
        matte = args.matte or Path(temp)/"matte.png"
        if args.matte is None:
            make_matte(matte)
        draft = args.output if args.speed == 1 else Path(temp)/"normal-speed.mp4"
        command = ["ffmpeg","-v","error","-y","-i",str(args.base),"-loop","1","-framerate","30","-i",str(matte),
                   "-f","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0",
                   "-i",str(args.audio),"-filter_complex_threads","2","-filter_complex",
                   "[0:v]fps=30,setsar=1[base];[base][1:v]overlay=0:0[b];[b][2:v]overlay=0:0,format=yuv420p[v]",
                   "-map","[v]","-map","3:a","-t",f"{duration:.6f}","-c:v","libx264","-threads","5",
                   "-preset","veryfast","-crf","18","-c:a","aac","-b:a","160k","-movflags","+faststart",str(draft)]
        with subprocess.Popen(command, stdin=subprocess.PIPE) as render:
            for i in range(frames):
                render.stdin.write(graphic.render(i/FPS).tobytes())
            render.stdin.close()
            if render.wait():
                raise RuntimeError("FFmpeg did not complete the render")
        if args.speed != 1:
            rate = args.speed
            subprocess.run(["ffmpeg","-v","error","-y","-i",str(draft),"-filter_complex",
                            f"[0:v]setpts=PTS/{rate},fps=30[v];[0:a]atempo={rate}[a]",
                            "-map","[v]","-map","[a]","-c:v","libx264","-preset","veryfast","-crf","18",
                            "-c:a","aac","-b:a","160k","-movflags","+faststart",str(args.output)],check=True)
    print(f"{args.output}: about {duration/args.speed:.2f} s at {args.speed:g}×")

if __name__ == "__main__":
    run()
