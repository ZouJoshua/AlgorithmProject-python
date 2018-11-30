#include <iostream>
#include <queue>
#include <string>
#include <vector>
#include <fstream>
#include <cstdlib>
#include <cassert>
#include <iomanip>

using namespace std;
using std::string;
using std::vector;

/**
 * lda每个doc对应的前n个词Id
 */
class Item {
    public:
        Item() {
            this->prob    = 0;
            this->word_id = 0;
        }

        Item(double prob, int word_id) {
            this->prob    = prob;
            this->word_id = word_id;
        }

//        bool operator < (const Item& obj) const{
//            return prob > obj.prob;
//        }

        Item& operator=(const Item& obj)
        {
            this->prob    = obj.prob;
            this->word_id = obj.word_id;
            return *this;
        }

    public:
        double prob;
        int word_id;
};

struct comp{
    bool operator()(const Item& a, const Item& b){
        return a.prob > b.prob;
    }
};

class LDAResult {
    private:
        double alpha;  //主题分布Dirichlet分布参数
        double beta;   //词分布Dirichlet分布参数
        int topic_num;  //主题数目
        int vocab_num;  //词数目
        int doc_num;    //文档数目
        double** doc_topic_mat=0;   //二维数组, 文档_主题概率矩阵[topic_num][doc_num]
        double** topic_vocab_mat=0; //二维数组, 主题_词概率矩阵[vocab_num][topic_num]
        Item**   doc_word_info=0;   //二维数组, 每个文档的topN个词的信息矩阵[doc_num][n]
        Item**   topic_word_info=0; //二维数组, 每个主题的topN个词的信息矩阵[topic_num][n]
        vector<string> words;

    public:
        LDAResult(double alpha, double beta, int topic_num, int vocab_num, int doc_num) {
            this->alpha     = alpha;
            this->beta      = beta;
            this->topic_num = topic_num;
            this->vocab_num = vocab_num;
            this->doc_num   = doc_num;

            doc_topic_mat  =  new double*[topic_num];
            for(int i = 0; i < topic_num; i++) {
                doc_topic_mat[i] = new double [doc_num];
            }

            topic_vocab_mat = new double*[vocab_num];
            for(int i = 0; i < vocab_num; i++) {
                topic_vocab_mat[i] = new double [topic_num];
            }
            doc_word_info = NULL;
            topic_word_info = NULL;
        }

        /**
         * 得到每个文档前n个关键词
         * @param n
         * @return
         */
        Item** getDocTopWordInfo(int n){
            doc_word_info = new Item*[doc_num];
            for(int i = 0; i < doc_num; i++) {
                doc_word_info[i] = new Item [n];
            }

            for(int i = 0; i < doc_num; ++i){ //每篇文档
                priority_queue<Item, vector<Item>, comp> queue;
                for(int j = 0; j < vocab_num; ++j){ //每个词
                    double prob = 0;
                    for(int k = 0; k < topic_num; ++k){ //每个主题
                        prob += doc_topic_mat[k][i] * topic_vocab_mat[j][k];
                    }
                    if (prob != 0) {
                        queue.push(Item(prob, j));
                        if(queue.size() > n){
                            queue.pop();
                        }
                    }
                }
                int q = queue.size();
                while(!queue.empty()){
                    q--;
                    doc_word_info[i][q] = queue.top();
                    queue.pop();
                }
            }
            return doc_word_info;
        }

        /**
         * 写每个主题的前n个关键词到文件中
         * @param n
         * @param output_name  输出文件
         */
        void dump_topic_topn_words(string output_name, int n) {
            if(n <= 0) {
                return;
            }
            ofstream outfile;
            outfile.open(output_name.c_str(), std::ios::out | std::ios::trunc);
            if(topic_word_info == NULL){
                topic_word_info = new Item*[topic_num];
                for(int i = 0; i < topic_num; i++) {
                    topic_word_info[i] = new Item [n];
                }

                priority_queue<Item, vector<Item>, comp> queue;
                for(int i = 0; i < topic_num; ++i){ //每个主题
                    for(int j = 0; j < vocab_num; ++j){ //每个词
                        double prob = topic_vocab_mat[j][i];
                        if (prob != 0) {
                            queue.push(Item(prob, j));
                            if(queue.size() > n){
                                queue.pop();
                            }
                        }
                    }
                    int q = queue.size();
                    while(!queue.empty()){
                        q--;
                        topic_word_info[i][q] = queue.top();
                        queue.pop();
                    }
                }
            }

            outfile << std::fixed; //以非科学计数法的形式打印
            outfile.precision(0);
            for(int i = 0; i < topic_num; ++i){  //topic_id
                outfile << i  <<  " : ";
                for(int j = 0; j < n; j++) {
                    Item& item = topic_word_info[i][j];
                    outfile << words[item.word_id] << ":" << item.prob << " ";
                }
                outfile << endl;
            }

            outfile.close();
        }

        /**
         * 写每个文档的前n个关键词到文件中
         * @param n
         * @param output_name  输出文件
         */
        void dump_doc_topn_words(string output_name, int n) {
            if(n <= 0) {
                return;
            }
            ofstream outfile;
            outfile.open(output_name.c_str(), std::ios::out | std::ios::trunc);
            if(doc_word_info == NULL){
                doc_word_info = getDocTopWordInfo(n);
            }

            for(int i = 0; i < doc_num; ++i){  //doc_id
                outfile << i + " : ";
                for(int j = 0; j < n; j++) {
                    Item& item = doc_word_info[i][j];
                    outfile << words[item.word_id] << "/" <<  item.prob << " ";
                }
                outfile << endl;
            }

            outfile.close();
        }

