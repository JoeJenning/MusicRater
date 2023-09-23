import spotipy
import SQLer, Ranker, Draw, Const
from spotipy.oauth2 import SpotifyClientCredentials
import tkinter as tk
from PIL import ImageTk, Image
import requests
from io import BytesIO
import customtkinter
import numpy as np
from datetime import datetime
import pytz

#pyinstaller --onefile SpotifyRanker.py

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials("be576e4423764bf0bb1fe905d32f624d","9d3db488623d410fafba2eeb3bf38e8c"))

print("App version: "+Const.VERSION)
print("Please wait while I load. The login screen will pop up shortly...")

album_id="31UtR7w5vJtg8AmBvWAwL5"
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

class App(customtkinter.CTk):
	# __init__ function for class tkinterApp
	def __init__(self, *args, **kwargs):
		super().__init__(*args,**kwargs)

		# __init__ function for class Tk
		customtkinter.CTk.__init__(self, *args, **kwargs)

		# creating a container
		container = customtkinter.CTkFrame(self)
		container.pack(side = "top", fill = "both", expand = True)

		container.grid_rowconfigure(0, weight = 1)
		container.grid_columnconfigure(0, weight = 1)

		# initializing frames to an empty array
		self.frames = {}

		# iterating through a tuple consisting
		# of the different page layouts
		for F in (StartPage, Ratings, Rate,LoginPage):
			frame = F(container, self)
			# initializing frame of that object from
			# startpage, page1, page2 respectively with
			# for loop
			self.frames[F] = frame
			frame.grid(row = 0, column = 0, sticky ="nsew")
		self.show_frame(LoginPage)

	# to display the current frame passed as
	# parameter
	def show_frame(self, cont):
		frame = self.frames[cont]
		frame.tkraise()


class LoginPage(customtkinter.CTkFrame):
	def __init__(self,parent, controller):
		customtkinter.CTkFrame.__init__(self,parent)
		self.winfo_toplevel().title("Login")

		def checkHours():
			def popup(error,title):
				top=customtkinter.CTkToplevel(self)
				top.attributes('-topmost',True)
				top.title(title)
				label_error=customtkinter.CTkLabel(top,text=error)
				label_error.grid(sticky='nsew',padx=50,pady=50)
				grid_size=customtkinter.CTk.grid_size(top)
				grid_numRows=grid_size[0]
				grid_numCols=grid_size[1]
				for row in range(grid_numRows):
					customtkinter.CTk.grid_rowconfigure(top,index=row,weight=1)
				for col	in range(grid_numCols):
					customtkinter.CTk.grid_columnconfigure(top,index=col,weight=1)
			
			tz_Chicago = pytz.timezone('America/Chicago') 
			# Get the current time in Chicago
			datetime_Chicago = datetime.now(tz_Chicago)

			if(datetime_Chicago.time()<=Const.TIME_DB_OPEN.time() or datetime_Chicago.time()>=Const.TIME_DB_CLOSE.time()):
				print("DATABASE CLOSED!")
				message="DATABASE CLOSED!\n\nYou will be unable to login.\nPlease try again later.\n\nDatabase hours: 9 AM - Midnight Central"
				popup(message,"Error: Database Closed")
			else:
				print("DB open")
				if(datetime_Chicago.time()<=Const.TIME_DB_OPEN.time() or datetime_Chicago.time()>=Const.TIME_DB_CLOSE_WARNING.time()):
					print("WARNING: The Database is closing in "+str(round((Const.TIME_DB_CLOSE-datetime_Chicago).total_seconds()/60))+" minutes!")
					message="WARNING: The Database is closing in "+str(round((Const.TIME_DB_CLOSE-datetime_Chicago).total_seconds()/60))+" minutes!\n\nYou will be unable to access the database, and any unsaved scores will be lost after this time.\nBe quick!\n\nDatabase hours: 9 AM - Midnight Central"
					popup(message, "Warning: Database Closing Soon")
		checkHours()

		#global USER_ID
		entry_user=customtkinter.CTkEntry(self,placeholder_text="user id")
		entry_user.grid(row=0,column=0, padx=50, pady=50,sticky='nsew')

		entry_pass=customtkinter.CTkEntry(self, placeholder_text="password")
		entry_pass.grid(row=0,column=1,padx=50,pady=50,sticky='nsew')

		def login():
			#global USER_ID
			if(Const.SKIP_LOGIN):
				Const.USER_ID="user"
				self.winfo_toplevel().title("Spotify Ranker")
				controller.show_frame(StartPage)
			else:
				tempUser_id=entry_user.get()
				password=entry_pass.get()

				def popup(error):
					top=customtkinter.CTkToplevel(self)
					top.attributes('-topmost',True)
					top.title("Error!")
					label_error=customtkinter.CTkLabel(top,text=error)
					label_error.grid(sticky='nsew',padx=50,pady=50)
					grid_size=customtkinter.CTk.grid_size(top)
					grid_numRows=grid_size[0]
					grid_numCols=grid_size[1]
					for row in range(grid_numRows):
						customtkinter.CTk.grid_rowconfigure(top,index=row,weight=1)
					for col	in range(grid_numCols):
						customtkinter.CTk.grid_columnconfigure(top,index=col,weight=1)

				if(tempUser_id=="" or password==""):
					popup("Error: Required Fields Left Blank!")
					print("Required Fields!")
				else:
					SQL="""select * from users where user_id='"""+tempUser_id+"""'"""
					result=SQLer.query(Const.DB, SQL)
					if(len(result)==0):
						popup("Error: Invalid User ID! \nIf you need to create an account, text Joe.\n281-691-1883")
						print("Invalid user_id")
					else:
						if(result[0][1]==password):
							Const.USER_ID=tempUser_id
							controller.show_frame(StartPage)
						else:
							popup("Error: Invalid password! \nTo reset your password, text Joe.\n281-691-1883")
							print("Invalid password")

		button_enter=customtkinter.CTkButton(self,text="Enter",command=login)
		button_enter.grid(row=0,column=2,padx=50, pady=50,sticky='nsew')
		
		grid_size=customtkinter.CTk.grid_size(self)
		grid_numRows=grid_size[0]
		grid_numCols=grid_size[1]
		for row in range(grid_numRows):
			customtkinter.CTk.grid_rowconfigure(self,index=row,weight=1)
		for col	in range(grid_numCols):
			customtkinter.CTk.grid_columnconfigure(self,index=col,weight=1)


