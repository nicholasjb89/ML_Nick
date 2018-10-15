from PIL import Image, ImageGrab
import time

class Picture(object):
    def __init__(self,location):
        self.image = Image.open(location).convert("RGB")
        self.data = self.image.load()
        self.res = self.image.size
        
    def indexCheck(self,pos):
        try:
            self.data[pos[0],pos[1]]
            return True
        except:
            return False
    def pixelList(self,color):
        
        positions = []
        for x in range(self.res[0]-1):
            for y in range(self.res[1]-1):
                if self.data[x,y] == (color[0],color[1],color[2]):
                    positions.append([x,y])
        return positions
    
    def color(self, pixel):
        print(pixel)
        return self.data[pixel[0], pixel[1]]

class Search(object):
    def __init__(self):
        pass
    def search(self,ssPath, imagePath):
        timestart = time.time()
        
        screen = Picture(ssPath)
        image = Picture(imagePath)
        
        sPixel = [] ; sColor = []

        for x in range(int(screen.res[0]/15)):
            x = x * 15
            
            for y in range(int(screen.res[1]/15)):
                y = y * 15
                sPixel = [x,y]
                sColor = screen.color(sPixel)

                iPixels = image.pixelList(sColor)
                
                if len(iPixels) != 0:
                    
                    for iPixel in iPixels:
                        sPos, iPos = self.check(sPixel, iPixel, image, screen)
                        sPixel = [x,y] #hotfix for check altering sPixel (resets position)
                            
                        if sPos and iPos:
                            print(time.time() - timestart)
                            
        return False
                                        
    def compair(self,p1,p2):
        print(p1,p2)
        p1RGB = (p1[0],p1[1],p1[2])
        p2RGB = (p2[0],p2[1],p2[2])
        if p1RGB == p2RGB: return True
        else: return False

    def check(self,sPixel,iPixel,image,screen):

        """moves location to the right side of the image"""

        while image.indexCheck(iPixel) != False:

            sColor = screen.color(sPixel)
            iColor = image.color(iPixel)

            if self.compair(sColor,iColor) == False:
                return (False, False)

            sPixel[0] += 1
            iPixel[0] += 1
        sPixel[0] -= 1
        iPixel[0] -= 1
        """moves location to the top of the image"""
        while image.indexCheck(iPixel) != False:

            sColor = screen.color(sPixel)
            iColor = image.color(iPixel)
            
            if self.compair(sColor,iColor) == False:
                return (False, False)

            sPixel[1] -= 1
            iPixel[1] -= 1
        sPixel[1] += 1
        iPixel[1] += 1
        for y in range(image.res[1]-1):
            
            for x in range(image.res[0]-1):
                sPixel[0] -= 1
                iPixel[0] -= 1

                sColor = screen.color(sPixel)
                iColor = image.color(iPixel)
                if screen.indexCheck(sPixel):
                    
                    if self.compair(sColor,iColor):
                        pass
                    else:
                        return (False, False)
                    
            sPixel = [sPixel[0] + image.res[0]-1, sPixel[1]+1]
            iPixel = [image.res[0]-1, iPixel[1]+1]

        return sPixel, iPixel

Search().search("C:/Users/rambo/Desktop/test/0000000249.jpg", "C:/Users/rambo/OneDrive/Documents/Programming/Python/PycharmProjects/ML_Nick/Training/images/icons/Q.jpg" )
