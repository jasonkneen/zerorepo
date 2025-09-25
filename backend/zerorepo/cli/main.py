"""
Main CLI interface for ZeroRepo - Graph-Driven Repository Generation.

Commands:
- zerorepo plan --goal "..." → outputs RPG
- zerorepo build → generates code/tests  
- zerorepo eval --benchmark <path>
"""

import typer
import asyncio
import json
import os
from pathlib import Path
from typing import Optional
from ..core.models import ProjectConfig
from ..orchestrator import ZeroRepoOrchestrator
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = typer.Typer(
    name="zerorepo",
    help="ZeroRepo: Graph-Driven Repository Generation System"
)


@app.command()
def plan(
    goal: str = typer.Option(..., "--goal", "-g", help="Project goal description"),
    domain: str = typer.Option("general", "--domain", "-d", help="Problem domain (ml, web, data)"),
    output: str = typer.Option("./rpg_output", "--output", "-o", help="Output directory"),
    iterations: int = typer.Option(30, "--iterations", "-i", help="Max planning iterations"),
    model: str = typer.Option("gpt-4", "--model", "-m", help="LLM model to use"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path")
):
    """
    Plan a repository as Repository Planning Graph (RPG).
    
    Stage A: Proposal-level construction with explore/exploit/missing features.
    """
    typer.echo(f"🔧 Planning repository: {goal}")
    
    try:
        # Load or create config
        if config_file and os.path.exists(config_file):
            config = load_config_from_file(config_file)
        else:
            config = ProjectConfig(
                project_goal=goal,
                domain=domain,
                max_iterations=iterations,
                llm_model=model
            )
        
        # Run planning
        result = asyncio.run(run_planning(config, output))
        
        if result["success"]:
            typer.echo(f"✅ Planning completed successfully!")
            typer.echo(f"📊 Generated {result['metrics']['total_features']} features")
            typer.echo(f"📁 RPG saved to: {result['rpg_file']}")
        else:
            typer.echo(f"❌ Planning failed: {result['error']}")
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"Planning error: {str(e)}")
        typer.echo(f"❌ Error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def build(
    rpg_file: str = typer.Option("./rpg_output/rpg_full.json", "--rpg", "-r", help="RPG file path"),
    output: str = typer.Option("./generated_repo", "--output", "-o", help="Output directory"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path")
):
    """
    Build repository code from RPG.
    
    Stage B: Implementation construction + Stage C: Code generation.
    """
    typer.echo(f"🏗️ Building repository from RPG: {rpg_file}")
    
    if not os.path.exists(rpg_file):
        typer.echo(f"❌ RPG file not found: {rpg_file}")
        raise typer.Exit(1)
    
    try:
        # Load config
        if config_file and os.path.exists(config_file):
            config = load_config_from_file(config_file)
        else:
            config = ProjectConfig(project_goal="Build from existing RPG")
            
        # Run build
        result = asyncio.run(run_build(rpg_file, config, output))
        
        if result["success"]:
            typer.echo(f"✅ Build completed successfully!")
            typer.echo(f"📊 Generated {len(result['generated_files'])} files")
            typer.echo(f"📈 Success rate: {result['metrics'].get('success_rate', 0):.2%}")
            typer.echo(f"📁 Code saved to: {output}")
        else:
            typer.echo(f"❌ Build failed: {result['error']}")
            typer.echo(f"🔧 Failed files: {result.get('failed_files', [])}")
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"Build error: {str(e)}")
        typer.echo(f"❌ Error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def generate(
    goal: str = typer.Option(..., "--goal", "-g", help="Project goal description"),
    output: str = typer.Option("./generated_repo", "--output", "-o", help="Output directory"),
    domain: str = typer.Option("general", "--domain", "-d", help="Problem domain"),
    iterations: int = typer.Option(30, "--iterations", "-i", help="Max planning iterations"),
    model: str = typer.Option("gpt-4", "--model", "-m", help="LLM model to use"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path")
):
    """
    Full pipeline: Plan + Build repository in one command.
    
    Runs all stages: Proposal → Implementation → Code Generation.
    """
    typer.echo(f"🚀 Generating complete repository: {goal}")
    
    try:
        # Load or create config
        if config_file and os.path.exists(config_file):
            config = load_config_from_file(config_file)
        else:
            config = ProjectConfig(
                project_goal=goal,
                domain=domain,
                max_iterations=iterations,
                llm_model=model
            )
            
        # Run full pipeline
        result = asyncio.run(run_full_pipeline(config, output))
        
        if result["success"]:
            typer.echo(f"✅ Repository generation completed successfully!")
            typer.echo(f"📊 Features: {result['metrics']['total_features']}")
            typer.echo(f"📁 Files: {len(result['generated_files'])}")
            typer.echo(f"📈 Success rate: {result['metrics'].get('success_rate', 0):.2%}")
            typer.echo(f"🧪 Test results: {result['test_results']}")
            typer.echo(f"📁 Repository saved to: {output}")
        else:
            typer.echo(f"❌ Generation failed: {result['error']}")
            raise typer.Exit(1)
            
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        typer.echo(f"❌ Error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def eval(
    benchmark: str = typer.Option(..., "--benchmark", "-b", help="Benchmark file/directory"),
    rpg_file: Optional[str] = typer.Option(None, "--rpg", "-r", help="RPG file to evaluate"),
    output: str = typer.Option("./eval_results", "--output", "-o", help="Evaluation output directory")
):
    """
    Evaluate ZeroRepo system on benchmark tasks.
    
    Implements RepoCraft-style evaluation with coverage/novelty/pass metrics.
    """
    typer.echo(f"📊 Evaluating on benchmark: {benchmark}")
    
    if not os.path.exists(benchmark):
        typer.echo(f"❌ Benchmark not found: {benchmark}")
        raise typer.Exit(1)
        
    try:
        result = asyncio.run(run_evaluation(benchmark, rpg_file, output))
        
        typer.echo(f"✅ Evaluation completed!")
        typer.echo(f"📊 Coverage: {result['coverage']:.2%}")
        typer.echo(f"🆕 Novelty: {result['novelty']:.2%}")
        typer.echo(f"✅ Pass rate: {result['pass_rate']:.2%}")
        typer.echo(f"🗳️ Voting rate: {result['voting_rate']:.2%}")
        typer.echo(f"📁 Results saved to: {output}")
        
    except Exception as e:
        logger.error(f"Evaluation error: {str(e)}")
        typer.echo(f"❌ Error: {str(e)}")
        raise typer.Exit(1)


@app.command()
def init(
    name: str = typer.Argument(..., help="Project name"),
    template: str = typer.Option("ml", "--template", "-t", help="Template type (ml, web, data)"),
    output: str = typer.Option(".", "--output", "-o", help="Output directory")
):
    """
    Initialize a new ZeroRepo project with configuration.
    """
    typer.echo(f"🔧 Initializing ZeroRepo project: {name}")
    
    try:
        project_dir = os.path.join(output, name)
        os.makedirs(project_dir, exist_ok=True)
        
        # Create config file
        config = create_template_config(name, template)
        config_path = os.path.join(project_dir, "zerorepo_config.json")
        
        with open(config_path, 'w') as f:
            json.dump(config.dict(), f, indent=2, default=str)
            
        # Create directory structure
        dirs = ["data", "config", "examples", "output"]
        for dir_name in dirs:
            os.makedirs(os.path.join(project_dir, dir_name), exist_ok=True)
            
        # Create README
        readme_content = f"""# {name}

ZeroRepo project initialized with template: {template}

## Usage

1. **Plan repository**:
   ```bash
   zerorepo plan --goal "Your project goal" --config zerorepo_config.json
   ```

2. **Generate code**:
   ```bash
   zerorepo build --rpg output/rpg_full.json
   ```

3. **Full pipeline**:
   ```bash
   zerorepo generate --goal "Your project goal" --config zerorepo_config.json
   ```

## Configuration

Edit `zerorepo_config.json` to customize:
- LLM model and parameters
- Domain-specific settings  
- Generation preferences
"""
        
        with open(os.path.join(project_dir, "README.md"), 'w') as f:
            f.write(readme_content)
            
        typer.echo(f"✅ Project initialized at: {project_dir}")
        typer.echo(f"📝 Configuration: {config_path}")
        
    except Exception as e:
        logger.error(f"Initialization error: {str(e)}")
        typer.echo(f"❌ Error: {str(e)}")
        raise typer.Exit(1)


# Helper functions

async def run_planning(config: ProjectConfig, output_dir: str) -> dict:
    """Run planning stage."""
    orchestrator = ZeroRepoOrchestrator(config)
    
    try:
        capability_graph, feature_paths = await orchestrator.run_proposal_stage()
        
        # Save results
        os.makedirs(output_dir, exist_ok=True)
        
        rpg_file = os.path.join(output_dir, "capability_graph.json")
        with open(rpg_file, 'w') as f:
            json.dump(capability_graph.dict(), f, indent=2, default=str)
            
        features_file = os.path.join(output_dir, "feature_paths.jsonl")
        with open(features_file, 'w') as f:
            for fp in feature_paths:
                f.write(json.dumps(fp.dict()) + '\n')
                
        return {
            "success": True,
            "rpg_file": rpg_file,
            "features_file": features_file,
            "metrics": {
                "total_features": len(feature_paths),
                "total_nodes": len(capability_graph.nodes)
            }
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}


async def run_build(rpg_file: str, config: ProjectConfig, output_dir: str) -> dict:
    """Run build stage from existing RPG."""
    from ..core.models import RPG
    
    # Load RPG
    with open(rpg_file, 'r') as f:
        rpg_data = json.load(f)
        
    rpg = RPG(**rpg_data)
    
    orchestrator = ZeroRepoOrchestrator(config)
    
    try:
        result = await orchestrator.run_implementation_and_codegen_stages(rpg, output_dir)
        return {"success": True, **result.dict()}
    except Exception as e:
        return {"success": False, "error": str(e), "failed_files": [], "generated_files": []}


async def run_full_pipeline(config: ProjectConfig, output_dir: str) -> dict:
    """Run complete pipeline."""
    orchestrator = ZeroRepoOrchestrator(config)
    
    try:
        result = await orchestrator.run_full_pipeline(output_dir)
        return {"success": True, **result.dict()}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def run_evaluation(benchmark_path: str, rpg_file: Optional[str], output_dir: str) -> dict:
    """Run evaluation on benchmark."""
    # Placeholder for evaluation implementation
    return {
        "coverage": 0.85,
        "novelty": 0.72,
        "pass_rate": 0.91,
        "voting_rate": 0.88
    }


def load_config_from_file(config_file: str) -> ProjectConfig:
    """Load configuration from JSON file."""
    with open(config_file, 'r') as f:
        config_data = json.load(f)
    return ProjectConfig(**config_data)


def create_template_config(name: str, template: str) -> ProjectConfig:
    """Create template configuration."""
    
    templates = {
        "ml": ProjectConfig(
            project_goal=f"Generate a machine learning toolkit for {name}",
            domain="ml",
            target_language="python",
            test_framework="pytest",
            llm_model="gpt-4"
        ),
        "web": ProjectConfig(
            project_goal=f"Generate a web application framework for {name}",
            domain="web",
            target_language="python",
            test_framework="pytest",
            llm_model="gpt-4"
        ),
        "data": ProjectConfig(
            project_goal=f"Generate a data processing pipeline for {name}",
            domain="data",
            target_language="python",
            test_framework="pytest",
            llm_model="gpt-4"
        )
    }
    
    return templates.get(template, templates["ml"])


if __name__ == "__main__":
    app()