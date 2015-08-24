import pmag, pmagplotlib
import pylab
import numpy as np
import matplotlib.pyplot as plt
import random
import os
import sys
from mpl_toolkits.basemap import Basemap

def iflip(D): #function simplified from PmagPy pmag.flip function
    """
    This function returns the antipode (flips) of the unit vectors in D (dec,inc,length).
    """
    Dflip=[]
    for rec in D:
        d,i=(rec[0]-180.)%360.,-rec[1]
        Dflip.append([d,i,1.])
    return Dflip
        
def iBootstrap(Data1,Data2,NumSims=1000):
    """
    Conduct a bootstrap test (Tauxe, 2010) for a common mean on two declination,
    inclination data sets
    
    This function modifies code from PmagPy for use calculating and plotting 
    bootstrap statistics. Three plots are generated (one for x, one for y and
    one for z). If the 95 percent confidence bounds for each component overlap
    each other, the two directions are not significantly different.

    Parameters
    ----------

    Data1 : a list of directional data [dec,inc]
    Data2 : a list of directional data [dec,inc]
    NumSims : number of bootstrap samples (default is 1000)
    """         
    counter=0
    BDI1=pmag.di_boot(Data1)
    BDI2=pmag.di_boot(Data2)
    print ""
    print "==============="
    print ""
    print "Here are the results of the bootstrap test for a common mean"
    CDF={'X':1,'Y':2,'Z':3}
    pylab.figure(CDF['X'],figsize=(3,3),dpi=160)
    pylab.figure(CDF['Y'],figsize=(3,3),dpi=160)
    pylab.figure(CDF['Z'],figsize=(3,3),dpi=160)
    pmagplotlib.plotCOM(CDF,BDI1,BDI2,["",""])
    
