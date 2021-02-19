from .Element2D import *
from .RectangularScheme import *
class Serendipity(Element2D,RectangularScheme):
	def __init__(this,coords,gdl,n=3):
		_coords = np.array([coords[i] for i in range(4)])
		Element2D.__init__(this,np.array(coords),_coords,gdl)
		RectangularScheme.__init__(this,n)
	def psis(this,z):
		return np.array([
			0.25*(1.0-z[0])*(1.0-z[1])*(-1.0-z[0]-z[1]),
			0.25*(1.0+z[0])*(1.0-z[1])*(-1.0+z[0]-z[1]),
			0.25*(1.0+z[0])*(1.0+z[1])*(-1.0+z[0]+z[1]),
			0.25*(1.0-z[0])*(1.0+z[1])*(-1.0-z[0]+z[1]),
			0.5*(1.0-z[0]**2.0)*(1.0-z[1]),
			0.5*(1.0+z[0])*(1.0-z[1]**2.0),
			0.5*(1.0-z[0]**2.0)*(1.0+z[1]),
			0.5*(1.0-z[0])*(1.0-z[1]**2.0)
			])
	def dpsis(this,z):
		return np.array([
			[-0.25*(z[1]-1.0)*(2.0*z[0]+z[1]),
			-0.25*(z[1]-1.0)*(2.0*z[0]-z[1]),
			0.25*(z[1]+1.0)*(2.0*z[0]+z[1]),
			0.25*(z[1]+1.0)*(2.0*z[0]-z[1]),
			(z[1]-1.0)*z[0],
			-0.5*(z[1]**2.0-1.0),
			-(z[1]+1.0)*z[0],
			0.5*(z[1]**2.0-1.0)],
			[-0.25*(z[0]-1.0)*(2.0*z[1]+z[0]),
			0.25*(z[0]+1.0)*(2.0*z[1]-z[0]),
			0.25*(z[0]+1.0)*(2.0*z[1]+z[0]),
			-0.25*(z[0]-1.0)*(2.0*z[1]-z[0]),
			0.5*(z[0]**2.0-1.0),
			-z[1]*(z[0]+1.0),
			-0.5*(z[0]**2.0-1.0),
			z[1]*(z[0]-1.0)]])