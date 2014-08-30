#!/usr/bin/env python3
# coding=utf8
# @author: Matthäus G. Chajdas
# @license: 2-clause BSD

from lina import *
import pytest

class MemoryTemplateRepository(TemplateRepository):
    def __init__(self):
        pass

    def Get(self, name):
        if name == 'item':
            return Template ('{{item}}')
        elif name == 'block':
            return Template ('{{#block}}{{.}}{{/block}}')
        elif name == 'text':
            return Template ('text')

def testReplaceVariable():
    template = Template ('{{test}}')
    result = template.RenderSimple(test='value')
    assert ('value' == result)

def testExpandDictionary():
    template = Template('{{#block}}{{test}}{{/block}}')
    result=template.RenderSimple(block={'test':'value'})
    assert ('value' == result)

def testExpandList():
    template = Template('{{#block}}{{.}}{{/block}}')
    result=template.RenderSimple(block=[1,2,3])
    assert ('123' == result)

def testExpandSet():
    template = Template('{{#block}}{{.}}{{/block}}')
    result = template.RenderSimple(block = {1, 2, 3})
    assert ('123' == result)

def testGlobalVariableGetsFound():
    template = Template ('{{#B}}{{test}}{{/B}}')
    result=template.RenderSimple(test='value', B=None)
    assert ('value' == result)

def testParentBlockVariableGetsFound():
    template = Template ('{{#A}}{{#B}}{{test}}{{/B}}{{/A}}')
    result=template.RenderSimple(A={'test':'value', 'B':None})
    assert ('value' == result)

def testReplaceBlockEmpty():
    template = Template('This is a {{#block}}test{{/block}}')
    result=template.RenderSimple(block=None)
    assert ('This is a test' == result)

def testReplaceBlockTwice():
    template = Template('This is a {{#block}}{{test}}{{/block}}')
    result=template.RenderSimple(block=[{'test':'sec'}, {'test':'ond'}])
    assert ('This is a second' == result)

def testReplaceBlockVariable():
    template = Template('Foo {{#block}}{{var1}}{{/block}}{{var2}}')
    result=template.RenderSimple(block={'var1':'1'},var2='2')
    assert ('Foo 12' == result)

def testReplaceBlockGetsEmptyIfUndefined():
    template = Template ('This is the end{{#block}}foo{{/block}}')
    result=template.RenderSimple()
    assert ('This is the end' == result)

def testReplaceBlockStartIsDefined():
    template = Template ('This is the {{#block}}{{#block#First}}first{{/block#First}}{{test}}{{/block}}')
    result=template.RenderSimple(block=[{'test':'2'},{'test':'3'}])
    assert ('This is the first23' == result)

def testReplaceBlockSeparatorIsDefined():
    template = Template ('{{#block}}{{item}}{{#block#Separator}}, {{/block#Separator}}{{/block}}')
    result=template.RenderSimple(block=[{'item':'0'},{'item':'1'}])
    assert ('0, 1' == result)

def testReplaceBlockEndIsDefined():
    template = Template ('{{#block}}{{item}}{{#block#Last}}last{{/block#Last}}{{/block}}')
    result=template.RenderSimple(block=[{'item':'0'},{'item':'1'}])
    assert ('01last' == result)

def testExpandWidthNegativeIsLeftAlign():
    template = Template ('{{item:width=-4}}')
    result=template.RenderSimple(item=42)
    assert ('  42' == result)

def testExpandWidthPositiveIsRightAlign():
    template = Template ('{{item:width=4}}')
    result=template.RenderSimple(item=42)
    assert ('42  ' == result)

def testExpandDefaultFormatterWorks():
    template = Template ('{{item:default=def}}')
    result=template.RenderSimple(item=None)
    assert ('def' == result)

def testExpandDefaultFormatterDoesNotReplaceIfSet():
    template = Template ('{{item:default=def}}')
    result=template.RenderSimple(item='bla')
    assert ('bla' == result)

def testSeparator():
    template = Template('{{#block:list-separator=, }}{{item}}{{/block}}')
    result=template.RenderSimple(block=[{'item' : '0'}, {'item' : '1'}])
    assert ('0, 1' == result)