def iWatsonV(Data1,Data2,NumSims=5000):
    """
    Conduct a Watson V test for a common mean on two declination, inclination data sets
    
    This function calculates Watson's V statistic from input files through Monte Carlo
    simulation in order to test whether two populations of directional data could have
    been drawn from a common mean. The critical angle between the two sample mean
    directions and the corresponding McFadden and McElhinny (1990) classification is printed.


    Parameters
    ----------

    Data1 : a list of directional data [dec,inc]
    Data2 : a list of directional data [dec,inc]
    NumSims : number of Monte Carlo simulations (default is 5000)
    """   
    pars_1=pmag.fisher_mean(Data1)
    pars_2=pmag.fisher_mean(Data2)

    cart_1=pmag.dir2cart([pars_1["dec"],pars_1["inc"],pars_1["r"]])
    cart_2=pmag.dir2cart([pars_2['dec'],pars_2['inc'],pars_2["r"]])
    Sw=pars_1['k']*pars_1['r']+pars_2['k']*pars_2['r'] # k1*r1+k2*r2
    xhat_1=pars_1['k']*cart_1[0]+pars_2['k']*cart_2[0] # k1*x1+k2*x2
    xhat_2=pars_1['k']*cart_1[1]+pars_2['k']*cart_2[1] # k1*y1+k2*y2
    xhat_3=pars_1['k']*cart_1[2]+pars_2['k']*cart_2[2] # k1*z1+k2*z2
    Rw=np.sqrt(xhat_1**2+xhat_2**2+xhat_3**2)
    V=2*(Sw-Rw)
    # keep weighted sum for later when determining the "critical angle" 
    # let's save it as Sr (notation of McFadden and McElhinny, 1990)
    Sr=Sw 
    
    # do monte carlo simulation of datasets with same kappas as data, 
    # but a common mean
    counter=0
    Vp=[] # set of Vs from simulations
    for k in range(NumSims): 
       
    # get a set of N1 fisher distributed vectors with k1,
    # calculate fisher stats
        Dirp=[]
        for i in range(pars_1["n"]):
            Dirp.append(pmag.fshdev(pars_1["k"]))
        pars_p1=pmag.fisher_mean(Dirp)
    # get a set of N2 fisher distributed vectors with k2, 
    # calculate fisher stats
        Dirp=[]
        for i in range(pars_2["n"]):
            Dirp.append(pmag.fshdev(pars_2["k"]))
        pars_p2=pmag.fisher_mean(Dirp)
    # get the V for these
        Vk=pmag.vfunc(pars_p1,pars_p2)
        Vp.append(Vk)

    # sort the Vs, get Vcrit (95th percentile one)

    Vp.sort()
    k=int(.95*NumSims)
    Vcrit=Vp[k]

    # equation 18 of McFadden and McElhinny, 1990 calculates the critical
    # value of R (Rwc)

    Rwc=Sr-(Vcrit/2)

    # following equation 19 of McFadden and McElhinny (1990) the critical
    # angle is calculated. If the observed angle (also calculated below)
    # between the data set means exceeds the critical angle the hypothesis 
    # of a common mean direction may be rejected at the 95% confidence
    # level. The critical angle is simply a different way to present 
    # Watson's V parameter so it makes sense to use the Watson V parameter
    # in comparison with the critical value of V for considering the test
    # results. What calculating the critical angle allows for is the 
    # classification of McFadden and McElhinny (1990) to be made
    # for data sets that are consistent with sharing a common mean.

    k1=pars_1['k']
    k2=pars_2['k']
    R1=pars_1['r']
    R2=pars_2['r']
    critical_angle=np.degrees(np.arccos(((Rwc**2)-((k1*R1)**2)
                                               -((k2*R2)**2))/
                                              (2*k1*R1*k2*R2)))
    D1=(pars_1['dec'],pars_1['inc'])
    D2=(pars_2['dec'],pars_2['inc'])
    angle=pmag.angle(D1,D2)

    print "Results of Watson V test: "
    print "" 
    print "Watson's V:           " '%.1f' %(V)
    print "Critical value of V:  " '%.1f' %(Vcrit)

    if V<Vcrit:
        print '"Pass": Since V is less than Vcrit, the null hypothesis'
        print 'that the two populations are drawn from distributions'
        print 'that share a common mean direction can not be rejected.'
    elif V>Vcrit:
        print '"Fail": Since V is greater than Vcrit, the two means can'
        print 'be distinguished at the 95% confidence level.'
    print ""    
    print "M&M1990 classification:"
    print "" 
    print "Angle between data set means: " '%.1f'%(angle)
    print "Critical angle for M&M1990:   " '%.1f'%(critical_angle)
    
    if V>Vcrit:
        print ""
    elif V<Vcrit:
        if critical_angle<5:
            print "The McFadden and McElhinny (1990) classification for"
            print "this test is: 'A'"
        elif critical_angle<10:
            print "The McFadden and McElhinny (1990) classification for"
            print "this test is: 'B'"
        elif critical_angle<20:
            print "The McFadden and McElhinny (1990) classification for"
            print "this test is: 'C'"
        else:
            print "The McFadden and McElhinny (1990) classification for"
            print "this test is: 'INDETERMINATE;"
            
def lat_from_inc(inc):
    """
    Calculate paleolatitude from inclination using the dipole equation
    """
    rad=np.pi/180.
    paleo_lat=np.arctan(0.5*np.tan(inc*rad))/rad
    return paleo_lat

def lat_from_i(inc):
    """
    Calculate paleolatitude from inclination using the dipole equation
    """
    rad=np.pi/180.
    paleo_lat=np.arctan( 0.5*np.tan(inc*rad))/rad
    return paleo_lat

def iplotNET(fignum):
    """
    draws circle and tick marks for equal area projection
    """
#
# make the perimeter
#
    pylab.figure(num=fignum)
    pylab.clf()
    pylab.axis("off")
    Dcirc=np.arange(0,361.)
    Icirc=np.zeros(361,'f')
    Xcirc,Ycirc=[],[]
    for k in range(361):
        XY= pmag.dimap(Dcirc[k],Icirc[k])
        Xcirc.append(XY[0])
        Ycirc.append(XY[1])
    pylab.plot(Xcirc,Ycirc,'k')
#
# put on the tick marks
    Xsym,Ysym=[],[]
    for I in range(10,100,10):
        XY=pmag.dimap(0.,I)
        Xsym.append(XY[0])
        Ysym.append(XY[1])
    pylab.plot(Xsym,Ysym,'k+')
    Xsym,Ysym=[],[]
    for I in range(10,90,10):
        XY=pmag.dimap(90.,I)
        Xsym.append(XY[0])
        Ysym.append(XY[1])
    pylab.plot(Xsym,Ysym,'k+')
    Xsym,Ysym=[],[]
    for I in range(10,90,10):
        XY=pmag.dimap(180.,I)
        Xsym.append(XY[0])
        Ysym.append(XY[1])
    pylab.plot(Xsym,Ysym,'k+')
    Xsym,Ysym=[],[]
    for I in range(10,90,10):
        XY=pmag.dimap(270.,I)
        Xsym.append(XY[0])
        Ysym.append(XY[1])
    pylab.plot(Xsym,Ysym,'k+')
    for D in range(0,360,10):
        Xtick,Ytick=[],[]
        for I in range(4):
            XY=pmag.dimap(D,I)
            Xtick.append(XY[0])
            Ytick.append(XY[1])
        pylab.plot(Xtick,Ytick,'k')
    pylab.axis("equal")
    pylab.tight_layout()

