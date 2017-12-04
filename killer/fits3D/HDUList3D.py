from astropy.io import fits
from copy import deepcopy
from scipy.ndimage.interpolation import rotate as scipy_rotate
import numpy as np
import sys


# FITS3D inherits from astropy.io.fits.HDUList and adds an astropy.wcs.WCS object as a class attribute.
# The purpose of this class is to provide 3D transformation functions (crop, scale, rotate, translate)
# which also update the 3D WCS information accordingly.

# AXES 1,2,3 are referred to as X, Y, W in this class.
# Numpy loads the data in the shape [W,Y,X]
#
# Assumptions:
# 1. CRVAL1 = RA (dd.ddd) and CRVAL2 = DEC (dd.ddd)
# 2. WCS axis info is given as CD1_1, CD2_2 etc. 

class fits3D(fits.HDUList):

    def __init__(self,filename):
    
        fits.HDUList.__init__(self,fits.open(filename))
        
        self.data = self[0].data
        self.header = self[0].header
        self.instConfig()

    
    
    def rotate(self,A):
    
        ## 
        ## This part, updating CRPIX1/2, only works for 90, 180 or 270 degrees.
        ## 
        ## Scipy.ndimage.interpolate.rotate uses the upper-right corner as a pivot and pads the image.
        ## This makes the coordinate system transformation messy. 
        ## Will generalize to any angle in a future update, but interpolating for non-right-angles
        ## adds noise anyway, so it's better not to do that.
        ##
        
        # Extract useful variables for 90 degree rotation of CRPIX values
        x0,y0 = self.header["CRPIX1"],self.header["CRPIX2"]
        X, Y  = self.header["NAXIS1"],self.header["NAXIS2"]

        #For 270 deg rotation (x1,y1) = (y0,X-x0)
        if A==270: self.header["CRPIX1"], self.header["CRPIX2"] =  y0, X - x0
           
        #For 180 deg rotation: (x1,y1) = (X-x0,Y-y0)
        elif A==180: self.header["CRPIX1"], self.header["CRPIX2"] = X-x0, Y-y0 

        #For 270 deg rotation: (x1,y1) = (Y-y0,x0)
        elif A==90: self.header["CRPIX1"], self.header["CRPIX2"] = Y-y0, x0 

        #Currently only allowing right-angle rotations. 
        else:
            print("Only 90, 180 or 270 degree rotations are allowed in this version.")
            return
            
        ## This following part, updating the axes, will work for any angle.
        ##
        ## Assuming an underling world coordinate system of VAL1 along AXIS1 and VAL2 along AXIS2 at PA=0
        ## Given an input image at angle A with respecto to VAL1 and VAL2, our header values would be:
        ##
        ## CD1_1a = XcosA
        ## CD2_1a = XsinA
        ## CD2_2a = YcosA
        ## CD1_2a = YsinA
        ##
        ## where X and Y are the plate scales in the X and Y axes of the image, respectively.
        ## Now, given a rotation of B, following simple cos(A+B) and sin(A+B) rules, we get:
        ##
        ## CD1_1b = CD1_1a*cosB + CD2_1a*sinB
        ## CD1_2b = CD1_2a*cosB + CD2_2a*sinB
        ## CD2_1b = CD2_1a*cosB - CD1_1a*sinB
        ## CD2_2b = CD2_2a*cosB - CD1_2a*sinB
        ## 
        ##
        
        #Get angle in radians
        Ar = A*np.pi/180
        
        #Get old values
        CD1_1a = self.header["CD1_1"]
        CD1_2a = self.header["CD1_2"]        
        CD2_1a = self.header["CD2_1"]
        CD2_2a = self.header["CD2_2"]
        
        #Update header values according to rotation
        self.header["CD1_1"] = CD1_1a*np.cos(Ar) + CD2_1a*np.sin(Ar)
        self.header["CD1_2"] = CD1_2a*np.cos(Ar) + CD2_2a*np.sin(Ar)
        self.header["CD2_1"] = CD2_1a*np.cos(Ar) - CD1_1a*np.sin(Ar)
        self.header["CD2_2"] = CD2_2a*np.cos(Ar) - CD1_2a*np.sin(Ar)
        

        ##
        ## Rotate the data now that the WCS is all sorted out
        ## 
        self.data = scipy_rotate(self.data,A,axes=(1,2))
            
    #Crop cube with lower and upper limit tuples for each axis
    def crop(self,xx=(2,-2),yy=(18,80),ww=(200,300)):
    
        #Crop cube
        self.data = self.data[ww[0]:ww[1],yy[0]:yy[1],xx[0]:xx[1]]

        #Change RA reference pixel
        #self.header["CRPIX1"] -= xx[0]
        self.header["CRVAL1"] += (xx[0]*self.header["CD1_1"] +yy[0]*self.header["CD1_2"])/np.cos(self.header["CRVAL2"]*np.pi/180)
        #Change DEC reference pixel
        #self.header["CRPIX2"] -= yy[0]
        self.header["CRVAL2"] += xx[0]*self.header["CD2_1"] +yy[0]*self.header["CD2_2"]
        
        
        #Change WAV reference pixel
        #self.header["CRPIX3"] -= ww[0]
        
    #Allow for different keywords fo        r different instruments
    def instConfig(self):
        instkey = "INSTRUME"
        if instkey in self[0].header.keys():            
            if self[0].header[instkey]=="KCWI":
                self.kwPA = "ROTPOSN"
            elif self[0].header[instkey]=="PCWI":
                self.kwPA = "ROTPA"
            
               
    #Save as astropy.io.fits.HDUList object
    def save(self,path):   
        hdu = fits.PrimaryHDU(self.data)
        hdulist = fits.HDUList([hdu])
        hdulist[0].header = self[0].header        
        hdulist.writeto(path,clobber=True)


f3d = fits3D(sys.argv[1])
#f3d.crop()
#f3d.crop(xx=(0,-1),yy=(0,-1),ww=(0,-1))
f3d.rotate(270)
f3d.save('test90r.fits')



