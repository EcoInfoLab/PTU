import math
import pandas as pd

def readLatFromDSSAT(path, sep):
# read DSSAT
# read latitude and longitude
    wx = []
    file = open(path, "r")
    for line in file:
        count = 0
        # Split the line into a list of values using tab as the delimiter
        values = line.strip().split(sep)
        for value in values:
            if value[0] == '@':
                count += 1
            if value == 'INSI':
                count += 1
            if value == 'LAT':
                count += 1
            if count == 3:                
                break
        if count== 3:
            break
    for line in file:
        # Split the line into a list of values using tab as the delimiter
        values = line.strip().split(sep)
        lat = float(values[1])
        break
    file.close()
    return  lat

def readDSSAT(path, sep):
# read DSSAT
# read latitude and longitude
    wx = []
    file = open(path, "r")
    for line in file:
        count = 0
        # Split the line into a list of values using tab as the delimiter
        values = line.strip().split(sep)
        for value in values:
            if value[0] == '@':
                count += 1
            if value == 'INSI':
                count += 1
            if value == 'LAT':
                count += 1
            if count == 3:                
                break
        if count== 3:
            break
    for line in file:
        # Split the line into a list of values using tab as the delimiter
        values = line.strip().split(sep)
        lat = float(values[1])
        break
    for line  in file:    
        # Print each value in the line
        values = line.strip().split(sep)
        if values[0] == '@DATE':             
            break       
# read wx content
    for line in file:
        # Split the line into a list of values using tab as the delimiter
        values = line.strip().split(sep)
        if len(values) > 0:
            # python 3 syntax
            data = list(map(float, values))
            wx.append(data)        
    file.close()
    return (wx)

def calcDayLength(lat, doy):
    pi = 3.1415927
    degrad = pi / 180
# oryza sastro
    declin =  -math.asin(math.sin ( 23.45 * degrad ) * math.cos( 2. * pi * (doy + 10) / 365))
    sinld =  math.sin (degrad * lat) * math.sin (declin)
    cosld =  math.cos (degrad * lat) * math.cos (declin)
    aob = sinld/cosld
    if aob < -1:
        daylength = 0
        zzcos = 0
        zzsin = 1
    elif aob > 1:
        daylength = 24
        zzcos = 0
        zzsin = -1
    else:
        daylength = 12. * (1 + 2 * math.asin (aob) / pi)
        daylengthP = 12.* (1 + 2 * math.asin ((-math.sin(-4.*degrad) + sinld)/cosld)/pi)
        zza = pi * (12 + daylength) / 24
        zzcos = math.cos(zza)
        zzsin = math.sin(zza)
    return (daylength)

def calcPhotoThermalDevelopmentRate(tavg, gdd, photoperiod, baseT, criticalT, optimumP, criticalP, Rmax, alpha, beta, threshold, chi):
# Yin et al. 1995. A nonlinear model for crop development as a function of temperature 
    if tavg > baseT and tavg < criticalT:
        fT = (tavg - baseT)**alpha * (criticalT - tavg)**beta
    else:
        fT = 0
    if chi != 0:
         if gdd > threshold:
# Wang et al. 1998. Simulation of Phenological Development of Wheat Crops 
            omega = 4.0 / abs(optimumP - criticalP)
            fL = 1-math.exp(- chi * omega * (photoperiod  - criticalP))
            if fL < 0:
                fL = 0
            if fL  > 1:
                fL = 1
         else:
            fL = 0
    else:
        fL = 1
    DR = math.exp(Rmax) * fT * fL
    return (DR)

def mainPhotoThermal(wx, plantingDate, lat, baseT, criticalT, alpha,
beta, optimumP, criticalP, chi, RmaxVeg, RmaxRep, threshold):
    year_id = 0
    doy_id = 1
    tmax_id = 2
    tmin_id = 3
    sigmaDR = 0
    heading = 0
    ndays = len(wx)
    gdd = 0
    for d in range(0,ndays):
        tmax = wx[d][tmax_id]
        tmin = wx[d][tmin_id]   
        doy  = wx[d][doy_id] 
        if doy < plantingDate:
            continue
        if sigmaDR < 1:        
            chi = -1
            Rmax = RmaxVeg
        else:
            chi = 0
            Rmax = RmaxRep
        tavg = (tmax + tmin) / 2
        photoperiod = calcDayLength(lat, doy)
        gdd = gdd + max(tavg - baseT, 0)
        DR = calcPhotoThermalDevelopmentRate(tavg, gdd, photoperiod, baseT, criticalT, optimumP, criticalP, Rmax, alpha, beta, threshold, chi)
        sigmaDR = sigmaDR + DR 
        if sigmaDR > 1:
            heading = doy 
            break
    return (heading)

def run(path, batch, par):
# short day plant 
    chi = -1 
    baseT = par[0]
    criticalT = par[1]
    alpha = par[2]
    beta = par[3]
    optimumP = par[4]
    criticalP = par[5]
    threshold = par[6]
    RmaxVeg = par[7]
    RmaxRep = par[8]

    file = open(batch, "r")
    results = []
    file.readline()
    for line in file:
       record = line.strip().split()
       site = record[0]
       yearstr = record[1]
       plantingDate = int(record[2])
       wx = []
       index=[0, 0, 2, 3] 
       wxpath = path + site + yearstr[2:4]  + "01.WTH"
       lat = readLatFromDSSAT(wxpath,None)
       wxBody = readDSSAT(wxpath, None)
       for lines in wxBody:
           values = lines
           values[1] = int(values[0]) % 1000
           values[0] = int(values[0] / 1000) + 1900
           if values[0] < 1950:
               values[0] += 100
           wx.append(values)
       heading = mainPhotoThermal(wx, plantingDate, lat,  baseT, criticalT, alpha, beta, optimumP, criticalP, chi, RmaxVeg, RmaxRep, threshold)
       record.append(heading)
       results.append(record)
    file.close()
    return results


  
def empirical():
    path = "./"
    batchfile = path + "input.txt"
    paramfilename = path + "parameter.txt"
    paramfile = pd.read_table(paramfilename)
    baseT = paramfile.baseT[0]
    criticalT = paramfile.criticalT[0]
    alpha = paramfile.alpha[0]
    beta = paramfile.beta[0]
    optimumP = paramfile.optimumP[0]
    criticalP = paramfile.criticalP[0]
    threshold = paramfile.threshold[0]
    RmaxVeg = paramfile.RmaxVeg[0]
    RmaxRep = paramfile.RmaxRep[0]
    initpar = []
    initpar.append(baseT)
    initpar.append(criticalT)
    initpar.append(alpha)
    initpar.append(beta)
    initpar.append(optimumP)
    initpar.append(criticalP)
    initpar.append(threshold)
    initpar.append(RmaxVeg)
    initpar.append(RmaxRep)
    
    results = run(path, batchfile, initpar)
    output = open(path + "output.txt", "w")
    output.write("site\tyear\tplanting\theadingM\theadingS\n")
    for lines in results:
        text = ""
        for values in lines:
            text += str(values) + "\t"
        text += "\n"
        output.write(text)
    output.close()

empirical()
