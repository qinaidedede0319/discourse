#!/bin/bash

# 文本分类
malletPath="/home/hongyi/discourse/Mallet-2.0.8RC2"
mallet=$malletPath/bin/mallet
inputDir=$malletPath/sample-data/web/en/
outputDir="./test/cc.mallet"
outputCls="./test/cc.classifier"
testFile=$malletPath/sample-data/web/en/elizabeth_needham.txt
resultFile="./test/result_file.txt"

# 将源文件txt格式转换为mallet自己的处理格式
$mallet import-dir --input $inputDir --output $outputDir
# 使用mallet算法库中的NaiveBayes算法训练获得分类器
$mallet train-classifier --input $outputDir --trainer NaiveBayes --training-portion 0.8 --output-classifier $outputCls
# 使用分类器测试新数据集
$mallet classify-file --input $testFile --output $resultFile --classifier $outputCls
