from PySide6.QtWidgets import QWidget, QSplitter, QHBoxLayout
from PySide6.QtCore import Qt, Signal

from GUI.ProjectSelection import ProjectSelection
from GUI.ProjectToolbar import ProjectToolbar

from GUI.Widgets.ScenesView import ScenesView
from GUI.Widgets.ContentView import ContentView
from GUI.Widgets.ProjectOptions import ProjectOptions

class ModelView(QWidget):
    optionsChanged = Signal(dict)
    requestAction = Signal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._toolbar = ProjectToolbar(self)
        self._toolbar.toggleOptions.connect(self.ToggleProjectOptions)
        self._toolbar.setVisible(False)
        layout.addWidget(self._toolbar)

        # Scenes & Batches Panel
        self.scenes_view = ScenesView(self)

        # Main Content Area
        self.content_view = ContentView(self)

        # Project Options
        self.project_options = ProjectOptions()
        self.project_options.hide()
        self.project_options.optionsChanged.connect(self.optionsChanged)

        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.project_options)
        splitter.addWidget(self.scenes_view)
        splitter.addWidget(self.content_view)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 3)

        layout.addWidget(splitter)
        self.setLayout(layout)

        self.scenes_view.onSelection.connect(self._items_selected)
        self.content_view.onTranslateSelection.connect(self._on_translate_selection)
        self.content_view.onMergeSelection.connect(self._on_merge_selection)

    def SetDataModel(self, datamodel):
        self.SetViewModel(datamodel.viewmodel)
        self.SetProjectOptions(datamodel.options)

    def SetViewModel(self, viewmodel):
        self.content_view.Clear()

        if viewmodel is None:
            self.scenes_view.Clear()
        else:
            self.scenes_view.Populate(viewmodel)
            self.content_view.Populate(viewmodel)

    def SetProjectOptions(self, options):
        self.project_options.Clear()
        if not options:
            self.project_options.hide()
            self._toolbar.hide()
        else:
            self.project_options.Populate(options)

            self._toolbar.show()
            self._toolbar.show_options = not options.get('movie_name', None)
            if self._toolbar.show_options:
                self.project_options.show()

    def ToggleProjectOptions(self, show = None):
        if self.project_options.isVisible() and not show:
            self.optionsChanged.emit(self.project_options.GetOptions())
            self.project_options.hide()
        else:
            self.project_options.show()

    def ShowSubtitles(self, subtitles, translated):
        if subtitles:
            self.content_view.ShowSubtitles(subtitles)
        
        if translated:
            self.content_view.ShowTranslated(translated)

    def GetSelection(self) -> ProjectSelection:
        """
        Retrieve the current project selection
        """
        selection = ProjectSelection()
        model = self.scenes_view.model()

        selected_indexes = self.scenes_view.selectionModel().selectedIndexes()
        for index in selected_indexes:
            selection.AppendItem(model, index)

        # selected_subtitles = self.content_view.subtitle_view.selectionModel().selectedIndexes()
        # for index in selected_subtitles:
        #     selection.AppendSubtitle(model, index)

        # selected_translations = self.content_view.translation_view.selectionModel().selectedIndexes()
        # for index in selected_translations:
        #     selection.AppendTranslation(model, index)

        return selection

    def _items_selected(self):
        selection : ProjectSelection = self.GetSelection()
        self.content_view.ShowSelection(selection)

    def _on_translate_selection(self):
        selection : ProjectSelection = self.GetSelection()
        self.requestAction.emit('Translate Selection', (selection,))

    def _on_merge_selection(self):
        selection : ProjectSelection = self.GetSelection()
        self.requestAction.emit('Merge Selection', (selection,))
