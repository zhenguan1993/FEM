from .Geometry import Geometry
from typing import Callable
import numpy as np

class Geometry2D(Geometry):
    """Creates a 2D geometry"""
    def __init__(self, dictionary: list, gdls: list, types: list, nvn: int = 1, segments: list = [], fast=False):
        Geometry.__init__(self, dictionary, gdls, types, nvn, segments, fast)


    def generateSegmentsFromCoords(self, p0: list, p1: list) -> None:
        """Generates a geometry segment by specified coordinates

        Args:
            p0 (list): Segment start point
            p1 (list): Segment end point
        """
        masCercano1 = None
        d1 = np.Inf
        masCercano2 = None
        d2 = np.Inf
        for i, gdl in enumerate(self.gdls):
            r1 = np.sqrt((p0[0]-gdl[0])**2+(p0[1]-gdl[1])**2)
            r2 = np.sqrt((p1[0]-gdl[0])**2+(p1[1]-gdl[1])**2)
            if r1 < d1:
                d1 = r1
                masCercano1 = i
            if r2 < d2:
                d2 = r2
                masCercano2 = i
        self.segments.append([masCercano1, masCercano2])

    def generateBCFromCoords(self, x: float, y: float, value: float = 0, nv: int = 1) -> list:
        """Generates border conditions by coordinates. The border condition is applied to the nearest node

        Args:
            x (float): X coordinate of point
            y (float): Y coordinate of point
            value (float, optional): Value of the border condition. Defaults to 0.
            nv (int, optional): Variable number. The first variable is 1. Defaults to 1.

        Returns:
            list: Matrix of border coordinates that can be concatenated
        """

        masCercano1 = None
        d1 = np.Inf
        for i, gdl in enumerate(self.gdls):
            r1 = np.sqrt((x-gdl[0])**2+(y-gdl[1])**2)
            if r1 < d1:
                d1 = r1
                masCercano1 = i
        return [[masCercano1*self.nvn+(nv-1), value]]

    def loadOnSegmentVF(self, segment: int, f: Callable = None, tol: float = 1*10**(-5), add=None) -> None:
        """Assign a load over a geometry segment.

        The start point of segment is the 0 point of load
        The end point of segment is the end point of load

        Load must be defined as a function (normal or lambda)

        Args:
            segment (int): Segment in wich load will be applied
            f (Callable, optional): Load Function. Defaults to None.
            tol (float, optional): Tolerancy for finding nodes. Defaults to 1*10**(-5).
        """
        c0, cf = [self.gdls[self.segments[segment][0]],
                  self.gdls[self.segments[segment][1]]]
        dy = cf[1]-c0[1]
        dx = cf[0]-c0[0]
        theta = np.arctan2(dy, dx)
        def fx(s): return f(c0[0]+s*np.cos(theta))[0]
        def fy(s): return f(c0[1]+s*np.sin(theta))[1]
        self.loadOnSegment(segment=segment, fx=fx, fy=fy, tol=tol, add=add)

    def loadOnSegment(self, segment: int, fx: Callable = None, fy: Callable = None, tol: float = 1*10**(-5), add=None) -> None:
        """Assign a load over a geometry segment.

        The start point of segment is the 0 point of load
        The end point of segment is the end point of load

        Load must be defined as a function (normal or lambda)

        Args:
            segment (int): Segment in wich load will be applied
            fx (Callable, optional): Load Function x component. Defaults to None.
            fy (Callable, optional): Load Function y component. Defaults to None.
            tol (float, optional): Tolerancy for finding nodes. Defaults to 1*10**(-5).
        """
        a = self.giveElementsOfSegment(segment, tol)
        coordenadas = np.array(self.gdls)[self.segments[segment]]
        vect_seg = coordenadas[1]-coordenadas[0]
        for e in a:
            e.intBorders = True
            for i in range(-1, len(e.borders)-1):
                pertenece1 = isBetween(
                    coordenadas[0], coordenadas[1], e._coords[i], tol)
                pertenece2 = isBetween(
                    coordenadas[0], coordenadas[1], e._coords[i+1], tol)
                if pertenece1 and pertenece2:
                    vect_lad = e._coords[i+1]-e._coords[i]
                    sign = np.sign(vect_seg@vect_lad)
                    e.borders[i].dir = sign
                    e.borders[i].s0 = np.linalg.norm(
                        e._coords[i]-coordenadas[0])
                    if fx:
                        e.borders[i].properties['load_x'].append(fx)
                    if fy:
                        e.borders[i].properties['load_y'].append(fy)
                    if add:
                        e.borders[i].properties.update(add)
                else:
                    e.borders[i].dir = 0.0

    def loadOnHole(self, hole: int, sa: float = 0, ea: float = 2*np.pi, fx: Callable = None, fy: Callable = None, tol: float = 1*10**(-5)) -> None:
        """Assign loads over a hole.

        Args:
            hole (int): Hole index in wich load will be applied
            sa (float, optional): Start face angle. Defaults to 0.
            ea (float, optional): Finish face angle. Defaults to :math:`2\\pi`.
            fx (Callable, optional): Load Function x component. Defaults to None.
            fy (Callable, optional): Load Function y component. Defaults to None.
            tol (float, optional): Tolerancy for finding nodes. Defaults to 1*10**(-5).
        """
        holee = self.holes[hole]
        segments_apply = []
        for i, segmento in enumerate(holee['segments']):
            seg_coords = np.array(self.gdls)[segmento]
            centradas = seg_coords[1]-seg_coords[0]
            angle = np.arctan2(centradas[1], centradas[0])
            angle += np.pi/2
            if angle < 0:
                angle += 2*np.pi
            if angleBetweenAngles(sa, ea, angle):
                segments_apply.append(segmento)
        for segmento in segments_apply:
            for i, seg in enumerate(self.segments):
                if seg == segmento:
                    self.loadOnSegment(i, fx, fy, tol)
                    break

    def cbOnHole(self, hole: int, value: float, nv: int = 1, sa: float = 0, ea: float = 2*np.pi, tol: float = 1*10**(-5)) -> list:
        """Generate a list of border conditions from specified hole.

        Args:
            hole (int): Hole index in wich load will be applied
            value (float): Value of the bc
            nv (int, optional): Variable number, starts with 1. Defaults to 1.
            sa (float, optional): Start face angle. Defaults to 0.
            ea (float, optional): Finish face angle. Defaults to :math:`2\\pi`.
            tol (float, optional): Tolerancy for finding nodes. Defaults to 1*10**(-5).

        Returns:
            list: List of border conditions that can be concatenated or assigned to the geometry
        """
        holee = self.holes[hole]
        segments_apply = []
        bc = []
        for i, segmento in enumerate(holee['segments']):
            seg_coords = np.array(self.gdls)[segmento]
            centradas = seg_coords[1]-seg_coords[0]
            angle = np.arctan2(centradas[1], centradas[0])
            angle += np.pi/2
            if angle < 0:
                angle += 2*np.pi
            if angleBetweenAngles(sa, ea, angle):
                segments_apply.append(segmento)
        for segmento in segments_apply:
            for i, seg in enumerate(self.segments):
                if seg == segmento:
                    bc += self.cbFromSegment(i, value, nv, tol)
                    break
        return bc


    def show(self, texto: int = 10, bolita: int = 0, draw_segs: bool = True, draw_labels: bool = False, draw_bc: bool = False, label_bc: bool = False) -> None:
        """Create a geometry graph

        Args:
            texto (int, optional): Text size. Defaults to 10.
            bolita (int, optional): Node size. Defaults to 0.
            draw_segs (bool, optional): To draw or not draw the segments. Defaults to True.
            draw_labels (bool, optional): To draw or not draw element labels. Defaults to False.
            draw_bc (bool, optional): To draw border conditions. Defaults to False.
            label_bc (bool, optional): To draw labels on border conditions. Defaults to False.
        """

        fig = plt.figure()
        ax = fig.add_subplot()

        ax.axes.set_aspect('equal')

        for i, e in enumerate(self.elements):
            coords = e._coords
            coords = np.array(coords.tolist() + [coords[0].tolist()])
            X = coords[:, 0]
            Y = coords[:, 1]
            ax.plot(X, Y, '-', color='black', alpha=1-0.6*draw_bc, zorder=-10)
            cx = self.centroids[i][0]
            cy = self.centroids[i][1]
            if draw_labels:
                ax.plot(cx, cy, 'o', markersize=texto + bolita, color='yellow')
                ax.annotate(format(i), [
                            cx, cy], size=texto, textcoords="offset points", xytext=(-0, -2.5), ha='center')
        try:
            if draw_segs:
                verts = self.gdls
                segs = self.segments
                for i, seg in enumerate(segs):
                    x0, y0 = verts[int(seg[0])]
                    x1, y1 = verts[int(seg[1])]

                    ax.fill(
                        [x0, x1],
                        [y0, y1],
                        facecolor='none',
                        edgecolor='b',
                        linewidth=3,
                        zorder=0,
                        alpha=1-0.6*draw_bc
                    )
                    cx = (x0+x1)*0.5
                    cy = (y0+y1)*0.5
                    ax.plot(cx, cy, 'o', markersize=texto +
                            bolita, color='pink', alpha=1-0.6*draw_bc)
                    ax.annotate(format(i), [
                                cx, cy], alpha=1-0.6*draw_bc, size=texto, textcoords="offset points", xytext=(-0, -2.5), ha='center')
        except:
            pass
        for j, e in enumerate(self.elements):
            if e.intBorders:
                for i in range(-1, len(e.borders)-1):
                    border = e.borders[i]
                    if (len(border.properties['load_x']) + len(border.properties['load_y'])):
                        coords_border_0 = e._coords[i]
                        coords_border_1 = e._coords[i+1]
                        ax.plot([coords_border_0[0], coords_border_1[0]], [coords_border_0[1], coords_border_1[1]],
                                color='yellow',
                                linewidth=5,
                                zorder=50,
                                )
                        cx = (coords_border_0 + coords_border_1)/2
                        ax.annotate(format(len(border.properties['load_x']) + len(border.properties['load_y'])), cx, size=texto,
                                    textcoords="offset points", xytext=(-0, -2.5), ha='center', zorder=55)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('Domain')

        gdls = np.array(self.gdls)

        labels = np.linspace(0, gdls.shape[0] - 1, gdls.shape[0]).astype(int)
        if draw_labels:
            ax.plot(gdls[:, 0], gdls[:, 1], 'o',
                    markersize=texto+bolita, color='gray')
        if draw_labels:
            for p, l in zip(gdls, labels):
                ax.annotate(l, p, size=texto, textcoords="offset points",
                            xytext=(-0, -2.5), ha='center')
        maxx = np.max(gdls[:, 0])
        maxy = np.max(gdls[:, 1])

        minx = np.min(gdls[:, 0])
        miny = np.min(gdls[:, 1])
        coordmax = min(maxx-minx, maxy-miny)
        tFlecha = coordmax/80
        if draw_bc:
            for i, cb in enumerate(self.cbe):
                coords_cb = gdls[int(cb[0]//self.nvn)]
                if cb[0] % self.nvn == 0:
                    color = 'red'
                    ax.annotate(f"{i}: {cb[1]}"*label_bc, xy=coords_cb, xytext=(
                        coords_cb[0]-tFlecha, coords_cb[1]), horizontalalignment='center', verticalalignment='center', arrowprops=dict(arrowstyle="->", facecolor=color))
                elif cb[0] % self.nvn == 1:
                    color = 'blue'
                    ax.annotate(f"{i}: {cb[1]}"*label_bc, xy=coords_cb, xytext=(
                        coords_cb[0], coords_cb[1]+tFlecha), horizontalalignment='center', verticalalignment='center', arrowprops=dict(arrowstyle="->", facecolor=color))
                elif cb[0] % self.nvn == 2:
                    color = 'yellow'
                    ax.annotate(f"{i}: {cb[1]}"*label_bc, xy=coords_cb, xytext=(
                        coords_cb[0]-tFlecha, coords_cb[1]-tFlecha), horizontalalignment='center', verticalalignment='center', arrowprops=dict(arrowstyle="->", facecolor=color))
                else:
                    color = 'black'
                    ax.annotate(f"{i}: {cb[1]}"*label_bc, xy=coords_cb, xytext=(
                        coords_cb[0]-tFlecha, coords_cb[1]), horizontalalignment='center', verticalalignment='center', arrowprops=dict(arrowstyle="->", facecolor=color))
            for i, cb in enumerate(self.cbn):
                coords_cb = gdls[int(cb[0]//self.nvn)]
                if cb[0] % self.nvn == 0:
                    color = 'red'
                    ax.annotate(f"NBC {i}: {cb[1]}"*label_bc, xy=coords_cb, xytext=(
                        coords_cb[0]-tFlecha, coords_cb[1]), horizontalalignment='center', verticalalignment='center', arrowprops=dict(arrowstyle="->", facecolor=color))
                elif cb[0] % self.nvn == 1:
                    color = 'blue'
                    ax.annotate(f"NBC {i}: {cb[1]}"*label_bc, xy=coords_cb, xytext=(
                        coords_cb[0], coords_cb[1]+tFlecha), horizontalalignment='center', verticalalignment='center', arrowprops=dict(arrowstyle="->", facecolor=color))
                elif cb[0] % self.nvn == 2:
                    color = 'yellow'
                    ax.annotate(f"NBC {i}: {cb[1]}"*label_bc, xy=coords_cb, xytext=(
                        coords_cb[0]-tFlecha, coords_cb[1]-tFlecha), horizontalalignment='center', verticalalignment='center', arrowprops=dict(arrowstyle="->", facecolor=color))
                else:
                    color = 'black'
                    ax.annotate(f"NBC {i}: {cb[1]}"*label_bc, xy=coords_cb, xytext=(
                        coords_cb[0]-tFlecha, coords_cb[1]), horizontalalignment='center', verticalalignment='center', arrowprops=dict(arrowstyle="->", facecolor=color))
        figManager = plt.get_current_fig_manager()
        figManager.full_screen_toggle()
