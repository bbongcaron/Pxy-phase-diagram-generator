# Pxy-phase-diagram-generator
***Author: Brenton Bongcaron***

**Brief Description:**
Generate a pressure vs. liquid/vapor mole fraction of component A (in a binary mixture of A+B) phase diagram, given user-inputted names of the components 
and the temperature T of the system.
## **Details:**  
This program uses Antoine's Equation coefficients from zyBooks 14:155:201 Table 9.10.1 and a user inputted constant pressure T through a tkinter GUI
to calculate the saturation pressures of the components at T. These points serve to define the upper and lower bound of the range of pressure values
this phase diagram exists in. The vapor and liquid phase boundaries are defined by 100 data points each and are calculated by the following algorithm:
  
For each composition in a linearly spaced array of 100 mole fractions of A:   
  - calculate the dew point of the binary mixture at each composition of the binary mixture to define the gaseous boundary  
  - calculate the bubble point of the binary mixture at each composition of the binary mixture to define the liquidus boundary  
  
A figure is then generated by plotting linearly spaced array of mole fractions each against the dew/bubble points of the binary mixture at each composition.  
## **Error Handling:**  
Each component has its own range of temperatures for which Raoult's Law will be accurate. A Data Base file is present that holds these temperature ranges
and will be interacted with by the application using SQLite3. The user-inputted temperature is checked to see if Raoult's Law is valid for each component 
at each temperature. The input temperature is not contained within the valid temperature range of both components, an error messagebox is displayed.  
  
In the event that a user-inputted component does not match any of the entries in the database, an error messagebox is displayed.
## **Equations Used:**  
Antoine's Equation : log10(p*) = A - (B / (T + C))  
  - A, B & C are coefficents according to the component  
  - p* = saturation pressure @T for component i  
  - T = temperature  
  
Bubble Point Pressure Equation : P = Σ(xp*)  
  - P = total pressure of system
  - x = liquid mole fraction of component i
  - p* = saturation pressure @T for component i  
    
Dew Point Pressure Equation : P = Σ[1/(yp*)]  
  - P = total pressure of system
  - x = vapor mole fraction of component i
  - p* = saturation pressure @T for component i
  
