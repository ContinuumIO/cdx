
import inspect

from .properties import (BaseProperty, HasProps, Instance, Enum, Float, Int,
        Color, Percent, Size, Bool, Pattern, Align, Angle, String)

from .objects import PlotObject, Viewable

# Size is a way to preserve a data-space-related metric all the way until
#   render time, when the screen dimensions are known
# Align may be "center", "min", "max", or "jitter(func)" where func is name
#   of a random distribution to draw random samples from. Defaults to uniform
#   but gaussian could certainly be useful.

#class Scene(object):
#    """ A set of related plots, each with their own panel(s) and each
#    panel representing some coherent coordinate space onto which Glyphs
#    are positioned and rendered.
#    """

class DataSpec(BaseProperty):
    """ Because the BokehJS glyphs support a fixed value or a named
    field for most data fields, we capture that in this property.

    We mirror the JS convention in this Python descriptor.  There are
    multiple ways to set a DataSpec, illustrated below with comments
    and example code.

    class Foo(HasProps):
        x = DataSpec("x", units="data")

    f = Foo()
    f.x = "fieldname"   # Sets x to a field named "fieldname"
    f.x = 12            # Sets x to a default value of 12
    f.x = {"name": "foo", "default": 12}

    Just reading out "f.x" will always retrieve what has been set.
    """
    # TODO: Check to see if the "units" field hasn't been removed...

    def __init__(self, field=None, units="data", default=None):
        """
        Parameters
        ==========
        **field** is the string name of a data column to look up.
        **units** is either "data" or "screen"
        **default** is the default value to use if a datapoint is
        missing the field specified in **name**

        If a constant value is desired, then leave **field** as None and
        set **default** to the fixed value.
        """
        # Don't use .name because the HasProps metaclass uses that to
        # store the attribute name on this descriptor.
        self.field = field
        self.units = units
        self.default = default

    @classmethod
    def autocreate(cls, name=None):
        # In this case, use the name the user assigned this DataSpec to
        # as the default field name.
        d = cls(field=name)
        return d

    def __get__(self, obj, cls=None):
        # It's kind of an open question what we should return here if the
        # user hasn't set anything yet.  We use our best heuristic and
        # return a name, a default, or a dict with both, depending on
        # what is None.
        if hasattr(obj, "_"+self.name):
            return getattr(obj, "_"+self.name)
        else:
            if self.field is None:
                return self.default
            elif self.default is None:
                return self.field
            else:
                return {"field": self.field, "default": self.default}

    def __set__(self, obj, value):
        setattr(obj, "_"+self.name, value)

    def __delete__(self, obj):
        if hasattr(obj, self.name + "_dict"):
            delattr(obj, self.name + "_dict")
        BaseProperty.__delete__(self, obj)

    def to_dict(self, obj):
        # Build the complete dict
        value = getattr(obj, "_"+self.name, self.default)
        if type(value) == str:
            d = {"name": value, "units": self.units, "default": self.default}
        elif isinstance(value, dict):
            d = {"name": self.field, "units": self.units, "default": self.default}
            d.update(value)
        else:
            # Assume value is a numeric type and is the default value.
            # We explicitly set the field name to None.
            d = {"name": None, "units": self.units, "default": value}
        return d


class FillProps(HasProps):
    """ Mirrors the BokehJS properties.fill_properties class """
    fill = Color("gray")
    fill_alpha = Percent(1.0)

class LineProps(HasProps):
    """ Mirrors the BokehJS properties.line_properties class """
    line_color = Color("red")
    line_width = Size(1)
    line_alpha = Percent(1.0)
    line_join = String("miter")
    line_cap = String("butt")
    line_dash = Pattern
    line_dash_offset = Int(0)

class TextProps(HasProps):
    """ Mirrors the BokehJS properties.text_properties class """
    text_font = String
    text_font_size = Int(10)
    text_font_style = Enum("normal", "italic", "bold")
    text_color = Color("black")
    text_alpha = Percent(1.0)
    text_align = Enum("left", "right", "center")
    text_baseline = Enum("top", "middle", "bottom")


class MetaGlyph(Viewable):
    """ Handles DataSpecs and other special attribute processing that Glyph
    subclasses need.

    I contemplated making this a class decorator, or monkeypatching the
    Viewable metaclass, but that all seemed more brittle than just
    making a sub-metaclass.
    """

    def __new__(cls, class_name, bases, class_dict):
        # This is a little unorthodox. Usually metaclasses munge the class_dict
        # and attributes before handing off to the base metaclass ctor. In our
        # case, we want the MetaHasProps.__new__ to handle all the machinery
        # of autocreating Property declarations and whatnot, and so we just
        # muck with the class after it's been created.  I've not seen it done
        # this way elsewhere, but it shouldn't be a problem.

        newcls = super(MetaGlyph,cls).__new__(cls, class_name, bases, class_dict)
        dataspecs = {}
        for attr,val in newcls.__dict__.iteritems():
            if isinstance(val, DataSpec):
                dataspecs[attr] = val
        setattr(newcls, "_dataspecs", dataspecs)
        return newcls


