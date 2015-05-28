import sublime, sublime_plugin, re

class KeenUseArgumentCommand(sublime_plugin.TextCommand):
	def run(self, edit):        
		for region in self.view.sel():
			line = self.view.line(region)
			line_str = self.view.substr(line)
			params = re.findall( "[*\s](\w+)(\[\])?\s*[),/]", line_str )

			line = self.view.line(line.end() + 1 )
			maxCount = 10
			while 1:
				line_str = self.view.substr(line)
				brace_pos = line_str.index( '{' )
				if brace_pos >= 0:
					content_ident = line_str[:brace_pos]
					break
				maxCount -= 1
				if maxCount == 0:
					break
			if maxCount > 0:
				line = self.view.line(line.end() + 1 )
				for param in params:
					self.view.insert(edit, line.begin(), content_ident + "	KEEN_USE_ARGUMENT( " + param[ 0 ] + " );\n" )
