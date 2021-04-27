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
from python_mysql_dbconfig import read_db_config

#Skapar och namnger huvudfönstret samt sätter storleken på fönstret
root = Tk()
root.title("T-schakts delägarregister")
root.geometry("600x400")
root.resizable(False, False)
#Hämtar databas informationen.
db_config=read_db_config()


class DB():
    def __init__(self, db_local):        
        self.connection=None
        self.connection = mysql.connector.connect(**db_local)

    def query(self, sql, args):
        cursor = self.connection.cursor()
        cursor.execute(sql, args)
        return cursor

    def fetch(self, sql, args):
        rows=[]
        cursor = self.query(sql,args)
        if cursor.with_rows:
            rows=cursor.fetchall()
        cursor.close()
        return rows

    def fetchone(self, sql, args):
        row = None
        cursor = self.query(sql, args)
        if cursor.with_rows:
            row = cursor.fetchone()
        cursor.close()
        return row

    def insert(self, sql ,args):
        cursor = self.query(sql, args)
        id = cursor.lastrowid
        self.connection.commit()
        cursor.close()
        return id
    
    def update(self,sql,args):
        cursor = self.query(sql, args)
        rowcount = cursor.rowcount
        self.connection.commit()
        cursor.close()
        return rowcount

    def __del__(self):
        print("Anslutningen bruten.")
        if self.connection!=None:
            self.connection.close()


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
        self.LbDelagare.bind('<<ListboxSelect>>', lambda x:self.hamtaAllaMaskiner())

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

        self.BtnMiljodeklaration = Button(home, text="Miljödeklaration", command=lambda:self.miljodeklaration(self.LbMaskiner.get(self.LbMaskiner.curselection())))
        self.BtnMiljodeklaration.grid(row=4, column=4, pady=(10,0), padx=(0,15), sticky=E, columnspan=2)

        self.BtnMaskinpresentation = Button(home, text="Maskinpresentation",command=lambda:self.maskinpresentation(self.LbMaskiner.get(self.LbMaskiner.curselection())))
        self.BtnMaskinpresentation.grid(row=4, column=2, pady=(10,0), padx=(0,10), sticky=E, columnspan=2)

        self.EntSokTillbehor = Entry(home, width= 10)
        self.EntSokTillbehor.grid(row=5, column=2, columnspan=2, sticky=E, pady=(30,0), padx=(0,15))

        self.BtnSokTillbehor = Button(home, text=("Sök tillbehör"), command=self.hamtaMaskinerGenomTillbehor)
        self.BtnSokTillbehor.grid(row=5, column=4, sticky=E, pady=(30,0), padx=(0,15))

        #self.fyllListbox()
        self.fyllListboxDelagare()
    def hamtaMaskinerGenomTillbehor(self):
        entry = '{}%'.format(self.EntSokTillbehor.get())
        
        sql_query="""SELECT Maskinnummer, MarkeModell, Arsmodell FROM maskinregister WHERE maskinnummer in (select maskinnummer from tillbehor where tillbehor like %s)"""
        databas = DB(db_config)
        result =databas.fetch(sql_query, (entry,))        
        
            
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
    def hamtaAllaMaskiner(self):
        selectedDelagare = self.LbDelagare.get(self.LbDelagare.curselection())
        indexSpace = selectedDelagare.index(" ")
        stringSelectedDelagare = str(selectedDelagare[0:indexSpace])
        delagare = "".join(stringSelectedDelagare)
        
        
        sql_query="""SELECT Maskinnummer, MarkeModell, Arsmodell FROM maskinregister WHERE Medlemsnummer = %s"""
        databas = DB(db_config)
        result =databas.fetch(sql_query, (delagare,))        
        
            
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

    def fyllListbox(self):        
        i = 0
        while i < 10:
            self.LbDelagare.insert("end", i)
            i+=1
            print(i) 

    #Fyller LbDelagare (Listboxen på Home-fliken) med delägarna ifrån databsen
    def fyllListboxDelagare(self):
        sql="SELECT Medlemsnummer, Fornamn, Efternamn, Foretagsnamn FROM foretagsregister"
        self.LbDelagare.delete(0, 'end')
        test = DB(db_config)
        delagareLista=test.fetch(sql, None)        
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
    
    def hamtaDelagareFranEntry(self):

        entry = '{}%'.format(self.EntMedlemsnummer.get())
        sql_query = """SELECT Medlemsnummer, Fornamn, Efternamn, Foretagsnamn FROM foretagsregister WHERE Medlemsnummer LIKE %s"""
        delagareLista = []
        databas = DB(db_config)
        delagareLista = databas.fetch(sql_query, (entry,))
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

    def hamtaMaskinerFranEntry(self):

        entry = '{}%'.format(self.EntMaskinnummer.get())
        sql_query="""SELECT Maskinnummer, MarkeModell, Arsmodell FROM maskinregister WHERE Maskinnummer LIKE %s"""
        result = []
        databas = DB(db_config)
        result = databas.fetch(sql_query, (entry,))
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

    def miljodeklaration(self, maskinnummer):

        if len(maskinnummer) == 0:
            messagebox.showerror("Fel", "Ingen maskin är vald.")
        
        else:
            maskin_sql_query = """select * from maskinregister where maskinnummer = %s"""

            
            indexSpace = maskinnummer.index(" ")
            stringSelectedDelagare = str(maskinnummer[0:indexSpace])
            maskin = "".join(stringSelectedDelagare)
            databas = DB(db_config)
            maskin_resultat = databas.fetch(maskin_sql_query,(maskin,))

            delagare_sql_query = """SELECT Fornamn, Efternamn, Foretagsnamn, Gatuadress, Postnummer, Postadress FROM foretagsregister WHERE Medlemsnummer = %s"""
            delagarInfoLista = databas.fetch(delagare_sql_query, (maskin_resultat[0][4],))

            forsakring_sql_query ="""SELECT forsakringsgivare FROM forsakringsgivare WHERE idforsakringsgivare = '1'"""
            forsakring = databas.fetchone(forsakring_sql_query, None)


            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)

            for item in range(len(maskin_resultat)):
                if maskin_resultat[item] == None:
                    maskin_resultat[item] = ""

            for item in range(len(delagarInfoLista)):
                if delagarInfoLista[item] == None:
                    delagarInfoLista[item] = ""

            #Översta delen
            c.drawString(130, 722, str(maskin_resultat[0][4]))
            c.drawString(130, 702, str(delagarInfoLista[0][2]))
            c.drawString(130, 682, str(delagarInfoLista[0][0]))
            c.drawString(195, 682, str(delagarInfoLista[0][1]))
            c.drawString(130, 662, str(delagarInfoLista[0][3]))
            c.drawString(130, 642, str(delagarInfoLista[0][4]))
            c.drawString(190, 642, str(delagarInfoLista[0][5]))
            c.drawString(470, 722, str(maskin_resultat[0][0]))
            c.drawString(458, 702, str(maskin_resultat[0][1]))
            c.drawString(458, 682, str(maskin_resultat[0][6]))
            c.drawString(458, 662, str(maskin_resultat[0][26]))
            c.drawString(458, 642, str(maskin_resultat[0][2]))
            c.drawString(458, 622, str(maskin_resultat[0][27]))

            #Motor
            c.drawString(50, 540, str(maskin_resultat[0][8]))
            c.drawString(160, 540, str(maskin_resultat[0][9]))
            c.drawString(270, 540, str(maskin_resultat[0][10]))

            #Eftermonterad avgasreninsutrustning
            if maskin_resultat[0][14] == 1:
                c.drawString(50, 482, "Ja")
            elif maskin_resultat[0][14] == 0:
                c.drawString(50, 482, "Nej")

            if maskin_resultat[0][15] == 1:
                c.drawString(120, 482, "Ja")
            elif maskin_resultat[0][15] == 0:
                c.drawString(120, 482, "Nej")

            if maskin_resultat[0][12] == 1:
                c.drawString(195, 482, "Ja")
            elif maskin_resultat[0][12] == 0:
                c.drawString(195, 482, "Nej")

            if maskin_resultat[0][11] == 1:
                c.drawString(280, 482, "Ja")
            elif maskin_resultat[0][11] == 0:
                c.drawString(280, 482, "Nej")


            #Bullernivå
            c.drawString(340, 482, str(maskin_resultat[0][29]))
            c.drawString(430, 482, str(maskin_resultat[0][31]))

            #Oljor och smörjmedel - Volym, liter
            if len(maskin_resultat[0][16]) < 25:
                c.drawString(50, 417, str(maskin_resultat[0][16]))
            else:
                c.setFontSize(9)
                c.drawString(50, 417, str(maskin_resultat[0][16]))
                c.setFontSize(11)

            if len(maskin_resultat[0][18]) < 25:
                c.drawString(50, 385, str(maskin_resultat[0][18]))
            else:
                c.setFontSize(9)
                c.drawString(50, 385, str(maskin_resultat[0][18]))
                c.setFontSize(11)

            if len(maskin_resultat[0][20]) < 25:
                c.drawString(50, 355, str(maskin_resultat[0][20]))
            else:
                c.setFontSize(9)
                c.drawString(50, 355, str(maskin_resultat[0][20]))
                c.setFontSize(11)


            c.drawString(50, 325, str(maskin_resultat[0][24]))
            c.drawString(205, 420, str(maskin_resultat[0][17]))
            c.drawString(205, 390, str(maskin_resultat[0][19]))
            c.drawString(205, 360, str(maskin_resultat[0][21]))

            #Miljöklassificering
            c.drawString(340, 420, str(maskin_resultat[0][30]))
            if maskin_resultat[0][22] == 1:
                c.drawString(345, 330, "Ja")
            elif maskin_resultat[0][22] == 0:
                c.drawString(345, 330, "Nej")

            #Övrigt
            c.drawString(50, 244, str(maskin_resultat[0][13]))
            if maskin_resultat[0][37] == 1:
                c.drawString(125, 244, "Ja")
            elif maskin_resultat[0][37] == 0:
                c.drawString(125, 244, "Nej")
            c.drawString(205, 244, str(maskin_resultat[0][25]))
            if maskin_resultat[0][35] == 1:
                c.drawString(375, 244, "Ja")
            elif maskin_resultat[0][35] == 0:
                c.drawString(375, 244, "Nej")
            c.drawString(470, 210, str(maskin_resultat[0][38]))
            c.drawString(50, 210, str(maskin_resultat[0][33]))
            c.drawString(205, 210, str(maskin_resultat[0][34]))
            if maskin_resultat[0][36] == 1:
                c.drawString(375, 210, "Ja")
            elif maskin_resultat[0][36] == 0:
                c.drawString(375, 210, "Nej") 
            c.drawString(470, 210, str(maskin_resultat[0][39]))

            #Bränsle
            c.drawString(50, 155, str(maskin_resultat[0][23]))

            #Försärking
            if maskin_resultat[0][3] == 1:
                c.drawString(50, 102, forsakring[0])
            c.drawString(240, 102, str(maskin_resultat[0][7]))
            if maskin_resultat[0][7] != "":
                c.drawString(305, 102, "-")
            c.drawString(315, 102, str(maskin_resultat[0][42]))

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

    def maskinpresentation(self, maskinnummer):     

        if len(maskinnummer) == 0:
            messagebox.showerror("Fel", "Ingen maskin är vald.")
        
        else:

            
            indexSpace = maskinnummer.index(" ")
            stringSelectedDelagare = str(maskinnummer[0:indexSpace])
            maskin = "".join(stringSelectedDelagare)
            maskin_sql_query = """SELECT Medlemsnummer, MarkeModell, Arsmodell, Registreringsnummer, ME_Klass, Maskintyp, Forarid FROM maskinregister WHERE Maskinnummer = %s"""
            databas = DB(db_config)
            maskin_resultat = databas.fetch(maskin_sql_query,(maskin,))

            foretags_sql_query = """SELECT Foretagsnamn FROM foretagsregister WHERE medlemsnummer = %s"""
            foretag = databas.fetch(foretags_sql_query,(str(maskin_resultat[0][0]),))

            print(maskin)
            
            tillbehor_sql_query="""SELECT tillbehor FROM tillbehor WHERE Maskinnummer =%s"""           
            tillbehor = databas.fetch(tillbehor_sql_query,(maskin,))

            
            bild_sql_query = """SELECT sokvag FROM bilder WHERE Maskinnummer = %s order by bildid desc LIMIT 1;"""
            bild = databas.fetchone(bild_sql_query, (maskin,))

            if maskin_resultat[0][6] is not None:
                forare_sql_query = """select namn from forare where forarid = %s"""
                forarnamn = databas.fetchone(forare_sql_query, (str(maskin_resultat[0][6]),))

                referens_sql_query="""SELECT Beskrivning FROM referens WHERE forarid = %s"""
                referenser = databas.fetch(referens_sql_query, (str(maskin_resultat[0][6]),))
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
            c.drawString(133, 710, str(maskin_resultat[0][0])) 
            c.drawString(455, 690, str(maskin_resultat[0][1]))
            c.drawString(455, 670, str(maskin_resultat[0][2]))
            c.drawString(455, 650, str(maskin_resultat[0][3]))
            c.drawString(455, 630, str(maskin_resultat[0][4]))
            c.drawString(455, 610, str(maskin_resultat[0][5]))
            if forarnamn is not None:
                c.drawString(133, 670, forarnamn)
            c.drawString(133, 690, str(foretag[0][0]))
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

    def on_closing():
        pass



#Dessa körs endast när denna fil körs som main. Om denna någon gång importeras till en annan fil så kommer dessa funktioner ej köras direkt.
if __name__ == "__main__":
    #Instansierar en ny GUI klass.
    Gui = GUI(root)
    #Håller fönstret igång, ta ej bort eller flytta!
    root.mainloop()

