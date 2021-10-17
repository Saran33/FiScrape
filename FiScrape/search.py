
from datetime import date, datetime, timedelta
from tkinter import Canvas, PhotoImage
from pytz import timezone
# from scrapy.utils import project
import sys

todays_date = date.today()
today = todays_date.strftime("%B %-d, %Y")


def search_input(**kwargs):
    # print(sys.argv)
    global query
    global start_date
    if 'test' not in sys.argv:
        if not 'query' in kwargs:
            query = input('Enter a search term: ').replace(' ', '+')
        elif 'query' in kwargs:
            query = kwargs['query']
        if query == 'b':
            query = 'bitcoin'
        if not 'start_date' in kwargs:
            start_date = input(
                'Enter a start date in Y/M/D (e.g. 2021-02-22): ')
        elif 'start_date' in kwargs:
            start_date = kwargs['start_date']
        if start_date == 'y':
            start_date = '2021-01-01'
        elif start_date == 't':
            start_date = datetime.utcnow()
            start_date = start_date.replace(
                hour=0, minute=0, second=0, microsecond=0)
        elif start_date == 'yd':
            start_date = datetime.utcnow()
            start_date = start_date.replace(
                hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
        elif start_date == 'w':
            start_date = datetime.utcnow()
            start_date = start_date.replace(
                hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
        elif start_date == 'm':
            start_date = datetime.utcnow()
            start_date = start_date.replace(
                hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
        if type(start_date) is str:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        start_date = timezone("UTC").localize(start_date)
        print('Getting articles on: ' + query + '...\n')

    else:
        query = None
        start_date = None

    return query, start_date


# For running Fiscrape GUI:
if 'fiscrape_gui.py' in sys.argv:
    from tkinter import Tk, Label, StringVar, Entry, Button, W, Frame, HORIZONTAL, EW
    from tkinter.ttk import Progressbar, Style
    # from tkinter import *
    from FiScrape.tools import phi_align
    if sys.platform == 'darwin':
        from tkmacosx import Button as OSXButton

    skin = '#DCBBA6'
    grey = '#64646F'

    def get_search(search_win, search_entry, date_entry):
        search_query = search_entry.get()
        start_dt = date_entry.get()
        query, start_date = search_input(
            query=search_query, start_date=start_dt)
        search_win.destroy()
        return query, start_date

    def end_splash(splash_win):
        return splash_win.destroy()

    splash_win = Tk()
    win_w = 427
    win_h = 250
    phi_align(splash_win, win_w, win_h)

    splash_win.overrideredirect(1)

    # s = Style()
    # s.theme_use('clam')
    # s.configure("red.Horizontal.TProgressbar",
    #             foreground=grey, background=skin)
    # progress = Progressbar(splash_win, style="red.Horizontal.TProgressbar",
    #                        orient=HORIZONTAL, length=440, mode='indeterminate')  # determinate
    # # progress.grid(row=0, column=0, sticky=EW, padx=10, pady=10)

    progress = Progressbar(splash_win, orient=HORIZONTAL, length=100, mode='indeterminate')
    progress.pack(pady=0)

    def search_window():
        global search_win
        search_win = Tk()
        search_win.title('FiScrape')

        # Search Entry
        search_label = Label(search_win, text="Search term:", font=('Roboto (Body)', 12))
        search_label.grid(row=0, column=0, sticky=W, pady=10, padx=10)
        search_text = StringVar(search_win)
        search_entry = Entry(search_win, textvariable=search_text, width=10, font=('Roboto (Body)', 11))
        search_entry.grid(row=0, column=1, pady=10, padx=10)

        # Start date
        date_label = Label(search_win, text="Start date:", font=('Roboto (Body)', 12))
        date_label.grid(row=1, column=0, sticky=W, pady=10, padx=10)
        date_string = StringVar(search_win)
        date_entry = Entry(search_win, textvariable=date_string, width=10, font=('Roboto (Body)', 11))
        date_entry.grid(row=1, column=1, pady=10, padx=10)
        date_entry.insert(0, "2021-09-30")

        next_btn = OSXButton(search_win, text='Next', command=lambda: get_search(search_win, search_entry, date_entry),
                             fg='#000000', bg='#d3ab95', borderless=1, activebackground=('#DCBCAA', '#E5CDBF'),
                             activeforeground='#FFFFFF', takefocus=0, focuscolor='#E5CDBF')
        next_btn.grid(row=2, column=1, columnspan=3)

        search_win.title('FiScrape')
        search_win.resizable(False, False)
        phi_align(search_win, 233, 144)

        search_win.mainloop()

    
    # def splash_root():
    #     import time
    #     global ext, count
    #     count = 0
    #     ext = 3.59
    #     bg_canvas.create_text(50, 210, text='Loading...', fill='black', font=('Roboto (Body)', 11))
    #     if count < 3000:
    #         bg_canvas.create_arc(10, 10, 200, 200, extent=ext, fill=grey, width=0)
    #         ext += 3.59
    #         count += 1
    #         splash_win.update_idletasks()
    #         time.sleep(0.1)
        
    #     splash_win.destroy()
    #     search_window()
    # progress.place(x=10, y=235)


    def splash_root():

        # Load_label = Label(splash_win, text='Loading...', fg='black', bg=skin)
        # load_st = ('Roboto (Body)', 10)
        # Load_label.config(font=load_st)
        # Load_label.place(x=18, y=210)
        # bg_canvas.create_text(50, 210, text='Loading...', fill='#000000', font=('Roboto (Body)', 11))

        import time
        t = 0
        for t in range(100):
            bg_canvas.itemconfig(prog_label, text=progress['value'])
            progress['value'] = t
            splash_win.update_idletasks()
            time.sleep(0.03)
            t = t+1

        splash_win.destroy()
        search_window()

    progress.place(x=10, y=235)

    # Adding a frame
    Frame(splash_win, width=427, height=241, bg=skin).place(x=0, y=0)
    bg_img = PhotoImage(file='images/PWE_FiScrape_splash.png')
    bg_canvas = Canvas(splash_win, width=win_w, height=win_h)
    bg_canvas.pack(fill="both", expand=True)
    bg_canvas.create_image(0, 0, image=bg_img, anchor="nw")

    bg_canvas.create_text(238, 165, text="FiScrape", fill='white', font=('Roboto (Body)', 26))
    prog_label = bg_canvas.create_text(150, 200, text="", fill='black', font=('Roboto (Body)', 11))
    bg_canvas.create_text(50, 210, text='Loading...', fill=grey, font=('Roboto (Body)', 11))

    # Spash screen timer
    splash_win.after(500, splash_root)

    splash_win.mainloop()

# For running Fiscrape CLI:
if not 'fiscrape_gui.py' in sys.argv:
    global query
    global start_date
    if 'test' not in sys.argv:
        query, start_date = search_input()
    else:
        query = None
        start_date = None
