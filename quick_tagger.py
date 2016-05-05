#author: Kyle Wiese
#CSCI 5832
#Programming Assignment 3 (Part 2)

import sys
import math
import collections

word_counts = {}
word_pos_counts = {}
pos_bigrams = {}
pos_counts = {}
transition_prob = {}
word_probs = {}
total = 0
number_right = 0

#train model
def train(tagged_sents):
	global word_counts
	global word_pos_counts
	global pos_bigrams
	global pos_counts

	pos_counts["<s>"] = 0
	pos_counts["<\s>"] = 0

	word_counts["<s>"] = 0
	word_counts["<\s>"] = 0

	prev_pos = "<s>"
	for sentence in tagged_sents:
		for comb in sentence:
			current_pos = comb[1]
			word = comb[0]
			combination = word + " " + current_pos
			pos_bigram = prev_pos + " " + current_pos

			if word not in word_counts:
				word_counts[word] = 1
			else:
				word_counts[word] = word_counts[word] + 1

			if current_pos not in pos_counts:
				pos_counts[current_pos] = 1
			else:
				pos_counts[current_pos] = pos_counts[current_pos] + 1

			if combination not in word_pos_counts:
				word_pos_counts[combination] = 1
			else:
				word_pos_counts[combination] = word_pos_counts[combination] + 1

			if pos_bigram not in pos_bigrams:
				pos_bigrams[pos_bigram] = 1
			else:
				pos_bigrams[pos_bigram] = pos_bigrams[pos_bigram] + 1

			prev_pos = current_pos

		current_pos = "<\s>"
		pos_bigram = prev_pos + " " + current_pos
		if pos_bigram not in pos_bigrams:
			pos_bigrams[pos_bigram] = 1
		else:
			pos_bigrams[pos_bigram] = pos_bigrams[pos_bigram] + 1
		prev_pos = "<s>"

		pos_counts["<s>"] = pos_counts["<s>"] + 1
		pos_counts["<\s>"] = pos_counts["<\s>"] + 1

		word_counts["<s>"] = word_counts["<s>"] + 1
		word_counts["<\s>"] = word_counts["<\s>"] + 1
			

	calculateProb()

#calculate needed probabilities
def calculateProb():
	global word_counts
	global word_pos_counts
	global pos_bigrams
	global pos_counts

	global transition_prob
	global word_probs

	#calculate the probability of p(word|tag)
	for combination in word_pos_counts:
		both = combination.split()
		tag = both[1]
		prob = 0
		prob = math.log10(word_pos_counts[combination]/float(pos_counts[tag]))
		word_probs[combination] = prob
	
	#calculate the probability of p(tag|tag) 
	for bigram in pos_bigrams:
		both = bigram.split()
		first_pos = both[0]
		#prob = math.log10((pos_bigrams[bigram] + .01) / (pos_counts[first_pos] + (.01 * len(pos_counts))))
		prob = math.log10(pos_bigrams[bigram]/float(pos_counts[first_pos]))
		transition_prob[bigram] = prob

#get the max value out of hash map
def getMax(d):
	maximum = float('-inf')
	key = "undefined"
	for i in d:
		if d[i] > maximum:
			maximum = d[i]
			key = i
	return key		

#runs testfile

def eval(gold_sentences):
	global total
	global number_right

	for gold_sentence in gold_sentences:
		test_sentence = []
		for word in gold_sentence:
			test_sentence.append(word[0])
		eval_sentence(test_sentence, gold_sentence)
	return(number_right/float(total))


def eval_sentence(test_sentence, gold_sentence):
	global word_counts
	global word_pos_counts
	global pos_bigrams
	global pos_counts

	global transition_prob
	global word_probs

	global total
	global number_right

	tagged_sentence = viterbi(test_sentence)
	tagged_pos = []
	for word in tagged_sentence:
		combination = word.split()
		tagged_pos.append(combination[1])
	for i in xrange(0,len(gold_sentence) - 1):
		combination = gold_sentence[i]
		if combination[1] == tagged_pos[i]:
			number_right += 1
		total += 1

def viterbi(sentence):
	global word_counts
	global word_pos_counts
	global pos_bigrams
	global pos_counts

	global transition_prob
	global word_probs

	curr_column_prob = {}
	prev_column_prob = {"<s>":0}
	prev_pos = ["<s>"]
	curr_pos = []
	input_words = []
	backtrace = []

	for word in sentence:
		#add word to list containing the words for the sentence
		input_words.append(word)
		#if word has not been seen before, make p(word|tag) 1 for every possible tag and add those tags to the current column's pos list
		if word not in word_counts:
			for pos in pos_counts:
				combination = word + " " + pos
				word_probs[combination] = 0
				curr_pos.append(pos)
				curr_column_prob[pos] = word_probs[combination]

		#otherwise,grab p(word|tag) and append the relevant tags and add them to the current column's pos list
		else:
			for pos in pos_counts:
				combination = word + " " + pos
				if combination in word_probs:
					curr_column_prob[pos] = word_probs[combination]
					curr_pos.append(pos)
				#else:
				#	curr_column_prob[pos] = float('-inf')
				#curr_pos.append(pos)

		#Find and calculate the max probability for each tag with respect to the current word
		for ctag in curr_pos:
			local_possibilities = {}
			for ptag in prev_pos:
				trans = ptag + " " + ctag
				if trans in transition_prob:
					local_possibilities[ptag] = transition_prob[trans] + prev_column_prob[ptag]
				else:
					local_possibilities[ptag] = math.log10(.01/(pos_counts[ptag]+(.01*len(pos_counts)))) + prev_column_prob[ptag]
			
			key = getMax(local_possibilities)
			#add max to back trace
			if key != "undefined":
				curr_column_prob[ctag] = local_possibilities[key] + curr_column_prob[ctag]
				backtrace.append((ctag, key))

		#mark end of word in backtrace list
		backtrace.append("column done")

		#if not end of sentence, reset only for next word 
		prev_column_prob = curr_column_prob
		curr_column_prob = {}
		prev_pos = curr_pos
		curr_pos = []
	#end of sentence reached, calculate output and reset for next sentence
	

	end_pos = []
	backtrace.append(("</s>",backtrace[len(backtrace)-2][0]))
	go_to = "</s>"
	next_column = 1
	i = 1
	for element in reversed(backtrace):
		if element == "column done":
			next_column = 1
			continue
		if next_column == 1:
			if element[0] == go_to:
				go_to = element[1]
				if go_to != "<s>":
					end_pos.append(go_to)
				next_column = 0
		i = i + 1

	end_pos.reverse()
	return_list = []
	for x in range(0, len(input_words) - 1):
		out_line = input_words[x] + " " + end_pos[x]
		return_list.append(out_line)
	#return_list
	return return_list

def main():

	train()
	test()

if __name__ == "__main__":
	main()
