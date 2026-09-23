"""OpenWorker Harness for Multi-Agent Orchestration.

Manages agent lifecycles, dedicated workspaces, concurrent execution,
and safe resource cleanup.
"""

from pathlib import Path
import shutil
from typing import Any

from app.core.logging import logger
from app.openworker.agent import OpenWorkerAgent


class OpenWorkerHarness:
    """Manages creation, execution, and discovery of multiple OpenWorker agents."""

    def __init__(self, base_workspace_dir: str | Path | None = None) -> None:
        self.base_dir = Path(base_workspace_dir or "./data/openworker_workspaces")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._agents: dict[str, OpenWorkerAgent] = {}

    def create_agent(
        self,
        agent_id: str | None = None,
        role: str = "Research & Knowledge Specialist",
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> OpenWorkerAgent:
        """Create and register a new OpenWorkerAgent."""
        agent = OpenWorkerAgent(
            agent_id=agent_id,
            role=role,
            workspace_dir=self.base_dir,
            system_instruction=system_instruction,
            **kwargs,
        )
        self._agents[agent.agent_id] = agent
        logger.info("OpenWorkerHarness registered agent: %s (%s)", agent.agent_id, role)
        return agent

    def get_agent(self, agent_id: str) -> OpenWorkerAgent | None:
        """Retrieve an active in-memory agent by ID."""
        return self._agents.get(agent_id)

    def get_or_create_agent(
        self,
        agent_id: str,
        role: str = "Research & Knowledge Specialist",
        **kwargs: Any,
    ) -> OpenWorkerAgent:
        """Get an existing agent or create a new one with the given ID."""
        if agent_id in self._agents:
            return self._agents[agent_id]
        return self.create_agent(agent_id=agent_id, role=role, **kwargs)

    def list_agents(self) -> list[dict[str, Any]]:
        """List all active agents and their status."""
        result = []
        for aid, ag in self._agents.items():
            result.append({
                "agent_id": aid,
                "role": ag.role,
                "workspace": str(ag.workspace_path),
                "collections_prefix": ag.kb.collection_prefix,
                "documents_count": len(ag.kb.list_documents()),
            })
        return result

    def delete_agent(self, agent_id: str) -> bool:
        """Tear down agent and remove its private database and storage files."""
        if agent_id in self._agents:
            agent = self._agents[agent_id]
            agent.close()
            del self._agents[agent_id]

        target_dir = self.base_dir / agent_id
        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)
            logger.info("Deleted workspace for agent: %s", agent_id)
            return True
        return False

    def close_all(self) -> None:
        """Dispose all open agent database engines."""
        for agent in list(self._agents.values()):
            agent.close()
        self._agents.clear()
        logger.info("Closed all OpenWorker agents in harness.")


# Global default harness instance
_default_harness: OpenWorkerHarness | None = None


def get_harness() -> OpenWorkerHarness:
    """Retrieve or initialize the global OpenWorkerHarness singleton."""
    global _default_harness
    if _default_harness is None:
        _default_harness = OpenWorkerHarness()
    return _default_harness