# first window frame startpage
class StartPage(customtkinter.CTkFrame):
	def __init__(self, parent, controller):
		customtkinter.CTkFrame.__init__(self, parent)
		self.winfo_toplevel().title("Spotify Ranker")

		# label of frame Layout 2
		label_page = customtkinter.CTkLabel(self, text ="Startpage", font = Const.LARGEFONT)
		label_page.grid(row = 0, column = 0,columnspan=3,sticky="NSEW", padx = 10, pady = 10)

		label_entry=customtkinter.CTkLabel(self,text="Enter Album URL: ")
		label_entry.grid(column=0, row=2, padx=10, pady=10,sticky="NSEW")
		entry1=customtkinter.CTkEntry(self,width=240)
		entry1.grid(column=1,row=2,columnspan=2,sticky="EW")
		
		def rateButtonPress():
			pb=customtkinter.CTkProgressBar(self,mode="indeterminate",width=200, height=35)
			pb.grid(row=4,column=3,padx = 10, pady = 10)
			pb.start()
			entry_value=entry1.get()
			album=Ranker.getAlbum(entry_value)
			global album_id
			album_id=Ranker.getAlbumID(album)
			self.winfo_toplevel().title("Rate")
			controller.show_frame(Rate)
		button_rate=customtkinter.CTkButton(self,text="Rate",command=rateButtonPress)
		button_rate.grid(row=2,column=3,sticky="NSEW")

		def ratingsButtonPress():
			self.winfo_toplevel().title("Your Ratings")
			controller.show_frame(Ratings)
		button_ratings = customtkinter.CTkButton(self, text ="Ratings",command = ratingsButtonPress)
		button_ratings.grid(row=4, column=1,columnspan=2, padx = 10, pady = 50,sticky="SEW")

		grid_size=customtkinter.CTk.grid_size(self)
		grid_numRows=grid_size[0]
		grid_numCols=grid_size[1]
		for row in range(grid_numRows):
			customtkinter.CTk.grid_rowconfigure(self,index=row,weight=1)
		for col	in range(grid_numCols):
			customtkinter.CTk.grid_columnconfigure(self,index=col,weight=1)


