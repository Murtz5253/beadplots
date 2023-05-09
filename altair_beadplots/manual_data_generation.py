import pandas as pd
import numpy as np
import altair as alt
import approximate_keyword_search as aks

from collections import OrderedDict
from transformers import pipeline


def fill_nulls(col):
	"""
	This function repeats the values of shorter sections so that all
	sections of the paper have the same number of rows, allowing a
	DataFrame with consistent values to be formed, which in turn
	allows for a proper BeadPlot.
	"""
	vals = col[~col.isnull()].values
	vals = np.resize(vals, len(col)) # this will cause the numbers to just repeat, as desired
	return vals

def replace_text_and_fill_nulls(col):
	"""
	This is almost the same as the above function, except it also
	replaces the text with numbers. The resulting DataFrame is the
	one actually used to make the BeadPlot (because I want paragraph
	numbers on the x-axis), whereas the other DataFrame is used to
	compute values for the approximate keyword search.
	"""
	vals = col[~col.isnull()].values
	vals = [i for i in range(len(vals))] # replace with numbers for ease of processing
	vals = np.resize(vals, len(col)) # this will cause the numbers to just repeat, as desired
	return vals

def make_csv(filename, section_dict, list_keywords, is_phrase=False):
	data_dict = dict([ (k,pd.Series(v)) for k,v in section_dict.items() ])
	data = pd.DataFrame(data_dict)
	data_replaced = data.apply(replace_text_and_fill_nulls, axis=0) # need a replaced version to get paragraph count post-algorithm
	data = data.apply(fill_nulls, axis=0) # Repeat values to remove nulls so beadplot can be formed
	long_form_data = data.melt(var_name='Section', value_name='Paragraph')
	long_form_data_replaced = data_replaced.melt(var_name='Section', value_name='Paragraph')

	if is_phrase: # different algorithm for phrases
		classifier = pipeline("zero-shot-classification")
		sequences = list(long_form_data['Paragraph']) # we will classify the word for each
		candidate_label = list_keywords # if a phrase, this will just be the phrase as one string in the list

		# The below is a list of dictionaries, where each dictionary has three keys: 1) labels, 2) scores, 3) sequence
		output = classifier(sequences, candidate_label)
		# I want the scores in order as a list for the algorithm_raw_score
		# each scores list has one value, because I have one candidate label
		scores = [nested_dict['scores'][0] for nested_dict in output]
		long_form_data['algo_score_raw'] = scores
	else:
		edit_distance = list_keywords[0].count(' ') # one more edit than the number of spaces allowed, so scales with phrase
		algo_func = lambda paragraph : aks.count_all_matches(list_keywords, paragraph, edit_distance=edit_distance)
		long_form_data['algo_score_raw'] = long_form_data['Paragraph'].apply(algo_func)

	# min-max normalize the column data
	# long_form_data['algo_score_normalized'] = (long_form_data['algo_score_raw'] - long_form_data['algo_score_raw'].min())\
	# 										/(long_form_data['algo_score_raw'].max()-long_form_data['algo_score_raw'].min())\
	# 										+ 0.2 # so all marks show up

	# Now that all the stuff is computed, can replace actual text with paragraph numbers
	long_form_data['Paragraph'] = long_form_data_replaced['Paragraph']
	# third command-line arg is the output path to CSV
	output_file = f"{filename}-{'-'.join(list_keywords)}.csv"
	filename = f"./output/{output_file}"
	long_form_data.to_csv(filename)
	return filename

def generate_beadplot(data_csv, title, num_citations):
	data = pd.read_csv(data_csv)
	# data['algo_score_raw'] = data['algo_score_raw'].replace({0: -1})
	# display(data)
	# First generate base graph

	tick_count = len(set(data['algo_score_raw']))
	tick_count = min(10, tick_count) # need to reduce the legend size for the manual ones
	tick_count = 7 # temporary manual one to make differences easier to see
	base = alt.Chart(data).mark_circle(opacity=1, stroke='#4c78a8').encode(
		x=alt.X('Paragraph:N', axis=alt.Axis(labelAngle=0, labelFontSize=21)),
		y=alt.Y('Section:N', axis=alt.Axis(labelFontSize=23), sort=list(OrderedDict.fromkeys(data['Section']))),
		size=alt.Size('algo_score_raw:Q', scale=alt.Scale(range=[0, 1800]), title="Probability of Match", legend=alt.Legend(tickCount=tick_count)), # ordinal variable type so legend not continuous
	).properties(
		title = alt.TitleParams(
			[f"{title}, {num_citations} Citations"],
			fontSize=30,
			offset=10
		),
		width=1200,
		height=500
	)
	
	# Next generate the overlying graph with the lines
	
	lines = alt.Chart(data).mark_rule(stroke='#4c78a8').encode(
		x=alt.X('Paragraph:N', axis=alt.Axis(labelAngle=0)),
		y=alt.Y('Section:N', sort=list(OrderedDict.fromkeys(data['Section'])))
	).properties(
		width=1200,
		height=500
	)
	if max(data['algo_score_raw']) == 0:
		final_chart = lines # no beads if no matches
		final_chart = final_chart.configure_legend(
			titleFontSize=17,
			labelFontSize=17
		).configure_axis(
			labelFontSize=18,
			titleFontSize=25
		)
		return final_chart
	else:
		final_chart = base + lines
		final_chart = final_chart.configure_legend(
			titleFontSize=18,
			labelFontSize=18
		).configure_axis(
			titleFontSize=25
		)
		return final_chart

