from tkinter import *
from tkinter import messagebox
from numpy import *
import pandas as pd
import sqlite3
# SQLite3 automatically creates the PRIMARY_KEY

def removeDuplicates(og_list):
    list = []
    for item in og_list:
        list.append(item)
    # The list MUST be sorted
    i = 0
    lengthOfList = len(list)
    while i < lengthOfList - 1:
        if list[i] == list[i+1]:
            del list[i+1]
            lengthOfList -= 1
            i -= 1
        i += 1
    return list

def buildDatabase():
    # Import Excel spreadsheet as dataframe
    antoinesCoefficients_dataframe = pd.read_excel("antoinesCoefficients.xlsx")
    numRows = antoinesCoefficients_dataframe.shape[0]
    # Creating/connecting to a databse for heat capacity coefficients
    antoinesCoefficients_db = sqlite3.connect('antoinesCoefficients.db')
    # Creating the cursor: little "robot" you send off to do actions
    c = antoinesCoefficients_db.cursor()
    # Create table
    c.execute("""CREATE TABLE coefficients (
            Component text,
            A real,
            B real,
            C real,
            Low_T real,
            High_T real
            )""")
    for i in range(numRows):
        component_row = antoinesCoefficients_dataframe.loc[i]
        c.execute("INSERT INTO coefficients VALUES (:Component, :A, :B, :C, :Low_T, :High_T)",
            {
                'Component': component_row["Component"],
                'A': float(component_row['A']),
                'B': float(component_row['B']),
                'C': float(component_row['C']),
                'Low_T': float(component_row["Low T"]),
                'High_T': float(component_row["High T"])
            }
        )
    #Commit Changes
    antoinesCoefficients_db.commit()
    # Close database connection
    c.close()

def query(cmd):
    antoinesCoefficients_db = sqlite3.connect('antoinesCoefficients.db')
    c = antoinesCoefficients_db.cursor()
    # * means everything, oid is the primary key
    c.execute(cmd)
    data = c.fetchall()
    result = []
    for element in data:
        result.append(element[0])
    return result

def main():
    #buildDatabase()
    component_options = removeDuplicates(query("SELECT Component FROM coefficients"))

    root = Tk()

    # Creating Title Widget
    title = Label(root, text="Pressure-Composition Phase Diagram Generator")
    title.grid(row=0, columnspan=5)

    # Creating the variables storing component names
    component1 = StringVar(root)
    component1.set("Select a component")
    component2 = StringVar(root)
    component2.set("Select a component")

    # Creating component1 OptionMenu
    component1_prompt = Label(root, text="Select component 1:")
    component1_menu = OptionMenu(root, component1, *component_options)
    component1_prompt.grid(row=1, column=0)
    component1_menu.grid(row=1, column=1)

    # Creating component2 OptionMenu
    component2_prompt = Label(root, text="Select component 2:")
    component2_menu = OptionMenu(root, component2, *component_options)
    component2_prompt.grid(row=1, column=3)
    component2_menu.grid(row=1, column=4)

    # Select constant temperautre  widgets
    temperature_prompt = Label(root, text="Constant T [°C] of the system:")
    temperature_entry = Entry(root, width=20, bg="gray", fg="white")
    temperature_prompt.grid(row=2,column=0)
    temperature_entry.grid(row=2,column=1)

    def submit():
        low_T_1 = query("SELECT Low_T FROM coefficients WHERE Component = '" + component1.get() + "'")[0]
        high_T_1 = query("SELECT High_T FROM coefficients WHERE Component = '" + component1.get() + "'")[0]
        low_T_2 = query("SELECT Low_T FROM coefficients WHERE Component = '" + component2.get() + "'")[0]
        high_T_2 = query("SELECT High_T FROM coefficients WHERE Component = '" + component2.get() + "'")[0]
        temperature = float(temperature_entry.get())

    # Submit component values button
    submit_button = Button(root, text="Confirm", command=submit)
    submit_button.grid(row=3, column=2)

    # Set default row and column size
    col_count, row_count = root.grid_size()
    for col in range(col_count):
        root.grid_columnconfigure(col, minsize=100)
    for row in range(row_count):
        root.grid_rowconfigure(row, minsize=10)

    root.mainloop()

if __name__ == "__main__":
    main()