        void split(const std::string& line, const std::string del, vector<string>& pieces)
        {
            pieces.clear();
            size_t begin = 0;
            size_t pos = 0;
            std::string token;
            while ((pos = line.find(del, begin)) != std::string::npos) {
                if (pos > begin) {
                    token = line.substr(begin, pos - begin);
                    pieces.push_back(token);
                }
                begin = pos + del.size();
            }
            if (pos > begin) {
                token = line.substr(begin, pos - begin);
                pieces.push_back(token);
            }
        }

        /**
         * 得到词表
         * @param ori_word_path
         */
        void loadVocabs(string ori_word_path) {
            ifstream infile;
            infile.open(ori_word_path.c_str(), std::ios::in);
            string line;
            while(getline(infile, line)) {
                words.push_back(line);
            }
            infile.close();
        }

        /**
         * 加载文档_主题模型
         * @param model_path
         */
        void loadDocTopicModel(string model_path) {
            //将计数写入到矩阵中
            ifstream infile;
            infile.open(model_path.c_str(), std::ios::in);
            string line;
            vector<string> doc_info;
            while(getline(infile, line)) {
                doc_info.clear();
                split(line, " ", doc_info);
                int doc_id = atoi(doc_info[0].c_str());  //文档号，从0开始

                vector<string> topic_info;
                for(int i = 1; i < doc_info.size(); ++i){
                    topic_info.clear();
                    split(doc_info[i], ":", topic_info);//对应的主题信息
                    assert(topic_info.size() == 2);
                    int topic_id = atoi(topic_info[0].c_str());  //主题id
                    int topic_cnt = atoi(topic_info[1].c_str());  //主题次数
                    doc_topic_mat[topic_id][doc_id] = topic_cnt;
                }
            }
            infile.close();

            //计数
            int* doc_cnts = new int[doc_num];  //每个文档对应的主题数量和，即包含词的数目
            for(int i = 0; i < doc_num; ++i){  //对每个文档
                for(int j = 0; j < topic_num; ++j){  //对每个主题
                    doc_cnts[i] += doc_topic_mat[j][i];
                }
            }

            //计算概率
            double factor = topic_num * alpha;
            for(int i = 0; i < doc_num; ++i){  //对每个文档
                for(int j = 0; j < topic_num; ++j){  //对每个主题
                    doc_topic_mat[j][i] = (doc_topic_mat[j][i] + alpha) / (doc_cnts[i] + factor);
                }
            }
        }

        /**
         * 加载主题_词模型
         * @param model_path  主题_词模型位置,对应文件 server_model_0
         * @param model_summary_path   主题数目统计，对应文件 server_model_1
         */
        void loadTopicWordModel(string model_path, string model_summary_path) {
            //将计数写入到矩阵中
            ifstream infile;
            infile.open(model_path.c_str(), std::ios::in);
            string line;
            while(getline(infile, line)) {
                vector<string> info;
                split(line, " ", info);
                int word_id = atoi(info[0].c_str());  //词id
                for(int i = 1; i < info.size(); ++i){
                    vector<string> topic_info;
                    split(info[i], ":", topic_info); //对应的每个topic信息
                    int topic_id = atoi(topic_info[0].c_str());  //topic id
                    int topic_cnt = atoi(topic_info[1].c_str());  //topic计数
                    topic_vocab_mat[word_id][topic_id] = topic_cnt;
                }
            }
            infile.close();

            //写每个主题出现的次数
            int* topic_cnts = new int[topic_num];   //主题出现的次数
            infile.open(model_summary_path.c_str(), std::ios::in);
            vector<string> cnts;
            getline(infile, line);
            split(line, " ", cnts);
            for(int i = 1; i < cnts.size(); ++i){
                vector<string> cnt_info;
                split(cnts[i], ":", cnt_info);
                int topic_id = atoi(cnt_info[0].c_str());
                int topic_cnt = atoi(cnt_info[1].c_str());
                topic_cnts[topic_id] = topic_cnt;
            }
            infile.close();

//            //写概率
//            double factor = vocab_num * beta;   //归一化因子
//            for(int i = 0; i < vocab_num; ++i){  //每个词
//                for(int j = 0; j < topic_num; ++j){  //每个主题
//                    topic_vocab_mat[i][j] = (topic_vocab_mat[i][j] + beta) / (topic_cnts[j] + factor);
//                }
//            }
        }
};

int main(){
    string doc_topic_path = "doc_topic.0";
    string topic_word_path = "server_0_table_0.model";
    string topic_summary = "server_0_table_1.model";
    string ori_word_path = "vocab.news.txt";
    string output_doc_topn_words = "doc.topn";
    string output_topic_topn_words = "topic.topn";
//    LDAResult result(0.1, 0.01, 1000, 101491, 419660);
//    LDAResult result(0.1, 0.01, 1000, 111400, 1177450);
    LDAResult result(0.1, 0.01, 500, 111400, 11253518);
    result.loadVocabs(ori_word_path);  //得到所有词
    cout << ori_word_path <<  "加载完毕!" << endl;
    result.loadTopicWordModel(topic_word_path, topic_summary);  //得到主题-词概率分布
    cout << topic_word_path << "加载完毕!" << endl;
    cout << topic_summary << "加载完毕!" << endl;
    result.loadDocTopicModel(doc_topic_path);   //得到文档-主题概率分布
    cout << doc_topic_path << "加载完毕!" << endl;
//    result.dump_doc_topn_words(output_doc_topn_words, 10);  //每篇文档的前10个关键词写入到output_doc_topn_words中
    result.dump_topic_topn_words(output_topic_topn_words, 10);  //每个主题的前10个关键词写入到output_topic_topn_words中
}