import pya
from math import sqrt, cos, sin, atan2, pi, copysign
from pya import Point, DPoint, DSimplePolygon, SimplePolygon, DPolygon, Polygon, Region, DPath, DVector, DBox
from pya import Trans, DTrans, CplxTrans, DCplxTrans, ICplxTrans

from classLib._PROG_SETTINGS import *
from classLib.baseClasses import ElementBase, ComplexBase
from classLib.coplanars import CPW


class Rectangle(ElementBase):
    def __init__(self, origin, a, b, trans_in=None, inverse=False):
        self.a = a
        self.b = b
        super().__init__(origin, trans_in, inverse)

    def init_regions(self):
        origin = DPoint(0, 0)
        p1 = origin + DPoint(self.a, 0)
        p2 = p1 + DPoint(0, self.b)
        p3 = p2 + DPoint(-self.a, 0)
        pts_arr = [origin, p1, p2, p3]
        if self.inverse:
            self.empty_region.insert(SimplePolygon().from_dpoly(DSimplePolygon(pts_arr)))
        else:
            self.metal_region.insert(SimplePolygon().from_dpoly(DSimplePolygon(pts_arr)))


class Cross(ElementBase):
    def __init__(self, origin, inner_square_a, outer_square_a, trans_in=None):
        self.in_a = inner_square_a
        self.out_a = outer_square_a
        self.center = origin + DPoint(self.out_a / 2, self.out_a / 2)
        super(Cross, self).__init__(origin, trans_in)
        self.center = self.connections[0]

    def init_regions(self):
        origin = DPoint(0, 0)
        w = self.out_a / 2 - self.in_a / 2

        rec1 = Rectangle(origin, w, w)
        p2 = origin + DPoint(self.in_a + w, 0)
        rec2 = Rectangle(p2, w, w)
        p3 = origin + DPoint(self.in_a + w, self.in_a + w)
        rec3 = Rectangle(p3, w, w)
        p4 = origin + DPoint(0, self.in_a + w)
        rec4 = Rectangle(p4, w, w)

        tmp_reg = Region()

        rec1.place(tmp_reg)
        rec2.place(tmp_reg)
        rec3.place(tmp_reg)
        rec4.place(tmp_reg)

        rec = Rectangle(origin, self.out_a, self.out_a)
        rec.place(self.metal_region)

        self.empty_region = tmp_reg
        self.connections = [self.center]


