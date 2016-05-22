# -*- coding: utf-8 -*-
"""
Created on Wed May 18 15:01:37 2016

@author: michaelpastorino
"""
import kaggle
import numpy
from datetime import datetime

def inCommonFormula( val1, val2 ):
    smaller = min(val1, val2)
    larger = max(val1, val2)
    return smaller + ((smaller / larger) * (larger - smaller))

def calcSongsInCommon( AminusB, BminusA, intersection, listenersTotalPlays ):
    """
    When comparing 2 listeners, this will look at, for those songs they do not share, how "different" A's songs
    that B didn't listen to are to those that B did listen to, and vice versa.
    
    The idea is, if person1 listened to 4 Beatles songs, and person2 listened to 3 of the same Beatles songs and
    1 other Beatles song that person 1 didn't listen to, and person3 listened to 3 of the same Beatles songs as person1 and 
    1 Mozart tune, without knowing they are Beatles songs, you should be able to tell that person1 and person2 are more similar 
    than person1 and person3. We can do this by looking at the dictionaries of listener : playCount in the songsListeners dictionary,
    comparing 2 songs by whether a lot of the same people listened to them. 
    
    Params
    ______
    
    AminusB: section of songsListeners dictionary for those songs in A, but not in B
    Bminus A, intersection: analagous to above
    
    Post
    ___
    songsInCommonPercent and songsInCommonPlayCount are updated to reflect the similarity of thse songs
    
    """
    def helper( dict1, dict2 ):  
        songsInCommonPercent, songsInCommonPlayCount = 0.0, 0.0
        
        for song1, songListeners1 in dict1.iteritems():
            # compare each song's songListeners dictionary with that of every song the other listener listened to
            for song2, songListeners2 in dict2.iteritems():
                for listener, playPer1 in songListeners1.iteritems():
                    if listener in songListeners2:
                        playPer2 = songListeners2[listener]
                        # with %s...
                        songsInCommonPercent += inCommonFormula(playPer1, playPer2)
                        
                        # now repeat with playCounts...
                        playCount1 = playPer1 * listenersTotalPlays[listener]
                        playCount2 = playPer2 * listenersTotalPlays[listener]
                        songsInCommonPlayCount += inCommonFormula(playCount1, playCount2)
        return (songsInCommonPercent, songsInCommonPlayCount)
    
    # comparing the items in listA not in listB to all items in list B, and vice versa.
    # therefore, the different items in each list would be compared to each other twice -- therefore, 2 * below
    songsInCommonPercent, songsInCommonPlayCount = tuple(2 * x for x in helper(BminusA, AminusB))
    t1, t2 = helper(intersection, BminusA)
    songsInCommonPercent += t1
    songsInCommonPlayCount += t2
    
    t1, t2 = helper(intersection, AminusB)
    songsInCommonPercent += t1
    songsInCommonPlayCount += t2   
    
    return (songsInCommonPercent, songsInCommonPlayCount)


def calcInCommon( songDict1, songDict2, totalPlays1, totalPlays2, songListenersIntersection, songListeners1minus2, songListeners2minus1, listenersTotalPlays ):
    """
    Returns
    _______
    A measure of how similar 2 dictionaries are (of key = song, value = play percent). 
    """
    inCommonPercent = 0.0
    inCommonPlayCount = 0.0
    
    for song in songListenersIntersection.iterkeys():
        playPer1 = songDict1[song]
        playPer2 = songDict2[song]
        
        # with %s and with playCounts... need to weight them appropriately (later)
        
        # with %s...
        inCommonPercent += inCommonFormula(playPer1, playPer2)
        
        # now repeat with playCounts...
        playCount1 = playPer1 * totalPlays1
        playCount2 = playPer2 * totalPlays2
        inCommonPlayCount += inCommonFormula(playCount1, playCount2)
    
    songsInCommonPercent, songsInCommonPlayCount = calcSongsInCommon(songListeners1minus2, songListeners2minus1, songListenersIntersection, listenersTotalPlays)  
    
    return [inCommonPercent, inCommonPlayCount, songsInCommonPercent, songsInCommonPlayCount]


