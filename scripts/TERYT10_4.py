#-------------------------------------------------------------------------------
# Name:		Decode TERYT
# Author:	Alicja Byzdra
# Institution:	UMGDY
# Created:	24-04-2017
#-------------------------------------------------------------------------------


import arcpy
import xml.etree.ElementTree

# coding: utf8

try:
    ######################### PARAMETRES #########################
    table=arcpy.GetParameterAsText(0)
    xmlFile=arcpy.GetParameterAsText(1)
    obrFile=arcpy.GetParameterAsText(2)
    TERYTfield=str(arcpy.GetParameterAsText(3))
    nameField=str(arcpy.GetParameterAsText(4))
    ######################### PARAMETRES #########################

    root = xml.etree.ElementTree.parse(xmlFile).getroot()

    wojDict={}
    powDict={}
    gmDict={}

    for row in root:
        for i in range(len(row.findall('row'))):
            if (row[i][1].text == None and row[i][2].text==None and row[i][3].text==None) or (row[i][1].text == "\n      " and row[i][2].text=="\n      " and row[i][3].text=="\n      "):
                wojDict[row[i][0].text]=row[i][4].text
            elif (row[i][2].text==None and row[i][3].text==None) or (row[i][2].text=="\n      " and row[i][3].text=="\n      "):
                powDict[row[i][0].text+row[i][1].text]=row[i][4].text
            else:
                gmDict[row[i][0].text+row[i][1].text+row[i][2].text+"_"+row[i][3].text]=row[i][4].text
    del root
    del row
    arcpy.AddMessage("Dictionary from xml file created.")


    obrDict={}
    with arcpy.da.SearchCursor(obrFile, [TERYTfield,nameField]) as cursor:
        for row in cursor:
            obrDict[row[0]] = row[1]
    del cursor
    del row

    arcpy.AddMessage("Dictionary from shp or feature class created.")

    arcpy.AddField_management(table, "woj", "TEXT")
    arcpy.AddField_management(table, "powiat", "TEXT")
    arcpy.AddField_management(table, "gmina", "TEXT")
    arcpy.AddField_management(table, "obreb", "TEXT")
    arcpy.AddField_management(table, "dzialka", "TEXT")

    arcpy.AddMessage("Fields added.")

    cb='''def wojTERYT(teryt,wojDict):
        value = wojDict.get(teryt[:2], "empty")
        if value == "empty":
            value = teryt[:2]
        return value'''
    expr="wojTERYT(!Idd!,"+str(wojDict)+")"
    arcpy.CalculateField_management(table,"woj",expr,"PYTHON_9.3",cb)
    del wojDict


    cb='''def powTERYT(teryt,powDict):
        value = powDict.get(teryt[:4], "empty")
        if value == "empty":
            value = teryt[:4]
        return value'''
    expr="powTERYT(!Idd!,"+str(powDict)+")"
    arcpy.CalculateField_management(table,"powiat",expr,"PYTHON_9.3",cb)
    del powDict


    cb='''def gmTERYT(teryt,gmDict):
        value = gmDict.get(teryt[:8], "empty")
        if value == "empty":
            value = teryt[:8]
        return value'''
    expr="gmTERYT(!Idd!,"+str(gmDict)+")"
    arcpy.CalculateField_management(table,"gmina",expr,"PYTHON_9.3",cb)
    del gmDict


    cb='''def obrTERYT(teryt,obrDict):
        value = obrDict.get(teryt[:13], "empty")
        if value == "empty":
            value = teryt[9:13]
	else:
            value = value.upper()           
        return value'''
    expr="obrTERYT(!Idd!,"+str(obrDict)+")"
    arcpy.CalculateField_management(table,"obreb",expr,"PYTHON_9.3",cb)
    del obrDict


    cb='''def dzTERYT(teryt):
        terytSplit = teryt.split('.')
        return terytSplit[-1]'''
    expr="dzTERYT(!Idd!)"
    arcpy.CalculateField_management(table,"dzialka",expr,"PYTHON_9.3",cb)

    arcpy.AddMessage("Fields calculated")

except:
    arcpy.AddError("Error occurred")
    arcpy.AddMessage(arcpy.GetMessages())