class XmonCross(ComplexBase):
    def __init__(self, origin,
                 sideX_length, sideX_width, sideX_gnd_gap, sideX_face_gnd_gap=None,
                 sideY_length=None, sideY_width=None, sideY_gnd_gap=None, sideY_face_gnd_gap=None,
                 trans_in=None):
        """
        Draws cross for xmon qubit with a lot of customization parameters.

        Parameters
        ----------
        origin : DPoint
            center of the cross
        sideX_length : float
            length of the cross extensions along x-axis
        sideX_width : float
            width of the cross extensions along x-axis
        sideX_gnd_gap : float
            ground gap between longs sides of extensions along x-axis and ground (gap along y-axis)
        sideX_face_gnd_gap : float
            ground gap between face end of extensions along x-axis and ground (gap along x-axis)
            default - `sideX_gnd_gap`
        sideY_length : float
            length of the cross extensions along y-axis
            default - `sideX_length`
        sideY_width : float
            width of the cross extensions along y-axis
            default - `sideX_width`
        sideY_gnd_gap : float
            ground gap between face end of extensions along y-axis and ground (gap along x-axis)
            default - `sideX_gnd_gap`
        sideY_face_gnd_gap : float
            ground gap between face end of extensions along y-axis and ground (gap along y-axis)
            default - `sideX_face_gnd_gap`
        trans_in : DCplxTrans
            transformation of the cross

        Notes
        -----------
        if `sideX_face_gnd_gap` and `sideY_face_gnd_gap` both are ommited, then the latter
        will be equal `sideX_face_gnd_gap` default value that is `sideX_gnd_gap`
        """
        self.sideX_length = sideX_length
        self.sideY_length = None
        if sideY_length is None:
            self.sideY_length = self.sideX_length
        else:
            self.sideY_length = sideY_length

        self.sideX_width = sideX_width
        self.sideY_width = None
        if sideY_width is None:
            self.sideY_width = self.sideX_width
        else:
            self.sideY_width = sideY_width

        self.sideX_gnd_gap = sideX_gnd_gap
        self.sideY_gnd_gap = None
        if sideY_gnd_gap is None:
            self.sideY_gnd_gap = self.sideX_gnd_gap
        else:
            self.sideY_gnd_gap = sideY_gnd_gap

        if sideX_face_gnd_gap is None:
            self.sideX_face_gnd_gap = self.sideX_gnd_gap
        else:
            self.sideX_face_gnd_gap = sideX_face_gnd_gap

        if sideY_face_gnd_gap is None:
            self.sideY_face_gnd_gap = self.sideX_face_gnd_gap
        else:
            self.sideY_face_gnd_gap = self.sideY_face_gnd_gap

        # for saving
        self.center = origin
        super().__init__(origin, trans_in)
        self._geometry_parameters["sideX_length, um"] = self.sideX_length / 1e3
        self._geometry_parameters["sideY_length, um"] = self.sideY_length / 1e3
        self._geometry_parameters["sideX_width, um"] = self.sideX_width / 1e3
        self._geometry_parameters["sideY_width, um"] = self.sideY_width / 1e3
        self._geometry_parameters["sideX_gnd_gap, um"] = self.sideX_gnd_gap / 1e3
        self._geometry_parameters["sideY_gnd_gap, um"] = self.sideY_gnd_gap / 1e3
        self._geometry_parameters["sideX_face_gnd_gap, um"] = self.sideX_face_gnd_gap / 1e3
        self._geometry_parameters["sideY_face_gnd_gap, um"] = self.sideY_face_gnd_gap / 1e3
        self.center = self.connections[0]

    def init_primitives(self):
        origin = DPoint(0, 0)

        # draw central square
        from classLib.shapes import Rectangle
        lb_corner = DPoint(-self.sideX_width / 2, -self.sideY_width / 2)
        center_square = Rectangle(lb_corner, self.sideX_width, self.sideY_width)
        self.primitives["center_square"] = center_square

        """ left part of Xmon cross """
        p1 = origin + DPoint(-self.sideY_width / 2, 0)
        p2 = p1 + DPoint(-self.sideX_length, 0)
        self.cpw_l = CPW(self.sideX_width, self.sideX_gnd_gap, p1, p2)
        self.primitives["cpw_l"] = self.cpw_l
        p3 = p2 + DPoint(-self.sideX_face_gnd_gap, 0)
        self.cpw_lempt = CPW(0, self.cpw_l.b / 2, p2, p3)
        self.primitives["cpw_lempt"] = self.cpw_lempt

        """ right part of Xmon cross """
        p1 = origin + DPoint(self.sideY_width / 2, 0)
        p2 = p1 + DPoint(self.sideX_length, 0)
        self.cpw_r = CPW(self.sideX_width, self.sideX_gnd_gap, p1, p2)
        self.primitives["cpw_r"] = self.cpw_r
        p3 = p2 + DPoint(self.sideX_face_gnd_gap, 0)
        self.cpw_rempt = CPW(0, self.cpw_r.b / 2, p2, p3)
        self.primitives["cpw_rempt"] = self.cpw_rempt

        """ top part of Xmon cross """
        p1 = origin + DPoint(0, self.sideX_width / 2)
        p2 = p1 + DPoint(0, self.sideY_length)
        self.cpw_t = CPW(self.sideY_width, self.sideY_gnd_gap, p1, p2)
        self.primitives["cpw_t"] = self.cpw_t
        p3 = p2 + DPoint(0, self.sideY_face_gnd_gap)
        self.cpw_tempt = CPW(0, self.cpw_t.b / 2, p2, p3)
        self.primitives["cpw_tempt"] = self.cpw_tempt

        """ bottom part of Xmon cross """
        p1 = origin + DPoint(0, -self.sideX_width / 2)
        p2 = p1 + DPoint(0, -self.sideY_length)
        self.cpw_b = CPW(self.sideY_width, self.sideY_gnd_gap, p1, p2)
        self.primitives["cpw_b"] = self.cpw_b
        p3 = p2 + DPoint(0, -self.sideY_face_gnd_gap)
        self.cpw_bempt = CPW(0, self.cpw_b.b / 2, p2, p3)
        self.primitives["cpw_bempt"] = self.cpw_bempt

        self.connections = [origin]


class Circle(ElementBase):
    def __init__(self, center, r, trans_in=None, n_pts=50, solid=True, offset_angle=0):
        self.center = center
        self._offset_angle = offset_angle
        self.r = r
        self.n_pts = n_pts
        self.solid = solid
        super().__init__(center, trans_in)

    def init_regions(self):
        dpts_arr = [DPoint(self.r * cos(2 * pi * i / self.n_pts + self._offset_angle),
                           self.r * sin(2 * pi * i / self.n_pts + self._offset_angle)) for i in range(0, self.n_pts)]
        if (self.solid == True):
            self.metal_region.insert(SimplePolygon().from_dpoly(DSimplePolygon(dpts_arr)))
        else:
            self.empty_region.insert(SimplePolygon().from_dpoly(DSimplePolygon(dpts_arr)))
        self.connections.extend([self.center, self.center + DVector(0, -self.r)])
        self.angle_connections.extend([0, 0])


class Kolbaska(ElementBase):
    def __init__(self, origin, stop, width, r, trans_in=None):
        self._width = width
        self._vec = stop - origin
        self._r = r
        super().__init__(origin, trans_in)

    def init_regions(self):
        ext_start = self._r
        ext_end = self._r
        shps = [self._width, ext_start, ext_end]
        kolb = DPath([DPoint(0, 0), DPoint(0, 0) + self._vec], *shps, True)
        self.metal_region.insert(kolb)
        self.connections.extend([DPoint(0, 0), DPoint(0, 0) + self._vec])
        self.angle_connections.extend([0, 0])


