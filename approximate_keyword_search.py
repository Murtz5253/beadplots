import regex # This has a few more features than just re--specifically, approximate string matching.
import time
from nltk.corpus import wordnet, stopwords

def count_matches(keyword_phrase, paragraph, edit_distance=1):
	"""
	This function takes in two strings and conducts an approximate
	string match, looking for the first string in the second.

	For the purposes of this program, it takes in a keyword/phrase
	as the first string, and a paragraph a the second string,
	counting the number of times the keyword/phrase appears in
	the paragraph. The match is fuzzy to whatever extent is
	specified by the edit distance

	Default edit distance is 1 for now because any higher seems
	to result in irrelevant matches. May change later.
	"""

	# Create pattern with edit distance allowance
	pattern = f"({keyword_phrase}){{e<={edit_distance}}}" # double brackets excape the bracket
	matches = regex.findall(pattern, paragraph)
	return len(matches)

def count_all_matches(list_keywords, paragraph, edit_distance=1):
	"""
	This function effectively calls the above function on a list
	of keywords and returns the total number of matches.

	This returns a SINGLE integer and not a list because it is
	designed to be used with a list of words that are all
	synonyms and contribute to the algorithm score of a given
	paragraph in a BeadPlot.
	"""
	return sum([count_matches(keyword, paragraph, edit_distance) \
				for keyword in list_keywords])

def get_synonyms(word):
	"""
	This function produces a set of synonyms for a word from the
	NLTK wordnet corpus.
	"""
	synonyms = set()
	for syn in wordnet.synsets(word):
		for l in syn.lemmas():
			synonyms.add(l.name()) # avoid duplicates
	return synonyms


def get_keyword_synonyms(keyword):
	"""
	This function produces a set of synonyms for the input keyword
	using NLTK's wordnet corpus. It presents the synonyms to the
	user and asks the user to select the ones they would like to
	be included in the algorithm calculation for their BeadPlot.
	"""
	synonyms = get_synonyms(keyword)

	selected_words = [keyword]
	print("The following words have been identified as additional\
			related/relevant keywords as per your query.")
	print(synonyms, end="\n\n")
	time.sleep(3)
	print("One by one, please enter the words you would like to be included\
			in the match score for the generation of your BeadPlot. When you\
			have finished your selection, please enter the * key.")

	curr_word = str()
	while curr_word != '*':
		curr_word = input("Enter word: ")
		if curr_word != '*':
			selected_words.append(curr_word)

	print("Thank you. Your BeadPlot will be generated shortly.")
	return selected_words

def find_all_combinations(list_of_lists, i, string_so_far, combinations_list):
	"""
	Recursively finds all combinations of the list of lists, maintaining the
	order of the lists.
	"""
	if i == len(list_of_lists) - 1: # i.e. we are on the last list:
		for string in list_of_lists[i]:
			final_string = f"{string_so_far} {string}"
			combinations_list.append(final_string.lstrip()) # remove the extra space from first addition
	else:
		for string in list_of_lists[i]:
			find_all_combinations(list_of_lists, i + 1, f"{string_so_far} {string}", combinations_list)

def get_keyphrase_synonyms(keyphrase):
	"""
	This function works similarly to the above one, except
	it gets "synonyms" for multi-word phrases and asks the
	user which ones they would like to use.

	Applies the following algorithm:

	1) Tokenize phrase into individual words
	2) Run synonyms search on words independently except on stopwords
	3) Maintaining ordering of terms, present all possible combinations
	   of synonyms as "synonym phrases" for the user to choose from.
	4) Present 10 at a time, asking user if they would like to see more.
	"""

	# Eventual output
	selected_phrases = [keyphrase]

	# Set up the nested list of synonyms
	tokens = keyphrase.split()
	tracking_list = list()
	for token in tokens:
		tracking_list.append([token]) # can identify original word by first element of list
		if token not in stopwords.words('english'):
			tracking_list[-1].extend(list(get_synonyms(token)))
	
	# Get all combinations into a new list
	combinations_list = list()
	find_all_combinations(tracking_list, 0, str(), combinations_list)

	# Show to user and have them select
	print("The following phrases have been identified as the first 10\
			related/relevant phrases as per your query.")
	tracker = iter(combinations_list) # get an iterator over the combinations
	for _ in range(10):
		try:
			print(next(tracker))
		except StopIteration:
			print("There are no more related phrases.")

	time.sleep(3)
	print("One by one, please enter the phrases you would like to be included\
			in the match score for the generation of your BeadPlot. When you\
			have finished your selection, please enter the * key. If you would\
			like to see more options, please enter the > key.")
	curr_phrase = str()
	while curr_phrase != '*':
		curr_phrase = input("Enter phrase: ")
		if curr_phrase == '>':
			for _ in range(10):
				try:
					print(next(tracker))
				except StopIteration:
					print("There are no more related phrases.")
		elif curr_phrase != '*':
			selected_phrases.append(curr_phrase)

	print("Thank you. Your BeadPlot will be generated shortly.")
	return selected_phrases


