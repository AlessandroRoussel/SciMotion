"""Utilitary functions for color management."""

from enum import Enum
from typing import Union
import numpy as np


class ColorSpace(Enum):
    """Defines a list of color spaces."""

    LINEAR = 0
    SRGB = 1
    HSL = 2
    HSV = 3
    XYZ = 4
    OKLAB = 5
    OKLCH = 6


class ColorManagement:
    """Utilitary functions for color management."""

    linear_to_xyz_matrix = np.array([[.4124, .3576, .1805],
                                     [.2126, .7152, .0722],
                                     [.0193, .1192, .9505]])

    xyz_to_linear_matrix = np.array([[3.2406255, -1.537208, -.4986286],
                                     [-.9689307, 1.8757561, .0415175],
                                     [.0557101, -.2040211, 1.0569959]])
    
    @classmethod
    def convert(cls,
                values: Union[list[float], np.ndarray],
                src_space: ColorSpace,
                dest_space: ColorSpace) -> np.ndarray:
        """Convert a color between different color spaces."""
        _values = np.array(values, dtype=np.float32)
        if _values.shape not in [(3,),(4,)]:
            raise ValueError("Input values should be a 3D or 4D vector.")
        if len(_values) == 3:
            _values = np.append(_values, 1)
        if src_space == dest_space:
            return _values
        
        if src_space == ColorSpace.SRGB:
            if dest_space == ColorSpace.LINEAR:
                return cls.srgb_to_linear(_values)
            if dest_space == ColorSpace.XYZ:
                return cls.linear_to_xyz(cls.srgb_to_linear(_values))
        
        if src_space == ColorSpace.LINEAR:
            if dest_space == ColorSpace.SRGB:
                return cls.linear_to_srgb(_values)
            if dest_space == ColorSpace.XYZ:
                return cls.linear_to_xyz(_values)
        
        if src_space == ColorSpace.XYZ:
            if dest_space == ColorSpace.LINEAR:
                return cls.xyz_to_linear(_values)
            if dest_space == ColorSpace.SRGB:
                return cls.linear_to_srgb(cls.xyz_to_linear(_values))
        
        # HSL management:
        if src_space == ColorSpace.HSL:
            if dest_space == ColorSpace.SRGB:
                return cls.hsl_to_srgb(_values)
            else:
                return cls.convert(cls.hsl_to_srgb(_values),
                               ColorSpace.SRGB, dest_space)
        if dest_space == ColorSpace.HSL:
            if src_space == ColorSpace.SRGB:
                return cls.srgb_to_hsl(_values)
            else:
                return cls.srgb_to_hsl(cls.convert(
                    _values, src_space, ColorSpace.SRGB))
        
        # HSV management:
        if src_space == ColorSpace.HSV:
            if dest_space == ColorSpace.SRGB:
                return cls.hsv_to_srgb(_values)
            else:
                return cls.convert(cls.hsv_to_srgb(_values),
                               ColorSpace.SRGB, dest_space)
        if dest_space == ColorSpace.HSV:
            if src_space == ColorSpace.SRGB:
                return cls.srgb_to_hsv(_values)
            else:
                return cls.srgb_to_hsv(cls.convert(
                    _values, src_space, ColorSpace.SRGB))
        
        raise NotImplementedError(f"Conversion between {src_space} and "
                                  f"{dest_space} is not implemented.")

    @staticmethod
    def srgb_to_linear(in_color: np.ndarray) -> np.ndarray:
        """Convert sRGB to linear."""
        _out_color = in_color[:3]
        _filter = _out_color > .04045
        _out_color[_filter] = ((_out_color[_filter]+.055)/1.055)**2.4
        _out_color[~_filter] = _out_color[~_filter]/12.92
        return np.append(_out_color, in_color[3])

    @classmethod
    def linear_to_xyz(cls, in_color: np.ndarray) -> np.ndarray:
        """Convert linear to XYZ."""
        _out_color = cls.linear_to_xyz_matrix @ in_color[:3].reshape((3, 1))
        return np.append(_out_color, in_color[3])

    @staticmethod
    def linear_to_srgb(in_color: np.ndarray) -> np.ndarray:
        """Convert linear to sRGB."""
        _out_color = in_color[:3]
        _filter = _out_color > .0031308
        _out_color[_filter] = 1.055*_out_color[_filter]**(1/2.4)-.055
        _out_color[~_filter] = _out_color[~_filter]*12.92
        return np.clip(np.append(_out_color, in_color[3]), 0, 1)

    @classmethod
    def xyz_to_linear(cls, in_color: np.ndarray) -> np.ndarray:
        """Convert XYZ to linear."""
        _out_color = cls.xyz_to_linear @ in_color[:3].reshape((3, 1))
        return np.append(_out_color, in_color[3])
    
    @classmethod
    def srgb_to_hsl(cls, in_color: np.ndarray) -> np.ndarray:
        """Convert sRGB to HSL."""
        _min = np.min(in_color[:3])
        _max = np.max(in_color[:3])
        _luminance = .5*(_min+_max)
        _delta = _max-_min
        _saturation = 0 if _delta==0 else _delta/(1-abs(2*_luminance-1))
        if _delta == 0:
            _hue = 0
        elif _max == in_color[0]:
            _hue = (((in_color[1]-in_color[2])/_delta)%6)/6
        elif _max == in_color[1]:
            _hue = ((in_color[2]-in_color[0])/_delta+2)/6
        elif _max == in_color[2]:
            _hue = ((in_color[0]-in_color[1])/_delta+4)/6
        _out = [_hue%1, _saturation, _luminance]
        return np.clip(np.append(_out, in_color[3]), 0, 1)
    
    @classmethod
    def hsl_to_srgb(cls, in_color: np.ndarray) -> np.ndarray:
        """Convert HSL to sRGB."""
        _delta = in_color[1]*(1-abs(2*in_color[2]-1))
        _x = _delta*(1-abs(((6*in_color[0])%2)-1))
        _min = in_color[2]-_delta*.5
        _sextant = int(np.floor(in_color[0]*6))
        if _sextant == 0:
            _out_color = np.array([_delta, _x, 0]) + _min
        elif _sextant == 1:
            _out_color = np.array([_x, _delta, 0]) + _min
        elif _sextant == 2:
            _out_color = np.array([0, _delta, _x]) + _min
        elif _sextant == 3:
            _out_color = np.array([0, _x, _delta]) + _min
        elif _sextant == 4:
            _out_color = np.array([_x, 0, _delta]) + _min
        else:
            _out_color = np.array([_delta, 0, _x]) + _min
        return np.clip(np.append(_out_color, in_color[3]), 0, 1)

    @classmethod
    def srgb_to_hsv(cls, in_color: np.ndarray) -> np.ndarray:
        """Convert sRGB to HSV."""
        _min = np.min(in_color[:3])
        _value = np.max(in_color[:3])
        _delta = _value-_min
        _saturation = 0 if _value==0 else _delta/_value
        if _delta == 0:
            _hue = 0
        elif _value == in_color[0]:
            _hue = (((in_color[1]-in_color[2])/_delta)%6)/6
        elif _value == in_color[1]:
            _hue = ((in_color[2]-in_color[0])/_delta+2)/6
        elif _value == in_color[2]:
            _hue = ((in_color[0]-in_color[1])/_delta+4)/6
        _out = [_hue%1, _saturation, _value]
        return np.clip(np.append(_out, in_color[3]), 0, 1)
    
    @classmethod
    def hsv_to_srgb(cls, in_color: np.ndarray) -> np.ndarray:
        """Convert HSV to sRGB."""
        _delta = in_color[1]*in_color[2]
        _x = _delta*(1-abs(((6*in_color[0])%2)-1))
        _min = in_color[2]-_delta
        _sextant = int(np.floor(in_color[0]*6))
        if _sextant == 0:
            _out_color = np.array([_delta, _x, 0]) + _min
        elif _sextant == 1:
            _out_color = np.array([_x, _delta, 0]) + _min
        elif _sextant == 2:
            _out_color = np.array([0, _delta, _x]) + _min
        elif _sextant == 3:
            _out_color = np.array([0, _x, _delta]) + _min
        elif _sextant == 4:
            _out_color = np.array([_x, 0, _delta]) + _min
        else:
            _out_color = np.array([_delta, 0, _x]) + _min
        return np.clip(np.append(_out_color, in_color[3]), 0, 1)
