from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import sqlite3
from numpy import *
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
        if len(element) == 1:
            result.append(element[0])
        else:
            result.append(element)
    return result

def main():
    #buildDatabase()
    component_options = removeDuplicates(query("SELECT Component FROM coefficients"))

    root = Tk()

    # Creating the variables storing component names
    component1 = StringVar(root)
    component1.set("Select a component")
    component2 = StringVar(root)
    component2.set("Select a component")

    # Creating component1 OptionMenu
    component1_prompt = Label(root, text="Select component 1:")
    component1_menu = ttk.Combobox(root, textvariable=component1, values=component_options)
    component1_prompt.grid(row=1, column=0)
    component1_menu.grid(row=1, column=1)

    # Creating component2 OptionMenu
    component2_prompt = Label(root, text="Select component 2:")
    component2_menu = ttk.Combobox(root, textvariable=component2, values=component_options)
    component2_prompt.grid(row=1, column=3)
    component2_menu.grid(row=1, column=4)

    # Select constant temperautre  widgets
    temperature_prompt = Label(root, text="Constant T [°C] of the system:")
    temperature_entry = Entry(root, width=20)
    temperature_prompt.grid(row=2,column=0)
    temperature_entry.grid(row=2,column=1)

    def plot(temp):
        numDataPts = 100
        # moleFract are the mole fractions of component 1
        moleFract = np.linspace(0, 1.0, numDataPts, endpoint=True)
        coefficients_1 = query("Select A, B, C FROM coefficients WHERE Component = '" + component1.get() + "'")[0]
        coefficients_2 = query("Select A, B, C FROM coefficients WHERE Component = '" + component2.get() + "'")[0]
        # Pressures are in [mmHg] => 1 atm = 760 mmHg
        pSat_c1 = pow(10, (coefficients_1[0] - (coefficients_1[1] / (temp + coefficients_1[2])))) / 760
        pSat_c2 = pow(10, (coefficients_2[0] - (coefficients_2[1] / (temp + coefficients_2[2])))) / 760
        pressure_vapor = np.zeros(numDataPts)
        pressure_liquid = np.zeros(numDataPts)
        for i in range(numDataPts):
            pressure_vapor[i] = 1 / (moleFract[i]/pSat_c1 + (1-moleFract[i])/pSat_c2)
            pressure_liquid[i] = moleFract[i]*pSat_c1 + (1-moleFract[i])*pSat_c2
        figure = Figure(figsize=(7,7), dpi=numDataPts)
        # Parameter is location
        phase_diagram = figure.add_subplot(111)
        phase_diagram.plot(moleFract, pressure_liquid, 'orange', label="Liquidus Boundary")
        phase_diagram.plot(moleFract, pressure_vapor, 'blue', label="Gaseous Boundary")
        
        phase_diagram.set(xlim=(0,1.0),
                          ylim = (0,pressure_vapor[-1]*1.2),
                          xlabel=f"Mole fraction of {component1.get()}",
                          ylabel="Pressure [atm]",
                          title=f'Pressure vs. xy Phase Diagram of a(n) {component1.get()} + {component2.get()} Binary Mixture'
                        )
        phase_diagram.legend()
        phase_diagram.grid()
        chart = FigureCanvasTkAgg(figure, root)
        chart.get_tk_widget().grid(row=7, column=2)

    def submit():
        if component1.get() not in component_options or component2.get() not in component_options:
            messagebox.showerror(title="Invalid Component(s)", 
            message=f"{component1.get()} and/or {component2.get()} is an invalid component pair. Names are case-sensitive!" 
            )
        low_T_1 = query("SELECT Low_T FROM coefficients WHERE Component = '" + component1.get() + "'")[0]
        high_T_1 = query("SELECT High_T FROM coefficients WHERE Component = '" + component1.get() + "'")[0]
        low_T_2 = query("SELECT Low_T FROM coefficients WHERE Component = '" + component2.get() + "'")[0]
        high_T_2 = query("SELECT High_T FROM coefficients WHERE Component = '" + component2.get() + "'")[0]
        temperature = float(temperature_entry.get())
        if temperature < low_T_1 or temperature > high_T_1 or temperature < low_T_2 or temperature > high_T_2:
            messagebox.showerror(title="Invalid Temperature", 
            message=f"{component1.get()} and {component2.get()} do NOT both obey Raoult's Law @T = {temperature}" 
            )
            return
        plot(temperature)
    
    # Submit component values button
    submit_button = Button(root, text="Confirm", command=submit)
    submit_button.grid(row=3, column=2)

    # Set default row and column size
    col_count, row_count = root.grid_size()
    for col in range(col_count):
        root.grid_columnconfigure(col, minsize=100)
    for row in range(row_count):
        root.grid_rowconfigure(row, minsize=10)
    root.minsize(width=1250,height=700)
    root.title("Pressure-Composition Phase Diagram Generator")
    root.mainloop()

if __name__ == "__main__":
    main()