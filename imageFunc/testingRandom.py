
class raObject():
    WIDTH = None
    def __init__(self,w = 0):
        self.w = w*2
        self.WIDTH = (200,w)
        #self.you()
        pass
    def you(self):
        self.war,_  = 10, 5;

pi = raObject(7)
pi.you()

print(pi.war)