from FiScrape.search import search_win
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import os

import sys
if sys.platform == 'darwin':
    from tkmacosx import Button

# python fiscrape_gui.py

from scrapy.utils import project
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.log import configure_logging
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
import threading
from FiScrape.tools import phi_align
from scrapy.utils.trackref import iter_all
from scrapy import signals

import concurrent.futures


def get_spiders():
    settings = project.get_project_settings()
    spider_loader = SpiderLoader.from_settings(settings)
    return spider_loader.list()


def get_chosen_spider(value):
    global chosen_spider
    chosen_spider = value
    # print(chosen_spider)
    return chosen_spider

def get_chosen_feed(value):
    global chosen_feed
    chosen_feed = value
    return chosen_feed


def browse_button():
    global folder_path
    folder_path = filedialog.askdirectory()
    folder_path_entry.delete(0, END)
    folder_path_entry.insert(0, folder_path)
    return folder_path


def execute_spider():
    if folder_path_entry.get()!=None:
        folder_path = folder_path_entry.get()
        if not folder_path:
            messagebox.showerror('Error', 'All entries are required')
            return
    if file_entry.get() == '':
        messagebox.showerror('Error', 'All entries are required')
        return
    if 'chosen_feed' not in globals():
        messagebox.showerror('Error', 'All entries are required')
        return
    if chosen_feed not in ['DB', 'CSV', 'JSON']:
        messagebox.showerror('Error', 'All entries are required')
        return

    # try:
    #     feed_uri = f"file:///{folder_path}/{file_entry.get()}.{chosen_feed}"
    # except:
    #     messagebox.showerror('Error', 'All entries are required')

    if chosen_feed == 'DB':
        try:
            feed_uri = f"sqlite:///{folder_path}/{file_entry.get()}.{chosen_feed.lower()}"
            # feed_uri = 'sqlite:////Users/zenman618/Documents/git_packages/VisualStudioGit/FiScrape/sqlite_files/sqlite_files/FiScrape.db'
        except:
            messagebox.showerror('Error', 'All entries are required')
    else:
        try:
            feed_uri = f"file:///{folder_path}/{file_entry.get()}.{chosen_feed}"
        except:
            messagebox.showerror('Error', 'All entries are required')

    execute_btn["state"] = "active"
    execute_btn["state"] = "disabled"
    stop_btn["state"] = "normal"

    settings = project.get_project_settings()
    if chosen_feed == 'DB':
        settings.set('CONNECTION_STRING', feed_uri)
    else:
        settings.set('FEED_URI', feed_uri)
        if chosen_feed == 'JSON':
            settings.set('FEED_FORMAT', 'jsonlines')
        else:
            settings.set('FEED_FORMAT', chosen_feed)

    configure_logging()
    runner = CrawlerRunner(settings)
    if chosen_spider == 'all':
        remove_lst = ['all', 'cnbc', 'test']
        [spiders.remove(s) for s in remove_lst if s in spiders]
        # spiders = [s for s in spiders if s not in remove_lst]
        # [runnner.crawl(spider) for spider in spiders]
        for spider in spiders:
            runner.crawl(spider)
        d = runner.join()
        d.addBoth(lambda _: reactor.stop())
    else:
        runner.crawl(chosen_spider)

    reactor.run(installSignalHandlers=False)
    runner.signals.connect(close_reactor_if_no_spiders, signal=signals.spider_closed)
    finish_btn["state"] = "normal"


def close_reactor_if_no_spiders():
    running_spiders = [spider for spider in iter_all('Spider')]
    if not running_spiders:
        reactor.stop()
        finish_btn["state"] = "normal"
        execute_btn["state"] = "disabled"
        stop_btn["state"] = "disabled"
        print("No spiders")


def start_execute_thread(event):
    global execute_thread
    execute_thread = threading.Thread(target=execute_spider, daemon=True)
    execute_thread.start()
    app.after(10, check_execute_thread)


def check_execute_thread():
    if execute_thread.is_alive():
        app.after(10, check_execute_thread)

def stop_thread():
    # execute_thread.stop()
    reactor.stop()
    execute_btn["state"] = "normal"
    finish_btn["state"] = "disabled"
    stop_btn["state"] = "disabled"

def finish_app():
    execute_btn["state"] = "disabled"
    stop_btn["state"] = "disabled"
    finish_btn["state"] = "active"
    app.destroy()
    app.quit()

# def start_execute_thread(event):
#     global execute_thread
#     global execute_threads
#     execute_threads = []
#     if chosen_spider == 'All':
#         with concurrent.futures.ThreadPoolExecutor as executor:
#             t = executor.map(execute_spider)
#             t.start()
#             execute_threads.apped(t)
#     else:
#         execute_thread = threading.Thread(target=execute_spider, daemon=True)
#         execute_thread.start()
#     app.after(10, check_execute_thread)

