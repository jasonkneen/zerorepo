from fastapi import FastAPI, APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import asyncio

# ZeroRepo imports
from zerorepo.orchestrator import ZeroRepoOrchestrator, generate_repository, plan_repository
from zerorepo.core.models import ProjectConfig, GenerationResult


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="ZeroRepo API", description="Graph-Driven Repository Generation System")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# ZeroRepo API Models
class GenerateRepositoryRequest(BaseModel):
    project_goal: str = Field(..., description="High-level project objective")
    domain: str = Field("general", description="Problem domain (ml, web, data, etc.)")
    llm_model: str = Field("gpt-4", description="LLM model to use")
    max_iterations: int = Field(30, description="Maximum planning iterations")
    target_language: str = Field("python", description="Programming language")

class PlanRepositoryRequest(BaseModel):
    project_goal: str = Field(..., description="High-level project objective") 
    domain: str = Field("general", description="Problem domain")
    llm_model: str = Field("gpt-4", description="LLM model to use")
    max_iterations: int = Field(30, description="Maximum planning iterations")

class GenerationJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = Field("pending", description="Job status: pending, running, completed, failed")
    project_goal: str
    domain: str
    progress: int = Field(0, description="Progress percentage 0-100")
    current_stage: str = Field("Initializing", description="Current processing stage")
    current_file: Optional[str] = Field(None, description="Currently processing file")
    generated_files: List[str] = Field(default_factory=list, description="List of generated files")
    files_in_progress: List[str] = Field(default_factory=list, description="Files currently being worked on")
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Basic endpoints
@api_router.get("/")
async def root():
    return {"message": "ZeroRepo API - Graph-Driven Repository Generation"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# ZeroRepo API Endpoints

@api_router.post("/zerorepo/generate", response_model=dict)
async def generate_repository_endpoint(
    request: GenerateRepositoryRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a complete repository using ZeroRepo system.
    Returns job ID for tracking progress.
    """
    try:
        # Create job record
        job = GenerationJob(
            project_goal=request.project_goal,
            domain=request.domain,
            status="pending"
        )
        
        # Store in database
        await db.generation_jobs.insert_one(job.dict())
        
        # Start background task
        background_tasks.add_task(
            run_generation_job,
            job.id,
            request
        )
        
        return {
            "job_id": job.id,
            "status": "pending",
            "message": "Repository generation started",
            "project_goal": request.project_goal
        }
        
    except Exception as e:
        logging.error(f"Error starting generation job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start generation: {str(e)}")

@api_router.post("/zerorepo/plan", response_model=dict)
async def plan_repository_endpoint(request: PlanRepositoryRequest):
    """
    Plan a repository (Stage A only) - returns RPG and feature paths.
    Optimized for real LLM performance.
    """
    try:
        logging.info(f"Planning repository: {request.project_goal}")
        
        # Use faster model and fewer iterations for better UX
        actual_model = "gpt-4o-mini" if request.llm_model == "gpt-4" else request.llm_model
        actual_iterations = min(request.max_iterations, 3)  # Cap at 3 for speed
        
        logging.info(f"Using model {actual_model} with {actual_iterations} iterations for speed")
        
        # Run planning
        capability_graph, feature_paths = await plan_repository(
            project_goal=request.project_goal,
            domain=request.domain,
            llm_model=actual_model,
            max_iterations=actual_iterations,
            emergent_api_key=os.environ.get('EMERGENT_LLM_KEY', 'sk-emergent-b99311bB564934e547')
        )
        
        return {
            "success": True,
            "capability_graph": capability_graph.dict(),
            "feature_paths": [fp.dict() for fp in feature_paths],
            "metrics": {
                "total_features": len(feature_paths),
                "total_nodes": len(capability_graph.nodes),
                "total_edges": len(capability_graph.edges)
            },
            "optimization_info": {
                "model_used": actual_model,
                "iterations_used": actual_iterations,
                "original_iterations": request.max_iterations
            }
        }
        
    except Exception as e:
        logging.error(f"Planning error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")

@api_router.get("/zerorepo/jobs/{job_id}")
async def get_generation_job(job_id: str):
    """Get status and results of a generation job."""
    try:
        job = await db.generation_jobs.find_one({"id": job_id})
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
            
        return {
            "id": job["id"],
            "status": job["status"],
            "project_goal": job["project_goal"],
            "domain": job["domain"],
            "progress": job["progress"],
            "current_stage": job.get("current_stage", "Unknown"),
            "current_file": job.get("current_file"),
            "generated_files": job.get("generated_files", []),
            "files_in_progress": job.get("files_in_progress", []),
            "result": job.get("result"),
            "error": job.get("error"),
            "created_at": job["created_at"],
            "updated_at": job["updated_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error fetching job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch job status")

@api_router.get("/zerorepo/jobs")
async def list_generation_jobs(limit: int = 20, skip: int = 0):
    """List recent generation jobs."""
    try:
        jobs = await db.generation_jobs.find().sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        
        return {
            "jobs": [
                {
                    "id": job["id"],
                    "status": job["status"], 
                    "project_goal": job["project_goal"],
                    "domain": job["domain"],
                    "progress": job["progress"],
                    "created_at": job["created_at"]
                }
                for job in jobs
            ],
            "total": len(jobs)
        }
        
    except Exception as e:
        logging.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list jobs")

@api_router.post("/zerorepo/quick-demo")
async def quick_demo():
    """
    Quick demo endpoint - OPTIMIZED for speed with minimal real AI calls.
    """
    try:
        # Use a simple, fast example with minimal processing
        demo_goal = "Generate a basic math calculator with add and subtract functions"
        
        logging.info("Starting OPTIMIZED ZeroRepo quick demo")
        
        # Ultra-minimal config for speed
        config = ProjectConfig(
            project_goal=demo_goal,
            domain="general",  # Changed from "ml" to "general" for simpler processing
            max_iterations=1,  # Just 1 iteration for speed
            llm_model="gpt-4o-mini"  # Fastest model
        )
        
        # Run only the proposal stage (fastest)
        orchestrator = ZeroRepoOrchestrator(
            config,
            emergent_api_key=os.environ.get('EMERGENT_LLM_KEY', 'sk-emergent-b99311bB564934e547')
        )
        
        capability_graph, feature_paths = await orchestrator.run_proposal_stage()
        
        await orchestrator.cleanup()
        
        return {
            "success": True,
            "demo_goal": demo_goal,
            "features_generated": len(feature_paths),
            "nodes_in_graph": len(capability_graph.nodes),
            "sample_features": [fp.path for fp in feature_paths[:8]],
            "message": "Quick demo completed - ZeroRepo AI is working perfectly!",
            "optimization": "Ultra-fast demo: 1 iteration, general domain, minimal processing",
            "performance_note": "Full generation available on the Generate page"
        }
        
    except Exception as e:
        logging.error(f"Demo error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Demo encountered an error",
            "features_generated": 0,
            "nodes_in_graph": 0
        }

# Background task functions

async def run_generation_job(job_id: str, request: GenerateRepositoryRequest):
    """Background task to run repository generation with detailed progress updates."""
    try:
        # Update status to running
        await db.generation_jobs.update_one(
            {"id": job_id},
            {
                "$set": {
                    "status": "running",
                    "progress": 5,
                    "current_stage": "Initializing",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Create output directory
        output_dir = f"/tmp/zerorepo_output/{job_id}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Stage A: Proposal Construction
        await db.generation_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 15, "current_stage": "Stage A: Planning Repository Structure", "updated_at": datetime.utcnow()}}
        )
        
        config = ProjectConfig(
            project_goal=request.project_goal,
            domain=request.domain,
            llm_model=request.llm_model,
            max_iterations=min(request.max_iterations, 3)  # Cap for speed
        )
        
        orchestrator = ZeroRepoOrchestrator(
            config,
            emergent_api_key=os.environ.get('EMERGENT_LLM_KEY', 'sk-emergent-b99311bB564934e547')
        )
        
        # Proposal stage with progress updates
        await db.generation_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 25, "current_stage": "Stage A: Analyzing Features with AI", "updated_at": datetime.utcnow()}}
        )
        
        capability_graph, feature_paths = await orchestrator.run_proposal_stage()
        
        await db.generation_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 50, "current_stage": f"Stage A Complete: {len(feature_paths)} features planned", "updated_at": datetime.utcnow()}}
        )
        
        # Stage B: Implementation  
        await db.generation_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 60, "current_stage": "Stage B: Designing File Structure", "updated_at": datetime.utcnow()}}
        )
        
        complete_graph, interfaces = await orchestrator.implementation_controller.build_implementation_graph(capability_graph)
        
        await db.generation_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 75, "current_stage": f"Stage B Complete: {len(interfaces)} interfaces designed", "updated_at": datetime.utcnow()}}
        )
        
        # Stage C: Code Generation
        await db.generation_jobs.update_one(
            {"id": job_id},
            {"$set": {"progress": 85, "current_stage": "Stage C: Generating Code with AI", "updated_at": datetime.utcnow()}}
        )
        
        result = await orchestrator.code_generator.generate_repository(
            complete_graph, interfaces, output_dir
        )
        
        # Final results
        await db.generation_jobs.update_one(
            {"id": job_id},
            {
                "$set": {
                    "status": "completed" if result.success else "failed",
                    "progress": 100,
                    "current_stage": "Complete" if result.success else "Failed",
                    "result": result.dict() if result.success else None,
                    "error": result.errors[0] if result.errors else None,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        await orchestrator.cleanup()
        logging.info(f"Generation job {job_id} completed: {result.success}")
        
    except Exception as e:
        logging.error(f"Generation job {job_id} failed: {str(e)}")
        
        # Update with error
        await db.generation_jobs.update_one(
            {"id": job_id},
            {
                "$set": {
                    "status": "failed",
                    "progress": 100,
                    "current_stage": "Failed",
                    "error": str(e),
                    "updated_at": datetime.utcnow()
                }
            }
        )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Health check endpoint for ZeroRepo
@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ZeroRepo API",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }

@api_router.get("/test-models")
async def test_models():
    """Simple test endpoint."""
    return {"test": "models endpoint working"}

@api_router.get("/models")
async def get_available_models():
    """Get available models for each provider."""
    return {
        "openai": [
            {"id": "gpt-4o", "name": "GPT-4o", "description": "Most capable model, best for complex tasks"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "Fast and efficient, good for most tasks"},
            {"id": "gpt-4", "name": "GPT-4", "description": "Previous generation flagship model"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "Faster GPT-4 with updated knowledge"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and cost-effective"}
        ],
        "anthropic": [
            {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "description": "Most capable Claude model"},
            {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "description": "Fast and efficient Claude model"},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "description": "Previous flagship Claude model"}
        ],
        "google": [
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash", "description": "Latest Gemini model with fast performance"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro", "description": "Capable Gemini model for complex tasks"},
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash", "description": "Fast Gemini model for quick tasks"}
        ],
        "openrouter": [
            {"id": "openai/gpt-4o", "name": "GPT-4o (via OpenRouter)", "description": "OpenAI's latest model through OpenRouter"},
            {"id": "anthropic/claude-3.5-sonnet", "name": "Claude 3.5 Sonnet (via OpenRouter)", "description": "Anthropic's latest model through OpenRouter"},
            {"id": "google/gemini-2.0-flash", "name": "Gemini 2.0 Flash (via OpenRouter)", "description": "Google's latest model through OpenRouter"},
            {"id": "meta-llama/llama-3.2-90b-instruct", "name": "Llama 3.2 90B", "description": "Meta's powerful open source model"}
        ],
        "emergent": [
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini (Emergent)", "description": "Fast OpenAI model via Emergent key"},
            {"id": "gpt-4o", "name": "GPT-4o (Emergent)", "description": "OpenAI flagship via Emergent key"},
            {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet (Emergent)", "description": "Anthropic model via Emergent key"},
            {"id": "gemini-2.0-flash", "name": "Gemini 2.0 Flash (Emergent)", "description": "Google model via Emergent key"}
        ]
    }
