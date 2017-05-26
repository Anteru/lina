# coding=utf8
# @author: Matthäus G. Chajdas
# @license: 2-clause BSD

__version__ = '1.0.5'

import io
import os
import logging
import collections.abc
from enum import Enum, unique

class TemplateException(Exception):
	'''Base class for all exceptions thrown by Lina.'''
	def __init__(self, message, position):
		Exception.__init__(self, message)
		self._position = position

	def GetPosition (self):
		'''Get the position where the exception occurred.

		:returns: An object with two fields, ``line`` and ``column``.'''
		from collections import namedtuple
		p = namedtuple ('position', ['line', 'column'])
		return p (self._position [0], self._position [1])

class InvalidFormatter(TemplateException):
	'''An invalid formatter was encountered.

	This exception is raised when a formatter could not be found or instantiated.'''
	pass

class InvalidToken(TemplateException):
	'''An invalid token was encountered.'''
	pass

class InvalidWhitespaceToken(TemplateException):
	'''An invalid whitespace token was encountered.'''
	pass

class InvalidBlock(TemplateException):
	'''An invalid block was encountered.'''
	pass

class TextStream:
	'''A read-only text stream.

	The text stream is used for input only and keeps track of the current read
	pointer position in terms of line/column numbers.'''
	def __init__(self, text):
		self._text = text
		self._length = len (text)
		self.Reset ()

	def Reset(self):
		'''Reset back to the beginning of the stream.'''
		self._offset = 0
		self._line = 1
		self._column = 1

	def Get (self):
		'''Get a character.

		If the end of the stream has been reached, ``None`` is returned.'''
		result = None

		if self._offset < self._length:
			result = self._text[self._offset]
			self._offset += 1

			if result == '\n':
				self.indent = 0
				self._column = 1
				self._line += 1

		return result

	def Substring(self, start, end):
		'''Get a substring of the stream.'''
		assert start >= 0
		assert end > start
		assert end < self._length
		return self._text [start:end]

	def GetOffset(self):
		'''Get the current read offset in characters from the beginning of the stream.'''
		assert self._offset >= 0
		return self._offset

	def GetPosition (self):
		'''Get the current read position as a pair (line, column).'''
		assert self._line >= 1
		assert self._column >= 1
		return (self._line, self._column)

	def Skip(self, length):
		'''Skip a number of characters starting from the current position.'''
		assert length >= 0
		assert (self._offset + length) < self._length, 'Skip beyond end of stream'
		self._offset += length

	def Unget(self):
		'''Move one character back in the input stream.'''
		assert self._offset > 0, 'Read pointer is at the beginning'
		self._offset -= 1

	def Peek (self):
		'''Peek at the next character in the stream if possible.
		Returns None if the end of the stream has been reached.'''
		assert self._offset >= 0
		assert self._length >= 0
		if (self._offset < self._length):
			return self._text[self._offset]
		else:
			return None

	def IsAtEnd(self):
		'''Check if the end of the stream has been reached.'''
		assert self._offset >= 0
		assert self._length >= 0
		return self._offset >= self._length

@unique
class FormatterType(Enum):
	'''The formatter type, either ``Block`` or ``Value``.'''
	Block = 0
	Value = 1

class Formatter:
	'''Base class for all formatters.

	A formatter can be used to transform blocks/values during expansion.'''

	def __init__(self, formatterType):
		assert formatterType != None, 'Type must be set for Formatter'
		assert isinstance(formatterType, FormatterType)
		self.__type = formatterType

	def IsValueFormatter(self):
		'''Check if this formatter is a value formatter.'''
		return self.__type == FormatterType.Value

	def IsBlockFormatter(self):
		'''Check if this formatter is a block formatter.'''
		return self.__type == FormatterType.Block

	def Format (self, text):
		'''Format a value or a complete block.'''
		return text

	def OnBlockBegin(self, isFirst):
		'''Called before a block is expanded.

		:param isFirst: ``True`` if this is the first expansion of the block.
		:returns: String or ``None``. If a string is returned, it is prepended
			before the current block expansion.'''
		assert self.IsBlockFormatter ()
		pass

	def OnBlockEnd(self, isLast):
		'''Called after a block has been expanded.

		:param isLast: ``True`` if this is the last expansion of the block.
		:returns: String or ``None``. If a string is returned, it is appended
			after the current block expansion.'''
		assert self.IsBlockFormatter ()
		pass

