import csv

rows = []
FUTURE = ['نخواهند', 'نخواهید', 'نخواهیم', 'نخواهد', 'نخواهی', 'نخواهم', 'بخواهند', 'بخواهید', 'بخواهیم', 'بخواهد',
          'بخواهی', 'بخواهم', 'خواهند', 'خواهید', 'خواهیم', 'خواهد', 'خواهی', 'خواهم']
PREFIX_MOZARE = ["می", "نمی", "ب", "ن"]
SUFFIX_MOZARE = ['م', 'ی', 'د', 'یم', 'ید', 'ند']
PAST = ['باشند', 'باشید', 'باشیم', 'باشد', 'باشی', 'باشم', 'بودند', 'بودید', 'بودیم', 'بود', 'بودی', 'بودم', 'اند',
        'اید', 'ایم', 'است', 'ای', 'ام', 'ند', 'ید', 'یم', '', 'ی', 'م']
PRESENT_ROOT = ['شو', 'کن']
STOP_WORDS_LIST = ['از', 'با', 'را', 'و']
SYNONYM_WORDS_DICT = {'تهران': ['طهران'], 'ماشین': ['اتومبیل']}
not_list = list(range(1, 1731))
rows = []


class Post:
    def __init__(self, id, publish_date, title, url, summary, meta_tags, content, thumbnail):
        self.id = id
        self.publish_date = publish_date
        self.title = title
        self.url = url
        self.summary = summary
        self.meta_tags = meta_tags
        self.content = content
        self.thumbnail = thumbnail
        self.content_token_list = []

    def _get_allowed_ascii_codes(self):
        PERSIAN_CHARS_START = 1570
        PERSIAN_CHARS_END = 1800

        allowed_ascii_codes_list = []
        for ascii_code in range(PERSIAN_CHARS_START, PERSIAN_CHARS_END + 1):
            allowed_ascii_codes_list.append(ascii_code)


        allowed_ascii_codes_list.append(8204)

        return allowed_ascii_codes_list

    def _get_token_from_inputs(self, user_input):
        ALLOWED_ASCII_CODES = self._get_allowed_ascii_codes()

        i = 0

        token_list = []
        while i < len(user_input):
            if ord(user_input[i]) in ALLOWED_ASCII_CODES:
                j = i
                while j < len(user_input) and ord(user_input[j]) in ALLOWED_ASCII_CODES:
                    j += 1

                token_list.append(user_input[i:j])

                i = j + 1

            else:
                i += 1

        return token_list

    def remove_plural_from_token(self):
        def remove_ha(string):
            if len(string) > 2:
                if string[len(string) - 2: len(string) + 1] == "ها":
                    string = string[0:len(string) - 2]
            return string

        def remove_aan(string):
            if len(string) > 2:
                if string[len(string) - 2: len(string) + 1] == "ان":
                    string = string[0:len(string) - 2]
            return string

        for i in range(0, len(self.content_token_list)):
            self.content_token_list[i] = remove_ha(self.content_token_list[i])
            self.content_token_list[i] = remove_aan(self.content_token_list[i])

    def delete_stop_words(self):
        j = len(self.content_token_list) - 1
        i = 0
        while i <= j:
            # print("i is: ", i, " | j is : ", j, " | content_token_list size is: ", len(self.content_token_list))
            if self.content_token_list[i] in STOP_WORDS_LIST:
                self.content_token_list.pop(i)
                i -= 1
                j -= 1
            i += 1

    def set_token_list(self):
        self.content_token_list = self._get_token_from_inputs(self.content)

    def case_folding(self):
        for item_i, item in enumerate(self.content_token_list):
            for key, value in SYNONYM_WORDS_DICT.items():
                if item in value:
                    self.content_token_list[item_i] = key

    def _concat_based_on_list(self, word_list):
        temp_array = []
        for i in range(0, len(self.content_token_list) - 1):
            if self.content_token_list[i] in word_list:
                temp_str = self.content_token_list[i] + self.content_token_list[i + 1]
                temp_array.append(temp_str)
                i += 1
            else:
                temp_array.append(self.content_token_list[i])
        self.content_token_list = temp_array

    def present_verb_correction(self):
        self._concat_based_on_list(["می", "نمی"])

    def concat_nim_fasele(self):
        for i in range(0, len(self.content_token_list) - 1):
            item = self.content_token_list[i]

            if len(item) > 2:
                if item[0:2] == "می" and ord(item[2]) == 8204:
                    self.content_token_list[i] = item[0:2] + item[3:]
                    i += 1
            if len(item) > 3:
                if item[0:3] == "نمی" and ord(item[3]) == 8204:
                    self.content_token_list[i] = item[0:3] and item[4:]
                    i += 1

    def concat_ayande(self):
        self._concat_based_on_list(FUTURE)

    def derive_bon_from_mozare(self):
        def get_bon_from_word(word):
            for prefix in PREFIX_MOZARE:

                if prefix == word[0: len(prefix)]:

                    for suffix in SUFFIX_MOZARE:

                        if suffix == word[len(word) - len(suffix):]:

                            if word[len(prefix): len(word) - len(suffix)] in PRESENT_ROOT:
                                return word[len(prefix): len(word) - len(suffix)]
            return None

        for i in range(0, len(self.content_token_list)):
            new_word = get_bon_from_word(self.content_token_list[i])
            if new_word is not None:
                self.content_token_list[i] = new_word

    def __repr__(self):
        return str(self.title)

    def __str__(self):
        return str(self.title)


