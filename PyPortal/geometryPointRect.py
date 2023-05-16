class pointXY:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class rectangleTL_BR:
    def __init__(self, topLeftPoint, bottomRightPoint):
        self.topLeftPoint = topLeftPoint
        self.bottomRightPoint = bottomRightPoint
        self.width = bottomRightPoint.x - topLeftPoint.x
        self.height = bottomRightPoint.y - topLeftPoint.y
        
    
    # https://www.tutorialspoint.com/check-if-a-point-lies-on-or-inside-a-rectangle-in-python
    def pointInside(self, pt):
        if(pt[0] > self.topLeftPoint.x and pt[0] < self.bottomRightPoint.x and pt[1] > self.topLeftPoint.y and pt[1] < self.bottomRightPoint.y):
            # print(f"Point {pt} is in rectangle [({self.topLeftPoint.x}, {self.topLeftPoint.y}), ({self.bottomRightPoint.x}, {self.bottomRightPoint.y})]")
            return True
        else:
            return False