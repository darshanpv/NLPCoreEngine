# State-of-the-Art NLP Engine for intent classification and entity recognition – SPACY, DIET ,BERT Classifier

The NLP engine is highly flexible and customizable.  You can create your own NLP pipeline as per your need. The NLP engine runs on top of open source RASA NLU core that provides range of configuration that meet most of your NLP needs. You can take a look at how to configure your own pipeline [here][url1]

Based on my experience DIET classifier seems to be much faster to train, accurate and serves to find both intent and entities.

Here is how you could customize your pipeline and use this NLP engine that can act as backbone to your chatbot engine.

## Installation
### Prerequisites
This was implemented and tested on windows 10 – (Windows Subsystem for Linux) but should also work on Linux and Mac OS X.
- Make sure docker, and docker-compose are installed on your server. 
- Detailed instructions can be found in the Docker [documentation][url2].
### Download
- Clone or download this repo. Unzip and copy files from repo to your preferred location
### Docker build and run
- Build the docker by running following command at root of your folder
```sh
$ docker build . -t aria_nlp:latest
```
- Run the docker 
```sh
$ docker run -it  -d -p 5001:5001 ariabot:latest
```
- If your installation is successful, you should see the container running using following command
```sh
$ docker ps
```
## Usage
### Setup
- NLP Engine uses Rasa Open Source that performs intent classification, entity extraction.
- You need to provide training data in markdown format. More details can be found in the [documentation][url3]. 
- You can create your own training data and upload it in /app/intents/data folder.
- Follow the naming convention <domain>_<locale>.md where domain is name of function for which you are building your bot. (e.g. travel, hr, finance etc.) and locale is language. e.g. "banking_en.md" These are used while making REST API call. (explained below)
- Here is a sample training data provided for retail banking scenario for demonstration. (see "/app/intents/data/banking_en.md" for more details)
```
## intent:askTransferCharge
- Will I be charged for transferring money
- do transfers cost something?
- is there a transfer charge?
- Is there a charge
- will i be charged for a transaction?
- do xfers cost something?
- is there a transfer fee
- is there a xfer fee
- how much is the transfer fee

## intent:checkBalance
- What is balance in my account?
- How much money is on my account?
- What's left on that account?
- How much do I have on that account?
- What's the balance on that account?
- How much money is left on that account?
- what is my account balance
- what's my account balance?
- what's my account balance
- what's my balance?
- what’s my account balance
- balance in my account
```
- You can configure your own pipeline based on your preference (SPACY, BERT or DIET) and store it in folder "/app/intents/dnn/config" folder. While creating a pipeline you need to select following components -
    *	Word Vector Sources (Mitie, Spacy, HFTransformers etc.)
    *	Tokenizers (Whitespace, Jieba, Mitie, Spacy, ConveRT etc.)
    *	Text Featurizer (Mitie, Spacy, ConveRT, RegEx, CountVector, LexicalSyntactic etc.)
    *	Intent Classifier (Mitie, SKlearn, BERT, DIET etc.)
    *	Entity Extractor (Mitie, Spacy, Entity Synonym, CRF, Duckling, DIET etc) 
- You can get more details on how to configure in this [documentation][url4]. 
Here is a sample config file that has worked well for given example
```
language: en
pipeline:
    - name: WhitespaceTokenizer
    - name: RegexFeaturizer
    - name: LexicalSyntacticFeaturizer
    - name: CountVectorsFeaturizer
    - name: CountVectorsFeaturizer
        analyzer: "char_wb"
        min_ngram: 1
        max_ngram: 4
    - name: DIETClassifier
        epochs: 100
    - name: EntitySynonymMapper
    - name: ResponseSelector
        epochs: 100
```
- Now here is a last step before you are ready to run the NLP engine. You need to configure NLU properties file of NLP engine. Edit the “nlu.propoerties” file located at "/app/intents/config" file
Line -7 => Select algorithm = RASA in  [NLP_ALGORITHM]  as you are using RASA NLU core as your underneath engine 
Line -16 => Edit config_file parameter with your configuration file that you created in step 4 above

#### Training NLP Engine
*Important* – For any changes that you do in any of the files, you need to build and run the docker.
- Now if you have built and your container running , it’s time to train your NLP Engine on training data that you created using REST API
    * Method – GET
    * URL http://127.0.0.1:5001/train?domain=banking&locale=en   (assuming you domain is banking and language English)
    * Response - 
```    
{"response":{"Number of intents":"15","Number of utterances":"215","domain":"banking","locale":"en"}}
```
>Note – Training may take some time, have some patience

#### Intent Classification/ Entity Recognition
- If your training is successful, you can pass on utterance to classify its intent and get the entities if any.
    * Method – GET
    * URL - http://127.0.0.1:5001/predict?domain=banking&locale=en&userUtterance=I want to pay my SBI card    (assuming you domain is banking and language English)
    * Response - 
```
{"entities":[{"end":20,"entity":"creditCard","extractor":"DIETClassifier","start":17,"value":"SBI"}],"intent":{"confidence":"1.00","name":"makePayment"},"intent_ranking":[{"confidence":"1.00","name":"makePayment","utterance":"I would like to make payment"},{"confidence":"0.00","name":"transferMoney","utterance":"I want to transfer the money"},{"confidence":"0.00","name":"checkBalance","utterance":"What is balance in my account?"}],"text":"I want to pay my SBI card"}
```


License
----

MIT

   [url1]: <https://legacy-docs.rasa.com/docs/nlu/0.15.1/components/>
   [url2]: <https://docs.docker.com/install/>
   [url3]: <https://legacy-docs.rasa.com/docs/nlu/0.15.1/dataformat/>
   [url4]: <https://rasa.com/docs/rasa/components>