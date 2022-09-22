#!/usr/bin/python
from pyzabbix import ZabbixAPI
import sys
import argparse
import json
from pprint import pprint

def Ayuda():
    parser = argparse.ArgumentParser(description='Recupera todas las Actions, condiciones y operaciones. Ejemplo: ./action_cond.py -COND -U usuario -P password')
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
                  selectFilter=['conditions','evaltype','eval_formula','formulaid','esc_period'],
                  selectOperations=['opmessage_usr','operationtype','esc_period','esc_step_from','esc_step_to'],
                  #output=['actionid','name'],
                  filter={'eventsource':'0','status':'0'} # Solo las Actions en base a Triggers y Enabled. Podemos indicar {'eventsource':['0','1']} o {'actionid':'11'}
                  )
    #print(dataActions)
    return dataActions

def GrabFilter(dataActions): # Nos quedamos con el Filtro que especificamos en el llamado (en este caso las Conditions)
    dataFilter = []
    dataConds = []
    for action in range(0,len(dataActions)): # Recorremos las actions para quedarnos con lo que nos interesa (actionid, name, filter)
        dataFilter = [] # Se reinicia para guardar los valores que queremos para cada Action
        dataFilter.append(dataActions[action]['actionid'])
        dataFilter.append(dataActions[action]['name'])
        dataFilter.append(dataActions[action]['filter'])
        dataFilter.append(dataActions[action]['esc_period']) # Default Time operation del Action
        dataFilter.append(dataActions[action]['operations'])
        dataConds.append(dataFilter) # Lo guardamos en una lista
    #print(dataActions[action]['operations'])
    #print(dataConds)
    return dataConds

def GrabArrays(dataConds):
    listHostgroups = []
    listHosts = []
    listTriggers = []
    listTemplates = []

    for elem in range(0, len(dataConds)):
        if dataConds[elem][2]['conditions']:
            for condition in dataConds[elem][2]['conditions']:
                if condition['conditiontype'] == "0":     
                    listHostgroups.append(condition['value'])
                if condition['conditiontype'] == "1":
                    listHosts.append(condition['value'])
                if condition['conditiontype'] == "2":
                    listTriggers.append(condition['value'])
                if condition['conditiontype'] == "13":
                    listTemplates.append(condition['value'])
    return listHostgroups, listHosts, listTriggers, listTemplates

def GetHostgroups(zapi,listHostgroups): # Traemos Actions
    dataHostgroups = zapi.hostgroup.get(
                  groupids=listHostgroups,
                  output=['groupid','name'],
                  )
    return dataHostgroups

def GetHosts(zapi,listHosts): # Traemos Actions
    dataHosts = zapi.host.get(
                  hostids=listHosts,
                  output=['hostid','name'],
                  )
    return dataHosts

def GetTriggers(zapi,listTriggers): # Traemos Actions
    dataTriggers = zapi.trigger.get(
                  triggerids=listTriggers,
                  output=['triggerid','description'],
                  )
    return dataTriggers

def GetTemplates(zapi,listTemplates): # Traemos Actions
    dataTemplates = zapi.template.get(
                  templateids=listTemplates,
                  output=['templateid','name'],
                  )
    return dataTemplates

