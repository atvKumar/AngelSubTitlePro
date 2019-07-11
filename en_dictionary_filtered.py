from videoPanel import resource_path

def get_filtered_words(min_word_lenght = 3) -> list:
    valid_words = []
    with open(resource_path("words_alpha.txt"), "r") as word_file:
        for word in word_file:
            # print(word.strip(), len(word))
            word_in_dict = word.strip()
            if len(word_in_dict) > min_word_lenght:
                # print(word_in_dict)
                valid_words.append(word_in_dict)
    return valid_words

# print(len(get_filtered_words()))