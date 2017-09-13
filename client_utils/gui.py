"""
This module contains the Graphical User Interface
"""

from Tkinter import *
import tkMessageBox as tkmb

WINDOW_TITLE = 'Chat'
APP_WINDOW_WIDTH = 800
APP_WINDOW_HEIGHT = 780
CHAT_PAD = 20
INPUT_PAD = 20
CHAT_BORDER_WIDTH = 5
CHAT_FRAME_WIDTH = APP_WINDOW_WIDTH - CHAT_PAD * 2
CHAT_FRAME_HEIGHT = 500
INPUT_FRAME_HEIGHT = 200
INPUT_STARTER_WIDTH = 3
FONT = 'Sans-serif'
BACKGROUND_COLOR = '#404552'
DISABLED_BG_COLOR = '#161616'
QUIT_COMMAND = 'quit'
MAX_INPUT_LEN = 256
MAX_INPUT_INDEX = 1.256
CHAT_FRAME_BG = 'black'
CHAT_CONTENT_FG = 'green'
CHAT_CONTENT_BG = 'black'
INPUT_FRAME_BG = 'black'
INPUT_CONTENT_FG = 'green'
INPUT_CONTENT_BG = 'black'
CHAR_COUNTER_BG = 'black'
CHAR_COUNTER_FG = 'green'
BORDER_RELIEF = 'sunken'
INPUT_STARTER_CONTENT = '>>'
BORDER_WIDTH = '0'
PACK_PROPAGATE_VALUE = '0'
INPUT_FRAME_SIDE = 'top'
INPUT_CONTENT_SIDE = 'left'
INPUT_STARTER_SIDE = 'left'
CHAT_FRAME_SIDE = 'top'
CHAT_CONTENT_SIDE = 'left'
SCROLL_SIDE = 'right'
CHAR_COUNTER_FRAME_SIDE = 'top'
CHAR_COUNTER_SIDE = 'left'
EXIT_POPUP_TITLE = 'Quit'
EXIT_POPUP_QUESTION = 'Are you sure you want to quit?'


