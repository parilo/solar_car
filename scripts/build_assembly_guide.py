"""Generate the English panel assembly PDF. Requires reportlab and Pillow."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.colors import HexColor

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'docs/panel-assembly.pdf'
IMAGES = ROOT / 'site/solar-car-assets'
c = canvas.Canvas(str(OUT), pagesize=landscape(A4), invariant=1)
c.setTitle('BF5 - Panel frames and posts: assembly guide')
c.setAuthor('Anton Pechenko')

def text(x, y, value, size=10, bold=False):
    c.setFont('Helvetica-Bold' if bold else 'Helvetica', size)
    c.setFillColor(HexColor('#173c37'))
    c.drawString(x * mm, y * mm, value)

def para(x, y, value, width, size=9.4):
    line = ''
    for word in value.split():
        candidate = (line + ' ' + word).strip()
        if line and pdfmetrics.stringWidth(candidate, 'Helvetica', size) > width * mm:
            text(x, y, line, size)
            y -= 4.7
            line = word
        else:
            line = candidate
    if line:
        text(x, y, line, size)
        y -= 4.7
    return y

def picture(name, x, y, width, height):
    c.drawImage(str(IMAGES / (name + '.webp')), x * mm, y * mm,
                width * mm, height * mm, preserveAspectRatio=True, anchor='c')

text(13, 193, 'BF5 · snap joints at both ends of each post', 21, True)
text(13, 183, '2 frames + 8 one-piece posts. Accepted upper fit: SC1 post 1 + socket 6.', 10)
picture('mounts', 7, 72, 180, 103)
picture('joint', 185, 76, 99, 97)
text(191, 75, 'Lower joint: sectional view', 10, True)
para(191, 67, 'The post rests on the chassis; two prongs latch underneath it. '
     'Squeeze the prongs from below to release the joint.', 92, 9)
text(13, 64, 'STL files contain no built-in supports', 12, True)
text(13, 55, 'solar-car-bf5-frames.stl: both frames. solar-car-bf5-posts.stl: all eight posts.', 10)
para(13, 46, 'Individual files are also included: one F frame, one R frame, and two of each F1/F2/R1/R2 post. '
     'Use either the combined layouts or the individual files. Units: mm; scale: 100%. Set orientation and supports in your slicer.', 271)
para(13, 32, 'Insert the posts into the empty frames from below, with the upper latch tongues facing the central opening. '
     'Align the four lower stems with the chassis slots and press near each post. Install the panels last.', 271)
para(13, 18, 'November 22, 2026: the builder reported that the car was assembled and working. V2.10 chassis with BF5 mounts. '
     'Choose slicing settings for your printer. Speed and endurance have not been measured.', 271, 8.5)
c.save()
print(OUT)
