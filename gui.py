from tkinter import *
import indexer
import webbrowser

#from: http://effbot.org/zone/tkinter-text-hyperlink.htm
class HyperlinkManager:
    def __init__(self, text):
        self.text = text

        self.text.tag_config("hyper", foreground="blue", underline=1)

        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)

        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        # add an action to the manager.  returns tags to use in
        # associated text widget
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag]()
                return

class UI:
    def __init__(self):
        self.root = Tk()
        self.text = []
        self.frame = None
        self.query = ''
        self.serving_size = ''
        #self.indexer = indexer()
        self.go = None


    def run(self):
        self.root.wm_title("121 Search Engine")
        self.root.config(background = '#d3f7e0')
        self.root.resizable(False, False)

        self.start_screen()
    
        self.root.mainloop()


    def start_screen(self):
        Label(self.root, text='         Enter Query         ', bg='#d3f7e0', font=('times', 16, 'bold')).grid(row=0,
                                                   column=0, padx=10, pady=2)
        self.query = Entry(self.root)
        self.query.grid(row=1, column=0)
        
        self.go = Button(self.root, text='         GO         ',
               command=self._raise_infof, bg='#ba8c59')
        self.go.grid(row=2, column=0, padx=10, pady=2)

        Label(self.root, text='AUTHORS: Aishwarya B., Cynthia W., Bhavani P.', bg='#d3f7e0').grid(row=5, column=0, padx=10, pady=2)
        
    def second_screen(self):
        Label(self.root, text='         Entered Query         ', bg='#d3f7e0', font=('times', 16, 'bold')).grid(row=0,
                                                   column=0, padx=10, pady=2)
        self.go.destroy()
        Label(self.root, text='                                  ', bg='#d3f7e0').grid(row=2, column=0, padx=10, pady=2)

        t = Text(self.frame, height= 15,
                     width= 50, bg='#e9fdf0', fg='black')
        t.grid(row=3, column=0, padx=10, pady=2, sticky='nsew')

        hyperlink = HyperlinkManager(t)
        for i in self.text:
            t.insert(INSERT, i, hyperlink.add(lambda i=i: webbrowser.open(i)))
            t.insert(INSERT, "\n\n")

        s = Scrollbar(self.frame, command=t.yview)
        s.grid(row=3, column=1, padx=10, pady=2, sticky='nsew')
        t['yscrollcommand']=s.set

        self._make_back_button()
        
    def _make_back_button(self):
        Button(self.root, text='    Back    ',
               command=self.destroy_world, bg='#ba8c59').grid(row=4, column=0)

    def destroy_world(self):
        self.root.destroy()
        self.root=Tk()
        self.run()
        
    
    def _make_frame(self, color):
        self.frame = Frame(self.root, width=500, height=495,
              background = color).grid(row=3, column=0, padx=10, pady=2)
        

    def _raise_infof(self):
        try:
            url_text = ''
            url_text = self.query.get()
            self.text = self.get_analytics(url_text)
            infof = self._make_frame('#ffccff')
            self.second_screen()
            if self.query != None:
                self.query.destroy()
        except TypeError:
            self.start_screen()
        
    def get_analytics(self, q: str):
        try:
            if q == None or q == '':
                raise TypeError
            else:
                sorted_i = indexer.analytics(q)
                self.query = q
                return sorted_i
        except AttributeError:
            raise TypeError


if __name__ =='__main__':
    UI().run()

