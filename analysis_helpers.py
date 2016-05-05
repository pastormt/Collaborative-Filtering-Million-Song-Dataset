import numpy
import wendy_kan
from math import ceil

def calcMeanAveragePrecision( testListenersRecommendations, validListenersSongsLists ):
    # convert testListenersRecommendations and validListenersSongs to lists of lists, for Wendy Kan's
    # MAP function
    
    # index of each will align... so at each location in both lists, the user referred to matches
    recommendations = [] # list of lists of recommendations
    answers = [] # lists of lists of actual songs user listened to
    
    for listener, thisValidListenersSongs in validListenersSongsLists.iteritems():
        answers.append(validListenersSongsLists[listener]) # add what actually listened to (answers) to answers list
        
        thisListenersRecs = [] # to store recs, if any were made for this listener
        if listener in testListenersRecommendations:
            for song in sorted(testListenersRecommendations[listener], key=testListenersRecommendations[listener].get, reverse=True):
                thisListenersRecs.append(song)
        recommendations.append(thisListenersRecs) # add recs (or blank list) to recommendations list, in same index position as answers
    
    return wendy_kan.mapk(answers, recommendations, 500)
    
def appendFilterItems( songA, songB, sim, testListenersSongs, listenersRecs ):
    for listener, songDict in testListenersSongs.iteritems(): # each listener in the test data   
        if songB in songDict and songA not in songDict:
            if listener in listenersRecs:
                if songA not in listenersRecs[listener]:
                    listenersRecs[listener][songA] = sim * songDict[songB]
                else:
                    listenersRecs[listener][songA] += sim * songDict[songB]
            else:
                listenersRecs[listener] = {songA : sim * songDict[songB]}

def collabFilterItems( testListenersSongs, testItemSimilarities, listenersRecs ):
    print testItemSimilarities
    for songTuple, simTuple in testItemSimilarities.iteritems():
        song1, song2 = songTuple
        sim1, sim2 = simTuple
        appendFilterItems(song1, song2, sim1, testListenersSongs, listenersRecs)
        appendFilterItems(song2, song1, sim2, testListenersSongs, listenersRecs)
    
    print "ListenersRecs length:", len(listenersRecs)
    print listenersRecs

def collabFilterListeners( listenersSongs, prunedSimilarities, listenersRecs ):
    for listener, similaritiesDict in prunedSimilarities.iteritems(): # for all listeners in prunedSim
        for otherListener, similarity in similaritiesDict.iteritems():
            newSongs = {} # key = song, value = playPercent
            for song, playPercent in listenersSongs[otherListener].iteritems():
                if song not in listenersSongs[listener]:
                    newSongs[song] = playPercent * similarity
                    
            # now newSongs is populated with all songs otherListened listened to that listener did not...
            if listener not in listenersRecs:
                listenersRecs[listener] = newSongs
            else: # a recommendations dict for this listener already created from similarity w/ another user... so add to it
                for newSong, newSongPercentRec in newSongs.iteritems():
                    if newSong in listenersRecs[listener]:
                        listenersRecs[listener][newSong] += newSongPercentRec
                    else:
                        listenersRecs[listener][newSong] = newSongPercentRec

    print "ListenersRecs length:", len(listenersRecs)
    
def populateValidationStorage( dataFile, validListenersSongs, validListenersSongsLists ):  
    listenerID = None
    totalPlays = 0
    songs = {}
    songsList = []
    with open(dataFile,'r') as openFile:
        for line in openFile:
            thisLine = line.replace('\n', '').split('\t')
            
            if thisLine[0] != listenerID:
                if listenerID is not None:
                    for song, playCount in songs.iteritems():
                        songs[song] = (playCount * 100) / float(totalPlays)
                    validListenersSongs[listenerID] = songs
                    validListenersSongsLists[listenerID] = songsList
                listenerID = thisLine[0]
                songs = {}
                songsList = []
                totalPlays = 0
            
            totalPlays += int(thisLine[2])
            songs[thisLine[1]] = int(thisLine[2])
            songsList.append(thisLine[1])

    # to add last user in file
    for song, playCount in songs.iteritems():
        songs[song] = (playCount * 100) / float(totalPlays)
    validListenersSongs[listenerID] = songs
    validListenersSongsLists[listenerID] = songsList

