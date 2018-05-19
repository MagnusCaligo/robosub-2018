import csv
import os

class Previous_State_Logging:
    # @param Pass in the file name formatted as: fileName.csv
    def __init__(self, fileName):
        self.dictionary = {}

        # Put the two log files in their own folder.
        path = 'savedSettings'
        if not os.path.exists(path):
            os.makedirs(path)

        self.file1 = "savedSettings/" + fileName
        self.file2 = "savedSettings/backup" + fileName

        # Working variable keeps track of which file we're currently working with.
        self.working = self.file1

        path = "savedSettings/" + fileName
        if not os.path.exists(path):

            #Create the files.
            with open(self.file1, 'wb') as csvfile:
                fieldnames = ['key', 'value']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            with open(self.file2, 'wb') as csvfile:
                fieldnames = ['key', 'value']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    def __goodFile__(self):
        file1Done = False
        file2Done = False
        goodFile = ""

        # Open the first file to see if DoneWriting is present.
        with open(self.file1, 'rb') as csvfile:
            fieldnames = ['key', 'value']
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)

            for row in reader:
                if (row['key'] == 'DoneWriting'):
                    file1Done = True

        # Open the second file to see if DoneWriting is present.
        with open(self.file2, 'rb') as csvfile:
            fieldnames = ['key', 'value']
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)

            for row in reader:
                if (row['key'] == 'DoneWriting'):
                    file2Done = True

        # Set the good file to whichever file has "done" at the end.
        # If "DoneWriting" is present in both files, we need to see which one is most recent.
        if (file1Done == file2Done):
            if (os.path.getmtime(self.file2) < os.path.getmtime(self.file1)):
                goodFile = self.file1
            else:
                goodFile = self.file2
        elif (file1Done):
            goodFile = self.file1
        elif (file2Done):
            goodFile = self.file2

        return goodFile

    # Reads the values from the csv file from a passed in key.
    # If the value isn't in the file, add it to the file with a default value of 0.
    # Returns the value if it's found, returns 0 if not found.
    def readFile(self, key):
        goodFile = self.__goodFile__()

        # Open and read from the good file.
        with open(goodFile, 'rb') as csvfile:
            fieldnames = ['key', 'value']
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)

            # Loop through the file to find the value from the key passed in.
            for row in reader:
                if (row['key'] == key):
                    return row['value']

        # If you get here, that means the value wasn't found,
        # so we make a new key and set it to a default value of 0.
        self.add(key, 0)
        return 0

    # Adds a key and a value from a dictionary (with only ONE key and ONE value) passed in.
    def addDict(self, dictionary):
        keys = dictionary.keys()
        values = dictionary.values()
        key = keys[0]
        value = values[0]
        self.add(key, value)

    # Adds a key and a value to the csv file and the dictionary.
    # Swap between adding to file1 and file2, so that you can have at least one file that works,
    # in case the GUI crashes, you can check the other file.
    def add(self, key, value):
        #Update the dictionary.
        self.dictionary[key] = value

        #Erase the current file we're working with to start fresh.
        with open(self.working, 'wb') as csvfile:
            csvfile.truncate()

        #Put everything from the dictionary back into the file we just erased.
        with open(self.working, 'ab') as csvfile:
            fieldnames = ['key', 'value']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            for key in self.dictionary:
                writer.writerow({'key': key, 'value': self.dictionary[key]})

            writer.writerow({'key': "DoneWriting", 'value': "True"})

        if (self.working == self.file1):
            self.working = self.file2
        else:
            self.working = self.file1

    # Load parameters into the dictionary from the csv file.
    def loadFile(self):
        file = self.__goodFile__()

        with open(file, 'rb') as csvfile:
            fieldnames = ['key', 'value']
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)

            # Loop through the file to add the values into the dictionary from this file.
            for row in reader:
                self.dictionary[row['key']] = row['value']
        #print (self.dictionary)
        return self.dictionary

    # Returns the value from the dictionary from the key passed in.
    # Unless the value was already a 0, if the value wasn't in the file, it will return a 0.
    def getValue(self, key):
        return self.readFile(key)

    def saveDict(self, dictionary):
        """
        Saves new dictionary to file
        :param dictionary:
        :return:
        """
        self.dictionary = dictionary

        #Erase the current file we're working with to start fresh.
        with open(self.working, 'wb') as csvfile:
            csvfile.truncate()

        #Put everything from the dictionary back into the file we just erased.
        with open(self.working, 'ab') as csvfile:
            fieldnames = ['key', 'value']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            for key in self.dictionary:
                writer.writerow({'key': key, 'value': self.dictionary[key]})

            writer.writerow({'key': "DoneWriting", 'value': "True"})

        if self.working == self.file1:
            self.working = self.file2
        else:
            self.working = self.file1