def generate_bitcoin(keyword):
	path = './test_papers_text/bitcoin'
	section_dict = {'abstract': list(),
					'introduction': list(),
					'research_framework': list(),
					'reflection': list(),
					'conclusion': list()
					}
	for key in section_dict:
		filepath = f"{path}/{key}.txt"
		f = open(filepath, 'r', encoding="utf8")
		for line in f.readlines():
			if line == '\n':
				continue
			else:
				section_dict[key].append(line)
		f.close()

	if " " in keyword: # checking if a phrase
		filename = make_csv('bitcoin', section_dict, [keyword], is_phrase=True)
	else:
		list_keywords = list(aks.get_keyword_synonyms(keyword)) # ask user for words related to second command-line arg
		filename = make_csv('bitcoin', section_dict, list_keywords)

	chart = generate_beadplot(filename, "Exploring Trust in Bitcoin Technology: A Framework for HCI Research", 69)

def generate_driving(keyword):
	path = './test_papers_text/driving'
	section_dict = {'abstract': list(),
					'introduction': list(),
					'related_work': list(),
					'experimental_setup': list(),
					'results': list(),
					'discussion': list(),
					'results': list(),
					'limitations': list(),
					'summary': list(),
					'conclusion': list()
					}
	for key in section_dict:
		filepath = f"{path}/{key}.txt"
		f = open(filepath, 'r', encoding="utf8")
		for line in f.readlines():
			if line == '\n':
				continue
			else:
				section_dict[key].append(line)
		f.close()

	if " " in keyword: # checking if a phrase
		filename = make_csv('driving', section_dict, [keyword], is_phrase=True)
	else:
		list_keywords = list(aks.get_keyword_synonyms(keyword)) # ask user for words related to second command-line arg
		filename = make_csv('driving', section_dict, list_keywords)

	chart = generate_beadplot(filename, "Explain Yourself! Transparency for Positive UX in Autonomous Driving", 3)
	#chart.save("./driving.png")
	chart.show()

def generate_ethnography(keyword):
	path = './test_papers_text/ethnography'
	section_dict = {'abstract': list(),
					'introduction': list(),
					'ref_terms': list(),
					'joining_dots': list(),
					'coloring_dots': list(),
					'conclusion': list()
					}
	for key in section_dict:
		filepath = f"{path}/{key}.txt"
		f = open(filepath, 'r', encoding="utf8")
		for line in f.readlines():
			if line == '\n':
				continue
			else:
				section_dict[key].append(line)
		f.close()

	if " " in keyword: # checking if a phrase
		filename = make_csv('ethnography', section_dict, [keyword], is_phrase=True)
	else:
		list_keywords = list(aks.get_keyword_synonyms(keyword)) # ask user for words related to second command-line arg
		filename = make_csv('ethnography', section_dict, list_keywords)

	chart = generate_beadplot(filename, "Anticipatory Ethnography: Design Fiction as an Input to Design Ethnography", 64)
	chart.show()

def generate_women_hci(keyword):
	path = './test_papers_text/women_hci'
	section_dict = {'abstract': list(),
					'introduction': list(),
					'related_work': list(),
					'background': list(),
					'methodology': list(),
					'findings': list(),
					'discussion': list(),
					'conclusion': list()
					}
	for key in section_dict:
		filepath = f"{path}/{key}.txt"
		f = open(filepath, 'r', encoding="utf8")
		for line in f.readlines():
			if line == '\n':
				continue
			else:
				section_dict[key].append(line)
		f.close()

	if " " in keyword: # checking if a phrase
		filename = make_csv('women_hci', section_dict, [keyword], is_phrase=True)
	else:
		list_keywords = list(aks.get_keyword_synonyms(keyword)) # ask user for words related to second command-line arg
		filename = make_csv('women_hci', section_dict, list_keywords)

	chart = generate_beadplot(filename, "The Unexpected Entry and Exodus of Women in Computing and HCI in India", 29)
	chart.show()




