from stanfordcorenlp import StanfordCoreNLP
nlp = StanfordCoreNLP('/home/hongyi/stanford-corenlp-4.4.0',lang='en')
 
sentence='Tom who graduated from Tsinghua University is a good boy and now he works at Apple Inc.'
print(nlp.word_tokenize(sentence))
print(nlp.pos_tag(sentence))
print(nlp.ner(sentence))
print(nlp.parse(sentence))
print(nlp.dependency_parse(sentence))
nlp.close()

