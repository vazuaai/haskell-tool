import sublime
import sublime_plugin
    
class IsDirtyCommand(sublime_plugin.WindowCommand):
    def run(self, edit):
        isDirty = self.view.is_dirty()

        if isDirty == True:
        	self.view.insert(edit, 0, "#This file is dirty.\n")
        else:
        	self.view.insert(edit, 0, "#This file is clean.\n") #yxcxycsadasd
