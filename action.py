




class twoBodyPrimitiveAction:

    def __init__( self, potential, groups ):

        self.potential=potential
        self.groups=groups
    

    def toJson(self):

        return {
            "kind": "twoBody",
            "groupA": self.groups[0],
            "groupB": self.groups[1],
            "potential": self.potential.toJson()
        }


class oneBodyAction:

    def __init__( self, potential, group ):

        self.potential=potential
        self.group=group

    def toJson(self):
        return {
            "kind": "oneBody",
            "group": self.group,
            "potential": self.potential.toJson()
        }



class actions:
    def __init__(self,S=[]):
        self._actions=S

    def append(self,S):
        self._actions.append(S)
    
    def toJson(self):
        return [   S.toJson()  for S in self._actions ]


class caoBerneAction:
    def __init__(self,a,groups,cutOff=None,mesh=False):
        self.a=a
        self.groups=groups
        self.cutOff=cutOff
        self.mesh=mesh

    def toJson( self):
        G={
                "a": self.a,
                "kind": "caoBerne"
            }
        
        if self.cutOff is not None:
            G["kind"]="caoBerneTruncated"
            G["cutOff"]=self.cutOff
        

        if self.mesh:
            kind="twoBodyMesh"
        else:
            kind="twoBody"

        return {
            "kind": kind,
            "groupA": self.groups[0],
            "groupB": self.groups[1],
            "minimumDistance" : self.a,
            "greenFunction": G
        }
    




