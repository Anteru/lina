# coding=utf8
# @author: Matthäus G. Chajdas
# @license: 2-clause BSD

import io
import os
import logging

class TemplateException(Exception):
	def __init__(self, message, position=None):
		Exception.__init__(self, message)
		self.position = position

class InvalidFormatter(TemplateException):
	pass

class InvalidToken(TemplateException):
	pass

class InvalidWhitespaceToken(TemplateException):
	pass

class InvalidBlock(TemplateException):
	pass

class TextStream:
	'''A read-only text stream. Stores the current position.'''
	def __init__(self, text):
		self.text = text
		self.length = len(text)
		self.Reset ()

	def Reset(self):
		self.current = 0
		self.indent = 0
		self.row = 1
		self.column = 1

	def Get (self):
		result = None

		if (self.current < self.length):
			result = self.text[self.current]
			self.current += 1

			if (result == '\n'):
				self.indent = 0
				self.column = 1
				self.row += 1
			elif (result == '\t'):
				self.indent += 1

		return result

	def Substring(self, start, end):
		assert start >= 0
		assert end > start
		assert end < self.length
		return self.text [start:end]

	def GetCurrentPosition(self):
		assert self.current >= 0
		return self.current

	def GetRowColumn(self):
		assert self.row >= 1
		assert self.column >= 1
		return (self.row, self.column)

	def Skip(self, length):
		'''Skip a number of characters starting from the current position.'''
		assert length >= 0
		assert (self.current + length) < self.length, 'Skip beyond end of stream'
		self.current += length

	def Unget(self):
		'''Move one character back in the input stream.'''
		assert self.current > 0, 'Read pointer is at the beginning'
		self.current -= 1

	def Peek (self):
		'''Peek at the next character in the stream if possible.
		Returns None if the end of the stream has been reached.'''
		assert self.current >= 0
		assert self.length >= 0
		if (self.current < self.length):
			return self.text[self.current]
		else:
			return None

	def IsAtEnd(self):
		'''Check if the end of the stream has been reached.'''
		assert self.current >= 0
		assert self.length >= 0
		return self.current >= self.length

class Formatter:
	'''Base class for all formatters. A formatter can be used to transform
	blocks/values during expansion.'''
	def __init__(self, formatterType):
		assert formatterType != None, 'Type must be set for Formatter'
		assert formatterType == 'block' or formatterType == 'value'
		self.type = formatterType

	def IsValueFormatter(self):
		return self.type == 'value'

	def IsBlockFormatter(self):
		return self.type == 'block'

	def Format (self, text):
		'''Format a value or a complete block.'''
		return text

	def OnBlockBegin(self, outputStream, isFirst):
		'''Called before a block is expanded.'''
		assert self.type == 'block'
		pass

	def OnBlockEnd(self, outputStream, isLast):
		'''Called after a block has been expanded.'''
		assert self.type == 'block'
		pass

class IndentFormatter(Formatter):
	'''Indent a block using tabs.'''
	def __init__(self, depth):
		Formatter.__init__(self, 'block')
		self.depth = depth
		self.tabs = '\t' * depth

	def OnBlockBegin(self, outputStream, isFirst):
		outputStream.write (self.tabs)

	def Format(self, block):
		return block.replace ('\n', '\n' + self.tabs)

class ListSeparatorFormatter(Formatter):
	'''Separate block entries.'''
	def __init__(self, value):
		Formatter.__init__(self, 'block')
		value = value.replace ('NEWLINE', '\n')
		value = value.replace ('SPACE', ' ')
		self.value = value

	def OnBlockEnd(self, outputStream, isLast):
		if (not isLast):
			outputStream.write (self.value)

class WidthFormatter(Formatter):
	'''Align the value to a particular width. Negative values
	align to the left '  42', positive values to the right '42  '.'''
	def __init__(self, width):
		Formatter.__init__(self, 'value')
		self.width = str(width) if width >= 0 else '>' + str(-width)

	def Format(self, text):
		return str.format ("{0:" + self.width + "}", str(text))

class PrefixFormatter(Formatter):
	'''Add a prefix to a value.'''
	def __init__(self, prefix):
		Formatter.__init__(self, 'value')
		self.prefix = prefix

	def Format(self, text):
		return self.prefix + str (text)

