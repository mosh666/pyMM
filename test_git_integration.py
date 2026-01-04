"""
Test Git integration functionality.

This test script verifies:
- GitService operations
- Project Git integration
- Git status, commit, and log operations
"""

import sys
import shutil
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.project import Project
from app.services.project_service import ProjectService
from app.services.git_service import GitService


def test_git_service():
    """Test GitService functionality."""
    print("=" * 60)
    print("Testing Git Service")
    print("=" * 60)
    
    test_repo_path = Path("D:/pyMM/test_projects/git_test_repo")
    
    # Clean up if exists
    if test_repo_path.exists():
        shutil.rmtree(test_repo_path)
    
    test_repo_path.mkdir(parents=True)
    
    try:
        # Test init_repository
        print("\n✓ Creating test repository directory")
        repo = GitService.init_repository(test_repo_path, initial_commit=True)
        print(f"✓ Initialized Git repository with initial commit")
        
        # Test is_repository
        assert GitService.is_repository(test_repo_path)
        print(f"✓ Confirmed directory is a Git repository")
        
        # Test get_status
        status = GitService.get_status(test_repo_path)
        print(f"✓ Got repository status: {status['branch']}")
        print(f"  - Branch: {status['branch']}")
        print(f"  - Changes: {status['total_changes']}")
        
        # Create a test file
        test_file = test_repo_path / "test.txt"
        test_file.write_text("Hello, Git!")
        print(f"✓ Created test file: test.txt")
        
        # Check status with untracked file
        status = GitService.get_status(test_repo_path)
        assert len(status['untracked']) == 1
        print(f"✓ Detected untracked file: {status['untracked']}")
        
        # Test commit
        success = GitService.commit(test_repo_path, "Add test file", add_all=True)
        assert success
        print(f"✓ Committed changes")
        
        # Check status after commit
        status = GitService.get_status(test_repo_path)
        assert status['total_changes'] == 0
        print(f"✓ Repository is clean after commit")
        
        # Test get_log
        log = GitService.get_log(test_repo_path, max_count=5)
        assert len(log) == 2  # Initial commit + test file commit
        print(f"✓ Retrieved commit log: {len(log)} commits")
        for commit in log:
            print(f"  - {commit['sha']}: {commit['message'][:50]}")
        
        # Close the repository to release file handles
        repo.close()
        
        print("\n✅ Git service tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Clean up
        if test_repo_path.exists():
            try:
                # On Windows, we need to handle file permissions
                import stat
                def remove_readonly(func, path, _):
                    """Clear the readonly bit and reattempt the removal"""
                    Path(path).chmod(stat.S_IWRITE)
                    func(path)
                
                shutil.rmtree(test_repo_path, onerror=remove_readonly)
            except Exception as e:
                print(f"Warning: Could not clean up test repo: {e}")
        print(f"✓ Cleaned up test repository")


def test_project_git_integration():
    """Test Project Git integration."""
    print("\n" + "=" * 60)
    print("Testing Project Git Integration")
    print("=" * 60)
    
    projects_metadata_dir = Path("D:/pyMM/test_projects/.metadata")
    project_path = Path("D:/pyMM/test_projects/git_integration_test")
    
    # Clean up if exists
    if project_path.exists():
        shutil.rmtree(project_path)
    
    service = ProjectService(projects_metadata_dir)
    
    try:
        # Create project with Git
        print("\n✓ Creating project with Git enabled")
        project = service.create_project(
            name="Git Integration Test",
            path=project_path,
            description="Testing Git integration",
            git_enabled=True,
            use_template="default",
        )
        
        # Initialize Git
        success = service.init_git_repository(project, initial_commit=True)
        assert success
        print(f"✓ Initialized Git repository for project")
        
        # Check Git status
        status = service.get_git_status(project)
        assert status is not None
        print(f"✓ Got Git status: {status['branch']}")
        
        # Make changes
        test_file = project_path / "media" / "test.txt"
        test_file.write_text("Test media file")
        print(f"✓ Created test file in project")
        
        # Check status
        status = service.get_git_status(project)
        assert status['total_changes'] > 0
        print(f"✓ Detected changes: {status['total_changes']} files")
        
        # Commit changes
        success = service.commit_changes(
            project,
            "Add test media file",
            add_all=True,
        )
        assert success
        print(f"✓ Committed changes to project")
        
        # Get log
        log = service.get_git_log(project, max_count=5)
        assert len(log) >= 2
        print(f"✓ Retrieved commit log: {len(log)} commits")
        for commit in log:
            print(f"  - {commit['sha']}: {commit['message'][:50]}")
        
        # Clean status check
        status = service.get_git_status(project)
        assert status['total_changes'] == 0
        print(f"✓ Repository is clean after commit")
        
        print("\n✅ Project Git integration tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        # Clean up
        if project_path.exists():
            try:
                import stat
                def remove_readonly(func, path, _):
                    """Clear the readonly bit and reattempt the removal"""
                    Path(path).chmod(stat.S_IWRITE)
                    func(path)
                
                shutil.rmtree(project_path, onerror=remove_readonly)
            except Exception as e:
                print(f"Warning: Could not clean up project: {e}")
        metadata_file = service._get_metadata_file(project_path)
        if metadata_file.exists():
            metadata_file.unlink()
        print(f"✓ Cleaned up test project")


if __name__ == "__main__":
    print("=" * 60)
    print("Git Integration Test")
    print("=" * 60)
    
    try:
        test_git_service()
        test_project_git_integration()
        
        print("\n" + "=" * 60)
        print("All tests complete!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
