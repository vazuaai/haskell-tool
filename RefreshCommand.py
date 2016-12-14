import sublime
import sublime_plugin
    
class RefreshCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.active_view().run_command("revert")