class Circle_arc(ElementBase):
    def __init__(self, center, r, alpha_start=0, alpha_end=pi, trans_in=None, n_pts=50, solid=True):
        self.center = center
        self.r = r
        self.alpha_start = alpha_start
        self.alpha_end = alpha_end
        self.n_pts = n_pts
        self.solid = solid
        super(Circle_arc, self).__init__(center, trans_in)

    def init_regions(self):
        d_alpha = (self.alpha_end - self.alpha_start) / (self.n_pts - 1)
        alphas = [(self.alpha_start + d_alpha * i) for i in range(0, self.n_pts)]
        dpts_arr = [DPoint(self.r * cos(alpha), self.r * sin(alpha)) for alpha in alphas]
        dpts_arr.append(DPoint(0, 0))

        if (self.solid == True):
            self.metal_region.insert(SimplePolygon().from_dpoly(DSimplePolygon(dpts_arr)))
        else:
            self.empty_region.insert(SimplePolygon().from_dpoly(DSimplePolygon(dpts_arr)))
        self.connections.extend([self._center, self._center + DVector(0, -self.r)])
        self.angle_connections.extend([0, 0])


class Ring(ElementBase):
    """@brief: class represents a ring (radius - thicknes < R < radius)
        @params:  DPoint origin - the center of the ring
                        float radius - outer radius of the ring
                        float thickness - thickness of the ring
                        int n_pts - number of points comprising the circumference of the ring (50 by default)
                        Trans trans_in - initial transformation (None by default)
                        bool inverse - if True then the ring is subtracted from a layer (False by default)
    """

    def __init__(self, origin, radius, thickness, n_pts=50, trans_in=None, inverse=False):
        self.r = radius
        self.t = thickness
        self.n_pts = n_pts
        super().__init__(origin, trans_in, inverse)

    def init_regions(self):
        origin = DPoint(0, 0)
        Rin = self.r - self.t
        Rout = self.r
        dpts_arr_Rout = [DPoint(Rout * cos(2 * pi * i / self.n_pts), Rout * sin(2 * pi * i / self.n_pts)) for i in
                         range(0, self.n_pts)]
        dpts_arr_Rin = [DPoint(Rin * cos(2 * pi * i / self.n_pts), Rin * sin(2 * pi * i / self.n_pts)) for i in
                        range(0, self.n_pts)]
        outer_circle = Region(SimplePolygon().from_dpoly(DSimplePolygon(dpts_arr_Rout)))
        inner_circle = Region(SimplePolygon().from_dpoly(DSimplePolygon(dpts_arr_Rin)))
        ring = outer_circle - inner_circle
        # self.metal_region.insert(ring)
        if self.inverse:
            self.empty_region = ring
        else:
            self.metal_region = ring


class IsoTrapezoid(ElementBase):
    """@brief: class represents an isosceles trapezoid
        @params:  DPoint origin - position of the left bottom node
                        float height - height of the trapezoid
                        float bottom - length of the bottom side
                        float top - length of the top side
                        Trans trans_in - initial transformation (None by default)
                        bool inverse - if True then the ring is subtracted from a layer (False by default)
    """

    def __init__(self, origin, height, bottom, top, trans_in=None, inverse=False):
        self.h = height
        self.b = bottom
        self.t = top
        super().__init__(origin, trans_in, inverse)

    def init_regions(self):
        origin = DPoint(0, 0)
        dx = (self.b - self.t) / 2
        p1 = origin + DPoint(dx, self.h)
        p2 = p1 + DPoint(self.t, 0)
        p3 = p2 + DPoint(dx, -self.h)
        pts_arr = [origin, p1, p2, p3]
        if self.inverse:
            self.empty_region.insert(SimplePolygon().from_dpoly(DSimplePolygon(pts_arr)))
        else:
            self.metal_region.insert(SimplePolygon().from_dpoly(DSimplePolygon(pts_arr)))


class Cross2(ElementBase):
    """@brief: class represents a cross
        @params:  DPoint origin - center of the cross
                        float thickness - thickness of the line
                        float length - size of the cross
                        Trans trans_in - initial transformation (None by default)
                        bool inverse - if True then the ring is subtracted from a layer (False by default)
    """

    def __init__(self, origin, thickness, length, trans_in=None, inverse=False):
        self.l = length
        self.t = thickness
        super().__init__(origin, trans_in, inverse)

    def init_regions(self):
        origin = DPoint(0, 0)
        hor_box = DBox(origin - DPoint(self.l / 2, self.t / 2), DPoint(self.l / 2, self.t / 2))
        vert_box = DBox(origin - DPoint(self.t / 2, self.l / 2), DPoint(self.t / 2, self.l / 2))
        cross = (Region(hor_box) + Region(vert_box)).merge()
        if self.inverse:
            self.empty_region.insert(cross)
        else:
            self.metal_region.insert(cross)