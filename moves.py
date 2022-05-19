import copy


class restriction:
    def __init__(self , sets, particleRanges):

        self.particleRanges=particleRanges
        self.sets=sets
    def toJson(self):
        return {
            "sets" : self.sets,
            "minParticleNumber" : [  setRange[0]    for setRange in self.particleRanges ],
            "maxParticleNumber" : [  setRange[1]    for setRange in self.particleRanges ]
        }


class semiOpenClose:
    def __init__( self, setA, setB , C, l=1 ):
        self._jOpen={"setA" : setA, "setB" : setB , "C" : C ,  "reconstructionMaxLength" : l,"kind" : "semiOpen"}
        
        self.name="semiOpenClose"
    
    def toJson(self):
        jClose=copy.deepcopy(self._jOpen)
        jClose["kind"]="semiClose"
        return [self._jOpen,jClose ] 

class levy:
    def __init__( self, l = 1 ):
        self._j={ "reconstructionMaxLength" : l,"kind" : "levy"}
        self.name="levy"

    def toJson(self):
        return [self._j]

class swap:
    def __init__( self, l = 1 ):
        self._j={ "reconstructionMaxLength" : l,"kind" : "swap"}
        self.name="swap"

    def toJson(self):
        return [self._j]

class advanceRecedeHead:
    def __init__( self, l = 1 , restriction=None):
        self._jAdvance={ "reconstructionMaxLength" : l,"kind" : "advanceHead"}
        self._jRecede={ "reconstructionMaxLength" : l,"kind" : "recedeHead"}
        self.name="advanceRecedeHead"

        

    def toJson(self):
        return [self._jAdvance,self._jRecede]

    
class advanceRecedeHeadTail:
    def __init__( self, setA , setB, l = 1 , restriction=None ):
        self._jAdvance={ "reconstructionMaxLength" : l,"kind" : "advanceHeadTail","setA" : setA, "setB" : setB}
        self._jRecede={ "reconstructionMaxLength" : l,"kind" : "recedeHeadTail", "setA" : setA, "setB" : setB}
        self.name="advanceRecedeHeadTail"
        if restriction is not None:
            self._jAdvance["restriction"]=restriction.toJson()
            self._jRecede["restriction"]=restriction.toJson()
            

    def toJson(self):
        return [ self._jAdvance, self._jRecede ]


class fullOpenClose:
    def __init__( self, setA , setB, C,  l = 1 , restriction=None ):
        self._jOpen={ "reconstructionMaxLength" : l,"kind" : "fullOpen","setA" : setA, "setB" : setB,"C" : C }
        self._jClose={ "reconstructionMaxLength" : l,"kind" : "fullClose","setA" : setA, "setB" : setB,"C" : C}
        self.name="fullOpenClose"
        if restriction is not None:
            self._jClose["restriction"]=restriction.toJson()
            
    def toJson(self):
        return [ self._jOpen, self._jClose ]

class createDeleteTwoWorms:
    def __init__( self, setA , setB, C , l = 1 ,restriction=None):
        self._jCreate={ "reconstructionMaxLength" : l,"kind" : "createTwoWorms","setA" : setA, "setB" : setB , "CA" : C[0],
            "CB" : C[1], "initialBeadSampling" : { "kind" : "uniform"} }
        self._jDelete=copy.copy(self._jCreate)
        self._jDelete["kind"]="deleteTwoWorms"
        self.name="createDeleteTwoWorms"
        if restriction is not None:
            self._jCreate["restriction"]=restriction.toJson()
            self._jDelete["restriction"]=restriction.toJson()


    def toJson(self):
        return [ self._jCreate, self._jDelete ]




    

class translate:
    def __init__( self, delta , l= 1 ):
        self._j={ "delta" : delta,"kind" : "translate"}
        self.name="translate"
    def toJson(self):
        return [self._j]
    

class moveHead:
    def __init__( self, l = 1 ):
        self._j={ "reconstructionMaxLength" : l,"kind" : "moveHead"}
        self.name="moveHead"
    
    def toJson(self):
        return [self._j]

    
class moveTail:
    def __init__( self, l = 1 ):
        self._j={ "reconstructionMaxLength" : l,"kind" : "moveTail"}
        self.name="moveTail"
    def toJson(self):
        return [self._j]