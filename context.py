import re

def find_sentence(book: Dict[int, List[str]], page: int, line: int) -> str:
    '''
    Находит полное предсказание по номеру страницы и строки.

    Параметры:
        book(Dict[int, List[str]]): Книгу в формате словаря {номер_страницы: [строки]}
        page(int): Номер страницы (начиная с 1)
        line(int): Номер строки на странице (начиная с 1)

    Возвращает всё предложение, содержащее указанную строку.
    '''
    line_n = line - 1
    page_n = page - 1
    sentence_end = ['.', '!', '?']
    start_context = ''
    end_context = ''
    if (line_n != 0 and book[page_n][line_n - 1][-1] not in sentence_end) or (line_n == 0 and book[page_n - 1][-1][-1] not in sentence_end):
        if line_n == 0:
            start_page = page_n - 1
            start_line = len(book[start_page]) - 1
        else:
            start_page = page_n
            start_line = line_n - 1
        last_match = None
        start_index = None
        while last_match == None:
            matches = list(re.finditer(r'[.!?»"]', book[start_page][start_line]))
            if matches:
                last_match = matches[-1]
                start_index = last_match.start() + 2
                start_context = book[start_page][start_line][start_index:] + ' ' + start_context
            else:
                start_context = book[start_page][start_line] + ' ' + start_context
                if start_line == 0:
                    if start_page == 0:
                        break
                    else:
                        start_page -= 1
                    start_line = len(book[start_page]) - 1
                else:
                    start_line -= 1
                    
    if book[page_n][line_n][-1] not in sentence_end:
        if line_n == len(book[page_n]) - 1:
            end_page = page_n + 1
            end_line = 0
        else:
            end_page = page_n
            end_line = line_n + 1
        first_match = None
        end_index = None
        while first_match == None:
            if end_page not in book:
                break
            matches = list(re.finditer(r'[.!?«"]', book[end_page][end_line]))
            if matches:
                first_match = matches[0]
                end_index = first_match.start() + 2
                end_context = end_context + ' ' + book[end_page][end_line][: end_index]
            else:
                end_context = end_context + ' ' + book[end_page][end_line]
                if end_line == len(book[end_page]) - 1:
                    end_line = 0
                    end_page += 1
                else:
                    end_line += 1
    full_context = start_context + book[page_n][line_n] + end_context
    return full_context.strip()
