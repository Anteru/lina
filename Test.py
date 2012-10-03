# coding=utf8
# @author: Matthäus G. Chajdas
# @license: 3-clause BSD

import unittest, Template

class Test(unittest.TestCase):
    def testReplaceVariable(self):
        template = Template.Template ('{{test}}')
        result = template.RenderSimple(test='value')
        self.assertEqual(result, 'value')

    def testExpandDictionary(self):
        template = Template.Template('{{#block}}{{test}}{{/block}}')
        result=template.RenderSimple(block={'test':'value'})
        self.assertEqual('value', result)

    def testExpandList(self):
        template = Template.Template('{{#block}}{{.}}{{/block}}')
        result=template.RenderSimple(block=[1,2,3])
        self.assertEqual('123', result)

    def testExpandSet(self):
        template = Template.Template('{{#block}}{{.}}{{/block}}')
        result = template.RenderSimple(block = {1, 2, 3})
        self.assertEqual('123', result)

    def testGlobalVariableGetsFound(self):
        template = Template.Template ('{{#B}}{{test}}{{/B}}')
        result=template.RenderSimple(test='value', B=None)
        self.assertEqual('value', result)

    def testParentBlockVariableGetsFound(self):
        template = Template.Template ('{{#A}}{{#B}}{{test}}{{/B}}{{/A}}')
        result=template.RenderSimple(A={'test':'value', 'B':None})
        self.assertEqual('value', result)

    def testReplaceBlockEmpty(self):
        template = Template.Template('This is a {{#block}}test{{/block}}')
        result=template.RenderSimple(block=None)
        self.assertEqual('This is a test', result)

    def testReplaceBlockTwice(self):
        template = Template.Template('This is a {{#block}}{{test}}{{/block}}')
        result=template.RenderSimple(block=[{'test':'sec'}, {'test':'ond'}])
        self.assertEqual('This is a second', result)

    def testReplaceBlockVariable(self):
        template = Template.Template('Foo {{#block}}{{var1}}{{/block}}{{var2}}')
        result=template.RenderSimple(block={'var1':'1'},var2='2')
        self.assertEqual('Foo 12', result)

    def testReplaceBlockGetsEmptyIfUndefined(self):
        template = Template.Template ('This is the end{{#block}}foo{{/block}}')
        result=template.RenderSimple()
        self.assertEqual('This is the end', result)

    def testReplaceBlockStartIsDefined(self):
        template = Template.Template ('This is the {{#block}}{{#block#First}}first{{/block#First}}{{test}}{{/block}}')
        result=template.RenderSimple(block=[{'test':'2'},{'test':'3'}])
        self.assertEqual('This is the first23', result)

    def testReplaceBlockSeparatorIsDefined(self):
        template = Template.Template ('{{#block}}{{item}}{{#block#Separator}}, {{/block#Separator}}{{/block}}')
        result=template.RenderSimple(block=[{'item':'0'},{'item':'1'}])
        self.assertEqual('0, 1',result)

    def testReplaceBlockEndIsDefined(self):
        template = Template.Template ('{{#block}}{{item}}{{#block#Last}}last{{/block#Last}}{{/block}}')
        result=template.RenderSimple(block=[{'item':'0'},{'item':'1'}])
        self.assertEqual('01last',result)

    def testExpandWidthNegativeIsLeftAlign(self):
        template = Template.Template ('{{item:width=-4}}')
        result=template.RenderSimple(item=42)
        self.assertEqual('  42',result)

    def testExpandWidthPositiveIsRightAlign(self):
        template = Template.Template ('{{item:width=4}}')
        result=template.RenderSimple(item=42)
        self.assertEqual('42  ',result)

    def testExpandDefaultFormatterWorks(self):
        template = Template.Template ('{{item:default=def}}')
        result=template.RenderSimple(item=None)
        self.assertEqual('def', result)

    def testExpandDefaultFormatterDoesNotReplaceIfSet(self):
        template = Template.Template ('{{item:default=def}}')
        result=template.RenderSimple(item='bla')
        self.assertEqual('bla', result)

    def testSeparator(self):
        template = Template.Template('{{#block:list-separator=, }}{{item}}{{/block}}')
        result=template.RenderSimple(block=[{'item' : '0'}, {'item' : '1'}])
        self.assertEqual('0, 1', result)

    def testSeparatorIsNotAddedOnSingleItem(self):
        template = Template.Template('{{#block:list-separator=, }}{{item}}{{/block}}')
        result=template.RenderSimple(block=[{'item' : '0'}])
        self.assertEqual('0', result)

    def testExpandCompundItem(self):
        template = Template.Template('{{item.key}}')
        result=template.RenderSimple(item = {'key':'value'})
        self.assertEqual('value', result)

    def testExpandListSeparatorSingleItemSimpleList(self):
        template = Template.Template('{{#block:list-separator=, }}{{.}}{{/block}}')
        result=template.RenderSimple(block=[0])
        self.assertEqual('0', result)

    def testExpandListSeparatorShortAlias(self):
        template = Template.Template('{{#block:l-s=, }}{{item}}{{/block}}')
        result=template.RenderSimple(block=[{'item' : '0'}, {'item' : '1'}])
        self.assertEqual('0, 1', result)

    def testExpandListSeparatorNewline(self):
        template = Template.Template('{{#block:l-s=NEWLINE}}{{item}}{{/block}}')
        result=template.RenderSimple(block=[{'item' : '0'}, {'item' : '1'}])
        self.assertEqual('0\n1', result)

    def testExpandListSeparatorSpace(self):
        template = Template.Template('{{#block:l-s=SPACE}}{{item}}{{/block}}')
        result=template.RenderSimple(block=[{'item' : '0'}, {'item' : '1'}])
        self.assertEqual('0 1', result)

    def testExpandPrefixAfterWidth(self):
        template = Template.Template('{{item:width=-4:prefix=a}}')
        result=template.RenderSimple(item='b')
        self.assertEqual('a   b', result)

    def testExpandPrefixBeforeWidth(self):
        template = Template.Template('{{item:prefix=a:width=-4}}')
        result=template.RenderSimple(item='b')
        self.assertEqual('  ab', result)

    def testIndentBlock(self):
        template = Template.Template('{{#block:l-s=NEWLINE:indent=2}}{{item}}{{/block}}')
        result=template.RenderSimple(block=[{'item' : '0'}, {'item' : '1'}])
        self.assertEqual('\t\t0\n\t\t1', result)

    def testExpandWhitespaceSpace(self):
        template = Template.Template('{{_SPACE}}')
        result=template.RenderSimple()
        self.assertEqual(' ', result)

    def testExpandWhitespaceNewline(self):
        template = Template.Template('{{_NEWLINE}}')
        result=template.RenderSimple()
        self.assertEqual('\n', result)

    def testInvalidFormatterRaisesException(self):
        template = Template.Template ('{{test:foo}}')
        self.assertRaises(Template.InvalidFormatter, template.RenderSimple,test='test')

    def testInvalidTokenWithoutEndRaisesException(self):
        template = Template.Template ('{{test')
        self.assertRaises(Template.InvalidToken, template.RenderSimple)

    def testInvalidTokenWithSingleBraceAtEndRaisesException(self):
        template = Template.Template ('{{test}')
        self.assertRaises(Template.InvalidToken, template.RenderSimple)

    def testInvalidWhitespaceTokenRaisesException(self):
        template = Template.Template ('{{_NEWLINES}}')
        self.assertRaises(Template.InvalidWhitespaceToken, template.RenderSimple)

    def testUppercaseTransformation(self):
        template = Template.Template('{{item:upper-case}}')
        result=template.RenderSimple(item='baD')
        self.assertEqual('BAD', result)

    def testExpandSingleItemAsBlock(self):
        template = Template.Template('{{#item}}This is {{.}}{{/item}}')
        result = template.RenderSimple(item='value')
        self.assertEqual('This is value', result)

    def testExpandSingleItemAsBlockIsSkippedIfNotSet(self):
        template = Template.Template('{{#item}}This is {{.}}{{/item}}')
        result = template.RenderSimple()
        self.assertEqual('', result)

    def testExpandNestedRepeatedBlock (self):
        template = Template.Template ('{{#block}}{{#block}}{{item}}{{/block}}{{/block}}')
        result = template.RenderSimple (block = [{'item':0},{'item':1}])
        self.assertEqual('0101', result)

    def testExpandNestedRepeatedBlockTwoLevelsDeep (self):
        template = Template.Template ('{{#block}}{{#block}}{{#block}}{{item}}{{/block}}{{/block}}{{/block}}')
        result = template.RenderSimple (block = [{'item':0},{'item':1}])
        self.assertEqual('01010101', result)

    def testExpandSingleItemCompound (self):
        template = Template.Template('{{#item}}This is {{.field}}{{/item}}')
        result = template.RenderSimple(item={'field':'value'})
        self.assertEqual('This is value', result)

    def testFormatAsHex (self):
        template = Template.Template('{{item:hex}}')
        result = template.RenderSimple(item=127)
        self.assertEqual('0x7F', result)

if __name__ == '__main__':
    unittest.main()