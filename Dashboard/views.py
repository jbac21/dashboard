from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import User, DfType, pIndicator, Data, Dashboard

import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import numpy as np


# Initialize forms and choice fields
class NewDfForm(forms.Form):
    code = forms.CharField(max_length=4, widget=forms.TextInput(attrs={'autocomplete':'off', 'placeholder' : 'Field Code', 'class' : "form-control"}))
    name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'autocomplete':'off', 'placeholder' : 'Name', 'class' : "form-control"}))

typeChoices = [(0,"€"),(1,"%")]
class NewPIndicatorForm(forms.Form):
    formula = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'autocomplete':'off', 'placeholder' : 'Formula (enter field codes in ?...?)', 'class' : "form-control", 'id': "formula"}))
    name = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'autocomplete':'off', 'placeholder' : 'Name', 'class' : "form-control"}))
    valueType = forms.ChoiceField(choices = typeChoices, widget = forms.Select(attrs={'class' : "form-control"}))

choicesMarket =[(0,"Select Market"),(1,"Germany"),(2,"France"),(3,"Italy"),(4,"United States"),(5,"Canada"),(6,"China"), (7,"Global")]
marketRegion = {
    "Germany" : "Europe",
    "France" : "Europe",
    "Italy" : "Europe",
    "United States" : "NorthAmerica",
    "Canada" : "NorthAmerica",
    "China" : "Asia"
}

choices = []
def initializeNewDataForm():
    
    global choices
    choices = []
    dfTypes = DfType.objects.all()
    choicesList = ["Select Data Field"]
    for entry in dfTypes:
        choicesList.append(str(entry.code) + " - " + str(entry.name))

    numeration = range(0, len(choicesList))
    choices = list(zip(numeration, choicesList))
    return choices

