#Importerar Tkinter (GUI), PIL (Bilder), PyPDF2 (För att läsa & skriva PDF), reportlab (För att skapa PDF), tkcalendar (Datepicker) och MySQL Connector (SQL)
from tkinter import *
from tkinter import ttk, messagebox
from PIL import ImageTk,Image
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import PIL
import mysql.connector
from tkinter.simpledialog import askstring
from tkinter import filedialog
from tkcalendar import DateEntry
from datetime import datetime,date
import os
import traceback

#Skapar och namnger huvudfönstret samt sätter storleken på fönstret
root = Tk()
root.title("T-schakts delägarregister")
root.geometry("600x400")
root.resizable(False, False)

def readAFile():
     global filelist
     file = open("test.txt", "r")
     filelist = file.readlines()
     file.close()


#Skapar databasanslutningen
global filelist
readAFile()
h = str(filelist[0])
_h = h[:-1]
u = str(filelist[1])
_u = u[:-1]
p = str(filelist[2])
_p = p[:-1]
_d = str(filelist[3])
print(_d)
try:
    db = mysql.connector.connect(
    host = _h ,
    user = _u ,
    password = _p ,
    database = _d
    )
    cursor = db.cursor()
except Exception:
    print("Databasuppkopplingen misslyckades!")
    traceback.print_exc()

class GUI:
    
    def __init__(self, master):
        
        home = Frame(master)
        home.pack()

        #Skapar de widgets vi har på Home-fliken
        self.EntMedlemsnummer = Entry(home, width=5, text = "Medlemsnummer") 
        self.EntMedlemsnummer.grid(row=1, column=1, sticky = W, pady =(10,0), padx=(10,0))
        #EntMedlemsnummer.bind("<KeyRelease>", lambda args: hamtaDelagareFranEntry())

        self.EntMaskinnummer = Entry(home, width=5, text ="Maskinnummer") 
        self.EntMaskinnummer.grid(row=1, column=3, sticky = W,  pady =(10,0), padx=(10,0))
        #EntMaskinnummer.bind("<KeyRelease>", lambda args: hamtaMaskinerFranEntry())

        self.LbDelagare = Listbox(home, width = 60, height = 15, exportselection=0)
        self.LbDelagare.grid(row = 2, column = 1, columnspan = 2, rowspan = 2,  pady =(10,0), padx=(10,0))
        #LbDelagare.bind('<<ListboxSelect>>', hamtaAllaMaskiner)

        self.LbMaskiner = Listbox(home, width = 30, height = 15, exportselection=0)
        self.LbMaskiner.grid(row = 2, column = 3, columnspan = 2, rowspan = 2,  pady =(10,0), padx=(10,0))

        self.ScbDelagare = Scrollbar(home, orient="vertical")
        self.ScbDelagare.grid(row = 2, column = 2, sticky = N+S+E, rowspan = 2)
        self.ScbDelagare.config(command =self.LbDelagare.yview)

        self.ScbDMaskiner = Scrollbar(home, orient="vertical")
        self.ScbDMaskiner.grid(row = 2, column = 4, sticky = N+S+E, rowspan = 2)
        self.ScbDMaskiner.config(command =self.LbMaskiner.yview)

        self.LbDelagare.config(yscrollcommand=self.ScbDelagare.set)
        self.LbMaskiner.config(yscrollcommand=self.ScbDMaskiner.set)

        self.BtnMiljodeklaration = Button(home, text="Miljödeklaration")
        self.BtnMiljodeklaration.grid(row=4, column=4, pady=(10,0), padx=(0,15), sticky=E, columnspan=2)

        self.BtnMaskinpresentation = Button(home, text="Maskinpresentation")
        self.BtnMaskinpresentation.grid(row=4, column=2, pady=(10,0), padx=(0,10), sticky=E, columnspan=2)

        self.EntSokTillbehor = Entry(home, width= 10)
        self.EntSokTillbehor.grid(row=5, column=2, columnspan=2, sticky=E, pady=(30,0), padx=(0,15))

        self.BtnSokTillbehor = Button(home, text=("Sök tillbehör"))
        self.BtnSokTillbehor.grid(row=5, column=4, sticky=E, pady=(30,0), padx=(0,15))

        self.fyllListboxDelagare()

    #Fyller LbDelagare (Listboxen på Home-fliken) med delägarna ifrån databsen
    def fyllListboxDelagare(self):
        
        global cursor
        cursor.execute("SELECT Medlemsnummer, Fornamn, Efternamn, Foretagsnamn FROM foretagsregister")
        delagareLista = []
        delagareLista = cursor.fetchall()
        self.LbDelagare.delete(0, 'end')

        for item in delagareLista:
            item = list(item)
            if item[1] == None:
                item[1] = ""
            if item[2] == None:
                item[2] = ""
            s=""
            s += str(item[0])
            if item[1] == "":
                s+= ""
            else:
                s+= " - "
                s+=str(item[1])
                s+= " "
                s+=str(item[2])
            s+=" - "
            s+=str(item[3])                              
                
            self.LbDelagare.insert("end", s)
    

#Globala variabler
filePath = None
imgNyBild = None
medlemsnummer = ""
maskinnummer = ""
forarid = ""


#Instansiera GUI


#validera = root.register(valideraSiffror)
if __name__ == "__main__":
    
    Gui = GUI(root)
    root.mainloop()
#Håller fönstret igång, ta ej bort eller flytta!
