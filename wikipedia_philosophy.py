import json
import requests
from bs4 import BeautifulSoup
import wikipedia
from colorama import Fore, Back, Style

# save the links path to philosophy
def save_object(filename, _object):
    json_object = json.dumps(_object, indent=3, ensure_ascii=False)
    with open(filename, "a") as outfile: 
        outfile.write(json_object + ',\n')

# remove all links from the last run
def earase_output_file(filename):
    with open(filename, 'r+') as outfile: 
        outfile.truncate(0)

# return a random link
def get_random_link() :
    response = requests.get('https://en.wikipedia.org/wiki/Special:Random')
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1', attrs ={'id':'firstHeading'})
    return title.text, wikipedia.page(title.text).url

# detect text between start_char and end_char
def detect_bad_indexes(text, start_char, end_char):
    text_between = ''
    counter = 0
    indexes = []
    start_index = 0
    end_index = 0
    for each in range(text.__len__()):
        if counter > 0:
            text_between += text[each]
        if counter > 0:
            text_between += text[each]
        elif counter < 0 :
            counter = 0

        if text[each] == start_char :
            if  counter == 0 :
                start_index = each
            counter += 1
        if text[each] == end_char:
            counter -= 1
            if counter == 0 :
                end_index = each
                indexes.append((start_index, end_index))
            elif counter < 0 :
                start_index = end_index = 0
    return indexes

# check if a is inside of bad indexes 
def check_a_isbad(a_tag_text, text, bad_indexes):
    a_tag_text_index = text.index(a_tag_text)    
    res = [x for x in bad_indexes  if a_tag_text_index > x[0] and a_tag_text_index < x[1]]
    if  res :
        return True
    else:
        return False
    
# opens the link
def open_link(link) :
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')

    div_tag = soup.find('div', attrs={'class':'mw-parser-output'})
    p_tags = div_tag.find_all("p",  recursive = False)
    counter = 1
    for each_p in p_tags:
        if each_p.has_attr('class') and each_p['class'][0] == 'mw-empty-elt' :
            continue

        bad_par_indexes = detect_bad_indexes(each_p.text, '(', ')')
        bad_curly_indexes = detect_bad_indexes(each_p.text, '{', '}')
        a_tags =  each_p.find_all('a', recursive = False)
        for each_a in a_tags :
            if each_a != None :
                a_text = each_a.text
                a_href = each_a['href']

                # detect text in parantheses and curly brackets
                if check_a_isbad(a_text, each_p.text, bad_par_indexes) :
                    continue
                if check_a_isbad(a_text, each_p.text, bad_curly_indexes) :
                    continue

                # Detect red links
                if each_a.has_attr('class') and each_a['class'][0] in ['new', 'mw-disambig'] :
                    continue
                # Detect links to the out side of wikipedia
                if 'https://' in a_href or  'http://' in a_href:
                    continue

                ret_val ={
                    'a_text' : each_a.text,
                    'a_href' : each_a['href'],
                    'p_number' : counter,
                }
                return ret_val, True
        counter += 1
    return {}, False


if __name__ == "__main__":
    wiki_english = 'https://en.wikipedia.org/wiki/Main_Page'
    wiki_link = 'https://en.wikipedia.org'
    wiki_random = ''
    wiki_philosophy = '/wiki/Philosophy'
    output_file = 'links_path.json'

    print(Style.RESET_ALL + Style.DIM + Fore.GREEN + 'Starting game ...' + Style.RESET_ALL)

    wiki_random = get_random_link()
    earase_output_file(output_file)

    counter = 1
    flag = False
    link = dict()
    link['a_text'] = wiki_random[0]
    link['a_href'] = wiki_random[1].replace(wiki_link,'')
    link['p_number'] = 0

    check_loop = set()

    while counter < 120:
        if link['a_href'] in check_loop:
            print(Style.RESET_ALL + Style.DIM + Fore.RED + 'Oops! It is a loop!' + Style.RESET_ALL)
            flag = False
            break
        else :
            check_loop.add(link['a_href'])

        temp_link = wiki_link + link['a_href']
        print(Style.RESET_ALL + Style.DIM + str(counter) , link['a_text']
                    , Fore.BLUE +  f'({temp_link})'+ Style.RESET_ALL)
        save_object(output_file,link)

        link, flag = open_link(temp_link)

        if flag == False :
            break

        if link['a_href'] == wiki_philosophy :
            save_object(output_file, link)
            counter += 1
            print(Style.RESET_ALL + Style.DIM + str(counter) , link['a_text'] + Style.RESET_ALL)
            flag = True
            break
        else:
            counter += 1
    if flag == True :
        print(Style.RESET_ALL + Fore.WHITE + Back.GREEN + f'Congratulation! Philosophy has been found on {counter}th time.' + Style.RESET_ALL)
    else :
        print(Style.RESET_ALL  + Fore.WHITE + Back.RED + f'Sorry! Philosophy was not reached.' + Style.RESET_ALL)
