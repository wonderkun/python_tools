#!/bin/python
###############################################
# File Name : ClassBuilder.py
#    Author : rootkiter
#    E-mail : rootkiter@rootkiter.com
#   Created : 02/10 10:30:41 2017
###############################################

TYPE_U16 = 'u16'
TYPE_U32 = 'u32'
TYPE_STR = 'str'
TYPE_LIST= 'list'
TYPE_DICT= 'dict'

def _mClass_Metaclass__Xprint(data):
    string = "[ Xprint ] "+str(data)
    print string

def Xprint(data):
    _mClass_Metaclass__Xprint(data)

class ClassBuilder_Metaclass(type):
    def __new__(cls,name,bases,classdict):
        i=0
        def set_Method(self,attr,value_type,value):
            if(value_type == type(value)):
                return setattr(self,attr,value)
            else:
                selfstr="type(self."+attr+")="+str(type(1))
                valuestr="type(value)="+str(value_type)
                __Xprint("{"+selfstr+"} != {"+valuestr+"}")
                return None
        def get_Method(self,attr):
            return getattr(self,attr)

        def append_Method(self,attr,value):
            if(hasattr(self,attr)):
                buf=getattr(self,attr)
            else:
                buf=[]
            buf.append(value)
            return setattr(self,attr,buf)

        def at_Method(self,attr,item_id):
            if(hasattr(self,attr)):
                buf=getattr(self,attr)
            else:
                buf=[]
            if(item_id < len(buf)):
                return buf[item_id]
            return None

        def remove_Method(self,attr,value):
            if(hasattr(self,attr)):
                buf=getattr(self,attr)
                for item_id in range(0,len(buf)):
                    if(buf[item_id] == value):
                        del buf[item_id]
                        setattr(self,attr,buf)
                        return True
            return False

        def addkey_Method(self,attr,key,value):
            if(hasattr(self,attr)):
                buf=getattr(self,attr)
            else:
                buf={}
            buf[key]=value
            return setattr(self,attr,buf)

        def haskey_Method(self,attr,key):
            if(hasattr(self,attr)):
                buf=getattr(self,attr)
                if(key in buf):
                    return True
            return False

        def getkey_Method(self,attr,key):
            if(hasattr(self,attr)):
                buf=getattr(self,attr)
                if(key in buf):
                    return buf[key]
            return None
        
        for attr,v in classdict.get('_fields',()):
            if( v == TYPE_U16  or v == TYPE_U32):
                def set_int_Method(self,value=0,attr=attr):
                    return set_Method(self,attr,type(1),value)
                def get_int_Method(self,attr=attr):
                    return get_Method(self,attr)
                classdict['set_'+attr]=set_int_Method
                classdict['get_'+attr]=get_int_Method
                classdict[attr] = 0
            elif( v == TYPE_STR ):
                def set_str_Method(self,value="",attr=attr):
                    return set_Method(self,attr,type("1"),value)
                def get_str_Method(self,attr=attr):
                    return get_Method(self,attr)
                classdict['set_'+attr]=set_str_Method
                classdict['get_'+attr]=get_str_Method
                classdict[attr]       =""
            elif( v == TYPE_LIST ):
                def append_list_Method(self,value,attr=attr):
                    return append_Method(self,attr,value)
                def at_list_Method(self,item_id,attr=attr):
                    return at_Method(self,attr,item_id)
                def remove_list_Method(self,item_value,attr=attr):
                    return remove_Method(self,attr,item_value)
                classdict['append_'+attr]=append_list_Method
                classdict['at_'+attr]=at_list_Method
                classdict['remove_'+attr]=remove_list_Method
                classdict[attr]       =[]
            elif( v == TYPE_DICT ):
                def haskey_dict_Method(self,key,attr=attr):  
                    return haskey_Method(self,attr,key)
                def getkey_dict_Method(self,key,attr=attr):
                    return getkey_Method(self,attr,key)
                def addkey_dict_Method(self,key,value,attr=attr):
                    return addkey_Method(self,attr,key,value)
                classdict['haskey_'+attr]=haskey_dict_Method
                classdict['getkey_'+attr]=getkey_dict_Method
                classdict['addkey_'+attr]=addkey_dict_Method
                classdict[attr]       ={}
            i=i+1
        return type.__new__(cls,name,bases,classdict)

class ClassBuilder:
    __metaclass__=ClassBuilder_Metaclass
    _fields = []
    def __init__(self,*args,**kargs):
        if(args and len(args)>0):
            margs={}
            for i in range(0,len(args)):
                if(i < len(self._fields)):
                    margs[self._fields[i][0]]=args[i]
            self.__dict__.update(margs)
        if(kargs and len(kargs)>0):
            self.__dict__.update(kargs)

    def buildJSON(self):
        import json
        res = {}
        i=0
        for attr,v in self._fields:
            itembuf={}
            itembuf['name']=attr
            itembuf['type']=v
            itembuf['value']=getattr(self,attr)
            res[str(i)]=json.dumps(itembuf)
            i=i+1
        return json.dumps(res)

    def loadJSON(self,json_data):
        import json
        jsdict=json.loads(json_data)
        for i in range(0,len(jsdict)):
            itembuf=json.loads(jsdict[str(i)])
            iname=str(itembuf['name'])
            itype=str(itembuf['type'])
            ival =itembuf['value']
            field = (iname,itype)
            if(field not in self._fields):
                Xprint( "parse Error");
            if(itype==TYPE_STR):
                setattr(self,str(itembuf['name']),str(itembuf['value']))
            elif(itype==TYPE_U16 or itype==TYPE_U32):
                setattr(self,str(itembuf['name']),itembuf['value'])
            elif(itype==TYPE_LIST):
                setattr(self,str(itembuf['name']),itembuf['value'])
            elif(itype==TYPE_DICT):
                setattr(self,str(itembuf['name']),itembuf['value'])
            else:
                Xprint("Not support Now !");

    def __str__(self):
        res = ""
        for name,v in self._fields:
            res += "%5s %-20s %s\n" % (v,name,str(getattr(self,name)))
        return res

class mClassTest(ClassBuilder):
    _fields = [
        ('ident' ,'u16'),
        ('type'  ,'u32'),
        ('string',"str"),
        ('mlist' ,"list"),
        ('mdict' ,"dict"),
    ]


if __name__ == "__main__":
    tt = mClassTest(20,30,'bbb',string=30,bb='bb')
    tt.set_ident(20)
    tt.set_string("Hello")
    tt.append_mlist("hello")

    helptest={1:"20",2:{11:20}}
    tt.append_mlist(helptest)

    tt.addkey_mdict("key","value")

    jsondata= tt.buildJSON()
    
    t2=mClassTest()
    t2.loadJSON(jsondata)
    print jsondata
    print t2.buildJSON()
    print tt
    print str(t2)