# second window frame Ratings
class Ratings(customtkinter.CTkFrame):
	def __init__(self, parent, controller):
		#global DB
		customtkinter.CTkFrame.__init__(self, parent)
		self.winfo_toplevel().title("Your Ratings")

		def albumsByArtist():
			for widget in self.winfo_children():
					widget.destroy()

			SQL="""select distinct albums.album_type from albums JOIN scores on albums.album_id=scores.album_id WHERE scores.user_id='"""+Const.USER_ID+"""'"""
			result=SQLer.query(Const.DB,SQL)
			albumTypes=['All']
			for albumType in result:
				albumTypes.append(albumType[0])
			combo_albumType=customtkinter.CTkComboBox(self,values=albumTypes)
			combo_albumType.grid(row=2,column=1)

			combo_avgType=customtkinter.CTkComboBox(self,values=Const.AVG_TYPES)
			combo_avgType.grid(row=2,column=2)

			combo_orderType=customtkinter.CTkComboBox(self,values=Const.ORDER_TYPES)
			combo_orderType.grid(row=2,column=3)

			label_reportType=customtkinter.CTkLabel(self,text="Show as a: ")
			label_reportType.grid(row=2,column=4,sticky="E")
			combo_reportType=customtkinter.CTkComboBox(self,values=Const.REPORT_TYPES)
			combo_reportType.grid(row=2,column=5)

			label_lowerLimit=customtkinter.CTkLabel(self,text="Where score is greater than or equal to: ")
			label_lowerLimit.grid(row=3,column=4)
			combo_lowerLimit=customtkinter.CTkComboBox(self,values=Const.LIMITS)
			combo_lowerLimit.grid(row=3,column=5,pady=10)

			SQL="select distinct(artist) from albums JOIN scores ON albums.album_id=scores.album_id where scores.user_id='"+Const.USER_ID+"'order by artist"
			result=SQLer.query(Const.DB,SQL)
			artist_list=[]
			for artist in result:
				artist_list.append(artist[0][2:-2])
			combo_artists=customtkinter.CTkComboBox(self,values=artist_list)
			combo_artists.grid(row=2,column=0,sticky="nsew")

			def interim():
				pb=customtkinter.CTkProgressBar(self,mode="indeterminate",width=200, height=35)
				pb.grid(row=5,column=3,padx = 10, pady = 10)
				pb.start()
				Draw.popupQueryCount(self,"Artist",combo_artists.get(),combo_albumType.get(),combo_avgType.get(),combo_orderType.get(),combo_reportType.get(),combo_lowerLimit.get())
			button_execute=customtkinter.CTkButton(self,text="Execute",command=interim)
			button_execute.grid(row=2,rowspan=2,column=6,sticky="nsew")

			button_back=customtkinter.CTkButton(self,text="Back",command=reportBuilder)
			button_back.grid(row=0,column=0)

			def searchButtonPress():
				def popup(error):
					top=customtkinter.CTkToplevel(self)
					top.attributes('-topmost',True)
					top.title("Artist Not Found!")
					label_error=customtkinter.CTkLabel(top,text=error)
					label_error.grid(sticky='nsew',padx=50,pady=50)
					def okButtonPress():
						top.destroy()
					button_ok=customtkinter.CTkButton(top,text="Ok",command=okButtonPress)
					button_ok.grid(row=1,pady=25)

					grid_size=customtkinter.CTk.grid_size(top)
					grid_numRows=grid_size[0]
					grid_numCols=grid_size[1]
					for row in range(grid_numRows):
						customtkinter.CTk.grid_rowconfigure(top,index=row,weight=1)
					for col	in range(grid_numCols):
						customtkinter.CTk.grid_columnconfigure(top,index=col,weight=1)

				found=False
				entry=entry_artistSearch.get()
				for artist in artist_list:
					if(str.lower(entry) in str.lower(artist)):
						combo_artists.set(value=artist)
						found=True
						break
				if(not found):
					popup("No ratings found for this artist.")
					print("No ratings found for this artist.")
			 
			entry_artistSearch=customtkinter.CTkEntry(self,placeholder_text="Search for an artist")
			entry_artistSearch.grid(row=0,column=2,columnspan=4,pady=25,sticky="nsew")
			button_search=customtkinter.CTkButton(self, text="Search",command=searchButtonPress)
			button_search.grid(row=0,column=6)

			label_artist=customtkinter.CTkLabel(self,text="Artist:")
			label_artist.grid(row=1,column=0)
			label_albumType=customtkinter.CTkLabel(self,text="Album Type:")
			label_albumType.grid(row=1,column=1)
			label_avgType=customtkinter.CTkLabel(self,text="Average Method:")
			label_avgType.grid(row=1,column=2)
			label_orderBy=customtkinter.CTkLabel(self,text="Order By:")
			label_orderBy.grid(row=1,column=3)
			label_reportType=customtkinter.CTkLabel(self,text="Report Type:")
			label_reportType.grid(row=1,column=5)

		def albumsByYear():
			for widget in self.winfo_children():
					widget.destroy()
			
			SQL="""select distinct albums.album_type from albums JOIN scores on albums.album_id=scores.album_id WHERE scores.user_id='"""+Const.USER_ID+"""'"""
			result=SQLer.query(Const.DB,SQL)
			albumTypes=['All']
			for albumType in result:
				albumTypes.append(albumType[0])
			combo_albumType=customtkinter.CTkComboBox(self,values=albumTypes)
			combo_albumType.grid(row=1,column=1)

			combo_avgType=customtkinter.CTkComboBox(self,values=Const.AVG_TYPES)
			combo_avgType.grid(row=1,column=2)

			combo_orderType=customtkinter.CTkComboBox(self,values=Const.ORDER_TYPES)
			combo_orderType.grid(row=1,column=3)

			label_reportType=customtkinter.CTkLabel(self,text="Show as a ")
			label_reportType.grid(row=1,column=4)
			combo_reportType=customtkinter.CTkComboBox(self,values=Const.REPORT_TYPES)
			combo_reportType.grid(row=1,column=5)

			label_lowerLimit=customtkinter.CTkLabel(self,text="With scores greater than or equal to ")
			label_lowerLimit.grid(row=2,column=4)
			combo_lowerLimit=customtkinter.CTkComboBox(self,values=Const.LIMITS)
			combo_lowerLimit.grid(row=2,column=5)

			SQL="select distinct extract(year from release_date) as year from albums JOIN scores on albums.album_id=scores.album_id where scores.user_id='"+Const.USER_ID+"' order by year DESC"
			result=SQLer.query(Const.DB,SQL)
			year_list=[]
			for year in result:
				year_list.append(str(year[0]))
			combo_years=customtkinter.CTkComboBox(self,values=year_list)
			combo_years.grid(row=1,column=0,sticky="nsew")

			def interim():
				pb=customtkinter.CTkProgressBar(self,mode="indeterminate",width=200, height=35)
				pb.grid(row=4,column=3,padx = 10, pady = 10)
				pb.start()
				Draw.popupQueryCount(self,"Year",combo_years.get(),combo_albumType.get(),combo_avgType.get(),combo_orderType.get(),combo_reportType.get(),combo_lowerLimit.get())
			button_execute=customtkinter.CTkButton(self,text="execute",command=interim)
			button_execute.grid(row=1,column=6,sticky="nsew")

			button_back=customtkinter.CTkButton(self,text="Back",command=reportBuilder)
			button_back.grid(row=2,column=0)

		def albumsByDecade():
			for widget in self.winfo_children():
					widget.destroy()
			
			SQL="""select distinct albums.album_type from albums JOIN scores on albums.album_id=scores.album_id WHERE scores.user_id='"""+Const.USER_ID+"""'"""
			result=SQLer.query(Const.DB,SQL)
			albumTypes=['All']
			for albumType in result:
				albumTypes.append(albumType[0])
			combo_albumType=customtkinter.CTkComboBox(self,values=albumTypes)
			combo_albumType.grid(row=1,column=1)

			combo_avgType=customtkinter.CTkComboBox(self,values=Const.AVG_TYPES)
			combo_avgType.grid(row=1,column=2)

			combo_orderType=customtkinter.CTkComboBox(self,values=Const.ORDER_TYPES)
			combo_orderType.grid(row=1,column=3)

			label_reportType=customtkinter.CTkLabel(self,text="Show as a ")
			label_reportType.grid(row=1,column=4)
			combo_reportType=customtkinter.CTkComboBox(self,values=Const.REPORT_TYPES)
			combo_reportType.grid(row=1,column=5)

			label_lowerLimit=customtkinter.CTkLabel(self,text="With scores greater than or equal to ")
			label_lowerLimit.grid(row=2,column=4)
			combo_lowerLimit=customtkinter.CTkComboBox(self,values=Const.LIMITS)
			combo_lowerLimit.grid(row=2,column=5)

			SQL="select distinct extract(year from release_date) as year from albums JOIN scores on albums.album_id=scores.album_id where scores.user_id='"+Const.USER_ID+"' order by year DESC"
			result=SQLer.query(Const.DB,SQL)
			yearList=[]
			for year in result:
				yearList.append(str(int(int(year[0])/10))+"0")
			x=np.array(yearList)
			decadeList=np.unique(x)
			combo_decades=customtkinter.CTkComboBox(self,values=decadeList)
			combo_decades.grid(row=1,column=0,sticky="nsew")

			def interim():
				pb=customtkinter.CTkProgressBar(self,mode="indeterminate",width=200, height=35)
				pb.grid(row=4,column=3,padx = 10, pady = 10)
				pb.start()
				Draw.popupQueryCount(self,"Decade",combo_decades.get(),combo_albumType.get(),combo_avgType.get(),combo_orderType.get(),combo_reportType.get(),combo_lowerLimit.get())
			button_execute=customtkinter.CTkButton(self,text="execute",command=interim)
			button_execute.grid(row=1,column=6,sticky="nsew")

			button_back=customtkinter.CTkButton(self,text="Back",command=reportBuilder)
			button_back.grid(row=2,column=0)

		def albumsByHalfDecade():
			for widget in self.winfo_children():
					widget.destroy()
			
			SQL="""select distinct albums.album_type from albums JOIN scores on albums.album_id=scores.album_id WHERE scores.user_id='"""+Const.USER_ID+"""'"""
			result=SQLer.query(Const.DB,SQL)
			albumTypes=['All']
			for albumType in result:
				albumTypes.append(albumType[0])
			combo_albumType=customtkinter.CTkComboBox(self,values=albumTypes)
			combo_albumType.grid(row=1,column=1)

			combo_avgType=customtkinter.CTkComboBox(self,values=Const.AVG_TYPES)
			combo_avgType.grid(row=1,column=2)

			combo_orderType=customtkinter.CTkComboBox(self,values=Const.ORDER_TYPES)
			combo_orderType.grid(row=1,column=3)

			label_reportType=customtkinter.CTkLabel(self,text="Show as a ")
			label_reportType.grid(row=1,column=4)
			combo_reportType=customtkinter.CTkComboBox(self,values=Const.REPORT_TYPES)
			combo_reportType.grid(row=1,column=5)

			label_lowerLimit=customtkinter.CTkLabel(self,text="With scores greater than or equal to ")
			label_lowerLimit.grid(row=2,column=4)
			combo_lowerLimit=customtkinter.CTkComboBox(self,values=Const.LIMITS)
			combo_lowerLimit.grid(row=2,column=5)

			SQL="select distinct extract(year from release_date) as year from albums JOIN scores on albums.album_id=scores.album_id where scores.user_id='"+Const.USER_ID+"' order by year DESC"
			result=SQLer.query(Const.DB,SQL)
			yearList=[]
			for year in result:
				yearList.append(str(int(int(year[0])/10))+"0-"+str(int(int(year[0])/10))+"4")
				yearList.append(str(int(int(year[0])/10))+"5-"+str(int(int(year[0])/10))+"9")
			x=np.array(yearList)
			halfDecadeList=np.unique(x)
			combo_halfDecades=customtkinter.CTkComboBox(self,values=halfDecadeList)
			combo_halfDecades.grid(row=1,column=0,sticky="nsew")

			def interim():
				pb=customtkinter.CTkProgressBar(self,mode="indeterminate",width=200, height=35)
				pb.grid(row=4,column=3,padx = 10, pady = 10)
				pb.start()
				Draw.popupQueryCount(self,"HalfDecade",combo_halfDecades.get(),combo_albumType.get(),combo_avgType.get(),combo_orderType.get(),combo_reportType.get(),combo_lowerLimit.get())
			button_execute=customtkinter.CTkButton(self,text="execute",command=interim)
			button_execute.grid(row=1,column=6,sticky="nsew")

			button_back=customtkinter.CTkButton(self,text="Back",command=reportBuilder)
			button_back.grid(row=2,column=0)

		def albumsByAllTime():
			for widget in self.winfo_children():
					widget.destroy()
			
			SQL="""select distinct albums.album_type from albums JOIN scores on albums.album_id=scores.album_id WHERE scores.user_id='"""+Const.USER_ID+"""'"""
			result=SQLer.query(Const.DB,SQL)
			albumTypes=['All']
			for albumType in result:
				albumTypes.append(albumType[0])
			combo_albumType=customtkinter.CTkComboBox(self,values=albumTypes)
			combo_albumType.grid(row=1,column=1)

			combo_avgType=customtkinter.CTkComboBox(self,values=Const.AVG_TYPES)
			combo_avgType.grid(row=1,column=2)

			combo_orderType=customtkinter.CTkComboBox(self,values=Const.ORDER_TYPES)
			combo_orderType.grid(row=1,column=3)

			label_reportType=customtkinter.CTkLabel(self,text="Show as a ")
			label_reportType.grid(row=1,column=4)
			combo_reportType=customtkinter.CTkComboBox(self,values=Const.REPORT_TYPES)
			combo_reportType.grid(row=1,column=5)
			
			label_lowerLimit=customtkinter.CTkLabel(self,text="With scores greater than or equal to ")
			label_lowerLimit.grid(row=2,column=4)
			combo_lowerLimit=customtkinter.CTkComboBox(self,values=Const.LIMITS)
			combo_lowerLimit.grid(row=2,column=5)

			def interim():
				pb=customtkinter.CTkProgressBar(self,mode="indeterminate",width=200, height=35)
				pb.grid(row=4,column=3,padx = 10, pady = 10)
				pb.start()
				Draw.popupQueryCount(self,"AllTime","none",combo_albumType.get(),combo_avgType.get(),combo_orderType.get(),combo_reportType.get(),combo_lowerLimit.get())
			button_execute=customtkinter.CTkButton(self,text="execute",command=interim)
			button_execute.grid(row=1,column=7,sticky="nsew")

			button_back=customtkinter.CTkButton(self,text="Back",command=reportBuilder)
			button_back.grid(row=2,column=0)

		def albumsByAstro():
			for widget in self.winfo_children():
					widget.destroy()
			
			SQL="""select distinct albums.album_type from albums JOIN scores on albums.album_id=scores.album_id WHERE scores.user_id='"""+Const.USER_ID+"""'"""
			result=SQLer.query(Const.DB,SQL)
			albumTypes=['All']
			for albumType in result:
				albumTypes.append(albumType[0])
			combo_albumType=customtkinter.CTkComboBox(self,values=albumTypes)
			combo_albumType.grid(row=1,column=1)

			combo_avgType=customtkinter.CTkComboBox(self,values=Const.AVG_TYPES)
			combo_avgType.grid(row=1,column=2)

			combo_orderType=customtkinter.CTkComboBox(self,values=Const.ORDER_TYPES)
			combo_orderType.grid(row=1,column=3)

			label_reportType=customtkinter.CTkLabel(self,text="Show as a ")
			label_reportType.grid(row=1,column=4)
			combo_reportType=customtkinter.CTkComboBox(self,values=Const.REPORT_TYPES)
			combo_reportType.grid(row=1,column=5)

			label_lowerLimit=customtkinter.CTkLabel(self,text="With scores greater than or equal to ")
			label_lowerLimit.grid(row=2,column=4)
			combo_lowerLimit=customtkinter.CTkComboBox(self,values=Const.LIMITS)
			combo_lowerLimit.grid(row=2,column=5)

			combo_astros=customtkinter.CTkComboBox(self,values=Const.ASTROS[:,0])
			combo_astros.grid(row=1,column=0,sticky="nsew")

			def interim():
				pb=customtkinter.CTkProgressBar(self,mode="indeterminate",width=200, height=35)
				pb.grid(row=4,column=3,padx = 10, pady = 10)
				pb.start()
				Draw.popupQueryCount(self,"Astro",combo_astros.get(),combo_albumType.get(),combo_avgType.get(),combo_orderType.get(),combo_reportType.get(),combo_lowerLimit.get())
			button_execute=customtkinter.CTkButton(self,text="execute",command=interim)
			button_execute.grid(row=1,column=6,sticky="nsew")

			button_back=customtkinter.CTkButton(self,text="Back",command=reportBuilder)
			button_back.grid(row=2,column=0)

		def reportBuilder():
			for widget in self.winfo_children():
				widget.destroy()
			self.winfo_toplevel().title("Your Ratings")

			label = customtkinter.CTkLabel(self, text ="Report Builder", font = Const.LARGEFONT)
			label.grid(row = 0, column = 4, padx = 10, pady = 10)

			def startPageButtonPressed():
				self.winfo_toplevel().title("Spotify Ranker")
				controller.show_frame(StartPage)
			button1 = customtkinter.CTkButton(self, text ="Back",command = startPageButtonPressed)
			button1.grid(row = 0, column = 0, padx = 10, pady = 10)

			def reportOptions():
				reportOption=combo_reportByNumerator.get()+" by "+combo_reportByDenominator.get()
				if(reportOption=="Albums by Artist"):
					albumsByArtist()
				elif(reportOption=="Albums by Year"):
					albumsByYear()
				elif(reportOption=="Albums by Decade"):
					albumsByDecade()
				elif(reportOption=="Albums by Half-Decade"):
					albumsByHalfDecade()
				elif(reportOption=="Albums by All Time"):
					albumsByAllTime()
				elif(reportOption=="Albums by Astrological Sign"):
					albumsByAstro()
				else:
					print("Report Option Not Yet Available.")
			reportBuilderRow=1	
			
			label_show=customtkinter.CTkLabel(self,text="Show:")
			label_show.grid(row=reportBuilderRow,column=1, padx=10)
			combo_reportByNumerator=customtkinter.CTkComboBox(self,values=Const.REPORT_BY_NUMERATOR)
			combo_reportByNumerator.grid(row=reportBuilderRow,column=2)
			label_by=customtkinter.CTkLabel(self,text="By")
			label_by.grid(row=reportBuilderRow,column=3,padx=10)
			combo_reportByDenominator=customtkinter.CTkComboBox(self,values=Const.REPORT_BY_DENOMINATOR)
			combo_reportByDenominator.grid(row=reportBuilderRow,column=4)
			button_build=customtkinter.CTkButton(self,text="Build",command=reportOptions)
			button_build.grid(row=reportBuilderRow,column=5)
		reportBuilder()

		grid_size=customtkinter.CTk.grid_size(self)
		grid_numRows=grid_size[0]
		grid_numCols=grid_size[1]
		for row in range(grid_numRows):
			customtkinter.CTk.grid_rowconfigure(self,index=row,weight=1)
		for col	in range(grid_numCols):
			customtkinter.CTk.grid_columnconfigure(self,index=col,weight=1)


