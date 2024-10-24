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
        using an interpolation factor t from 0 to 1.
        """
        _t = min(max(0, t), 1)
        return a*(1-_t) + b*_t

    @staticmethod
    def cubic_bezier(v0, v1, v2, v3, t: float):
        """Perform cubic bezier interpolation.

        Interpolates between values v0 and v3,
        with Bezier control points v1 and v2,
        using a parametric interpolation
        factor t from 0 to 1.
        """
        _t = min(max(0, t), 1)
        return (v0 + (v1-v0)*(3*_t*(1-_t)**2)
                + (v2-v0)*(3*_t**2*(1-_t)) + (v3-v0)*_t**3)

    @staticmethod
    def non_parametric_cubic_bezier(x0: float,
                                    x1: float,
                                    x2: float,
                                    x3: float,
                                    y0,
                                    y1,
                                    y2,
                                    y3,
                                    x: float):
        """Perform non-parametric cubic bezier interpolation.

        Interpolates between values y0 and y3 at times x0 and x3,
        with Bezier control points y1 and y2 at times x1 and x2,
        using a non-parametric interpolation at time x.

        Requirements:
            x0 < x3
            x0 <= x1 <= x3
            x0 <= x2 <= x3
            x0 <= x <= x3
        """
        if x <= x0:
            return y0
        if x >= x3:
            return y3
        if x0 == x3:
            raise ValueError("TemporalCubicBezier error: x0 == x3")
        _X = (x-x0)/(x3-x0)
        _a = 1+3*(x1-x2)/(x3-x0)
        _b = (x2+x0-2*x1)/(x3-x0)
        _c = (x1-x0)/(x3-x0)
        _t = 0
        if _a == 0:
            if _b == 0:
                if _c == 0:
                    return y0
                else:
                    _t = _X/3/_c
            elif _c**2+4*_b*_X/3 >= 0:
                _t = (-_c + np.sqrt(_c**2+4*_b*_X/3))/2/_b
        else:
            _d = _b**2-_a*_c
            _f = 2*_b**3-3*_a*_b*_c-_a**2*_X
            if _d == 0:
                _t = -(_b+np.sign(_f)*abs(_f)**(1/3))/_a
            elif _f**2 >= 4*_d**3:
                _g = (_f+np.sqrt(_f**2-4*_d**3))/2
                _g = np.sign(_g)*abs(_g)**(1/3)
                _t = -(_b+_g+_d/_g)/_a
            else:
                _t = -(_b+2*np.sqrt(_d)*np.cos(
                    np.arccos(_f/2/_d**(3/2))/3))/_a
                if _t < 0 or _t > 1:
                    _t = -(_b+2*np.sqrt(_d)*np.cos(
                        2*np.pi / 3 + np.arccos(_f/2/_d**(3/2))/3))/_a
                if _t < 0 or _t > 1:
                    _t = -(_b+2*np.sqrt(_d)*np.cos(
                        4*np.pi / 3 + np.arccos(_f/2/_d**(3/2))/3))/_a
        return Interpolate.cubic_bezier(y0, y1, y2, y3, _t)
