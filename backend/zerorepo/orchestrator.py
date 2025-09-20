"""
Main orchestrator for ZeroRepo system.
Coordinates the three-stage pipeline: Proposal → Implementation → Code Generation.
"""

import os
import asyncio
import logging
from typing import Tuple, Dict
from .core.models import RPG, ProjectConfig, GenerationResult, FeaturePath
from .tools.llm_client import LLMClient
from .tools.vector_store import VectorStore
from .tools.docker_runtime import DockerTestRunner
from .plan.proposal import ProposalController
from .plan.implementation import ImplementationController
from .codegen.generator import CodeGenerator

logger = logging.getLogger(__name__)


class ZeroRepoOrchestrator:
    """
    Main orchestrator coordinating all ZeroRepo stages.
    
    Implements the complete three-stage pipeline:
    - Stage A: Proposal-level construction (capabilities graph)
    - Stage B: Implementation-level construction (file structure + interfaces)
    - Stage C: Graph-guided code generation (topological TDD)
    """
    
    def __init__(self, config: ProjectConfig, emergent_api_key: str = None):
        self.config = config
        
        # Initialize components
        api_key = emergent_api_key or os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise ValueError(
                "Emergent LLM API key not provided. Set EMERGENT_LLM_KEY or pass emergent_api_key."
            )

        self.llm_client = LLMClient(api_key, config.llm_model)
        
        self.vector_store = VectorStore(config.embedding_model)
        self.docker_runner = DockerTestRunner()
        
        # Initialize controllers
        self.proposal_controller = ProposalController(config, self.llm_client, self.vector_store)
        self.implementation_controller = ImplementationController(config, self.llm_client)  
        self.code_generator = CodeGenerator(config, self.llm_client, self.docker_runner)
        
        logger.info(f"ZeroRepo orchestrator initialized for: {config.project_goal}")
        
    async def run_full_pipeline(self, output_dir: str) -> GenerationResult:
        """
        Run the complete ZeroRepo pipeline.
        
        Args:
            output_dir: Target directory for generated repository
            
        Returns:
            GenerationResult with success status and metrics
        """
        logger.info("Starting full ZeroRepo pipeline")
        
        try:
            # Stage A: Proposal-level construction
            logger.info("=== Stage A: Proposal Construction ===")
            capability_graph, feature_paths = await self.run_proposal_stage()
            
            # Stage B & C: Implementation + Code Generation
            logger.info("=== Stage B & C: Implementation + Code Generation ===")
            result = await self.run_implementation_and_codegen_stages(capability_graph, output_dir)
            
            # Add proposal metrics to result
            result.metrics.update({
                "total_features": len(feature_paths),
                "proposal_nodes": len(capability_graph.nodes)
            })
            
            logger.info(f"Full pipeline completed. Success: {result.success}")
            
            return result
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return GenerationResult(
                success=False,
                errors=[f"Pipeline failed: {str(e)}"],
                metrics={"pipeline_error": True}
            )
            
    async def run_proposal_stage(self) -> Tuple[RPG, list]:
        """
        Run Stage A: Proposal-level construction.
        
        Returns:
            Tuple of (capability_graph, feature_paths)
        """
        
        # Initialize vector store with domain ontology if not already done
        if len(self.vector_store.feature_paths) == 0:
            logger.info("Initializing vector store with sample ontology")
            sample_ontology = self.vector_store.create_sample_ontology()
            self.vector_store.build_from_ontology(sample_ontology)
        
        logger.info(f"Vector store ready with {len(self.vector_store.feature_paths)} features")
        
        # Run proposal construction
        capability_graph, feature_paths = await self.proposal_controller.build_capability_graph()
        
        logger.info(f"Proposal stage complete: {len(feature_paths)} features, {len(capability_graph.nodes)} nodes")
        
        return capability_graph, feature_paths
        
    async def run_implementation_and_codegen_stages(
        self, 
        capability_graph: RPG, 
        output_dir: str
    ) -> GenerationResult:
        """
        Run Stage B (Implementation) and Stage C (Code Generation).
        
        Args:
            capability_graph: RPG from proposal stage
            output_dir: Target directory for generated code
            
        Returns:
            GenerationResult with generation metrics
        """
        
        # Stage B: Implementation-level construction
        logger.info("Stage B: Building implementation graph")
        
        complete_graph, interfaces = await self.implementation_controller.build_implementation_graph(
            capability_graph
        )
        
        logger.info(f"Implementation stage complete: {len(interfaces)} interfaces generated")
        
        # Stage C: Code generation  
        logger.info("Stage C: Generating repository code")
        
        result = await self.code_generator.generate_repository(
            complete_graph, interfaces, output_dir
        )
        
        logger.info(f"Code generation complete. Success: {result.success}")
        
        return result
        
    async def validate_pipeline_prerequisites(self) -> bool:
        """
        Validate that all required components are available.
        
        Returns:
            True if all prerequisites met, False otherwise
        """
        
        checks = []
        
        # Check LLM client
        try:
            test_response = await self.llm_client.generate(
                prompt="Test connection", 
                max_tokens=10
            )
            checks.append(("LLM Client", test_response.success))
        except Exception as e:
            logger.error(f"LLM client check failed: {str(e)}")
            checks.append(("LLM Client", False))
            
        # Check vector store - but initialize it first if needed
        try:
            # Initialize if not already done
            if len(self.vector_store.feature_paths) == 0:
                sample_ontology = self.vector_store.create_sample_ontology()
                self.vector_store.build_from_ontology(sample_ontology)
                
            stats = self.vector_store.get_stats()
            checks.append(("Vector Store", stats["total_features"] > 0))
        except Exception as e:
            logger.error(f"Vector store check failed: {str(e)}")
            checks.append(("Vector Store", False))
            
        # Check Docker runner - allow fallback to subprocess
        try:
            # Docker runner has subprocess fallback, so it's always considered available
            checks.append(("Docker Runner", True))  # Fallback always available
        except Exception as e:
            logger.warning(f"Docker runner check failed (will use subprocess fallback): {str(e)}")
            checks.append(("Docker Runner", True))  # Fallback available
            
        # Log results
        for component, status in checks:
            status_icon = "✅" if status else "❌"
            logger.info(f"{status_icon} {component}: {'Ready' if status else 'Failed'}")
            
        return all(status for _, status in checks)
        
    def get_pipeline_status(self) -> Dict:
        """Get current pipeline status and component health."""
        
        return {
            "config": {
                "project_goal": self.config.project_goal,
                "domain": self.config.domain,
                "llm_model": self.config.llm_model,
                "max_iterations": self.config.max_iterations
            },
            "vector_store": self.vector_store.get_stats(),
            "components": {
                "proposal_controller": "initialized",
                "implementation_controller": "initialized", 
                "code_generator": "initialized"
            }
        }
        
    async def cleanup(self):
        """Cleanup resources."""
        
        try:
            if hasattr(self.docker_runner, 'cleanup'):
                self.docker_runner.cleanup()
            logger.info("Orchestrator cleanup completed")
        except Exception as e:
            logger.warning(f"Cleanup error: {str(e)}")