def appendStorage( trainOrTest, listenerID, songs, totalPlays, listenersSongs, listenersTotalPlays, songsListeners, songsTotalPlays, testSongsListeners, testListenersSongs):
    for key, value in songs.iteritems():
        playPercent = (value*100) / float(totalPlays) # play count to % of total plays for user
        songs[key] = playPercent
        if key not in songsListeners:
            songsListeners[key] = set(listenerID)
            songsTotalPlays[key] = value
        else:
            songsListeners[key].add(listenerID)
            songsTotalPlays[key] += value
            
        if trainOrTest == "TEST":
            if key not in testSongsListeners:
                testSongsListeners[key] = set(listenerID)
            else:
                testSongsListeners[key].add(listenerID)
    
    listenersTotalPlays[listenerID] = totalPlays
    if trainOrTest == "TEST":
        testListenersSongs[listenerID] = songs
    listenersSongs[listenerID] = songs

def adjustSongsListenersVals( songsListeners, testSongsListeners, listenersTotalPlays, songsTotalPlays ):
    def adjustHelper( aDict ):
        for song, userDict in aDict.iteritems():
            for user, listenerPer in userDict.iteritems():
                songPer = (listenerPer * listenersTotalPlays[user]) # back to plays for this user... * 100
                songPer /= float(songsTotalPlays[song])
                userDict[user] = songPer

    adjustHelper(songsListeners)
    adjustHelper(testSongsListeners)
            
            
def populateStorage( trainOrTest, dataFile, listenersSongs, listenersTotalPlays, songsListeners, songsTotalPlays, testSongsListeners, testListenersSongs): 
    listenerID = None
    songs = {} # dict where keys are songID, values are % play count (of user's total) -- value of listenersSongs dict
    totalPlays = 0 # total play count for a given listener

    with open(dataFile,'r') as openFile:
        for line in openFile:
            thisLine = line.replace('\n', '').split('\t')
            if thisLine[0] != listenerID:
                if listenerID is not None:
                    appendStorage(trainOrTest, listenerID, songs, totalPlays, listenersSongs, listenersTotalPlays, songsListeners, songsTotalPlays, testSongsListeners, testListenersSongs)
                listenerID = thisLine[0]
                songs = {}
                totalPlays = 0
                
            songs[thisLine[1]] = int(thisLine[2])
            totalPlays += int(thisLine[2])
    
    # to add for last user in file, as will have finished 'for' loop, and exited 'with'
    appendStorage(trainOrTest, listenerID, songs, totalPlays, listenersSongs, listenersTotalPlays, songsListeners, songsTotalPlays, testSongsListeners, testListenersSongs)

# note: for the listeners (not for songs, though), can be done more efficiently, as the listeners in test data
# are not in the training data... think about it ... but not worth writing another one...
def pruneSimilarities( similarities, testListenersSongs, cutoff=0 ):
    prunedSimilarities = {} # keys are listener, values are dicts of {other listener : similarity}
    # goal is to remove similarities below a certain cutoff
    for listener in testListenersSongs.iterkeys():
        for listenerTuple, similarity in similarities.iteritems():
            listener1, listener2 = listenerTuple
            if listener == listener1 or listener == listener2: # similarity references this listener
                if listener == listener1:
                    thisListener = listener1
                    otherListener = listener2
                else:
                    thisListener = listener2
                    otherListener = listener1
                    
                if thisListener not in prunedSimilarities:
                    prunedSimilarities[thisListener] = {otherListener : similarity}
                else:
                    prunedSimilarities[thisListener][otherListener] = similarity
            # end if: similarity references this listener
        if listener in prunedSimilarities and cutoff != 0:
            threshold = cutoff * max(prunedSimilarities[listener].values())
            prunedSimilarities[listener] = {k: v for k, v in prunedSimilarities[listener].iteritems() if v > threshold}
        
    print "Pruned similarities length: ", len(prunedSimilarities)
    return prunedSimilarities
        

def singleValList( aList ):
    singleVal = True
    for value in aList:
        if value != aList[0]:
            singleVal = False
            break
    return singleVal

