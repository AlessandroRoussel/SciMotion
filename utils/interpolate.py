"""
Utilitary functions for interpolation.

The Interpolate class provides utilitary functions
to interpolate between values in various ways.
"""

import numpy as np


class Interpolate:
    """Utilitary functions for interpolation.

    The handled data type can be anything, as long as
    it supports the additive binary operation +, and
    scalar multiplication * by a float number.
    """

    # TODO : problem with angles when interpolating
    # (tangents get changed with the modulo 2pi)
    # different possible directions for animation

    @staticmethod
    def linear(a, b, t: float):
        """Perform linear interpolation.

        Interpolates between values a and b,
        using interpolation factor 0 < t < 1.
        """
        _t = min(max(0, t), 1)
        return a*(1-_t) + b*_t

    @staticmethod
    def cubic_bezier(v0, v1, v2, v3, t: float):
        """Perform cubic bezier interpolation.

        Interpolates between values v0 and v3,
        with Bezier control values v1 and v2,
        using interpolation factor 0 < t < 1.
        """
        _t = min(max(0, t), 1)
        return (v0*(1-_t)**3 + v1*(3*_t*(1-_t)**2)
                + v2*(3*_t**2*(1-_t)) + v3*_t**3)

    @staticmethod
    def cubic_bezier_2d_handles(y0,
                                y1,
                                y2,
                                y3,
                                t1: float,
                                t2: float,
                                t: float):
        """Perform cubic bezier interpolation with 2D handles.

        Interpolates between values y0 and y3,
        with 2D Bezier control points (t1,y1) and (t2,y2),
        using interpolation factor 0 < t < 1.

        Requirements:
            0 <= t1 <= 1
            0 <= t2 <= 1
        """
        _t = min(max(0, t), 1)
        _t1 = min(max(0, t1), 1)
        _t2 = min(max(0, t2), 1)
        _a = 1 + 3*(_t1-_t2)
        _b = _t2 - 2*_t1

        _T = 0
        if _a == 0:
            if _b == 0:
                if _t1 == 0:
                    return y0
                else:
                    _T = _t/3/_t1
            elif _t1**2+4*_b*_t/3 >= 0:
                _T = (-_t1 + np.sqrt(_t1**2+4*_b*_t/3))/2/_b
        else:
            _d = _b**2-_a*_t1
            _f = 2*_b**3-3*_a*_b*_t1-_a**2*_t
            if _d == 0:
                _T = -(_b+np.sign(_f)*abs(_f)**(1/3))/_a
            elif _f**2 >= 4*_d**3:
                _g = (_f+np.sqrt(_f**2-4*_d**3))/2
                _g = np.sign(_g)*abs(_g)**(1/3)
                _T = -(_b+_g+_d/_g)/_a
            else:
                _T = -(_b+2*np.sqrt(_d)*np.cos(
                    np.arccos(_f/2/_d**(3/2))/3))/_a
                if _T < 0 or _T > 1:
                    _T = -(_b+2*np.sqrt(_d)*np.cos(
                        2*np.pi / 3 + np.arccos(_f/2/_d**(3/2))/3))/_a
                if _T < 0 or _T > 1:
                    _T = -(_b+2*np.sqrt(_d)*np.cos(
                        4*np.pi / 3 + np.arccos(_f/2/_d**(3/2))/3))/_a
        return Interpolate.cubic_bezier(y0, y1, y2, y3, _T)
