import numpy as np
import json

class canonicalEnsamble:
    def __init__(self,N, boxSize, T):
        self.N=N
        self.boxSize=boxSize
        self.T=T


class run:
    def __init__(self, nBlocks,stepsPerBlock,correlationSteps=None):
        self.nBlocks=nBlocks
        self.stepsPerBlock=stepsPerBlock
        self.correlationSteps=correlationSteps
        self.saveConfigurations=True



class model:
    def __init__(self, ensamble , nBeads , actions ):
        self.ensamble=ensamble
        self.actions=actions
        self.nBeads=nBeads



class simulation:
    def __init__( self, model, run , moves,observables=None,folder="."):
        self.model=model
        self.run=run
        self.observables=observables
        self.moves=moves
        self.seed=567
    
    def toJson(self ):
        j={}
        N0=self.model.ensamble.N
        nSpecies=len(N0)
        j["inverseTemperature"]=float(1/self.model.ensamble.T)
        j["nBeads"]=int(self.model.nBeads)
        j["stepsPerBlock"]=int(self.run.stepsPerBlock)
        j["correlationSteps"]=int(self.run.correlationSteps)
        j["nBlocks"]=int(self.run.nBlocks)
        j["particles"]=[int(n) for n in N0]
        j["ensamble"]="grandCanonical"
        j["checkPointFile"]="latest.hdf5"
        j["saveConfigurations"]=self.run.saveConfigurations
        j["chemicalPotential"]= [0 for n in range(nSpecies)]
        j["maxParticles"]=[ int(n)+2 for n in N0 ]
        j["checkPointFile"]="latest.hdf5"
        j["lBox"]=[ float(L) for L in self.model.ensamble.boxSize ]

        j["actions"]= [action.toJson() for action in self.model.actions]
        j["observables"] = [ ob.toJson() for ob in self.observables ]

        minimumDistance=max( [S.minimumDistance for S in self.model.actions ]  )

        j["movesTable"]=self.moves.toJson()

        j["randomInitialCondition"]= {
            "minimumDistance" :minimumDistance
        }

        j["seed"]=self.seed


        return j









