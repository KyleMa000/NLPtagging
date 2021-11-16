# -*- coding: utf-8 -*-
"""
Created on Fri Sep 24 13:06:08 2021

@author: chime
"""

import sys


#Reading Development

f = open(str(sys.argv[1]), 'r', encoding = "UTF-8")

train = f.readlines()

f.close()

#Reading the Training

f = open(str(sys.argv[2]), 'r', encoding = "UTF-8")

train1 = f.readlines()

f.close()

train = train + train1

#Clean data
for i in range(len(train)):
    train[i] = train[i].split("\t")

for i in range(len(train)):
    if(train[i][0] != '\n'):
        train[i][1] = train[i][1].strip('\n') #remove \n following tags


#Training Stage
#Data gathering Stage
#Creat Likelihood and Transition and WordCounter Dictionary

Like = {}

Tran = {'B':{}}

Word = {}

Tag = {'B':0, 'ES':0}

#Filling up three tables
for i in range(len(train)):

    #WordCounter
    if(train[i][0] != '\n'):
        Word[train[i][0]] = Word.get(train[i][0], 0) + 1

    #TagCounter
    if(train[i][0] != '\n'):
        Tag[train[i][1]] = Tag.get(train[i][1], 0) + 1
    else:
        Tag['B'] += 1
        Tag['ES'] += 1

    #Likelihood
    if(train[i][0] != '\n'):
        if(train[i][1] not in Like):
            Like[train[i][1]] = {train[i][0] : 1}
        else:
            if(train[i][0] not in Like[train[i][1]]):
                Like[train[i][1]][train[i][0]] = 1
            else:
                Like[train[i][1]][train[i][0]] += 1

    #Transition
    #Handling the first B
    if(i == 0):
        Tran['B'][train[i][1]] = 1

    #When i = \n set next tag in B
    if(train[i][0] == '\n'):
        if(i+1 < len(train)):
            if(train[i+1][1] not in Tran['B']):
                Tran['B'][train[i+1][1]] = 1
            else:
                Tran['B'][train[i+1][1]] += 1

    #When i != \n
    else:
        #When i+ 1 != \n set next tag normally
        if(train[i+1][0] != '\n'):
            if(train[i][1] not in Tran):
                Tran[train[i][1]] = {train[i+1][1] : 1}
            else:
                if(train[i+1][1] not in Tran[train[i][1]]):
                    Tran[train[i][1]][train[i+1][1]] = 1
                else:
                    Tran[train[i][1]][train[i+1][1]] += 1
        #When i + 1 == \n set next tag as ES
        else:
            if(train[i][1] not in Tran):
                Tran[train[i][1]] = {'ES' : 1}
            else:
                if('ES' not in Tran[train[i][1]]):
                    Tran[train[i][1]]['ES'] = 1
                else:
                    Tran[train[i][1]]['ES'] += 1

#Converting Frequency to Probabilities
#Converting Likelihood
for key in Like:
    for k in Like[key]:
        Like[key][k] = Like[key][k] / Word[k]

#Converting Transitional
for key in Tran:
    for k in Tran[key]:
        Tran[key][k] = Tran[key][k] / Tag[k]


#Main Algorithm
#State Tag Array
def viterbi(Sentence):
    States = list(Tag.keys())
    
    length = len(Sentence)
    
    viterbi = [[0 for i in range(len(Sentence)+1)] for j in range(len(States))]
    backpointer = [[0 for i in range(len(Sentence)+1)] for j in range(len(States))]
    
    #Initialization
    for i in range(len(States)):
        if(Sentence[0] in Word):
            if((States[i] in Tran['B']) & (States[i] in Like)): 
                if(Sentence[0] in Like[States[i]]):
                    viterbi[i][0] = Tran['B'][States[i]] * Like[States[i]][Sentence[0]]
                else:

                    viterbi[i][0] = Tran['B'][States[i]] * 1/100000

            else:
                viterbi[i][1] = 0
                backpointer[i][1] = 0
        else:
            if(States[i] in Tran['B']):
                if(Sentence[0].endswith('s')):
                    viterbi[12][0] = 0.5       #hardcode end with s as NNS
                if(Sentence[0][0].isupper()):
                    viterbi[4][0] = 0.5        #hardcode start with cap as NNP
                if(any(m.isdigit() for m in Sentence[0])):
                    viterbi[5][0] = 1           #hardcode with numbers
                viterbi[i][0] = Tran['B'][States[i]] * 1/100000
    
    #Processing
    for i in range(1, len(Sentence)):
        for j in range(len(States)):
            #max previous state viterbi
            maxV = 0
            q = 0
            for x in range(len(States)):
                if maxV < viterbi[x][i - 1]:
                    q = x
                    maxV = viterbi[x][i - 1]
            #max current viterbi
            if(Sentence[i] in Word):
                if(States[q] in Tran):
                    if((States[j] in Tran[States[q]]) & (States[j] in Like)): #undone Like unknown word
                        if(Sentence[i] in Like[States[j]]):
                            backpointer[j][i] = q
                            viterbi[j][i] = maxV * Tran[States[backpointer[j][i]]][States[j]] * Like[States[j]][Sentence[i]]
                        else:

                            
                            backpointer[j][i] = q
                            viterbi[j][i] = maxV * Tran[States[backpointer[j][i]]][States[j]] * 1/100000
            else:
                if(States[j] in Tran[States[q]]):
                    if(Sentence[i].endswith('s')):
                        viterbi[12][i] = 0.5       #hardcode end with s as NNS
                    if(Sentence[i][0].isupper()):
                        viterbi[4][i] = 0.5        #hardcode start with cap as NNP
                    if(any(m.isdigit() for m in Sentence[i])):
                        viterbi[5][i] = 1           #hardcode with numbers
                    backpointer[j][i] = q
                    viterbi[j][i] = maxV * Tran[States[backpointer[j][i]]][States[j]] * 1/100000

    
    
    
    #ToEndState
    for i in range(len(States)):
        if(States[i] in Tran):
            if(States[1] in Tran[States[i]]):
                viterbi[i][length] = viterbi[i][length-1] * Tran[States[i]][States[1]]
    
    #Find Best Result
    a = 0
    b = 0
    for j in range(len(States)):
        if(viterbi[j][length] > b):
            b = viterbi[j][length]
            a = j

    #Return Best Result
    output = []
    output.append(States[a])
    for i in range(len(Sentence)-1, 0, -1):
        output.append(States[backpointer[a][i]])
        a = backpointer[a][i]
    
    output = list(reversed(output))
    return output


f = open(str(sys.argv[3]), 'r', encoding = "UTF-8")

test = f.readlines()

for i in range(len(test)):
    if(test[i]!='\n'):
        test[i] = test[i].strip("\n")

f.close()

input_list = test[0:25]

output = viterbi(input_list)


f = open('submission.pos', 'w', encoding = "UTF-8")

c = 0

States = list(Tag.keys())


while c < len(test):
    input_list = []
    print(c)
    while (test[c] != '\n'):
        input_list.append(test[c])
        c += 1
        if(c == len(test)):
            break
    c += 1
    print(input_list)
    output = viterbi(input_list)
    print(output)
    for j in range(len(input_list)):
        f.write(input_list[j] + '\t' + output[j]+'\n')
    f.write('\n')

f.close()


