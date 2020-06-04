from sources.edimdoma.loader import EdimDoma
from sources.eda.loader import EdaRu


class Collector:

    def __init__(self, base_path):
        self.sources = [EdimDoma(base_path)]

    def load_all(self):

        for module in self.sources:
            print(f'Выполняется загрузка данных из источника {module.__name__}')
            module.load()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for i, source in enumerate(self.sources): del self.sources[i]
