import customtkinter
import tkinter as tk
import random
import sqlite3
from datetime import datetime
import webbrowser
from hexagrams import HEXAGRAMS
import secrets
import urllib.request
from urllib.error import URLError


customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green

# Connect to the database
conn = sqlite3.connect("hexagram.db")
c = conn.cursor()

# Create the table if it does not exist
c.execute(
	"""CREATE TABLE IF NOT EXISTS hexagrams
			 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
			  date_time TEXT,
			  question TEXT,
			  hexagram_number INTEGER,
			  changing_lines INTEGER,
			  transformed_hexagram_number INTEGER)"""
)
conn.commit()

# Close the connection to the database
conn.close()

# Hexagram data
# Hexagram data


#main function
def generate_hexagram():    
    hexagram_change_label.configure(text="No Changes")
    transformed_hexagram_name_label.configure(text="")
    transformed_hexagram_char_label.configure(text="")
    hex_ = throw_hexagram()
    title = lookup_hexagram_title(hex_)
    piccy= lookup_hexagram_visual(hex_)
    #lines = render_lines(hex_)
    hex_out = f"Hexagram: {title}"
    hexagram_name_label.configure(text=title)
    hexagram_char_label.configure(text=piccy)
    print(hex_out)
    if 6 in hex_ or 9 in hex_:
        next_hex = transform_changing_lines(hex_)
        next_title = lookup_hexagram_title(next_hex)
        next_piccy = lookup_hexagram_visual(next_hex)
        next_out = f"Changing to: {next_title}"
        index_number=1
        transformed_hexagram_char_label.configure(text=next_piccy)
        hexagram_change_label.configure(text="Changing to:")
        transformed_hexagram_name_label.configure(text=next_title)
        print(next_out)
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    question = question_entry.get()
    conn = sqlite3.connect("hexagram.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO hexagrams (date_time, question, hexagram_number, changing_lines, transformed_hexagram_number) VALUES (?, ?, ?, ?, ?)", (date_time, question, hex_out, index_number, next_out),
        )
    conn.commit()
    conn.close()
    hex_num = int(binary_hexagram(hex_), 2) + 1
    hex_out = f"Hexagram: {hex_num}"
    # Set default text for input box
    question_entry.delete(0, 'end')
    question_entry.configure()


def throw_hexagram():
    url = (
        "https://www.random.org/integers/"
        "?num=6&min=0&max=15&col=6&base=10&format=plain&rnd=new"
    )
    try:
        get = urllib.request.urlopen(url).read().decode("utf-8").strip()
        throw = get.split("\t")
        throw = [int(i) for i in throw]
    except URLError:
        throw = [secrets.randbelow(16) for i in range(6)]
    prob = [6, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9]
    hexagram = []
    for i in throw:
        x = prob[i]
        hexagram.append(x)
    return hexagram
    

#####here I need to put the changing line identification into a variable and/or label

    # Loop through each line and print whether it is a six or a nine
    for i, line in enumerate(hexagram):
        if line == 6:
            print(f"Line {i+1} is changing")
        elif line == 9:
            print(f"Line {i+1} is changing")
    
    return hexagram


def binary_hexagram(hexagram):
    binary_list = []
    for i in hexagram:
        if i in (7, 9):
            binary_list.append("1")
        else:
            binary_list.append("0")
    binary_hexagram = "".join(binary_list)
    return binary_hexagram


def lookup_hexagram_title(hexagram):
    bingram = binary_hexagram(hexagram)
    web_hex = HEXAGRAMS[bingram][:2] # Extract first two characters of the title
    web_hex=web_hex.replace(".", "")
    url = f"https://www.jamesdekorne.com/GBCh/hex{web_hex}.htm"
    webbrowser.open_new(url)
    title=HEXAGRAMS[bingram]
    return title

def lookup_hexagram_visual(hexagram):
    bingram = binary_hexagram(hexagram) 
    visual = HEXAGRAMS[bingram][-1]
    print(visual)
    return visual

def transform_changing_lines(hexagram):
    new_hexagram = []
    for i in hexagram:
        if i == 6:
            i = 7
        elif i == 9:
            i = 8
        new_hexagram.append(i)
    return new_hexagram

