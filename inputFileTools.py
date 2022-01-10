from functools import reduce
import re
import pandas as pd
import numpy as np
import re
import copy
import json
import itertools
import os


closedSectorMoves=["levy","translate"]
openSectorMoves=["advance","recede","moveHead","moveTail","advanceHeadTail","recedeHeadTail"]
switchingMoves=["open/close","createWorm/deleteWorm","semiOpen/semiClose","createTwoWorms/deleteTwoWorms","fullOpen/fullClose"]

openSectorMoves=openSectorMoves + closedSectorMoves
closedSectorMoves+= switchingMoves
openSectorMoves+= switchingMoves


class pathMove:
    def __init__(self,name,l):
        self.l=l
        self.name=name
        
    def toJson(self):
        return {"kind" : self.name , "reconstructionMaxLength" : self.l }


class generalMove :
    def __init__(self, **kwds ):
        self._json={}
        for key,value in kwds.items():
            self._json[key]=value
        
    def toJson(self):
        return self._json
    


class semiOpenMove(generalMove):
    def __init__( self, setA, setB , CA, CB, l=1 ):
        super(semiOpenMove,self).__init__(setA=setA,setB=setB,kind="semiOpen",reconstructionMaxLength=l,CA=CA,CB=CB)

class semiCloseMove(generalMove):
    def __init__( self, setA, setB , CA, CB, l=1 ):
        super(semiOpenMove,self).__init__(setA=setA,setB=setB,kind="semiClose",reconstructionMaxLength=l,CA=CA,CB=CB)

class fullOpenMove(generalMove):
    def __init__( self, setA, setB , CA, CB, l=1 ):
        super(semiOpenMove,self).__init__(setA=setA,setB=setB,kind="fullOpen",reconstructionMaxLength=l,CA=CA,CB=CB)

class fullCloseMove(generalMove):
    def __init__( self, setA, setB , CA, CB, l=1 ):
        super(semiOpenMove,self).__init__(setA=setA,setB=setB,kind="fullClose",reconstructionMaxLength=l,CA=CA,CB=CB)
    
class createTwoWorms(generalMove):
    def __init__( self, setA, setB , CA, CB, l=1 ):
        super(semiOpenMove,self).__init__(setA=setA,setB=setB,kind="createTwoWorms",reconstructionMaxLength=l,CA=CA,CB=CB)

class deleteTwoWorms(generalMove):
    def __init__( self, setA, setB , CA, CB, l=1 ):
        super(semiOpenMove,self).__init__(setA=setA,setB=setB,kind="deleteTwoWorms",reconstructionMaxLength=l,CA=CA,CB=CB)




class translateMove(pathMove):
    def __init__(self,delta):
        super(translateMove,self).__init__("translate",None)
        self.delta=delta
    def toJson(self):
        return {"kind" : "translate" , "delta" : self.delta}

class openCloseMove(pathMove):
    def __init__(self,*args,**kwds):
        self.C=kwds["C"]
        del kwds["C"]
        super(openCloseMove,self).__init__(*args,**kwds)
        
    def toJson(self):
        return { **super(openCloseMove,self).toJson() , "C" : self.C }
    
    
class createDeleteWorm(openCloseMove):
    def __init__(self,*args,**kwds):
        self.alpha=kwds["alpha"]
        self.distribution=kwds["firstParticleDistribution"]
       
        
        del kwds["alpha"]
        del kwds["firstParticleDistribution"]
        
        super(createDeleteWorm,self).__init__(*args,**kwds)
        
    def toJson(self):
        return { **super(createDeleteWorm,self).toJson() , "alpha" : self.alpha, "firstParticleDistribution" : self.distribution }
    


    
def createMove(name,*args,**kwds):
    if name == "translate":
        return translateMove(*args,**kwds)
    else:
        
        if name in switchingMoves:
            if name == "createWorm/deleteWorm":
                return createDeleteWorm(name,*args,**kwds)
            else:
                return openCloseMove(name,*args,**kwds)
        else:
            return pathMove(name,*args,**kwds)



