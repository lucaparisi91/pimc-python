from functools import reduce
import re
import pandas as pd
import numpy as np
import re
import copy
import json
import itertools
import os
from pimc import moves



    


class tableMove:

    def __init__(self):
        self.moves=[]
    
    def addMove(self,move, sector, p, group=0, *args , **kwds):

        self.moves.append( {"move" : move ,"p": p , "sector" : sector , "set" :  group } )
    
    def table( self):

        rows= [ { **move, "move" : move["move"].name  } for move in self.moves ]

        
        return pd.DataFrame( rows )


        return data
    def closedSectorMoves(self,group):

        return [ move for move in self.moves if ( move["set"]==group and move["sector"]=="closed"  ) ]

    def openSectorMoves(self,group):

        return [ move for move in self.moves if ( move["set"]==group and move["sector"]=="open"  ) ]

    def totProbability(self,group,sector):

        data=self.table()

        data=data[ ( (data["sector"] == sector ) | (data["sector"]=="closed/open") ) & (data["set"]== group) ]

        return np.sum( data["p"])


    def __str__(self):

        return str(self.table() )
    
    def __repr__(self):
        return repr( self.table() )

    
    def toJson(self):

        j=[]

        for move in self.moves:
                jMoves=move["move"].toJson()
                n=len(jMoves)
                sectors=[move["sector"] for w in range(n) ]
                p=move["p"]/n
                if (move["sector"] == "closed/open"):
                    sectors[0]="closed"
                    sectors[1]="open"
                    p*=2

                for sector,jMove in zip(sectors,jMoves ):
                    j.append( { "move" : jMove , "weight" : p, "sectors" : [sector], "sets" : [ move["set"] ] } )
        
        return j

        

def getJson(j,queryString):
    
    if queryString=="":
        return j
    pattern="([a-zA-Z0-9]+)(?:\[(\d+)\])?(?:/(.+))?"
    m=re.match(pattern,queryString)
    print(m[3])
    if m is not None:
        key=m[1]
        index=m[2]
        
        remainder=m[3]
        result=j[key]
        
        if index is not None:
            result=result[int(index)]
        if remainder is not None:    
            return getJson(result,remainder)
        else:
            return result
def setJson(j,queryString,value):
    
    if queryString=="":
        return j
    pattern="([a-zA-Z0-9]+)(?:\[(\d+)\])?(?:/(.+))?"
    m=re.match(pattern,queryString)
    key=m[1]
    index=m[2]
    remainder=m[3]
    
    
    if m is not None:
        
        if remainder is None:
            
            if index is None:
                j[key]=value
            else:
                j[key][int(index)]=value
        else:
                result=j[key]
        
                if index is not None:
                    result=result[int(index)]
                setJson(result,remainder,value)



def expandJson(jTtemplate, **kwds):
    '''
    jTemplate : template json input file
    Takes in input a series of kwd , valude with value a vector and kwd the value to update
    TODO : mondodb queries 
    '''
    js=[]
    #alues=[ v.flatten() for v in np.meshgrid(*kwds.values()) ]
    for currentValues in itertools.product(*kwds.values() ):
        j=copy.deepcopy(jTemplate)
        for kwd,value in zip( kwds.keys(), currentValues):
            
            setJson(j,kwd,value)
        js.append(j)
    return js

def createInputFilesFromTemplate(template,params):
    keys=list(params.keys())
    N=len(params[keys[0]])
    js=[]
    
    for i in range(N):
        
        j=copy.deepcopy(template)
        for key in keys:
            value=params[key][i]
            setJson(j,str(key),value)
        js.append(j)
    return js

class numpyCompatibleEncoder(json.JSONEncoder):
    # Handles the default behavior of
    # the encoder when it parses an object 'obj'
    def default(self, obj):
        # If the object is a numpy array
        if isinstance(obj, np.ndarray):
            # Convert to Python List
            return obj.tolist()
        else:
            if isinstance(obj, np.int64) or sinstance(obj, np.int32):
                return int(obj)
            
            # Let the base class Encoder handle the object
            return json.JSONEncoder.default(self, obj)


        
def createSimFolders(settings):
    '''
    vector of json file of format
    "folder" : name of the folder to create
    "jSon" : vector of {name : content}
    '''
    
    for j in settings:
        folder=j["folder"]
        if not os.path.exists(folder):
            os.makedirs(folder)
        for jSonInput in j["jSon"]:
            filename=os.path.join( folder, jSonInput[0] )
            content=jSonInput[1]
            with open(filename,"w") as f:
                json.dump(content,f,indent=4,cls=numpyCompatibleEncoder)

def cartesianProduct(kwds):
    rows=[]
    for currentValues in itertools.product(*kwds.values() ):
          rows.append(np.array(currentValues)) 
    return pd.DataFrame(rows,columns=kwds.keys())
