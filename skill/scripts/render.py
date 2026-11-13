"""Render a narrated black/gold vertical film from a storyboard JSON.
Requires Python 3.10+, Pillow, ffmpeg/ffprobe. edge-tts is optional with supplied audio.
"""
import argparse
import asyncio
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 576, 1024, 30
GOLD, WHITE, MUTED = '#e9b957', '#f4f0e8', '#8b8780'


def run(args):
    subprocess.run([str(x) for x in args], check=True)


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=nw=1:nk=1', str(path)], text=True))


def font_path(value):
    candidates = [value, os.environ.get('VIDEO_FONT'), 'C:/Windows/Fonts/msyhbd.ttc',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
        '/System/Library/Fonts/PingFang.ttc']
    for p in candidates:
        if p and Path(p).is_file():
            return str(p)
    raise RuntimeError('Chinese font missing. Pass --font /path/to/CJK-font.ttf')


def ease(t):
    return 1 - (1 - max(0, min(1, t))) ** 3


class Painter:
    def __init__(self, font):
        self.font = font
        self.fonts = {}
        self.images = {}
        self.bg = Image.new('RGB', (W, H), '#11100f')
        d = ImageDraw.Draw(self.bg)
        for x in range(30, W, 48):
            d.line((x, 150, x, 680), fill='#191713')
        for y in range(150, 680, 48):
            d.line((30, y, W-30, y), fill='#191713')

    def f(self, size):
        if size not in self.fonts:
            self.fonts[size] = ImageFont.truetype(self.font, size)
        return self.fonts[size]

    def lines(self, text, size, width):
        result, line = [], ''
        for ch in text:
            if ch == '\n':
                result.append(line); line = ''; continue
            if line and self.f(size).getlength(line + ch) > width:
                result.append(line); line = ''
            line += ch
        return result + ([line] if line else [])

    def text(self, d, text, x, y, size=26, color=WHITE, width=500, center=False):
        for line in self.lines(str(text), size, width):
            px = x - self.f(size).getlength(line)/2 if center else x
            d.text((px, y), line, font=self.f(size), fill=color)
            y += size * 1.5
        return y

    def frame(self, scene, t, length, chapter, index, total, base):
        im = self.bg.copy(); d = ImageDraw.Draw(im)
        self.text(d, f'{chapter:02d}  {scene.get("chapter", "知识解说")}', 32, 128, 17, GOLD)
        d.line((32, 157, 300, 157), fill=GOLD, width=2)
        d.line((32, 872, W-32, 872), fill='#353024', width=2)
        progress = (index + t/length) / total
        d.line((32, 872, 32+(W-64)*progress, 872), fill=GOLD, width=3)
        offset = 25*(1-ease(t/.5))
        self.text(d, scene['title'], 32, 194+offset, 30, WHITE, width=510)
        kind = scene.get('kind', 'title')
        rows = scene.get('items', [])
        if kind == 'timeline':
            d.line((63, 310, 63, 610), fill='#514329', width=3)
            for n, row in enumerate(rows[:4]):
                p = ease((t - .4 - n*.55)/.5)
                if p <= 0: continue
                y = 312+n*88
                d.rounded_rectangle((52, y+6, 74, y+28), radius=4, fill=GOLD)
                self.text(d, row['label'], 95, y, 26, GOLD)
                self.text(d, row.get('text', ''), 95, y+38, 19, WHITE, width=420)
        elif kind == 'bars':
            maximum = max([float(r['value']) for r in rows] or [1]) or 1
            for n, row in enumerate(rows[:4]):
                y=315+n*80; p=ease((t-.4-n*.25)/.9)
                self.text(d, row['label'], 40, y, 21)
                d.rectangle((40, y+35, 40+max(1,420*float(row['value'])/maximum*p), y+49), fill=GOLD)
                self.text(d, str(row['value'])+scene.get('unit',''), 470, y, 20, GOLD, width=70)
        elif kind == 'evidence':
            path = (base / scene['image']).resolve()
            if path not in self.images:
                self.images[path] = Image.open(path).convert('RGB')
            pic = self.images[path].copy(); pic.thumbnail((512, 365))
            x=(W-pic.width)//2; y=290
            im.paste(pic,(x,y)); d=ImageDraw.Draw(im)
            if scene.get('highlight') and t>.7:
                # Normalized x/y/width/height relative to the original source.
                hx,hy,hw,hh=scene['highlight']
                d.rectangle((x+hx*pic.width,y+hy*pic.height,x+(hx+hw)*pic.width,
                    y+(hy+hh)*pic.height), outline=GOLD,width=4)
        elif kind == 'relationship':
            for n, row in enumerate(rows[:3]):
                if t < .3+n*.4: continue
                x=32+n*174
                d.rounded_rectangle((x,320,x+164,410),radius=6,outline=GOLD,width=2)
                self.text(d,row['label'],x+82,340,20,WHITE,width=148,center=True)
                p=ease((t-.6-n*.4)/.5)
                if p>0: d.line((x+82,410,x+82+(288-x-82)*p,410+110*p), fill=GOLD,width=3)
            d.rounded_rectangle((140,520,436,600),radius=8,fill=GOLD)
            self.text(d,scene.get('target','结论'),288,541,27,'#17130d',width=280,center=True)
        else:
            self.text(d,scene.get('headline', scene['title']),W/2,345+offset,48,GOLD,width=490,center=True)
            self.text(d,scene.get('detail',''),W/2,530,23,WHITE,width=490,center=True)
        # Sentence captions distributed by character count; refine with aligned timestamps for production.
        clauses=[c.strip() for c in re.split(r'(?<=[，。！？；])',scene['narration']) if c.strip()]
        weights=sum(len(c) for c in clauses) or 1
        point=min(.999,t/max(.1,length-.4))*weights
        caption=clauses[-1] if clauses else ''
        for clause in clauses:
            point-=len(clause)
            if point<0: caption=clause; break
        self.text(d,caption,W/2,720,25,WHITE,width=510,center=True)
        self.text(d,scene.get('source',''),W/2,815,12,MUTED,width=510,center=True)
        return im


