from setuptools import setup, find_packages

setup(
      name="topic_modeling",
      version="0.2.0",
      description="topic modeling",
      long_description="topic modeling",
      author="apus",
      author_email="***@gmail.com",
      url="https://git.apusapps.in/nlp/topic_modeling",
      packages=find_packages(),
      #package_dir = {'':'topic_modeling'},
      package_data={
          'topic_modeling': ['stopwords/*.txt']
          },
      install_requires=['gensim'],
      keywords=["lda", "topic", "nlp"],
)
