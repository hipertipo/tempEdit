import os, sys
from AppKit import NSFilenamesPboardType, NSDragOperationCopy
from vanilla import FloatingWindow, List, Button, TextBox, EditText, RadioGroup, ProgressBar, Group
from fontTools.designspaceLib import DesignSpaceDocument
from fontTools.ufoLib.glifLib import GlyphSet
from mojo.UI import AccordionView
from mojo.roboFont import OpenFont, NewFont, CurrentFont


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
    width  = 320
    height = 640
    padding = 10
    lineHeight = 22
    verbose = True

    _designspaces = {}
    _sources = {}

    def __init__(self):
        self.w = FloatingWindow(
                (self.width, self.height),
                title='tempEdit',
                minSize=(240, 360))

        self.designspaces = Group((0, 0, -0, -0))
        x = y = p = self.padding
        self.designspaces.list = List(
                (x, y, -p, -p),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                # editCallback=self.selectDesignspaceCallback,
                selectionCallback=self.selectDesignspaceCallback,
                enableDelete=True,
                otherApplicationDropSettings=dict(
                    type=NSFilenamesPboardType,
                    operation=NSDragOperationCopy,
                    callback=self.dropCallback))

        self.sources = Group((0, 0, -0, -0))

        x = y = p = self.padding
        self.sources.list = List((x, y, -p, -p), [])

        self.glyphs = Group((0, 0, -0, -0))

        x = y = p = self.padding
        textBoxHeight = -(self.lineHeight * 5) - (p * 3)
        self.glyphs.names = EditText(
                (x, y, -p, textBoxHeight),
                'a b c A B C one two three')

        y = -(p + self.lineHeight) * 4
        self.glyphs.importButton = Button(
                (x, y, -p, self.lineHeight),
                'import glyphs',
                callback=self.importButtonCallback)

        y = -(p + self.lineHeight) * 3
        self.glyphs.importMode = RadioGroup(
                (x, y, -p, self.lineHeight),
                ['fonts → fonts', 'fonts → layers'],
                sizeStyle='small',
                isVertical=False)
        self.glyphs.importMode.set(0)

        y = -(p + self.lineHeight) * 2
        self.glyphs.exportButton = Button(
                (x, y, -p, self.lineHeight),
                'export selected glyphs',
                callback=self.exportButtonCallback)

        y = -(p + self.lineHeight)
        self.glyphs.progress = ProgressBar((x, y, -p, self.lineHeight))

        descriptions = [
           dict(label="designspaces",
                view=self.designspaces,
                size=self.lineHeight*5,
                minSize=self.lineHeight*3,
                collapsed=False,
                canResize=True),
           dict(label="sources",
                view=self.sources,
                size=self.lineHeight*8,
                minSize=self.lineHeight*6,
                collapsed=False,
                canResize=True),
           dict(label="glyphs",
                view=self.glyphs,
                size=self.lineHeight*10,
                minSize=self.lineHeight*8,
                collapsed=False,
                canResize=True),
        ]
        self.w.accordionView = AccordionView((0, 0, -0, -0), descriptions)

        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

    # -------------
    # dynamic attrs
    # -------------

    @property
    def glyphNames(self):
        return self.glyphs.names.get().split()

    @property
    def selectedDesignspace(self):
        selection = self.designspaces.list.getSelection()
        designspaces = self.designspaces.list.get()
        return [designspace for i, designspace in enumerate(designspaces)] \
            if len(designspaces) else None

    @property
    def selectedMasters(self):
        selection = self.sources.list.getSelection()
        masters = self.sources.list.get()
        return [master for i, master in enumerate(masters) if i in selection]

    @property
    def glyphSetPathKey(self):
        return f'{self.key}.glyphSetPath'

    @property
    def importMode(self):
        return self.glyphs.importMode.get()

    # ---------
    # callbacks
    # ---------

    def selectDesignspaceCallback(self, sender):
        selection = sender.getSelection()
        designSpaces = self.designspaces.list.get()

        # delete current list
        posSize = self.sources.list.getPosSize()
        del self.sources.list

        # list of sources is empty
        if not selection or not len(designSpaces):
            items = []
            self.sources.list = List(posSize, [])
            return

        # get sources from selected designspace
        designSpaceLabel = [D for i, D in enumerate(designSpaces) if i in selection][0]
        designSpacePath = self._designspaces[designSpaceLabel]
        designSpace = DesignSpaceDocument()
        designSpace.read(designSpacePath)

        # get column descriptions
        titles  = ['name']
        titles += [axis.name for axis in designSpace.axes]
        descriptions = [{"title": D} for D in titles]

        # make list items
        self._sources = {}
        items = []
        for source in designSpace.sources:
            sourceName = os.path.splitext(os.path.split(source.path)[-1])[0]
            self._sources[sourceName] = source.path
            item = { 'name' : sourceName }
            for axis in designSpace.axes:
                item[axis.name] = source.location[axis.name]
            items.append(item)

        # create list UI with items
        self.sources.list = List(
            posSize, items,
            columnDescriptions=descriptions,
            allowsMultipleSelection=True,
            enableDelete=False)

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
                label = os.path.splitext(os.path.split(path)[-1])[0]
                self._designspaces[label] = path
                self.designspaces.list.append(label)
                self.designspaces.list.setSelection([0])

        return True

    def importButtonCallback(self, sender):

        if not len(self.selectedMasters):
            return

        if self.verbose:
            print('importing glyphs from selected sources...\n')

        # mode 0 : fonts → fonts

        if self.importMode == 0:

            for master in self.selectedMasters:
                ufoPath = self._sources[master['name']]
                srcFont = OpenFont(ufoPath, showInterface=False)
                tmpFont = NewFont(familyName=srcFont.info.familyName, styleName=srcFont.info.styleName, showInterface=False)
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
                                tmpFont[component.baseGlyph].lib[self.glyphSetPathKey] = glyphsFolder

                    if self.verbose:
                        print(f'\t\timporting {glyphName}...')
                    tmpFont[glyphName] = srcGlyph
                    tmpFont[glyphName].lib[self.glyphSetPathKey] = glyphsFolder

                tmpFont.openInterface()

                if self.verbose:
                    print()

        # mode 1 : fonts → layers

        else:
            
            tmpFont = CurrentFont()
            if tmpFont is None:
                tmpFont = NewFont(familyName='tempEdit')

            for i, master in enumerate(self.selectedMasters):
                ufoPath = self._sources[master['name']]
                if not os.path.exists(ufoPath):
                    if self.verbose:
                        print(f'source file does not exist: {ufoPath}')
                    continue
                
                srcFont = OpenFont(ufoPath, showInterface=False)
                glyphsFolder = os.path.join(ufoPath, 'glyphs')
                ufoName = splitall(glyphsFolder)[-2]
                layerName = os.path.splitext(ufoName)[0] # ufoName.replace('.ufo', '')
                tmpLayer = tmpFont.newLayer(layerName)

                if self.verbose:
                    print(f'\t{ufoName}:')

                if i == 0:
                    tmpFont.defaultLayer = tmpLayer
                    if 'foreground' in tmpFont.layerOrder:
                        tmpFont.removeLayer('foreground')

                for glyphName in self.glyphNames:

                    if glyphName not in srcFont:
                        if self.verbose:
                            print(f'\t\tcreating {glyphName}...')
                            tmpLayer.newGlyph(glyphName)

                    else:
                        srcGlyph = srcFont[glyphName]
                        for component in srcGlyph.components:
                            if component.baseGlyph not in tmpLayer:
                                if component.baseGlyph not in srcFont:
                                    continue
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
