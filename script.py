import ConfigParser #Configuration files
import urllib #Page is up
import urllib2 #get source code
import sys
import ast
import json
import hashlib
from hashlib import md5
import urllib2
from configobj import ConfigObj
import io
################################################
FICHEIRO_CONFIG="config.ini"
FICHEIRO_DATA="teste.txt"
################################################

def is_up(link):
    return urllib.urlopen(link).getcode() == 200

def error_log(message):
    file = open("error.log", "rw+")
    line = file.write(message)
    file.close()

def ConfigSectionMap(Config,section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            error_log("#0000100001%s!" % option)
            dict1[option] = None
    return dict1

def get_sourcecode(link):
    response = urllib2.urlopen(link)
    m = hashlib.md5()
    m.update(response.read())
    return m.hexdigest()

def config_init(name):
    config = ConfigParser.ConfigParser()
    config.read(name)
    return config

def get_cadeiras(config):
    i=0
    for a in config.sections():
        if(a!="email"):
            i=i+1
        else:
            break
    return config.sections()[0:i]



def read_file_lines(file):
    with open(file) as f:
        lines = f.readlines()
    for i in range(0,len(lines)):
        json_acceptable_string = lines[i].replace("'", "\"")
        #print json_acceptable_string
        d = json.loads(json_acceptable_string)
        lines[i]=d
    return lines


def del_reverse_list_index(data,eliminar):
    for i in reversed(eliminar):
        del(data[i])

def atualizar_cadeira(data,config):
    if(is_up(data["link"])):
        md5=get_sourcecode(data["link"])
        if(md5 != data["md5"]):
            #alerta(data,config)
            print "ALERTA!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            altera_config(data,config)
            return True
        else:
            return False
    else:
        error_log("IS DOWN!! " % data["link"])

def altera_config(data,config):
    try:
        from configparser import ConfigParser
    except ImportError:
        from ConfigParser import ConfigParser
    config = ConfigParser()
    config.read(FICHEIRO_CONFIG)
    config.set(data["cadeira"], 'ativo', False)
    with open(FICHEIRO_CONFIG, 'w') as configfile:
        config.write(configfile)

def adicionar_cadeira(cadeira,config):
    new={}
    lista=[]
    new["cadeira"]=cadeira
    new["sigla"]=ConfigSectionMap(config,cadeira)['sigla']
    new["link"]=ConfigSectionMap(config,cadeira)['link']
    print ConfigSectionMap(config,cadeira)['ativo'],(ConfigSectionMap(config,cadeira)['ativo'])
    new["ativo"]=bool(ConfigSectionMap(config,cadeira)['ativo'])
    new["md5"]=get_sourcecode(ConfigSectionMap(config,cadeira)['link'])
    return json.loads(json.dumps(new))

def record_data(data):
    f = open(FICHEIRO_DATA,'w')
    for i in data: 
        i = json.dumps(i, ensure_ascii=False, encoding='utf8')
        f.write(unicode(i)+"\n")
    f.close()

def del_unexistent_json(data,cadeiras):
    eliminar=[]
    for a in range(0,len(data)):
        for b in range(0,len(cadeiras)):
            if cadeiras[b] == data[a]["cadeira"]:
                break
            elif (b+1)==len(cadeiras):
                eliminar.append(a)
    del_reverse_list_index(data,eliminar)

def del_False_ones(data):
    eliminar=[]
    for i in range(0,len(data)):
        if data[i]["ativo"]==False:
            eliminar=eliminar+[i]
    print eliminar
    del_reverse_list_index(data,eliminar)

def str2bool(s):
    return s.lower() in ["true","t","1"]

if __name__ == "__main__":
    config = config_init(FICHEIRO_CONFIG)
    cadeiras=get_cadeiras(config)
    data = read_file_lines(FICHEIRO_DATA)
    print data
    #eliminar jsons que ja nao existem na config WORKING TESTED
    del_unexistent_json(data,cadeiras)
    #Elimina Falses
    del_False_ones(data)
    print "lalas",data
    #print "fodasse"
    #-------------------------------------

    #-------------------------------------
    #"""
    #atualiza cadeiras e adiciona novas cadeiras WORKING - NOT FULL TESTED
    #print data
    novos=[]
    achas=[]
    pos=[]
    for b in range(0,len(cadeiras)):
        print "a:",bool(ConfigSectionMap(config,cadeiras[b])['ativo']),str2bool(ConfigSectionMap(config,cadeiras[b])['ativo'])
        if len(data)==0 and str2bool(ConfigSectionMap(config,cadeiras[b])['ativo'])==True:
            novos.append(adicionar_cadeira(cadeiras[b],config))
        for a in range(0,len(data)):
            print data[a]["ativo"],data[a]["cadeira"]

            if cadeiras[b] == data[a]["cadeira"] and data[a]["ativo"]==True:
                #print "asmdbasgduashdiuashdiusa"
                if str2bool(ConfigSectionMap(config,cadeiras[b])['ativo'])==True:
                    if atualizar_cadeira(data[a],config):
                        print "FODASSSSSSSS"
                        pos=pos+[a]
                        data[a]["ativo"]=False
                else:
                    pos=pos+[a]
                achas=achas+[data[a]["cadeira"]]

            if (a+1)==len(data) and cadeiras[b] not in achas and str2bool(ConfigSectionMap(config,cadeiras[b])['ativo'])==True:
                novos.append(adicionar_cadeira(cadeiras[b],config))
    print "pos",pos
    data=data+novos
    del_reverse_list_index(data,pos)
    for i in data:
        print i,"\n"
    record_data(data)
    #-------------------------------------
    #"""



