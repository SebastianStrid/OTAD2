#Importerar Tkinter (GUI), PIL (Bilder), PyPDF2 (För att läsa & skriva PDF), reportlab (För att skapa PDF), tkcalendar (Datepicker) och MySQL Connector (SQL)
from tkinter import *
from tkinter import ttk, messagebox
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
#import mysql.connector
from datetime import datetime,date
import os
import traceback
from python_mysql_dbconfig import read_db_config
import pyodbc

#Skapar och namnger huvudfönstret samt sätter storleken på fönstret
root = Tk()
root.title("T-schakts rapportgenerator")
root.geometry("800x340")
root.resizable(False, False)

#-----------Validering----------#
#Validerar entrys så att endast siffror går att använda i dem.
def valideraSiffror(input):
    if input.isdigit() and len(input) < 7 or len(input)==0 :
        return True
    else:
        return False 
validera = root.register(valideraSiffror)

#Hämtar databas informationen ifrån en config.ini fil.
try:
    db_config=read_db_config()
except:
    db_config=""
#Skapar en Databas klass med alla inbyggad funktioner färdiga som funktioner.
class DB():
    def __init__(self, db_local):
        try:        
            self.connection=None
            self.connection = pyodbc.connect('DSN=Tschakt2;Trusted_Connection=yes;')
        except Exception:
            traceback.print_exc()
    #Skapar cursorn och skickar in queryn tillsammans med argumenten.
    def query(self, sql, args):
        cursor = self.connection.cursor()
        if args == None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, args)
        return cursor
    #Kör fetchall
    def fetch(self, sql, args):
        rows=[]
        cursor = self.query(sql,args)
        res = cursor.fetchall()
        if len(res)!=0:
            rows=res
        cursor.close()
        return rows
    #Kör fetchone
    def fetchone(self, sql, args):
        row = None
        cursor = self.query(sql, args)
        res = cursor.fetchall()
        if len(res)!=0:
            row=res
        cursor.close()
        return row
    #Kör en insert.
    def insert(self, sql ,args):
        cursor = self.query(sql, args)
        id = cursor.lastrowid
        self.connection.commit()
        cursor.close()
        return id
    #Kör en update.
    def update(self,sql,args):
        cursor = self.query(sql, args)
        rowcount = cursor.rowcount
        self.connection.commit()
        cursor.close()
        return rowcount
    #Stänger ner anslutningen när den inte används längre. Garbage collectas.
    def __del__(self):
        if self.connection!=None:
            self.connection.close()