def iplotDI(DIblock,color='k',label=''):
    """
    Plot declination, inclination data on an equal area plot

    This function modifies the plotDI function of PmagPy for use in the IPython notebook environment

    Parameters
    ----------

    DIblock : a DIblock is comprise of a list of unit vectors [dec,inc,1.]
    color : the default color is black. Other colors can be chosen (e.g. 'r')
    """
    # initialize the variables
    X_down,X_up,Y_down,Y_up=[],[],[],[]
    for rec in DIblock:
        Up,Down=0,0
        XY=pmag.dimap(rec[0],rec[1])
        if rec[1] >= 0:         
            X_down.append(XY[0])
            Y_down.append(XY[1])
        else:
            X_up.append(XY[0])
            Y_up.append(XY[1])

    if len(X_up)>0:
        pylab.scatter(X_up,Y_up,facecolors='none', edgecolors=color)

    if len(X_down)>0: 
        pylab.scatter(X_down,Y_down,facecolors=color, edgecolors=color)
    pylab.legend(loc=2)
    pylab.tight_layout()

def iplotDImean(Dec,Inc,a95,color='k',marker='o',label=''):
    """
    Plot a mean declination, inclination with alpha_95 ellipse on an equal area plot.

    Before this function is called a plot needs to be initialized with code that looks 
    something like:
    >fignum = 1
    >plt.figure(num=fignum,figsize=(10,10),dpi=160)
    >IPmag.iplotNET(fignum)

    Parameters
    ----------

    Dec : declination of mean being plotted
    Inc : inclination of mean being plotted
    a95 : a95 confidence ellipse of mean being plotted
    color : the default color is black. Other colors can be chosen (e.g. 'r')
    marker : the default is a circle. Other symbols can be chose (e.g. 's')
    label : the default is no label. Labels can be assigned
    """
    DI_dimap=pmag.dimap(Dec,Inc)
    if Inc < 0:
        pylab.plot(DI_dimap[0],DI_dimap[1],markeredgecolor=color , markerfacecolor='white', marker=marker,label=label)
    if Inc >= 0:
        pylab.plot(DI_dimap[0],DI_dimap[1],color=color,marker=marker,label=label)
    Xcirc,Ycirc=[],[]
    Da95,Ia95=pmag.circ(Dec,Inc,a95)
    pylab.legend(loc=2)
    for k in  range(len(Da95)):
        XY=pmag.dimap(Da95[k],Ia95[k])
        Xcirc.append(XY[0])
        Ycirc.append(XY[1])
    pylab.plot(Xcirc,Ycirc,color)
    pylab.tight_layout()
    
