from Dataset.Repository import Repository
from DBconnector import Session, engine


class Filter:
    def __init__(self, repository_id=0, name="", is_fork=False, commits=0, branches=0, default_branch="",
                 releases=0, contributors=0, repository_license="", watchers=0, stargazers=0, forks=0,
                 size=0, created_at="", pushed_at="", updated_at="",
                 homepage="", main_language=None, total_issues=0, open_issues=0, total_pull_requests=0,
                 open_pull_requests=0, last_commit="", last_commit_sha="", has_wiki=False,
                 is_archived=False, languages=None, labels=None, is_processed=False):
        if main_language is None:
            main_language = []
        if labels is None:
            labels = []
        if languages is None:
            languages = []
        self.__id = repository_id
        self.__name = name
        self.__is_fork = is_fork
        self.__commits = commits
        self.__branches = branches
        self.__default_branch = default_branch
        self.__releases = releases
        self.__contributors = contributors
        self.__license = repository_license
        self.__watchers = watchers
        self.__stargazers = stargazers
        self.__forks = forks
        self.__size = size
        self.__created_at = created_at
        self.__pushed_at = pushed_at
        self.__updated_at = updated_at
        self.__homepage = homepage
        self.__main_language = main_language
        self.__total_issues = total_issues
        self.__open_issues = open_issues
        self.__total_pull_requests = total_pull_requests
        self.__open_pull_requests = open_pull_requests
        self.__last_commit = last_commit
        self.__last_commit_sha = last_commit_sha
        self.__has_wiki = has_wiki
        self.__is_archived = is_archived
        self.__languages = languages
        self.__labels = labels
        self.__is_processed = is_processed

    def filtering(self):
        local_session = Session(bind=engine)
        filtered_repositories = []
        repositories = local_session.query(Repository).filter(Repository.is_fork == self.__is_fork,
                                                              Repository.commits >= self.__commits,
                                                              Repository.stargazers >= self.__stargazers,
                                                              Repository.contributors >= self.__contributors,
                                                              Repository.is_processed == self.__is_processed).all()
        print("la lista è lunga " + str(len(repositories)))
        for repository in repositories:
            repository.convert_string_language_in_list()
            print(repository.name)
            print(repository.languages)
            print(repository.main_language)

            for language in self.__languages:
                if language in repository.languages or language == repository.main_language:
                    filtered_repositories.append(repository)
                    print("l'id è " + str(repository.ID) + " il nome è " + repository.name)
                    break

            print(len(filtered_repositories))
        return filtered_repositories
