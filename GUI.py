import csv
import random
import tkinter as tk
import pyttsx3
import threading

##### TODO: timing for each word / add radio button for practice or dictation
# https://www.geeksforgeeks.org/radiobutton-in-tkinter-python/

table = []
with open('duolingo.csv', encoding='utf-8-sig') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    first_row = next(reader)
    for row in reader:
        table.append(row)

CUSTOM_FONT = ('Arial', 20)
dictation = True  # 是否听写

# use to store the index of next word
word_lst = []
# use to store result (num, word, user_input)
result_lst = []

# sound engine
engine = pyttsx3.init()
engine.setProperty('rate', 130)


def read_word_thread():
    try:
        lbl_read_indicate.configure(text='发音中...')
        engine.say(var_word.get())
        engine.runAndWait()
        lbl_read_indicate.configure(text='')
    except RuntimeError:
        print('TODO')


def read_word():
    if var_number.get() != '':
        threading.Thread(target=read_word_thread).start()


def update_word():
    num, word, phonogram, meaning = table[word_lst.pop()]
    var_number.set(num)
    var_word.set(word.strip())
    var_phonogram.set(phonogram)
    var_meaning.set(meaning)
    read_word()


def start_test():
    start = ent_from.get()
    end = ent_to.get()
    try:
        start = int(start)
        end = int(end)
    except ValueError:
        lbl_warning.configure(text=f'"{start}"或"{end}"不是有效数字')
        return
    if not (1 <= start <= len(table)) or not (1 <= end <= len(table)):
        lbl_warning.configure(text=f'"{start}"或"{end}"超出范围（1-{len(table)}）')
        return
    if not start <= end:
        lbl_warning.configure(text=f'"{start}"大于"{end}"')
        return
    
    # clear warning
    lbl_warning.configure(text='')
    
    # create random word list
    global word_lst
    word_lst = list(range(start-1, end))  # 0-based index
    random.shuffle(word_lst)
    update_word()
    
    frm_select.grid_remove()
    frm_disp.grid()


def handle_keypress(event):
    # print(event)
    keycode = event.keycode
    if keycode == 13:
        # Enter key pressed
        next_word()
    elif keycode == 17:
        # ctrl key pressed
        read_word()


def next_word():
    if var_number.get() == '':
        # test finished
        return

    # get input and store
    user_input = ent_input.get()
    result_lst.append((var_number.get(), var_word.get(), user_input))
    ent_input.delete(0, tk.END)
    
    if word_lst:
        update_word()
    else:
        var_number.set('')  # set var_number to -1 to indicate test finished
        # all tested, show result page
        frm_disp.grid_remove()
        frm_result.grid()
        
        res_text = []
        correctness = 0
        for i, (num, word, user_input) in enumerate(result_lst):
            res = '错误'
            if word==user_input:
                res = '正确'
                correctness += 1
            elif word.lower()==user_input.lower():
                res = '半对（大小写错误）'
                correctness += 0.5
            res_text.append(f'{i+1}.\t{num}\t{word}\t{user_input}\t{res}')
        
        lbl_res_text.insert("1.0", '\t序号\t单词\t输入\t结果\n')
        lbl_res_text.insert("2.0", '\n'.join(res_text))
        lbl_res_text.insert("end", f'\n正确率：{correctness}/{len(result_lst)}')


def reset():
    # empty result list
    global result_lst
    result_lst = []
    
    # delete text in result label
    lbl_res_text.delete("1.0", tk.END)
    
    frm_result.grid_remove()
    frm_select.grid()


# create the window
root = tk.Tk()
root.title('背单词助手')

# bind key for shortcut
root.bind('<Key>', handle_keypress)

# create frame
# selection frame
frm_select = tk.Frame(root)
# display frame
frm_disp = tk.Frame(root)
# result frame
frm_result = tk.Frame(root)

# selection frame
lbl_text = tk.Label(frm_select, text='选择查词范围', font=CUSTOM_FONT)
ent_from = tk.Entry(frm_select, font=CUSTOM_FONT)
lbl_to = tk.Label(frm_select, text='to', font=CUSTOM_FONT)
ent_to = tk.Entry(frm_select, font=CUSTOM_FONT)
lbl_warning = tk.Label(frm_select, text='', font=CUSTOM_FONT)
btn_confirm = tk.Button(frm_select, text='确定', font=CUSTOM_FONT, command=start_test)

# create display text
# 序号
var_number = tk.StringVar(root, '')
# 单词
var_word = tk.StringVar(root, '')
# 音标
var_phonogram = tk.StringVar(root, '')
# 词义
var_meaning = tk.StringVar(root, '')
# create button
btn_read = tk.Button(frm_disp, text='读音（Ctrl）', font=CUSTOM_FONT, command=read_word)
lbl_read_indicate = tk.Label(frm_disp, text='')

lbl_number = tk.Label(frm_disp)
lbl_word = tk.Label(frm_disp, font=CUSTOM_FONT)
lbl_phonogram = tk.Label(frm_disp, font=CUSTOM_FONT)
lbl_meaning = tk.Label(frm_disp)
if not dictation:
    lbl_number.configure(textvariable=var_number)
    lbl_word.configure(textvariable=var_word)
    lbl_phonogram.configure(textvariable=var_phonogram)
    lbl_meaning.configure(textvariable=var_meaning)

# create input bar
ent_input = tk.Entry(frm_disp, font=CUSTOM_FONT)
btn_next = tk.Button(frm_disp, text='确认（Enter）', font=CUSTOM_FONT, command=next_word)

# create result widgets
btn_back = tk.Button(frm_result, text='返回主界面', font=CUSTOM_FONT, command=reset)
lbl_res_text = tk.Text(frm_result)

# config grid
total_row = 1
total_col = 1
for i in range(total_row):
    root.rowconfigure(i, weight=1)
for i in range(total_col):
    root.columnconfigure(i, weight=1)

# place frames
# frm_disp.grid(row=0, column=0)
frm_select.grid(padx=5, pady=5)

# place the widgets
# selection frame
lbl_text.grid(row=0, column=0, columnspan=3)
ent_from.grid(row=1, column=0)
lbl_to.grid(row=1, column=1)
ent_to.grid(row=1, column=2)
lbl_warning.grid(row=2, column=0, columnspan=3, sticky=tk.W)
btn_confirm.grid(row=3, column=2, sticky=tk.E)

# display frame
lbl_number.grid(row=0, column=0, sticky='w')
lbl_word.grid(row=0, column=1, padx=5, pady=10)
btn_read.grid(row=0, column=2, sticky='e')
lbl_read_indicate.grid(row=1, column=2)
lbl_phonogram.grid(row=1, column=1, padx=5, pady=10)
lbl_meaning.grid(row=2, column=0, columnspan=2, sticky='e')
ent_input.grid(row=3, column=0, columnspan=2)
btn_next.grid(row=3, column=2)

# result frame
btn_back.grid(row=0, column=0)
lbl_res_text.grid(row=1, column=0)

root.mainloop()