# third window frame Rate
class Rate(customtkinter.CTkFrame):
	def __init__(self, parent, controller):
		customtkinter.CTkFrame.__init__(self, parent)

		def sliderViewButtonPress():
			for widget in self.winfo_children():
				widget.destroy()
			self.winfo_toplevel().title("Rate")

			frame_slider=customtkinter.CTkFrame(self)
			frame_cells=customtkinter.CTkScrollableFrame(self,orientation='vertical',width=400, height=550)
			
			label_page = customtkinter.CTkLabel(self, text ="ALBUM TITLE", font = Const.LARGEFONT)
			label_page.grid(row = 0,columnspan=2, padx = 10, pady = 10,sticky="NSEW")
			label_artist=customtkinter.CTkLabel(self,text="ARTIST NAME")
			label_artist.grid(row=1,columnspan=2,padx = 10,sticky="NSEW")

			def finishButtonPress():
				pb=customtkinter.CTkProgressBar(self,mode="indeterminate",width=200, height=35)
				pb.grid(row=4,column=3,padx = 10, pady = 10)
				pb.start()

				score=labels_matrix_trackScores[currentTrack-1].cget("text")
				try:
					SQL=Ranker.ratingExists(Const.USER_ID,album_id,currentTrack)
					ratingExists=SQLer.query(Const.DB,SQL)
					if(ratingExists[0][0]==0):
						try:
							SQL=Ranker.insertScore(Const.USER_ID,album_id,currentTrack,score)
							SQLer.query(Const.DB,SQL)
						except Exception as e:
							print("Error inserting track score: "+str(e))
					else:
						try:
							SQL=Ranker.updateScore(Const.USER_ID, album_id, currentTrack,score)
							SQLer.query(Const.DB,SQL)
						except Exception as e:
							print("Error updating track score: "+str(e))
				except Exception as e:
					print("Error rating exists?: "+str(e))

				#reset this page
				#frame_slider.destroy()
				#frame_cells.destroy()
				initialView()

				#then go back to start page
				self.winfo_toplevel().title("Spotify Ranker")
				controller.show_frame(StartPage)

			global album_id
			global album
			album=Ranker.getAlbum(album_id)

			try:
				Ranker.insertAlbum(album)
			except:
				print("Error Inserting Album")

			SQL="""select count(tracks.name) from tracks where album_id='"""+album_id+"""'"""
			num_tracks=SQLer.query(Const.DB,SQL)[0][0]

			button_finish = customtkinter.CTkButton(frame_slider, text ="Finish",command = finishButtonPress)
			button_finish.grid(row = 2+5, column = 1, sticky="NSEW")

			response = requests.get(album['images'][0]['url'])
			img_data=response.content
			img=ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
			panel=customtkinter.CTkLabel(frame_slider, image=img, text="")
			panel.grid(row=2,column=1,sticky="NSEW")

			label_trackName=customtkinter.CTkLabel(frame_slider,text="TRACK NAME")
			label_trackName.grid(row=2+1,column=1, sticky="NSEW")
			label_trackNum=customtkinter.CTkLabel(frame_slider,text="Track X of Y")
			label_trackNum.grid(row=2+2,column=1, sticky="NSEW")

			global currentTrack
			currentTrack=1
			label_trackNum.configure(text="Track "+str(currentTrack)+" of "+str(Ranker.getNumTracks(album)))
			label_trackName.configure(text=Ranker.getTracksList(album)[currentTrack-1])
			if(len(album['name'])>49):
				albumName=album['name'][:46]+"..."
			else: 
				albumName=album['name']
			label_page.configure(text=albumName)
			artists=""
			for artist in album['artists']:
				artists=artist['name']+", "+artists
			label_artist.configure(text=artists[:-2])

			global labels_matrix_trackScores
			labels_matrix_trackScores=[]
			SQL="""select name from tracks where album_id='"""+album_id+"""' order by track_number"""
			trackNames=SQLer.query(Const.DB,SQL)
			SQL="""select score_id, score from scores where user_id='"""+Const.USER_ID+"""' AND album_id='"""+album_id+"""' order by track_number"""
			scores=SQLer.query(Const.DB,SQL)
			for trackNum in range(num_tracks):
				label_matrix_tracklist=customtkinter.CTkLabel(frame_cells,text=trackNum+1)
				label_matrix_tracklist.grid(row=2+trackNum,column=0,padx = 10,sticky="nsew")

				if(len(trackNames[trackNum][0])>49):
					trackName=trackNames[trackNum][0][:46]+"..."
				else:
					trackName=trackNames[trackNum][0]
				label_matrix_trackName=customtkinter.CTkLabel(frame_cells,text=trackName)
				label_matrix_trackName.grid(row=2+trackNum,column=1,padx = 10, pady = 5,sticky="nsew")

				score_id=Const.USER_ID+"_"+album_id+"_"+str(trackNum+1)
				try:
					trackScoreValue=-1
					for row in scores:
						if(row[0]==score_id):
							trackScoreValue=row[1]
							trackScore=trackScoreValue  
							break 
					if(trackScoreValue==-1):
						print("Error finding track score: " + trackNames[trackNum][0])
						trackScore=""
						trackScoreValue=-1 
				except:
					print("Error finding track score: " + trackNames[trackNum][0])
					trackScore=""
				if(trackScore==""):
					color_hex="transparent"
				else:
					color_hex=Draw.getHexColorCode(float(trackScore))
				label_matrix_trackScore=customtkinter.CTkLabel(frame_cells,text=trackScore,bg_color=color_hex,text_color="black")
				labels_matrix_trackScores.append(label_matrix_trackScore)
				labels_matrix_trackScores[trackNum].grid(row=2+trackNum,column=2,padx = 10,sticky="nsew")

			# button_updateImg=customtkinter.CTkButton(self,text="Update Img",command=updateImage)
			# button_updateImg.grid(row=8,column=1,padx = 10, pady = 10, sticky="NSEW")

			def slider_event(value):
				value=round(value,1)
				value_hex=Draw.getHexColorCode(value)
				label_sliderValue.configure(text=value)
				slider.configure(bg_color=value_hex)
				labels_matrix_trackScores[currentTrack-1].configure(text=value)
				labels_matrix_trackScores[currentTrack-1].configure(bg_color=value_hex)
			slider = customtkinter.CTkSlider(master=frame_slider, from_=1, to=10, command=slider_event, number_of_steps=90,bg_color="#8e7100", progress_color="transparent", border_color="transparent", button_color="#FFFFFF", button_hover_color="#FFFFFF", button_corner_radius=5, height=50, border_width=30)
			slider.set(5)
			slider.grid(row=2+3,column=1, sticky='NSEW')
			label_sliderValue=customtkinter.CTkLabel(frame_slider,text=slider.get())
			label_sliderValue.grid(row=2+4,column=1,sticky="NSEW",padx = 10, pady = 10)

			def nextButtonPress():
				global currentTrack
				#global USER_ID
				#save current score first
				#score=label_sliderValue.cget("text")
				score=labels_matrix_trackScores[currentTrack-1].cget("text")
				if(currentTrack<Ranker.getNumTracks(album) and score>0):
					try:
						SQL=Ranker.ratingExists(Const.USER_ID,album_id,currentTrack)
						ratingExists=SQLer.query(Const.DB,SQL)
						if(ratingExists[0][0]==0):
							try:
								SQL=Ranker.insertScore(Const.USER_ID,album_id,currentTrack,score)
								SQLer.query(Const.DB,SQL)
							except Exception as e:
								print("Error inserting track score: "+str(e))
						else:
							try:
								SQL=Ranker.updateScore(Const.USER_ID, album_id, currentTrack,score)
								SQLer.query(Const.DB,SQL)
							except Exception as e:
								print("Error updating track score: "+str(e))
					except Exception as e:
						print("Error rating exists?: "+str(e))

					score_id=Const.USER_ID+"_"+album_id+"_"+str(currentTrack)
					try:
						trackScoreValue=-1
						for row in scores:
							if(row[0]==score_id):
								trackScoreValue=row[1]
								trackScore=trackScoreValue  
								break 
						if(trackScoreValue==-1):
							print("Error finding track score: " + trackNames[currentTrack][0])
							trackScore=""
					except:
						print("Error finding track score: " + trackNames[currentTrack][0])
						trackScore=""
						trackScoreValue=-1 
					# score=tk.StringVar()
					# score.set(trackScore)
					#labels_matrix_trackScores[currentTrack-1].configure(text=trackScore)
					#color_hex=Draw.getHexColorCode(float(trackScoreValue))
					#labels_matrix_trackScores[currentTrack-1].configure(bg_color=color_hex)

					#then increment current track and update labels
					currentTrack+=1
					label_trackNum.configure(text="Track "+str(currentTrack)+" of "+str(Ranker.getNumTracks(album)))
					label_trackName.configure(text="TRACK NAME")
					label_trackName.configure(text=Ranker.getTracksList(album)[currentTrack-1])
			button_next=customtkinter.CTkButton(frame_slider,text="Next Track",command=nextButtonPress)
			button_next.grid(row=2+3,column=2,sticky="NSEW")

			def prevButtonPress():
				global currentTrack

				if(currentTrack>1):
					#decrement current track and update labels
					currentTrack-=1
					label_trackNum.configure(text="Track "+str(currentTrack)+" of "+str(Ranker.getNumTracks(album)))
					label_trackName.configure(text=Ranker.getTracksList(album)[currentTrack-1])
			button_prev=customtkinter.CTkButton(frame_slider,text="Prev Track",command=prevButtonPress)
			button_prev.grid(row=2+3,column=0,sticky="NSEW")

			frame_slider.grid(row=2,column=0,sticky="NSEW")
			frame_cells.grid(row=2,column=1,sticky="NSEW")

			# grid_size=customtkinter.CTk.grid_size(self)
			# grid_numRows=grid_size[0]
			# grid_numCols=grid_size[1]
			# for row in range(grid_numRows):
			# 	customtkinter.CTk.grid_rowconfigure(self,index=row,weight=1)
			# for col	in range(grid_numCols):
			# 	customtkinter.CTk.grid_columnconfigure(self,index=col,weight=1)

		def cellsViewButtonPress():
			for widget in self.winfo_children():
				widget.destroy()
			self.winfo_toplevel().title("Rate")
			frame_list=customtkinter.CTkScrollableFrame(self,orientation='vertical',width=600,height=550)
			frame_list.grid(row=2,column=1, columnspan=3)

			global album_id
			global album
			album=Ranker.getAlbum(album_id)

			try:
				Ranker.insertAlbum(album)
			except:
				print("Error Inserting Album")

			artists=""
			for artist in album['artists']:
				artists=artist['name']+", "+artists
			if(len(album['name'])>49):
				albumName=album['name'][:46]+"..."
			else: 
				albumName=album['name']
			label_page = customtkinter.CTkLabel(self, text=albumName, font = Const.LARGEFONT)
			label_page.grid(row = 0,column=1,columnspan=3, padx = 10, pady = 10,sticky="NSEW")
			label_artist=customtkinter.CTkLabel(self,text=artists[:-2])
			label_artist.grid(row=1,column=1,columnspan=3,padx = 10, pady = 10,sticky="NSEW")

			SQL="""select count(tracks.name) from tracks where album_id='"""+album_id+"""'"""
			num_tracks=SQLer.query(Const.DB,SQL)[0][0]

			entries_matrix_trackScores=[]
			SQL="""select name from tracks where album_id='"""+album_id+"""' order by track_number"""
			trackNames=SQLer.query(Const.DB,SQL)
			SQL="""select score_id, score from scores where user_id='"""+Const.USER_ID+"""' AND album_id='"""+album_id+"""' order by track_number"""
			scores=SQLer.query(Const.DB,SQL)
			for trackNum in range(num_tracks):
				label_matrix_tracklist=customtkinter.CTkLabel(frame_list,text=trackNum+1)
				label_matrix_tracklist.grid(row=trackNum,column=1,padx = 10, pady = 5,sticky="nsew")

				if(len(trackNames[trackNum][0])>55):
					trackName=trackNames[trackNum][0][:52]+"..."
				else: 
					trackName=trackNames[trackNum][0]
				label_matrix_trackName=customtkinter.CTkLabel(frame_list,text=trackName)
				label_matrix_trackName.grid(row=trackNum,column=2,padx = 10,sticky="nsew")

				score_id=Const.USER_ID+"_"+album_id+"_"+str(trackNum+1)
				try:
					trackScoreValue=-1
					for row in scores:
						if(row[0]==score_id):
							trackScoreValue=row[1]
							trackScore=trackScoreValue  
							break 
					if(trackScoreValue==-1):
						print("Error finding track score: " + trackNames[trackNum][0])
						trackScore=""
				except:
					print("Error finding track score: " + trackNames[trackNum][0])
					trackScore=""
					trackScoreValue=-1

				score=tk.StringVar()
				score.set(trackScore)
				entry_matrix_trackScore=customtkinter.CTkEntry(frame_list,textvariable=score)
				entries_matrix_trackScores.append(entry_matrix_trackScore)
				entries_matrix_trackScores[trackNum].grid(row=trackNum,column=3,padx = 10,sticky="nsew")

			def finishButtonPress():
				pb=customtkinter.CTkProgressBar(self,mode="indeterminate",width=200, height=35)
				pb.grid(row=4,column=4,padx = 10, pady = 10)
				pb.start()
				
				def popup(error):
					top=customtkinter.CTkToplevel(self)
					top.attributes('-topmost',True)
					top.title("Error!")
					label_error=customtkinter.CTkLabel(top,text=error)
					label_error.grid(sticky='nsew',padx=50,pady=50)
					def okButtonPress():
						top.destroy()
					button_ok=customtkinter.CTkButton(top,text="Ok",command=okButtonPress)
					button_ok.grid(row=1,column=0,padx = 10, pady = 10,sticky="nsew")
					grid_size=customtkinter.CTk.grid_size(top)
					grid_numRows=grid_size[0]
					grid_numCols=grid_size[1]
					for row in range(grid_numRows):
						customtkinter.CTk.grid_rowconfigure(top,index=row,weight=1)
					for col	in range(grid_numCols):
						customtkinter.CTk.grid_columnconfigure(top,index=col,weight=1)
				
				willExit=True

				i=0
				for entry in entries_matrix_trackScores:
					try:
						SQL=Ranker.ratingExists(Const.USER_ID,album_id,i+1)
						ratingExists=SQLer.query(Const.DB,SQL)
						try:
							score=round(float(entry.get()),1)
							if(score<1 or score >10):
								popup("Invalid Score Value: '"+entry.get()+"'\nScore value must be in 1.0 <= score <= 10.0.")
								willExit=False
								break
						except:
							popup("Invalid Score Value: '"+entry.get()+"'\nScore value must be in 1.0 <= score <= 10.0.")
							print("Invalid score!")
							willExit=False
							break
						if(ratingExists[0][0]==0):
							try:
								SQL=Ranker.insertScore(Const.USER_ID,album_id,i+1,score)
								SQLer.query(Const.DB,SQL)
							except Exception as e:
								print("Error inserting track score: "+str(e))
						else:
							try:
								SQL=Ranker.updateScore(Const.USER_ID, album_id,i+1,score)
								SQLer.query(Const.DB,SQL)
							except Exception as e:
								print("Error updating track score: "+str(e))
					except Exception as e:
						print("Error rating exists?: "+str(e))
					i+=1

				if(willExit):
					#reset this page
					initialView()

					#then go back to start page
					self.winfo_toplevel().title("Spotify Ranker")
					controller.show_frame(StartPage)
			
			def backButtonPress():
				top=customtkinter.CTkToplevel(self)
				top.attributes('-topmost',True)
				top.title("Go Back?")
				label_error=customtkinter.CTkLabel(top,text="Any ratings you have entered on this page will not be saved!\n\nContinue?")
				label_error.grid(columnspan=2,sticky='nsew',padx=50,pady=50)
				def cancelButtonPress():
					top.destroy()
				def okButtonPress():
					top.destroy()
					#reset this page
					initialView()
					#then go back to start page
					self.winfo_toplevel().title("Spotify Ranker")
					controller.show_frame(StartPage)

				button_ok=customtkinter.CTkButton(top,text="Ok",command=okButtonPress)
				button_ok.grid(row=1,column=0,padx = 10, pady = 10,sticky="nsew")
				button_cancel=customtkinter.CTkButton(top,text="Cancel",command=cancelButtonPress)
				button_cancel.grid(row=1,column=1,padx = 10, pady = 10,sticky="nsew")
				grid_size=customtkinter.CTk.grid_size(top)
				grid_numRows=grid_size[0]
				grid_numCols=grid_size[1]
				for row in range(grid_numRows):
					customtkinter.CTk.grid_rowconfigure(top,index=row,weight=1)
				for col	in range(grid_numCols):
					customtkinter.CTk.grid_columnconfigure(top,index=col,weight=1)

			button_finish=customtkinter.CTkButton(self,text="Finish",command=finishButtonPress)
			button_finish.grid(row=3,column=1,columnspan=3,padx = 10, pady = 10,sticky="nsew")
			button_back=customtkinter.CTkButton(self,text="Back",command=backButtonPress)
			button_back.grid(row=0,column=0,padx = 10, pady = 10,sticky="nsew")

			grid_size=customtkinter.CTk.grid_size(self)
			grid_numRows=grid_size[0]
			grid_numCols=grid_size[1]
			for row in range(grid_numRows):
				customtkinter.CTk.grid_rowconfigure(frame_list,index=row,weight=1)
			for col	in range(grid_numCols):
				customtkinter.CTk.grid_columnconfigure(frame_list,index=col,weight=1)

		def initialView():
			for widget in self.winfo_children():
				widget.destroy()
			label_choose=customtkinter.CTkLabel(self, text="How would you like to rate this album?")
			label_choose.grid(row=0,column=0,columnspan=2,padx=10,pady=10)
			button_cellView=customtkinter.CTkButton(self,text="Grid View",command=cellsViewButtonPress)
			button_cellView.grid(row=1,column=1,padx=10,pady=10)
			button_sliderView=customtkinter.CTkButton(self,text="Slider View",command=sliderViewButtonPress)
			button_sliderView.grid(row=1,column=0,padx=10,pady=10)
		initialView()

# Driver Code
app = App()
app.mainloop()
