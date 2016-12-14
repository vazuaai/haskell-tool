import sublime
import sublime_plugin

class FoldersCommand(sublime_plugin.WindowCommand):

	def run(self):

		folderlist = []
		folderlist = sublime.active_window().folders() 
		#self.view.window().folders()

		print("\nThe opened folders on the sidebar: " )
		for i in folderlist:0
			print(i)

		return folderlist
