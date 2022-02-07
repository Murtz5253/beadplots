import fitz
import re
from itertools import chain

def extract_paragraphs(page, page_no):
	"""
	Takes in a page and returns a list of the paragraphs after polishing them (see above function)
	in the page.
	"""
	all_block_data = page.get_text("blocks")
	# Lowercase everything upon extraction for simplicity
	paragraphs = [elem[4].lower() for elem in all_block_data] # Fourth element is where text is actually stored

	# Ensure we start at the abstract of the paper; email info and such not important; will handle title later
	# Might even just ask for the title, citations, + year of publication as input to the program later
	if page_no == 0:
		while 'abstract' not in paragraphs[0]:
			paragraphs.pop(0) # WRONG PLACE FOR THIS BECAUSE THIS GETS CALLED FOR ALL PAGES!
		# Now we only want the part after the abstract
		paragraphs[0] = f"abstract \n {paragraphs[0].split('abstract')[1]}"

	filtered_paragraphs = filter_paragraphs(paragraphs)
	polished_paragraphs = polish_paragraphs(filtered_paragraphs)
	return polished_paragraphs

def polish_paragraphs(paragraphs):
	"""
	Combines blocks that aren't actually separate paragraphs
	but were separated due to the ending of a column or page
	"""
	polished_paragraphs, i = [], 0
	while i < len(paragraphs):
		curr_block = paragraphs[i]

		# Check second-to-last element b/c last one is always newline character
		if curr_block[-2] in ['.', '?', '!'] or i == len(paragraphs) - 1: # want to append last paragraph for now regardless
			polished_paragraphs.append(curr_block)
			i += 1
		else:
			curr_block = curr_block[:-1] # remove the newline from the first block
			curr_block += paragraphs[i+1]
			polished_paragraphs.append(curr_block)
			i += 2 # This might not handle all cases (e.g a paragraph spanning >2 columns) but should handle most for now
	return polished_paragraphs

def filter_paragraphs(paragraphs):
	"""
	This function removes paragraphs that are unrelated to
	the paper's overall content.

	It calls multiple other functions, and is a work-in-progress.
	That is to say, as more papers are tested, more possibilities
	for irrelevant paragraphs will emerge, and a correspondent
	function will subsequently be added.
	"""

	# First function removes copyright detail paragraphs
	filtered_paragraphs = remove_copyright(paragraphs)
	return filtered_paragraphs

def remove_copyright(paragraphs):
	"""
	Removes paragraphs that just describe copyright
	details of the paper.
	"""

	copyright_removed = []

	# Most copyright paragraphs consist of both these terms/phrases in any order
	# Avoids removing paragraphs which might mention copyright or permissions briefly but have another purpose
	# However, this might not be the best approach in a paper in which the research is actually about copyright.

	# search_string1 = r"permission.*to.*copyrights"
	# search_string2 = r"copyright.*permission.*to" # Admittedly regex is not my strong suit
	for paragraph in paragraphs:
	# 	if 'permission to' in paragraph:
	# 		print("PARAGRAPH")
	# 		print(repr(paragraph))
	# 		print()
	# 		print(re.search(search_string1, paragraph, re.IGNORECASE))
	# 	check1 = re.search(search_string1, paragraph, re.IGNORECASE)
	# 	check2 = re.search(search_string2, paragraph, re.IGNORECASE)
		if 'permission to' in paragraph and 'copyright' in paragraph: # TEMP FIX I EVENTUALLY NEED TO FIGURE OUT REGEX
			print("REMOVED ONE")
			print(paragraph)
			continue
		else:
			copyright_removed.append(paragraph)
	return copyright_removed

def separate_sections(paragraphs):
	"""
	This function takes as input a list of POLISHED and FILTERED paragraphs
	and returns a dictionary where the keys are the section titles (e.g. 
	Abstract, Introduction, etc.) and the values are lists of paragraphs
	inside of that section.
	"""
	return




filename = './test_papers/DistributedMentoringCSCW2016.pdf'
doc = fitz.open(filename)
pages = [doc.load_page(i) for i in range(doc.page_count)]
# Below is a list of lists; each list consists of one page's paragraphs
all_paragraphs = [extract_paragraphs(pages[i], i) for i in range(len(pages))]
all_paragraphs = list(chain.from_iterable(all_paragraphs)) # Flatten into one paragraph list
all_paragraphs = polish_paragraphs(all_paragraphs) # This time, we call to combine single paragraphs separated by page

for i in range(len(all_paragraphs)):
	if all_paragraphs[i].split()[0] in ['abstract', 'introduction', 'conclusion']:
		print("PARAGRAPH {}".format(i))
		print(all_paragraphs[i])
		print()
		print()





































"""
CODE BELOW MAY PROVE USEFUL EVENTUALLY
"""