# def check_execute_thread():
#     if execute_threads:
#         for t in execute_threads:
#             if t.is_alive():
#                 app.after(10, check_execute_thread)
#             else:
#                 stop_btn["state"] = "disabled"
#                 finish_btn["state"] = "normal"
#     else:           
#         if execute_thread.is_alive():
#             app.after(10, check_execute_thread)
#         else:
#             stop_btn["state"] = "disabled"
#             finish_btn["state"] = "normal"


rob10 = ('Roboto (Body)', 10)
rob11 = ('Roboto (Body)', 11)
rob9l_it = ('Roboto (Body)', 9, "italic")
l_grey = "#c6c6c5"
d_grey = '#403d3e'

app = Tk()

spider_label = Label(app, text='Choose a spider', font="Roboto")
spider_label.grid(row=0, column=0, sticky=W, pady=10, padx=10)

spider_text = StringVar(app)
spider_text.set('   ')
global spiders
spiders = ['all']
[spiders.append(spider) for spider in get_spiders()]
# spiders = [spider for spider in get_spiders()]

spiders_dropdown = OptionMenu(
    app, spider_text, *spiders, command=get_chosen_spider)
spiders_dropdown.configure(font=rob11)
spiders_dropdown.grid(row=0, column=1, columnspan=2)

# Feed Type
feed_label = Label(app, text='Choose a feed', font="Roboto")
feed_label.grid(row=1, column=0, sticky=W, pady=10, padx=10)

feed_text = StringVar(app)
feed_text.set('   ')
feeds = ['DB', 'JSON', 'CSV']

feed_dropdown = OptionMenu(app, feed_text, *feeds, command=get_chosen_feed)
feed_dropdown.configure(font=rob10)
feed_dropdown.grid(row=1, column=1, columnspan=2)

# Path Entry
folder_path_text = StringVar(app)
folder_path_entry = Entry(app, textvariable=folder_path_text)
folder_path_entry.configure(font=rob11)
folder_path_entry.grid(row=2, column=0, pady=(10,0), padx=10)
folder_path_entry.insert(0, f"{os.getcwd()}/article_files")
path_label = Label(app, text='Path', font=rob9l_it, fg=l_grey)
path_label.grid(row=3, column=0, sticky=W, pady=(0,6.18), padx=10)

# file Entry
file_text = StringVar(app)
file_entry = Entry(app, textvariable=file_text, width=10, font="Roboto")
file_entry.configure(font=rob11)
file_entry.grid(row=2, column=1, pady=(10,0), padx=10)
file_label = Label(app, text='File name', font=rob9l_it, fg=l_grey)
file_label.grid(row=3, column=1, sticky=W, pady=(0,6.18), padx=10)


browse_btn = Button(app, text='Browse', font="Roboto", command=browse_button, fg='#000000', bg='#d3ab95', borderless=1, relief=RAISED,
                    activebackground=('#DCBCAA', '#E5CDBF'), activeforeground='#FFFFFF', takefocus=0, focuscolor='#E5CDBF')
browse_btn.grid(row=2, column=2, pady=(10,0), padx=1)

execute_btn = Button(app, text='Execute', font="Roboto", command=lambda: start_execute_thread(None), fg='#000000', bg='#d3ab95', borderless=1,
                     activebackground=('#DCBCAA', '#E5CDBF'), activeforeground='#FFFFFF', takefocus=0, focuscolor='#E5CDBF',
                     disabledbackground='#d3ab95', disabledforeground=d_grey)
execute_btn.grid(row=4, column=0, columnspan=1, padx=0)

stop_btn = Button(app, text='Stop', font="Roboto", command=stop_thread, fg='#000000', bg='#d3ab95', borderless=1, relief=RAISED,
                     activebackground=('#DCBCAA', '#E5CDBF'), activeforeground='#FFFFFF', takefocus=0, focuscolor='#E5CDBF',
                     disabledbackground='#d3ab95', disabledforeground=d_grey)
stop_btn.grid(row=4, column=1, columnspan=1, padx=1)
stop_btn["state"] = "disabled"

finish_btn = Button(app, text='Finish', font="Roboto", command=lambda: finish_app(), fg='#000000', bg='#d3ab95', borderless=1, relief=RAISED,
                     activebackground=('#DCBCAA', '#E5CDBF'), activeforeground='#FFFFFF', takefocus=0, focuscolor='#E5CDBF',
                     disabledbackground='#d3ab95', disabledforeground=d_grey)
finish_btn.grid(row=4, column=2, columnspan=1, padx=1)
finish_btn["state"] = "disabled"

app.title('FiScrape')
# app.geometry('445x170')
app.resizable(False, False)
# app.eval('tk::PlaceWindow . center')
phi_align(app, 374, 175)
app.mainloop()
if search_win:
    app.wait_window(search_win)
