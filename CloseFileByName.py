import sublime
import sublime_plugin

class CloseFileCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.active_view().close()