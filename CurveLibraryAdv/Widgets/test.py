""" Circuitous, LLC - 
    An Adventurous Circle Company

"""

import math

class Circle(object):
    """An advanced circle analytic toolkit"""

    __slots__ = ['diameter']     # flyweight design pattern suppresses the instance dictionary, saving lots of memory
    version = '0.5b'             # class variable

    def __init__(self, radius):
        self.radius = radius    # instance variable

    @property                   # convert dotted access to method calls
    def radius(self):
        """Radius of a circle"""
        return self.diameter / 2.0
    
    @radius.setter
    def radius(self, radius):
        self.diameter = radius * 2.0

    def area(self):
        """Perform quadrature on a shape of uniform radius"""
        p = self.__perimeter()
        r = p / math.pi / 2.0
        return math.pi * r ** 2.0

    def perimeter(self):
        return 2.0 * math.pi * self.radius

    @classmethod                # alternative constructor
    def from_bbd(cls, bbd):
        """Construct a circle from a bounding box diagonal"""
        radius = bbd/ 2.0 / math.sqrt(2.0)
        return Circle(radius)

    @staticmethod               # unrelated method, but some people need it in context
    def angle_to_grade(angle):
        """Convert angle in degree to a percentage grade"""
        return math.tan(math.radians(angle)) * 100.0

class Tire(Circle):
    """Tires are circles with a corrected perimeter"""

    def perimeter(self):
        """Circumference corrected for the rubber"""
        return Circle.perimeter(self) * 1.25