class Glyph(PlotObject):
    """ Base class for all glyphs/marks/geoms/whatever-you-call-'em in Bokeh.
    """

    __metaclass__ = MetaGlyph

    # The name that will be used for the 'type' field of the glyph when we
    # create the JS dict representation of this glyph.  "glyph" is not a valid
    # glyph type; it's just a placeholder.
    glyphtype = "glyph"

    # Common attributes for all glyphs
    #color = Color
    #alpha = Percent
    visible = Bool
    margin = Size   # the amount of desired space around this glyph
    halign = Align  # when there is horizontal wiggle room (e.g. categorical)
    valign = Align  # when there is vertical wiggle room

    radius_units = Enum("screen", "data")
    length_units = Enum("screen", "data")
    angle_units = Enum("deg", "rad")
    start_angle_units = Enum("deg", "rad")
    end_angle_units = Enum("deg", "rad")

    def to_glyphspec(self):
        """ Returns a dict mapping attributes to values, that is amenable for
        inclusion in a GlyphRenderer definition.
        """
        d = self.vm_props(withvalues=True)
        d["type"] = d.pop("glyphtype")
        # Iterate over all the DataSpec properties and convert them, using the
        # fact that DataSpecs store the dict-ified version on the object.
        for attrname, dspec in self.dataspecs().iteritems():
            d[attrname] = dspec.to_dict(self)
        return d

    def dataspecs(self):
        dataspecs = {}
        for cls in reversed(inspect.getmro(self.__class__)):
            if isinstance(cls, MetaGlyph):
                dataspecs.update(cls._dataspecs)
        return dataspecs

class Marker(Glyph, FillProps, LineProps):
    """ Base class for glyphs which are just simple markers placed at (x,y)
    locations.
    """

    x = DataSpec
    y = DataSpec
    #size = Size

    # TODO: Remove this and use the color attributes in Glyph instead
    #stroke_color = Color
    #fill_pattern = Pattern
    #shape = Enum("circle", "dot", "square", "tri", "diamond", "x", "+", "char")
    #char_value = String

class Circle(Marker):
    glyphtype = String("circle")
    radius = DataSpec(units="screen", default=4)

#class Rects(Glyph):
#    glyphtype = "rects"
#    x = DataSpec
#    y = DataSpec
#    width = DataSpec
#    height = DataSpec
#    angle = DataSpec
#    color = Color
#    outline_color = Color
#    outline_width = Size

# Other kinds of Markers, to match what GGplot provides
class Triangle(Marker):
    glyphtype = String("triangle")

class Cross(Marker):
    glyphtype = String("cross")

class Xmarker(Marker):
    glyphtype = String("xmarker")

class Diamond(Marker):
    glyphtype = String("diamond")

class InvertedTriangle(Marker):
    glyphtype = String("invertedtriangle")

class SquareX(Marker):
    glyphtype = String("squarex")

class Asterisk(Marker):
    glyphtype = String("asterisk")

class DiamondCross(Marker):
    glyphtype = String("diamondcross")

class CircleCross(Marker):
    glyphtype = String("circlecross")

class HexStar(Marker):
    glyphtype = String("hexstar")

class SquareCross(Marker):
    glyphtype = String("squarecross")

class CircleX(Marker):
    glyphtype = String("circlex")


class AnnularWedge(Glyph, FillProps, LineProps):
    glyphtype = String('annular_wedge')
    x = DataSpec
    y = DataSpec
    inner_radius = DataSpec
    outer_radius = DataSpec
    start_angle = DataSpec
    end_angle = DataSpec
    direction = Enum('clock', 'anticlock')

class Annulus(Glyph, FillProps, LineProps):
    glyphtype = String('annulus')
    x = DataSpec
    y = DataSpec
    inner_radius = DataSpec
    outer_radius = DataSpec

class Arc(Glyph, LineProps):
    glyphtype = String('arc')
    x = DataSpec
    y = DataSpec
    radius = DataSpec
    start_angle = DataSpec
    end_angle = DataSpec
    direction = Enum('clock', 'anticlock')

# TODO
# class Area

class Bezier(Glyph, LineProps):
    glyphtype = String('bezier')
    x0 = DataSpec
    y0 = DataSpec
    x1 = DataSpec
    y1 = DataSpec
    cx0 = DataSpec
    cy0 = DataSpec
    cx1 = DataSpec
    cy1 = DataSpec

# TODO
# class image

class ImageURI(Glyph):
    glyphtype = String('image_uri')
    x = DataSpec
    y = DataSpec
    angle = DataSpec

# TODO
# image_rgba

class Line(Glyph, LineProps):
    glyphtype = String("line")
    xs = DataSpec
    ys = DataSpec

class Oval(Glyph, FillProps, LineProps):
    glyphtype = String('oval')
    x = DataSpec
    y = DataSpec
    width = DataSpec
    height = DataSpec
    angle = DataSpec

class Quad(Glyph, FillProps, LineProps):
    glyphtype = String("quad")
    left = DataSpec
    right = DataSpec
    bottom = DataSpec
    top = DataSpec

class QuadCurve(Glyph, FillProps, LineProps):
    glyphtype = String('quad_curve')
    x0 = DataSpec
    y0 = DataSpec
    x1 = DataSpec
    y1 = DataSpec
    cx = DataSpec
    cy = DataSpec

class Ray(Glyph, LineProps):
    glyphtype = String("ray")
    x = DataSpec
    y = DataSpec
    angle = DataSpec
    length = DataSpec

class Rect(Glyph, FillProps, LineProps):
    glyphtype = String("rect")
    x = DataSpec
    y = DataSpec
    width = DataSpec
    height = DataSpec
    angle = DataSpec

class Segment(Glyph, LineProps):
    glyphtype = String('segment')
    x0 = DataSpec
    y0 = DataSpec
    x1 = DataSpec
    y1 = DataSpec

class Text(Glyph):
    glyphtype = String("text")
    x = DataSpec
    y = DataSpec
    angle = DataSpec
    text = String

class Wedge(Glyph, FillProps, LineProps):
    glyphtype = String('wedge')
    x = DataSpec
    y = DataSpec
    radius = DataSpec
    start_angle = DataSpec
    end_angle = DataSpec
    direction = Enum('clock', 'anticlock')


