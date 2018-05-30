import csv
import os
import datetime

class exLog:
    def __init__(self, fileName):
        # Each column is for a different category of data.
        self.fieldnames = ['Time', 'north', 'east', 'up', 'heading', 'pitch', 'roll',]

        # Create the file with the fieldnames.
        self.path = fileName + ".csv"
        if not os.path.exists(self.path):
            with open(self.path, 'wb') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
                writer.writeheader()

    # Pass in the correct data as lists.
    def writeToFile(self, dvl, ahrs):
        return
        time = str(datetime.datetime.now().time().hour) + ':' + str(datetime.datetime.now().time().minute)\
               + ':' + str(datetime.datetime.now().time().second)

        with open(self.path, 'ab') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)

            writer.writerow({'Time': time, 'north': dvl[0], 'east': dvl[1], 'up': dvl[2],
                             'heading': ahrs[0], 'pitch': ahrs[1], 'roll': ahrs[2]})
