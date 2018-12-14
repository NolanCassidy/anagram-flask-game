#Vocabulary anagrams game for primary school English language learners

A simple anagram game designed for English-language learning students in elementary and middle school. Students are presented with a list of vocabulary words (taken from a text file) and an anagram. The anagram is a jumble of some number of vocabulary words, randomly chosen. Students attempt to type words that can be created from the jumble. When a matching word is typed, it is added to a list of solved words.

The vocabulary word list is fixed for one invocation of the server, so multiple students connected to the same server will see the same vocabulary list but may  have different anagrams.

* AJAX in the frontend (vocab.html)
* Logic in the backend (flask_vocab.py)
* Frontend to backend interaction (with correct requests/responses) between vocab.html and flask_vocab.py

Live updating on webpage to show tiles for letters entered by user.
