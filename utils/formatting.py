"""Formatage des valeurs pour l'affichage (français)."""
import time as _time


def fmt_value(metric, value):
    if value is None:
        return "--"
    if metric == "heart_rate":
        return str(int(round(value)))
    if metric == "spo2":
        return str(int(round(value)))
    if metric == "glucose":
        return f"{value:.2f}"
    if metric == "temperature":
        return f"{value:.1f}"
    if metric == "sleep":
        return str(int(round(value)))
    if metric == "sweat":
        return f"{value:.1f}"
    if metric == "blood_pressure":
        try:
            sys_v, dia_v = value
            return f"{int(round(sys_v / 10.0))} / {int(round(dia_v / 10.0))}"
        except (TypeError, ValueError):
            return "--"
    return str(value)


def fmt_time(ts=None):
    return _time.strftime("%H:%M", _time.localtime(ts))


def fmt_datetime(ts=None):
    return _time.strftime("%d/%m/%Y %H:%M", _time.localtime(ts))


def fmt_duration(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def fmt_distance(km):
    return f"{km:.1f} km"