#Skapar en GUI klass, allt utseende och majoriteten av funktionerna skapas här.
class GUI:    
    def __init__(self, master):
        #Skapar framen allt annat ska hamna i. 
        home = Frame(master)
        home.pack()

        #Skapar de widgets vi har på Home-fliken
        self.EntMedlemsnummer = Entry(home, width=5, text = "Medlemsnummer",validate = "key", validatecommand=(validera, "%P")) 
        self.EntMedlemsnummer.grid(row=1, column=1, sticky = W, pady =(10,0), padx=(10,0))
        self.EntMedlemsnummer.bind("<KeyRelease>", lambda args: self.hamtaDelagareFranEntry())

        self.EntMaskinnummer = Entry(home, width=5, text ="Maskinnummer",validate ="key", validatecommand=(validera, "%P")) 
        self.EntMaskinnummer.grid(row=1, column=3, sticky = W,  pady =(10,0), padx=(10,0))
        self.EntMaskinnummer.bind("<KeyRelease>", lambda args: self.hamtaMaskinerFranEntry())

        self.lblForare = Label(home, text="Kopplad förare.")
        self.lblForare.grid(column=5,row=3, sticky=N, pady=(10,0))
        self.entForare = Entry(home,state=DISABLED)
        self.entForare.grid(column=5, row=3, columnspan = 2, sticky=W+E+S, padx=(10,0),pady=(10,0))

        self.LbDelagare = Listbox(home, width = 60, height = 15, exportselection=0)
        self.LbDelagare.grid(row = 2, column = 1, columnspan = 2, rowspan = 2,  pady =(10,0), padx=(10,0))
        self.LbDelagare.bind('<<ListboxSelect>>', lambda x:self.hamtaAllaMaskiner())

        self.LblDelagare = Label(home, text="Delägare")
        self.LblDelagare.grid(row=1, column =1,  pady =(10,0), padx=(0,0), sticky=E)

        self.LbMaskiner = Listbox(home, width = 30, height = 15, exportselection=0)
        self.LbMaskiner.grid(row = 2, column = 3, columnspan = 2, rowspan = 2,  pady =(10,0), padx=(10,0))
        self.LbMaskiner.bind('<<ListboxSelect>>', lambda args: self.fyllTillbehorOchForare())

        self.LblMaskiner = Label(home, text="Maskiner")
        self.LblMaskiner.grid(row=1, column= 4, pady =(10,0), padx=(0,0), sticky=W)

        self.LbTillbehor = Listbox(home, width=30, exportselection =0)
        self.LbTillbehor.grid(row=2, column=5, columnspan=2,  pady =(10,0), padx=(10,0), sticky=N+S+W+E)

        self.ScbDelagare = Scrollbar(home, orient="vertical")
        self.ScbDelagare.grid(row = 2, column = 2, sticky = N+S+E, rowspan = 2)
        self.ScbDelagare.config(command =self.LbDelagare.yview)

        self.ScbDMaskiner = Scrollbar(home, orient="vertical")
        self.ScbDMaskiner.grid(row = 2, column = 4, sticky = N+S+E, rowspan = 2)
        self.ScbDMaskiner.config(command =self.LbMaskiner.yview)

        self.ScbTillbehor = Scrollbar(home, orient="vertical")
        self.ScbTillbehor.grid(row = 2, column = 6, sticky = N+S+E)
        self.ScbTillbehor.config(command =self.LbTillbehor.yview)

        self.LbDelagare.config(yscrollcommand=self.ScbDelagare.set)
        self.LbMaskiner.config(yscrollcommand=self.ScbDMaskiner.set)
        self.LbTillbehor.config(yscrollcommand=self.ScbTillbehor.set)

        self.BtnMiljodeklaration = Button(home, text="Miljödeklaration", command=lambda:self.miljodeklaration())
        self.BtnMiljodeklaration.grid(row=4, column=0, pady=(10,0), padx=(10,15), sticky=W, columnspan=2)

        self.BtnMaskinpresentation = Button(home, text="Maskinpresentation",command=lambda:self.maskinpresentation())
        self.BtnMaskinpresentation.grid(row=4, column=1, pady=(10,0), padx=(0,140), sticky=E, columnspan=2)

        self.EntSokTillbehor = Entry(home, width= 15)
        self.EntSokTillbehor.grid(row=4, column=3, columnspan=2, sticky=E, pady=(10,0), padx=(0,90))

        self.BtnSokTillbehor = Button(home, text=("Sök tillbehör"), command=self.hamtaMaskinerGenomTillbehor)
        self.BtnSokTillbehor.grid(row=4, column=4, sticky=E, pady=(10,0), padx=(0,10))

        self.entSokForare = Entry(home)
        self.entSokForare.grid(row=4, column=5,sticky=E, pady=(10,0),padx=(10,0))

        self.btnSokForare = Button(home, text=("Sök förare"),command = self.hamtaMaskinerGenomForare)
        self.btnSokForare.grid(row=4, column=6, sticky=E, pady=(10,0),padx=(10,0))

        

        self.LblTillbehor = Label(home, text="Tillbehör")
        self.LblTillbehor.grid(row=1, column=5, pady =(10,0), padx=(10,0), sticky=E)

        self.fyllListboxDelagare()
    def hamtaMaskinerGenomForare(self):
        entry = '{}%'.format(self.entSokForare.get())
        if len(entry)==0:
            messagebox.showerror("Fel", "Du måste skriva i något i tillbehörs sökrutan.") 
        else:
            sql_query="""SELECT Maskinnummer, MarkeModell, Arsmodell FROM tschakt.maskinregister WHERE forarid in (select forarid from tschakt.forare where namn like ?) order by maskinnummer asc"""
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
    #Hämtar maskinerna som har ett tillbehör kopplat till sig vilket liknar tillbehöret man skrivit in i sökrutan.
    def hamtaMaskinerGenomTillbehor(self):
        self.LbTillbehor.delete(0,'end')
        entry = '{}%'.format(self.EntSokTillbehor.get())
        if len(entry)==0:
            messagebox.showerror("Fel", "Du måste skriva i något i tillbehörs sökrutan.") 
        else:
            sql_query="""SELECT Maskinnummer, MarkeModell, Arsmodell FROM tschakt.maskinregister WHERE maskinid in (select maskinID from tschakt.tillbehor where tillbehor like ?) order by maskinnummer asc"""
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
    #Hämtar alla maskiner när programmet körs och fyller på LbMaskiner listan.
    def hamtaAllaMaskiner(self):
        selectedDelagare = self.LbDelagare.get(self.LbDelagare.curselection())
        indexSpace = selectedDelagare.index(" ")
        stringSelectedDelagare = str(selectedDelagare[0:indexSpace])
        delagare = "".join(stringSelectedDelagare)
        self.LbTillbehor.delete(0,'end')
        print(delagare)
        
        
        sql_query="SELECT Maskinnummer, MarkeModell, Arsmodell FROM tschakt.maskinregister WHERE Medlemsnummer = ? order by maskinnummer asc"
        try:
            databas = DB(db_config)
            result =databas.fetch(sql_query, (delagare,))
        except:
            traceback.print_exc()        
        
            
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
    #Fyller LbDelagare (Listboxen på Home-fliken) med delägarna ifrån databsen
    def fyllListboxDelagare(self):
        sql="SELECT Medlemsnummer, Fornamn, Efternamn, Foretagsnamn FROM tschakt.foretagsregister"
        self.LbDelagare.delete(0, 'end')
        
        try:
            test = DB(db_config)
            delagareLista=test.fetch(sql, None)
             
        except Exception:
            traceback.print_exc()       
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
    #Hämtar alla delägare som matchar siffrorna som skrivit i än så länge i delägar sökrutan.
    def hamtaDelagareFranEntry(self):

        entry = '{}%'.format(self.EntMedlemsnummer.get())
        sql_query = """SELECT Medlemsnummer, Fornamn, Efternamn, Foretagsnamn FROM tschakt.foretagsregister WHERE Medlemsnummer LIKE ?"""
        delagareLista = []
        try:
            databas = DB(db_config)
            delagareLista = databas.fetch(sql_query, (entry,))
        except:
            pass
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
    #Hämtar alla maskiner som matchar siffrorna som skrivit i än så länge i maskin sökrutan.
    def hamtaMaskinerFranEntry(self):

        entry = '{}%'.format(self.EntMaskinnummer.get())
        sql_query="""SELECT Maskinnummer, MarkeModell, Arsmodell FROM tschakt.maskinregister WHERE Maskinnummer LIKE ? order by maskinnummer asc"""
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
    #Funktion som skapar PDF-rapporten miljödeklaration
    def miljodeklaration(self):
        maskinnummer=""
        try:
            maskinnummer = self.LbMaskiner.get(self.LbMaskiner.curselection())
        except:
            pass
        if len(maskinnummer) == 0:
            messagebox.showerror("Fel", "Ingen maskin är vald.")    
        else:
            maskin_sql_query = """select * from tschakt.maskinregister where maskinnummer = ?"""
           
            indexSpace = maskinnummer.index(" ")
            stringSelectedDelagare = str(maskinnummer[0:indexSpace])
            maskin = "".join(stringSelectedDelagare)
            databas = DB(db_config)
            maskin_resultat=databas.fetchone(maskin_sql_query,(maskin,))[0]
            print(maskin_resultat[4])

            
            delagare_sql_query = """SELECT Fornamn, Efternamn, Foretagsnamn, Gatuadress, Postnummer, Postadress FROM tschakt.foretagsregister WHERE Medlemsnummer = ?"""
            delagarInfoLista = databas.fetchone(delagare_sql_query, (maskin_resultat[4],))[0]

            forsakring_sql_query ="""SELECT forsakringsgivare FROM tschakt.forsakringsgivare WHERE idforsakringsgivare = '1'"""
            forsakring = databas.fetchone(forsakring_sql_query, None)[0]


            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=letter)

            for item in range(len(maskin_resultat)):
                if item == None:
                        item[0] = ""

            for item in range(len(delagarInfoLista)):
                if delagarInfoLista[item] == None:
                        delagarInfoLista[item] = ""

            c.setFontSize(11)

            #Översta delen
            c.drawString(130, 722, str(maskin_resultat[4]))
            c.drawString(130, 702, str(delagarInfoLista[2]))
            c.drawString(130, 682, str(delagarInfoLista[0]))
            c.drawString(195, 682, str(delagarInfoLista[1]))
            c.drawString(130, 662, str(delagarInfoLista[3]))
            c.drawString(130, 642, str(delagarInfoLista[4]))
            c.drawString(190, 642, str(delagarInfoLista[5]))
            c.drawString(470, 722, str(maskin_resultat[0]))
            c.drawString(458, 702, str(maskin_resultat[1]))
            if maskin_resultat[6] is not None:
                c.drawString(458, 682, str(maskin_resultat[6]))
            c.drawString(458, 662, str(maskin_resultat[26]))
            if maskin_resultat[2] is not None:
                c.drawString(458, 642, str(maskin_resultat[2]))
            c.drawString(458, 622, str(maskin_resultat[27]))

            #Motor
            c.drawString(50, 540, str(maskin_resultat[8]))
            c.drawString(160, 540, str(maskin_resultat[9]))
            if maskin_resultat[10] is not None:
                c.drawString(270, 540, str(maskin_resultat[10]))

            #Eftermonterad avgasreninsutrustning
            if maskin_resultat[14] == 1:
                c.drawString(50, 482, "Ja")
            elif maskin_resultat[14] == 0:
                c.drawString(50, 482, "Nej")

            if maskin_resultat[15] == 1:
                c.drawString(120, 482, "Ja")
            elif maskin_resultat[15] == 0:
                c.drawString(120, 482, "Nej")

            if maskin_resultat[12] == 1:
                c.drawString(195, 482, "Ja")
            elif maskin_resultat[12] == 0:
                c.drawString(195, 482, "Nej")

            if maskin_resultat[11] == 1:
                c.drawString(280, 482, "Ja")
            elif maskin_resultat[11] == 0:
                c.drawString(280, 482, "Nej")


            #Bullernivå
            c.drawString(340, 482, str(maskin_resultat[29]))
            c.drawString(430, 482, str(maskin_resultat[31]))

            #Oljor och smörjmedel - Volym, liter
            if maskin_resultat[16] is not None:
                if len(maskin_resultat[16]) < 25:
                    c.drawString(50, 417, str(maskin_resultat[16]))
                else:
                    c.setFontSize(9)
                    c.drawString(50, 417, str(maskin_resultat[16]))
                    c.setFontSize(11)
            if maskin_resultat[18] is not None:
                if len(maskin_resultat[18]) < 25:
                    c.drawString(50, 385, str(maskin_resultat[18]))
                else:
                    c.setFontSize(9)
                    c.drawString(50, 385, str(maskin_resultat[18]))
                    c.setFontSize(11)
            if maskin_resultat[20] is not None:
                if len(maskin_resultat[20]) < 25:
                    c.drawString(50, 355, str(maskin_resultat[20]))
                else:
                    c.setFontSize(9)
                    c.drawString(50, 355, str(maskin_resultat[20]))
                    c.setFontSize(11)
                
                
            c.drawString(50, 325, str(maskin_resultat[24]))
            c.drawString(205, 420, str(maskin_resultat[17]))
            c.drawString(205, 390, str(maskin_resultat[19]))
            c.drawString(205, 360, str(maskin_resultat[21]))
            

            #Miljöklassificering
            c.drawString(340, 420, str(maskin_resultat[30]))
            if maskin_resultat[22] == 1:
                c.drawString(345, 330, "Ja")
            elif maskin_resultat[22] == 0:
                c.drawString(345, 330, "Nej")

            #Övrigt
            c.drawString(50, 244, str(maskin_resultat[13]))
            if maskin_resultat[37] == 1:
                c.drawString(125, 244, "Ja")
            elif maskin_resultat[37] == 0:
                c.drawString(125, 244, "Nej")
            c.drawString(205, 244, str(maskin_resultat[25]))
            if maskin_resultat[35] == 1:
                c.drawString(375, 244, "Ja")
            elif maskin_resultat[35] == 0:
                c.drawString(375, 244, "Nej")
            c.drawString(470, 210, str(maskin_resultat[38]))
            if maskin_resultat[33] is not None:
                if len(maskin_resultat[33]) > 25:
                    c.setFontSize(9)
                    c.drawString(50, 210, str(maskin_resultat[33]))
                    c.setFontSize(11)
                else:
                    c.drawString(50, 210, str(maskin_resultat[33]))
            c.drawString(205, 210, str(maskin_resultat[34]))
            if maskin_resultat[36] == 1:
                c.drawString(375, 210, "Ja")
            elif maskin_resultat[36] == 0:
                c.drawString(375, 210, "Nej") 
            c.drawString(470, 210, str(maskin_resultat[39]))

            #Bränsle
            c.drawString(50, 155, str(maskin_resultat[23]))

            #Försärking
            if maskin_resultat[3] == 1:
                c.drawString(50, 102, forsakring[0])
            if maskin_resultat[7] is not None:    
                c.drawString(240, 102, str(maskin_resultat[7]))
                if maskin_resultat[7] != "":
                    c.drawString(305, 102, "-")
                c.drawString(315, 102, str(maskin_resultat[42]))

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

            outputStream = open( "Miljödeklaration - " + str(maskin) + ".pdf", "wb")
            output.write(outputStream)
            outputStream.close()
            os.startfile("Miljödeklaration - " + str(maskin) + ".pdf" )
    #Funktion som skapar PDF-rapporten maskinpresentation
    def maskinpresentation(self):
        maskinnummer =""
        try:     
            maskinnummer=self.LbMaskiner.get(self.LbMaskiner.curselection())
        except:
            pass
        if len(maskinnummer) == 0:
            messagebox.showerror("Fel", "Ingen maskin är vald.")
        
        else:

            
            indexSpace = maskinnummer.index(" ")
            stringSelectedDelagare = str(maskinnummer[0:indexSpace])
            maskin = "".join(stringSelectedDelagare)
            maskin_sql_query = """SELECT Medlemsnummer, MarkeModell, Arsmodell, Registreringsnummer, ME_Klass, Maskintyp, Forarid FROM tschakt.maskinregister WHERE Maskinnummer = ?"""
            try:
                databas = DB(db_config)
                maskin_resultat=databas.fetchone(maskin_sql_query,(maskin,))[0]
            except:
                pass
            foretags_sql_query = """SELECT Foretagsnamn FROM tschakt.foretagsregister WHERE medlemsnummer = ?"""
            foretag = databas.fetchone(foretags_sql_query,(str(maskin_resultat[0]),))[0]
            
            tillbehor_sql_query="""SELECT Tillbehor FROM tschakt.tillbehor WHERE maskinid = (select maskinid from tschakt.maskinregister where maskinnummer = ?)"""           
            tillbehor = databas.fetch(tillbehor_sql_query,(maskin,))

            
            bild_sql_query = """SELECT top 1 sokvag FROM tschakt.bilder WHERE maskinid = (select maskinid from tschakt.maskinregister where maskinnummer = ?) order by bildid desc;"""
            try:
                bild = databas.fetchone(bild_sql_query, (maskin,))[0]
            except:
                bild = None            
            if maskin_resultat[6] is not None:
                forare_sql_query = """select namn from tschakt.forare where forarid = ?"""
                forarnamn = databas.fetchone(forare_sql_query, (str(maskin_resultat[6]),))[0]
                
                referens_sql_query="""SELECT Beskrivning FROM tschakt.referens WHERE forarid = ?"""
                referenser = databas.fetch(referens_sql_query, (str(maskin_resultat[6]),))                
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
            if maskin_resultat[0] is not None:
                c.drawString(133, 710, str(maskin_resultat[0]))
            if maskin_resultat[1] is not None:
                c.drawString(455, 690, str(maskin_resultat[1]))
            if maskin_resultat[2] is not None:
                c.drawString(455, 670, str(maskin_resultat[2]))
            if maskin_resultat[3] is not None:
                c.drawString(455, 650, str(maskin_resultat[3]))
            if maskin_resultat[4] is not None:
                c.drawString(455, 630, str(maskin_resultat[4]))
            if maskin_resultat[5] is not None:
                c.drawString(455, 610, str(maskin_resultat[5]))
            if forarnamn is not None:
                c.drawString(133, 670, str(forarnamn[0]))
            if foretag[0] is not None:
                c.drawString(133, 690, str(foretag[0]))
            if maskin is not None:
                c.drawString(470, 712, str(maskin))
            
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

            
            c.drawString(142, 561, str(rad1))
            c.drawString(142, 541, str(rad2))
            c.drawString(142, 521, str(rad3))
            c.drawString(142, 501, str(rad4))
            c.drawString(142, 481, str(rad5))
            
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
            outputStream = open("Maskinpresentationer/Maskinpresentation - " + maskin + ".pdf", "wb")
            output.write(outputStream)
            outputStream.close()
            #Öppnar dokumentet efter man skapat det. Måste ändra sökväg efter vi fixat servern.
            os.startfile("Maskinpresentationer\Maskinpresentation - " + maskin + ".pdf")
    #Funktion som fyller LbTillbehor när man trycker på en maskin i LbMaskiner
    def fyllTillbehorOchForare(self):
        sql="SELECT Tillbehor FROM tschakt.tillbehor WHERE maskinid = (select maskinid from tschakt.maskinregister where maskinnummer = ?)"
        sql_forare = """select namn from tschakt.forare where forarid = (select forarid from tschakt.maskinregister where maskinnummer = ?)"""
        maskinnummer=""
        maskinnummer = self.LbMaskiner.get(self.LbMaskiner.curselection())
        
        indexSpace = maskinnummer.index(" ")
        stringSelectedMaskin = str(maskinnummer[0:indexSpace])
        maskin = "".join(stringSelectedMaskin)
        print(maskin)
        databas = DB(db_config)
        tillbehor_resultat = databas.fetch(sql,(maskin,))

        forare_namn=databas.fetchone(sql_forare,(maskin,))


        self.LbTillbehor.delete(0,'end')
        for x in tillbehor_resultat:
            self.LbTillbehor.insert('end', x[0])

        self.entForare.config(state=NORMAL)
        self.entForare.delete(0,'end')
        if forare_namn is not None:
            self.entForare.insert(0,forare_namn[0][0])
        self.entForare.config(state=DISABLED)



  

#Dessa körs endast när denna fil körs som main. Om denna någon gång importeras till en annan fil så kommer dessa funktioner ej köras direkt.
if __name__ == "__main__":
    #Instansierar en ny GUI klass.
    Gui = GUI(root)
    #Håller fönstret igång, ta ej bort eller flytta!
    root.mainloop()

