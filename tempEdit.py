import os, sys
from AppKit import NSFilenamesPboardType, NSDragOperationCopy
from vanilla import Window, List, Button, TextBox, EditText, RadioGroup, ProgressBar
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
            'designspaces:', sizeStyle='small')

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
        self.w.mastersListLabel = TextBox(
            (x, y, -p, self.lineHeight),
            'UFO sources:', sizeStyle='small')

        y += self.lineHeight
        listHeight = -self.lineHeight * 6 - p * 6
        self.w.mastersList = List((x, y, -p, listHeight), [])

        y = -self.lineHeight * 6 - p * 5
        self.w.glyphNamesLabel = TextBox(
            (x, y, -p, self.lineHeight),
            'glyph names:', sizeStyle='small')

        y = -(p + self.lineHeight) * 5
        self.w.glyphNames = EditText(
            (x, y, -p, self.lineHeight),
            'a b c A B C one two three')

        y = -(p + self.lineHeight) * 4
        self.w.importButton = Button(
                (x, y, -p, self.lineHeight),
                'import glyphs',
                callback=self.importButtonCallback)

        y = -(p + self.lineHeight) * 3
        self.w.importMode = RadioGroup(
                (x, y, -p, self.lineHeight),
                ['fonts → fonts', 'fonts → layers'],
                sizeStyle='small',
                isVertical=False)
        self.w.importMode.set(0)

        y = -(p + self.lineHeight) * 2
        self.w.exportButton = Button(
                (x, y, -p, self.lineHeight),
                'export selected glyphs',
                callback=self.exportButtonCallback)

        y = -(p + self.lineHeight)
        self.w.progress = ProgressBar((x, y, -p, self.lineHeight))

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

    @property
    def importMode(self):
        return self.w.importMode.get()

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

        if self.verbose:
            print('importing glyphs from selected sources...\n')

        # ----------------------
        # mode 0 : fonts → fonts
        # ----------------------

        if self.importMode == 0:

            for master in self.selectedMasters:
                ufoPath = master['UFO path']
                srcFont = OpenFont(ufoPath, showInterface=False)
                tmpFont = NewFont(familyName=srcFont.info.familyName, styleName=srcFont.info.styleName)
                glyphsFolder = os.path.join(ufoPath, 'glyphs')
                ufoName = splitall(glyphsFolder)[-2]

                if self.verbose:
                    print(f'\t{ufoName}:')

                for glyphName in self.glyphNames:
                    if glyphName not in srcFont:
                        if self.verbose:
                            print(f'\t\t{glyphName} not in font.')
                        continue

                    srcGlyph = srcFont[glyphName]
                    if srcGlyph.components:
                        for component in srcGlyph.components:
                            if not component.baseGlyph in tmpFont:
                                if self.verbose:
                                    print(f'\t\timporting {component.baseGlyph} ({glyphName})...')
                                tmpFont[component.baseGlyph] = srcFont[component.baseGlyph]
                                tmpFont[glyphName].lib[self.glyphSetPathKey] = glyphsFolder

                    if self.verbose:
                        print(f'\t\timporting {glyphName}...')
                    tmpFont[glyphName] = srcGlyph
                    tmpFont[glyphName].lib[self.glyphSetPathKey] = glyphsFolder

                if self.verbose:
                    print()

        # -----------------------
        # mode 1 : fonts → layers
        # -----------------------

        else:
            tmpFont  = NewFont(familyName='tempEdit')

            for i, master in enumerate(self.selectedMasters):
                ufoPath = master['UFO path']
                srcFont = OpenFont(ufoPath, showInterface=False)
                glyphsFolder = os.path.join(ufoPath, 'glyphs')
                ufoName = splitall(glyphsFolder)[-2]

                layerName = ufoName.replace('.ufo', '')
                tmpLayer = tmpFont.newLayer(layerName)

                if self.verbose:
                    print(f'\t{ufoName}:')

                if i == 0:
                    tmpFont.defaultLayer = tmpLayer
                    tmpFont.removeLayer('foreground')

                for glyphName in self.glyphNames:
                    if glyphName not in srcFont:
                        if self.verbose:
                            print(f'\t\t{glyphName} not in font.')
                        continue

                    srcGlyph = srcFont[glyphName]
                    if srcGlyph.components:
                        for component in srcGlyph.components:
                            if not component.baseGlyph in tmpFont:
                                if self.verbose:
                                    print(f'\t\timporting {component.baseGlyph} ({glyphName})...')
                                tmpLayer[component.baseGlyph] = srcFont[component.baseGlyph]
                                tmpLayer[component.baseGlyph].lib[self.glyphSetPathKey] = glyphsFolder

                    if self.verbose:
                        print(f'\t\timporting {glyphName}...')
                    tmpLayer[glyphName] = srcGlyph
                    tmpLayer[glyphName].width = srcGlyph.width
                    tmpLayer[glyphName].lib[self.glyphSetPathKey] = glyphsFolder

                if self.verbose:
                    print()

        if self.verbose:
            print('...done.\n')

    def exportButtonCallback(self, sender):
        f = CurrentFont()
        if f is None:
            return

        if self.verbose:
            print('exporting selected glyphs back to their sources...\n')

        for glyphName in f.selectedGlyphNames:
            for layerName in f.layerOrder:
                glyph = f[glyphName].getLayer(layerName)

                if self.glyphSetPathKey not in glyph.lib:
                    continue

                glyphsFolder = glyph.lib[self.glyphSetPathKey]
                glyphSet = GlyphSet(glyphsFolder, validateWrite=True)
                ufoName = splitall(glyphsFolder)[-2]

                if self.verbose:
                    print(f'\twriting {glyphName} to {ufoName}...')

                glyphSet.writeGlyph(glyphName, glyph.naked(), glyph.drawPoints)
                glyphSet.writeContents()

        if self.verbose:
            print()
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
