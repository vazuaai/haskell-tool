import sublime
import sublime_plugin
import os
import threading
import time
import sublime
import sublime_plugin

class OutputPanelCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.panel = self.view.window().create_output_panel('sf_st3_output')
        self.view.window().run_command('show_panel', { 'panel': 'output.sf_st3_output' })
        self.panel.run_command('sfprint')

