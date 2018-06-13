class Vector():
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y
        
    def magnitude(self):
        return ((self.x)**2 + (self.y)**2)**0.5
    
    def shortenTo(self, radius):
        magnitude = self.magnitude()
        unitX = self.x/magnitude
        unitY = self.y/magnitude
        
        return Vector(unitX*radius, unitY*radius)
        
    def add(self, addedVector):
        self.x += addedVector.x
        self.y += addedVector.y
        
    def subtract(self, subtractedVector):
        self.x -= subtractedVector.x
        self.y -= subtractedVector.y