import sublime, sublime_plugin
import copy

class Layout(object):
	def __init__(self, layout, width, bar_type):
		self.cells = layout["cells"]
		self.cols  = layout["cols"]
		self.rows  = layout["rows"]

		self.sidebar_index = None

		self.bar_type = bar_type

		self.width = width

		self.originalLayout = copy.deepcopy(layout)

	def add_sidebar(self, name = "Information"):
		self.sidebar_index = len(self.cells)
		if self.bar_type == "VERTICAL":
			self.cols.insert(-1,self.width)
			self.cells.append([len(self.cols)-2,0,len(self.cols)-1,len(self.rows)-1])
		if self.bar_type == "HORIZONTAL":
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
		"""
		Utility function to adjust regions when text is removed from the sidebar.
		"""
		self.region = regionObject(self.region.a - amount, self.region.b - amount)


class SidebarController(object):
	def __init__(self, window, bar_type="HORIZONTAL", element_delimiter="-", width=.75):
		self.window = window
		self.view   = self.window.active_view()

		self.layout = Layout(self.window.get_layout(), width, bar_type)

		self.element_delimiter = element_delimiter

		self.original_view_index = self.window.get_view_index(self.view)[1]

		self.buffer_pointer = 0
		self.sidebar_width  = 0

		self.elements = []


	def create(self, name="Information"):
		self.layout.add_sidebar()
		self.window.set_layout(self.layout.get_layout())

		self.focus_call(self.create_file, name)
		self.focus_call(self.fix_settings)
		self.fix_settings()

	def fix_settings(self):
		settings = self.sidebar_view.settings()

		settingsToSetFalse = ["line_numbers","gutter","draw_indent_guides"]
		for item in settingsToSetFalse:
			settings.set(item,False)

		self.window.run_command("toggle_minimap");

	def create_file(self, *args):
		self.sidebar_view = self.window.new_file()
		self.sidebar_view.set_name(args[0])
		self.sidebar_width = int(self.sidebar_view.viewport_extent()[0]/self.sidebar_view.em_width())

	def close_sidebar(self):
		dummyAllElement = TextEntry("","",sublime.Region(0,self.buffer_pointer))
		self.delete(dummyAllElement, force=True)
		self.window.run_command("close");

	def focus_call(self, callback, *args):
		self.window.focus_group(self.layout.sidebar_index)
		if args:
			callback(*args)
		else:
			callback()
		self.window.focus_group(self.original_view_index)


	def add(self, title=None, text=None):
		if not text: return None

		self.sidebar_view.set_read_only(False)

		start_buffer = self.buffer_pointer

		total = ""

		total += self.element_delimiter*self.sidebar_width + "\n"
		if title:
			total += " " * ((self.sidebar_width-len(title))/2) + title + "\n"
			total += self.element_delimiter*self.sidebar_width + "\n"
		total += text + "\n\n\n"

		edit = self.sidebar_view.begin_edit()
		self.buffer_pointer += self.sidebar_view.insert(edit, self.buffer_pointer, total)
		self.sidebar_view.end_edit(edit)

		self.sidebar_view.set_read_only(True)

		textElement =  TextEntry(text, title, sublime.Region(start_buffer, self.buffer_pointer))

		self.elements.append(textElement)

		return textElement

	def delete(self, element, force=False):
		if element not in self.elements and not force:
			return

		self.sidebar_view.set_read_only(False)

		edit = self.sidebar_view.begin_edit()
		self.sidebar_view.erase(edit, element.region)
		self.buffer_pointer -= element.region.size()
		self.sidebar_view.end_edit(edit)

		self.sidebar_view.set_read_only(True)

		if not force:
			self.adjust_elements(self.elements.index(element), element.region.size())
			self.elements.remove(element)

	def adjust_elements(self, midpoint, amount):
		for element in self.elements[midpoint:]:
			element.adjust(amount, sublime.Region)


	def destroy(self):
		self.focus_call(self.close_sidebar)
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