class tableMove:
    
    def __init__(self):
        self.moves=[]
        
    def addMove(self,name, sector, weight=1, group=0, *args , **kwds):
        #if name in [ move.name for move in self.moves ] :
        #    return False
        
        move=createMove(name,*args,**kwds)
        self.moves.append( {"move" : move ,"weight": weight , "sector" : sector , "set" : group } )
        
    def table(self):
        
        j=self.jsonInput()
        
        entries=[{** move["move"] , "weight" : move["weight"] , "sector":move["sectors"][0] , "set" : move["sets"][0]  }  for move in j ]
        return pd.concat([pd.DataFrame(entry,index=[0]) for entry in entries ]).reset_index(drop=True)

    
    def jsonInput(self):
        

        def getName(name,sector):
            m = re.match(r"(.*)/(.*)",name)
            if m is None:
                return name
            else:
                if sector == "closed":
                    return m[1]
                else:
                    return m[2]
        
        
        groups=list(set([move["set"] for move in self.moves]))

        moves=[]
        openSectorMoves=list(filter(lambda move: move["sector"] == "open",self.moves))
        closedSectorMoves=list(filter(lambda move: move["sector"] == "closed",self.moves))
        
        Wos=np.zeros( max(groups) + 1 )
        Wcs=np.zeros( max(groups) + 1 )


        for group in groups:
            
            groupMoves=list(filter(lambda move: move["set"]==group , self.moves))
            groupOpenCloseMoves=list(filter(lambda move: move["sector"] == "open/closed",groupMoves))
            groupOpenSectorMoves=list(filter(lambda move: move["sector"] == "open",groupMoves))
            groupClosedSectorMoves=list(filter(lambda move: move["sector"] == "closed",groupMoves))


            # determinne the total weights for each sector and open/close probability
            Wc=sum(map(lambda a : a["weight"],groupClosedSectorMoves))
            Wo=sum(map(lambda a : a["weight"],groupOpenSectorMoves))
            Woc=sum(map(lambda a : a["weight"],groupOpenCloseMoves))

        
        
            Wc+=Woc
            pOpen=Woc/Wc
            Wco=pOpen*Wo/(1-pOpen)
            Wo+=Wco

            Wos[group]=Wo
            Wcs[group]=Wc



            openSectorMoves=openSectorMoves + list(map(
                lambda move : {**move, 
                                "sector":"closed" } , groupOpenCloseMoves))
            
            closedSectorMoves=closedSectorMoves + list(map(
                lambda move : {**move, 
                            **{"sector":"open",
                                "weight" : move["weight"]*Wo/Wc
                                }
                            } , groupOpenCloseMoves))
            
                
                
        moves= moves +  [  move["move"].toJson() for move in openSectorMoves + closedSectorMoves ]


        def getWeight(sector,group):
            if sector=="open":
                return Wos[group]
            if sector=="closed":
                return Wcs[group]
            


        
        return  [ { "move" : {**moveDict,"kind" : getName(moveDict["kind"],move["sector"])} ,
                  "weight" : move["weight"] / getWeight(move["sector"],move["set"]) , "sectors" : [ move["sector"] ] ,
                   "sets" : [ move["set"] ]
                 } for moveDict,move in zip(moves,openSectorMoves + closedSectorMoves) ]
    

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


def createTable(C,l,lShort,ensamble="canonical",groups=[0],uniform=True):

    tab=tableMove()

    for group in groups:
        tab.addMove("levy","closed",l=l,weight=2,group=group)
        tab.addMove("translate","closed",delta=0.1,group=group)

        tab.addMove("levy","open",l=l,group=group)
        tab.addMove("moveTail","open",l=lShort,group=group)
        tab.addMove("moveHead","open",l=lShort,group=group)
        tab.addMove("swap","open",l=lShort,group=group)
        tab.addMove("open/close","open/closed",l=lShort,C=C,group=group)
        tab.addMove("translate","open",delta=0.1,group=group)

        if (ensamble == "grandCanonical"):
        
            tab.addMove("advanceHead","open",l=lShort,group=group)
            tab.addMove("recedeHead","open",l=lShort,group=group)

            if uniform:
                firstParticleDistribution="uniform"
            else:
                firstParticleDistribution="gaussian"
            
            tab.addMove("createWorm/deleteWorm","open/closed",l=lShort,C=C,alpha=1,group=group,firstParticleDistribution=firstParticleDistribution)

    
    return tab