# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 23:13:54 2016

@author: michaelpastorino
"""

def portionOfTrainData( originalFile, outputFile, reqLines ):
    opf = open(outputFile, 'w')
    count = 0
    readyToBreak = False
    listenerID = None
    with open(originalFile) as openFile:
        for line in openFile:
            thisLine = line.replace('\n', '').split('\t')
            if readyToBreak and (thisLine[0] != listenerID):
                break
            listenerID = thisLine[0]
            opf.write(line)
            count += 1
            if count >= reqLines:
                readyToBreak = True
    opf.close()

portionOfTrainData("train_triplets-copy.txt", "train_triplets-10M.txt", 10000000)

# take a portion of the training data to split into train and test
def divyTrainAndTest( originalFileInput, trainFileOutput, testFileOutput ):
    import random
    import math
    
    listenerID = None
    listenerStart = 0 # where does this listener start?
    listenerEnd = 0 # ditto, end?
    listenerLines = 0 # how many lines are in the file for this listener?
    
    listeners = {} # key is (listenerStart, listenerEnd), value is count of lines for this listener
    
    # line offsets
    linesOffset = []
    offset = 0
    
    with open(originalFileInput) as openFile:
        for line in openFile:
            thisLine = line.replace('\n', '').split('\t')    
            
            if thisLine[0] != listenerID:
                if listenerID != None:
                    listenerEnd = linesOffset[-1]
                    linesOffset = []
                    listeners[(listenerStart, listenerEnd)] = listenerLines
                # new listener
                listenerID = thisLine[0]
                listenerStart = offset
                listenerLines = 0
                
            linesOffset.append(offset)
            offset += len(line)
            listenerLines += 1
        
    # for the last listener
    listenerEnd = linesOffset[-1]
    linesOffset = []
    listeners[(listenerStart, listenerEnd)] = listenerLines
    
    # choose train and test lines foreach listener and write to respective files
    
    # create test and train files
    trainFile = open(trainFileOutput, 'w')
    testFile = open(testFileOutput, 'w')
    
    openFile = open(originalFileInput)
    for startEnd, linesCount in listeners.iteritems():
        trainCount = int(math.ceil(linesCount / 2.0)) # how many lines for training subset?
        
        # list of lines for training subset, starting with 1 for the user's first line in the file
        trainLines = random.sample(xrange(1, linesCount + 1), trainCount) 
        curLine = 1
        
        openFile.seek(startEnd[0])
        offset = 0
        
        for line in openFile:
            if offset > startEnd[1]:
                break
            if curLine in trainLines:
                trainFile.write(line)
            else:
                testFile.write(line)
                
            curLine += 1
            offset += len(line)
            
    openFile.close()
    trainFile.close()
    testFile.close()