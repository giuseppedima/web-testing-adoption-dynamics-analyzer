from sqlalchemy import ForeignKey, String, Integer, Boolean, Column, ForeignKeyConstraint
from sqlalchemy.exc import SQLAlchemyError

from core.database import Base, Session, engine

class RepositoryModel(Base):
    __tablename__ = "repository"
    name = Column(String(),primary_key=True)
    is_fork = Column(Boolean())
    commits = Column(Integer())
    branches = Column(Integer())
    releases = Column(Integer())
    forks = Column(Integer())
    main_language = Column(String())
    default_branch = Column(String())
    licences = Column(String())
    homepage = Column(String())
    watchers = Column(Integer())
    stargazers = Column(Integer())
    contributors = Column(Integer())
    size = Column(Integer())
    created_at = Column(String())
    pushed_at = Column(String())
    updated_at = Column(String())
    total_issues = Column(Integer())
    open_issues = Column(Integer())
    total_pull_requests = Column(Integer())
    open_pull_requests = Column(Integer())
    blank_lines = Column(Integer())
    code_lines = Column(Integer())
    comment_lines = Column(Integer())
    metrics = Column(String())
    last_commit = Column(String())
    last_commit_sha = Column(String())
    has_wiki = Column(Boolean())
    is_archived = Column(Boolean())
    is_disabled = Column(Boolean())
    is_locked = Column(Boolean())
    languages = Column(String())
    labels = Column(String())
    topics = Column(String())

    def __init__(self, name, is_fork, commits, branches, releases, forks,
                 main_language, default_branch, licenses, homepage, watchers,
                 stargazers, contributors, size, created_at, pushed_at, updated_at,
                 total_issues, open_issues, total_pull_requests, open_pull_requests,
                 blank_lines, code_lines, comment_lines, metrics, last_commit,
                 last_commit_sha, has_wiki, is_archived, is_disabled, is_locked, languages, labels, topics):
        self.name = name
        self.is_fork = is_fork
        self.commits = commits
        self.branches = branches
        self.releases = releases
        self.forks = forks
        self.main_language = main_language
        self.default_branch = default_branch
        self.licences = licenses
        self.homepage = homepage
        self.watchers = watchers
        self.stargazers = stargazers
        self.contributors = contributors
        self.size = size
        self.created_at = created_at
        self.pushed_at = pushed_at
        self.updated_at = updated_at
        self.total_issues = total_issues
        self.open_issues = open_issues
        self.total_pull_requests = total_pull_requests
        self.open_pull_requests = open_pull_requests
        self.blank_lines = blank_lines
        self.code_lines = code_lines
        self.comment_lines = comment_lines
        self.metrics = metrics
        self.last_commit = last_commit
        self.last_commit_sha = last_commit_sha
        self.has_wiki = has_wiki
        self.is_archived = is_archived
        self.is_disabled = is_disabled
        self.is_locked = is_locked
        self.languages = languages
        self.labels = labels
        self.topics = topics
        Base.metadata.create_all(engine)

    def connect_to_db(self):
        local_session = Session(bind=engine)
        return local_session

    def add_repository_to_db(self):
        local_session = Session(bind=engine)
        self.languages = self.convert_list_in_string(self.languages)
        self.labels = self.convert_list_in_string(self.labels)
        self.topics = self.convert_list_in_string(self.topics)
        self.metrics = self.convert_metrics_in_string(self.metrics)
        local_session.add(self)
        local_session.commit()

    def convert_metrics_in_string(self, metric):
        import json
        data = json.loads(metric)

        # Initialize a list to store metric strings
        metrics_strings = []

        # Iterate over each element in the list
        for item in data:
            # Build the string for the current element
            metrics_str = f"language:{item['language']}, commentLines:{item['commentLines']}, codeLines:{item['codeLines']}, blankLines:{item['blankLines']}"
            # Add the string to the list
            metrics_strings.append(metrics_str)

        # Join all metric strings using semicolon as separator
        output_string = "; ".join(metrics_strings)
        return output_string

    def convert_list_in_string(self, general_list):
        string = ""
        for element in general_list:
            string = string + element + "; "
        return string

    def convert_string_language_in_list(self):
        # Rimuovi lo spazio finale e poi suddividi la stringa utilizzando il separatore "; "
        elements = self.languages.rstrip("; ").split("; ")
        self.languages = elements

    def update_processed_repository(self):
        local_session = Session(bind=engine)
        # self.is_processed = True
        repository_to_update = local_session.query(RepositoryModel).filter(RepositoryModel.ID == self.ID).first()
        repository_to_update.is_processed = True
        local_session.commit()


class NonTrivialRepoDao:

    def __init__(self, name):
        self.name = name
        self.is_web_java = False
        self.is_web_python = False
        self.is_web_javascript = False
        self.is_web_typescript = False
        self.web_dependencies = []

    def set_is_web_java(self, value):
        self.is_web_java = value

    def set_is_web_python(self, value):
        self.is_web_python = value

    def set_is_web_javascript(self, value):
        self.is_web_javascript = value

    def set_is_web_typescript(self, value):
        self.is_web_typescript = value

    def set_web_dependency(self, dependencies):
        self.web_dependencies = dependencies