def shoot(lon, lat, azimuth, maxdist=None):
    """
    This function enables A95 error ellipses to be drawn in basemap around paleomagnetic
    poles in conjunction with equi
    (from: http://www.geophysique.be/2011/02/20/matplotlib-basemap-tutorial-09-drawing-circles/)
    """
    glat1 = lat * np.pi / 180.
    glon1 = lon * np.pi / 180.
    s = maxdist / 1.852
    faz = azimuth * np.pi / 180.
 
    EPS= 0.00000000005
    if ((np.abs(np.cos(glat1))<EPS) and not (np.abs(np.sin(faz))<EPS)):
        alert("Only N-S courses are meaningful, starting at a pole!")
 
    a=6378.13/1.852
    f=1/298.257223563
    r = 1 - f
    tu = r * np.tan(glat1)
    sf = np.sin(faz)
    cf = np.cos(faz)
    if (cf==0):
        b=0.
    else:
        b=2. * np.arctan2 (tu, cf)
 
    cu = 1. / np.sqrt(1 + tu * tu)
    su = tu * cu
    sa = cu * sf
    c2a = 1 - sa * sa
    x = 1. + np.sqrt(1. + c2a * (1. / (r * r) - 1.))
    x = (x - 2.) / x
    c = 1. - x
    c = (x * x / 4. + 1.) / c
    d = (0.375 * x * x - 1.) * x
    tu = s / (r * a * c)
    y = tu
    c = y + 1
    while (np.abs (y - c) > EPS):
 
        sy = np.sin(y)
        cy = np.cos(y)
        cz = np.cos(b + y)
        e = 2. * cz * cz - 1.
        c = y
        x = e * cy
        y = e + e - 1.
        y = (((sy * sy * 4. - 3.) * y * cz * d / 6. + x) *
              d / 4. - cz) * sy * d + tu
 
    b = cu * cy * cf - su * sy
    c = r * np.sqrt(sa * sa + b * b)
    d = su * cy + cu * sy * cf
    glat2 = (np.arctan2(d, c) + np.pi) % (2*np.pi) - np.pi
    c = cu * cy - su * sy * cf
    x = np.arctan2(sy * sf, c)
    c = ((-3. * c2a + 4.) * f + 4.) * c2a * f / 16.
    d = ((e * cy * c + cz) * sy * c + y) * sa
    glon2 = ((glon1 + x - (1. - c) * d * f + np.pi) % (2*np.pi)) - np.pi    
 
    baz = (np.arctan2(sa, b) + np.pi) % (2 * np.pi)
 
    glon2 *= 180./np.pi
    glat2 *= 180./np.pi
    baz *= 180./np.pi
 
    return (glon2, glat2, baz)

def equi(m, centerlon, centerlat, radius, color):
    """
    This function enables A95 error ellipses to be drawn in basemap around paleomagnetic poles
    in conjunction with shoot
    (from: http://www.geophysique.be/2011/02/20/matplotlib-basemap-tutorial-09-drawing-circles/).
    """
    glon1 = centerlon
    glat1 = centerlat
    X = []
    Y = []
    for azimuth in range(0, 360):
        glon2, glat2, baz = shoot(glon1, glat1, azimuth, radius)
        X.append(glon2)
        Y.append(glat2)
    X.append(X[0])
    Y.append(Y[0])
 
    X,Y = m(X,Y)
    plt.plot(X,Y,color)

def poleplot(mapname,plong,plat,A95,label='',color='k',marker='o'):
    """
    This function plots a paleomagnetic pole and A95 error ellipse on whatever 
    current map projection has been set using the basemap plotting library.

    Parameters
    -----------
    mapname : the name of the current map that has been developed using basemap
    plong : the longitude of the paleomagnetic pole being plotted (in degrees E)
    plat : the latitude of the paleomagnetic pole being plotted (in degrees)
    A95 : the A_95 confidence ellipse of the paleomagnetic pole (in degrees)
    label : a string that is the label for the paleomagnetic pole being plotted
    color : the color desired for the symbol and its A95 ellipse (default is 'k' aka black)
    marker : the marker shape desired for the pole mean symbol (default is 'o' aka a circle)
    """
    centerlon, centerlat = mapname(plong,plat)
    A95_km=A95*111.32
    mapname.scatter(centerlon,centerlat,20,marker=marker,color=color,label=label,zorder=101)
    equi(mapname, plong, plat, A95_km,color)

def plot_pole(mapname,plong,plat,A95,label='',color='k',marker='o',legend='no'):
    """
    This function plots a paleomagnetic pole and A95 error ellipse on whatever 
    current map projection has been set using the basemap plotting library.

    Required Parameters
    -----------
    mapname : the name of the current map that has been developed using basemap
    plong : the longitude of the paleomagnetic pole being plotted (in degrees E)
    plat : the latitude of the paleomagnetic pole being plotted (in degrees)
    A95 : the A_95 confidence ellipse of the paleomagnetic pole (in degrees)
    
    Optional Parameters
    -----------
    label : a string that is the label for the paleomagnetic pole being plotted
    color : the color desired for the symbol and its A95 ellipse (default is 'k' aka black)
    marker : the marker shape desired for the pole mean symbol (default is 'o' aka a circle)
    legend : the default is no legend ('no'). Putting 'yes' will plot a legend.
    """
    centerlon, centerlat = mapname(plong,plat)
    A95_km=A95*111.32
    mapname.scatter(centerlon,centerlat,20,marker=marker,color=color,label=label,zorder=101)
    equi(mapname, plong, plat, A95_km,color)
    if legend=='yes':
        pylab.legend(loc=2)

