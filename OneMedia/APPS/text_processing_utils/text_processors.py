from typing import Set

import nltk

nltk.download('punkt')


def text_to_words(text: str) -> Set[str]:
    return set(nltk.word_tokenize(text, language="russian"))


if __name__ == '__main__':
    text = """
To do this properly is quite complex. For your research, it is known as word tokenization. 
You should look at NLTK if you want to see what others have done, rather than starting from scratch:
Top-down
делать это должным образом довольно сложно. Для вашего исследования это называется токенизацией слов. 
Вам следует взглянуть на NLTK, если вы хотите увидеть
Команда университета ИТМО завоевала один из четырех комплектов золотых медалей финала международного студенческого 
чемпионата мира по программированию International Collegiate Programming Contest (ICPC).

Как сообщает пресс-служба Смольного, финал проходил в Москве с 1 по 6 октября, Россию в нем представляли 15 команд.



    """
    print(text_to_words(text))