def show_records():
    # This function will be called when the "Show Records" button is clicked
    conn = sqlite3.connect("hexagram.db")
    c = conn.cursor()
    
    # Query the records
    c.execute("SELECT rowid, * FROM hexagrams")
    records = c.fetchall()
    
    # Create a new window to display the records
    records_window = customtkinter.CTkToplevel(root)
    records_window.title("Hexagram Records")
    records_window.geometry("1000x700")
    # Create a scrollable frame to hold the records
    canvas = customtkinter.CTkCanvas(records_window, borderwidth=0)
    frame = customtkinter.CTkFrame(canvas)
    scrollbar = customtkinter.CTkScrollbar(records_window, command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=frame, anchor="nw")
    frame.bind("<Configure>", lambda event, canvas=canvas: canvas.configure(scrollregion=canvas.bbox("all")))
    
    # Display the records in the frame
    for row in records:
        record_id = row[0]
        label = customtkinter.CTkLabel(frame, text=f"{row[1]} {row[2]} {row[3]}")
        label.pack()
        button = customtkinter.CTkButton(frame, text="View details", command=lambda id=record_id: show_record_details(id))
        button.pack()
    
    conn.close()

def show_record_details(record_id):
    # This function will be called when the "View details" button is clicked
    conn = sqlite3.connect("hexagram.db")
    c = conn.cursor()
    
    # Query the details of the selected record
    c.execute("SELECT * FROM hexagrams WHERE rowid = ?", (record_id,))
    record = c.fetchone()
    
    # Create a new window to display the record details
    details_window = customtkinter.CTkToplevel(root)
    details_window.title(f"Details of Record {record[0]}")
    details_window.geometry("500x300")
    
    # Display the details in the window
    for i in range(len(record)):
        label = customtkinter.CTkLabel(details_window, text=f"{c.description[i][0]}: {record[i]}")
        label.pack()
    
    conn.close()

# Create the main window
root = customtkinter.CTk()
root.title("Hexagram Generator")
root.geometry("700x400")


# Create the input box widget
question_entry = customtkinter.CTkEntry(root, font=("Arial", 12))
question_entry.pack(pady=10, padx=10, fill=customtkinter.BOTH)

# Set default text for input box
question_entry.insert(0, "Enter your question...")
question_entry.configure()
#question_entry.bind("<FocusIn>", clear_default_text)

# Bind FocusIn event to clear default text
def clear_default_text(event):
    if question_entry.get() == "Enter your question...":
        question_entry.delete(0, "end")
        question_entry.configure()

# Create the button widgets
button_frame = customtkinter.CTkFrame(root)
button_frame.pack(side="bottom", pady=10, padx=10)
button = customtkinter.CTkButton(button_frame, text="Generate Hexagram", font=("Arial", 12), command=generate_hexagram)
button.pack(side="left", padx=5)
show_records_button = customtkinter.CTkButton(button_frame, text="View History", font=("Arial", 12), command=show_records)
show_records_button.pack(side="right", padx=5)

# Create a frame to hold the hexagram display
hexagram_frame = customtkinter.CTkFrame(root)
hexagram_frame.pack(pady=20)

# Label to display the hexagram 
hexagram_char_label = customtkinter.CTkLabel(hexagram_frame, font=("Arial", 40), text="")
hexagram_char_label.pack()


# Label to display the hexagram name
hexagram_name_label = customtkinter.CTkLabel(hexagram_frame, font=("Arial", 16), text="")
hexagram_name_label.pack()

# Label to display the hexagram changing line
hexagram_change_label = customtkinter.CTkLabel(hexagram_frame, font=("Arial Unicode MS", 16), text="")
hexagram_change_label.pack()

# Label to display the transformed_hexagram name
transformed_hexagram_char_label = customtkinter.CTkLabel(hexagram_frame, font=("Arial", 40), text="")
transformed_hexagram_char_label.pack()

# Label to display the transformed_hexagram name
transformed_hexagram_name_label = customtkinter.CTkLabel(hexagram_frame, font=("Arial", 16), text="")
transformed_hexagram_name_label.pack()

#space label
space_label = customtkinter.CTkLabel(hexagram_frame, font=("Arial", 16), text="   ") 
transformed_hexagram_name_label.pack()

# Start the main event loop
root.mainloop()