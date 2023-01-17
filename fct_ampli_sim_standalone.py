import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import math, re



#------ function -----#
def proj_ortho(points, z0, incid):
    """compute orthogonal projection of point [x,y,z] along plane defined by
    inciddir, ey and M[0,0,z0]
    incidence angle in rad
    """
    X = points[0,:]
    Y = points[1,:]
    Z = points[2,:]
    u = math.sin(incid)
    w = math.cos(incid)
    proj = np.array([(X+((Z - z0) * (w/u)))/(1 + (w/u)**2), Y, (X + (z0 * u / w) + (Z*w/u))/((u/w)+(w/u))])
    return proj


#------ Main -----#


# Map footprint in meters
xmin, xmax = -3500, 3500
ymin, ymax = -3500, 3500
ech = 501     # x and y sampling number
subs = 5     # subsampling intervalle for plots
ech2 = 1000     # range sampling for amplitude computation


# Define grid
x,y = np.linspace(xmin,xmax, ech), np.linspace(ymin,ymax, ech)
Y,X = np.meshgrid(x,y)
Z = np.zeros(X.shape)        # initialise elevation at 0m everywhere


#------ Define 3D Volcano -----#

# Cone edifice
Rcald = 675
Rbase = 2500
Zbase = 2500
Zvolc = 3460
R_P2 = 420
ZP2 = 3190
ZBotcrat = 2880
Rcrat = 300
Beta = 0 # 0 conic, 1 cylinder
Alpha = 0.2 # 0 conic, 1 cylinder
decalX = -100
# 
incid_deg = 39.36
azim = 14.05
slra = 2.33
MODE = "Descending Right"


theta_edifice = math.atan((Rcald - Rbase)/(Zbase - Zvolc))
ind =  np.where((X**2 + Y**2) <= Rbase**2)
Z[ind] = (Rbase / math.tan(theta_edifice)) - np.sqrt((X[ind]**2 + Y[ind]**2)/(math.tan(theta_edifice))**2)

# inverted cone caldera
theta_cald = math.atan((R_P2 - Rcald)/(Zvolc - ZP2))
ind =  np.where((X**2 + Y**2) <= Rcald**2)
Z[ind] = Zvolc - Zbase + (Rcald/math.tan(theta_cald)) + np.sqrt((X[ind]**2 + Y[ind]**2)/(math.tan(theta_cald))**2)
Z = Z + Zbase

# platform P2
ind =  np.where((X**2 + Y**2) <= R_P2**2)
Z[ind] = ZP2

# crater cylinder
ind =  np.where((X**2 + Y**2) <= Rcrat**2)
Z[ind] = Z[ind] - (Beta * (ZP2 - ZBotcrat))

# crater inverted cone
theta_crat = math.atan((Rcrat * (Alpha - 1))/((ZP2 - ZBotcrat)*(1 - Beta)))
Z[ind] = Z[ind] + (Rcrat/math.tan(theta_crat)) + np.sqrt(((X[ind] - decalX)**2) + Y[ind]**2)/((math.tan(theta_crat)**2))

# crater flat bottom
ind =  np.where(((X - decalX)**2 + Y**2) <= (Alpha * Rcrat)**2)
Z[ind] = ZBotcrat


#------ Projection -----#

incid = math.radians(incid_deg)
incidir = [math.sin(incid), 0, math.cos(incid)]
M = [0,0,Zvolc]

# projection line of interest
ind = np.where(abs(X - decalX) == min(abs(x - decalX)))
proj = proj_ortho(np.array([X[ind], Y[ind], Z[ind]]), M[2], incid)         # !!! not same indice as in matlab
ind2 = np.where(abs(X) == min(abs(x)))
proj2 = proj_ortho(np.array([X[ind2], Y[ind2], Z[ind2]]), M[2], incid)         # !!! not same indice as in matlab

# projection of all points (X,Y,Z)
n, p = Z.shape

fullsize = n * p
Xr = X.reshape(fullsize, 1)
Yr = Y.reshape(fullsize, 1)
Zr = Z.reshape(fullsize, 1)

points2proj = np.array([Xr, Yr, Zr])
pointsproj = proj_ortho(points2proj, M[2], incid)

