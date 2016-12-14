import sublime
import sublime_plugin

class IsModifiedCommand(sublime_plugin.TextCommand, sublime_plugin.ViewEventListener):
    def run(self,edit):
        on_modify(self.view)