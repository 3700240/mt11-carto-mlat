import numpy as np

# parameters for Lambert93 projection
[lon0, lat0, lat1, lat2] = [np.radians(x) for x in [3, 46.5, 44, 49]]
x0, y0 = 700000, 6600000
r = 6371000

# Lambert conformal conic projection (from spherical coordinates)
def sph2lcc(lon, lat):
    lon, lat = np.radians(lon), np.radians(lat)
    n = np.sin(lat1)
    if lat1 != lat2:
        n = np.log(np.cos(lat1) / np.cos(lat2))
        n /= np.log(np.tan(np.pi / 4 + lat2 / 2) / np.tan(np.pi / 4 + lat1 / 2))
    F = r * np.cos(lat1) * np.exp(n * np.log(np.tan(np.pi / 4 + lat1 / 2))) / n
    rho = F / np.exp(n * np.log(np.tan(np.pi / 4 + lat / 2)))
    rho0 = F / np.exp(n * np.log(np.tan(np.pi / 4 + lat0 / 2)))
    x = x0 + rho * np.sin(n * (lon - lon0))
    y = y0 + rho0 - rho * np.cos(n * (lon - lon0))
    return (x, y)