"""Carte prototype 100 % Kivy (Canvas).

Conçue pour être remplacée plus tard par une vraie tuile cartographique :
l'interface publique (set_data) reste identique.
"""
import math

from kivy.animation import Animation
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.metrics import dp, sp
from kivy.properties import ListProperty, NumericProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout

from utils.constants import (BACKGROUND, BORDER, CYAN, DANGER, SURFACE_LIGHT,
                             TEXT, WARNING)

TYPE_COLORS = {
    "Hôpital": DANGER,
    "Clinique": CYAN,
    "Centre médical": WARNING,
}


class MockMapWidget(FloatLayout):
    patient = ObjectProperty(None, allownone=True)   # (lat, lon, adresse)
    facilities = ListProperty([])                    # [(Facility, distance)]
    pulse = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(patient=lambda *a: self._redraw(),
                  facilities=lambda *a: self._redraw(),
                  size=lambda *a: self._redraw(),
                  pos=lambda *a: self._redraw(),
                  pulse=lambda *a: self._redraw())
        self._anim = Animation(pulse=1.0, duration=1.0) + Animation(
            pulse=0.0, duration=1.0)
        self._anim.repeat = True
        self._anim.start(self)

    # -- projection -----------------------------------------------------
    def _project(self, lat, lon):
        w, h = self.width, self.height
        if not self.patient:
            return self.x + w / 2, self.y + h / 2
        clat, clon = self.patient[0], self.patient[1]
        span_lat = 0.10
        span_lon = span_lat / max(0.2, math.cos(math.radians(clat)))
        x = w / 2 + (lon - clon) / span_lon * w
        y = h / 2 + (lat - clat) / span_lat * h
        m = dp(26)
        x = min(max(x, m), w - m)
        y = min(max(y, m), h - m)
        return self.x + x, self.y + y

    # -- dessin -----------------------------------------------------------
    def _redraw(self, *args):
        self.canvas.clear()
        w, h = self.size
        if w <= 1 or h <= 1:
            return

        with self.canvas:
            Color(*SURFACE_LIGHT)
            Rectangle(pos=self.pos, size=self.size)
            # quadrillage "rues"
            Color(BORDER[0], BORDER[1], BORDER[2], 0.9)
            for i in range(1, 6):
                x = self.x + w * i / 6.0
                Line(points=[x, self.y, x, self.y + h], width=0.8)
            for i in range(1, 8):
                y = self.y + h * i / 8.0
                Line(points=[self.x, y, self.x + w, y], width=0.8)
            # deux axes principaux
            Color(BORDER[0] + 0.06, BORDER[1] + 0.06, BORDER[2] + 0.08, 1)
            Line(points=[self.x, self.y + h * 0.5, self.x + w,
                          self.y + h * 0.62], width=2.2)
            Line(points=[self.x + w * 0.42, self.y, self.x + w * 0.55,
                          self.y + h], width=2.2)

            if not self.patient:
                return

            px, py = self._project(self.patient[0], self.patient[1])

            # rayon d'urgence
            Color(DANGER[0], DANGER[1], DANGER[2], 0.35)
            Line(circle=(px, py, min(w, h) * 0.36), width=1.2)
            Color(DANGER[0], DANGER[1], DANGER[2], 0.06)
            Ellipse(pos=(px - min(w, h) * 0.36, py - min(w, h) * 0.36),
                    size=(min(w, h) * 0.72, min(w, h) * 0.72))

            # structures + liaisons
            for fac, dist in self.facilities:
                fx, fy = self._project(fac.latitude, fac.longitude)
                color = TYPE_COLORS.get(fac.type, CYAN)
                Color(color[0], color[1], color[2], 0.5)
                Line(points=[px, py, fx, fy], width=1.0)
                Color(*color)
                Ellipse(pos=(fx - dp(7), fy - dp(7)), size=(dp(14), dp(14)))
                Color(*BACKGROUND)
                Ellipse(pos=(fx - dp(3), fy - dp(3)), size=(dp(6), dp(6)))
                self._draw_text(fac.name, fx, fy + dp(10), color)
                self._draw_text(f"{dist:.1f} km", fx, fy - dp(16), color)

            # halo pulsant du patient
            Color(CYAN[0], CYAN[1], CYAN[2], 0.25 * (1 - self.pulse))
            r = dp(14) + dp(16) * self.pulse
            Ellipse(pos=(px - r, py - r), size=(2 * r, 2 * r))
            Color(*CYAN)
            Ellipse(pos=(px - dp(8), py - dp(8)), size=(dp(16), dp(16)))
            Color(*BACKGROUND)
            Ellipse(pos=(px - dp(3), py - dp(3)), size=(dp(6), dp(6)))
            self._draw_text("Patient localisé", px, py + dp(14), CYAN)

    def _draw_text(self, text, x, y, color=TEXT):
        """Texte dessiné directement dans le canvas de la carte."""
        core = CoreLabel(text=text, font_size=sp(9), color=color)
        core.refresh()
        tex = core.texture
        Color(*color)
        Rectangle(pos=(x - tex.width / 2.0, y), size=tex.size, texture=tex)

    def set_data(self, patient, facilities):
        self.patient = patient
        self.facilities = facilities
