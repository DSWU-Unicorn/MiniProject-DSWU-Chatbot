from tensorflow.keras.models import Model, load_model
from tensorflow.keras import preprocessing
import numpy as np
from utils.Preprocess import Preprocess

p = Preprocess(word2index_dic='../../train_tools/dict/chatbot_dict.bin',
               userdic='../../utils/user_dic.tsv')


new_sentence = '차관에서 공부할 곳'
new_sentence = '오늘 오전 13시 2분에 탕수육 주문 하고 싶어요'
new_sentence = "차미리사관 빈 강의실 어디야?"
new_sentence = "내일 오전 차미리사관 빈 강의실 어디야?"
new_sentence = '오늘 차관 비었어?'
new_sentence = "차관 오늘 이용할 수 있어?"
new_sentence = "차미리사관 어디로 가야해?"
pos = p.pos(new_sentence)
keywords = p.get_keywords(pos, without_tag=True)
new_seq = p.get_wordidx_sequence(keywords)
print(new_seq)

max_len = 40
new_padded_seqs = preprocessing.sequence.pad_sequences([new_seq], padding="post", value=0, maxlen=max_len)
print("새로운 유형의 시퀀스 : ", new_seq)
print("새로운 유형의 시퀀스 : ", new_padded_seqs)

# NER 예측
model = load_model('ner_model.h5')
p = model.predict(np.array([new_padded_seqs[0]]))
print(np.array([new_padded_seqs[0]]))
p = np.argmax(p, axis=-1) # 예측된 NER 인덱스 값 추출
print("p출력", p) # ============================== 여기서 부터 시작하기
print("{:10} {:5}".format("단어", "예측된 NER"))
print("-" * 50)
# index_to_ner = {1: 'O', 2: 'B_DT', 3: 'B_ROOM', 4: 'I', 5: 'B_OG', 6: 'B_PS', 7: 'B_LC', 8: 'NNP', 9: 'B_TI', 0: 'PAD', 10:'B_ROOM'}
index_to_ner = {1: 'O', 2: 'B_DT', 3: 'B_FOOD', 4: 'B_ROOM', 5: 'I', 6: 'B_OG', 7: 'B_PS', 8: 'B_LC', 9: 'NNP', 10: 'B_TI', 0: 'PAD'}
print(p) ##===
for w, pred in zip(keywords, p[0]):
    print("{:10} {:5}".format(w, index_to_ner[pred]))


# 새로운 유형의 시퀀스 :  [39, 214, 117, 194, 404, 3, 2, 9]
# 새로운 유형의 시퀀스 :  [[ 39 214 117 194 404   3   2   9   0   0   0   0   0   0   0   0   0   0
#     0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0   0
#     0   0   0   0]]