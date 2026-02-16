"""Tests for workspace management."""
import pytest
from pathlib import Path

from pipeline.workspace import (
    create_workspace,
    get_next_build_number,
    get_workspace,
    list_workspaces,
    delete_workspace,
    WORKSPACES_BASE,
)


class TestWorkspaceManagement:
    """Tests for workspace creation and management."""

    @pytest.fixture
    def temp_base(self, tmp_path):
        """Use a temporary directory for workspaces."""
        return tmp_path / "workspaces"

    def test_get_next_build_number_empty(self, temp_base):
        """Test build number generation with no existing workspaces."""
        assert get_next_build_number(temp_base) == 1

    def test_get_next_build_number_with_existing(self, temp_base):
        """Test build number generation with existing workspaces."""
        temp_base.mkdir()
        (temp_base / "00001").mkdir()
        (temp_base / "00002").mkdir()

        assert get_next_build_number(temp_base) == 3

    def test_create_workspace(self, temp_base):
        """Test workspace creation."""
        ws = create_workspace(base_dir=temp_base)

        assert ws.workspace_id == "00001"
        assert ws.workspace_path.exists()
        assert ws.project_dir.exists()
        assert ws.context_dir.exists()
        assert ws.state_dir.exists()
        assert ws.logs_dir.exists()

    def test_create_workspace_auto_increment(self, temp_base):
        """Test workspace IDs auto-increment."""
        ws1 = create_workspace(base_dir=temp_base)
        ws2 = create_workspace(base_dir=temp_base)

        assert ws1.workspace_id == "00001"
        assert ws2.workspace_id == "00002"

    def test_create_workspace_duplicate_fails(self, temp_base):
        """Test that creating duplicate workspace fails."""
        create_workspace(build_number=1, base_dir=temp_base)

        with pytest.raises(ValueError, match="already exists"):
            create_workspace(build_number=1, base_dir=temp_base)

    def test_get_workspace(self, temp_base):
        """Test retrieving existing workspace."""
        ws_created = create_workspace(base_dir=temp_base)
        ws_retrieved = get_workspace(ws_created.workspace_id, base_dir=temp_base)

        assert ws_retrieved.workspace_id == ws_created.workspace_id
        assert ws_retrieved.workspace_path == ws_created.workspace_path

    def test_get_workspace_not_found(self, temp_base):
        """Test retrieving non-existent workspace."""
        with pytest.raises(FileNotFoundError):
            get_workspace("99999", base_dir=temp_base)

    def test_list_workspaces(self, temp_base):
        """Test listing all workspaces."""
        ws1 = create_workspace(base_dir=temp_base)
        ws2 = create_workspace(base_dir=temp_base)

        workspaces = list_workspaces(base_dir=temp_base)

        assert len(workspaces) == 2
        # Should be sorted by creation time (newest first)
        assert workspaces[0].workspace_id == "00002"
        assert workspaces[1].workspace_id == "00001"

    def test_list_workspaces_empty(self, temp_base):
        """Test listing with no workspaces."""
        workspaces = list_workspaces(base_dir=temp_base)
        assert workspaces == []

    def test_delete_workspace(self, temp_base):
        """Test workspace deletion."""
        ws = create_workspace(base_dir=temp_base)
        assert ws.workspace_path.exists()

        delete_workspace(ws.workspace_id, base_dir=temp_base)
        assert not ws.workspace_path.exists()

    def test_delete_workspace_not_found(self, temp_base):
        """Test deleting non-existent workspace."""
        with pytest.raises(FileNotFoundError):
            delete_workspace("99999", base_dir=temp_base)