Xp = pointsproj[0]
Yp = pointsproj[1]
Zp = pointsproj[2]

Xproj = Xp.reshape(n, p)
Yproj = Yp.reshape(n, p)
Zproj = Zp.reshape(n, p)

# print(Xproj)
# print(Yproj)
# print(Zproj)
# print(Z.shape)
#------ Compute distance for simulated amplitude -----#


# initialisation
Dist = np.zeros(Z.shape)
Distcum = np.zeros(Z.shape)
Distnorm = np.zeros(Z.shape)

for k in range(1, p):
    # compute distance topo between two consecutive points for all raws
    Dist[:,k] = np.sqrt(((Z[k,:] - Z[k-1, :])**2 + (X[k,:] - X[k-1, :])**2))
    # compute cumulative distance since the beginning of the profiles
    Distcum[:,k] = Distcum[:, k-1] + Dist[:,k]

maxdistcum = np.max(Distcum,1) # compute distance max of each profile   # !!! not same indice as in matla


for k in range(0, n):
    # normalize Dist with distance max of each profile
    Distnorm[k,:] = np.divide(Dist[k,:], maxdistcum[k])



# # compute vector between each projected point and fixed point M

pointsproj_f = pointsproj.transpose()
pointsproj_f = pointsproj_f.reshape(fullsize, 3)
M_np = np.array(M)
M_np = M_np.reshape(1, 3)
rep_M = np.tile(M_np, (fullsize, 1))
Vec = np.subtract(pointsproj_f, rep_M)


# # compute scalar product of Vec with direction of incidence (distance along range)
distproj = np.zeros((fullsize, 1))
for k in range(0, fullsize):
    distproj[k,:] = np.dot(Vec[k,:], incidir)

Distproj = distproj.reshape(n, p)
Distproj = Distproj.transpose()

mindistproj = np.min(np.min(Distproj))
maxdistproj = np.max(np.max(Distproj))


distotprojforinterp = np.linspace(mindistproj, maxdistproj, ech2) # interpole range regular sampling
Matdist = np.zeros((n, p, ech2))

for k in range(0, n):
    distprojk = Distproj[k,:]
    mindistprojk = np.min(distprojk)
    maxdistprojk = np.max(distprojk)
    distotproj = np.linspace(mindistproj, maxdistproj, ech2)
    for l in range(1, p):
        dist1 = distprojk[l-1]
        dist2 = distprojk[l]
        if (dist1 < dist2):
            ind = np.where((distotproj > dist1) & (distotproj <= dist2))
        else:
            ind = np.where((distotproj <= dist1) & (distotproj > dist2))

        Matdist[k,l,ind] = Distnorm[k,l]/abs(dist1 - dist2) * abs(maxdistprojk - mindistprojk)



# # Compute simulated amplitude
MATDIST = np.zeros((n, ech2))
MATDIST[:,:] = np.sum(Matdist, 1)


print(MATDIST.shape)

if (re.search("Ascending Right", MODE) or (re.search("Descending Left", MODE))):
 sign=- 1
else:
    sign = 1



# print(maxdistcum)



print(MATDIST.shape)
print(distotprojforinterp.shape)

#------ Plot stuff -----#

# 3D Surface plot
plt.figure(figsize = (5,6))
# ax = plt.subplot(121, projection='3d')
# ax.plot_surface(X,Y,Z, alpha=0.6)
# ax.plot_surface(Xproj,Yproj,Zproj, color='red', alpha=0.6)

range_ra = sign*distotprojforinterp/slra
range_az = y/azim

print(range_ra.shape)
print(range_az.shape)

ax1 = plt.subplot(111)
# ax1.imshow(MATDIST, cmap='Greys_r')
mean_val = np.mean(MATDIST)
vmin = mean_val - (80/100 * mean_val)
vmax = mean_val + (150/100 * mean_val)
ax1.imshow(MATDIST, cmap='Greys_r', vmin=vmin, vmax=vmax, extent=[range_ra[0] ,range_ra[-1], range_az[0] ,range_az[-1]], aspect='auto')
# ax1.imshow(MATDIST, extent=[0,1000,0,501], aspect='auto')
plt.show()



