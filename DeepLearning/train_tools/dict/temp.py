import csv
with open('./question.csv', newline='', encoding='utf-8') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in spamreader:

        # print('0000\t' +' '.join(row) + '\t5')
        print(' '.join(row) + ",5")