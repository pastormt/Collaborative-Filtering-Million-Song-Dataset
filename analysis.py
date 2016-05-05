import analysis_helpers
import datetime

trainData = "train_triplets.txt"
testData = "year1_test_triplets_visible-test.txt"
hiddenData = "year1_test_triplets_hidden-test.txt"

listenersSongs = {} # keys are userIDs, values are dicts of songs and play counts (%) per each that this listener listened to
listenersTotalPlays = {} # keys are userIDs, values are total user play counts

songsTotalPlays = {}
songsListeners = {} # key = songID, value = set of listeners

testSongsListeners = {} # same as songsListeners, but only includes TEST data
testListenersSongs = {} # same as listenersSongs, but only includes TEST data

# populate storage dictionaries with TRAIN and TEST data

print "Populating train storage at", datetime.datetime.now()
analysis_helpers.populateStorage("TRAIN", trainData, listenersSongs, listenersTotalPlays, songsListeners, songsTotalPlays, testSongsListeners, testListenersSongs)


print "Populating test storage at", datetime.datetime.now()
analysis_helpers.populateStorage("TEST", testData, listenersSongs, listenersTotalPlays, songsListeners, songsTotalPlays, testSongsListeners, testListenersSongs)

'''
print "Adjusting songs listeners values at", datetime.datetime.now()
analysis_helpers.adjustSongsListenersVals(songsListeners, testSongsListeners, listenersTotalPlays, songsTotalPlays)
'''

# clear space
songsTotalPlays = {}
# end clear space

print "Calculating listener similarities at", datetime.datetime.now()
# calculate user - user and song - song similarities
testListenersSimilarities = analysis_helpers.calcListenersSimilarities(testListenersSongs, listenersSongs)

#clear space
listenersTotalPlays = {} # keys are userIDs, values are total user play counts
#end clear space

print "Pruning listener similarities at", datetime.datetime.now()
prunedTestListenersSimilarities = analysis_helpers.pruneSimilarities(testListenersSimilarities, testListenersSongs, 0)

#clear space
testListenersSimilarities = {}
# end clear space

# produce guesses (i.e. recommendations) based on collab filtering
print "Collab filtering..."

testListenersRecommendations = {} # key = listener, val = dict of songs recommended for this listener (key = song, val = recommended value... greater means more highly recommended)

print "Listener-based collab filtering at", datetime.datetime.now()
# all listenersSongs, since using those listener - listener tuples in testListenersSimilarities to get recommendations from any
# user, obviously including those in training data
analysis_helpers.collabFilterListeners(listenersSongs, prunedTestListenersSimilarities, testListenersRecommendations) # user-based

'''
totalListeners = float(len(listenersSongs))
'''

# clear space
prunedTestListenersSimilarities = {}
listenersSongs = {} # keys are userIDs, values are dicts of songs and play counts (%) per each that this listener listened to
# end clear space
'''
print "Calculating song similarities at", datetime.datetime.now()

testItemsSimilarities = analysis_helpers.calcSongSimilarities(totalListeners, testSongsListeners, songsListeners)

print "Item-based collab filtering at", datetime.datetime.now()
# here, testListenersSongs since going to loop through all songs for test listeners to see which songs from all users should
# be recommended, based on similarity to highly played songs in testListenersSongs

analysis_helpers.collabFilterItems(testListenersSongs, testItemsSimilarities, testListenersRecommendations) # item-based
'''

# clear space
testItemsSimilarities = {}
songsListeners = {}

testSongsListeners = {} # same as songsListeners, but only includes TEST data
testListenersSongs = {} # same as listenersSongs, but only includes TEST data
# end clear space

# populate storage dictionary with VALID (hidden, answers) data
validListenersSongs = {} # same as listenersSongs, but only includes answers... 
validListenersSongsLists = {} # does not store percent played of each song

print "Populating validation storage at", datetime.datetime.now()
analysis_helpers.populateValidationStorage(hiddenData, validListenersSongs, validListenersSongsLists)

print "Evaluating results at", datetime.datetime.now()
# finally, evaluate results...
print "Mean average precision = ", analysis_helpers.calcMeanAveragePrecision(testListenersRecommendations, validListenersSongsLists)