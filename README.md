# Collaborative-Filtering-Million-Song-Dataset
Written in Python; collaborative filtering on a music dataset containing 48 million user - song - playcount triplets.

An updated algorithm to my 1st attempt -- which used conditional probability for song-song filtering and a custom similarity measure for listener-listener filtering, yielding a mean average precision of .1106, 5.32 times as precise as recommending by song popularity. 

This version first compares listeners, using the same similarity measure as v1 -- for two dictionaries of items, for each key that is in both dictionaries: smaller = smaller of values of dictionary 1 and dictionary 2, larger = ditto, but larger of the two, and returns smaller + ((smaller / larger) * (larger - smaller)). 

For each pair of listeners, it does this comparison for each song the 2 listeners have in common, and the percent of each listener's total play count the song accounts for, and then repeats the procedure with play counts, rather than percents of play counts (my thoughts here being that, percentages of a listener's total play count are relevant as a listener that listened to every song, by play count alone would look similar to every other user, and yet, play counts are relevant too as a reliability measure: i.e. say the dictionaries for listeners A, B, and C all look like {song1 : 100%}. If listeners A and B each listened to the song 50 times, and listener C only listened to it once, we would be more confident in saying listeners B and A are more similar than C and A. 

The code also uses mean average precision (of 2 ordered lists of songs, each describing 1 listener's listening history) to compare the songs two listeners have in common, and leaves open the possibility to alter the weights of this vs. the method described above. 

Finally, after looking at songs a given pair of listeners have both listened to, it looks at, for those songs listener A listened to than B did not, and vice-versa, how similar or different those songs are to songs the other listener listened to.

The idea is, if person1 listened to 4 Beatles songs, and person2 listened to 3 of the same Beatles songs and 1 other Beatles song that person 1 didn't listen to, and person3 listened to 3 of the same Beatles songs as person1 and 1 Mozart tune, without knowing they are Beatles songs, you should be able to tell that person1 and person2 are more similar than person1 and person3. We can do this by looking at the dictionaries of which listeners listened to which songs, with similar songs having many of the same listeners with similar play percents / play counts (same expression as above).

And as in v1, the code prunes listeners below x% of listenerB's similarity to listenerA, where listenerB is the most similar listener to listenerA. (In v1, x = 30 yielded the best resutls -- that is, not considering song recommendations from listeners whose similarity to a given listener is less than 30% of the similarity of the most similar listener. The idea here being that for any listener, there will likely be a disproportionately large # of listeners that are not very similar to him, yet aggregating the influence of all of these not very similar listeners will overpower the influence of a few very similar listeners.

Currently running with test data.
