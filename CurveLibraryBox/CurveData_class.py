class CurveData:
    def __init__( self, name_val, controlPoints_val ):
        self.name = name_val
        self.controlPoints = controlPoints_val

    # formats the class CurveData into a JSON dictionary
    def formatted( self ):
        curveDictionary = { 'name': self.name,
                            'controlPoints': self.controlPoints }

        return curveDictionary

    # takes a dictionary and assigns the variables of the class to its contents
    def deformatted( self, pDictionary ):
        self.name = pDictionary['name']
        self.controlPoints = pDictionary['controlPoints']