# # SOURCE: https://github.com/LouisdeBruijn/Medium/blob/master/PDF%20retrieval/pdf_retrieval.py
# from operator import itemgetter
# import fitz
# import json


# def fonts(doc, granularity=False):
#     """Extracts fonts and their usage in PDF documents.
#     :param doc: PDF document to iterate through
#     :type doc: <class 'fitz.fitz.Document'>
#     :param granularity: also use 'font', 'flags' and 'color' to discriminate text
#     :type granularity: bool
#     :rtype: [(font_size, count), (font_size, count}], dict
#     :return: most used fonts sorted by count, font style information
#     """
#     styles = {}
#     font_counts = {}

#     for page in doc:
#         blocks = page.getText("dict")["blocks"]
#         for b in blocks:  # iterate through the text blocks
#             if b['type'] == 0:  # block contains text
#                 for l in b["lines"]:  # iterate through the text lines
#                     for s in l["spans"]:  # iterate through the text spans
#                         if granularity:
#                             identifier = "{0}_{1}_{2}_{3}".format(s['size'], s['flags'], s['font'], s['color'])
#                             styles[identifier] = {'size': s['size'], 'flags': s['flags'], 'font': s['font'],
#                                                   'color': s['color']}
#                         else:
#                             identifier = "{0}".format(s['size'])
#                             styles[identifier] = {'size': s['size'], 'font': s['font']}

#                         font_counts[identifier] = font_counts.get(identifier, 0) + 1  # count the fonts usage

#     font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)

#     if len(font_counts) < 1:
#         raise ValueError("Zero discriminating fonts found!")

#     return font_counts, styles


# def font_tags(font_counts, styles):
#     """Returns dictionary with font sizes as keys and tags as value.
#     :param font_counts: (font_size, count) for all fonts occuring in document
#     :type font_counts: list
#     :param styles: all styles found in the document
#     :type styles: dict
#     :rtype: dict
#     :return: all element tags based on font-sizes
#     """
#     p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
#     p_size = p_style['size']  # get the paragraph's size

#     # sorting the font sizes high to low, so that we can append the right integer to each tag
#     font_sizes = []
#     for (font_size, count) in font_counts:
#         font_sizes.append(float(font_size))
#     font_sizes.sort(reverse=True)

#     # aggregating the tags for each font size
#     idx = 0
#     size_tag = {}
#     for size in font_sizes:
#         idx += 1
#         if size == p_size:
#             idx = 0
#             size_tag[size] = '<p>'
#         if size > p_size:
#             size_tag[size] = '<h{0}>'.format(idx)
#         elif size < p_size:
#             size_tag[size] = '<s{0}>'.format(idx)

#     return size_tag


# def headers_para(doc, size_tag):
#     """Scrapes headers & paragraphs from PDF and return texts with element tags.
#     :param doc: PDF document to iterate through
#     :type doc: <class 'fitz.fitz.Document'>
#     :param size_tag: textual element tags for each size
#     :type size_tag: dict
#     :rtype: list
#     :return: texts with pre-prended element tags
#     """
#     header_para = []  # list with headers and paragraphs
#     first = True  # boolean operator for first header
#     previous_s = {}  # previous span

#     for page in doc:
#         blocks = page.getText("dict")["blocks"]
#         for b in blocks:  # iterate through the text blocks
#             if b['type'] == 0:  # this block contains text

#                 # REMEMBER: multiple fonts and sizes are possible IN one block

#                 block_string = ""  # text found in block
#                 for l in b["lines"]:  # iterate through the text lines
#                     for s in l["spans"]:  # iterate through the text spans
#                         if s['text'].strip():  # removing whitespaces:
#                             if first:
#                                 previous_s = s
#                                 first = False
#                                 block_string = size_tag[s['size']] + s['text']
#                             else:
#                                 if s['size'] == previous_s['size']:

#                                     if block_string and all((c == "|") for c in block_string):
#                                         # block_string only contains pipes
#                                         block_string = size_tag[s['size']] + s['text']
#                                     if block_string == "":
#                                         # new block has started, so append size tag
#                                         block_string = size_tag[s['size']] + s['text']
#                                     else:  # in the same block, so concatenate strings
#                                         block_string += " " + s['text']

#                                 else:
#                                     header_para.append(block_string)
#                                     block_string = size_tag[s['size']] + s['text']

#                                 previous_s = s

#                     # new block started, indicating with a pipe
#                     block_string += "|"

#                 header_para.append(block_string)

#     return header_para


# def main():

#     document = './test_papers/DistributedMentoringCSCW2016.pdf'
#     doc = fitz.open(document)

#     font_counts, styles = fonts(doc, granularity=False)

#     size_tag = font_tags(font_counts, styles)

#     elements = headers_para(doc, size_tag)

#     for elem in elements:
#     	print("PARAGRAPH")
#     	print(elem)
#     	print()
#     	print()


# if __name__ == '__main__':
#     main()