class SuffixFormatter(Formatter):
	'''Add a suffix to a value.'''
	def __init__(self, suffix):
		Formatter.__init__(self, 'value')
		self.suffix = suffix

	def Format(self, text):
		return str (text) + self.suffix

class DefaultFormatter(Formatter):
	'''Emit the default if the value is None, otherwise the value itself.'''
	def __init__(self, value):
		Formatter.__init__(self, 'value')
		self.value = value

	def Format(self, text):
		if text is None:
			return self.value
		else:
			return text

class UppercaseFormatter(Formatter):
	'''Format a value as uppercase.'''
	def __init__(self):
		Formatter.__init__(self, 'value')

	def Format(self, text):
		return str (text).upper ()

class EscapeNewlineFormatter(Formatter):
	'''Escape embedded newlines.'''
	def __init__(self):
		Formatter.__init__(self, 'value')

	def Format(self, text):
		return str (text).replace ('\n', '\\n')

class WrapStringFormatter(Formatter):
	'''Wrap strings with quotation marks.'''
	def __init__(self):
		Formatter.__init__(self, 'value')

	def Format(self, text):
		if isinstance (text, str):
			return '"{}"'.format (text)
		else:
			return text

class CBooleanFormatter(Formatter):
	'''For booleans, write true or false to the output. Otherwise,
	the input is just passed through.'''
	def __init__(self):
		Formatter.__init__(self, 'value')

	def Format(self, value):
		if isinstance (value, bool):
			return 'true' if value else 'false'
		else:
			return value

class HexFormatter(Formatter):
	'''Write an integer as a hex literal (0x133F).'''
	def __init__(self):
		Formatter.__init__(self, 'value')

	def Format(self, value):
		# Format as 0xUPPERCASE
		result = hex(value)
		result = '0x' + result [2:].upper ()
		return result

def GetFormatter (name, value = None):
	'''Get a formatter. If the formatter cannot be found, an exception is raised.'''
	if name == 'width' or name == 'w':
		return WidthFormatter (int (value))
	elif name == 'prefix':
		return PrefixFormatter (value)
	elif name == 'suffix':
		return SuffixFormatter (value)
	elif name == 'list-separator' or name == 'l-s' or name == 'separator':
		return ListSeparatorFormatter(value)
	elif name == 'indent':
		return IndentFormatter(int (value))
	elif name == 'upper-case' or name == 'uc':
		return UppercaseFormatter ()
	elif name == 'default':
		return DefaultFormatter (value)
	elif name == 'wrap-string':
		return WrapStringFormatter ()
	elif name == 'cbool':
		return CBooleanFormatter ()
	elif name == 'escape-newlines':
		return EscapeNewlineFormatter ()
	elif name == 'hex':
		return HexFormatter ()
	else:
		raise InvalidFormatter("Invalid formatter '{0}'".format (name))

class Token:
	'''Represents a single token.
	Each token may contain an optional list of flags, separated by :. The
	grammar implemented here is:
		[prefix]?[^:}]+(:[^:})+, for example:
		{{#Foo}} -> name = Foo, prefix = #
		{{Bar:width=8}} -> name = Bar, prefix = None,
							flags = {width:8}
	'''

	__validPrefixes = {'#', '/', '_', '>'}

	def __init__(self, name, start, end):
		for prefix in self.__validPrefixes:
			if (name.startswith(prefix)):
				self.prefix = prefix
				self.name = name [len(prefix):]
				break
		else:
			self.name = name
			self.prefix = None

		self.start = start
		self.end = end

		separator = self.name.find(':')

		self.formatters = list ()

		if (separator > 0):
			tmp = self.name
			self.name = tmp[:separator]
			flags = tmp[separator+1:].split(':')

			for flag in flags:
				(key, value) = (None, None)
				if (flag.find ('=') != -1):
					(key, value) = flag.split('=')
				else:
					(key, value) = (flag, None)

				self.formatters.append (GetFormatter (key, value))

	def GetName(self):
		return self.name

	def GetStart(self):
		return self.start

	def GetEnd(self):
		return self.end

	def GetFormatters(self):
		return self.formatters

	def IsBlockStart (self):
		return self.prefix == '#'

	def IsBlockClose (self):
		return self.prefix == '/'

	def IsWhiteSpaceToken (self):
		return self.prefix == '_'

	def IsIncludeToken (self):
		return self.prefix == '>'

	def IsSelfReference (self):
		return self.name[0] == '.'

	def EvaluateWhiteSpaceToken (self):
		if (self.name == 'NEWLINE'):
			return '\n'
		elif (self.name == 'SPACE'):
			return ' '
		else:
			raise InvalidWhitespaceToken ("Unrecognized white-space token '{}'".format (self.name))

	def IsValue (self):
		return self.prefix == None and self.name != '.'

