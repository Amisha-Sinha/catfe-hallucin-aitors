from time import sleep
from github import Github, InputGitTreeElement
from langchain.tools import Tool, tool, BaseTool, StructuredTool  # Import BaseTool and StructuredTool for no-input schema
from pydantic import BaseModel, Field
import subprocess
import os

class RepoNameSchema(BaseModel):
    repo_name: str = Field(..., description="The name of the repository")

class PRSchema(BaseModel):
    repo_name: str = Field(..., description="The name of the repository")
    pr_number: int = Field(..., description="The pull request number")

class FileSchema(BaseModel):
    repo_name: str = Field(..., description="The name of the repository")
    filename: str = Field(..., description="The name of the file")

class CreatePRSchema(BaseModel):
    repo_name: str = Field(..., description="The name of the repository")
    filename: str = Field(..., description="The name of the file to edit")
    content: str = Field(..., description="The new content for the file")
    title: str = Field(..., description="The title of the pull request")  # Add title field

class NoInputSchema(BaseModel):
    pass

class DeleteForkSchema(BaseModel):
    repo_name: str = Field(..., description="The name of the repository")

class GitHubToolkit:
    def __init__(self, auth_token, hostname, organization):
        self.auth_token = auth_token
        self.hostname = hostname
        self.organization = organization
        self.client = Github(auth_token, base_url=hostname)
        self.org = self.client.get_organization(organization)

    def get_all_repo_names(self):
        repos = self.org.get_repos()
        return [repo.name for repo in repos]

    def get_repo_file_structure(self, repo_name):
        repo = self.org.get_repo(repo_name)
        contents = repo.get_contents("")
        file_structure = []
        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                file_structure.append(file_content.path)
        return file_structure

    def get_repo_pr_list(self, repo_name):
        repo = self.org.get_repo(repo_name)
        prs = repo.get_pulls(state='all')
        return [{'number': pr.number, 'title': pr.title} for pr in prs]

    def get_pr_diff(self, repo_name, pr_number):
        repo = self.org.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        return pr.diff()

    def get_file_contents(self, repo_name, filename):
        repo = self.org.get_repo(repo_name)
        file_content = repo.get_contents(filename)
        return file_content.decoded_content.decode()

    def create_bdd_repo_using_template(self, repo_name):
        template_repo_url = "https://github.com/GaurangRastogi/karate-bdd-template.git"  # Template repo URL
        new_repo = self.org.create_repo(repo_name, private=True)
        new_repo_url = new_repo.clone_url.replace("https://", f"https://{self.auth_token}@")

        # Clone the template repository
        try:
            subprocess.run(["git", "clone", template_repo_url, "template_bdd_repo"], check=True)
        except:
            pass

        # Change directory to the cloned repository
        os.chdir("template_bdd_repo")

        # Add the new repository as a remote and push the contents
        subprocess.run(["git", "remote", "add", "new_repo", new_repo_url], check=True)
        subprocess.run(["git", "push", "new_repo", "main"], check=True)

        # Change back to the original directory and remove the cloned repository
        os.chdir("..")

        return new_repo

    def create_pr_with_edits(self, repo_name, filename, content, title):
        repo = self.org.get_repo(repo_name)
        fork = repo.create_fork()
        file_content = fork.get_contents(filename)
        fork.update_file(file_content.path, "Update file", content, file_content.sha)
        pr = repo.create_pull(title=title, body="Updated file content", head=f"{fork.owner.login}:{fork.default_branch}", base=repo.default_branch)
        return pr.html_url

    def delete_fork(self, repo_name):
        repo = self.client.get_repo(f"{self.organization}/{repo_name}")
        repo.delete()
        return f"Fork {repo_name} deleted successfully."
    
    def generate_tools(self):
        get_all_repo_names_tool = StructuredTool.from_function(
            self.get_all_repo_names,
            name="Get all repositories in Organization",
            description="Get all repository names in the organization",
            args_schema=NoInputSchema  # Use no-input schema
        )

        get_repo_file_structure_tool = StructuredTool.from_function(
            self.get_repo_file_structure,
            name="Get Repository File Structure",
            description="Get the file structure of a repository in array form",
            args_schema=RepoNameSchema
        )

        get_repo_pr_list_tool = StructuredTool.from_function(
            self.get_repo_pr_list,
            name="Get all Pull Requests in Repository",
            description="Get the list of pull requests in a repository",
            args_schema=RepoNameSchema
        )

        get_pr_diff_tool = StructuredTool.from_function(
            self.get_pr_diff,
            name="get_pr_diff",
            description="Get the diff of a pull request",
            args_schema=PRSchema
        )

        get_file_contents_tool = StructuredTool.from_function(
            self.get_file_contents,
            name="Get contents of file in Repository",
            description="Get the entire contents of a file in a repository",
            args_schema=FileSchema
        )

        create_bdd_repo_using_template_tool = StructuredTool.from_function(
            self.create_bdd_repo_using_template,
            name="Create a BDD test suite Repo",
            description="Creates a new repository for BDD testing using a template repository",
            args_schema=RepoNameSchema
        )

        create_pr_with_edits_tool = StructuredTool.from_function(
            self.create_pr_with_edits,
            name="Make a PR with some changes",
            description="Forks the repo, commits changes to one file, and raises a PR",
            args_schema=CreatePRSchema
        )

        delete_fork_tool = StructuredTool.from_function(
            self.delete_fork,
            name="Delete a forked repository",
            description="Deletes a forked repository",
            args_schema=DeleteForkSchema
        )

        return [
            get_all_repo_names_tool,
            get_repo_file_structure_tool,
            get_repo_pr_list_tool,
            get_pr_diff_tool,
            get_file_contents_tool,
            create_bdd_repo_using_template_tool,
            create_pr_with_edits_tool,
            delete_fork_tool  # Add the new tool to the list
        ]