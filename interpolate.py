import numpy as np

"""
The Interpolate class provides utilitary functions
to interpolate between values in various ways...
"""

class Interpolate:
	# linear interpolation
	# interpolates between a and b, for 0 < t < 1
	def linear(a, b, t):
		tt = min(max(0,t),1)
		return a*(1-tt) + b*tt
	
	# parametric cubic bezier interpolation
	# interpolates between v0 and v3
	# using control points v1 and v2, for 0 < t < 1
	def cubicBezier(v0,v1,v2,v3,t):
		tt = min(max(0,t),1)
		return v0 + 3*(v1-v0)*tt*(1-tt)**2 + 3*(v2-v0)*tt**2*(1-tt) + (v3-v0)*tt**3
	
	# non-parametric solution for 2D cubic Bezier interpolation
	# useful for temporal interpolation between keyframes
	# interpolates between (x0,y0) and (x3,y3)
	# using control points (x1,y1) and (x2,y2)
	# returns the interpolated y-value at position x
	# Requirements:
	# x0 < x3
	# x0 <= x1 <= x3
	# x0 <= x2 <= x3
	# x0 <= x <= x3
	def temporalCubicBezier(x0,x1,x2,x3,y0,y1,y2,y3,x):
		if x <= x0: return y0
		if x >= x3: return y3
		if x0 == x3:
			raise ValueError("TemporalCubicBezier error: x0 == x3")
		X = (x-x0)/(x3-x0)
		a = 1+3*(x1-x2)/(x3-x0)
		b = (x2+x0-2*x1)/(x3-x0)
		c = (x1-x0)/(x3-x0)
		t = 0
		if a == 0:
			if b == 0:
				if c == 0:
					return y0
				else:
					t = X/3/c
			elif c**2+4*b*X/3 >= 0:
				t = (-c + np.sqrt(c**2+4*b*X/3))/2/b
		else:
			d = b**2-a*c
			f = 2*b**3-3*a*b*c-a**2*X
			if d == 0:
				t = -(b+np.sign(f)*abs(f)**(1/3))/a
			elif f**2 >= 4*d**3:
				g = (f+np.sqrt(f**2-4*d**3))/2
				g = np.sign(g)*abs(g)**(1/3)
				t = -(b+g+d/g)/a
			else:
				t = -(b+2*np.sqrt(d)*np.cos(np.arccos(f/2/d**(3/2))/3))/a
				if t < 0 or t > 1:
					t = -(b+2*np.sqrt(d)*np.cos(2*np.pi/3 + np.arccos(f/2/d**(3/2))/3))/a
				if t < 0 or t > 1:
					t = -(b+2*np.sqrt(d)*np.cos(4*np.pi/3 + np.arccos(f/2/d**(3/2))/3))/a
		return Interpolate.cubicBezier(y0,y1,y2,y3,t)