class NonTrivialRepo(Base):
    __tablename__ = "non_trivial_repository"
    name = Column(String(),primary_key=True)
    is_web_java = Column(Boolean())
    is_web_python = Column(Boolean())
    is_web_javascript = Column(Boolean())
    is_web_typescript = Column(Boolean())
    web_dependencies = Column(String())

    __table_args__ = (
        ForeignKeyConstraint(['name'], ['repository.name']),
    )

    def __init__(self, Non):
        self.name = NonTrivialRepo.name
        self.is_web_java = NonTrivialRepo.is_web_java
        self.is_web_python = NonTrivialRepo.is_web_python
        self.is_web_javascript = NonTrivialRepo.is_web_javascript
        self.is_web_typescript = NonTrivialRepo.is_web_typescript
        self.web_dependencies = self.convert_list_in_string(NonTrivialRepo.web_dependencies)
        Base.metadata.create_all(engine)

    def add_web_repository_to_db(self):
        local_session = Session(bind=engine)
        local_session.add(self)
        local_session.commit()

    def convert_list_in_string(self, general_list):
        string = ""
        for element in general_list:
            string = string + element + "; "
        return string

    def fetch_allwebrepo(self):
        local_session = Session(bind=engine)
        return local_session
        records = session.query(WebRepositoryDAO).all()

        # Stampa i record
        for record in records:
            print(record.id, record.name, record.value)


class GUITestingTestDetails(Base):
    __tablename__ = "gui_testing_test_details"

    repository_name = Column(String, ForeignKey("non_trivial_repository.name"), nullable=False)
    test_path = Column(String, primary_key=True, nullable=False)
    is_selenium_java = Column(Boolean())
    is_selenium_js = Column(Boolean())
    is_selenium_ts = Column(Boolean())
    is_selenium_py = Column(Boolean())
    is_playwright_java = Column(Boolean())
    is_playwright_js = Column(Boolean())
    is_playwright_ts = Column(Boolean())
    is_playwright_py = Column(Boolean())
    is_puppeteer_js = Column(Boolean())
    is_puppeteer_ts = Column(Boolean())
    is_puppeteer_py = Column(Boolean())
    is_cypress_js = Column(Boolean())
    is_cypress_ts = Column(Boolean())
    with_junit = Column(Boolean())
    with_testng = Column(Boolean())
    with_jest = Column(Boolean())
    with_mocha = Column(Boolean())
    with_jasmine = Column(Boolean())
    with_pytest = Column(Boolean())
    with_unittest = Column(Boolean())
    number_of_tests = Column(Integer())


class PerformanceTestingTestDetails(Base):
    __tablename__ = "performance_testing_test_details"

    repository_name = Column(String, ForeignKey("non_trivial_repository.name"), nullable=False)
    test_path = Column(String, primary_key=True, nullable=False)
    threadgroup_taskset_id = Column(Integer, primary_key=True, nullable=False)
    is_jmeter = Column(Boolean())
    is_locust = Column(Boolean())
    threadgroup_taskset_name = Column(String)
    number_of_users = Column(String)
    ramp_up = Column(String())
    loop_count = Column(String())
    duration = Column(String())
    number_of_requests = Column(String())


# GUITestingRepoDetails table definition
class GUITestingRepoDetails(Base):
    __tablename__ = 'gui_testing_repo_details'

    repository_name = Column(String, ForeignKey('non_trivial_repository.name'), primary_key=True)
    number_files_selenium_java = Column(Integer)
    number_files_selenium_js = Column(Integer)
    number_files_selenium_ts = Column(Integer)
    number_files_selenium_py = Column(Integer)
    number_files_playwright_java = Column(Integer)
    number_files_playwright_js = Column(Integer)
    number_files_playwright_ts = Column(Integer)
    number_files_playwright_py = Column(Integer)
    number_files_puppeteer_js = Column(Integer)
    number_files_puppeteer_ts = Column(Integer)
    number_files_puppeteer_py = Column(Integer)
    number_files_cypress_js = Column(Integer)
    number_files_cypress_ts = Column(Integer)
    with_junit = Column(Integer)
    with_testng = Column(Integer)
    with_jest = Column(Integer)
    with_mocha = Column(Integer)
    with_jasmine = Column(Integer)
    with_pytest = Column(Integer)
    with_unittest = Column(Integer)
    number_of_tests = Column(Integer)
    number_of_files = Column(Integer)

    def __init__(self, repo_name):
        self.repository_name=repo_name
        self.number_files_selenium_java = 0
        self.number_files_selenium_js = 0
        self.number_files_selenium_ts = 0
        self.number_files_selenium_py = 0
        self.number_files_playwright_java = 0
        self.number_files_playwright_js = 0
        self.number_files_playwright_ts = 0
        self.number_files_playwright_py = 0
        self.number_files_puppeteer_js = 0
        self.number_files_puppeteer_ts = 0
        self.number_files_puppeteer_py = 0
        self.number_files_cypress_js = 0
        self.number_files_cypress_ts = 0
        self.with_junit = 0
        self.with_testng = 0
        self.with_jest = 0
        self.with_mocha = 0
        self.with_jasmine = 0
        self.with_pytest = 0
        self.with_unittest = 0
        self.number_of_test = 0
        self.number_of_file = 0
    def add_e2erepository_to_db(self):
        with Session(bind=engine) as local_session:
            local_session.add(self)
            local_session.commit()
