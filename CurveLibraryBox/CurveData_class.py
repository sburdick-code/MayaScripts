class CurveData:
    def __init__( self, name_val, controlPoints_val ):
        self.name = name_val
        self.controlPoints = controlPoints_val

    def formatted( self ):
        curveDictionary = { 'name': self.name,
                            'controlPoints': self.controlPoints }

        return curveDictionary