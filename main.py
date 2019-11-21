try:
	import kivy

	from kivy.app import App

	from kivy.uix.screenmanager import ScreenManager, Screen
	from kivy.core.window import Window

	from kivy.uix.gridlayout import GridLayout
	from kivy.uix.floatlayout import FloatLayout
	from kivy.uix.scrollview import ScrollView

	from kivy.uix.image import Image
	from kivy.uix.behaviors import ButtonBehavior
	from kivy.uix.widget import Widget
	from kivy.uix.checkbox import CheckBox
	from kivy.uix.togglebutton import ToggleButton
	from kivy.uix.button import Button
	from kivy.uix.label import Label

	from codecs import open as co_open
	from json import dump as j_dump
	from json import load as j_load

	from os import listdir, remove, walk, makedirs
	from os.path import dirname, exists
	from shutil import copyfile, move

	import cv2
	import numpy as np
	from functools import partial
	from json_funs import *
except:
	pass

class ImageButton(ButtonBehavior, Image):
	pass

class HomeScreen(Screen):
	def __init__(self,**kwargs):
		super(HomeScreen,self).__init__(**kwargs)
		self.savePath = "answers.json"
		self.imageFolder = "./images/"
		self.imageExt = ".jpg"
		self.fontStyle = "./font/LobsterTwo-BoldItalic.otf"
		self.fontSize = 30

		self.defineView()
		self.getQuestions()
		self.getOptions()
		self.getImageList()

		self.currIndex = 0
		self.lastIndex = len(self.images) - 1

		self.totImages = np.max(self.images)
		self.totQuestions = len(self.questions)

		print(self.totImages)
		self.preAnnots = True
		self.loadAnswers()

		self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
		self._keyboard.bind(on_key_down=self._on_keyboard_down)

	def _keyboard_closed(self):
		self._keyboard.unbind(on_key_down=self._on_keyboard_down)
		self._keyboard = None

	def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
		# Reading Keyboard Inputs
		key_no, self.pressed_key = keycode

		# Shortcut Keys
		if(self.pressed_key=="s"):
			self.saveAnswers()
		elif(self.pressed_key=="a" or self.pressed_key=="left"):
			self.changeImage(-1)
		elif(self.pressed_key=="d" or self.pressed_key=="right"):
			self.changeImage(+1)

	def defineView(self):
		self.imageXs, self.imageYs = [0.3,0.7], [0.8,0.8]
		self.imageW,  self.imageH  = 0.4, 0.4

		self.nextBtnX, self.nextBtnY = 0.95, 0.8
		self.nextBtnW, self.nextBtnH = 0.1, 0.4
		self.prevBtnX, self.prevBtnY = 0.05, 0.8
		self.prevBtnW, self.prevBtnH = 0.1, 0.4

		self.qScrollX, self.qScrollY = 0.5, 0.3
		self.qScrollW, self.qScrollH = 1.0, 0.6

		self.qTabHeight = 200
		self.qTabQue = 0.5
		self.qTabAns = 0.25

	def getQuestions(self):
		self.questions = [chr(97+i)*250 for i in range(26)]

	def getOptions(self):
		self.options = {0:["A","B","AB"],1:["sure","somewhat sure","not very sure"]}

	def getImageList(self):
		self.images = [[1,2],[3,5],[7,20]]

	def on_pre_enter(self):
		self.cust_pre_enter()

	def cust_pre_enter(self):
		self.clear_widgets()
		self.showImages()
		self.showButtons()
		self.showQuestions()

	def showImages(self):
		for i in range(2):
			imageName = self.imageFolder + str(self.images[self.currIndex][i]) + self.imageExt
			image = ImageButton(source=imageName,keep_ratio=True,allow_stretch=True,size_hint=(self.imageW,self.imageH),pos_hint={"center_x":self.imageXs[i],"center_y":self.imageYs[i]})
			self.add_widget(image)

	def showButtons(self):
		if(0!=self.currIndex):
			fun = partial(self.changeImage,-1)
			fontColor = (1.0,1.0,1.0,1.0)
		else:
			fun = self.doNothing
			fontColor = (1.0,1.0,1.0,0.5)
		prevBtn = Button(text="<",halign='center',font_size=self.fontSize*2,background_color=(0,0,0,0),size_hint=(self.prevBtnW,self.prevBtnH),pos_hint={"center_x":self.prevBtnX,"center_y":self.prevBtnY},font_name=self.fontStyle,color=fontColor,on_press=fun)
		self.add_widget(prevBtn)
		if(self.lastIndex!=self.currIndex):
			fun = partial(self.changeImage,1)
			fontColor = (1.0,1.0,1.0,1.0)
		else:
			fun = self.doNothing
			fontColor = (1.0,1.0,1.0,0.5)
		nextBtn = Button(text=">",halign='center',font_size=self.fontSize*2,background_color=(0,0,0,0),size_hint=(self.nextBtnW,self.nextBtnH),pos_hint={"center_x":self.nextBtnX,"center_y":self.nextBtnY},font_name=self.fontStyle,color=fontColor,on_press=fun)
		self.add_widget(nextBtn)

	def changeImage(self,index,_="_"):
		if(0<=self.currIndex + index and self.currIndex + index<=self.lastIndex):
			self.currIndex += index
			self.cust_pre_enter()
			self.saveAnswers()

	def showQuestions(self):
		Play = ScrollView(size_hint=(self.qScrollW,self.qScrollH),pos_hint={"center_x":self.qScrollX,"center_y":self.qScrollY}, size=(Window.width, Window.height))
		Roll = GridLayout(cols=1,spacing=25,padding=10,size_hint_y=None)
		Roll.bind(minimum_height=Roll.setter('height'))
		Play.add_widget(Roll)
		self.add_widget(Play)


		for qNo in range(len(self.questions)):
			qTab = GridLayout(cols=1,size_hint=(1.0,None),height=self.qTabHeight,spacing=5,padding=10)
			qTab.bind(minimum_height=qTab.setter('height'))
			question = Button(text=self.questions[qNo],halign='center',font_size=self.fontSize,background_color=(0.4,0.4,0.4,0.4),size_hint=(1.0,None),font_name=self.fontStyle,color=(1,1,1,1))
			question.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
			question.bind(texture_size=question.setter("size"))
			qTab.add_widget(question)

			for listNo in range(len(self.options)):
				optTab = GridLayout(cols=len(self.options[listNo]),size_hint=(1.0,None))
				optTab.bind(minimum_height=optTab.setter('height'))
				for optNo in range(len(self.options[listNo])):
					btn = ToggleButton(text=self.options[listNo][optNo],halign='center', state="normal", group=str(qNo) + "-" + str(listNo), font_name=self.fontStyle, font_size=self.fontSize, background_color=(0.5,0.5,0.5,0.5), size_hint_y=None)
					btn.bind(width=lambda s,w: s.setter("text_size")(s,(w,None)))
					btn.bind(texture_size=btn.setter("size"))
					btn.bind(on_release=partial(self.set_option,qNo,listNo,optNo))
					if(self.answers[self.images[self.currIndex][0]-1,self.images[self.currIndex][1]-1,qNo,listNo]==optNo+1):
						btn.state = "down"
					optTab.add_widget(btn)

				qTab.add_widget(optTab)
			Roll.add_widget(qTab)

	def set_option(self,qNo,listNo,optNo,instance,_="_"):
		if(instance.state == "down"):
			self.answers[self.images[self.currIndex][0]-1,self.images[self.currIndex][1]-1,qNo,listNo] = optNo+1
		else:
			self.answers[self.images[self.currIndex][0]-1,self.images[self.currIndex][1]-1,qNo,listNo] = 0
 
	def doNothing(self,_="_"):
		pass

	def saveAnswers(self):
		write_json(self.answers.tolist(),self.savePath)

	def loadAnswers(self):
		if(exists(self.savePath) and self.preAnnots):
			print("loading")
			self.answers = np.array(read_json(self.savePath))
		else:
			self.answers = np.zeros((self.totImages,self.totImages,self.totQuestions,2),dtype="int8")

class MainClass(App):
	def build(self):
		ScreenMan = ScreenManagerbuild()

		ScreenMan.add_widget(HomeScreen(name='home_window'))

		return ScreenMan

class ScreenManagerbuild(ScreenManager):
	pass

if __name__ == '__main__':
	MainClass().run()