def listenerSimilaritiesHelper( key1, subDict1, key2, subDict2, similarities):
    
    key1Plays, key2Plays, inCommon = [], [], []
    # meaningfullyInCommon: if 2 users have listened to the same song, but 1 listened to it 2,000 times, and 
    # the other listened once, they don't really have it soooo much in common. meaningfullyInCommon would store a 1
    # (of course, this will be partially captured in the corrcoef calculation as well)
    meaningfullyInCommon = 0.0 
    # if user1 listened to song A 30 times, and user B 20 times, this 10 difference shouldn't totally count against
    # their similarity as much as a song that one listened to and the other did not...
    # in similarity calculation, a gauge for how much the 2 play counts were off by... rewarding for being
    # off by less
    
    inCommon = 0
    
    #subKey1 is song, plays1 is % played
    for subKey1, plays1 in subDict1.iteritems():
        if subKey1 in subDict2:
            inCommon += 1
            
            key1Plays.append(plays1)
            key2Plays.append(subDict2[subKey1])
            
            # these should already be floats... so no problem
            if plays1 < subDict2[subKey1]:
                meaningfullyInCommon += plays1 + ((plays1 / subDict2[subKey1]) * (subDict2[subKey1] - plays1))
            else:
                meaningfullyInCommon += subDict2[subKey1] + ((subDict2[subKey1] / plays1) * (plays1 - subDict2[subKey1]))
    
    if inCommon != 0: # if == 0 then not similar, don't calc or add to dictionary
        
        # test if either key1Plays or key2Plays (or both) contains all the same values in which case, a correlation between 
        # the 2 lists is not applicable since at least 1 does not vary
        
        if singleValList(key1Plays) or singleValList(key2Plays):
            # adding 2 as likening this to a no correlation situation, which in the scenario where noVary == False, would be 0, 
            # which would be added to 2, and multiplied by multiplier (see else block below)
            similarity = 2 * meaningfullyInCommon
        else:
            # 2 + corrcoef since any sort of correlation shouldn't lower the multiplier, by this method
            # so a perfect negative correlation of -1 + 2 is 1, so the multiplier does not change
            similarity = meaningfullyInCommon * (2 + numpy.corrcoef(numpy.array(key1Plays), numpy.array(key2Plays))[1,0])
        # add this similarity to similarities
        similarities[(key1, key2)] = similarity
        
def songSimilaritiesHelper( totalListeners, key1, subDict1, key2, subDict2, similarities ):
    inCommon = float(len(subDict1.intersection(subDict2)))
    
    if inCommon != 0: # if they have any listeners in Common
        adjustedCorr = 300 # to match max similarity between listeners
        
        # Bayes
        lenSubDict2 = float(len(subDict2))
        lenSubDict1 = float(len(subDict1))
        
        multiplier1 = ceil(((inCommon / lenSubDict1) * (lenSubDict1 / totalListeners)) / (lenSubDict2 / totalListeners))
        multiplier2 = ceil(((inCommon / lenSubDict2) * (lenSubDict2 / totalListeners)) / (lenSubDict1 / totalListeners))
        
        similarities[(key1, key2)] = (adjustedCorr * multiplier1, adjustedCorr * multiplier2)

def calcSongSimilarities ( totalListeners, testDataDict, allDataDict ):
    relevantSongsDict = {k: v for k, v in allDataDict.iteritems() if k in testDataDict}
    
    # print for testing
    print "relevantSongsDict length: ", len(relevantSongsDict)
    print relevantSongsDict
    
    print "allDataDict length: ", len(allDataDict)
    similarities = {}
    
    count = 0
    for key1, subDict1 in relevantSongsDict.iteritems(): # song, set of listeners to song
        count += 1
        print count
        for key2, subDict2 in allDataDict.iteritems(): # song, set of listeners to song
            if key1 != key2 and (key1, key2) not in similarities and (key2, key1) not in similarities:
                songSimilaritiesHelper(totalListeners, key1, subDict1, key2, subDict2, similarities)
                
    return similarities

def calcListenersSimilarities( testDataDict, allDataDict ):
    similarities = {} # key (user, user) or (song, song) depending on call, value = similarity
    
    # print for testing
    print "testDataDict length: ", len(testDataDict)
    print "allDataDict length: ", len(allDataDict)    
    
    count = 0
    for key1, subDict1 in testDataDict.iteritems(): # only TEST data
        count += 1
        print count
        for key2, subDict2 in allDataDict.iteritems(): # TEST and TRAINING data
            if key1 != key2 and (key1, key2) not in similarities and (key2, key1) not in similarities:
                listenerSimilaritiesHelper(key1, subDict1, key2, subDict2, similarities)
                
    return similarities