import json
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

class RaisePRSchema(BaseModel):
    repo_name: str = Field(..., description="The name of the repository")
    title: int = Field(..., description="The title of the pull request")

class FileSchema(BaseModel):
    repo_name: str = Field(..., description="The name of the repository")
    filename: str = Field(..., description="The name of the file")

class CreateCommitSchema(BaseModel):
    repo_name: str = Field(..., description="The name of the repository")
    filename: str = Field(..., description="The name of the file to edit")
    content: str = Field(..., description="The new content for the file")
    title: str = Field(..., description="The title of the commit")  # Add title field

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
        return [{'number': pr.number, 'title': pr.title, 'state': pr.state} for pr in prs]
    
    def fetch_pr_details(self, repo_name, pr_number):
        """Fetch details of a specific PR, including files changed, comments, and state."""
        try:
            repo = self.org.get_repo(repo_name)
            pr = repo.get_pull(pr_number)
            pr_info = {
                "title": pr.title,
                "number": pr.number,
                "state": pr.state,  # open or closed
                "description": pr.body,
                "files": [
                    {"filename": file.filename, "patch": file.patch} for file in pr.get_files()
                ],
                "comments": [comment.body for comment in pr.get_issue_comments()]
            }
            return json.dumps(pr_info, indent=4)
        except Exception as e:
            return f"Error: {e}"
    
    def get_file_contents(self, repo_name, filename):
        repo = self.org.get_repo(repo_name)
        file_content = repo.get_contents(filename)
        return file_content.decoded_content.decode()

    def create_bdd_repo_using_template(self, repo_name):
        template_repo_url = "https://github.com/GaurangRastogi/karate-bdd-template.git"  # Template repo URL
        new_repo = self.org.create_repo(repo_name)
        new_repo_url = new_repo.clone_url.replace("https://", f"https://{self.auth_token}@")

        # Clone the template repository
        if not os.path.exists("template_bdd_repo"):
            try:
                subprocess.run(["git", "clone", template_repo_url, "template_bdd_repo"], check=True)
            except Exception as e:
                return f"Error cloning template repository: {e}"

        # Change directory to the cloned repository
        os.chdir("template_bdd_repo")

        # Add the new repository as a remote and push the contents
        try:
            subprocess.run(["git", "remote", "add", "new_repo", new_repo_url], check=True)
        except subprocess.CalledProcessError:
            subprocess.run(["git", "remote", "set-url", "new_repo", new_repo_url], check=True)

        subprocess.run(["git", "push", "new_repo", "main"], check=True)

        # Change back to the original directory and remove the cloned repository
        os.chdir("..")

        return new_repo

    def fork_repo(self, repo_name):
        try:
            repo = self.org.get_repo(repo_name)
            # Check if a fork already exists and delete it
            user = self.client.get_user()
            try:
                fork = user.get_repo(repo_name)
                fork.delete()
            except:
                pass
            fork = repo.create_fork()
            return fork
        except Exception as e:
            return f"Error creating fork: {e}"

    def push_commits_to_fork(self, repo_name, filename, content, title):
        try:
            fork = self.client.get_repo(f"{self.client.get_user().login}/{repo_name}")
            if not fork:
                return "Error: Fork does not exist."
            try:
                file_content = fork.get_contents(filename)
                fork.update_file(file_content.path, title, content, file_content.sha)
                return "Files updated successfully"
            except:
                fork.create_file(filename, title, content)
                return "Files created successfully"
        except Exception as e:
            return f"Error pushing commits to fork: {e}"

    def raise_pr_from_fork(self, repo_name, title):
        try:
            fork = self.client.get_repo(f"{self.client.get_user().login}/{repo_name}")
            if not fork:
                return "Error: Fork does not exist."
            repo = self.org.get_repo(repo_name)
            pr = repo.create_pull(
                title=f"Automated PR: {title}",
                body="Updated file content",
                head=f"{fork.owner.login}:{fork.default_branch}",
                base=repo.default_branch
            )
            return pr.html_url
        except Exception as e:
            return f"Error raising PR from fork: {e}"

    def delete_fork(self, repo_name):
        repo = self.client.get_repo(f"{self.client.get_user().login}/{repo_name}")
        repo.delete()
        return f"Fork {repo_name} deleted successfully."
    
    def generate_tools(self):
        get_all_repo_names_tool = StructuredTool.from_function(
            self.get_all_repo_names,
            description="Get all repository names in the organization. This tool retrieves the names of all repositories within the specified organization. It is useful for understanding the scope of available repositories and identifying which repositories you can interact with.",
            args_schema=NoInputSchema  # Use no-input schema
        )

        get_repo_file_structure_tool = StructuredTool.from_function(
            self.get_repo_file_structure,
            name="get_repository_file_structure",  # Updated name
            description="Get the file structure of a repository in array form. This tool retrieves the hierarchical structure of files and directories within a specified repository. It is useful for understanding the organization of the repository, identifying files of interest, and determining the overall layout of the project.",
            args_schema=RepoNameSchema
        )

        get_repo_pr_list_tool = StructuredTool.from_function(
            self.get_repo_pr_list,
            name="get_all_pull_requests_in_repository",  # Updated name
            description="Get the list of pull requests in a repository. This tool retrieves all pull requests (open, closed, and merged) for a specified repository. It is useful for reviewing the history of changes, understanding ongoing work, and identifying contributions to the repository.",
            args_schema=RepoNameSchema
        )

        fetch_pr_details_tool = StructuredTool.from_function(
            self.fetch_pr_details,
            name="fetch_pr_details",  # Updated name
            description="Fetch detailed information about a specific pull request in a repository. This tool retrieves the pull request's title, number, state (open or closed), description, the list of files changed (including their patches), and all comments associated with the pull request. It is useful for reviewing the changes made in a pull request, understanding its context, and analyzing the feedback provided by reviewers.",
            args_schema=PRSchema  # Schema specifying the repository name and pull request number as inputs
        )

        get_file_contents_tool = StructuredTool.from_function(
            self.get_file_contents,
            name="get_contents_of_file_in_repository",  # Updated name
            description="Get the entire contents of a file in a repository. You should use this when you want to understand the project and know the contents of the file. Good for learning about the project and performing edits",
            args_schema=FileSchema
        )

        create_bdd_repo_using_template_tool = StructuredTool.from_function(
            self.create_bdd_repo_using_template,
            name="create_bdd_test_suite_repo",  # Updated name
            description="Creates a new repository for Behavior-Driven Development (BDD) testing using a predefined template repository. This tool is useful for quickly setting up a standardized BDD test suite in a new repository, ensuring consistency and saving time.",
            args_schema=RepoNameSchema
        )

        fork_repo_tool = StructuredTool.from_function(
            self.fork_repo,
            name="fork_repository",  # New tool name
            description="Forks a specified repository. Useful for creating a personal copy of a repository for experimentation or contributions.",
            args_schema=RepoNameSchema
        )

        push_commits_to_fork_tool = StructuredTool.from_function(
            self.push_commits_to_fork,
            name="push_commits_to_fork",  # New tool name
            description="Pushes commits to a forked repository. Useful for updating the fork with new changes or preparing for a pull request.",
            args_schema=CreateCommitSchema  # Correct schema for repo_name, filename, and content
        )

        raise_pr_from_fork_tool = StructuredTool.from_function(
            self.raise_pr_from_fork,
            name="raise_pr_from_fork",  # New tool name
            description="Creates a pull request from a forked repository with a good descriptive title. Useful for contributing changes back to the original repository.",
            args_schema=RaisePRSchema  # Correct schema for repo_name and title
        )

        delete_fork_tool = StructuredTool.from_function(
            self.delete_fork,
            name="delete_forked_repository",  # Updated name
            description="Deletes a forked repository. Useful for cleanup after completing work on a fork.",
            args_schema=DeleteForkSchema
        )

        return [
            get_all_repo_names_tool,
            get_repo_file_structure_tool,
            get_repo_pr_list_tool,
            fetch_pr_details_tool,
            get_file_contents_tool,
            create_bdd_repo_using_template_tool,
            fork_repo_tool,  # Add the new tool to the list
            push_commits_to_fork_tool,  # Add the new tool to the list
            raise_pr_from_fork_tool,  # Add the new tool to the list
            delete_fork_tool
        ]