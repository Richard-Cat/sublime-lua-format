import os
import sublime, sublime_plugin, sys
import subprocess


class LuaFormatCommand(sublime_plugin.TextCommand):
    def run(self, edit, error=True, save=True):
        # run lua-format
        package_path = os.path.split(os.path.dirname(__file__))[1]
        executable_path = os.path.join(sublime.packages_path(), package_path, "bin", sys.platform, "lua-format")

        contents = self.view.substr(sublime.Region(0, self.view.size()))

        cmd = [executable_path]
        configFile = sublime.load_settings("LuaFormatter.sublime-settings").get("config_file", "")
        if configFile != "":
            cmd.append("-c")
            cmd.append(configFile)

        startupinfo = None
        IS_WIN32 = "win32" in str(sys.platform).lower()
        if IS_WIN32:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
        process.stdin.write(str.encode(contents))
        process.stdin.close()
        output = bytes.decode(process.stdout.read()).replace("\r\n", "\n")
        error = bytes.decode(process.stderr.read())
        if error == "":
            self.view.replace(edit, sublime.Region(0, self.view.size()), output)
        else:
            sublime.error_message(error)


class LuaFormatOnPreSave(sublime_plugin.EventListener):
    def on_pre_save(self, view):
        if view.file_name().endswith(".lua"):
            config = sublime.load_settings("LuaFormatter.sublime-settings")
            if config.get("auto_format_on_save", False):
                view.run_command("lua_format")
