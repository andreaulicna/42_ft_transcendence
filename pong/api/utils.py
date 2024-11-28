import math


# fix for 0 denominator
# https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
def get_line_intersection(p0_x, p0_y, p1_x, p1_y, p2_x, p2_y, p3_x, p3_y):
	s1_x = p1_x - p0_x
	s1_y = p1_y - p0_y
	s2_x = p3_x - p2_x
	s2_y = p3_y - p2_y

	s = (-s1_y * (p0_x - p2_x) + s1_x * (p0_y - p2_y)) / (-s2_x * s1_y + s1_x * s2_y)
	t = (s2_x * (p0_y - p2_y) - s2_y * (p0_x - p2_x)) / (-s2_x * s1_y + s1_x * s2_y)


	if -0.001 <= s <= 1.001 and -0.001 <= t <= 1.001:
		# Collision detected
		i_x = p0_x + (t * s1_x)
		i_y = p0_y + (t * s1_y)
		return Vector2D(i_x, i_y)

	return None 

def ccw(A,B,C):
	return (C.y-A.y) * (B.x-A.x) > (B.y-A.y) * (C.x-A.x)

# Return true if line segments AB and CD intersect
def intersect(A,B,C,D):
	return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

class Vector2D:
	"""A two-dimensional vector with Cartesian coordinates."""

	def __init__(self, x, y):
		self.x, self.y = x, y

	def __str__(self):
		"""Human-readable string representation of the vector."""
		return '[{:g},{:g}]'.format(self.x, self.y)

	def __repr__(self):
		"""Unambiguous string representation of the vector."""
		return repr((self.x, self.y))

	def dot(self, other):
		"""The scalar (dot) product of self and other. Both must be vectors."""

		if not isinstance(other, Vector2D):
			raise TypeError('Can only take dot product of two Vector2D objects')
		return self.x * other.x + self.y * other.y
	# Alias the __matmul__ method to dot so we can use a @ b as well as a.dot(b).
	__matmul__ = dot

	def __sub__(self, other):
		"""Vector subtraction."""
		return Vector2D(self.x - other.x, self.y - other.y)

	def __add__(self, other):
		"""Vector addition."""
		return Vector2D(self.x + other.x, self.y + other.y)

	def __mul__(self, scalar):
		"""Multiplication of a vector by a scalar."""

		if isinstance(scalar, int) or isinstance(scalar, float):
			return Vector2D(self.x*scalar, self.y*scalar)
		raise NotImplementedError('Can only multiply Vector2D by a scalar')

	def __rmul__(self, scalar):
		"""Reflected multiplication so vector * scalar also works."""
		return self.__mul__(scalar)

	def __neg__(self):
		"""Negation of the vector (invert through origin.)"""
		return Vector2D(-self.x, -self.y)

	def __truediv__(self, scalar):
		"""True division of the vector by a scalar."""
		return Vector2D(self.x / scalar, self.y / scalar)

	def __mod__(self, scalar):
		"""One way to implement modulus operation: for each component."""
		return Vector2D(self.x % scalar, self.y % scalar)

	def __abs__(self):
		"""Absolute value (magnitude) of the vector."""
		return math.sqrt(self.x**2 + self.y**2)

	def distance_to(self, other):
		"""The distance between vectors self and other."""
		return abs(self - other)

	def to_polar(self):
		"""Return the vector's components in polar coordinates."""
		return self.__abs__(), math.atan2(self.y, self.x)
	
	def cross_product(self, other):
		"""Return z-component of the resulting cross-product vector"""
		return self.x * other.y - self.y * other.x
	



# class Vector2D:
# 	"""A two-dimensional vector with Cartesian coordinates."""

# 	def __init__(self, x, y):
# 		self.x, self.y = x, y

# 	def __str__(self):
# 		"""Human-readable string representation of the vector."""
# 		return '[{:g},{:g}]'.format(self.x, self.y)

# 	def __repr__(self):
# 		"""Unambiguous string representation of the vector."""
# 		return repr((self.x, self.y))

# 	def dot(self, other):
# 		"""The scalar (dot) product of self and other. Both must be vectors."""
# 		if not isinstance(other, Vector2D):
# 			raise TypeError('Can only take dot product of two Vector2D objects')
# 		return self.x * other.x + self.y * other.y

# 	def __sub__(self, other):
# 		"""Subtract two vectors."""
# 		return Vector2D(self.x - other.x, self.y - other.y)

# 	def __add__(self, other):
# 		"""Add two vectors."""
# 		return Vector2D(self.x + other.x, self.y + other.y)

# 	def cross(self, other):
# 		"""The 2D cross product of self and other."""
# 		return self.x * other.y - self.y * other.x

# 	def length(self):
# 		"""The length of the vector."""
# 		return math.sqrt(self.x**2 + self.y**2)

# class LineSegment:
# 	def __init__(self, start: Vector2D, end: Vector2D):
# 		self.start = start
# 		self.end = end

# 		self.length = self.distance(start, end)

# 		if self.length == 0 or math.isnan(self.length) or not math.isfinite(self.length):
# 			raise ValueError('Invalid length')

# 		self.direction = end - start

# 	@staticmethod
# 	def distance(p1: Vector2D, p2: Vector2D) -> float:
# 		return (p2 - p1).length()

# epsilon = 1 / 1000000

# def equals0(x: float) -> bool:
# 	return abs(x) < epsilon

# def intersection(ls0: LineSegment, ls1: LineSegment):
# 	p = ls0.start
# 	r = ls0.direction
# 	q = ls1.start
# 	s = ls1.direction

# 	r_s = r.cross(s)
# 	q_p_r = (q - p).cross(r)

# 	if equals0(r_s) and equals0(q_p_r):
# 		t1 = (q + s - p).dot(r) / r.dot(r)
# 		t0 = t1 - s.dot(r) / r.dot(r)

# 		if 0 <= t0 <= 1 or 0 <= t1 <= 1:
# 			return {'type': 'colinear-overlapping', 'ls0t0': t0, 'ls0t1': t1}

# 		return {'type': 'colinear-disjoint'}

# 	if equals0(r_s) and not equals0(q_p_r):
# 		return {'type': 'parallel-non-intersecting'}

# 	t = (q - p).cross(s) / r_s
# 	u = (q - p).cross(r) / r_s

# 	if not equals0(r_s) and 0 <= t <= 1 and 0 <= u <= 1:
# 		return {'type': 'intersection', 'ls0t': t, 'ls1u': u}

# 	return {'type': 'no-intersection'}