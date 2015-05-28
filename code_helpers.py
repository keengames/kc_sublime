import sublime, sublime_plugin, re

def gotoFunctionBody( view, edit, headLine ):
	line = headLine
	for x in range( 0, 10 ):
		line = view.line( line.end() + 1 )
		line_str = view.substr( line )
		brace_pos = line_str.find( '{' )
		if brace_pos >= 0:
			if view.size() == line.end():
				view.insert( edit, line.end(), "\n" )
			return view.line( line.end() + 1 ), line_str[ :brace_pos ]
	return False, False

class KeenUseArgumentCommand( sublime_plugin.TextCommand ):
	def run( self, edit ):
		for region in self.view.sel():
			line = self.view.line( region )
			line_str = self.view.substr( line )
			params = re.findall( "[*\s](\w+)(\[\])?\s*[),/]", line_str )
			line, ident_str = gotoFunctionBody( self.view, edit, line )
			if line != False:
				for param in reversed( params ):
					self.view.insert( edit, line.begin(), ident_str + "	KEEN_USE_ARGUMENT( " + param[ 0 ] + " );\n" )

class KeenAssertNullptrCommand( sublime_plugin.TextCommand ):
	def run( self, edit ):
		for region in self.view.sel():
			line = self.view.line( region )
			line_str = self.view.substr( line )
			params = re.findall( "\*\s*(p[A-Z]\w*)(\[\])?\s*[),/]", line_str )

			line, ident_str = gotoFunctionBody( self.view, edit, line )
			if line != False:
				for param in reversed( params ):
					self.view.insert( edit, line.begin(), ident_str + "	KEEN_ASSERTE( " + param[ 0 ] + " != nullptr );\n" )

class PasteCstringCommand( sublime_plugin.TextCommand ):
	def run( self, edit ):
		for region in self.view.sel():
			c_string = sublime.get_clipboard().replace( '\\', '\\\\' ).replace( '"', '\\"' ).replace( chr( 13 ), '' ).replace( chr( 10 ), '"\n"' )
			self.view.insert( edit, region.begin(), '"' + c_string + '"' )
