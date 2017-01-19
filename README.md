# Collaborative-Filtering-Million-Song-Dataset
Written in Python; collaborative filtering on a music dataset (http://labrosa.ee.columbia.edu/millionsong/) containing 48 million user - song - playcount triplets.

The goal of the project is to, given half of the songs a user listened to, to guess the other half with the highest possible precision. 

### Results
Achieved a mean average precision of .1106, 5.32 times as precise as recommending by song popularity alone.

### Summary
I developed a collaborative filtering system, which calculates similarities between each pair of users based upon their listening histories. Then, in predicting the missing half of the listening history of a given user, the system looks for the most listened to songs by those users that are most similar to the current user. 

### Similarities between Users
For each pair of users, I took the set of songs that each user had listened to, and took the intersection of those two sets -- which provided the list of songs they had both listened to. For each song the pair of users had each listened to, I then took percentage of each user's total song play count this song accounted for, as well as each user's raw play count for this song.

Both seemed important in measuring similarity, as: 
+ 1) By looking at the percentage of plays in common, you can, in the extreme case, find users that only listened to songs that another user also listened to
+ 2) By looking at the play counts, you can get a sense of the reliability of the measurement. As if two listeners, B and C, both listened only to songs that listener A listened to (so they both have 100% of plays in common), but listener B only played 1 song 1 time, whereas listener C's total play count is much greater, we can be more confident in saying that listener C and listener A are very similar (and less so regarding listeners B and A).

### Next Steps
I am working on also looking at song to song similarities -- in addition to the user to user similarities I am currently using. This seems like it would only increase precision, as there may be cases a certain song is listened to by many of the same people to the same degree as another song. This strength of these song to song relationships may get lost in user to user similarities.

For song to song similarities, one option I am considering is a Bayesian approach (building off of http://www.math.unipd.it/~aiolli/PAPERS/paperIIR.pdf), looking at the conditional probability a user listened to one song given that he or she listened to another. This would likely accurately capture the relationship between the probabilities of listening to, say a less popular song and a more popular song by the same artist. A user that we know listened to a B-side of a certain artist, I would guess, is very likely to have listened to that artist's most popular tune. However, going the other direction -- knowing that a user listened to an artist's most popular tune would not seem to suggest to a very high degree that the user also listened to the artist's B-sides. In other words, the probabilities are not symmetric, and the conditional probability here seems to handle this well.
