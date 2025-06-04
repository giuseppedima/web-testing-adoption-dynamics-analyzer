import logging
import os

from git import Repo, GitCommandError

logger = logging.getLogger(__name__)
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.INFO)


class Cloner:
    def __init__(self, output_folder):
        self.output_folder = output_folder
        self.max_retries = 5

    def create_repository_url(self, repository):
        print("trying to clone " + repository)
        repo_url = "https://github.com/" + repository + ".git"
        print(repo_url)
        return repo_url

    def is_directory_empty(self, path):
        return os.path.exists(path) and not os.listdir(path)

    def clone_repository(self, repository):
        repo_url = self.create_repository_url(repository)
        repo_path = ""
        logging.info("sto clonando " + repository)

        retries = 0
        while retries < self.max_retries:
            try:
                repo_name = repository.replace("/", "\\")
                repo_path = os.path.join(self.output_folder, repo_name)
                if self.is_directory_empty(repo_path):
                    os.rmdir(repo_path)
                if not os.path.exists(repo_path):
                    #depth=1 to not clone all the history
                    Repo.clone_from(repo_url, str(repo_path))
                    logging.info('repository clonata')
                    print(f"Repository '{repo_name}' cloned successfully.")
                    print("ho appena clonato " + str(repo_path))
                    logging.info("ho appena clonato " + str(repo_path))
                    return repo_path
                else:
                    logging.warning("ho già trovato clonato " + str(repo_path))
                    print("ho già trovato clonato " + str(repo_path))
                    return repo_path

            except GitCommandError as e:
                retries += 1
                logging.warning(
                    f"Problema durante la clonazione della repository '{repo_url}' (tentativo {retries}/{self.max_retries}): {str(e)}")
                print(f"Failed to clone repository '{repo_url}' (tentativo {retries}/{self.max_retries}): {str(e)}")
                if retries >= self.max_retries:
                    logging.error(
                        f"Superato il numero massimo di tentativi ({self.max_retries}) per clonare la repository '{repo_url}'")
                    print(
                        f"Superato il numero massimo di tentativi ({self.max_retries}) per clonare la repository '{repo_url}'")
                    return repo_path
                else:
                    logging.info(
                        f"Riprovo a clonare la repository '{repo_url}' (tentativo {retries + 1}/{self.max_retries})")
                    print(f"Riprovo a clonare la repository '{repo_url}' (tentativo {retries + 1}/{self.max_retries})")

        return repo_path

