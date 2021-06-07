from tkinter import *
import requests
import json
import threading
import googleSpeech
import webbrowser

#rasa run -m models --enable-api --cors "*" --debug

# defining the api-endpoint 
API_ENDPOINT = "http://localhost:5005/webhooks/rest/webhook"
headers = {'Content-Type': "application/json",}

#Apariencia
BG_GRAY = "#e0e0e0"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT_SEP2 = "Helvetica 6"
FONT_SEP1 = "Helvetica 4"
FONT = "Helvetica 12"
FONT_BOLD = "Helvetica 10 bold"

class ChatApplication:
    voice_button = None
    grabando = False
    
    def __init__(self):
        self.window = Tk()
        self._setup_main_window()
        self.thGrabar=threading.Thread(target=self.grabar,daemon=True)
        
    def run(self):
        self.window.mainloop()

    def linkTagClick(self,event):
        # get the index of the mouse click
        index = event.widget.index("@%s,%s" % (event.x, event.y))

        # get the indices of all "adj" tags
        tag_indices = list(event.widget.tag_ranges('msg_botLink'))
        # iterate them pairwise (start and end index)
        for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
            # check if the tag matches the mouse click index
            if event.widget.compare(start, '<=', index) and event.widget.compare(index, '<', end):
                # return string between tag start and end
                #print(start, end, event.widget.get(start, end))
                multiples=event.widget.get(start, end).splitlines()
                for mult in multiples:
                    mult=mult.strip()
                    if mult[0]=='[' and mult[len(mult)-1]==']':
                        link=mult[1:len(mult)-1]
                        webbrowser.open(link,new=1)
                
    def linkOnEnter(self,event):
        self.text_widget.config(cursor='hand1')
    def linkOnLeave(self,event):
        self.text_widget.config(cursor='arrow')

    def _setup_main_window(self):
        self.window.title("Asistente Classroom")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=460, height=550, bg=BG_COLOR)
        
        # head label
        head_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR,
                           text="Bienvenido", font=FONT_BOLD, pady=8)
        head_label.place(relwidth=1)
        
        # tiny divider
        line = Label(self.window, width=450, bg=BG_GRAY)
        line.place(relwidth=1, rely=0.07, relheight=0.012)
        
        # text widget
        self.text_widget = Text(self.window, width=20, height=2, bg=BG_COLOR, fg=TEXT_COLOR,
                                font=FONT, padx=5, pady=5)
        self.text_widget.place(relheight=0.8, relwidth=.96, rely=0.08)
        self.text_widget.configure(cursor="arrow", state=DISABLED)
        self.text_widget.tag_config('msg_usuario', justify='right',wrap='word',background='#263647')
        self.text_widget.tag_config('msg_usuarioError', justify='right',wrap='word',background='#263647',foreground='#ed5c5c')
        self.text_widget.tag_config('msg_bot', justify='left',wrap='word',background='#2f4359')
        self.text_widget.tag_config('msg_separacionU', justify='left',wrap='word',font=FONT_SEP2,background='#263647')
        self.text_widget.tag_config('msg_separacionB', justify='left',wrap='word',font=FONT_SEP2,background='#2f4359')
        self.text_widget.tag_config('msg_separacion', justify='left',wrap='word',font=FONT_SEP1)

        self.text_widget.tag_config('msg_botLink', justify='left',wrap='word',background='#2f4359',foreground='#abcbff')
        self.text_widget.tag_bind("msg_botLink", "<Button-1>", self.linkTagClick)
        self.text_widget.tag_bind("msg_botLink", "<Enter>", self.linkOnEnter)
        self.text_widget.tag_bind("msg_botLink", "<Leave>", self.linkOnLeave)
        

        # scroll bar
        scrollbar = Scrollbar(self.window)
        scrollbar.place(relheight=0.8, relx=0.97,rely=0.08)
        scrollbar.configure(command=self.text_widget.yview)
        
        # bottom label
        bottom_label = Label(self.window, bg=BG_GRAY, height=50)
        bottom_label.place(relwidth=1, rely=0.89)
        
        # message entry box
        self.msg_entry = Entry(bottom_label, bg="#2C3E50", fg=TEXT_COLOR, font=FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.05, rely=0.006, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)
        
        # send button
        send_button = Button(bottom_label, text="Enviar", font=FONT_BOLD, width=10, bg=BG_GRAY,
                             command=lambda: self._on_enter_pressed(None))
        send_button.place(relx=0.75, rely=0.006, relheight=0.05, relwidth=0.14)

        # voice button
        self.voice_button = Button(bottom_label, text="Voz", font=FONT_BOLD, width=10, bg=BG_GRAY,
                             command=lambda: self._voice_pressed(None))
        self.voice_button.place(relx=0.89, rely=0.006, relheight=0.05, relwidth=0.11)

    def _on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        self._insert_message(msg, "Tú")

    def _voice_pressed(self,event):
        self.grabando= not self.grabando

        if(self.grabando):
            if not self.thGrabar.isAlive():
                self.thGrabar=threading.Thread(target=self.grabar,daemon=True)
                self.thGrabar.start()
                self.voice_button['text']='Parar'
        else:
            self.voice_button['text']='Voz'
            googleSpeech.grabando=False
            self.msg_entry.delete(0, END)
            self.msg_entry.insert(END,'prediciendo...')
            

    def _insert_message(self, msg, sender):
        
        if not msg:
            return

        self.text_widget.configure(state=NORMAL)
        data = {
            "sender":"ventana_usuario",
            "message":msg
        }

        msgs=[]
        try:
            response = requests.request("POST", API_ENDPOINT, data=json.dumps(data), headers=headers)
            resJson = response.json()        
            for res in resJson:
                msgs.append(res['text'])

            self.msg_entry.delete(0, END)
            msg1 = f"{msg}"
            
            self.text_widget.insert(END,'\n','msg_separacionU')
            self.text_widget.insert(END, msg1+'   ','msg_usuario')
            self.text_widget.insert(END,' \n\n','msg_separacionU')
            self.text_widget.insert(END,'\n','msg_separacion')

        except:
            self.msg_entry.delete(0, END)

            msg1 = f"{msg}(error al enviar)"
            self.text_widget.insert(END,'\n','msg_separacionU')
            self.text_widget.insert(END, msg1+'   ','msg_usuarioError ')
            self.text_widget.insert(END,' \n\n','msg_separacionU')
            self.text_widget.insert(END,'\n','msg_separacion')
            pass
        
        for m in msgs:
            self.text_widget.insert(END,'\n','msg_separacionB')
            
            multiples=m.splitlines()
            esLink=False

            for mult in multiples:
                mult=mult.strip()
                if mult[0]=='[' and mult[len(mult)-1]==']':
                    esLink=True
                
            if esLink:
                self.text_widget.insert(END, '   '+m,'msg_botLink')
            else:
                self.text_widget.insert(END, '   '+m,'msg_bot')

            self.text_widget.insert(END,'\n\n','msg_separacionB')
            self.text_widget.insert(END,'\n','msg_separacion')
        
        self.text_widget.configure(state=DISABLED)
        self.text_widget.see(END)
             
    def grabar(self):
        res=googleSpeech.grabar()
        self.msg_entry.delete(0, END)
        if res:
            res=res.results[0].alternatives[0]
            
            self.msg_entry.insert(END,res.transcript)

if __name__ == "__main__":
    app = ChatApplication()
    app.run()