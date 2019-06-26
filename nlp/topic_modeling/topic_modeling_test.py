# -*- coding: utf-8 -*-

from topic_modeling.topic_model import TopicModelTrain, TopicModelUse
# from topic_model import TopicModelTrain, TopicModelUse
# from topic_modeling.evaluate.lda import EvaluateLDA
# from topic_modeling.evaluate.evaluate_model import EvaluateLDAMOdel

saving_path = "/home/abhishek/python/topic_modeling/topic_modeling/models/malayalam_model/"
dir_path = "/home/abhishek/python/malayalam_tm/dataset/test_corpus/topstories"

def training():
	train_model_obj = TopicModelTrain(TopicModelTrain.MALAYALAM, TopicModelTrain.LDA, dir_path)

	#generating corpus
	train_model_obj.generate_corpus()
	train_model_obj.save(saving_path=saving_path, file_type='dictionary')
	train_model_obj.save(saving_path=saving_path, file_type='corpus')

	#train_model
	train_model_obj.train(ntops=20)
	train_model_obj.save(saving_path=saving_path, file_type='model')


	#similarity_index
	train_model_obj.similarity_index()
	train_model_obj.save(saving_path=saving_path, file_type='model_similarity_index')



def use_model():
	use_topic_model_obj = TopicModelUse(TopicModelUse.MALAYALAM, TopicModelUse.LDA, saving_path)

	#load model
	use_topic_model_obj.load()

	# show topics either single or all topics
	topics = use_topic_model_obj.get_topics(topicid=17, topn=5, num_topics=10)

	text = """ ചെന്നൈ: ആര്‍എസ്എസിനെയും ബിജെപിയെയും നേരിടുന്നതിന് താന്‍ ഭഗവത് ഗീതയും ഉപനിഷത്തുകളും പഠിക്കുകയാണെന്ന് കോണ്‍ഗ്രസ് ഉപാധ്യക്ഷന്‍ രാഹുല്‍ ഗാന്ധി. ചെന്നൈയില്‍ കോണ്‍ഗ്രസ് പ്രവര്‍ത്തകരുടെ യോഗത്തെ അഭിസംബോധനചെയ്ത് സംസാരിക്കവെയാണ് രാഹുല്‍ ഗാന്ധി ഇക്കാര്യം പറഞ്ഞത്.
എല്ലാവരെയും ഒരുപോലെ കാണണമെന്നാണ് ഉപനിഷത്തുകള്‍ പറയുന്നത്. അതിനു വിരുദ്ധമായി ജനങ്ങളെ അടിച്ചമര്‍ത്തുകയാണ് ആര്‍എസ്എസുകാര്‍ ചെയ്യുന്നതെന്ന് രാഹുല്‍ ഗാന്ധി പറഞ്ഞു. ബിജെപിക്ക് ഇന്ത്യയെ മൗലികമായി മനസ്സിലാക്കാന്‍ സാധിച്ചിട്ടില്ല. അവര്‍ക്ക് ആകെ മനസ്സിലാകുന്നത് ആര്‍എസ്എസ് തലസ്ഥാനത്തുനിന്നുള്ള നിര്‍ദ്ദേശങ്ങള്‍ മാത്രമാണെന്നും അദ്ദേഹം പറഞ്ഞു.
പ്രപഞ്ചത്തിലെ എല്ലാ അറിവുകളും വരുന്നത് പ്രധാനമന്ത്രി നരേന്ദ്ര മോദിയില്‍നിന്നാണെന്നാണ് ബിജെപിക്കാര്‍ കരുതുന്നത്. രാജ്യത്തിനു മേല്‍ ഒരേ ആശയം അടിച്ചേല്‍പ്പിക്കാനാണ് ബിജെപിയുടെ ശ്രമം. എല്ലാ വ്യക്തികള്‍ക്കും അവരുടേതായ അഭിപ്രായം പറയാനും വിയോജിപ്പ് പ്രകടിപ്പിക്കാനുമുള്ള അവകാശമുണ്ട്. തമിഴ് സിനിമകളിലൂടെയും  പുസ്തകങ്ങളിലൂടെയും തമിഴ്‌നാടിന്റെ സംസ്‌കാരത്തെ അടുത്തറിയാന്‍ താന്‍ ശ്രമിക്കുകയാണെന്നും അദ്ദേഹം പറഞ്ഞു. """
	#get topic distribution
	topic_distribution = use_topic_model_obj.get_topic_dist(text)

	print topic_distribution


def evaluate():
	#evaluate model

	model_dir_path = '/home/abhishek/python/gensim_test/model/partial_complete_dataset/'
	evaluate_obj = EvaluateLDA(model_dir_path, 'HINDI')

	evaluate_obj.evaluate('/home/abhishek/python/gensim_test/dataset/test_hi_200 (copy)')


def evaluate_model():

	evaluate_obj = EvaluateLDAMOdel('/home/abhishek/python/gensim_test/model/complete_dataset_2/', 'HINDI')
	ROOT_DIR = '/home/abhishek/python/gensim_test/dataset/test_corpus_50'

	# evaluate_obj.create_sim_index(ROOT_DIR, '/home/abhishek/python/gensim_test/model/test_corpus/simIndex.index', '/home/abhishek/python/gensim_test/model/test_corpus/corpus-filename-map.txt')
	# evaluate_obj.create_sim_index()
	evaluate_obj.load_test_corpus('/home/abhishek/python/gensim_test/model/test_corpus/simIndex.index', '/home/abhishek/python/gensim_test/model/test_corpus/corpus-filename-map.txt')
	evaluate_obj.analysis(ROOT_DIR)


if __name__ == "__main__":
	# training()
	use_model()
	# evaluate()
	# evaluate_model()