def vgpplot(mapname,plong,plat,label='',color='k',marker='o'):
    """
    This function plots a paleomagnetic pole on whatever current map projection
    has been set using the basemap plotting library.

    Parameters
    -----------
    mapname : the name of the current map that has been developed using basemap
    plong : the longitude of the paleomagnetic pole being plotted (in degrees E)
    plat : the latitude of the paleomagnetic pole being plotted (in degrees)
    color : the color desired for the symbol and its A95 ellipse (default is 'k' aka black)
    marker : the marker shape desired for the pole mean symbol (default is 'o' aka a circle)
    """
    centerlon, centerlat = mapname(plong,plat)
    mapname.scatter(centerlon,centerlat,20,marker=marker,color=color,label=label,zorder=100)

def plot_vgp(mapname,plong,plat,label='',color='k',marker='o',legend='no'):
    """
    This function plots a paleomagnetic pole on whatever current map projection
    has been set using the basemap plotting library.

    Required Parameters
    -----------
    mapname : the name of the current map that has been developed using basemap
    plong : the longitude of the paleomagnetic pole being plotted (in degrees E)
    plat : the latitude of the paleomagnetic pole being plotted (in degrees)

    Optional Parameters
    -----------
    color : the color desired for the symbol and its A95 ellipse (default is 'k' aka black)
    marker : the marker shape desired for the pole mean symbol (default is 'o' aka a circle)
    label : the default is no label. Labels can be assigned.
    legend : the default is no legend ('no'). Putting 'yes' will plot a legend.
    """
    centerlon, centerlat = mapname(plong,plat)
    mapname.scatter(centerlon,centerlat,20,marker=marker,color=color,label=label,zorder=100)
    if legend=='yes':
        pylab.legend(loc=2)

def VGP_calc(dataframe):
    """
    This function calculates paleomagnetic poles from directional data within a pandas.DataFrame

    Parameters
    ----------- 
    dataframe : the name of the pandas.DataFrame containing the data
    dataframe['site_lat'] : the latitude of the site
    dataframe['site_long'] : the longitude of the site
    dataframe['inc_tc'] : the tilt-corrected inclination 
    dataframe['dec_tc'] : the tilt-corrected declination
    """
    #calculate the paleolatitude/colatitude
    dataframe['paleolatitude']=np.degrees(np.arctan(0.5*np.tan(np.radians(dataframe['inc_tc']))))
    dataframe['colatitude']=90-dataframe['paleolatitude']
    #calculate the latitude of the pole
    dataframe['pole_lat']=np.degrees(np.arcsin(np.sin(np.radians(dataframe['site_lat']))*
                                                         np.cos(np.radians(dataframe['colatitude']))+
                                                         np.cos(np.radians(dataframe['site_lat']))*
                                                         np.sin(np.radians(dataframe['colatitude']))*
                                                         np.cos(np.radians(dataframe['dec_tc']))))
    #calculate the longitudinal difference between the pole and the site (beta)
    dataframe['beta']=np.degrees(np.arcsin((np.sin(np.radians(dataframe['colatitude']))*
                                      np.sin(np.radians(dataframe['dec_tc'])))/
                                     (np.cos(np.radians(dataframe['pole_lat'])))))
    #generate a boolean array (mask) to use to distinguish between the two possibilities for pole longitude
    #and then calculate pole longitude using the site location and calculated beta
    mask = np.cos(np.radians(dataframe['colatitude']))>np.sin(np.radians(dataframe['site_lat']))*np.sin(np.radians(dataframe['pole_lat']))
    dataframe['pole_long']=np.where(mask,(dataframe['site_long']+dataframe['beta'])%360.,(dataframe['site_long']+180-dataframe['beta'])%360.)
    #calculate the antipode of the poles
    dataframe['pole_lat_rev']=-dataframe['pole_lat']
    dataframe['pole_long_rev']=(dataframe['pole_long']-180.)%360. 
    #the 'colatitude' and 'beta' columns were created for the purposes of the pole calculations
    #but aren't of further use and are deleted
    del dataframe['colatitude']
    del dataframe['beta']

