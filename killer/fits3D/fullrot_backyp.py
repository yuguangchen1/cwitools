def rot(A): 
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
        ## CD1_1b = CD1_1a*cosB - CD2_1a*sinB
        ## CD2_1b = CD2_1a*cosB + CD1_1a*sinB
        ## CD2_2b = CD2_2a*cosB - CD1_2a*sinB
        ## CD1_2b = CD1_2a*cosB + CD2_2a*sinB
        ##
        
        #Get angle in radians
        Ar = A*np.pi/180
        
        #Get old values
        CD1_1a = self.header["CD1_1"]
        CD1_2a = self.header["CD1_2"]        
        CD2_1a = self.header["CD2_1"]
        CD2_2a = self.header["CD2_2"]
        
        #Update header values according to rotation
        self.header["CD1_1"] = CD1_1a*np.cos(Ar) - CD2_1a*np.sin(Ar)
        self.header["CD2_1"] = CD2_1a*np.cos(Ar) + CD1_1a*np.sin(Ar)
        self.header["CD2_2"] = CD2_2a*np.cos(Ar) - CD1_2a*np.sin(Ar)
        self.header["CD1_2"] = CD1_2a*np.cos(Ar) + CD2_2a*np.sin(Ar)