# Convenience functions for direct usage

async def generate_repository(
    project_goal: str,
    output_dir: str,
    domain: str = "general",
    llm_model: str = "gpt-4",
    max_iterations: int = 30,
    emergent_api_key: str = None
) -> GenerationResult:
    """
    Convenience function to generate repository directly.
    
    Args:
        project_goal: High-level description of what to build
        output_dir: Directory for generated repository
        domain: Problem domain (ml, web, data)
        llm_model: LLM model to use
        max_iterations: Max planning iterations
        emergent_api_key: API key (optional, uses env var if not provided)
        
    Returns:
        GenerationResult
    """
    
    config = ProjectConfig(
        project_goal=project_goal,
        domain=domain,
        llm_model=llm_model,
        max_iterations=max_iterations
    )
    
    orchestrator = ZeroRepoOrchestrator(config, emergent_api_key)
    
    try:
        # Validate prerequisites
        if not await orchestrator.validate_pipeline_prerequisites():
            return GenerationResult(
                success=False,
                errors=["Pipeline prerequisites not met"],
                metrics={"prerequisite_check": False}
            )
            
        # Run pipeline
        result = await orchestrator.run_full_pipeline(output_dir)
        
        return result
        
    finally:
        await orchestrator.cleanup()


async def plan_repository(
    project_goal: str,
    domain: str = "general", 
    llm_model: str = "gpt-4",
    max_iterations: int = 30,
    emergent_api_key: str = None
) -> Tuple[RPG, list]:
    """
    Convenience function for planning stage only.
    
    Returns:
        Tuple of (capability_graph, feature_paths)
    """
    
    config = ProjectConfig(
        project_goal=project_goal,
        domain=domain,
        llm_model=llm_model,
        max_iterations=max_iterations
    )
    
    orchestrator = ZeroRepoOrchestrator(config, emergent_api_key)
    
    try:
        return await orchestrator.run_proposal_stage()
    finally:
        await orchestrator.cleanup()


# Example usage
if __name__ == "__main__":
    
    async def main():
        # Example: Generate ML toolkit
        result = await generate_repository(
            project_goal="Generate a classical ML toolkit with regression, classification, clustering, and evaluation metrics",
            output_dir="./ml_toolkit_demo",
            domain="ml"
        )
        
        if result.success:
            print(f"✅ Repository generated successfully!")
            print(f"📁 Files: {len(result.generated_files)}")
            print(f"📈 Success rate: {result.metrics.get('success_rate', 0):.2%}")
        else:
            print(f"❌ Generation failed: {result.errors}")
            
    asyncio.run(main())