class GUI(object):
    """
    This class is used for the graphical interface
    It is used by the chat client to display the chat
    """
    def __init__(self, chat_client):
        """
        The class constructor
        :param chat_client: a chat client
        """
        self.running = False
        self.chat_client = chat_client
        self.root = Tk(className='Chat')
        self.root.bind('<Shift-Return>', self.add_new_input_line)
        self.root.bind('<Return>', self.send_input)
        self.root.bind('<Key>', self.update_char_counter)
        self.root.bind_class('Text', '<Control-a>', self.select_all)
        self.root.protocol("WM_DELETE_WINDOW", self.ask_quit_gui)
        self.root.config(width=APP_WINDOW_WIDTH, height=APP_WINDOW_HEIGHT, background=BACKGROUND_COLOR)

        # Chat frame
        self.chat_frame = Frame(self.root, width=CHAT_FRAME_WIDTH, height=CHAT_FRAME_HEIGHT,
                                borderwidth=CHAT_BORDER_WIDTH, relief=BORDER_RELIEF, background=CHAT_FRAME_BG)
        self.chat_frame.pack(side=CHAT_FRAME_SIDE, pady=CHAT_PAD, padx=CHAT_PAD)
        self.chat_frame.pack_propagate(PACK_PROPAGATE_VALUE)

        self.chat_content = Text(self.chat_frame, borderwidth=BORDER_WIDTH, background=CHAT_CONTENT_BG,
                                 foreground=CHAT_CONTENT_FG, font=FONT)
        self.chat_content.pack(side=CHAT_CONTENT_SIDE, fill='both', expand=True)

        self.scroll = Scrollbar(self.chat_frame, command=self.chat_content.yview)
        self.scroll.pack(side=SCROLL_SIDE, fill='y', expand=False)
        self.chat_content['yscrollcommand'] = self.scroll.set

        # Input frame
        self.input_frame = Frame(self.root, width=CHAT_FRAME_WIDTH, height=INPUT_FRAME_HEIGHT
                                 , borderwidth=CHAT_BORDER_WIDTH, relief=BORDER_RELIEF, background=INPUT_FRAME_BG)
        self.input_frame.pack_propagate(PACK_PROPAGATE_VALUE)
        self.input_frame.pack(side=INPUT_FRAME_SIDE, padx=INPUT_PAD)

        self.input_content_starter = Text(self.input_frame, borderwidth=BORDER_WIDTH, width=INPUT_STARTER_WIDTH
                                          , background=INPUT_CONTENT_BG, foreground=INPUT_CONTENT_FG, font=FONT)
        self.input_content_starter.pack(side=INPUT_STARTER_SIDE)

        self.input_content = Text(self.input_frame, borderwidth=BORDER_WIDTH, background=INPUT_CONTENT_BG
                                  , foreground=INPUT_CONTENT_FG, font=FONT, insertbackground=INPUT_CONTENT_FG)
        self.input_content.pack(side=INPUT_CONTENT_SIDE)

        # Input character counter (256 is max)
        self.input_char_count_frame = Frame(self.root, width=INPUT_STARTER_WIDTH * 2, height=2
                                            , relief=BORDER_RELIEF, background=CHAR_COUNTER_BG)
        self.input_frame.pack_propagate(PACK_PROPAGATE_VALUE)
        self.input_char_count_frame.pack(side=CHAR_COUNTER_FRAME_SIDE)
        self.input_char_count = Text(self.input_char_count_frame, width=len(str(MAX_INPUT_LEN)), height=1
                                     , background=CHAR_COUNTER_BG, foreground=CHAR_COUNTER_FG, font=FONT)
        self.input_char_count.pack(side=CHAR_COUNTER_SIDE)

        self.input_char_count.config(state=DISABLED)
        self.chat_content.config(state=DISABLED)
        self.input_content_starter.insert(index='0.0', chars=INPUT_STARTER_CONTENT)
        self.input_content_starter.config(state=DISABLED)
        self.input_content.config(state=DISABLED)
        self.input = self.input_content
        self.root.pack_propagate(0)

    def start_gui(self, title=WINDOW_TITLE):
        """
        Runs the GUI application
        :param title: the title of the window
        *main loop - blocks program*
        """
        self.root.title(title)
        self.update_char_counter()
        self.running = True
        self.root.mainloop()

    def ask_quit_gui(self):
        """
        Asks the user whether to exit the GUI application or not
        If the user answers yes, a quit command is sent to the server
        and closes the socket and gui
        """
        if tkmb.askokcancel(EXIT_POPUP_TITLE, EXIT_POPUP_QUESTION, icon=tkmb.QUESTION, parent=self.root):
            try:
                self.chat_client.client.close()
            except:
                pass
            self.exit_gui()

    def exit_gui(self):
        """
        Quits the gui application
        """
        self.running = False
        self.root.destroy()

    def select_all(self, event):
        """
        Selects all text in focused widget
        :param event: The event of key detection
        """
        event.widget.tag_add(SEL, '1.0', END)

    def display_connection_status(self, status):
        """
        Only runs once to inform the user if the connection to the server
        was was established of failed
        :param status: boolean indicating the connection status (False=failed, True=established)
        """
        if not status:
            self.display_message('Could not connect to the server.')
            self.disable_input()
        else:
            self.display_message('Connection established.')
            self.enable_input()

    def disable_input(self):
        """
        Disables the user's ability to type input
        Changes the background color of the input field to the disabled color
        """
        self.input_content.config(state=DISABLED)
        self.input_content.config(background=DISABLED_BG_COLOR)
        self.input_content_starter.config(background=DISABLED_BG_COLOR)

    def enable_input(self):
        """
        Enables the user's ability to type input
        Changes the background color of the input field to the normal color
        """
        self.input_content.config(state=NORMAL)
        self.input_content.config(background=INPUT_CONTENT_BG)
        self.input_content_starter.config(background=INPUT_CONTENT_BG)

    def update_char_counter(self, event=None):
        """
        Updates the character counter to match the user's input length
        :param event: The event of key detection (None by default as it is run
        by the start_gui function)
        """
        self.input_char_count.config(state=NORMAL)
        input_length = len(self.input_content.get('0.0', END).strip())
        if input_length > MAX_INPUT_LEN:
            self.input_content.delete(MAX_INPUT_INDEX, END)
            input_length = MAX_INPUT_LEN
        char_count = MAX_INPUT_LEN - input_length
        self.input_char_count.delete('0.0', END)
        self.input_char_count.insert(END, chars=str(char_count))
        self.input_char_count.config(state=DISABLED)

    def add_new_input_line(self, event):
        """
        Adds a new line to the input field
        :param event: The event of key detection
        """
        self.input_content.insert(END, '')

    def add_new_chat_line(self):
        """
        Adds a new line to the chat field
        """
        self.chat_content.insert(END, '\n')

    def send_input(self, event):
        """
        Sends the user's input to the server (also deleting the input text)
        :param event: The event of key detection
        :return: "break" in order to stop further tkinter analysis of the event
        """
        text = self.input.get('0.0', END).strip()
        # cannot send only white space (pure spaces are the equivalent of an empty message)
        if text != '':
            self.chat_client.client.send_regular(text)
        self.input.delete('0.0', END)
        self.update_char_counter()
        return "break"

    def display_message(self, content):
        """
        Displays a message in the chat frame
        :param content: the string which is displayed
        """
        self.chat_content.config(state=NORMAL)
        self.chat_content.insert(END, content)
        self.add_new_chat_line()
        self.chat_content.config(state=DISABLED)
        self.chat_content.see(END)


def main():
    g = GUI(None)
    g.start_gui()

if __name__ == '__main__':
    main()