def setMoveParameters(j):
    for move in j["movesTable"]:
        if "reconstructionMaxLength" in move["move"].keys():
            
            move["move"]["reconstructionMaxLength"]=max( int(0.2 * int(j["nBeads"]) ) , 1 )
            
            
            if move["move"]["kind"]=="open" or move["move"]["kind"]=="close":
                move["move"]["C"]=1
                move["move"]["reconstructionMaxLength"]=1
            if move["move"]["kind"] != "levy":
                move["move"]["reconstructionMaxLength"]= max(1, move["move"]["reconstructionMaxLength"]//3) 
    return j



def createTableSemiCanonical( C,l,lShort,groups=None,uniform=True,delta=1, restriction=None ):
    if groups is None:
        groups=[0,1]
    
    tab=tableMove( )
    setA,setB=groups

    if not uniform:
        raise NotImplementedError("not uniform sampling of initial bead")
    CAB=C[2]
    for group in [setA,setB]:
        tab.addMove( moves.levy(l=l),p=0.8,sector="closed",group=group)
        tab.addMove( moves.translate(delta=delta),p=0.05,sector="closed",group=group)

        tab.addMove( moves.levy(l=lShort),p=0.1,sector="open",group=group)
        tab.addMove( moves.translate(delta=delta),p=0.05,sector="open",group=group)
        tab.addMove( moves.moveHead( l=lShort ),p=0.05,sector="open",group=group)
        tab.addMove( moves.moveTail( l=lShort ),p=0.05,sector="open",group=group)
        tab.addMove( moves.swap( l=l ),p=0.1,sector="open",group=group)
        tab.addMove( moves.advanceRecedeHeadTail( l=lShort, setA=group,setB=(group + 1)%2 ,restriction=restriction ) ,p=0.5,sector="open",group=group)

        tab.addMove( moves.semiOpenClose(l=lShort,setA=group,setB=(group + 1)%2,C=C[group]),p=0.05 ,sector="closed/open" , group=group),
        tab.addMove( moves.fullOpenClose(l=lShort,setA=group,setB=(group + 1)%2,C=CAB/C[(group + 1)%2] , restriction=restriction),p=0.05 ,sector="closed/open" , group=group),
        tab.addMove( moves.createDeleteTwoWorms(l=lShort,setA=group,setB=(group + 1)%2,C=[CAB,1] , restriction=restriction ),p=0.05 ,sector="closed/open" , group=group)

    return tab


def createTableCanonical(C,l,lShort,groups=None,uniform=True,delta=1):

    if groups is None:
        groups=[ 0 ]
    
    tab=tableMove( )
    
    for group in groups:
        tab.addMove( moves.levy(l=l),p=0.8,sector="closed",group=group)
        tab.addMove( moves.translate(delta=delta),p=0.05,sector="closed",group=group)
        tab.addMove( moves.levy(l=lShort),p=0.6 ,sector="open",group=group)
        tab.addMove( moves.translate(delta=delta),p=0.05,sector="open",group=group)
        tab.addMove( moves.moveHead( l=lShort ),p=0.05,sector="open",group=group)
        tab.addMove( moves.moveTail( l=lShort ),p=0.05,sector="open",group=group)
        tab.addMove( moves.swap( l=l ),p=0.1,sector="open",group=group)
        tab.addMove( moves.semiOpenClose(l=lShort,setA=group,setB=(group + 1)%2,C=C[group]),p=0.15 ,sector="closed/open" , group=group)

    return tab



def createTable(C,l,lShort,ensamble="canonical",groups=None,uniform=True,delta=1):

    if ensamble == "semiCanonical":
        return createTableSemiCanonical(C,l,lShort,groups=groups,uniform=uniform,delta=delta)

    tab=tableMove()

    for group in groups:
        tab.addMove("levy","closed",l=l,weight=2,group=group)
        tab.addMove("translate","closed",delta=delta,group=group)

        tab.addMove("levy","open",l=l,group=group)
        tab.addMove("moveTail","open",l=lShort,group=group)
        tab.addMove("moveHead","open",l=lShort,group=group)
        tab.addMove("swap","open",l=lShort,group=group)
        tab.addMove("open/close","closed/open",l=lShort,C=C,group=group)
        tab.addMove("translate","open",delta=delta,group=group)

        if (ensamble == "grandCanonical"):
        
            tab.addMove("advanceHead","open",l=lShort,group=group)
            tab.addMove("recedeHead","open",l=lShort,group=group)

            if uniform:
                firstParticleDistribution="uniform"
            else:
                firstParticleDistribution="gaussian"
            
            tab.addMove("createWorm/deleteWorm","closed/open",l=lShort,C=C,alpha=1,group=group,firstParticleDistribution=firstParticleDistribution)

    
    return tab