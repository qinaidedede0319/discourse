import json

test_file = "/home/hongyi/stanford-corenlp-4.4.0/t.json"
f = open(test_file,"r")

data = json.load(f)

dep_dict = {"compound":"nn","obj":"dobj","nummod":"num"}

# print(data)

def basicDependencies2dependencies(basicDependencies):
    dependencies = []
    for tmp_d in basicDependencies:
        dep = tmp_d["dep"].lower().split(":")[-1]
        if dep in dep_dict:
            dep = dep_dict[dep]
        # if dep not in ["punct","acl"]:
        govern = "{}-{}".format(tmp_d["governorGloss"].replace("ROOT","root"),tmp_d["governor"])
        depend = "{}-{}".format(tmp_d["dependentGloss"].replace("ROOT","root"),tmp_d["dependent"])
        tmp_l = [dep,govern,depend]
        dependencies.append(tmp_l)
    dependencies = sorted(dependencies,key=lambda x:int(x[2].split("-")[-1]))
    return dependencies

def parse2parsetree(parse):
    tmptree = parse.replace("ROOT\n ","")
    tmptree = tmptree.replace("\n","")
    parsetree = ""
    for i in range(len(tmptree)):
        if tmptree[i]!=" ":
            parsetree+=tmptree[i]
        else:
            if i>0 and tmptree[i-1]!=" ":
                parsetree+=tmptree[i]
    return parsetree

def tokens2words(tokens_full):
    words_full = []
    for tokens in tokens_full:
        word = tokens["word"]
        tmp_d = {}
        tmp_d["CharacterOffsetBegin"] = tokens["characterOffsetBegin"]
        tmp_d["CharacterOffsetEnd"] = tokens["characterOffsetEnd"]
        tmp_d["PartOfSpeech"] = tokens["pos"]
        words = [word,tmp_d]
        words_full.append(words)
    return words_full

out = {}
docId = data["docId"]
out[docId]={"sentences":[]}
sentences = data["sentences"]
for d in sentences:
    basicDependencies = d["basicDependencies"]
    dependencies = basicDependencies2dependencies(basicDependencies)
    parse = d["parse"]
    parsetree = parse2parsetree(parse)
    tokens = d["tokens"]
    words = tokens2words(tokens)
    out[docId]["sentences"].append({"dependencies":dependencies,"parsetree":parsetree,"words":words})
    
print(out)
with open("t.json","w") as f:
    json.dump(out,f)
    print("加载入文件完成...")
    # for k,v in d.items():
    #     print(k,v)