class IndentFormatter(Formatter):
	'''Indent a block using tabs.'''
	def __init__(self, depth):
		Formatter.__init__(self, FormatterType.Block)
		self._depth = depth
		self._tabs = '\t' * depth

	def OnBlockBegin(self, isFirst):
		return self._tabs

	def Format(self, block):
		return block.replace ('\n', '\n' + self._tabs)

class ListSeparatorFormatter(Formatter):
	'''Separate block entries.

	This formatter will insert a value between block expansions.'''
	def __init__(self, value):
		Formatter.__init__(self, FormatterType.Block)
		value = value.replace ('NEWLINE', '\n')
		value = value.replace ('SPACE', ' ')
		self._value = value

	def OnBlockEnd(self, isLast):
		if not isLast:
			return self._value

class WidthFormatter(Formatter):
	'''Align the value to a particular width.

	Negative values align to the left (i.e., the padding is added on the left:
	``'  42'``), positive values to the right (``'42  '``).'''
	def __init__(self, width):
		Formatter.__init__(self, FormatterType.Value)
		self._width = str(width) if width >= 0 else '>' + str(-width)

	def Format(self, text):
		return str.format ("{0:" + self._width + "}", str(text))

class PrefixFormatter(Formatter):
	'''Add a prefix to a value.'''
	def __init__(self, prefix):
		Formatter.__init__(self, FormatterType.Value)
		self._prefix = prefix

	def Format(self, text):
		return self._prefix + str (text)

class SuffixFormatter(Formatter):
	'''Add a suffix to a value.'''
	def __init__(self, suffix):
		Formatter.__init__(self, FormatterType.Value)
		self._suffix = suffix

	def Format(self, text):
		return str (text) + self._suffix

class DefaultFormatter(Formatter):
	'''Emit the default if the value is None, otherwise the value itself.'''
	def __init__(self, value):
		Formatter.__init__(self, FormatterType.Value)
		self._value = value

	def Format(self, text):
		if text is None:
			return self._value
		else:
			return text

class UppercaseFormatter(Formatter):
	'''Format a value as uppercase.'''
	def __init__(self):
		Formatter.__init__(self, FormatterType.Value)

	def Format(self, text):
		return str (text).upper ()

class EscapeNewlineFormatter(Formatter):
	'''Escape embedded newlines.'''
	def __init__(self):
		Formatter.__init__(self, FormatterType.Value)

	def Format(self, text):
		return str (text).replace ('\n', '\\n')

class EscapeStringFormatter(Formatter):
	'''Escape embedded newlines, tabs and quotes.'''
	def __init__(self):
		Formatter.__init__(self, FormatterType.Value)

	def Format(self, text):
		text = str (text).replace ('\n', '\\n')
		text = text.replace ('\t', '\\t')
		text = text.replace ('\"', '\\"')
		return text

class WrapStringFormatter(Formatter):
	'''Wrap strings with quotation marks.'''
	def __init__(self):
		Formatter.__init__(self, FormatterType.Value)

	def Format(self, text):
		if isinstance (text, str):
			return '"{}"'.format (text)
		else:
			return text

class CBooleanFormatter(Formatter):
	'''For booleans, write true or false to the output. Otherwise,
	the input is just passed through.'''
	def __init__(self):
		Formatter.__init__(self, FormatterType.Value)

	def Format(self, value):
		if isinstance (value, bool):
			return 'true' if value else 'false'
		else:
			return value

class HexFormatter(Formatter):
	'''Write an integer as a hex literal (0x133F).'''
	def __init__(self):
		Formatter.__init__(self, FormatterType.Value)

	def Format(self, value):
		# Format as 0xUPPERCASE
		result = hex(value)
		result = '0x' + result [2:].upper ()
		return result

