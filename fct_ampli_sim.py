import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import math



#------ function -----#
def proj_ortho(X, Y, Z, z0, incid):
    """compute orthogonal projection of point [x,y,z] along plane defined by
    inciddir, ey and M[0,0,z0]
    incidence angle in rad
    """
    u = math.sin(incid)
    w = math.cos(incid)
    proj = [(X+((Z - z0) * (w/u))/(1 + (w/u)**2)), Y, (X + (z0 * u / w) + (Z*w/u))/((u/w)+(w/u))]
    return proj

# def proj_ortho(points, z0, incid):
#     """compute orthogonal projection of point [x,y,z] along plane defined by
#     inciddir, ey and M[0,0,z0]
#     incidence angle in rad
#     """
#     print(points)
#     test = points[1,:]
#     u = math.sin(incid)
#     w = math.cos(incid)
#     proj = [(points[:,1]+((points[:,3] - z0) * (w/u))/(1 + (w/u)**2)), points[:,2], (points[:,1] + (z0 * u / w) + (points[:,3]*w/u))/((u/w)+(w/u))]
#     return proj


#------ Main -----#


# Map footprint in meters
xmin, xmax = -3500, 3500
ymin, ymax = -3500, 3500
ech = 501     # x and y sampling number
subs = 5     # subsampling intervalle for plots
ech2 = 1000     # range sampling for amplitude computation


# Define grid
x,y = np.linspace(xmin,xmax, ech), np.linspace(ymin,ymax, ech)
X,Y = np.meshgrid(x,y)
Z = np.zeros(X.shape)        # initialise elevation at 0m everywhere


#------ Define 3D Volcano -----#

# Cone edifice
Rcald = 650
Rbase = 2500
Zbase = 2500
Zvolc = 3460
R_P2 = 420
ZP2 = 3190
ZBotcrat = 2780
Rcrat = 300
Beta = 0.3 # 0 conic, 1 cylinder
Alpha = 0.2 # 0 conic, 1 cylinder
decalX = -75
incid_deg = -40.0

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
proj = proj_ortho(X[ind], Y[ind], Z[ind], M[2], incid)         # !!! not same indice as in matlab
ind2 = np.where(abs(X) == min(abs(x)))
proj2 = proj_ortho(X[ind2], Y[ind2], Z[ind2], M[2], incid)         # !!! not same indice as in matlab

# projection of all points (X,Y,Z)
n, p = Z.shape
new_size = n * p
Xr = X.reshape(1, new_size)
Yr = Y.reshape(1, new_size)
Zr = Z.reshape(1, new_size)

pointsproj = proj_ortho(Xr, Yr, Zr, M[2], incid)

Xp = pointsproj[0]
Yp = pointsproj[1]
Zp = pointsproj[2]

Xproj = Xp.reshape(n, p)
Yproj = Yp.reshape(n, p)
Zproj = Zp.reshape(n, p)

#------ Compute distance for simulated amplitude -----#


# initialisation
Dist = np.zeros(Z.shape)
Distcum = np.zeros(Z.shape)
Distnorm = np.zeros(Z.shape)

for k in range(2, p):
    # compute distance topo between two consecutive points for all raws
    Dist[:,k] = np.sqrt(((Z[:, k] - Z[:,k-1])**2 + (X[:, k] - X[:,k-1])**2))
    # compute cumulative distance since the beginning of the profiles
    Distcum[:k] = Distcum[:, k-1] + Dist[:,k]

maxdistcum = np.max(Distcum,1) # compute distance max of each profile   # !!! not same indice as in matla


for k in range(1, n):
    # normalize Dist with distance max of each profile
    Distnorm[k,:] = Dist[k,:]/maxdistcum[k]

# compute vector between each projected point and fixed point M
print(type(pointsproj))
print(dir(pointsproj))
print(pointsproj.__sizeof__)
pointsproj_np = np.array(pointsproj)
pointsproj_f = pointsproj_np.reshape(3, new_size)
print("pointsproj_np.shape = ", pointsproj_np.shape)
print("pointsproj_f.shape = ", pointsproj_f.shape)
print(pointsproj_np)
print("")
print(pointsproj_f)

M1 = np.array(M)
print("M1.shape = ", M1.shape)
print(M1)
M1 = M1.reshape(1, 3)
print("M1.shape = ", M1.shape)
print(M1)
test = np.tile(M1, (new_size, 1))
# test1 = test.reshape(new_size, 1, 3)
print("test.shape = ",test.shape)
# print("test1.shape = ",test1.shape)

# print(test)
# print(test1)

Vec = [pointsproj_f - test]

# Vec = np.add(pointsproj_np, test1)


# compute scalar product of Vac with direction of incidence (distance along range)
# for k in range(1, new_size):
#     distproj[k,:] = np.dot(Vec[k,:], incidir)


# Distproj = distproj.reshape(n, p)
# mindistproj = np.min(np.min(Distproj))
# maxdistproj = np.max(np.max(Distproj))

# distotprojforinterp = np.linspace(mindistproj, maxdistproj, ech2) # interpole range regular sampling
# Matdist = np.zeros((n, p, ech2))

# for k in range(1, n):
#     distprojk = Distproj[k,:]
#     mindistprojk = np.min(distprojk)
#     maxdistprojk = np.max(distprojk)
#     distotproj = np.linspace(mindistproj, maxdistproj, ech2)
#     for l in range(2, p):
#         dist1 = distprojk[l-1]
#         dist2 = distprojk[l]
#         if (dist1 < dist2):
#             ind = np.where((distotproj > dist1) & (distotproj <= dist2))







# print(maxdistcum)






#------ Plot stuff -----#

# 3D Surface plot
plt.figure(figsize = (5,6))
# Z2 = Z.copy(); Z2[10,:] = 0 # <----- Replace this code
ax = plt.subplot(111, projection='3d')
ax.plot_surface(X,Y,Z, alpha=0.6)

ax.plot_surface(Xproj,Yproj,Zproj, color='red', alpha=0.6)

# 2D Plot of slice of 3D plot 
# plt.subplot(212)
# print(type(Z))
# plt.plot(X,Z[10,:])
plt.show()



