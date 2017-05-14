
# Import the libraries
import os
import sys
import time

sys.path.append('../Voting')
from Voting import Voting

sys.path.append('../FaceRecognition')
from FaceRecognition import FaceRecognition

sys.path.append('../MachineryCommittee')
from MachineryCommittee import MachineryCommittee

class Report:
    """
    Class that provides an interface to generate reports
    """

    def __init__(self, object):
        """
        Get the object (FaceRecognition or MachineryCommittee)
        """
    	self.object = object

    def generateReportSummary(self):
        """
        Generate a report summary with informations about the test.
        Return the content as a string.
        """
        content = time.strftime("%d/%m/%Y %H:%M:%S")

        # For the face recognition class get only the name of the algorithm
        if type(self.object) == FaceRecognition:
            content += "\nAlgorithm: " + self.object.getAlgorithm().getAlgorithmName()
        # For the machinery committee class get the name of all algorithms
        elif type(self.object) == MachineryCommittee:
            for index in xrange(0, len(self.object.getFRAlgorithms())):
                content += "\nAlgorithm: " + self.object.getFRAlgorithms()[index].getAlgorithmName()

        recognized, unrecognized, nonFaces = self.object.getResults()
        content += "\nTrain Path: " + self.object.getTrainPath()
        content += "\nTest Path: "  + self.object.getTestPath()
        content += "\nTotal Images Analyzed: " + str(recognized + unrecognized + nonFaces)
        content += "\nRecognized Faces: "   + str(recognized)
        content += "\nUnrecognized Faces: " + str(unrecognized)
        content += "\nNon Faces: "          + str(nonFaces)

        # For face recognition class show the threshold
        if type(self.object) == FaceRecognition:
            if self.object.getThreshold() >= 0:
                content += "\nThreshold Used: " + str(self.object.getThreshold())
            else:
                content += "\nThreshold Not Used."
        # For machinery committee class show the voting algorithm name
        elif type(self.object) == MachineryCommittee:
            content += "\nVoting Scheme: " + self.object.getVoting().getVotingSchemeName()
            if self.object.getVoting().getVotingScheme() == Voting.WEIGHTED:
                content += "\nWeights: " + ', '.join(self.object.getVoting().getWeights())

        sizeX, sizeY = self.faceRecognition.getAuxiliary().getDefaultSize()
        content += "\n\nDefault Size Images: " + str(sizeX) + "x" + str(sizeY)
        content += "\nInterpolation Method: "  + self.object.getAuxiliary().getInterpolationMethodName()
        content += "\nSupported Files: " + ', '.join(self.object.getAuxiliary().getSupportedFiles())
        return content

    def generateFullReport(self):
        """
        Generate the full report.
        Return the content containing the information about each predicted image.
        """
        # Get the predicted results
        predictSubjectIds = self.object.getPredictedSubjectIds()
        predictConfidence = self.object.getPredictedConfidence()
        # Get the test information (labels and filenames)
        testLabels    = self.object.getTestLabels()
        testFileNames = self.object.getTestFileNames()

        content = ""

        # Create each line based on the predicted subject IDs
        for index in xrange(0, len(predictSubjectIds)):
            # Format: 1: Expected subject: 3: Classified as subject: 2: With confidence: 4123.123123: File name: 1_3
            content += str(index)
            content += ": Expected subject: " + str(testLabels[index])
            content += ": Classified as subject: " + str(predictSubjectIds[index])
            content += ": With confidence: " + str(predictConfidence[index])
            content += ": File name: " + testFileNames[index]
            content += "\n"

        return content

    def printResults(self):
        """
        Function used to show the results
        """
        print "========================= Results ========================="
        print self.generateReportSummary()
        print "==========================================================="

    def saveReport(self, path=""):
        """
        Function used to automatically save the report in a defined folder.
        Save only the text report not the images.
        """

        # Generate the report content
        content = self.generateReportSummary()
        content += "\n================================\n"
        content += self.generateFullReport()

        # Make sure that none folder will have the same name
        time.sleep(1)

        # If the parameters were set include it in the folder name
        fileName = time.strftime("%Y_%m_%d_%H_%M_%S") + ".txt"

        # If the path is not empty use it in the filename
        if path != "":
            if path.endswith("/"):
                fileName = path + fileName
            else:
                fileName = path + "/" + fileName

        # Save the text file
        self.object.getAuxiliary().writeTextFile(content, fileName)

    def saveAllResults(self, path=""):
        """
        Function used to automatically save the report in a defined folder.
        Save the entire results, including the summary report, full report and all images.
        """

        # If the path is not empty use it in the filename
        if path != "":
            if path.endswith("/") is not True:
                path += "/"

        # Defined the name of the new folder
        path += time.strftime("%Y_%m_%d_%H_%M_%S") + "/"

        # If the path does not exist, create it
        if not os.path.exists(path):
            os.makedirs(path)

        # Save the report
        self.saveReport(path)

        # Create 3 new folders
        recognizedFolder   = path + "Recognized/"
        unrecognizedFolder = path + "Unrecognized/"
        nonfacesFolder     = path + "NonFaces/"

        os.makedirs(recognizedFolder)
        os.makedirs(unrecognizedFolder)
        os.makedirs(nonfacesFolder)

        # The predicted results
        predictSubjectIds = self.object.getPredictedSubjectIds()
        predictConfidence = self.object.getPredictedConfidence()
        # The tests information
        testImages    = self.object.getTestImages()
        testLabels    = self.object.getTestLabels()
        testFileNames = self.object.getTestFileNames()
        # The training information
        trainImages   = self.object.getTrainImages()
        trainLabels   = self.object.getTrainLabels()

        delimiter = "_"

        for index in xrange(0, len(predictSubjectIds)):
            # Patter: 1_Expected_2_Classified_2_Confidence_40192.12938291.png
            label = str(index) + delimiter + "Expected" + delimiter + str(testLabels[index]) + delimiter
            label += "Classified" + delimiter + str(predictSubjectIds[index]) + delimiter

            if type(self.object) == FaceRecognition:
                label += "Confidence" + delimiter + str(predictConfidence[index])
            elif type(self.object) == MachineryCommittee:
                label += "Voting" + delimiter + self.object.getVoting().getVotingSchemeName()

            label += ".png"

            # Find the image that matches based on the trainLabel and predictedSubjectIDs
            image1 = testImages[index]
            image2 = None
            for i in xrange(0, len(trainLabels)):
                if str(trainLabels[i]) == str(predictSubjectIds[index]):
                    image2 = trainImages[i]

            # Concatenate the images
            image = self.object.getAuxiliary().concatenateImages(image1, image2)

            # Get the correct fileName
            fileName = ""
            if str(testLabels[index]) == "-1":
                fileName = nonfacesFolder
            elif str(testLabels[index]) == str(predictSubjectIds[index]):
                fileName = recognizedFolder
            else:
                fileName = unrecognizedFolder

            fileName += label

            # Save the concatenated image in the correct folder
            self.object.getAuxiliary().saveImage(fileName, image)