def bootstrap_common_mean(Data1,Data2,NumSims=1000):
    """
    Conduct a bootstrap test (Tauxe, 2010) for a common mean on two declination,
    inclination data sets
    
    This function modifies code from PmagPy for use calculating and plotting 
    bootstrap statistics. Three plots are generated (one for x, one for y and
    one for z). If the 95 percent confidence bounds for each component overlap
    each other, the two directions are not significantly different.

    Arguments
    ----------
    Data1 : a list of directional data [dec,inc]
    Data2 : a list of directional data [dec,inc]
    NumSims : number of bootstrap samples (default is 1000)
    """         
    counter=0
    BDI1=pmag.di_boot(Data1)
    BDI2=pmag.di_boot(Data2)

    cart1= pmag.dir2cart(BDI1).transpose()
    X1,Y1,Z1=cart1[0],cart1[1],cart1[2]
    cart2= pmag.dir2cart(BDI2).transpose()
    X2,Y2,Z2=cart2[0],cart2[1],cart2[2]
    
    print "Here are the results of the bootstrap test for a common mean:"
    
    fignum = 1
    fig = plt.figure(figsize=(9,3))
    fig = plt.subplot(1,3,1)
    
    minimum = int(0.025*len(X1))
    maximum = int(0.975*len(X1))
    
    X1,y=pmagplotlib.plotCDF(fignum,X1,"X component",'r',"")
    bounds1=[X1[minimum],X1[maximum]]
    pmagplotlib.plotVs(fignum,bounds1,'r','-')

    X2,y=pmagplotlib.plotCDF(fignum,X2,"X component",'b',"")
    bounds2=[X2[minimum],X2[maximum]]
    pmagplotlib.plotVs(fignum,bounds2,'b','--')
    plt.ylim(0,1)
    
    plt.subplot(1,3,2)
    
    Y1,y=pmagplotlib.plotCDF(fignum,Y1,"Y component",'r',"")
    bounds1=[Y1[minimum],Y1[maximum]]
    pmagplotlib.plotVs(fignum,bounds1,'r','-')
    
    Y2,y=pmagplotlib.plotCDF(fignum,Y2,"Y component",'b',"")
    bounds2=[Y2[minimum],Y2[maximum]]
    pmagplotlib.plotVs(fignum,bounds2,'b','--')
    plt.ylim(0,1)
    
    plt.subplot(1,3,3)
    
    Z1,y=pmagplotlib.plotCDF(fignum,Z1,"Z component",'r',"")
    bounds1=[Z1[minimum],Z1[maximum]]
    pmagplotlib.plotVs(fignum,bounds1,'r','-')
    
    Z2,y=pmagplotlib.plotCDF(fignum,Z2,"Z component",'b',"")
    bounds2=[Z2[minimum],Z2[maximum]]
    pmagplotlib.plotVs(fignum,bounds2,'b','--')
    plt.ylim(0,1)
    
    plt.tight_layout()
    plt.show()

