class hofAnime:
    def __init__(self, id, name):
        self.mal_id = id
        self.name = name
        self.themes = list()

    def addTheme(self, theme):
        self.themes.append(theme)

    def printContent(self):
        print(self.name)
        print(f'\t{self.mal_id}')
        print('\tThemes:')
        for theme in self.themes:
            print(f'\t\t{theme}')