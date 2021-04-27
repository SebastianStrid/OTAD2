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
        self.EntMedlemsnummer.bind("<KeyRelease>", lambda args: self.hamtaDelagareFranEntry())

        self.EntMaskinnummer = Entry(home, width=5, text ="Maskinnummer") 
        self.EntMaskinnummer.grid(row=1, column=3, sticky = W,  pady =(10,0), padx=(10,0))
        self.EntMaskinnummer.bind("<KeyRelease>", lambda args: self.hamtaMaskinerFranEntry())

        self.LbDelagare = Listbox(home, width = 60, height = 15, exportselection=0)
        self.LbDelagare.grid(row = 2, column = 1, columnspan = 2, rowspan = 2,  pady =(10,0), padx=(10,0))
        self.LbDelagare.bind('<<ListboxSelect>>', lambda args: self.hamtaAllaMaskiner())

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

        self.BtnMiljodeklaration = Button(home, text="Miljödeklaration", command = lambda: self.miljodeklaration(self.LbMaskiner.get(self.LbMaskiner.curselection())))
        self.BtnMiljodeklaration.grid(row=4, column=4, pady=(10,0), padx=(0,15), sticky=E, columnspan=2)

        self.BtnMaskinpresentation = Button(home, text="Maskinpresentation", command = lambda: self.maskinpresentation(self.LbMaskiner.get(self.LbMaskiner.curselection())))
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
    
    #Fyller LbMaskiner (Listboxen på Home-fliken) med maskinerna ifrån databasen
    def hamtaAllaMaskiner(self):
        global medlemsnummer

        selectedDelagare = self.LbDelagare.get(self.LbDelagare.curselection())
        indexSpace = selectedDelagare.index(" ")
        stringSelectedDelagare = str(selectedDelagare[0:indexSpace])
        delagare = "".join(stringSelectedDelagare)
        medlemsnummer = delagare
        cursor.execute('SELECT Maskinnummer, MarkeModell, Arsmodell FROM maskinregister WHERE Medlemsnummer = ' + delagare + ';')
        result = cursor.fetchall()
            
        if self.LbMaskiner.index("end") != 0:
            self.LbMaskiner.delete(0, "end")
            for item in result:
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
                if item[2] == "":
                        s+= " "
                else:
                        s+= " - "
                        s+=str(item[2])
                        
                self.LbMaskiner.insert("end",s )

        else:
            for item in result:
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
                if item[2] == "":
                        s+= " "
                else:
                        s+= " - "
                        s+=str(item[2])
                                                
                self.LbMaskiner.insert("end",s )

    #Hämtar delägare efter det medlemsnummer som söks på i Home-fliken
    def hamtaDelagareFranEntry(self):

        cursor.execute("SELECT Medlemsnummer, Fornamn, Efternamn, Foretagsnamn FROM foretagsregister WHERE Medlemsnummer LIKE '" + self.EntMedlemsnummer.get() + "%'")
        delagareLista = []
        delagareLista = cursor.fetchall()
        delagareLista = list(delagareLista)
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
    
    #Hämta maskiner efter det maskinnummer som söks på i Home-fliken
    def hamtaMaskinerFranEntry(self):

        cursor.execute("SELECT Maskinnummer, MarkeModell, Arsmodell FROM maskinregister WHERE Maskinnummer LIKE '" + self.EntMaskinnummer.get() + "%'")
        result = cursor.fetchall()
        result = list(result)
        self.LbMaskiner.delete(0, "end")   

        for item in result:
            item = list(item)
            if item[1] == None:
                item[1] = ""
            if item[2] == None:
                item[2] = ""

            s=""
            s += str(item[0])

            if item[1] == "":
                s+= " "
            else:
                s+= " - "
                s+=str(item[1])
            if item[2] == "":
                s+= " "
            else:
                s+= " - "
                s+=str(item[2])

            self.LbMaskiner.insert("end",s )

    #Funktion som skapar PDF-rapporten miljödeklaration
    def miljodeklaration(self, maskinnummer):

        if len(maskinnummer) == 0:
            messagebox.showerror("Fel", "Ingen maskin är vald.")
        
        else:
            indexSpace = maskinnummer.index(" ")
            stringSelectedMaskin = str(maskinnummer[0:indexSpace])
            maskin = "".join(stringSelectedMaskin)
            cursor.execute('SELECT * FROM maskinregister WHERE Maskinnummer = ' + str(maskin) + ';')
            maskinInfo = cursor.fetchone()
            maskinInfo = list(maskinInfo)
            
            cursor.execute('SELECT Fornamn, Efternamn, Foretagsnamn, Gatuadress, Postnummer, Postadress FROM foretagsregister WHERE Medlemsnummer = ' + str(maskinInfo[4]) + ';')
            delagarInfoLista = cursor.fetchone()
            delagarInfoLista = list(delagarInfoLista)

            cursor.execute('SELECT forsakringsgivare FROM forsakringsgivare WHERE idforsakringsgivare = "1"')
            forsakring = cursor.fetchone()

            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)

            for item in range(len(maskinInfo)):
                if maskinInfo[item] == None:
                        maskinInfo[item] = ""

            for item in range(len(delagarInfoLista)):
                if delagarInfoLista[item] == None:
                        delagarInfoLista[item] = ""

            #Översta delen
            c.drawString(130, 722, str(maskinInfo[4]))
            c.drawString(130, 702, str(delagarInfoLista[2]))
            c.drawString(130, 682, str(delagarInfoLista[0]))
            c.drawString(195, 682, str(delagarInfoLista[1]))
            c.drawString(130, 662, str(delagarInfoLista[3]))
            c.drawString(130, 642, str(delagarInfoLista[4]))
            c.drawString(190, 642, str(delagarInfoLista[5]))
            c.drawString(470, 722, str(maskinInfo[0]))
            c.drawString(458, 702, str(maskinInfo[1]))
            c.drawString(458, 682, str(maskinInfo[6]))
            c.drawString(458, 662, str(maskinInfo[26]))
            c.drawString(458, 642, str(maskinInfo[2]))
            c.drawString(458, 622, str(maskinInfo[27]))

            #Motor
            c.drawString(50, 540, str(maskinInfo[8]))
            c.drawString(160, 540, str(maskinInfo[9]))
            c.drawString(270, 540, str(maskinInfo[10]))

            #Eftermonterad avgasreninsutrustning
            if maskinInfo[14] == 1:
                c.drawString(50, 482, "Ja")
            elif maskinInfo[14] == 0:
                c.drawString(50, 482, "Nej")

            if maskinInfo[15] == 1:
                c.drawString(120, 482, "Ja")
            elif maskinInfo[15] == 0:
                c.drawString(120, 482, "Nej")

            if maskinInfo[12] == 1:
                c.drawString(195, 482, "Ja")
            elif maskinInfo[12] == 0:
                c.drawString(195, 482, "Nej")

            if maskinInfo[11] == 1:
                c.drawString(280, 482, "Ja")
            elif maskinInfo[11] == 0:
                c.drawString(280, 482, "Nej")


            #Bullernivå
            c.drawString(340, 482, str(maskinInfo[29]))
            c.drawString(430, 482, str(maskinInfo[31]))

            #Oljor och smörjmedel - Volym, liter
            if len(maskinInfo[16]) < 25:
                c.drawString(50, 417, str(maskinInfo[16]))
            else:
                c.setFontSize(9)
                c.drawString(50, 417, str(maskinInfo[16]))
                c.setFontSize(11)

            if len(maskinInfo[18]) < 25:
                c.drawString(50, 385, str(maskinInfo[18]))
            else:
                c.setFontSize(9)
                c.drawString(50, 385, str(maskinInfo[18]))
                c.setFontSize(11)

            if len(maskinInfo[20]) < 25:
                c.drawString(50, 355, str(maskinInfo[20]))
            else:
                c.setFontSize(9)
                c.drawString(50, 355, str(maskinInfo[20]))
                c.setFontSize(11)


            c.drawString(50, 325, str(maskinInfo[24]))
            c.drawString(205, 420, str(maskinInfo[17]))
            c.drawString(205, 390, str(maskinInfo[19]))
            c.drawString(205, 360, str(maskinInfo[21]))

            #Miljöklassificering
            c.drawString(340, 420, str(maskinInfo[30]))
            if maskinInfo[22] == 1:
                c.drawString(345, 330, "Ja")
            elif maskinInfo[22] == 0:
                c.drawString(345, 330, "Nej")

            #Övrigt
            c.drawString(50, 244, str(maskinInfo[13]))
            if maskinInfo[37] == 1:
                c.drawString(125, 244, "Ja")
            elif maskinInfo[37] == 0:
                c.drawString(125, 244, "Nej")
            c.drawString(205, 244, str(maskinInfo[25]))
            if maskinInfo[35] == 1:
                c.drawString(375, 244, "Ja")
            elif maskinInfo[35] == 0:
                c.drawString(375, 244, "Nej")
            c.drawString(470, 210, str(maskinInfo[38]))
            c.drawString(50, 210, str(maskinInfo[33]))
            c.drawString(205, 210, str(maskinInfo[34]))
            if maskinInfo[36] == 1:
                c.drawString(375, 210, "Ja")
            elif maskinInfo[36] == 0:
                c.drawString(375, 210, "Nej") 
            c.drawString(470, 210, str(maskinInfo[39]))

            #Bränsle
            c.drawString(50, 155, str(maskinInfo[23]))

            #Försärking
            if maskinInfo[3] == 1:
                c.drawString(50, 102, forsakring[0])
            c.drawString(240, 102, str(maskinInfo[7]))
            if maskinInfo[7] != "":
                c.drawString(305, 102, "-")
            c.drawString(315, 102, str(maskinInfo[42]))

            #Datum
            c.drawString(435, 52, str(datetime.date(datetime.now())))

            c.save()

            packet.seek(0)
            new_pdf = PdfFileReader(packet)

            existing_pdf = PdfFileReader(open("PDFMallar/Miljödeklaration.pdf", "rb"))
            output = PdfFileWriter()

            page = existing_pdf.getPage(0)
            page.mergePage(new_pdf.getPage(0))
            output.addPage(page)

            outputStream = open( "Miljödeklaration - " + str(maskinnummer) + ".pdf", "wb")
            output.write(outputStream)
            outputStream.close()
            os.startfile("Miljödeklaration - " + str(maskinnummer) + ".pdf" )
    
    #Funktion som skapar PDF-rapporten maskinpresentation
    def maskinpresentation(self, maskinnummer):     

        if len(maskinnummer) == 0:
            messagebox.showerror("Fel", "Ingen maskin är vald.")
        
        else:
            indexSpace = maskinnummer.index(" ")
            stringSelectedMaskin = str(maskinnummer[0:indexSpace])
            maskin = "".join(stringSelectedMaskin)
            cursor.execute('SELECT Medlemsnummer, MarkeModell, Arsmodell, Registreringsnummer, ME_Klass, Maskintyp, Forarid FROM maskinregister WHERE Maskinnummer = ' + maskin + ';')
            maskinInfo = cursor.fetchone()
            maskinInfo = list(maskinInfo)

            cursor.execute('SELECT Foretagsnamn FROM foretagsregister WHERE medlemsnummer = ' + str(maskinInfo[0]) + ';')
            foretag = cursor.fetchone()
            foretag = list(foretag)

            cursor.execute('SELECT tillbehor FROM tillbehor WHERE Maskinnummer = ' + maskin + ';')
            tillbehor = cursor.fetchall()
            tillbehor = list(tillbehor)

            cursor.execute('SELECT sokvag FROM bilder WHERE Maskinnummer = ' + maskin + ' order by bildid desc LIMIT 1;')
            bild = cursor.fetchone()

            if maskinInfo[6] is not None:
                cursor.execute('select namn from forare where forarid = '+ str(maskinInfo[6])+';')
                forarnamn = cursor.fetchone()
                forarnamn = list(forarnamn)

                cursor.execute('SELECT Beskrivning FROM referens WHERE forarid = ' + str(maskinInfo[6]) + ';')
                referenser = cursor.fetchall()
                referenser = list(referenser)

            else:
                forarnamn = None
                referenser = None

            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)
            rad1=""
            rad2=""
            rad3=""
            rad4=""
            rad5=""
            y=1

            if bild is not None:
                c.drawImage(bild[0], 72, 134, 450, 340)
            c.drawString(133, 710, str(maskinInfo[0])) 
            c.drawString(455, 690, str(maskinInfo[1]))
            c.drawString(455, 670, str(maskinInfo[2]))
            c.drawString(455, 650, str(maskinInfo[3]))
            c.drawString(455, 630, str(maskinInfo[4]))
            c.drawString(455, 610, str(maskinInfo[5]))
            if forarnamn is not None:
                c.drawString(133, 670, str(forarnamn[0]))
            c.drawString(133, 690, str(foretag[0]))
            c.drawString(467, 710, str(maskin))
            
            counter = 0
            for x in tillbehor:
                counter +=1
                s = x[0]
                if(counter == len(tillbehor)):
                        s+=""
                else:
                        s+=", "
                        
                if y>12:
                        rad5+=s
                elif y>9:
                        y+=1
                        rad4+=s          
                elif y>6:
                        y+=1
                        rad3+=s
                elif y>3:
                        y+=1
                        rad2+=s
                else:
                        y+=1
                        rad1+=s      

            
            c.drawString(140, 558, str(rad1))
            c.drawString(140, 538, str(rad2))
            c.drawString(140, 518, str(rad3))
            c.drawString(140, 498, str(rad4))
            c.drawString(140, 478, str(rad5))
            if referenser is not None and len(referenser) != 0:
                c.drawString(152, 112, str(referenser[0][0]))
                c.drawString(152, 86, str(referenser[1][0]))

            c.save() 

            packet.seek(0)
            new_pdf = PdfFileReader(packet)

            existing_pdf = PdfFileReader(open("PDFMallar/Maskinpresentation.pdf", "rb"))
            output = PdfFileWriter()

            page = existing_pdf.getPage(0)
            page.mergePage(new_pdf.getPage(0))
            output.addPage(page)
            #Fixa i framtiden så att man kan använda sig av custom paths (till servern) för att spara dokumenten på andra ställen.
            outputStream = open( "Maskinpresentation - " + maskinnummer + ".pdf", "wb")
            output.write(outputStream)
            outputStream.close()
            #Öppnar dokumentet efter man skapat det. Måste ändra sökväg efter vi fixat servern.
            os.startfile("Maskinpresentation - " + maskinnummer + ".pdf" )

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