def GetFormatter (name, value = None, position=None):
	'''Get a formatter.

	If the formatter cannot be found, an exception is raised.'''
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
	elif name == 'escape-string':
		return EscapeStringFormatter ()
	elif name == 'hex':
		return HexFormatter ()
	else:
		raise InvalidFormatter("Invalid formatter '{0}'".format (name),
			position)

class Token:
	'''Represents a single token.

	Each token may contain an optional list of flags, separated by colons. The
	grammar implemented here is::

		[prefix]?[^:}]+(:[^:})+, for example:
		{{#Foo}} -> name = Foo, prefix = #
		{{Bar:width=8}} -> name = Bar, prefix = None,
							flags = {width:8}
	'''

	__validPrefixes = {'#', '/', '_', '>', '!'}

	def __init__(self, name, start, end, position):
		for prefix in self.__validPrefixes:
			if (name.startswith(prefix)):
				self.__prefix = prefix
				self.__name = name [len(prefix):]
				break
		else:
			self.__name = name
			self.__prefix = None

		self.__start = start
		self.__end = end
		self.__position = position

		separator = self.__name.find(':')

		self.__formatters = list ()

		if (separator > 0):
			tmp = self.__name
			self.__name = tmp[:separator]
			flags = tmp[separator+1:].split(':')

			for flag in flags:
				(key, value) = (None, None)
				if (flag.find ('=') != -1):
					(key, value) = flag.split('=')
				else:
					(key, value) = (flag, None)

				self.__formatters.append (GetFormatter (key, value, position))

	def GetName(self):
		'''Get the name of this token.'''
		return self.__name

	def GetStart(self):
		'''Get the start offset.'''
		return self.__start

	def GetEnd(self):
		'''Get the end offset.'''
		return self.__end

	def GetPosition (self):
		'''Get the position as a (line, column) pair.'''
		return self.__position

	def GetFormatters(self):
		'''Get all active formatters for this token.'''
		return self.__formatters

	def IsBlockStart (self):
		'''Return true if this token is a block-start token.'''
		return self.__prefix == '#'

	def IsNegatedBlockStart (self):
		'''Return true if this token is a negated block-start token.'''
		return self.__prefix == '!'

	def IsBlockClose (self):
		'''Return true if this token is a block-close token.'''
		return self.__prefix == '/'

	def IsWhiteSpaceToken (self):
		'''Return true if this token is a whitespace directive.'''
		return self.__prefix == '_'

	def IsIncludeToken (self):
		'''Return true if this token is an include directive.'''
		return self.__prefix == '>'

	def IsSelfReference (self):
		'''Return true if this token is a self-reference.'''
		return self.__name[0] == '.'

	def EvaluateWhiteSpaceToken (self, position):
		'''Get the content of this token if this token is a whitespace token.

		If the content is not a valid whitespace name, this function will raise
		:py:class:`InvalidWhitespaceToken`.'''
		if (self.__name == 'NEWLINE'):
			return '\n'
		elif (self.__name == 'SPACE'):
			return ' '
		else:
			raise InvalidWhitespaceToken ("Unrecognized white-space token '{}'".format (self.__name),
				position)

	def IsValue (self):
		return self.__prefix == None and self.__name != '.'

class IncludeHandler:
	'''Base interface for include handlers.'''
	def Get(self, name):
		pass