def save_xlx_to_csv(xlx_address, csv_address):
    import pandas as pd
    data_xls = pd.read_excel(xlx_address, index_col=None)
    data_xls.to_csv(csv_address, encoding='utf-8', index=False)


def create_post_objects(csv_path):
    posts_list = []

    with open(csv_path, encoding="utf8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        rows = list(csv_reader)
        id = 1

        for row in rows[1:]:
            post_obj = Post(id, *row)
            post_obj.set_token_list()
            post_obj.remove_plural_from_token()
            post_obj.case_folding()
            post_obj.present_verb_correction()
            post_obj.concat_nim_fasele()
            post_obj.concat_ayande()
            post_obj.delete_stop_words()
            post_obj.derive_bon_from_mozare()
            posts_list.append(post_obj)

            id += 1

    return posts_list


def parse_input(user_input):
    def find_double_quotation(string):
        i = 0
        first_list = []

        while i < len(string):
            if string[i] == '"':
                j = i + 1
                while string[j] != '"':
                    j += 1

                first_list.append(string[i + 1:j])
                string = string[0:i] + user_input[j + 1:]
            i += 1

        return string, first_list

    def find_not(string):
        second_list = []

        i = 0
        while i < len(string):
            if string[i] == "!":
                j = i + 1
                while j < len(string) and string[j] != " ":
                    j += 1
                second_list.append(string[i + 1: j])
                string = string[0:i] + string[j:]

            i += 1

        return string, second_list

    def find_other_words(string):
        parsed_string = string.split(" ")
        new_parsed_string = []

        for item in parsed_string:
            if item != '':
                new_parsed_string.append(item)

        return new_parsed_string

    def cat_and_source_finder(user_input):
        SOURCE_STR = "source:"
        CAT_STR = "cat:"

        user_input_array = user_input.split(" ")

        cat_value = None
        if CAT_STR in user_input:
            cat_id = user_input_array.index(CAT_STR)
            cat_value = user_input_array[cat_id + 1]
            user_input_array.remove(CAT_STR)
            user_input_array.remove(cat_value)

        source_value = None
        if SOURCE_STR in user_input:
            source_id = user_input_array.index(SOURCE_STR)
            source_value = user_input_array[source_id + 1]
            user_input_array.remove(SOURCE_STR)
            user_input_array.remove(source_value)

        changed_user_input = ""
        for item in user_input_array:
            changed_user_input = changed_user_input + " " + item

        return changed_user_input, source_value, cat_value

    user_input, first_list = find_double_quotation(user_input)
    user_input, second_list = find_not(user_input)
    user_input, source_value, cat_value = cat_and_source_finder(user_input)
    third_list = find_other_words(user_input)

    return {
        "with_quotation": first_list,
        "with_exclamation_mark": second_list,
        "source_value": source_value,
        "cat_value": cat_value,
        "others": third_list,
    }


XLX_PATH = 'data/input.xlsx'
CSV_PATH = 'data/input.csv'

save_xlx_to_csv(XLX_PATH, CSV_PATH)
posts_list = create_post_objects(CSV_PATH)

DATA_DICT = {}


def create_data_dict(posts_list):
    for post in posts_list:
        content_token_list = post.content_token_list

        for word_index, word in enumerate(content_token_list):
            word_in_data_dict_value = DATA_DICT.get(word, None)
            # agar word vojod dasht
            if word_in_data_dict_value is not None:
                # shomare post ro migereft (shomare news)
                word_position_array = word_in_data_dict_value.get(post.id, None)
                # age bud be tahesh ezafe mikard
                if word_position_array is None:
                    DATA_DICT[word][post.id] = [word_index]
                    # age word nabod misazatesh
                else:
                    DATA_DICT[word][post.id].append(word_index)
            # age asi jun nabod bia besazesh
            else:
                DATA_DICT[word] = {post.id: [word_index]}


def search_in_dict_one_word(word):
    global DATA_DICT
    # data_row = []
    # data_row = DATA_DICT.get(word)
    # if word in DATA_DICT.keys():
    data_row = [k for k in DATA_DICT.get(word)]
    return data_row


def search_in_not_dict_one_word(word):
    global DATA_DICT
    # list_keys = []
    # if word in DATA_DICT.keys():
    list_keys = search_in_dict_one_word(word)
    list_not = set(not_list) - set(list_keys)
    return list_not


create_data_dict(posts_list)


def print_posts_list(posts_list):
    for post in posts_list:
        print(post.content_token_list)


# print_data_dict()


def search_in_dict_statement(statement):
    global DATA_DICT

    word_list = statement.split(" ")

    if len(word_list) < 2:
        raise ValueError('Statement contains less than 2 numbers')

    for word in word_list:
        if DATA_DICT.get(word, None) is None:
            return None

    common_posts = list(DATA_DICT.get(word_list[0], None).keys())

    for word in word_list:
        word_positions = DATA_DICT.get(word, None)

        if word_positions is None:
            common_posts = []

        i = 0
        while i < len(common_posts):

            for w in word_list[1:]:

                if common_posts[i] not in DATA_DICT[w].keys():
                    common_posts.pop(i)
                    i -= 1
                    break
            i += 1

    # Here we know that every post in common_posts contains all statement
    # words.

    result = []

    for post_num in common_posts:
        word_position_pointers = DATA_DICT[word_list[0]][post_num]

        for i in word_position_pointers:
            found = True

            for word in word_list[1:]:
                i += 1

                if i not in DATA_DICT[word][post_num]:
                    found = False
                    break

            if found:
                result.append(post_num)
    return result


def get_input(u_input):
    flag1 = 0
    flag2 = 0
    flag3 = 0
    if u_input.__contains__("طهران"):
        u_input = u_input.replace("طهران", "تهران")
    if u_input.__contains__("اتومبیل"):
        u_input = u_input.replace("اتومبیل", "ماشین")
    # print(u_input)

    first_list, second_list, source_value, cat_value, third_list = parse_input(u_input).values()
    first_list = list(first_list)
    second_list = list(second_list)
    third_list = list(third_list)
    # print(first_list)
    # print(second_list)
    # print(third_list)
    if first_list.__len__() == 0 and second_list.__len__() != 0 and third_list.__len__() != 0:
        flag3 = 1
    if first_list.__len__() == 0 and second_list.__len__() == 0 and third_list.__len__() != 0:
        flag3 = 1
        flag2 = 1
    if first_list.__len__() == 0 and second_list.__len__() != 0 and third_list.__len__() == 0:
        flag3 = 1
        flag1 = 1
    if first_list.__len__() == 0 and second_list.__len__() == 0 and third_list.__len__() == 0:
        flag3 = 1
        flag2 = 1
        flag1 = 1
    if first_list.__len__() != 0 and second_list.__len__() == 0 and third_list.__len__() != 0:
        flag2 = 1
    if first_list.__len__() != 0 and second_list.__len__() != 0 and third_list.__len__() == 0:
        flag1 = 1
    if first_list.__len__() != 0 and second_list.__len__() == 0 and third_list.__len__() == 0:
        flag1 = 1
        flag2 = 1
    temp = []
    temp2 = []
    temp3 = []
    final_not = []
    final_statement = []
    final_one = []
    count = 0
    for i in third_list:
        count = count + 1
        if count == 1:
            # print(i)
            final_one = search_in_dict_one_word(i)
            continue
        else:
            # print(i)
            # print(search_in_dict_one_word(i))
            temp.extend(list(set(search_in_dict_one_word(i)).intersection(set(final_one))))
            final_one = temp
            temp = []
    final_one = list(dict.fromkeys(final_one))
    # print(final_one)

    count = 0
    for i in second_list:
        count = count + 1
        if count == 1:
            final_not = search_in_not_dict_one_word(i)
            continue
        else:
            temp2.extend(list(set(search_in_not_dict_one_word(i)).intersection(set(final_not))))
            final_one = temp2
            temp2 = []
    final_not = list(dict.fromkeys(final_not))
    # print(final_not)
    count = 0
    for i in first_list:
        count = count + 1
        if count == 1:
            final_statement = search_in_dict_statement(i)
            continue
        else:
            temp3.extend(list(set(search_in_dict_statement(i)).intersection(set(final_statement))))
            final_statement = temp3
            temp3 = []
    final_statement = list(dict.fromkeys(final_statement))
    # print(final_statement)

    # print(final_statement)
    # print(final_one)
    # print(final_not)


    if flag1 == 1 and flag2 == 0 and flag3 == 0:
        my_result = set(final_not).intersection(set(final_statement))
    elif flag1 == 1 and flag2 == 1 and flag3 == 0:
        my_result = set(final_statement)
    elif flag1 == 1 and flag2 == 0 and flag3 == 1:
        my_result = set(final_not)
    elif flag1 == 1 and flag2 == 1 and flag3 == 1:
        my_result = []
    elif flag1 == 0 and flag2 == 0 and flag3 == 1:
        my_result = set(final_one).intersection(set(final_not))
    elif flag1 == 0 and flag2 == 1 and flag3 == 0:
        my_result = set(final_one).intersection(set(final_statement))
    elif flag1 == 0 and flag2 == 1 and flag3 == 1:
        my_result = set(final_one)
    elif flag1 == 0 and flag2 == 0 and flag3 == 0:
        my_result = set(final_one).intersection(set(final_not), set(final_statement))
    print(my_result)
    title = []
    pic = []
    content = []
    date = []
    with open(CSV_PATH, encoding="utf8") as csv_file:
         csv_reader = csv.reader(csv_file, delimiter=',')
         rows = list(csv_reader)

    for i in my_result:
        title.append(rows[i][1])
        pic.append(rows[i][6])
        content.append(rows[i][5])
        date.append(rows[i][0])
    print(title)
    print(content)
    print(pic)
    print(date)