def testSeparatorIsNotAddedOnSingleItem():
    template = Template('{{#block:list-separator=, }}{{item}}{{/block}}')
    result=template.RenderSimple(block=[{'item' : '0'}])
    assert ('0' == result)

def testExpandCompundItem():
    template = Template('{{item.key}}')
    result=template.RenderSimple(item = {'key':'value'})
    assert ('value' == result)

def testExpandListSeparatorSingleItemSimpleList():
    template = Template('{{#block:list-separator=, }}{{.}}{{/block}}')
    result=template.RenderSimple(block=[0])
    assert ('0' == result)

def testExpandListSeparatorShortAlias():
    template = Template('{{#block:l-s=, }}{{item}}{{/block}}')
    result=template.RenderSimple(block=[{'item' : '0'}, {'item' : '1'}])
    assert ('0, 1' == result)

def testExpandListSeparatorNewline():
    template = Template('{{#block:l-s=NEWLINE}}{{item}}{{/block}}')
    result=template.RenderSimple(block=[{'item' : '0'}, {'item' : '1'}])
    assert ('0\n1' == result)

def testExpandListSeparatorSpace():
    template = Template('{{#block:l-s=SPACE}}{{item}}{{/block}}')
    result=template.RenderSimple(block=[{'item' : '0'}, {'item' : '1'}])
    assert ('0 1' == result)

def testExpandPrefixAfterWidth():
    template = Template('{{item:width=-4:prefix=a}}')
    result=template.RenderSimple(item='b')
    assert ('a   b' == result)

def testExpandPrefixBeforeWidth():
    template = Template('{{item:prefix=a:width=-4}}')
    result=template.RenderSimple(item='b')
    assert ('  ab' == result)

def testIndentBlock():
    template = Template('{{#block:l-s=NEWLINE:indent=2}}{{item}}{{/block}}')
    result=template.RenderSimple(block=[{'item' : '0'}, {'item' : '1'}])
    assert ('\t\t0\n\t\t1' == result)

def testExpandWhitespaceSpace():
    template = Template('{{_SPACE}}')
    result=template.RenderSimple()
    assert (' ' == result)

def testExpandWhitespaceNewline():
    template = Template('{{_NEWLINE}}')
    result=template.RenderSimple()
    assert ('\n' == result)

def testInvalidFormatterRaisesException():
    template = Template ('{{test:foo}}')
    with pytest.raises (InvalidFormatter):
        template.RenderSimple (test='test')

def testInvalidTokenWithoutEndRaisesException():
    template = Template ('{{test')
    with pytest.raises (InvalidToken):
        template.RenderSimple()

def testInvalidTokenLocationAfterNewlineException():
    template = Template ('\n{{test')
    with pytest.raises (InvalidToken) as excinfo:
        template.RenderSimple()
    assert (excinfo.value.GetPosition ().line == 2)
    assert (excinfo.value.GetPosition ().column == 1)

def testInvalidTokenWithSingleBraceAtEndRaisesException():
    template = Template ('{{test}')
    with pytest.raises (InvalidToken):
        template.RenderSimple()

def testInvalidWhitespaceTokenRaisesException():
    template = Template ('{{_NEWLINES}}')
    with pytest.raises (InvalidWhitespaceToken):
        template.RenderSimple()

def testUppercaseTransformation():
    template = Template('{{item:upper-case}}')
    result=template.RenderSimple(item='baD')
    assert ('BAD' == result)

def testExpandSingleItemAsBlock():
    template = Template('{{#item}}This is {{.}}{{/item}}')
    result = template.RenderSimple(item='value')
    assert ('This is value' == result)

def testExpandSingleItemAsBlockIsSkippedIfNotSet():
    template = Template('{{#item}}This is {{.}}{{/item}}')
    result = template.RenderSimple()
    assert ('' == result)

def testExpandNestedRepeatedBlock ():
    template = Template ('{{#block}}{{#block}}{{item}}{{/block}}{{/block}}')
    result = template.RenderSimple (block = [{'item':0},{'item':1}])
    assert ('0101' == result)

