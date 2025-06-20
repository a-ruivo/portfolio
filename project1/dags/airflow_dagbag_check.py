from pathlib import Path
from datetime import datetime, timedelta

# Simulações mínimas para o script funcionar isoladamente
def correct_maybe_zipped(path):
    return path

def list_py_file_paths(folder, safe_mode=True):
    return [str(p) for p in Path(folder).glob("*.py")]

def timezone_utcnow():
    return datetime.utcnow()

class FileLoadStat:
    def __init__(self, file, duration, dag_num, task_num, dags, warning_num):
        self.file = file
        self.duration = duration
        self.dag_num = dag_num
        self.task_num = task_num
        self.dags = dags
        self.warning_num = warning_num

# Classe com estado para rodar o método
class DagCollector:
    def __init__(self):
        self.read_dags_from_db = False
        self.dag_folder = "/home/ruivo/analytics_engineer/portfolio/project1/dags"
        self.dagbag_stats = []
        self.captured_warnings = {}
        self.log = self  # Simula o logger como o próprio objeto

    # Simulação de logger
    def info(self, msg, *args): print("INFO:", msg % args if args else msg)
    def debug(self, msg, *args): print("DEBUG:", msg % args if args else msg)
    def error(self, msg, *args): print("ERROR:", msg % args if args else msg)
    def exception(self, e): print("EXCEPTION:", e)

    def process_file(self, filepath, only_if_updated=True, safe_mode=False):
        # Aqui simulamos que cada arquivo tem uma DAG com duas tasks
        class FakeDAG:
            def __init__(self, dag_id):
                self.dag_id = dag_id
                self.tasks = ["task_1", "task_2"]
        return [FakeDAG(Path(filepath).stem)]

    def collect_dags(self, dag_folder=None, only_if_updated=True, include_examples=False, safe_mode=False):
        if self.read_dags_from_db:
            self.debug("Leitura via DB — abortado.")
            return

        dag_folder = correct_maybe_zipped(str(dag_folder or self.dag_folder))
        self.info("Lendo DAGs de: %s", dag_folder)

        files_to_parse = list_py_file_paths(dag_folder, safe_mode=safe_mode)
        self.debug("Arquivos encontrados (%d): %s", len(files_to_parse), files_to_parse)

        stats = []
        for filepath in files_to_parse:
            self.debug("Processando: %s", filepath)
            try:
                start = timezone_utcnow()
                found_dags = self.process_file(filepath, only_if_updated, safe_mode)
                end = timezone_utcnow()
                stats.append(FileLoadStat(
                    file=filepath,
                    duration=end - start,
                    dag_num=len(found_dags),
                    task_num=sum(len(d.tasks) for d in found_dags),
                    dags=str([d.dag_id for d in found_dags]),
                    warning_num=len(self.captured_warnings.get(filepath, []))
                ))
                self.debug("%s: %d DAG(s)", filepath, len(found_dags))
            except Exception as e:
                self.error("Erro em %s: %s", filepath, e)
                self.exception(e)

        self.dagbag_stats = sorted(stats, key=lambda x: x.duration, reverse=True)
        self.info("%d arquivos processados", len(stats))

# Execução principal do script
if __name__ == "__main__":
    collector = DagCollector()
    collector.collect_dags()