class Template:
	def __init__(self, template, includeResolver=None):
		"""includeResolver is used to support nested templates. It must support
		a single function, Get(templateName) which returns a new Template
		instance. See also TemplateRepository()."""
		self.input = TextStream (template)
		self.resolver = includeResolver
		self.log = logging.getLogger('Miranda.Template')

	def __ExpandVariable(self, outputStream, token, itemStack):
		self.log.debug("Expanding variable '{}'".format(token.GetName()))
		assert token != None
		assert itemStack != None
		assert len(itemStack) > 0

		name = token.GetName ()
		value = None

		# a.b notation. We search for 'a', and then
		# we access using the rest of the path
		compound = None
		# If name starts with ., we have to separate it out
		if token.IsSelfReference ():
			if (len (name)) > 1:
				compound = name.split('.')
			name = '.'
		elif '.' in name:
			compound = name.split ('.')
			name = compound[0]

		for i in reversed(itemStack):
			assert i != None
			if name in i:
				value = i [name]

				if compound is not None:
					for component in compound[1:]:
						value = value [component]
				break
		else:
			return

		for formatter in token.GetFormatters():
			if formatter.IsValueFormatter():
				value = formatter.Format (value)

		if value is not None:
			value = str (value)

		if value == None:
			self.log.warn ("None/Null value found for variable '{}' after all formatters have run".format (token.GetName ()))
			return

		outputStream.write (value)

	def __ExpandBlock(self, inputStream, outputStream,
					  start, end, itemStack):
		def IsPrimitiveType(e):
			return isinstance(e, str) or isinstance (e, int) or \
				isinstance (e, float) or isinstance (e, bool)

		self.log.debug("Expanding block '{}'".format(start.GetName()))
		assert start.GetName () == end.GetName ()
		assert start.IsBlockStart ()
		assert end.IsBlockClose ()

		blockName = start.GetName ()

		assert (itemStack != None)
		assert len (itemStack) > 0
		assert itemStack [-1] != None

		# Must be present somewhere along the stack
		# Search up in case we have the same block nested
		blockItems = None
		for items in itemStack:
			if blockName in items:
				blockItems = items [blockName]
				break
		else:
			return

		blockContent = inputStream.Substring(start.GetEnd (), end.GetStart ())

		instanceCount = 0
		# deal with various dictionary types
		# Blocks are expanded by iterating over all entries. Wrap dictionaries,
		# empty items and primitive types into lists so we can iterate over them
		# name=dict => name = [dict]
		# name=None => name = [{}]
		# otherwise, just copy
		if (blockItems == None):
			instanceCount = 1
			blockItems = [{}]
		elif isinstance(blockItems, dict):
			blockItems = [blockItems]
			instanceCount = 1
		elif isinstance (blockItems, set):
			# Treat a set as a list
			blockItems = list (blockItems)
			instanceCount = len (blockItems)
		elif IsPrimitiveType (blockItems):
			# Plain objects are wrapped to support self-references
			instanceCount = 1
			blockItems = [blockItems]
		else:
			instanceCount = len (blockItems)

		for i in range(instanceCount):
			# Current entry
			current = dict ()

			# Add a self-reference
			# For simple types, wrap it into a dictionary, otherwise, just add
			# a self-reference to the already existing dictionary
			if not isinstance(blockItems [i], dict):
				current = {'.' : blockItems [i]}
			else:
				current = blockItems [i]
				current ['.'] = blockItems [i]

			isFirst = (i == 0)
			isLast = ((i+1) == instanceCount)

			if (i == 0):
				current [blockName + "#First"] = None
			if ((i+1) < instanceCount):
				current [blockName + "#Separator"] = None
			if ((i+1) == instanceCount):
				current [blockName + "#Last"] = None

			hasBlockFormatter = False
			for formatter in start.GetFormatters():
				if formatter.IsBlockFormatter():
					hasBlockFormatter = True
					formatter.OnBlockBegin (outputStream, isFirst)

			itemStack.append (current)
			if hasBlockFormatter:
				# Write the string to a temporary stream if a block formatter is
				# present
				tmpStream = io.StringIO()

				self.__Render(TextStream (blockContent), tmpStream, itemStack)

				tmpString = tmpStream.getvalue()

				for formatter in start.GetFormatters():
					if formatter.IsBlockFormatter():
						tmpString = formatter.Format (tmpString)
				outputStream.write (tmpString)
			else:
				# Directly render into output stream for maximum performance
				self.__Render(TextStream (blockContent), outputStream, itemStack)

			itemStack.pop ()

			if hasBlockFormatter:
				for formatter in start.GetFormatters():
					if formatter.IsBlockFormatter():
						formatter.OnBlockEnd (outputStream, isLast)

	def __ReadToken(self, inputStream):
		"""Read a single token from the stream."""
		token = ''
		start = inputStream.GetCurrentPosition ()
		# Token starts with {{
		inputStream.Skip(2)
		while True:
			c = inputStream.Get()
			if (c == None):
				raise InvalidToken ('End-of-file reached while reading token',
					inputStream.GetRowColumn ())
			elif (c != '}'):
				token += c
			else:
				if inputStream.Peek () == '}':
					inputStream.Get ()
					end = inputStream.GetCurrentPosition ()
					return Token(token, start, end)
				else:
					raise InvalidToken("Token '{}' incorrectly delimited".format (token),
						inputStream.GetRowColumn ())

	def __FindBlockEnd (self, inputStream, blockname):
		'''Find the block end for a block named blockname in a stream, starting
		from the current position.'''

		nestedStack = []
		while not inputStream.IsAtEnd ():
			current = inputStream.Get()

			if (current == '{' and inputStream.Peek() == '{'):
				inputStream.Unget()
				token = self.__ReadToken (inputStream)

				if (token.IsBlockStart ()):
					nestedStack.append (token.GetName ())

				if (token.IsBlockClose ()):
					if len(nestedStack) > 0:
						if token.GetName () != nestedStack.pop ():
							raise InvalidToken (
								"Invalid block nesting for block '{}'".format (token.GetName ()),
								inputStream.GetRowColumn())
					elif token.GetName () == blockname:
						return token
					else:
						break
		raise InvalidBlock ("Could not find block end for '{}'".format (blockname))

	def __ExpandInclude (self, outputStream, token, itemStack):
		self.log.debug("Expanding include statement: '{}'".format(token.GetName()))
		assert self.resolver is not None, "Cannot resolve includes without an include resolver"
		template = self.resolver.Get (token.GetName ())
		template.__RenderTo (outputStream, itemStack)

	def __Render(self, inputStream, outputStream, itemStack):
		while not inputStream.IsAtEnd ():
			current = inputStream.Get()

			if (current == '{' and inputStream.Peek() == '{'):
				inputStream.Unget()
				token = self.__ReadToken (inputStream)

				if (token.IsValue() or token.IsSelfReference ()):
					self.__ExpandVariable(outputStream, token, itemStack)
				elif (token.IsBlockStart ()):
					blockEnd = self.__FindBlockEnd(inputStream, token.GetName ())
					self.__ExpandBlock(inputStream, outputStream,
									   token, blockEnd, itemStack)
				elif (token.IsWhiteSpaceToken()):
					outputStream.write (token.EvaluateWhiteSpaceToken())
				elif (token.IsIncludeToken ()):
					self.__ExpandInclude (outputStream, token, itemStack)
			else:
				# pass through to output
				outputStream.write(current)

	def __RenderTo (self, outputStream, itemStack):
		self.__Render (self.input, outputStream, itemStack)

	def Render(self, dictionary):
		itemStack = [dictionary]

		output = io.StringIO ()
		self.__Render(self.input, output, itemStack)
		self.input.Reset ()
		return output.getvalue ()

	def RenderSimple(self, **items):
		'''Simpler rendering function. Build the dictionary from the parameter list.
		This is just a convenience function which calls Render(self, dict).'''
		return self.Render (items)

class TemplateRepository:
	def __init__(self, templateDirectory, suffix = ''):
		self.dir = templateDirectory
		self.suffix = suffix

	def Get(self, name):
		content = open(os.path.join(self.dir, name + self.suffix)).read ()
		return Template (content, self)