def testExpandNestedRepeatedBlockTwoLevelsDeep ():
    template = Template ('{{#block}}{{#block}}{{#block}}{{item}}{{/block}}{{/block}}{{/block}}')
    result = template.RenderSimple (block = [{'item':0},{'item':1}])
    assert ('01010101' == result)

def testExpandSingleItemCompound ():
    template = Template('{{#item}}This is {{.field}}{{/item}}')
    result = template.RenderSimple(item={'field':'value'})
    assert ('This is value' == result)

def testExpandItemCompound ():
    template = Template('{{#items}}This is {{item.field}}{{/items}}')
    class Item:
        def __init__ (self, field):
            self.field = field
    result = template.RenderSimple(items=[{'item':Item ('value')}])
    assert ('This is value' == result)

def testExpandDictionaryCompound ():
    template = Template('{{#items}}This is {{item.field}}{{/items}}')
    result = template.RenderSimple(items=[{'item': {'field':'value'}}])
    assert ('This is value' == result)

def testExpandCompoundThrowsIfNoSuchFieldNone ():
    template = Template('{{#items}}This is {{item.field}}{{/items}}')
    with pytest.raises (TemplateException):
        result = template.RenderSimple(items=[{'item':None}])

def testExpandCompoundThrowsIfNoSuchFieldEmptyDict ():
    template = Template('{{#items}}This is {{item.field}}{{/items}}')
    with pytest.raises (TemplateException):
        result = template.RenderSimple(items=[{'item':{}}])

def testFormatAsHex ():
    template = Template('{{item:hex}}')
    result = template.RenderSimple(item=127)
    assert ('0x7F' == result)

def testEscapeNewlineFormatter ():
    template = Template ('{{item:escape-newlines}}')
    result = template.RenderSimple(item='\n')
    assert ('\\n' == result)

def testWrapStringFormatter ():
    template = Template ('{{item:wrap-string}}')
    result = template.RenderSimple(item='Some string')
    assert ('"Some string"' == result)

def testWrapStringFormatterIgnoresNonStrings ():
    template = Template ('{{item:wrap-string}}')
    result = template.RenderSimple(item=256)
    assert ('256' == result)

def testCBooleanFormatter ():
    template = Template ('{{true:cbool}}, {{false:cbool}}')
    result = template.RenderSimple(true=True,false=False)
    assert ('true, false' == result)

def testCBooleanFormatterIgnoresNonBooleans ():
    template = Template ('{{item:cbool}}')
    result = template.RenderSimple(item=1)
    assert ('1' == result)

def testExpandSuffixAfterWidth():
    template = Template('{{item:width=-4:suffix=a}}')
    result=template.RenderSimple(item='b')
    assert ('   ba' == result)

def testExpandSuffixBeforeWidth():
    template = Template('{{item:suffix=a:width=-4}}')
    result=template.RenderSimple(item='b')
    assert ('  ba' == result)

def testMissingBlockEndRaisesException ():
    template = Template('{{#block}}')
    with pytest.raises (InvalidBlock):
        template.RenderSimple()

def testInvalidBlockEndRaisesException():
    template = Template('{{#block}}{{/other}}')
    with pytest.raises (InvalidBlock):
        template.RenderSimple()

def testInvalidBlockNestingRaisesException ():
    template = Template('{{#block}}{{#otherblock}}{{/block}}{{/otherblock}}')
    with pytest.raises (InvalidToken):
        template.RenderSimple()

def testMissingVariableIsReplacedWithEmptyString ():
    template = Template ('{{var}}')
    assert ('' == template.RenderSimple ())

def testIncludeItem ():
    repo = MemoryTemplateRepository ()
    template = Template ('{{>item}}', repo)
    assert ('theitem' == template.RenderSimple(item = 'theitem'))

def testIncludeBlock ():
    repo = MemoryTemplateRepository ()
    template = Template ('{{>block}}', repo)
    assert ('theitem' == template.RenderSimple(block = 'theitem'))

def testIncludeText ():
    repo = MemoryTemplateRepository ()
    template = Template ('{{>text}}', repo)
    assert ('text' == template.RenderSimple())
