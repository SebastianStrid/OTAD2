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

def database():
    #Skapar databasanslutningen
    global filelist
    global cursor
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
        EntMedlemsnummer = Entry(home, width=5, text = "Medlemsnummer") 
        EntMedlemsnummer.grid(row=1, column=1, sticky = W, pady =(10,0), padx=(10,0))
        #EntMedlemsnummer.bind("<KeyRelease>", lambda args: hamtaDelagareFranEntry())

        EntMaskinnummer = Entry(home, width=5, text ="Maskinnummer") 
        EntMaskinnummer.grid(row=1, column=3, sticky = W,  pady =(10,0), padx=(10,0))
        #EntMaskinnummer.bind("<KeyRelease>", lambda args: hamtaMaskinerFranEntry())

        LbDelagare = Listbox(home, width = 60, height = 15, exportselection=0)
        LbDelagare.grid(row = 2, column = 1, columnspan = 2, rowspan = 2,  pady =(10,0), padx=(10,0))
        #LbDelagare.bind('<<ListboxSelect>>', hamtaAllaMaskiner)

        LbMaskiner = Listbox(home, width = 30, height = 15, exportselection=0)
        LbMaskiner.grid(row = 2, column = 3, columnspan = 2, rowspan = 2,  pady =(10,0), padx=(10,0))

        ScbDelagare = Scrollbar(home, orient="vertical")
        ScbDelagare.grid(row = 2, column = 2, sticky = N+S+E, rowspan = 2)
        ScbDelagare.config(command =LbDelagare.yview)

        ScbDMaskiner = Scrollbar(home, orient="vertical")
        ScbDMaskiner.grid(row = 2, column = 4, sticky = N+S+E, rowspan = 2)
        ScbDMaskiner.config(command =LbMaskiner.yview)

        LbDelagare.config(yscrollcommand=ScbDelagare.set)
        LbMaskiner.config(yscrollcommand=ScbDMaskiner.set)

        BtnMiljodeklaration = Button(home, text="Miljödeklaration")
        BtnMiljodeklaration.grid(row=4, column=4, pady=(10,0), padx=(0,15), sticky=E, columnspan=2)

        BtnMaskinpresentation = Button(home, text="Maskinpresentation")
        BtnMaskinpresentation.grid(row=4, column=2, pady=(10,0), padx=(0,10), sticky=E, columnspan=2)

        EntSokTillbehor = Entry(home, width= 10)
        EntSokTillbehor.grid(row=5, column=2, columnspan=2, sticky=E, pady=(30,0), padx=(0,15))

        BtnSokTillbehor = Button(home, text=("Sök tillbehör"))
        BtnSokTillbehor.grid(row=5, column=4, sticky=E, pady=(30,0), padx=(0,15))

    #Fyller LbDelagare (Listboxen på Home-fliken) med delägarna ifrån databsen
    def fyllListboxDelagare():

        global cursor
        cursor.execute("SELECT Medlemsnummer, Fornamn, Efternamn, Foretagsnamn FROM foretagsregister")
        delagareLista = []
        delagareLista = cursor.fetchall()
        LbDelagare.delete(0, 'end')

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
                
            LbDelagare.insert("end", s)
    fyllListboxDelagare()

#Globala variabler
global cursor
filePath = None
imgNyBild = None
medlemsnummer = ""
maskinnummer = ""
forarid = ""


#Instansiera GUI
database()

#validera = root.register(valideraSiffror)
if __name__ == "__main__":
    
    Gui = GUI(root)
    root.mainloop()
#Håller fönstret igång, ta ej bort eller flytta!
