#! /bin/bash
root=`pwd`
echo $root
bin=$root/../bin
dir=$root/data/news_content

mkdir -p $diri
cd $dir

# 1. UCI format to libsvm format
python $root/text2libsvm_new.py $dir/docword.news_content.txt $dir/vocab.news_content.txt $dir/news_content.libsvm $dir/news_content.word_id.dict

# 2. libsvm format to binary format
$bin/dump_binary $dir/news_content.libsvm $dir/news_content.word_id.dict $dir 0

# 4. Run LightLDA
$bin/lightlda -num_vocabs 15984962 -num_topics 500 -num_iterations 10 -alpha 0.1 -beta 0.01 -mh_steps 2 -num_local_workers 1 -num_blocks 1 -max_num_document 4800000 -input_dir $dir -data_capacity 800
