#!/usr/bin/python
from pyzabbix import ZabbixAPI
import sys
import argparse
import json
from pprint import pprint

def Ayuda():
    parser = argparse.ArgumentParser(description='Recupera todas las Actions y sus condiciones. Ejemplo: ./action_cond.py -COND -U usuario -P password')
    parser.add_argument('-COND', '--cond', type=str, metavar='', help='Si queremos traer las condiciones')
    parser.add_argument('-U', '--user', type=str, metavar='', required=True, help='Usuario para la conexion')
    parser.add_argument('-P', '--passwd', type=str, metavar='', required=True, help='Password para la conexion')
    args = parser.parse_args()
    return args

def Conex(URL, USR, PASSWD): #Nos conectamos
    zapi = ZabbixAPI(URL)
    zapi.login(USR,PASSWD)
    return zapi

def GetActions(zapi,actionsCond): # Traemos Actions
    dataActions = zapi.action.get(
                  selectFilter='extend',
                  selectOperations='extend',
                  output=['actionid','name'],
                  filter={'eventsource':'0'} # Solo las Actions en base a Triggers. Podemos indicar {'eventsource':['0','1']} o {'actionid':'11'}
                  )
    return dataActions

def GrabFilter(dataActions): # Nos quedamos con el Filtro que especificamos en el llamado (en este caso las Conditions)
    dataFilter = []
    dataList = []
    for action in range(0,len(dataActions)): # Recorremos las actions para quedarnos con lo que nos interesa (actionid, name, filter)
        dataFilter = [] # Se reinicia para guardar los valores que queremos para cada Action
        dataFilter.append(dataActions[action]['actionid'])
        dataFilter.append(dataActions[action]['name'])
        dataFilter.append(dataActions[action]['filter'])
        dataList.append(dataFilter) # Lo guardamos en una lista
    return dataList

def TranslateFilter(dataList): # Creamos dataList, una lista para hacerlo iterable y la recorremos
    #pprint(dataList)
    listPrint = []
    #listPrint = ""
    for elem in range(0, len(dataList)):
        #pprint(dataList[elem][2]['conditions']['conditiontype'])
        #listPrint = []
        #stringAction = (dataList[elem][0] + ";" + dataList[elem][1]) # ID y Nombre del Action
        stringAction = (dataList[elem][1])
        listPrint.append(stringAction)
        for condition in dataList[elem][2]['conditions']: # Concatenamos las Conditions
            #pprint(condition[u'conditiontype'])
            for prop in condition:
                if prop == 'conditiontype':
                    #pprint(condition[u'conditiontype'])
                    if condition[prop] == '0':
                        condition[prop] = 'Hostgroup'
                        #listPrint["prop"]
                        listPrint.append(" " + stringCondType)
                    elif condition[prop] == '1':
                        stringCondType = 'Host'
                        listPrint.append(" " + stringCondType)
                    elif condition[prop] == '2':
                        stringCondType = 'Trigger'
                        listPrint.append(" " + stringCondType)
                    elif condition[prop] == '3':
                        stringCondType = 'Trigger Name'
                        listPrint.append(" " + stringCondType)
                    elif condition[prop] == '4':
                        stringCondType = 'Trigger Severity'
                        listPrint.append(" " + stringCondType)
                    elif condition[prop] == '6':
                        stringCondType = 'Time Period'
                        listPrint.append(" " + stringCondType)
                    elif condition[prop] == '13':
                        stringCondType = 'Host Template'
                        listPrint.append(" " + stringCondType)
                    elif condition[prop] == '16':
                        stringCondType = 'Problem is supressed'
                        listPrint.append(" " + stringCondType)
                    elif condition[prop] == '25':
                        stringCondType = 'Event Tag'
                        listPrint.append(" " + stringCondType)
                    elif condition[prop] == '1':
                        stringCondType = 'Event Tag Value'
                        listPrint.append(" " + stringCondType)          
                elif prop == 'operator':
                    if condition[prop] == '0':
                        stringOperation = 'Equals'
                        listPrint.append(" " + stringOperation)
                    elif condition[prop] == '1':
                        stringOperation = 'Does not equal'
                        listPrint.append(" " + stringOperation)
                    elif condition[prop] == '2':
                        stringOperation = 'Contains'
                        listPrint.append(" " + stringOperation)
                    elif condition[prop] == '3':
                        stringOperation = 'Does not contain'
                        listPrint.append(" " + stringOperation)
                    elif condition[prop] == '4':
                        stringOperation = 'in'
                        listPrint.append(" " + stringOperation)
                    elif condition[prop] == '5':
                        stringOperation = 'Is greater than or equals'
                        listPrint.append(" " + stringOperation)
                    elif condition[prop] == '6':
                        stringOperation = 'Is less than or equals'
                        listPrint.append(" " + stringOperation)
                    elif condition[prop] == '7':
                        stringOperation = 'not in'
                        listPrint.append(" " + stringOperation)
                    elif condition[prop] == '8':
                        stringOperation = 'Matches'
                        listPrint.append(" " + stringOperation)
                    elif condition[prop] == '9':
                        stringOperation = 'Does not match'
                        listPrint.append(" " + stringOperation)
                    elif condition[prop] == '10':
                        stringOperation = 'Yes'
                        listPrint.append(" " + stringOperation)
                    elif condition[prop] == '11':
                        stringOperation = 'No'
                        listPrint.append(" " + stringOperation)
                else:
                    stringCondType = ""
                    stringOperation = ""
    print(listPrint)
        


def PrintData(dataHosts,dataInterfaces,dataInterfacesNew,SEP): #Imprimimos 'host', 'hostid', 'ip' y 'dns' para ver como quedaron los cambios
    print('\nResumen de las modificaciones:')
    header = '\nHostname' + SEP + 'HostID' + SEP + 'IP Anterior' + SEP + 'IP Nueva' + SEP + 'DNS Anterior' + SEP + 'DNS Nuevo'
    print(header)
    for h in range (0,len(dataHosts)):
        hostid = dataHosts[h]['hostid']
        for i in range (0,len(dataInterfaces)):
            linea = dataHosts[h]['host'] + SEP + dataInterfaces[i]['hostid'] + SEP + dataInterfaces[i]['ip'] + SEP + dataInterfacesNew[i]['ip'] + SEP + dataInterfaces[i]['dns'] + SEP + dataInterfacesNew[i]['dns']
            if dataInterfaces[i]['hostid'] == hostid:
                print(linea)
                
if __name__ == "__main__":
    # AYUDA Y ARGUMENTOS
    args = Ayuda()
    # CONEXIONES
    URLConn = "http://67.207.86.91/"
    USRConn = args.user
    PASSWDConn = args.passwd
    # FORMATO
    SEP = ";"
    VALSEP = ","
    # ARGUMENTOS DADOS
    actionsCond = args.cond
    # MAIN
    Conn = Conex(URLConn,USRConn,PASSWDConn)
    dataActions = GetActions(Conn,actionsCond)
    dataList = GrabFilter(dataActions)
    dataTranslated = TranslateFilter(dataList)
    #PrintData(dataHosts,dataInterfaces,dataInterfacesNew,SEP)