def watson_common_mean(Data1,Data2,NumSims=5000,plot='no'):
    """
    Conduct a Watson V test for a common mean on two declination, inclination data sets
    
    This function calculates Watson's V statistic from input files through Monte Carlo
    simulation in order to test whether two populations of directional data could have
    been drawn from a common mean. The critical angle between the two sample mean
    directions and the corresponding McFadden and McElhinny (1990) classification is printed.


    Required Arguments
    ----------
    Data1 : a list of directional data [dec,inc]
    Data2 : a list of directional data [dec,inc]
    
    Optional Arguments
    ----------
    NumSims : number of Monte Carlo simulations (default is 5000)
    plot : the default is no plot ('no'). Putting 'yes' will the plot the CDF from
    the Monte Carlo simulations.
    """   
    pars_1=pmag.fisher_mean(Data1)
    pars_2=pmag.fisher_mean(Data2)

    cart_1=pmag.dir2cart([pars_1["dec"],pars_1["inc"],pars_1["r"]])
    cart_2=pmag.dir2cart([pars_2['dec'],pars_2['inc'],pars_2["r"]])
    Sw=pars_1['k']*pars_1['r']+pars_2['k']*pars_2['r'] # k1*r1+k2*r2
    xhat_1=pars_1['k']*cart_1[0]+pars_2['k']*cart_2[0] # k1*x1+k2*x2
    xhat_2=pars_1['k']*cart_1[1]+pars_2['k']*cart_2[1] # k1*y1+k2*y2
    xhat_3=pars_1['k']*cart_1[2]+pars_2['k']*cart_2[2] # k1*z1+k2*z2
    Rw=np.sqrt(xhat_1**2+xhat_2**2+xhat_3**2)
    V=2*(Sw-Rw)
    # keep weighted sum for later when determining the "critical angle" 
    # let's save it as Sr (notation of McFadden and McElhinny, 1990)
    Sr=Sw 
    
    # do monte carlo simulation of datasets with same kappas as data, 
    # but a common mean
    counter=0
    Vp=[] # set of Vs from simulations
    for k in range(NumSims): 
       
    # get a set of N1 fisher distributed vectors with k1,
    # calculate fisher stats
        Dirp=[]
        for i in range(pars_1["n"]):
            Dirp.append(pmag.fshdev(pars_1["k"]))
        pars_p1=pmag.fisher_mean(Dirp)
    # get a set of N2 fisher distributed vectors with k2, 
    # calculate fisher stats
        Dirp=[]
        for i in range(pars_2["n"]):
            Dirp.append(pmag.fshdev(pars_2["k"]))
        pars_p2=pmag.fisher_mean(Dirp)
    # get the V for these
        Vk=pmag.vfunc(pars_p1,pars_p2)
        Vp.append(Vk)

    # sort the Vs, get Vcrit (95th percentile one)

    Vp.sort()
    k=int(.95*NumSims)
    Vcrit=Vp[k]

    # equation 18 of McFadden and McElhinny, 1990 calculates the critical
    # value of R (Rwc)

    Rwc=Sr-(Vcrit/2)

    # following equation 19 of McFadden and McElhinny (1990) the critical
    # angle is calculated. If the observed angle (also calculated below)
    # between the data set means exceeds the critical angle the hypothesis 
    # of a common mean direction may be rejected at the 95% confidence
    # level. The critical angle is simply a different way to present 
    # Watson's V parameter so it makes sense to use the Watson V parameter
    # in comparison with the critical value of V for considering the test
    # results. What calculating the critical angle allows for is the 
    # classification of McFadden and McElhinny (1990) to be made
    # for data sets that are consistent with sharing a common mean.

    k1=pars_1['k']
    k2=pars_2['k']
    R1=pars_1['r']
    R2=pars_2['r']
    critical_angle=np.degrees(np.arccos(((Rwc**2)-((k1*R1)**2)
                                               -((k2*R2)**2))/
                                              (2*k1*R1*k2*R2)))
    D1=(pars_1['dec'],pars_1['inc'])
    D2=(pars_2['dec'],pars_2['inc'])
    angle=pmag.angle(D1,D2)

    print "Results of Watson V test: "
    print "" 
    print "Watson's V:           " '%.1f' %(V)
    print "Critical value of V:  " '%.1f' %(Vcrit)

    if V<Vcrit:
        print '"Pass": Since V is less than Vcrit, the null hypothesis'
        print 'that the two populations are drawn from distributions'
        print 'that share a common mean direction can not be rejected.'
    elif V>Vcrit:
        print '"Fail": Since V is greater than Vcrit, the two means can'
        print 'be distinguished at the 95% confidence level.'
    print ""    
    print "M&M1990 classification:"
    print "" 
    print "Angle between data set means: " '%.1f'%(angle)
    print "Critical angle for M&M1990:   " '%.1f'%(critical_angle)
    
    if V>Vcrit:
        print ""
    elif V<Vcrit:
        if critical_angle<5:
            print "The McFadden and McElhinny (1990) classification for"
            print "this test is: 'A'"
        elif critical_angle<10:
            print "The McFadden and McElhinny (1990) classification for"
            print "this test is: 'B'"
        elif critical_angle<20:
            print "The McFadden and McElhinny (1990) classification for"
            print "this test is: 'C'"
        else:
            print "The McFadden and McElhinny (1990) classification for"
            print "this test is: 'INDETERMINATE;"

    if plot=='yes':
        CDF={'cdf':1}
        #pmagplotlib.plot_init(CDF['cdf'],5,5)
        p1 = pmagplotlib.plotCDF(CDF['cdf'],Vp,"Watson's V",'r',"")
        p2 = pmagplotlib.plotVs(CDF['cdf'],[V],'g','-')
        p3 = pmagplotlib.plotVs(CDF['cdf'],[Vp[k]],'b','--')
        pmagplotlib.drawFIGS(CDF)

