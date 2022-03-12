import tkinter as tk
import tkinter.messagebox
from tkinter import filedialog as fd

root = tk.Tk()


def startGui():
    __showHomeScreen()

    root.title('Spotiviz')
    root.geometry('{width}x{height}'.format(
        width=800,
        height=600
    ))

    root.mainloop()


def __showHomeScreen():
    frame = tk.Frame(root)

    title = tk.Label(frame, text='Spotiviz', font=('Times New Roman', 36))
    title.grid(row=0, column=0, pady=10)

    selector = tk.Button(frame, text='Import Data', command=__selectFiles)
    selector.grid(row=1, column=0, pady=10)

    exitButton = tk.Button(frame, text='Exit', command=root.destroy)
    exitButton.grid(row=2, column=0, pady=10)

    frame.pack()


def __selectFiles():
    filename = fd.askopenfilename(
        title='Select Spotify Data'
    )

    tkinter.messagebox.showinfo(
        title='Selected Files',
        message=filename
    )