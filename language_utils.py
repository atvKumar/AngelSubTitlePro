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

def write_filtered_text(source_words_file, output_file, min_word_lenght = 3):
    with open(resource_path(source_words_file), "r") as word_file:
        with open(resource_path(output_file), "w") as fp:
            for word in word_file:
                word_in_dict = word.strip()
                if len(word_in_dict) > min_word_lenght:
                    fp.write(word_in_dict + "\r\n")

# write_filtered_text("words_alpha.txt", "en_dict_words.txt")

def load_dict_words(source_words_file):
    with open(resource_path(source_words_file), "r") as word_file:
        return list(word_file.read().split())

# print(load_dict_words("en_dict_words.txt"))

def en_autocomplete_words() -> list:
    return load_dict_words(resource_path("en_dict_words.txt"))