def TranslateData(dataConds,dataHostgroups,dataHosts,dataTriggers,dataTemplates,SEP): # Creamos dataConds, una lista para hacerlo iterable y la recorremos
    actionPropCondType = {
            "0" : "Hostgroup",
            "1" : "Host",
            "2" : "Trigger",
            "3" : "Trigger name",
            "4" : "Trigger severity" ,
            "6" : "Time period",
            "13" : "Host template",
            "16" : "Problem supressed",
            "25" : "Event tag",
            "26" : "Event tag value"
        }

    actionPropOperator = {
        "0" : "equals",
        "1" : "does not equal",
        "2" : "contains",
        "3" : "does not contain",
        "4" : "in",
        "5" : "is greater than or equals",
        "6" : "is less than or equals",
        "7" : "not in",
        "8" : "matches",
        "9" : "does not match",
        "10" : "Yes",
        "11" : "No"
    }
    
    triggerSeverity = {
        "0" : "Not classified",
        "1" : "Information",
        "2" : "Warning",
        "3" : "Average",
        "4" : "High",
        "5" : "Disaster"
    }

    columns = "Action Name" + SEP + "Evaluation" + SEP + "ID" + SEP + "Condition" + SEP + "OperatorValue" + SEP + "Valor" + SEP + "Valor2"
    print(columns)

    #for elem in range(0, len(dataConds)):
        #print(dataConds[elem])
        #print(dataConds[elem][2]['evaltype'])
        #print(dataConds[elem][2]['eval_formula'])
        #for condition in dataConds[elem][2]['conditions']:
            #print(condition['formulaid'])

    for elem in range(0, len(dataConds)):
        line = ""
        actionName = (dataConds[elem][1])
        actionTime = (dataConds[elem][3])
        # Ejemplo: pprint(dataConds[elem][2]['conditions']['conditiontype'])
        # actionName = (dataConds[elem][0] y dataConds[elem][1]) son ID y Nombre del Action respectivamente

        #if dataConds[elem][4]:
        #    print(dataConds[elem][4])
        #    for operationdata in dataConds[elem][4]:
                #print(operationdata['esc_period']) # Time del Step
        #        print(operationdata)
        #        operation.foreach(print(operation))
                #print(operationdata['opmessage_usr'])
       # aux = dataConds[elem][4]
       # for item in range(0, len(aux)):
       #     print(aux[item]['opmessage_usr'])

       # if dataConds[elem][4]:
       #     aux = dataConds[elem][4]
            #for operationdata in aux:
                    #print(aux)

        if dataConds[elem][2]['conditions']:
            for condition in dataConds[elem][2]['conditions']:
                line = actionName
                line += SEP + dataConds[elem][2]['eval_formula'] + SEP
                if dataConds[elem][4]:
                    for operationdata in dataConds[elem][4]:
                        if operationdata['esc_step_to'] == "0":
                            line += operationdata['esc_step_from']
                            line += "-" + "0" # Infinito
                            line += " (Mensaje a usuario bla bla) "
                        else:
                            line += operationdata['esc_step_from']
                            line += "-" + operationdata['esc_step_to']
                            line += " (Mensaje a usuario bla bla) "
                    for operationdata in dataConds[elem][4]:
                        if operationdata['esc_period'] == "0":
                            line += SEP + actionTime
                        else:
                            line += SEP + operationdata['esc_period']
                #line += SEP + dataConds[elem][0]
                # Ejemplo: print(condition['operator'])
                if condition['formulaid']:
                    line += SEP + condition['formulaid']
                if condition['conditiontype'] in actionPropCondType.keys():
                    if condition['conditiontype'] == "0":
                        for hostgroup in dataHostgroups:
                            if condition['value'] == hostgroup['groupid']:
                                condition['value'] = hostgroup['name']
                    elif condition['conditiontype'] == "1":
                        for host in dataHosts:
                            if condition['value'] == host['hostid']:
                                condition['value'] = host['name']
                    elif condition['conditiontype'] == "2":
                        for trigger in dataTriggers:
                            if condition['value'] == trigger['triggerid']:
                                condition['value'] = trigger['description']
                    elif condition['conditiontype'] == "13":
                        for template in dataTemplates:
                            if condition['value'] == template['templateid']:
                                condition['value'] = template['name']
                    elif condition['conditiontype'] == "4":
                        if condition['operator'] in triggerSeverity.keys():
                            condition['value'] = triggerSeverity[condition['value']]
                    elif condition['conditiontype'] == "26":
                        condition['value'] = "Tag Value: " + condition['value']
                        condition['value2'] = "Tag Name: " + condition['value2']
                    condition['conditiontype'] = actionPropCondType[condition['conditiontype']]
                line += SEP + condition['conditiontype']
                if condition['operator'] in actionPropOperator.keys():
                    condition['operator'] = actionPropOperator[condition['operator']]
                    line += SEP + condition['operator']
                if condition['value']:
                    line += SEP + condition['value']
                if condition['value2']: # Normalmente no se utiliza
                    line += SEP + condition['value2']
                print(line.encode('utf-8'))
        else:
            line = actionName
            line += SEP + "No existen condiciones para este Action"
            print(line.encode('utf-8'))

if __name__ == "__main__":
    # AYUDA Y ARGUMENTOS
    args = Ayuda()
    # CONEXIONES
    URLConn = "http://67.207.86.91/"
    #URLConn = "http://10.231.13.68/"
    USRConn = args.user
    PASSWDConn = args.passwd
    # FORMATO
    SEP = "|"
    # ARGUMENTOS DADOS
    actionsCond = args.cond
    # MAIN
    Conn = Conex(URLConn,USRConn,PASSWDConn)
    dataActions = GetActions(Conn,actionsCond)
    dataConds = GrabFilter(dataActions)
    dataArrays = GrabArrays(dataConds)
    dataHostgroups = GetHostgroups(Conn,dataArrays[0])
    dataHosts = GetHosts(Conn,dataArrays[1])
    dataTriggers = GetTriggers(Conn,dataArrays[2])
    dataTemplates = GetTemplates(Conn,dataArrays[3])
    TranslateData(dataConds,dataHostgroups,dataHosts,dataTriggers,dataTemplates,SEP)