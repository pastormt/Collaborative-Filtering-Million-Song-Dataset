# -*- coding: utf-8 -*-
"""
Created on Tue May 17 20:34:37 2016

@author: Michael Pastorino
"""

def appendTestData( listenerID, songs, totalPlays, listenersTotalPlays, listenersSongs, songsListeners, listenerIDs ):
    """
    Called by traverseFile, puts test data into storage dictionaries.
    
    Does everything appendTrainData does, and adds listenerIDs of test listeners to set.
    
    """
    appendTrainData(listenerID, songs, totalPlays, listenersTotalPlays, listenersSongs, songsListeners)
    listenerIDs.add(listenerID)

def appendTrainData( listenerID, songs, totalPlays, listenersTotalPlays, listenersSongs, songsListeners ):
    """
    Called by traverseFile, puts training data into storage dictionaries.
    
    """
    for song, playCount in songs.iteritems():
        playPercent = playCount / float(totalPlays)
        songs[song] = playPercent
        
        if song not in songsListeners:
            songsListeners[song] = {listenerID : playPercent}
        else:
            songsListeners[song][listenerID] = playPercent
    
    listenersTotalPlays[listenerID] = totalPlays
    listenersSongs[listenerID] = songs


def appendAnswersData ( listenerID, songs, totalPlays, listenersAnswersLists ):
    """
    Called by traverseFile, appends to dictionary of key = listenerID, value = songs this listener listened to (in answers data), 
    songs per listener are in no particular order
    """
    songList = list(songs.keys()) # song list for this listenerID
    listenersAnswersLists[listenerID] = songList
    
def traverseFile( dataFile, fcn, args ):
    """
    Iterates over dataFile and executes fcn when listenerID changes.
    
    Used for populating training, test, and hidden data into dictionaries where they're needed.
    
    Train and test data populate listenersTotalPlays, listenersSongs, songsListeners.
    Test data also needs to fill listenerIDs set with the id of each listener in the test data.
    Hidden (i.e. answers) data only needs to produce a dictionary of 
    key = listenerID, value = list of songs listened to (order doesn't matter)
    
    Params (only those that seem to need comments)
    ______
        
    fcn: the function to execute
    args: addt'l arguments to fcn
    
    """
    listenerID = None
    songs = {} # dict where keys are songID, values are % play count (of user's total) -- value of listenersSongs dict
    totalPlays = 0 # total play count for a given listener
    
    with open(dataFile,'r') as openFile:
        for line in openFile:
            thisLine = line.replace('\n', '').split('\t')
            if thisLine[0] != listenerID:
                if listenerID is not None:
                    fcn(listenerID, songs, totalPlays, *args)
                listenerID = thisLine[0]
                songs = {}
                totalPlays = 0
                
            songs[thisLine[1]] = int(thisLine[2])
            totalPlays += int(thisLine[2])
    
    # to add for last user in file, as will have finished 'for' loop, and exited 'with'
    fcn(listenerID, songs, totalPlays, *args)

        
def populateTestStorage( dataFile, listenersTotalPlays, listenersSongs, songsListeners ):
    """
    Calls traverseFile with key argument (appendTestData function) and following argument (the quartet)
    
    Returns
    _______
    set of listenerIDs of listeners in test data
    """
    listenerIDs = set()
    traverseFile(dataFile, appendTestData, [listenersTotalPlays, listenersSongs, songsListeners, listenerIDs])
    return listenerIDs
    
def populateTrainStorage( dataFile, listenersTotalPlays, listenersSongs, songsListeners ):
    """
    Calls traverseFile with key arguments (appendTrainData function) and following argument (the triplet)
    """    
    traverseFile(dataFile, appendTrainData, [listenersTotalPlays, listenersSongs, songsListeners])

def populateAnswersStorage( dataFile ):
    """
    Calls traverseFile with key arguments (appendAnswersData function) and following argument 
    
    Returns
    _______
    dictionary, key = listenerID, value = list (in no particular order) of songs in hidden data this listener listened to
    """    
    listenersAnswersLists = {} # see above
    traverseFile(dataFile, appendAnswersData, [listenersAnswersLists])
    return listenersAnswersLists
    