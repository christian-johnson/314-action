import googlesearch as gs
import re
import pandas as pd
import pickle
import numpy as np
import string

class LegislatorList():
    def __init__(self):
        self.fileName = 'statelegislators.txt'

        self.scienceWords = ['PhD', "Masters", "Master's", 'masters', "master's", 'biology', 'Biology', 'chemistry', 'Chemistry', 'physics', 'Physics', 'Computer science', 'computer science', 'Computer Science', 'Math ',
            ' math', 'mathematics', 'Mathematics', 'Statistics', 'statistics', 'Biologist', 'biologist', 'chemist', 'Chemist', 'physicist', 'Physicist', 'mathematician', 'Mathematician', 'Statistician', 'statistician',
            'scientist', 'Scientist', 'Researcher', 'researcher', 'M.D.', 'Doctor', 'doctor', 'doctorate', 'Doctorate', 'Doctoral', 'doctoral', 'physician', 'Physician', 'Engineering', 'engineering', 'Engineer',
            'engineer', 'surgeon', 'Surgeon', 'Dentist', 'dentist', 'endocrinologist', 'Endocrinologist', 'Zoologist', 'zoologist', 'botanist', 'Botanist', 'Entymologist', 'entymologist', 'anthropologist',
            'anthropology', 'Anthropology', 'environmental science', 'Environmental Science', 'environmental scientist', 'Environmental Scientist', 'Environmental scientist', 'phamacology',
            'Pharmacology', 'pharmacologist', 'Pharmacologist']

        self.states = ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawii', 'Idaho', 'Illinois', 'Indiana','Iowa', 'Kansas', 'Kentucky', 'Louisiana',
            'Maine', 'Maryland', 'Massachusets', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire','New Jersey', 'New Mexico', 'New York', 'North Carolina',
            'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
            'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming', 'END']

        self.legislators = []
        self.theChamber='Senate'
        self.theState='Alabama'
        self.theDistrict=1
        self.extractDigits = lambda x: "".join(char for char in x if char in string.digits)

    def openFile(self):
        self.file = open(self.fileName)
        self.fileLines = self.file.readlines()

    def closeFile(self):
        self.file.close()

    def aStateInLine(self, line, states):
        for state in states:
            if state in line and '==' in line:
                return True, state
        return False, None

    def addLegislator(self, theName, theState, theChamber, theDistrict):
        self.legislators.append({'Name': theName, 'State': theState, 'District': theDistrict, 'Chamber': theChamber})

    def scrapeFile(self):
        i = 0

        for i in range(len(self.fileLines)):
            #Check state
            self.stateBool, returnedState = self.aStateInLine(self.fileLines[i], self.states)
            if self.stateBool:
                self.theState = returnedState

            #Check chamber
            if 'Senate' in self.fileLines[i] or 'Senator' in self.fileLines[i]:
                self.theChamber = 'Senate'
                chamberBool = True
                self.theDistrict = 1
            elif 'Representatives' in self.fileLines[i] or 'House' in self.fileLines[i]:
                self.theChamber = 'House'
                chamberBool = True
                self.theDistrict = 1
            else:
                chamberBool = False

            #Check for number in the line
            if self.extractDigits(self.fileLines[i]):
                districtBool = True
                self.theDistrict=self.extractDigits(self.fileLines[i])
            else:
                districtBool = False

            if len(self.fileLines[i])>4 and not districtBool and not chamberBool and not self.stateBool:
                if len(self.fileLines[i].split('|')) == 1:
                    self.theName = self.fileLines[i]
                if len(self.fileLines[i].split('|')) == 2:
                    if 'politician' in self.fileLines[i].split('|')[0] or 'Politician' in self.fileLines[i].split('|')[0] or 'politician' in self.fileLines[i].split('|')[0] or 'Representative' in self.fileLines[i].split('|')[0] or 'Senator' in self.fileLines[i].split('|')[0] or 'senator' in self.fileLines[i].split('|')[0]:
                        self.theName = self.fileLines[i].split('|')[0]
                    elif 'politician' in self.fileLines[i].split('|')[1] or 'Politician' in self.fileLines[i].split('|')[1] or 'politician' in self.fileLines[i].split('|')[1] or 'Representative' in self.fileLines[i].split('|')[1] or 'Senator' in self.fileLines[i].split('|')[1] or 'senator' in self.fileLines[i].split('|')[1]:
                        self.theName = self.fileLines[i].split('|')[1]
                    else:
                        self.theName = self.fileLines[i].split('|')[0]+' '+self.fileLines[i].split('|')[1]
                if len(self.fileLines[i].split('|')) == 3:
                    for j in range(3):
                        if 'politician' in self.fileLines[i].split('|')[j] or 'Politician' in self.fileLines[i].split('|')[j]:
                            self.theName = self.fileLines[i].split('|')[j]
                while self.theName[0] == ' ':
                    self.theName = self.theName[1:]
                self.theName = self.theName.split('\n')[0]

                nearbyIndex = False
                for j in range(i-2, i+2):
                    if self.extractDigits(self.fileLines[j]):
                        nearbyIndex = True
                if not nearbyIndex:
                    self.theDistrict = str(int(self.theDistrict) + 1)

                self.addLegislator(self.theName, self.theState, self.theChamber, self.theDistrict)

    def cleanhtml(self, raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def checkScience(self, htmlString, scienceWords):
        i = 0
        scienceVector = np.zeros((len(scienceWords)))
        for word in scienceWords:
            if word in htmlString:
                scienceVector[i] = 1
            i += 1
        if sum(scienceVector)>0:
            return True, scienceVector
        else:
            return False, scienceVector

    def searchLegislator(self):
        j = 0
        self.scienceLegislators = pd.concat([pd.DataFrame(self.legislators),pd.DataFrame(np.zeros((len(self.legislators), len(self.scienceWords))), columns=self.scienceWords)],axis=1)
        print(self.scienceLegislators)
        for j in self.scienceLegislators.index:
            if j%100 ==0:
                print(str(float(j)/float(len(self.scienceLegislators))*100.)+'%')
            scienceBool = False
            #Check Wikipedia first
            urlstring = 'https://en.wikipedia.org/wiki/'+self.scienceLegislators.loc[j]['Name'].replace(' ','_')
            try:
                htmlstring = self.cleanhtml(str(gs.get_page(urlstring)))
                scienceBool, scienceVector = self.checkScience(htmlstring, self.scienceWords)
                if scienceBool:
                    self.scienceLegislators.loc[j,self.scienceWords] = self.scienceLegislators.loc[j,self.scienceWords]+scienceVector

            except:
                urlstring = 'https://en.wikipedia.org/wiki/'+self.scienceLegislators.loc[j]['Name'].replace(' ','_')+'_(Politician)'
                try:
                    htmlstring = self.cleanhtml(str(gs.get_page(urlstring)))
                    scienceBool, scienceVector = self.checkScience(htmlstring, self.scienceWords)
                    if scienceBool:
                        self.scienceLegislators.loc[j,self.scienceWords] = self.scienceLegislators.loc[j,self.scienceWords]+scienceVector

                except:
                    pass
            x = gs.search(self.scienceLegislators.loc[j]['Name']+' biography')
            for k in range(3):
                try:
                    htmlstring = self.cleanhtml(str(gs.get_page(urlstring)))
                    scienceBool, scienceVector = checkScience(htmlstring, scienceWords)
                    if scienceBool:
                        self.scienceLegislators.loc[j,self.scienceWords] = self.scienceLegislators.loc[j,self.scienceWords]+scienceVector
                except:
                    pass

        self.scienceLegislators.to_csv('legislators.csv')



def main():
    legislatorList = LegislatorList()
    legislatorList.openFile()
    legislatorList.scrapeFile()
    legislatorList.closeFile()
    legislatorList.searchLegislator()

if __name__ == '__main__':
    main()
