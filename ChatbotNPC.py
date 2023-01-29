import tkinter
from tkinter import Variable, StringVar, IntVar, DoubleVar, BooleanVar
import customtkinter

from transformers import AutoModelWithLMHead, AutoModelForCausalLM, AutoTokenizer
import torch

class ChatbotApplication:

    def __init__(self, title, window_size="854x480", mode="dark", color_theme="blue"):
        # initialize AI
        #self.AI_tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        #self.AI_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")

        self.AI_tokenizer = AutoTokenizer.from_pretrained("DialoGPT-small-HanSolo")
        self.AI_model = AutoModelForCausalLM.from_pretrained("DialoGPT-small-HanSolo")

        self.chat_history_ids = 0
        self.is_first_message = True

        # initialize interface
        customtkinter.set_appearance_mode(mode) # Modes: "System" (standard), "Dark", "Light"
        customtkinter.set_default_color_theme(color_theme)  # Themes: "blue" (standard), "green", "dark-blue"

        self.interface = customtkinter.CTk()
        self.interface.geometry(window_size)
        self.interface.title(title)
        self.interface.bind('<Return>', self.enter_user_text)

        # create interface
        self.create_chatbot_interface()

    def run(self):
        self.interface.mainloop()

    # ------------------------
    # -- Interface creation --
    # ------------------------

    def create_chatbot_interface(self):
        # create main frame
        main_frame = customtkinter.CTkFrame(master=self.interface)
        main_frame.columnconfigure(tuple(range(3)), weight=1)  # auto resize
        main_frame.rowconfigure(tuple(range(3)), weight=1)  # auto resize
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # add everything
        title_label = customtkinter.CTkLabel(master=main_frame, text="NPC chat", font=('Arial', 27))
        title_label.pack(pady=30, padx=10, fill="x", expand=False)

        self.create_chatbox(master=main_frame)

        self.create_text_input(master=main_frame)

    def create_chatbox(self, master):
        grid = customtkinter.CTkFrame(master=master, fg_color="transparent")
        grid.columnconfigure(tuple(range(1)), weight=1)  # auto resize
        grid.rowconfigure(tuple(range(1)), weight=1)  # auto resize
        grid.pack(pady=(0, 10), padx=20, fill="both", expand=True)

        self.textbox = customtkinter.CTkTextbox(master=grid, width=200, height=70, font=('Arial', 16))
        self.textbox.grid(row=0, column=0, pady=(0, 10), padx=10, sticky="news")

        self.textbox.tag_config('npc', background="black", foreground="lightblue")
        self.textbox.tag_config('user', foreground="white")

        self.textbox.configure(state="disabled")

    def create_text_input(self, master):
        grid = customtkinter.CTkFrame(master=master, height=48, fg_color="transparent")
        grid.columnconfigure(tuple(range(1)), weight=1) # auto resize
        grid.pack(pady=(0, 10), padx=20, fill="x", expand=False)

        self.entry_text: StringVar = StringVar()
        text_entry = customtkinter.CTkEntry(master=grid, width=900, placeholder_text="Enter your message here", textvariable=self.entry_text)
        text_entry.grid(row=0, column=0, pady=(0, 10), padx=(10, 5), sticky="news")

        enter_button = customtkinter.CTkButton(master=grid, text="Enter", width=70, command=self.enter_user_text)
        enter_button.grid(row=0, column=1, pady=(0, 10), padx=(5, 10))

    # ---------------------------
    # -- Interface interaction --
    # ---------------------------

    def enter_user_text(self, event=None):
        # TODO: don't allow to execute (return) if AI is still busy
        if len(self.entry_text.get()) == 0:
            return

        self.add_message(prefix="You: ", message=self.entry_text.get(), tag='user')
        self.enter_AI_text()
        self.entry_text.set("")

    def enter_AI_text(self):
        self.add_message(prefix="NPC: ", message=self.generate_AI_response(), tag='npc')

    def add_message(self, prefix: str, message: str, tag):
        self.textbox.configure(state="normal", text_color="light blue")
        self.textbox.insert("end", "\n" + prefix + message + "\n\n", tag)
        self.textbox.configure(state="disabled")
        self.textbox.see("end")

    # ---------------------
    # -- Other functions --
    # ---------------------

    def generate_AI_response(self) -> str:
        input_text = self.entry_text.get()

        # encode the new user input, add the eos_token and return a tensor in Pytorch
        new_user_input_ids = self.AI_tokenizer.encode(input_text + self.AI_tokenizer.eos_token, return_tensors='pt')
        bot_input_ids = torch.cat([self.chat_history_ids, new_user_input_ids], dim=-1) if not self.is_first_message else new_user_input_ids

        # generate a response while limiting the total chat history to max_allowed_tokens

        #self.chat_history_ids = self.AI_model.generate(bot_input_ids, max_length=1000, pad_token_id=self.AI_tokenizer.eos_token_id, temperature=0.6, repetition_penalty=1.3)
        self.chat_history_ids = self.AI_model.generate(bot_input_ids, max_new_tokens=200, pad_token_id=self.AI_tokenizer.eos_token_id, do_sample=True, top_k=50, top_p=0.95, no_repeat_ngram_size=3)
        #self.chat_history_ids = self.AI_model.generate(bot_input_ids, max_length=1000, pad_token_id=self.AI_tokenizer.eos_token_id, do_sample=True, top_k=100, top_p=0.7, temperature=0.8, no_repeat_ngram_size=3)

        output_text = "{}".format(self.AI_tokenizer.decode(self.chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True))

        self.is_first_message = False
        return output_text

# main()
if __name__ == "__main__":
    app = ChatbotApplication(title="NPC Chatbot", window_size="1280x720")
    app.run()
