import os, sys
from AppKit import NSFilenamesPboardType, NSDragOperationCopy
from vanilla import Window, List, Button, TextBox, EditText
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.ufoLib.glifLib import GlyphSet
from mojo.roboFont import OpenWindow


def splitall(path):
    # copied from http://www.oreilly.com/library/view/python-cookbook/0596001673/ch04s16.html
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


class TempEditGlyphs:

    key = 'com.hipertipo.tempEdit'

    width      = 640
    height     = 640
    padding    = 10
    lineHeight = 22

    verbose = True

    def __init__(self):
        self.w = Window((self.width, self.height),
            title='tempEdit',
            minSize=(self.width * 0.6, self.height * 0.7))

        x = y = p = self.padding
        self.w.designSpacesListLabel = TextBox(
            (x, y, -p, self.lineHeight),
            'design spaces:', sizeStyle='small')

        y += self.lineHeight
        listHeight = self.lineHeight * 4
        self.w.designSpacesList = List(
            (x, y, -p, listHeight),
            [],
            allowsMultipleSelection=False,
            allowsEmptySelection=False,
            selectionCallback=self.selectDesignspaceCallback,
            enableDelete=True,
            otherApplicationDropSettings=dict(
                type=NSFilenamesPboardType,
                operation=NSDragOperationCopy,
                callback=self.dropCallback))

        y += listHeight + p
        self.w.glyphNamesLabel = TextBox(
            (x, y, -p, self.lineHeight),
            'glyph names:', sizeStyle='small')

        y += self.lineHeight
        self.w.glyphNames = EditText(
            (x, y, -p, self.lineHeight),
            'a b c A B C one two three')

        y += self.lineHeight + p
        self.w.mastersListLabel = TextBox(
            (x, y, -p, self.lineHeight),
            'masters:', sizeStyle='small')

        y += self.lineHeight
        listHeight = -(p * 3 + self.lineHeight * 2)
        self.w.mastersList = List((x, y, -p, listHeight), [])

        y = -(p + self.lineHeight) * 2
        self.w.importButton = Button(
                (x, y, -p, self.lineHeight),
                'import glyphs',
                callback=self.importButtonCallback)

        y = -(p + self.lineHeight)
        self.w.exportButton = Button(
                (x, y, -p, self.lineHeight),
                'export glyphs',
                callback=self.exportButtonCallback)

        self.w.open()

    @property
    def glyphNames(self):
        return self.w.glyphNames.get().split()

    @property
    def selectedDesignspace(self):
        selection = self.w.designSpacesList.getSelection()
        designspaces = self.w.designSpacesList.get()
        return [designspace for i, designspace in enumerate(designspaces)] if len(designspaces) else None

    @property
    def selectedMasters(self):
        selection = self.w.mastersList.getSelection()
        masters = self.w.mastersList.get()
        return [master for i, master in enumerate(masters) if i in selection]

    @property
    def glyphSetPathKey(self):
        return f'{self.key}.glyphSetPath'

    def selectDesignspaceCallback(self, sender):
        selection = sender.getSelection()
        designSpaces = self.w.designSpacesList.get()
        if not selection or not len(designSpaces):
            return
        designSpacePath = [D for i, D in enumerate(designSpaces) if i in selection][0]
        designSpace = DesignSpaceDocument()
        designSpace.read(designSpacePath)

        posSize = self.w.mastersList.getPosSize()
        del self.w.mastersList

        titles  = ['UFO path']
        titles += [axis.name for axis in designSpace.axes]
        descriptions = [{"title": D} for D in titles]
        for i, D in enumerate(descriptions):
            if i > 0:
                D['width'] = 60

        items = []
        for source in designSpace.sources:
            item = { 'UFO path' : source.path }
            for axis in designSpace.axes:
                item[axis.name] = source.location[axis.name]
            items.append(item)

        self.w.mastersList = List(
            posSize, items,
            columnDescriptions=descriptions,
            allowsMultipleSelection=True,
            enableDelete=False)

    def importButtonCallback(self, sender):
        if not len(self.selectedMasters):
            return

        if self.verbose: print('importing glyphs from selected sources...\n')

        for master in self.selectedMasters:
            ufoPath = master['UFO path']
            srcFont = OpenFont(ufoPath, showInterface=False)
            tmpFont = NewFont(familyName=srcFont.info.familyName, styleName=srcFont.info.styleName)
            glyphsFolder = os.path.join(ufoPath, 'glyphs')
            tmpFont.lib[self.glyphSetPathKey] = glyphsFolder
            ufoName = splitall(glyphsFolder)[-2]

            if self.verbose: print(f'\t{ufoName}:')
            for glyphName in self.glyphNames:
                if glyphName not in srcFont:
                    if self.verbose: print(f'\t\t{glyphName} not in font.')
                    continue

                srcGlyph = srcFont[glyphName]
                if srcGlyph.components:
                    for component in srcGlyph.components:
                        if not component.baseGlyph in tmpFont:
                            if self.verbose: print(f'\t\timporting {component.baseGlyph} ({glyphName})...')
                            tmpFont[component.baseGlyph] = srcFont[component.baseGlyph]

                if self.verbose: print(f'\t\timporting {glyphName}...')
                tmpFont[glyphName] = srcGlyph

            if self.verbose: print()

        if self.verbose: print('...done.\n')

    def exportButtonCallback(self, sender):
        f = CurrentFont()
        if f is None:
            return

        print('exporting selected glyphs back to their sources...')

        glyphsFolder = f.lib[self.glyphSetPathKey]
        glyphSet = GlyphSet(glyphsFolder, validateWrite=True)
        ufoName = splitall(glyphsFolder)[-2]

        for glyphName in f.selectedGlyphNames:
            print(f'\twriting {glyphName} in {ufoName}...')
            glyphSet.writeGlyph(glyphName, f[glyphName].naked(), f[glyphName].drawPoints)

        glyphSet.writeContents()

        print('...done.\n')

    def dropCallback(self, sender, dropInfo):
        isProposal = dropInfo["isProposal"]
        existingPaths = sender.get()
        paths = dropInfo["data"]
        paths = [path for path in paths if path not in existingPaths]
        paths = [path for path in paths if os.path.splitext(path)[-1].lower() == '.designspace']

        if not paths:
            return False

        if not isProposal:
            for path in paths:
                self.w.designSpacesList.append(path)

        return True


if __name__ == '__main__':

    OpenWindow(TempEditGlyphs)
