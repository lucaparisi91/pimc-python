from . import simulation
from . import action
from . import observable
from . import moves
from .theory import free
import argparse
import pandas as pd
import numpy as np
from . import inputFileTools
import os


def createSim( a, boxSize, N, T, C , nBeads):

    ensamble=simulation.canonicalEnsamble(N=[N],boxSize=boxSize,T=T)
    run=simulation.run(nBlocks=10000,stepsPerBlock=1000,correlationSteps=N)
    run.saveConfigurations=False

    actions=[action.caoBerneAction(a=a,groups=[0,0] )]

    observables=[observable.thermodynamicEnergy(label="energy") , observable.virialEnergy(label="eV") ]

    model=simulation.model( ensamble=ensamble,actions=actions,nBeads=nBeads)

    tab= moves.createTableCanonical(C=[C],l=int(0.6*nBeads),lShort=int(0.3*nBeads),groups=[0],delta=0.3*boxSize[0])
    
    sim=simulation.simulation(model=model,run=run,observables=observables,moves=tab)

    return(sim)



def generateInputFiles(data):
    js=[]
    for i,row in data.iterrows():
        
        N=int(row["N"])
        T=float(row["T"])
        na3=float(row["na3"])
        C=float(row["CA"])
        nBeads=int(row["nBeads"])


        landaC=np.sqrt(2*np.pi)
        L=( (N) * landaC**3/free.G(3/2,1) )**(1/3)
        n=N/L**3
        a=(na3/n)**(1/3)

        sim=createSim(a=a,N=N,T=T,boxSize=[L,L,L] ,C=C,nBeads=nBeads)
        js.append(sim.toJson())
    return(js)


def generateLabels(data):
    labels=[]
    for i,row in data.iterrows():
        values=[ value for value in row.values ]

        formatStrings=["{}{{}}".format( key) for key in row.keys() ]   
        formatString="_".join(formatStrings)
        #return values
        labels.append(formatString.format(*values) )
    return (labels)



if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Generate list of json files')
    parser.add_argument('parameters_file', type=str )

    parser.add_argument('--folder', type=str , default="." )

    args = parser.parse_args()
        
    parameters=args.parameters_file

    data=pd.read_csv(parameters,delim_whitespace=True)

    print(data)


    js=generateInputFiles(data)

    labels=generateLabels(data)
    
    settings=[ {"folder" : os.path.join(args.folder,label) , "jSon" : [ ["input.json", j  ] ] } for label,j in zip(labels,js) ]
    folders=[ os.path.abspath(setting["folder"]) for setting in settings  ]
    data["folder"]=folders
    inputFileTools.createSimFolders(settings)
    data.to_csv("folders-{}.dat".format(args.folder),sep="\t")