def sb_vgp_calc(dataframe):
    """
    This function calculates the angular dispersion of VGPs and corrects
    for within site dispersion to return a value S_b. The input data
    needs to be within a pandas Dataframe. The function also plots the
    VGPs and their associated Fisher mean on a projection centered on
    the mean.
    
    Parameters
    ----------- 
    dataframe : the name of the pandas.DataFrame containing the data
    
    the data frame needs to contain these columns:
    dataframe['site_lat'] : latitude of the site
    dataframe['site_lon'] : longitude of the site ---- changed to site_long so that it works for a given DF
    dataframe['inc_tc'] : tilt-corrected inclination
    dataframe['dec_tc'] : tilt-corrected declination
    dataframe['k'] : fisher precision parameter for directions
    dataframe['vgp_lat'] : VGP latitude ---- changed to pole_lat so that it works for a given DF
    dataframe['vgp_lon'] : VGP longitude ---- changed to pole_long so that it works for a given DF
    """

    # calculate the mean from the directional data
    dataframe_dirs=[]
    for n in range(0,len(dataframe)): 
        dataframe_dirs.append([dataframe['dec_tc'][n],
                               dataframe['inc_tc'][n],1.])
    dataframe_dir_mean=pmag.fisher_mean(dataframe_dirs)

    # calculate the mean from the vgp data
    dataframe_poles=[]
    dataframe_pole_lats=[]
    dataframe_pole_lons=[]
    for n in range(0,len(dataframe)): 
        dataframe_poles.append([dataframe['pole_long'][n],
                                dataframe['pole_lat'][n],1.])
        dataframe_pole_lats.append(dataframe['pole_lat'][n])
        dataframe_pole_lons.append(dataframe['pole_long'][n])                            
    dataframe_pole_mean=pmag.fisher_mean(dataframe_poles)

    # calculate mean paleolatitude from the directional data
    dataframe['paleolatitude']=lat_from_inc(dataframe_dir_mean['inc'])

    angle_list=[]
    for n in range(0,len(dataframe)):
        angle=pmag.angle([dataframe['pole_long'][n],dataframe['pole_lat'][n]],
                         [dataframe_pole_mean['dec'],dataframe_pole_mean['inc']])
        angle_list.append(angle[0])
    dataframe['delta_mean-pole']=angle_list

    # use eq. 2 of Cox (1970) to translate the directional precision parameter
    # into pole coordinates using the assumption of a Fisherian distribution in
    # directional coordinates and the paleolatitude as calculated from mean
    # inclination using the dipole equation
    dataframe['K']=dataframe['k']/(0.125*(5+18*np.sin(np.deg2rad(dataframe['paleolatitude']))**2
                                          +9*np.sin(np.deg2rad(dataframe['paleolatitude']))**4))
    dataframe['Sw']=81/(dataframe['K']**0.5)

    summation=0
    N=0
    for n in range(0,len(dataframe)):
        quantity=dataframe['delta_mean-pole'][n]**2-dataframe['Sw'][n]**2/np.float(dataframe['n'][n])
        summation+=quantity
        N+=1

    Sb=((1.0/(N-1.0))*summation)**0.5
    
    plt.figure(figsize=(6, 6))
    m = Basemap(projection='ortho',lat_0=dataframe_pole_mean['inc'],lon_0=dataframe_pole_mean['dec'],resolution='c',area_thresh=50000)
    m.drawcoastlines(linewidth=0.25)
    m.fillcontinents(color='bisque',lake_color='white',zorder=1)
    m.drawmapboundary(fill_color='white')
    m.drawmeridians(np.arange(0,360,30))
    m.drawparallels(np.arange(-90,90,30))
    
    plot_vgp(m,dataframe_pole_lons,dataframe_pole_lats,dataframe_pole_lons)
    plot_pole(m,dataframe_pole_mean['dec'],dataframe_pole_mean['inc'],
                    dataframe_pole_mean['alpha95'],color='r',marker='s')
    return Sb

def make_di_block(dec,inc):
    """
    Some pmag.py functions require a list of unit vectors [dec,inc,1.] as input. This
    function takes declination and inclination data and make it into such a list
    """
    di_block=[]
    for n in range(0,len(dec)):
        di_block.append([dec[n],inc[n],1.0])
    return di_block
