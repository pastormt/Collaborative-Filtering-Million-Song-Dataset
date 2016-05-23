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


def calcInCommon( songDict1, songDict2, totalPlays1, totalPlays2, intersection ):
    """
    Returns
    _______
    A measure of how similar 2 dictionaries are (of key = song, value = play percent). 
    """
    inCommonPercent = 0.0
    inCommonPlayCount = 0.0
    
    for song in intersection:
        playPer1 = songDict1[song]
        playPer2 = songDict2[song]
        
        # with %s...
        inCommonPercent += inCommonFormula(playPer1, playPer2)
        
        # now repeat with playCounts...
        playCount1 = playPer1 * totalPlays1
        playCount2 = playPer2 * totalPlays2
        inCommonPlayCount += inCommonFormula(playCount1, playCount2)

    return [inCommonPercent, inCommonPlayCount]
    
def calcSimsAndRecommend( testListeners, listenersTotalPlays, listenersSongs, pruning, power=1 ):
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
                
                if len(intersection) != 0:
                    
                    # inCommon is a list of 2 different measures returned by calcInCommon 
                    inCommon = calcInCommon(listenersSongs[listenerA], songsDictB, listenersTotalPlays[listenerA], listenersTotalPlays[listenerB], intersection)                                    
                    
                    listenerSimilarities[listenerB] = inCommon
        
        # now, for each similarity list (for each listenerB similar to listenerA), normalize
        scaleCoeff = []
        for i in range(0,2):
            scaleCoeff.append(100 / max([v[i] for v in listenerSimilarities.itervalues()]))
        
        # normalized, and combined
        listenerSimilarities = {k: sum(numpy.array(v)*numpy.array(scaleCoeff))**power for k, v in listenerSimilarities.iteritems()}
        # recommend, and prune
        numRecsRequired = len(listenersSongs[listenerA])
    
        maxSim = max(listenerSimilarities.values())
        
        recs = {} # for this test listener's recommendations. key = songID, value = recommendation value
        
        print "Recommending for listener, ", testListenerCount, " @", datetime.now()
        
        for listenerB, similarity in sorted(listenerSimilarities.iteritems(), key=lambda x:x[1], reverse=True):
            if (len(recs) >= numRecsRequired and similarity < pruning * maxSim):
                break
            # songs that B listened to that A did not
            BminusA = {k: v for k, v in listenersSongs[listenerB].iteritems() if k not in listenersSongs[listenerA]}
            for song, playPercent in BminusA.iteritems():
                if song not in recs: # need to add it to dictionary if not already in there
                    recs[song] = similarity
                    # recs[song] = playPercent * similarity
                else:
                    recs[song] += playPercent * similarity
                    # recs[song] += playPercent * similarity
        listenersRecs[listenerA] = [k for k in sorted(recs, key=recs.get, reverse=True)]
    return listenersRecs
    
def calcMeanAveragePrecision( testListenersRecommendations, validListenersSongsLists ):
    
    # index of each will align... so at each location in both lists, the user referred to matches
    recommendations = [] # list of lists of recommendations
    answers = [] # lists of lists of actual songs user listened to
    
    for listener, thisValidListenersSongs in validListenersSongsLists.iteritems():
        answers.append(thisValidListenersSongs) # add what actually listened to (answers) to answers list
        recommendations.append(testListenersRecommendations[listener])
    return kaggle.mapk(answers, recommendations, 500)