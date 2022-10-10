# open("output_ner_train.txt", "r", encoding='utf-8')
word = ['차미리사관', '차미리사', '차미리관', '차미리', '미리관', '미리사', '차관', '차']
output_list = []
with open("output_ner_train.txt", "r", encoding='utf-8') as f:
    for i in f:
        if '$' in i:
            for w in word:
                if w in i:
                    i = i.replace(w, '<'+w+':ROOM>')
                    output_list.append(i)
                    # print(i)
                    break


fr = open("output_ner_train.txt", 'r', encoding='utf-8')
lines = fr.readlines()
# print(lines)

fw = open("output_ner_train3.txt", 'w', encoding='utf-8')
cnt = 0
for line in lines:
    if '$' in line:
        # print(line)
        line = line.replace(line, output_list[cnt])
        # fw.write(line.replace(line, output_list[cnt]))
        cnt += 1

    fw.write(line)
    # print(line)
    # else:
    #     break

fw.close()
fr.close()


