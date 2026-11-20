#!/usr/bin/env python3
"""The World Today: Friday 20 November 2026.

A program that draws one newspaper front page summing up the world's
news of Friday 20 November 2026 and writes it to /output/entry.png.

Pure Python 3.13 standard library. No network, no randomness, no clock:
running it twice produces byte-identical output. The page is drawn on a
small raster canvas with a hand-made 5x7 bitmap font (glyphs stored as
bitmask rows) and a hand-written PNG encoder.
"""

import math
import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

# Palette: newsprint paper, ink and flat accent colours.
PAPER = (247, 243, 232)
INK = (18, 18, 18)
CRIMSON = (178, 30, 30)
NAVY = (24, 48, 110)
ROYAL = (34, 84, 200)
SKY = (140, 185, 225)
AMBER = (226, 138, 30)
GOLD = (206, 158, 34)
TEAL = (14, 108, 108)
SLATE = (88, 86, 78)
PALE = (224, 218, 202)
SNOW = (255, 255, 255)
COAL = (12, 12, 20)
LEAF = (36, 118, 58)
SAND = (210, 182, 136)
OCEAN = (44, 104, 158)
PLUM = (96, 52, 128)


class Page:
    """A 1024x1024 RGB canvas backed by one flat bytearray."""

    def __init__(self):
        self.buf = bytearray(bytes(PAPER) * (W * H))

    def set(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            o = (y * W + x) * 3
            self.buf[o] = c[0]
            self.buf[o + 1] = c[1]
            self.buf[o + 2] = c[2]

    def fill(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            o = (yy * W + x0) * 3
            self.buf[o:o + (x1 - x0) * 3] = row

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def frame(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill(x0 - t // 2, y0 - t // 2, t, t, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, c)

    def halo(self, cx, cy, r, c, t=2):
        steps = max(24, r * 6)
        for i in range(steps):
            a = 2.0 * math.pi * i / steps
            self.fill(int(cx + r * math.cos(a)) - t // 2,
                      int(cy + r * math.sin(a)) - t // 2, t, t, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for dy in range(-ry, ry + 1):
            f = 1.0 - (dy * dy) / float(ry * ry)
            dx = int(rx * math.sqrt(max(0.0, f)))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, c)

    def poly(self, pts, c):
        """Scanline fill of a polygon (even-odd rule)."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        y0, y1 = min(ys), max(ys)
        n = len(pts)
        for y in range(y0, y1 + 1):
            xs = []
            for i in range(n):
                x0, yy0 = pts[i]
                x1, yy1 = pts[(i + 1) % n]
                if (yy0 <= y < yy1) or (yy1 <= y < yy0):
                    t = (y - yy0) / float(yy1 - yy0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.hline(int(xs[j]), y, max(1, int(xs[j + 1]) - int(xs[j])), c)

    def burst(self, cx, cy, r1, r2, n, c):
        pts = []
        for i in range(2 * n):
            r = r1 if i % 2 == 0 else r2
            a = math.pi * i / n
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        self.poly(pts, c)

    def png(self):
        raw = bytearray()
        for y in range(H):
            raw.append(0)
            raw += self.buf[y * W * 3:(y + 1) * W * 3]

        def chunk(tag, data):
            out = struct.pack(">I", len(data)) + tag + data
            out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
                + chunk(b"IEND", b""))


PAGE = Page()


# ---------------------------------------------------------------- font
# A 5x7 bitmap font, drawn from scratch: each glyph is seven rows of
# five bits, most significant bit on the left, stored as integers.
GLYPHS = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01111, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b01111),
    "D": (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01111, 0b10000, 0b10000, 0b10111, 0b10001, 0b10001, 0b01110),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    "X": (0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b01010, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b01000, 0b11111),
    "3": (0b11110, 0b00001, 0b00001, 0b01110, 0b00001, 0b00001, 0b11110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b01110, 0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b00100, 0b00100, 0b00100),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00001, 0b01110),
}
GLYPHS.update({
    "a": (0b00000, 0b00000, 0b01111, 0b00001, 0b01111, 0b10001, 0b01111),
    "b": (0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b11110),
    "c": (0b00000, 0b00000, 0b01111, 0b10000, 0b10000, 0b10000, 0b01111),
    "d": (0b00001, 0b00001, 0b01111, 0b10001, 0b10001, 0b10001, 0b01111),
    "e": (0b00000, 0b00000, 0b01110, 0b10001, 0b11111, 0b10000, 0b01110),
    "f": (0b00110, 0b01000, 0b01000, 0b11110, 0b01000, 0b01000, 0b01000),
    "g": (0b00000, 0b01111, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    "h": (0b10000, 0b10000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001),
    "i": (0b00100, 0b00000, 0b01100, 0b00100, 0b00100, 0b00100, 0b01110),
    "j": (0b00010, 0b00000, 0b00110, 0b00010, 0b00010, 0b00010, 0b01100),
    "k": (0b10000, 0b10000, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010),
    "l": (0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "m": (0b00000, 0b00000, 0b11010, 0b10101, 0b10101, 0b10101, 0b10101),
    "n": (0b00000, 0b00000, 0b11110, 0b10001, 0b10001, 0b10001, 0b10001),
    "o": (0b00000, 0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b01110),
    "p": (0b00000, 0b00000, 0b11110, 0b10001, 0b11110, 0b10000, 0b10000),
    "q": (0b00000, 0b00000, 0b01111, 0b10001, 0b01111, 0b00001, 0b00001),
    "r": (0b00000, 0b00000, 0b10110, 0b11001, 0b10000, 0b10000, 0b10000),
    "s": (0b00000, 0b00000, 0b01111, 0b10000, 0b01110, 0b00001, 0b11110),
    "t": (0b01000, 0b01000, 0b11110, 0b01000, 0b01000, 0b01000, 0b00110),
    "u": (0b00000, 0b00000, 0b10001, 0b10001, 0b10001, 0b10011, 0b01101),
    "v": (0b00000, 0b00000, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "w": (0b00000, 0b00000, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010),
    "x": (0b00000, 0b00000, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001),
    "y": (0b00000, 0b00000, 0b10001, 0b10001, 0b01111, 0b00001, 0b01110),
    "z": (0b00000, 0b00000, 0b11111, 0b00010, 0b00100, 0b01000, 0b11111),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b01100),
    ",": (0b00000, 0b00000, 0b00000, 0b00000, 0b01100, 0b01100, 0b01000),
    ":": (0b00000, 0b01100, 0b01100, 0b00000, 0b01100, 0b01100, 0b00000),
    ";": (0b00000, 0b01100, 0b01100, 0b00000, 0b01100, 0b01100, 0b01000),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00000, 0b00100),
    "?": (0b01110, 0b10001, 0b00001, 0b00010, 0b00100, 0b00000, 0b00100),
    "'": (0b00100, 0b00100, 0b01000, 0b00000, 0b00000, 0b00000, 0b00000),
    '"': (0b01010, 0b01010, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000),
    "-": (0b00000, 0b00000, 0b00000, 0b11111, 0b00000, 0b00000, 0b00000),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "&": (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "%": (0b10001, 0b10010, 0b00010, 0b00100, 0b01000, 0b01001, 0b10001),
    "+": (0b00000, 0b00100, 0b00100, 0b11111, 0b00100, 0b00100, 0b00000),
    "=": (0b00000, 0b00000, 0b11111, 0b00000, 0b11111, 0b00000, 0b00000),
    "$": (0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
    "@": (0b01110, 0b10001, 0b10111, 0b10101, 0b10111, 0b10000, 0b01110),
    "*": (0b00000, 0b01010, 0b00100, 0b11111, 0b00100, 0b01010, 0b00000),
    "[": (0b00111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00111),
    "]": (0b11100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b11100),
    "#": (0b01010, 0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b01010),
    "_": (0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111),
})


def glyph(x, y, ch, s, c):
    rows = GLYPHS.get(ch)
    if rows is None:
        return
    for r in range(7):
        bits = rows[r]
        for col in range(5):
            if (bits >> (4 - col)) & 1:
                PAGE.fill(x + col * s, y + r * s, s, s, c)


def text_w(s, scale):
    return len(s) * 6 * scale - scale if s else 0


def text(x, y, s, scale, c):
    cx = x
    for ch in s:
        glyph(cx, y, ch, scale, c)
        cx += 6 * scale
    return cx


def centred(x0, x1, y, s, scale, c):
    text(x0 + (x1 - x0 - text_w(s, scale)) // 2, y, s, scale, c)


def right(x1, y, s, scale, c):
    text(x1 - text_w(s, scale), y, s, scale, c)


def wrap(s, width, scale):
    """Greedy word wrap to a pixel width; returns lines of text."""
    unit = 6 * scale
    per = max(1, width // unit)
    out = []
    for chunk in s.split("\n"):
        words = chunk.split(" ")
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip() if cur else w
            if len(trial) <= per:
                cur = trial
            else:
                if cur:
                    out.append(cur)
                while len(w) > per:
                    out.append(w[:per])
                    w = w[per:]
                cur = w
        if cur:
            out.append(cur)
    return out


def para(x, y, s, width, scale, c, leading=None):
    if leading is None:
        leading = 7 * scale + 2
    for ln in wrap(s, width, scale):
        text(x, y, ln, scale, c)
        y += leading
    return y


# ---------------------------------------------------------------- art

def art_cyclone(x, y, w, h):
    """Cyclone Akvan: spiral arms over a dark sea, coastline below."""
    bands = [(OCEAN, 0), ((36, 88, 140), 1), ((28, 70, 120), 2)]
    bh = h // 3
    for col, i in bands:
        PAGE.fill(x, y + i * bh, w, bh + 1, col)
    cx, cy = x + w // 2, y + h // 2 - 8
    for arm in range(3):
        prev = None
        for step in range(0, 55):
            t = step / 54.0
            ang = t * 4.6 + arm * 2.094
            r = 5 + t * 58
            px = int(cx + r * math.cos(ang))
            py = int(cy + r * math.sin(ang) * 0.82)
            if prev is not None:
                PAGE.line(prev[0], prev[1], px, py, SNOW, 3)
            prev = (px, py)
    PAGE.disc(cx, cy, 8, SNOW)
    PAGE.disc(cx, cy, 4, OCEAN)
    for i in range(8):
        rx = x + 14 + i * 42
        PAGE.line(rx, y + 10, rx - 9, y + 30, (205, 225, 242), 2)
    PAGE.poly([(x, y + h), (x + w, y + h), (x + w, y + h - 16),
               (x + w - 110, y + h - 30), (x + 80, y + h - 20),
               (x, y + h - 28)], SAND)
    PAGE.fill(x, y + h - 3, w, 3, GOLD)


def art_scales(x, y, w, h):
    """ICJ: the scales of justice on a deep blue field."""
    PAGE.fill(x, y, w, h, NAVY)
    cx, cy = x + w // 2, y + h // 2
    PAGE.fill(cx - 2, y + 12, 4, h - 30, GOLD)
    PAGE.fill(cx - 52, y + 16, 104, 4, GOLD)
    PAGE.disc(cx, y + 10, 5, GOLD)
    for sx in (cx - 52, cx + 52):
        PAGE.line(sx, y + 20, sx, y + 34, GOLD, 2)
        PAGE.poly([(sx - 26, y + 34), (sx + 26, y + 34),
                   (sx, y + 56)], GOLD)
        PAGE.fill(sx - 26, y + 34, 52, 3, GOLD)
    PAGE.fill(cx - 30, y + h - 18, 60, 6, GOLD)
    PAGE.fill(cx - 38, y + h - 12, 76, 4, GOLD)
    text(x + 10, y + h - 26, "9-6", 2, SNOW)


def art_flags(x, y, w, h):
    """Shenzhen: three leaders' flags side by side."""
    PAGE.fill(x, y, w, h, PALE)
    fw = w // 3
    # United States: stripes and canton.
    for i in range(7):
        PAGE.fill(x, y + i * (h // 7), fw, h // 7 + 1,
                  CRIMSON if i % 2 == 0 else SNOW)
    PAGE.fill(x, y, fw, h // 2, NAVY)
    for i in range(3):
        for j in range(4):
            PAGE.fill(x + 6 + j * 14, y + 6 + i * 10, 3, 3, SNOW)
    # China: red field, gold stars.
    PAGE.fill(x + fw, y, fw, h, CRIMSON)
    PAGE.burst(x + fw + fw // 3, y + h // 3, 10, 4, 5, GOLD)
    for sx, sy in ((x + fw + fw - 16, y + 10), (x + fw + fw - 16, y + 26),
                   (x + fw + fw - 30, y + 8)):
        PAGE.disc(sx, sy, 3, GOLD)
    # Russia: white, blue, red bands.
    PAGE.fill(x + 2 * fw, y, fw, h // 3, SNOW)
    PAGE.fill(x + 2 * fw, y + h // 3, fw, h // 3, ROYAL)
    PAGE.fill(x + 2 * fw, y + 2 * h // 3, fw, h - 2 * h // 3, CRIMSON)
    PAGE.frame(x, y, w, h, INK, 1)


def art_embassy(x, y, w, h):
    """Kyiv: a columned embassy front, a cracked window, smoke."""
    PAGE.fill(x, y, w, h, SKY)
    PAGE.fill(x, y + h - 14, w, 14, (110, 140, 90))
    cx = x + w // 2
    PAGE.fill(cx - 46, y + 8, 92, 10, (226, 222, 210))
    PAGE.poly([(cx - 52, y + 18), (cx + 52, y + 18), (cx, y + 2)], (226, 222, 210))
    for i in range(4):
        colx = cx - 42 + i * 24
        PAGE.fill(colx, y + 18, 7, h - 36, SNOW)
    PAGE.fill(cx - 48, y + h - 22, 96, 5, (226, 222, 210))
    # Shattered window: dark pane with a zigzag crack.
    PAGE.fill(x + 12, y + 22, 26, 22, (40, 50, 70))
    PAGE.line(x + 14, y + 24, x + 24, y + 34, SNOW, 1)
    PAGE.line(x + 24, y + 34, x + 18, y + 42, SNOW, 1)
    PAGE.line(x + 24, y + 34, x + 34, y + 42, SNOW, 1)
    # Smoke drifting from the roof.
    PAGE.disc(x + w - 26, y + 12, 7, (150, 150, 150))
    PAGE.disc(x + w - 16, y + 6, 5, (170, 170, 170))
    PAGE.disc(x + w - 34, y + 5, 4, (150, 150, 150))


def art_rocket(x, y, w, h):
    """Iran: a missile climbing past a warning ring."""
    PAGE.fill(x, y, w, h, COAL)
    for sx, sy in ((10, 8), (40, 20), (70, 6), (100, 24), (130, 10),
                   (160, 28), (190, 12), (26, 40), (150, 44)):
        if x + sx < x + w - 4 and y + sy < y + h - 4:
            PAGE.fill(x + sx, y + sy, 2, 2, SNOW)
    cx = x + w // 2
    PAGE.halo(cx, y + h // 2 + 6, 26, CRIMSON, 2)
    PAGE.halo(cx, y + h // 2 + 6, 18, AMBER, 2)
    # Rocket body, nose up.
    PAGE.poly([(cx, y + 6), (cx + 9, y + 24), (cx + 9, y + h - 22),
               (cx - 9, y + h - 22), (cx - 9, y + 24)], SNOW)
    PAGE.poly([(cx, y + 6), (cx + 9, y + 24), (cx - 9, y + 24)], CRIMSON)
    PAGE.poly([(cx - 9, y + h - 30), (cx - 20, y + h - 12),
               (cx - 9, y + h - 16)], CRIMSON)
    PAGE.poly([(cx + 9, y + h - 30), (cx + 20, y + h - 12),
               (cx + 9, y + h - 16)], CRIMSON)
    PAGE.fill(cx - 9, y + h - 22, 18, 4, SLATE)
    PAGE.burst(cx, y + h - 10, 12, 5, 6, AMBER)
    PAGE.burst(cx, y + h - 8, 7, 3, 6, GOLD)


def art_controller(x, y, w, h):
    """GTA VI: a neon skyline behind a game controller."""
    bands = [(PLUM, 0), ((150, 60, 120), 1), ((60, 40, 110), 2),
             ((30, 30, 90), 3)]
    bh = h // 4
    for col, i in bands:
        PAGE.fill(x, y + i * bh, w, bh + 1, col)
    PAGE.disc(x + w - 34, y + 16, 10, (255, 220, 130))
    base = y + h - 14
    heights = [16, 26, 20, 34, 24, 30, 18, 28]
    bw = w // len(heights)
    for i, hh in enumerate(heights):
        PAGE.fill(x + i * bw + 2, base - hh, bw - 4, hh, COAL)
    text(x + 12, y + 8, "VI", 5, SNOW)
    # Controller body.
    cx, cy = x + w // 2, y + h - 34
    PAGE.poly([(cx - 58, cy - 8), (cx + 58, cy - 8), (cx + 66, cy + 10),
               (cx + 40, cy + 16), (cx - 40, cy + 16), (cx - 66, cy + 10)],
              (20, 20, 30))
    PAGE.frame(cx - 58, cy - 8, 116, 24, (120, 120, 140), 1)
    PAGE.fill(cx - 44, cy - 2, 4, 12, GOLD)
    PAGE.fill(cx - 38, cy + 2, 12, 4, GOLD)
    for dx, dy, col in ((34, -2, CRIMSON), (44, 4, LEAF),
                        (34, 8, ROYAL), (24, 4, GOLD)):
        PAGE.disc(cx + dx, cy + dy, 3, col)
    PAGE.disc(cx - 12, cy + 6, 4, (90, 90, 110))
    PAGE.disc(cx + 8, cy + 6, 4, (90, 90, 110))


def art_gavel(x, y, w, h):
    """Seoul: a judge's gavel on its block."""
    PAGE.fill(x, y, w, h, (96, 70, 50))
    cx, cy = x + w // 2, y + h // 2 - 6
    PAGE.line(cx - 46, cy - 18, cx + 40, cy + 26, (150, 105, 60), 6)
    PAGE.fill(cx - 52, cy - 30, 34, 20, (120, 80, 40))
    PAGE.fill(cx - 52, cy - 30, 34, 4, (170, 125, 75))
    PAGE.fill(cx - 52, cy - 14, 34, 4, (170, 125, 75))
    PAGE.disc(cx + 44, cy + 28, 4, (120, 80, 40))
    PAGE.ellipse(cx + 6, y + h - 14, 46, 8, (170, 125, 75))
    PAGE.ellipse(cx + 6, y + h - 16, 46, 8, (150, 105, 60))
    text(x + 8, y + 6, "15 YRS", 2, SNOW)
    PAGE.line(x + 8, y + 22, x + 62, y + 22, CRIMSON, 2)


def art_cricket(x, y, w, h):
    """Wellington: bat, ball and stumps on a green outfield."""
    PAGE.fill(x, y, w, h, (52, 130, 70))
    PAGE.fill(x, y + h - 18, w, 18, (40, 105, 55))
    # Pitch strip.
    PAGE.fill(x + w // 2 - 26, y + 8, 52, h - 8, (196, 172, 120))
    # Stumps.
    for i in range(3):
        PAGE.fill(x + w // 2 - 12 + i * 10, y + 12, 4, 18, GOLD)
    PAGE.fill(x + w // 2 - 12, y + 10, 28, 3, GOLD)
    # Bat, leaning across the pitch.
    PAGE.poly([(x + w // 2 + 4, y + 30), (x + w // 2 + 16, y + 26),
               (x + w // 2 + 34, y + h - 26), (x + w // 2 + 22, y + h - 22)],
              (222, 200, 160))
    PAGE.line(x + w // 2 + 10, y + 28, x + w // 2 - 2, y + 12,
              (160, 120, 80), 4)
    # Red ball.
    PAGE.disc(x + 26, y + h - 34, 7, CRIMSON)
    PAGE.halo(x + 26, y + h - 34, 7, SNOW, 1)
    text(x + w - 52, y + h - 22, "146*", 2, SNOW)


# ---------------------------------------------------------------- stories

HERO_KICKER = "INDIA - CYCLONE AKVAN - LANDFALL TODAY"
HERO_HEAD = ["AKVAN SLAMS ASHORE", "AS 300,000 FLEE"]
HERO_BODY = ("Severe Cyclone Akvan crosses the Odisha coast near "
             "Gopalpur at noon, winds to 110 kmph. Over 300,000 people "
             "have fled to shelters; 69 trains cancelled.")
HERO_STRAP = "RED ALERT: 11 DISTRICTS - SCHOOLS SHUT - 423 RESCUE TEAMS OUT"

ROW2 = [
    (art_scales, "THE HAGUE - WORLD COURT",
     ["WORLD COURT: MYANMAR", "GUILTY OF GENOCIDE"],
     "The Hague rules 9-6 that Myanmar's 2017 crackdown was genocide, "
     "the first time the court has held a state guilty. Reparations are "
     "ordered; 700,000 Rohingya fled to Bangladesh."),
    (art_flags, "SHENZHEN - APEC",
     ["THREE LEADERS, ONE", "PEACE DECLARATION"],
     "Trump, Xi and Putin meet in Shenzhen and declare a nuclear war "
     "'cannot be won'. They pledge UN reform and more oil as APEC "
     "adopts its Shenzhen Outlook."),
    (art_embassy, "KYIV - WAR IN UKRAINE",
     ["KYIV STRIKES HIT", "TWO EMBASSIES"],
     "Russian daytime strikes kill one and wound five in Kyiv. The "
     "Austrian and Dutch embassies are damaged, a cathedral's windows "
     "shatter, and 98 drones are fired."),
]

ROW3 = [
    (art_rocket, "WASHINGTON - IRAN",
     ["TRUMP WEIGHS", "NEW IRAN STRIKES"],
     "Netanyahu urges a four-to-seven-day joint bombing campaign. "
     "Trump has not decided; US bombers sit on 96-hour notice."),
    (art_controller, "GAMING - GTA VI",
     ["GTA VI: 19M", "COPIES, DAY ONE"],
     "Sensor Tower puts day-one sales at $1.84bn. Metacritic 99; six "
     "million watched the streams. Take-Two shares slip 2.7%."),
    (art_gavel, "SEOUL - MARTIAL LAW",
     ["SEOUL: EX-PM'S", "TERM OVERTURNED"],
     "The top court quashes Han Duck-soo's 15-year term and orders a "
     "retrial. Martial law itself was illegal, the judges rule."),
    (art_cricket, "WELLINGTON - CRICKET",
     ["NICHOLLS 146*", "AS NZ PASS 300"],
     "Day two in Wellington: Nicholls is unbeaten on 146 at lunch, NZ "
     "317 for 6. Phillips fell for 108 after a 200-run stand."),
]

BRIEFS = [
    ("ANT DEBUTS", "Anthropic opens at $111.50, up 34%, and closes up 17% at $97.17."),
    ("WALL ST TUMBLES", "Dow falls 2.2% below 50,000; S&P down 2%; Nasdaq down 2.3%."),
    ("CARACAS DEAL", "US and Venezuela sign a military pact; joint training and intel sharing."),
    ("YONGBYON", "IAEA says North Korea built a new uranium enrichment extension."),
    ("FIJI", "Nationwide disaster declared over El Nino drought; F$20m set aside for water."),
    ("ROYALS", "William and Kate meet Modi in Delhi to end their three-day India tour."),
    ("CRIMEA BRIDGE", "Hit again overnight; rail traffic halted in the third strike this week."),
    ("BLACK SEA", "LPG tanker Gas Husky hit by four projectiles and sank; 19 crew rescued."),
    ("SETTLERS", "Australia sanctions three people and four groups over West Bank building."),
    ("VOYAGER 1", "The probe is now a full light-day from Earth, 48 years after launch."),
    ("GAZA", "Israeli tanks cross the Yellow Line in central Gaza; 1,600 killed since the truce."),
    ("LEBANON", "IDF strikes a Hezbollah arms site at Janta, in the Beqaa valley."),
    ("IRAN ARSENAL", "US intel puts Tehran's missiles at 1,500 to 2,500, a low-confidence call."),
    ("APEC", "Leaders adopt the Shenzhen Outlook and pledge joint action on digital risks."),
    ("BERLIN", "Ukraine's backers meet and urge a winter energy ceasefire."),
    ("SUDAN", "Court hands RSF chief Hemedti a second death sentence over a $396m scandal."),
    ("SUDAN", "UN says airstrikes displaced 2,500 people this week in West Kordofan."),
    ("EBOLA", "Six months on, the DRC outbreak is still out of control, the NRC warns."),
    ("CONGO", "Sassou-Nguesso mediates to reconcile Tshisekedi and Ruto."),
    ("NIGERIA", "Two death-row inmates escape a Kwara prison; police free 20 abducted in Zamfara."),
    ("VAN GOGH", "'Chataigniers en fleurs' sells for a record $190.4m at Sotheby's."),
    ("AMD", "Shares fall 9.2% after a short seller takes aim at the chipmaker."),
    ("BITCOIN", "Flat near $62,640 as traders watch the Anthropic debut."),
    ("WALMART", "Retail giant raises its outlook as shoppers keep spending."),
    ("TAKE-TWO", "Shares slip 2.7% on GTA VI launch day, despite record sales."),
    ("CRICKET", "England beat Australia by 97 runs in the third ODI at Hobart."),
    ("BURKINA FASO", "Rights group says the junta is targeting critics in exile."),
    ("UN", "Guterres welcomes the ICJ verdict on Myanmar as historic."),
    ("FAITH", "Pew projects Islam will be the world's largest faith by 2035."),
    ("TOKYO TALKS", "India and Japan hold defence talks as ties deepen."),
]

STATS = [
    ("300,000+", "EVACUATED AS AKVAN MAKES LANDFALL"),
    ("$1.84BN", "GTA VI DAY-ONE SALES, ESTIMATED"),
    ("$190.4M", "RECORD PRICE FOR A VAN GOGH"),
    ("9-6", "ICJ VOTE: MYANMAR GUILTY OF GENOCIDE"),
]


def brief_lines(tag, body, width=312):
    """Wrap a brief so the first line leaves room for its red tag."""
    tagw = text_w(tag + ": ", 1)
    words = body.split(" ")
    lines = []
    cur = ""
    limit = max(1, (width - tagw) // 6)
    for w in words:
        trial = (cur + " " + w).strip() if cur else w
        if len(trial) <= limit:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            limit = width // 6
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_brief(x, y, tag, body):
    lines = brief_lines(tag, body)
    tagw = text_w(tag + ": ", 1)
    text(x, y, tag + ":", 1, CRIMSON)
    if lines:
        text(x + tagw, y, lines[0], 1, INK)
        for i, ln in enumerate(lines[1:], 1):
            text(x, y + 9 * i, ln, 1, INK)
    return y + 9 * max(1, len(lines)) + 3


# ---------------------------------------------------------------- layout

def build():
    # Masthead.
    PAGE.hline(24, 14, 976, INK, 2)
    PAGE.hline(24, 18, 976, INK, 1)
    centred(24, 1000, 26, "THE WORLD TODAY", 6, INK)
    text(24, 74, "FRIDAY, 20 NOVEMBER 2026", 2, INK)
    right(1000, 74, "38 STORIES - ONE IMAGE", 2, CRIMSON)
    PAGE.hline(24, 92, 976, INK, 2)
    PAGE.hline(24, 96, 976, INK, 1)

    # Hero: Cyclone Akvan.
    text(24, 108, HERO_KICKER, 1, CRIMSON)
    yy = 126
    for ln in HERO_HEAD:
        text(24, yy, ln, 3, INK)
        yy += 23
    para(24, 180, HERO_BODY, 600, 2, INK)
    text(24, 240, HERO_STRAP, 1, CRIMSON)
    art_cyclone(648, 104, 352, 164)
    PAGE.frame(648, 104, 352, 164, INK, 1)
    PAGE.hline(24, 272, 976, INK, 2)

    # Row 2: three mains.
    cols2 = [(24, 312), (356, 312), (688, 312)]
    for (art, kicker, head, body), (cx, cw) in zip(ROW2, cols2):
        art(cx, 280, cw, 64)
        PAGE.frame(cx, 280, cw, 64, INK, 1)
        text(cx, 350, kicker, 1, CRIMSON)
        yy = 366
        for ln in head:
            text(cx, yy, ln, 2, INK)
            yy += 16
        para(cx, 404, body, cw, 1, INK)
    PAGE.vline(344, 280, 172, SLATE, 1)
    PAGE.vline(676, 280, 172, SLATE, 1)
    PAGE.hline(24, 456, 976, INK, 2)

    # Row 3: four mains.
    cols3 = [(24, 232), (272, 232), (520, 232), (768, 232)]
    for (art, kicker, head, body), (cx, cw) in zip(ROW3, cols3):
        art(cx, 464, cw, 56)
        PAGE.frame(cx, 464, cw, 56, INK, 1)
        text(cx, 526, kicker, 1, CRIMSON)
        yy = 540
        for ln in head:
            text(cx, yy, ln, 2, INK)
            yy += 16
        para(cx, 578, body, cw, 1, INK)
    for vx in (264, 512, 760):
        PAGE.vline(vx, 464, 172, SLATE, 1)
    PAGE.hline(24, 640, 976, INK, 2)

    # Briefs: three columns of ten.
    text(24, 648, "AROUND THE WORLD - 30 MORE STORIES", 2, INK)
    PAGE.hline(24, 666, 976, INK, 1)
    for ci in range(3):
        bx = 24 + ci * 332
        by = 676
        for tag, body in BRIEFS[ci * 10:(ci + 1) * 10]:
            by = draw_brief(bx, by, tag, body)
        if ci < 2:
            PAGE.vline(bx + 320, 676, 206, SLATE, 1)

    # Footer: by the numbers.
    PAGE.hline(24, 890, 976, INK, 2)
    centred(24, 1000, 900, "BY THE NUMBERS", 2, INK)
    for i, (num, label) in enumerate(STATS):
        sx = 24 + i * 248
        centred(sx, sx + 232, 926, num, 3, CRIMSON)
        lab = wrap(label, 232, 1)
        ly = 952
        for ln in lab:
            centred(sx, sx + 232, ly, ln, 1, INK)
            ly += 9
    centred(24, 1000, 988,
            "Drawn by a program. Sources: Reuters, AP, BBC, NYT, IMD, ICJ, "
            "Cricinfo. Stories first reported 18-20 Nov 2026.",
            1, SLATE)
    PAGE.hline(24, 1006, 976, INK, 1)


def main():
    build()
    out = Path(os.environ.get("ENTRY_OUTPUT", "/output/entry.png"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(PAGE.png())


if __name__ == "__main__":
    main()
