import sublime, sublime_plugin
import copy # needed for deepcopy with layouts

# SideBar SublimeText Controller
# Thanks to the following resources:
#	https://github.com/SublimeText/Origami
#	http://www.sublimetext.com/forum/viewtopic.php?f=6&t=7284
#	http://www.asciiflow.com/#Draw7061136993147687848

class Layout(object):
	def __init__(self, layout, width, btype):
		self.cells = layout["cells"]
		self.cols  = layout["cols"]
		self.rows  = layout["rows"]

		self.sidebarIndex = None

		self.btype = btype

		self.width = width

		self.originalLayout = copy.deepcopy(layout)

	def add_sidebar(self, name = "Information"):
		self.sidebarIndex = len(self.cells)
		if self.btype == "VERTICAL":
			self.cols.insert(-1,self.width)
			self.cells.append([len(self.cols)-2,0,len(self.cols)-1,len(self.rows)-1])
		if self.btype == "HORIZONTAL":
			self.rows.insert(-1,self.width)
			self.cells.append([0,len(self.rows)-2,len(self.cols)-1, len(self.rows)-1])

	def get_layout(self):
		return {"cols": self.cols, "rows": self.rows, "cells": self.cells}

class TextEntry(object):
	def __init__(self, text, title, region):
		self.text   = text
		self.title  = title
		self.region = region
	def adjust(self, amount, regionObject):
		self.region = regionObject(self.region.a - amount, self.region.b - amount)


class SidebarController(object):
	def __init__(self, window, bar_type="HORIZONTAL", element_delimiter="-", width=.75):
		self.window = window
		self.view   = self.window.active_view()

		self.layout = Layout(self.window.get_layout(), width, bar_type)

		self.element_delimiter = element_delimiter

		self.originalViewIndex = self.window.get_view_index(self.view)[1]

		self.bufferPointer = 0
		self.sidebarWidth  = 0

		self.elements = []


	def create(self, name="Information"):
		self.layout.add_sidebar()
		self.window.set_layout(self.layout.get_layout())

		self.focusCall(self.createFile, name)
		self.focusCall(self.fixSettings)
		self.fixSettings()

	def fixSettings(self):
		settings = self.sidebarView.settings()

		settingsToSetFalse = ["line_numbers","gutter","draw_indent_guides"]
		for item in settingsToSetFalse:
			settings.set(item,False)

		self.window.run_command("toggle_minimap");

	def createFile(self, *args):
		self.sidebarView = self.window.new_file()
		self.sidebarView.set_name(args[0])
		self.sidebarWidth = int(self.sidebarView.viewport_extent()[0]/self.sidebarView.em_width())

	def closeSidebar(self):
		dummyAllElement = TextEntry("","",sublime.Region(0,self.bufferPointer))
		self.delete(dummyAllElement, force=True)
		self.window.run_command("close");

	def focusCall(self, callback, *args):
		self.window.focus_group(self.layout.sidebarIndex)
		if args:
			callback(*args)
		else:
			callback()
		self.window.focus_group(self.originalViewIndex)


	def add(self, title=None, text=None):
		if not text: return None

		self.sidebarView.set_read_only(False)

		startBuffer = self.bufferPointer

		total = ""

		total += self.element_delimiter*self.sidebarWidth + "\n"
		if title:
			total += " " * ((self.sidebarWidth-len(title))/2) + title + "\n"
			total += self.element_delimiter*self.sidebarWidth + "\n"
		total += text + "\n\n\n"

		edit = self.sidebarView.begin_edit()
		self.bufferPointer += self.sidebarView.insert(edit, self.bufferPointer, total)
		self.sidebarView.end_edit(edit)

		self.sidebarView.set_read_only(True)

		textElement =  TextEntry(text, title, sublime.Region(startBuffer, self.bufferPointer))

		self.elements.append(textElement)

		return textElement

	def delete(self, element, force=False):
		if element not in self.elements and not force:
			return

		self.sidebarView.set_read_only(False)

		edit = self.sidebarView.begin_edit()
		self.sidebarView.erase(edit, element.region)
		self.bufferPointer -= element.region.size()
		self.sidebarView.end_edit(edit)

		self.sidebarView.set_read_only(True)

		if not force:
			self.adjustElements(self.elements.index(element), element.region.size())
			self.elements.remove(element)

	def adjustElements(self, midpoint, amount):
		for element in self.elements[midpoint:]:
			element.adjust(amount, sublime.Region)


	def destroy(self):
		self.focusCall(self.closeSidebar)
		self.window.set_layout(self.layout.originalLayout)

class SideBarCommand(sublime_plugin.WindowCommand, sublime.View):
    def run(self):
		infobar = SidebarController(self.window, bar_type="VERTICAL", element_delimiter="-", width=.75)
		infobar.create("Infobar!")

		text1 = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed nec egestas massa. Nam ligula elit, sagittis ut rhoncus nec, suscipit vitae nunc. Suspendisse id ante ac metus adipiscing ornare eget eu quam. Morbi vel porta tortor. Fusce vehicula euismod libero, eget hendrerit nisi bibendum a."""
		text2 = """Nunc scelerisque egestas interdum. Sed pharetra semper nisl, nec posuere nibh tempus in. Maecenas ac urna libero. Integer et arcu at quam vulputate euismod non sed ante. Nullam luctus velit vel erat aliquam placerat lacinia lacus imperdiet."""

		element1 = infobar.add("Item # 1",text1)
		element2 = infobar.add("Item # 2",text2)

		# infobar.delete(element1)
		# infobar.delete(element2)

		# infobar.destroy()