choicesCummulation = [(0,"YTD"),(1,"R12"),(2,"Month")]
years = range(datetime.now().year,2009,-1)
months  = ['January', 'Feburary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
indexYears = range(0,len(years))
indexMonths = range(0,len(months))
yearsTuples = zip(indexYears, years)
monthsTuples = zip(indexMonths, months)
choicesMarketTotal = []
choicesMarketTotal.append((0, "Global"))
for element in choicesMarket[1:]:
    choicesMarketTotal.append(element)

class DashboardForm(forms.Form):
    year = forms.ChoiceField(choices = yearsTuples, initial=[len(years)-1], widget = forms.Select(attrs={'class' : "form-control form-xselement"}))
    month = forms.ChoiceField(choices = monthsTuples, widget = forms.Select(attrs={'class' : "form-control form-xselement"}))
    cummulation = forms.ChoiceField(choices = choicesCummulation, widget = forms.Select(attrs={'class' : "form-control form-xselement"}))

DftypeChoice = ["Select ..."]
PindicatorChoice = ["Select ..."]
DftypeObjects = DfType()
PindicatorObjects = pIndicator()
pIndicatorList = zip()
dfTypeList = zip()

def initializeNewTileForm():
    
    global DftypeChoice
    global PindicatorChoice
    global DftypeObjects
    global PindicatorObjects
    global pIndicatorList
    global dfTypeList

    DftypeChoice = ["Select ..."]
    PindicatorChoice = ["Select ..."]
    DftypeObjects = DfType()
    PindicatorObjects = pIndicator()
    pIndicatorList = zip()
    dfTypeList = zip()
    
    DftypeObjects = DfType.objects.all()
    PindicatorObjects = pIndicator.objects.all()
    DftypeIndex = range(0,len(DftypeObjects)+1)
    PindicatorIndex = range(0,len(PindicatorObjects)+1)
    for element in DftypeObjects:
        DftypeChoice.append(element.name)
    for element in PindicatorObjects:
        PindicatorChoice.append(element.name)
    pIndicatorList = zip(PindicatorIndex,PindicatorChoice)
    dfTypeList = zip(DftypeIndex, DftypeChoice)
    return list(pIndicatorList), list(dfTypeList)

initializeNewTileForm()


# Function converting performance indicator formulas in lists of codes or names or a combination.
def dfDescription(input, mode="default"):
    # Create list of lists for kpis
    orgList = [] # List including original formulas
    if mode == "default" or mode == "fieldcodes":
        for formula in input:
                orgList.append(str(formula.formula))
    else:
        orgList.append(str(input))

    # Remove operators
    dfList = orgList # List for editing
    dfResult = [] # List with formulas + description
    operators = ['','+', '-', '*', '/', '(', ')', '[', ']']
    dfListSplit = []
    formulaList = []
    message=""

    for formula in dfList:
        dfListSplit.append(formula.split("?"))
    
    formulaList = dfListSplit

    # Add description
    j = 0 # Iterator for formulas

    for formula in dfListSplit:
        i = 0 # Iterator for entries in formulas
        k = len(formula) # Number of entries in formula
        if mode == "fieldcodes":
            interimResult = [] # If only fieldcodes are returned
        while i < k:
            if formula[i] in operators: 
                i += 1
            else:
                if len(DfType.objects.filter(code=formula[i])) == 0:
                    message = "Data Field " + str(formula[i]) + " does not exist!"
                    break
                else:
                    code = DfType.objects.filter(code=formula[i])[0].name
                    dfListSplit[j].insert(i+1, code)                   
                    message = "ok"
                    if mode == "fieldcodes":
                        interimResult.append(code)
                    i += 2 
                    k += 1 
        if mode == "fieldcodes":
            dfResult.append(interimResult)
        j += 1  

        # Concatenate strings
        if message == "ok" and mode != "fieldcodes":
            for formula in dfListSplit:
                string = ""
                for entry in formula:
                    string = string + str(entry) + " "
                dfResult.append(string)
        
    return message, dfResult, formulaList


# Function  for retrieving data
def retrieveData(criterias=[]):
    results = []
    for criteria in criterias:
        datafield = DfType.objects.get(name = criteria)
        queryObjects = Data.objects.filter(dfCode = datafield)
        queryData = []
        for element in queryObjects:
            queryData.append(element)
        results.append(queryData)
    return results


# Function for calculating kpi values
def calculate(criteriasList, kpi, cummulation, dfMarkets, piMarkets, marketsFilter, strdate):

    global choicesMarket
    criteriasOrg = []
    criterias = []
    for element in criteriasList: # For preparing returning values
        criteriasOrg.append(element)
        if element not in criterias:
            criterias.append(element)

    # Retrieve data
    # Add criteria for kpi
    indicatorList = []
    for k in kpi:
        indicator = pIndicator.objects.get(name=k)
        indicatorList.append(indicator)

    # Isolate datafields from formula
    indicatorCriteriaComplete = dfDescription(indicatorList, mode="fieldcodes")
    indicatorCriteria = indicatorCriteriaComplete[1]

    for kpi in indicatorCriteria:
        for element in kpi:
            if element not in criterias:
                criterias.append(element)

    # Retrieve dataset
    queryResults = retrieveData(criterias)
    
    # Prepare dataframe
    i = 0
    values = []
    dates = []
    markets = []
    nameList = []

    while i < len(criterias):
        # name =  DfType.objects.get(code = criterias[i])
        for entry in queryResults[i]:
            values.append(entry.value)
            dates.append(datetime.date(entry.timestamp))
            markets.append(choicesMarket[int(entry.country)][1])
            nameList.append(criterias[i])
        i += 1
    df = pd.DataFrame(list(zip(nameList, dates, markets, values)), columns =['Name','Date','Market','Value'])
    df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')

    # Set Filter for dataframe
    strdate = str(strdate) + "-1" # Default settings
    if cummulation == "Month":
        startDate = datetime.strptime(strdate, '%Y-%m-%d')
        endDate = startDate+relativedelta(months=+1)+relativedelta(days=-1)
    elif cummulation == "R12":
        startDate = datetime.strptime(strdate, '%Y-%m-%d')+relativedelta(months=-11)
        endDate = startDate+relativedelta(months=+12)+relativedelta(days=-1)
    else:
        date = datetime.strptime(strdate, '%Y-%m-%d')
        month = date.month - 1
        startDate = datetime.strptime(strdate, '%Y-%m-%d')+relativedelta(months=-month)
        deltaMonth = month + 1
        endDate = startDate+relativedelta(months=deltaMonth)+relativedelta(days=-1)

    # Calculate sums per market
    marketResults = [] #kpi results per market
    marketSums = [] # df sums per market
    for market in marketsFilter:  
        dfFiltered = pd.DataFrame()
        dfFiltered2 = pd.DataFrame()
        boolean_series = []
        # Filter dataframe
        if market != "Global":
            boolean_series = df.Market.isin([market])
            dfFiltered = df[boolean_series]
            dfFiltered2 = dfFiltered.loc[(dfFiltered['Date'] >= startDate) & (dfFiltered['Date'] <= endDate)]
        else:
            dfFiltered2 = df.loc[(df['Date'] >= startDate) & (df['Date'] <= endDate)]
        
        sums = []
        # criterias - all kpis unique
        # criteriasOrg - dfs on tiles in order

        for criteria in criterias:
            dfCriteria = dfFiltered2[dfFiltered2['Name'] == criteria]
            sums.append(dfCriteria['Value'].sum())
        marketSums.append(sums)

        # Calculate kpis
        # Create dictionaries with sums for each criteria
        dfValues = {}
        i = 0
        while i < len(criterias):
            dfValues[criterias[i]] = sums[i]
            i += 1

        marketResults.append(dfValues)

    # Create formula with values as string
    removeList = [' ']
    operatorList = ['+', '-', '*', '/', '(', ')', '[', ']']

    indicatorCriteria2 = indicatorCriteriaComplete[2] # kpi formulas
    calcList = []

    i = 0
    while i < len(indicatorCriteria2):
        kpiEdited = []
        for element in indicatorCriteria2[i]:
            if element in operatorList:
                kpiEdited.append(element)
            elif element in criterias:
                for position in marketsFilter:
                    if position == piMarkets[i]:
                        dataset = marketResults[marketsFilter.index(position)]
                        try: 
                            kpiEdited.append(dataset[element])
                        except:
                            kpiEdited.append(0)
        calcList.append(kpiEdited)
        i += 1
    
    # Calculate numerical kpi values
    calcResults = []
    for entry in calcList:
        calcFormula = ""
        for element in entry:
            calcFormula = calcFormula + str(element)
        try: calcResults.append(eval(calcFormula))
        except: calcResults.append(0)

    sumsOrg = [] 
    
    j = 0
    i = 0
    while i < len(criteriasOrg):
        while j < len(criterias):
            if criteriasOrg[i] == criterias[j]:
                break
            else:
                j += 1
        
        k = 0
        while k < len(marketsFilter):
            if dfMarkets[i] == marketsFilter[k]:
                marketIndex = k
                break
            else:
                k += 1

        sumsOrg.append(marketResults[marketIndex][criterias[j]])
        i += 1

    return sumsOrg, calcResults


# Dashboard webpage
def index(request):

    choicesTypes =[(0, "Data Fields"),(1, "Performance Indicator")]
    class NewTileForm(forms.Form):
        dfFormList = forms.ChoiceField(choices = initializeNewTileForm()[1], widget = forms.Select(attrs={'class' : "form-control"}))
        kpiFormList = forms.ChoiceField(choices = initializeNewTileForm()[0], widget = forms.Select(attrs={'class' : "form-control"}))
        market = forms.ChoiceField(choices = choicesMarket, widget = forms.Select(attrs={'class' : "form-control"}))
        typeChoice = forms.ChoiceField(choices = choicesTypes, widget = forms.Select(attrs={'id': 'formChoice', 'class' : "form-control"}))

    message = ""
    criteriasResults = ""
    kpiResults = ""
    title = []
    value = []
    form = DashboardForm()
    tileForm = NewTileForm()
    form.fields['month'].initial = [datetime.now().month]
    tileResultsAll = {}

    # Create new Tile on Dashboard
    if request.method == "POST":
        newTile = NewTileForm(request.POST)
        if newTile.is_valid():

            if int(newTile.cleaned_data["typeChoice"]) == 0:
                dataEntry = DftypeChoice[int(newTile.cleaned_data['dfFormList'])]
            else:
                dataEntry = PindicatorChoice[int(newTile.cleaned_data['kpiFormList'])]

            if dataEntry != "Select...":
                f = Dashboard(user = User.objects.get(id=request.user.id), 
                    index = 1, 
                    type=newTile.cleaned_data["typeChoice"], 
                    market=choicesMarket[int(newTile.cleaned_data["market"])][1],
                    data = dataEntry)
                f.save()
                newTile = NewTileForm()
                message="New Tile has been created."
            else:
                message = "Configure New Tile form not filled out correctly."

    if request.user.id:
        
        username = User.objects.get(id=request.user.id)
        tiles = Dashboard.objects.filter(user = username)
        
        # Set up default lists & values
        criterias = []
        kpi = []
        id = [] 
        cummulation = "YTD"
        marketsFilter=[]
        marketsOrder = []
        year = int(datetime.now().year)
        benchmarkYear = year - 1
        month = '1'
        strdate = str(year)+"-"+str(month)
        benchmark = str(benchmarkYear)+"-"+str(month)
        #strdate = datetime.now().strftime("%Y-%m")

        # Prepare markets filter
        for tile in tiles:
            marketsOrder.append(tile.market)
            if tile.market not in marketsFilter:
                marketsFilter.append(tile.market)

        # Get Filter settings
        form = DashboardForm(request.GET)
        if form.is_valid():
            cummulation = choicesCummulation[int(form.cleaned_data["cummulation"])][1]
            year = years[int(form.cleaned_data["year"])]
            benchmarkYear = year - 1
            month = int(form.cleaned_data["month"])+1
            strdate = str(year)+"-"+str(month)
            benchmark = str(benchmarkYear)+"-"+str(month)
        
        # List of markets for which tile data to be calculated
        dfMarkets = []
        piMarkets = []

        for tile in tiles:
            if tile.type == 0:
                criterias.append(tile.data)
                id.append("df")
                dfMarkets.append(tile.market)
            elif tile.type == 1:
                kpi.append(tile.data)
                id.append("kpi")
                piMarkets.append(tile.market)

        criteriasBenchmark = []
        for element in criterias:
            criteriasBenchmark.append(element)
        results = calculate(criteriasList=criterias, kpi=kpi, cummulation=cummulation, dfMarkets=dfMarkets, piMarkets=piMarkets, marketsFilter=marketsFilter, strdate=strdate)
        resultsBenchmark = calculate(criteriasList=criteriasBenchmark, kpi=kpi, cummulation=cummulation, dfMarkets=dfMarkets, piMarkets=piMarkets, marketsFilter=marketsFilter, strdate=benchmark)
        

        # Bring tile results into the correct order
        tileResults = []
        tileResultsBenchmark = []

        k = 0
        i = 0
        j = 0

        while k < len(id):
            if id[k] == "df":
                tileResults.append(results[0][j])
                tileResultsBenchmark.append(resultsBenchmark[0][j])
                j += 1
            else:
                tileResults.append(results[1][i])
                tileResultsBenchmark.append(resultsBenchmark[1][i])
                i += 1
            k += 1

        # Create dict for output
        i = 0
        tileResultsAll = []

        while i < len(tiles):
            tileResultsDict = {}
            if tiles[i].type == 1 and tileResults[i] <= 1:
                tileResultsDict['value'] = str(round(tileResults[i] * 100, 2)) + " %"
                tileResultsDict['valueStrip'] = round(tileResults[i] * 100, 2)
                tileResultsDict['benchmarkValue'] = str(round(tileResultsBenchmark[i] * 100, 2)) + " %"
                tileResultsDict['benchmarkValueStrip'] = round(tileResultsBenchmark[i] * 100, 2)
                delta = round((tileResults[i] - tileResultsBenchmark[i]) * 100, 2)
                if delta > 0:
                    tileResultsDict['delta'] = "+" + str(delta) + " %°"
                elif delta < 0:
                    tileResultsDict['delta'] = str(delta) + " %°"
                tileResultsDict['type'] = ["in %"]
            else:
                tileResultsDict['value'] = str(tileResults[i]) + " €"
                tileResultsDict['valueStrip'] = round(tileResults[i], 2)
                tileResultsDict['benchmarkValue'] = str(round(tileResultsBenchmark[i],2)) + " €"
                tileResultsDict['benchmarkValueStrip'] = round(tileResultsBenchmark[i],2)
                delta = round(tileResults[i] - tileResultsBenchmark[i], 2)
                if delta > 0:
                    tileResultsDict['delta'] = "+" + str(delta) + " €"
                elif delta < 0:
                    tileResultsDict['delta'] = str(delta) + " €"
                tileResultsDict['type'] = ["in €"]
            tileResultsDict['kpi'] = tiles[i].data
            if tiles[i].market == "global":
                tileResultsDict['market'] = "All"
            else:
                tileResultsDict['market'] = tiles[i].market
            tileResultsDict['id'] = tiles[i].id
            tileResultsDict['year'] = year
            tileResultsDict['benchmarkYear'] = benchmarkYear
            tileResultsDict['name'] = tiles[i].data
            tileResultsAll.append(tileResultsDict)
            i += 1

    return render(request, "dashboard/index.html", {
        'form' : form,
        'tiles' : tileResultsAll,
        'tileForm' : tileForm,
        'message' : message
    })


@login_required
def delete_tile(request):

    if request.method == "POST":
        id = request.POST['id']
        try: 
            tile = Dashboard.objects.get(id=id)
        except:
            tile = []
        if tile != []:
            tile.delete()

    return JsonResponse(data={
        'message' : 'Tile has been deleted.'
    })  


@login_required
def delete_data(request):

    if request.method == "POST":
        id = request.POST['id']
        try: 
            data = Data.objects.get(id=id)
        except:
            data = []
        if data != []:
            data.delete()

    return JsonResponse(data={
        'message' : 'Data entry has been deleted.'
    })  


@login_required
def delete_pIndicator(request):

    if request.method == "POST":
        id = request.POST['id']
        try: 
            data = pIndicator.objects.get(id=id)
        except:
            data = []
        if data != []:
            data.delete()

    return JsonResponse(data={
        'message' : 'Performance Indicator entry has been deleted.'
    })  


@login_required
def delete_df(request):

    if request.method == "POST":
        id = request.POST['id']
        try: 
            data = DfType.objects.get(id=id)
        except:
            data = []
        if data != []:
            data.delete()

    return JsonResponse(data={
        'message' : 'Data Field has been deleted.'
    })  


@login_required
def datafields(request):
    
    form = NewDfForm()
    datafields = DfType.objects.all()
    message = ""

    if request.method == "POST":
        form = NewDfForm(request.POST)

        if form.is_valid():
            f = DfType(code=form.cleaned_data["code"], name=form.cleaned_data["name"])
            f.save()
            message = "New code has been created!"
            form = NewDfForm()
        
    datafields = DfType.objects.all()

    return render(request, "dashboard/datafields.html", {
        'datafield': datafields,
        'message': message,
        'form': form
    })


# Data wegpage
def data(request):
    global choicesMarket    
    class NewDataForm(forms.Form):
        timestamp = forms.DateTimeField(widget=forms.SelectDateWidget(attrs={'class' : "form-control"}, years=range(2010, 2022)))
        dfCode = forms.ChoiceField(choices = initializeNewDataForm(), widget = forms.Select(attrs={'class' : "form-control"}))
        value = forms.DecimalField(widget=forms.TextInput(attrs={'placeholder' : 'Value in €', 'class' : "form-control"}))
        market = forms.ChoiceField(choices = choicesMarket, widget = forms.Select(attrs={'class' : "form-control"}))
    
    form = NewDataForm()

    # Add new data
    if request.method == "POST":
        form = NewDataForm(request.POST)
        if form.is_valid():
            timestamp = form.cleaned_data["timestamp"]
            dfIndex = form.cleaned_data["dfCode"]
            dfCode = choices[int(dfIndex)][1].split(" - ")[0]
            value = form.cleaned_data["value"]
            market = form.cleaned_data["market"]
            dfTypeInstance = DfType.objects.get(code=dfCode)

            f = Data(timestamp=timestamp, dfCode=dfTypeInstance, value=value, country=market)
            f.save()
            form = NewDataForm()
 
    # Create dictionary for entries in table
    i = 0
    data = Data.objects.all()
    dataList = []
    for entry in data:
        dataSet = {}
        dataSet['timestamp'] = str(entry.timestamp).split(" ")[0]
        dataSet['dfCode'] = entry.dfCode.code
        dataSet['value'] = entry.value
        dataSet['market'] = choicesMarket[int(entry.country)][1]
        dataSet['name'] = entry.dfCode.name
        dataSet['id'] = entry.id
        dataList.append(dataSet)
        i += 1

    # Render Page
    return render(request, "dashboard/data.html", {
        'dataList' : dataList,
        'form' : form
    })



# kpi webpage
def kpi(request):
    form = NewPIndicatorForm()
    message = ''

    # Create new kpi
    if request.method == "POST":
        form = NewPIndicatorForm(request.POST)

        if form.is_valid():

            formula = form.cleaned_data["formula"]

            # Get description and check datafields
            formulaDes = dfDescription(formula, mode="check")

            # Data fields exist
            if formulaDes[0] == "ok":
                f = pIndicator(name=form.cleaned_data["name"], formula=formula, valueType=form.cleaned_data["valueType"])
                f.save()
                message = "New performance indicator has been created!"
            # Data fields do not exist
            else:
                message = formulaDes[0]

    # Get data for entries in table        
    indicator = pIndicator.objects.all()
    indicatorDes = dfDescription(indicator)
    kpiList = []

    # Create dictionary for entries in table
    i = 0
    for entry in indicatorDes[1]:
        kpi = {}
        kpi['name'] = indicator[i].name
        kpi['formula'] = entry
        if int(indicator[i].valueType) == 1:
            kpi['valueType'] = "%"
        else:
            kpi['valueType'] = "Numeric"
        kpi['id'] = indicator[i].id
        kpiList.append(kpi)
        i += 1

    # Render Page
    return render(request, "dashboard/kpi.html", {
        'form' : form,
        'kpiList' : kpiList,
        'message' : message
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successfull
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "dashboard/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "dashboard/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "dashboard/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "dashboard/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "dashboard/register.html")