class Template:
	'''The main template class.'''

	def __init__(self, template, includeHandler=None):
		'''includeHandler is used to support nested templates. It must support
		a single function, Get(templateName) which returns a new Template
		instance. See also TemplateRepository().'''
		self.__input = TextStream (template)
		self.__includeHandler = includeHandler
		self.__log = logging.getLogger('Lina.Template')

	def __ExpandVariable(self, outputStream, token, itemStack):
		'''Expand a value token.'''
		self.__log.debug("Expanding variable '{}'".format(token.GetName()))
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
						try:
							# If [number], we use it as a list index
							if component [0] == '[' and component [-1] == ']':
								index = int (component [1:-1])
								value = value [index]
							# try as a field name
							elif hasattr (value, component):
								# Field
								value = getattr (value, component)
							# try dictionary lookup
							elif component in value:
								# Dictionary lookup
								value = value [component]
							else:
								raise Exception ()
						except:
							raise TemplateException ("Cannot expand token, component '{}' is missing or invalid".format (component),
								token.GetPosition ())

				break
		else:
			# Variable not found, ignore
			return

		for formatter in token.GetFormatters():
			if formatter.IsValueFormatter():
				value = formatter.Format (value)

		if value is not None:
			value = str (value)
		else:
			self.__log.warn ("None/Null value found for variable '{}' after all formatters have run".format (token.GetName ()))
			return

		outputStream.write (value)

	def __ExpandBlock(self, inputStream, outputStream,
					  start, end, context):
		'''Expand a block.'''
		def IsPrimitiveType(e):
			return isinstance(e, str) or isinstance (e, int) or \
				isinstance (e, float) or isinstance (e, bool)

		self.__log.debug("Expanding block '{}'".format(start.GetName()))
		assert start.GetName () == end.GetName ()
		assert start.IsBlockStart () or start.IsNegatedBlockStart ()
		assert end.IsBlockClose ()

		blockName = start.GetName ()

		assert (context != None)
		assert len (context) > 0
		assert context [-1] != None

		# Must be present somewhere along the stack
		# Search up in case we have the same block nested
		blockItems = None
		for items in context:
			if blockName in items:
				blockItems = items [blockName]

				# Using name=None is an alternative way to skip a block
				# A block specified using name=None is ignored, as if it was
				# never defined
				if blockItems is None:
					if start.IsNegatedBlockStart ():
						break
					else:
						return

				if start.IsNegatedBlockStart ():
					return
				break
		else:
			if not start.IsNegatedBlockStart ():
				return

		blockContent = inputStream.Substring(start.GetEnd (), end.GetStart ())

		instanceCount = 0
		# deal with various dictionary types
		# Blocks are expanded by iterating over all entries. Wrap dictionaries,
		# empty items and primitive types into lists so we can iterate over them
		# name=dict => name = [dict]
		# name=None => name = [{}]
		# otherwise, just copy
		if blockItems is None:
			blockItems = [{}]
			instanceCount = 1
		elif isinstance(blockItems, collections.abc.Mapping):
			blockItems = [blockItems]
			instanceCount = 1
		elif isinstance (blockItems, collections.abc.Set):
			# Treat a set as a list
			blockItems = list (blockItems)
			instanceCount = len (blockItems)
		elif IsPrimitiveType (blockItems):
			# Plain objects are wrapped to support self-references
			# cannot use isinstance (Sequence) here as we don't want to treat
			# str as a list
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
				current [blockName + "#First"] = {}
			if ((i+1) < instanceCount):
				current [blockName + "#Separator"] = {}
			if ((i+1) == instanceCount):
				current [blockName + "#Last"] = {}

			hasBlockFormatter = False
			for formatter in [f for f in start.GetFormatters() if f.IsBlockFormatter()]:
				hasBlockFormatter = True
				blockFormatterPrefix = formatter.OnBlockBegin (isFirst)
				if blockFormatterPrefix:
					outputStream.write (blockFormatterPrefix)

			context.append (current)
			if hasBlockFormatter:
				# Write the string to a temporary stream if a block formatter is
				# present
				tmpStream = io.StringIO()

				self.__Render(TextStream (blockContent), tmpStream, context)

				tmpString = tmpStream.getvalue()

				for formatter in start.GetFormatters():
					if formatter.IsBlockFormatter():
						tmpString = formatter.Format (tmpString)
				outputStream.write (tmpString)
			else:
				# Directly render into output stream for maximum performance
				self.__Render(TextStream (blockContent), outputStream, context)

			context.pop ()

			if hasBlockFormatter:
				for formatter in [f for f  in start.GetFormatters() if f.IsBlockFormatter()]:
					blockFormatterSuffix = formatter.OnBlockEnd (isLast)
					if blockFormatterSuffix:
						outputStream.write (blockFormatterSuffix)

	def __ReadToken(self, inputStream):
		'''Read a single token from the stream.'''
		token = ''
		start = inputStream.GetOffset ()
		startPosition = inputStream.GetPosition  ()
		# Token starts with {{
		inputStream.Skip(2)
		while True:
			c = inputStream.Get()
			if (c == None):
				raise InvalidToken ('End-of-file reached while reading token',
					inputStream.GetPosition  ())
			elif (c != '}'):
				token += c
			else:
				if inputStream.Peek () == '}':
					inputStream.Get ()
					end = inputStream.GetOffset ()
					return Token(token, start, end, startPosition)
				else:
					raise InvalidToken("Token '{}' incorrectly delimited".format (token),
						inputStream.GetPosition  ())

	def __FindBlockEnd (self, inputStream, blockname):
		'''Find the block end for a block named blockname in a stream, starting
		from the current position.'''

		nestedStack = []
		while not inputStream.IsAtEnd ():
			current = inputStream.Get()

			if current == '{' and inputStream.Peek() == '{':
				inputStream.Unget()
				token = self.__ReadToken (inputStream)

				if token.IsBlockStart () or token.IsNegatedBlockStart ():
					nestedStack.append (token.GetName ())

				if token.IsBlockClose ():
					if len(nestedStack) > 0:
						if token.GetName () != nestedStack.pop ():
							raise InvalidToken (
								"Invalid block nesting for block '{}'".format (token.GetName ()),
								inputStream.GetPosition ())
					elif token.GetName () == blockname:
						return token
					else:
						break
		raise InvalidBlock ("Could not find block end for '{}'".format (blockname),
			inputStream.GetPosition  ())

	def __ExpandInclude (self, outputStream, token, itemStack):
		'''Expand an include directive.'''
		self.__log.debug("Expanding include statement: '{}'".format(token.GetName()))
		assert self.__includeHandler is not None, "Cannot resolve includes without an include handler"
		template = self.__includeHandler.Get (token.GetName ())
		template.__RenderTo (outputStream, itemStack)

	def __Render(self, inputStream, outputStream, itemStack):
		while not inputStream.IsAtEnd ():
			current = inputStream.Get()

			if current == '{' and inputStream.Peek() == '{':
				inputStream.Unget()
				token = self.__ReadToken (inputStream)

				if token.IsValue() or token.IsSelfReference ():
					self.__ExpandVariable(outputStream, token, itemStack)
				elif token.IsBlockStart () or token.IsNegatedBlockStart ():
					blockEnd = self.__FindBlockEnd(inputStream, token.GetName ())
					self.__ExpandBlock(inputStream, outputStream,
									   token, blockEnd, itemStack)
				elif token.IsWhiteSpaceToken():
					outputStream.write (token.EvaluateWhiteSpaceToken(inputStream.GetPosition  ()))
				elif token.IsIncludeToken ():
					self.__ExpandInclude (outputStream, token, itemStack)
			else:
				# pass through to output
				outputStream.write(current)

	def __RenderTo (self, outputStream, itemStack):
		self.__Render (self.__input, outputStream, itemStack)

	def Render(self, context):
		'''Render the template using the provided context.'''
		context = [context]

		output = io.StringIO ()
		self.__Render(self.__input, output, context)
		self.__input.Reset ()
		return output.getvalue ()

	def RenderSimple(self, **items):
		'''Simple rendering function.

		This is just a convenience function which creates the context from the passed
		items and forwards them to :py:meth:`Template.Render`.'''
		return self.Render (items)

class TemplateRepository (IncludeHandler):
	'''A file template repository.

	This template repository will load files from a specified folder.'''
	def __init__(self, templateDirectory, suffix = ''):
		self.dir = templateDirectory
		self.suffix = suffix

	def Get(self, name):
		content = open(os.path.join(self.dir, name + self.suffix)).read ()
		return Template (content, self)
