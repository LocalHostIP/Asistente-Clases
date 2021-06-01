from tkinter import *
import requests
import json
import googleSpeech

#rasa run -m models --enable-api --cors "*" --debug

# defining the api-endpoint 
API_ENDPOINT = "http://localhost:5005/webhooks/rest/webhook"
headers = {'Content-Type': "application/json",}

#Apariencia
BG_GRAY = "#c7ccd1"
BG_COLOR = "#17202A"
TEXT_COLOR = "#EAECEE"

FONT = "Helvetica 12"
FONT_BOLD = "Helvetica 10 bold"


class ChatApplication:
    
    def __init__(self):
        self.window = Tk()
        self._setup_main_window()
        
    def run(self):
        self.window.mainloop()
        
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
        self.text_widget.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_widget.configure(cursor="arrow", state=DISABLED)
        
        # scroll bar
        scrollbar = Scrollbar(self.text_widget)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.configure(command=self.text_widget.yview)
        
        # bottom label
        bottom_label = Label(self.window, bg=BG_GRAY, height=50)
        bottom_label.place(relwidth=1, rely=0.87)
        
        # message entry box
        self.msg_entry = Entry(bottom_label, bg="#2C3E50", fg=TEXT_COLOR, font=FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.006, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)
        
        # send button
        send_button = Button(bottom_label, text="Enviar", font=FONT_BOLD, width=10, bg=BG_GRAY,
                             command=lambda: self._on_enter_pressed(None))
        send_button.place(relx=0.75, rely=0.006, relheight=0.06, relwidth=0.14)

        # voice button
        send_button = Button(bottom_label, text="Voz", font=FONT_BOLD, width=10, bg=BG_GRAY,
                             command=lambda: self._voice_pressed(None))
        send_button.place(relx=0.89, rely=0.006, relheight=0.06, relwidth=0.11)
     
    def _on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        self._insert_message(msg, "Tú")

    def _voice_pressed(self,event):
        print('voice pressed')
        res=googleSpeech.grabar().results[0].alternatives[0]
        print(res.transcript)
        self._insert_message(res.transcript,'Tú')

    def _insert_message(self, msg, sender):
        if not msg:
            return
        
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
            msg1 = f"{sender}: {msg}\n\n"
            self.text_widget.configure(state=NORMAL)
            self.text_widget.insert(END, msg1)
            self.text_widget.configure(state=DISABLED)
        except:
            self.msg_entry.delete(0, END)
            msg1 = f"{sender}: {msg} (error al enviar)\n\n"
            self.text_widget.configure(state=NORMAL)
            self.text_widget.insert(END, msg1)
            self.text_widget.configure(state=DISABLED)
            pass
        
        for m in msgs:
            self.text_widget.configure(state=NORMAL)
            self.text_widget.insert(END, m+"\n\n")
            self.text_widget.configure(state=DISABLED)
        
        self.text_widget.see(END)
             
if __name__ == "__main__":
    app = ChatApplication()
    app.run()
    