async def narrate(text, voice, path):
    import edge_tts
    await edge_tts.Communicate(text, voice).save(str(path))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('storyboard', type=Path)
    ap.add_argument('--out',type=Path,default=Path('output/final.mp4'))
    ap.add_argument('--font')
    ap.add_argument('--voice',default='zh-CN-YunxiNeural')
    ap.add_argument('--bgm',type=Path)
    args=ap.parse_args()
    for name in ('ffmpeg','ffprobe'):
        if not shutil.which(name): raise RuntimeError(f'{name} is required on PATH')
    data=json.loads(args.storyboard.read_text(encoding='utf-8-sig'))
    scenes=data['scenes']; base=args.storyboard.resolve().parent
    if not scenes: raise ValueError('scenes is empty')
    for s in scenes:
        if not s.get('title') or not s.get('narration'): raise ValueError('Each scene needs title and narration')
        if s.get('kind','title') not in ('title','timeline','bars','evidence','relationship'):
            raise ValueError('Unsupported kind')
        if s.get('kind') == 'bars' and any(float(r['value']) < 0 for r in s.get('items', [])):
            raise ValueError('bars supports nonnegative values only')
    painter=Painter(font_path(args.font)); out=args.out.resolve()
    out.parent.mkdir(parents=True,exist_ok=True)
    work=out.parent/(out.stem+'_work'); work.mkdir(exist_ok=True)
    parts=[]; timings=[]; cursor=0
    for i,s in enumerate(scenes):
        print(f'Scene {i+1}/{len(scenes)}: {s["title"]}',flush=True)
        audio=(base/s['audio']).resolve() if s.get('audio') else work/f'voice-{i:03}.mp3'
        if not s.get('audio'):
            asyncio.run(narrate(s['narration'],args.voice,audio))
        if not audio.is_file(): raise FileNotFoundError(audio)
        seconds=duration(audio)+.5; frames=math.ceil(seconds*FPS); seconds=frames/FPS
        part=work/f'part-{i:03}.mp4'; log=work/f'ffmpeg-{i:03}.log'
        cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}',
            '-r',str(FPS),'-i','pipe:0','-i',str(audio),'-map','0:v','-map','1:a',
            '-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p',
            '-af','apad,loudnorm=I=-16:TP=-1.5:LRA=9','-t',str(seconds),'-c:a','aac','-b:a','160k',str(part)]
        with log.open('wb') as err:
            proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=err)
            try:
                for frame in range(frames):
                    proc.stdin.write(painter.frame(s,frame/FPS,seconds,s.get('chapterNumber',1),i,len(scenes),base).tobytes())
                proc.stdin.close()
                if proc.wait(): raise RuntimeError(log.read_text(errors='replace'))
            except BaseException:
                proc.kill(); proc.wait(); raise
        parts.append(part); timings.append({'title':s['title'],'start':round(cursor,3),'duration':seconds})
        cursor+=seconds
    concat=work/'concat.txt'
    # Generated filenames only; use relative names to avoid Windows path escaping.
    concat.write_text(''.join(f"file '{p.name}'\n" for p in parts),encoding='utf-8')
    joined=work/'joined.mp4'
    run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',concat,'-c','copy',joined])
    if args.bgm:
        run(['ffmpeg','-y','-v','error','-i',joined,'-stream_loop','-1','-i',args.bgm,
            '-filter_complex','[1:a]volume=0.10[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]',
            '-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-movflags','+faststart',out])
    else:
        run(['ffmpeg','-y','-v','error','-i',joined,'-c','copy','-movflags','+faststart',out])
    (out.parent/(out.stem+'_timings.json')).write_text(json.dumps(timings,ensure_ascii=False,indent=2),encoding='utf-8')
    print(str(out),flush=True)


if __name__=='__main__': main()