def calcSimsAndRecommend( testListeners, listenersTotalPlays, listenersSongs, songsListeners, pruning ):
    """
    Calculates the similarity between each test listener and every other listener, and produces recommendations
    based upon each similarity.
    
    Pre
    ___
    
    The args have been populated with test and training data.
    
    testListeners: set of listeners in test data
    listenersTotalPlays: dictionary, key = listenerID, value = this listener's total play count
    listenersSongs: the usual
    songsListeners: the usual
    
    Returns
    ______
    
    listenersRecs: dictionary of keys = listenerIDs, values = lists (order matters) of recommendations (ie songs) for this listenerID
    
    """
    
    # stores all recommendations
    # key = listenerID, value = ordered list of recommendations
    listenersRecs = {}
    
    # for test printing
    testListenerCount = 0
    totalTestListeners = len(testListeners)
    
    for listenerA in testListeners: # compare this test listener to every other listener
        # for just the current listenerA (below) in testListeners being iterated over, store a dictionary 
        # w/ key = listenerID of similar listener, value = inCommon (a list, below, of different similarity measures)
        # need to store these for the listener, rather than recommend upon each right away, so, for this listenerA alone,
        # the dictionary of all similar listeners can be sent to a pruning function
        listenerSimilarities = {}
        
        testListenerCount += 1
        print "Test listener ", testListenerCount, " of ", totalTestListeners, " @", datetime.now()
        
        #trainListenerCount = 0
        for listenerB, songsDictB in listenersSongs.iteritems(): 
            #trainListenerCount += 1
            #print "Test listener ", testListenerCount, " Train listener ", trainListenerCount
            
            if listenerA != listenerB:
                # 1st similarity measure (%, and play count, in common)
                # also calculate item - item similarities for items that one listener listened to, but the other did not
                intersection = {k for k in listenersSongs[listenerA].iterkeys() if k in songsDictB}
                
                if len(intersection) != 0: # listenerA and listenerB have > 0 songs in common
                    AminusB = {k for k in listenersSongs[listenerA].iterkeys() if k not in songsDictB}
                    BminusA = {k for k in songsDictB.iterkeys() if k not in listenersSongs[listenerA]}
                    
                    songListenersIntersection = {k: v for k, v in songsListeners.iteritems() if k in intersection}  
                    songListenersAminusB = {k: v for k, v in songsListeners.iteritems() if k in AminusB}
                    songListenersBminusA = {k: v for k, v in songsListeners.iteritems() if k in BminusA}
                    
                    # inCommon is a list of 4 different measures returned by calcInCommon
                    inCommon = calcInCommon(listenersSongs[listenerA], songsDictB, listenersTotalPlays[listenerA], listenersTotalPlays[listenerB], songListenersIntersection, songListenersAminusB, songListenersBminusA, listenersTotalPlays)
                                    
                    # 2nd similarity measure (MAP... a better version of % of songs in common)
                    list1 = [k for k in sorted(listenersSongs[listenerA], key=listenersSongs[listenerA].get, reverse=True)]
                    list2 = [k for k in sorted(songsDictB, key=songsDictB.get, reverse=True)]
                    
                    # average precision both from listener1 to listener2 and vice versa
                    meanAvgPreBoth = kaggle.apk(list2, list1, len(list1)) + kaggle.apk(list1, list2, len(list2))
                    
                    inCommon.insert(0, meanAvgPreBoth) # at beginning of inCommon list
                    # len inCommon is now 5                    
                    
                    listenerSimilarities[listenerB] = inCommon
                
        # now, for each similarity list (for each listenerB similar to listenerA), normalize
        scaleCoeff = []
        for i in range(0,5): # len inCommon is 5
            # each of 1st 3 items in inCommon similarities list should count 2x as much as each of last 2
            maxVal = 200 if i < 3 else 100
            scaleCoeff.append(maxVal / max([v[i] for v in listenerSimilarities.itervalues()])) # max value is 100
        
        # normalized, and combined
        listenerSimilarities = {k: sum(numpy.array(v)*numpy.array(scaleCoeff)) for k, v in listenerSimilarities.iteritems()}
        
        # recommend, and prune
        numRecsRequired = len(listenersSongs[listenerA])
        maxSim = 800 # highest max value of 5 similarities combined (200 x 3 + 100 x 2... above)
            
        recs = {} # for this test listener's recommendations. key = songID, value = recommendation value
        
        "Recommending for listener, ", testListenerCount, " @", datetime.now()
        
        for listenerB, similarity in sorted(listenerSimilarities.iteritems(), key=lambda x:x[1], reverse=True):
            if (len(recs) >= numRecsRequired and similarity < pruning * maxSim):
                break
            for song, playPercent in listenersSongs[listenerB].iteritems():
                if song not in listenersSongs[listenerA]: # listenerA didn't already listen to this song -- OK to recommend it
                    if song not in recs: # need to add it to dictionary if not already in there
                        recs[song] = playPercent * similarity
                    else:
                        recs[song] += playPercent * similarity
        listenersRecs[listenerA] = [k for k in sorted(recs, key=recs.get, reverse=True)]
    
    return listenersRecs

def calcMeanAveragePrecision( testListenersRecommendations, validListenersSongsLists ):
    # convert testListenersRecommendations and validListenersSongs to lists of lists
    
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
    
    return kaggle.mapk(answers, recommendations, 500)