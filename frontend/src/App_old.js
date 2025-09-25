import React, { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ZeroRepoInterface = () => {
  const [projectGoal, setProjectGoal] = useState("");
  const [domain, setDomain] = useState("ml");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPlanning, setIsPlanning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [demoResult, setDemoResult] = useState(null);
  const [currentJob, setCurrentJob] = useState(null);
  const [jobProgress, setJobProgress] = useState(null);

  // Poll job status for live updates
  useEffect(() => {
    if (currentJob && currentJob.status === "running") {
      const pollInterval = setInterval(async () => {
        try {
          const response = await axios.get(`${API}/zerorepo/jobs/${currentJob.id}`);
          const jobData = response.data;
          
          setJobProgress(jobData);
          
          if (jobData.status === "completed" || jobData.status === "failed") {
            clearInterval(pollInterval);
            setIsGenerating(false);
            setCurrentJob(null);
            
            if (jobData.status === "completed") {
              setResult({
                type: 'generate_complete',
                data: jobData
              });
            } else {
              setError(jobData.error || "Generation failed");
            }
          }
        } catch (err) {
          console.error("Polling error:", err);
        }
      }, 3000); // Poll every 3 seconds
      
      return () => clearInterval(pollInterval);
    }
  }, [currentJob]);

  const handleQuickDemo = async () => {
    setIsGenerating(true);
    setError(null);
    setDemoResult(null);

    try {
      const response = await axios.post(`${API}/zerorepo/quick-demo`);
      setDemoResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Demo failed");
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePlanRepository = async () => {
    if (!projectGoal.trim()) {
      setError("Please enter a project goal");
      return;
    }

    setIsPlanning(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API}/zerorepo/plan`, {
        project_goal: projectGoal,
        domain: domain,
        llm_model: "gpt-4o-mini",  // Use faster model
        max_iterations: 2  // Reduced from 15 for speed
      });

      setResult({
        type: 'plan',
        data: response.data
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Planning failed");
    } finally {
      setIsPlanning(false);
    }
  };

  const handleGenerateRepository = async () => {
    if (!projectGoal.trim()) {
      setError("Please enter a project goal");
      return;
    }

    setIsGenerating(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API}/zerorepo/generate`, {
        project_goal: projectGoal,
        domain: domain,
        llm_model: "gpt-4o-mini",  // Use faster model
        max_iterations: 3  // Reduced from 20 for speed
      });

      setResult({
        type: 'generate',
        data: response.data,
        jobId: response.data.job_id
      });
      
      // Set up job tracking for live updates
      setCurrentJob({
        id: response.data.job_id,
        status: "running"
      });
      
      setJobProgress({
        progress: 0,
        current_stage: "Starting generation...",
        status: "running"
      });
    } catch (err) {
      setError(err.response?.data?.detail || "Generation failed");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-white text-black">
      {/* Header */}
      <div className="border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold tracking-tight text-black mb-2">
              ZeroRepo
            </h1>
            <p className="text-lg text-gray-600 mb-1">Graph-Driven Repository Generation</p>
            <p className="text-sm text-gray-500">
              AI-powered system that plans, designs, and generates complete software repositories
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">

        {/* Quick Demo Section */}
        <div className="bg-slate-800 rounded-lg p-6 mb-8 border border-slate-700">
          <h2 className="text-2xl font-semibold mb-4 text-blue-400">Quick Demo</h2>
          <p className="text-gray-300 mb-4">
            Test the ZeroRepo system with a simple machine learning example
          </p>
          
          <button
            onClick={handleQuickDemo}
            disabled={isGenerating}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 px-6 py-3 rounded-lg font-medium transition-colors"
          >
            {isGenerating ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Running Real AI Demo...
              </span>
            ) : "🚀 Run Quick Demo (Fast)"}
          </button>

          {demoResult && (
            <div className="mt-4 p-4 bg-slate-700 rounded-lg border border-green-500">
              <h3 className="font-semibold text-green-400 mb-2">Demo Results:</h3>
              <div className="text-sm text-gray-300 space-y-1">
                <p><strong>Status:</strong> {demoResult.success ? "✅ Success" : "❌ Failed"}</p>
                <p><strong>Goal:</strong> {demoResult.demo_goal}</p>
                <p><strong>Features Generated:</strong> {demoResult.features_generated}</p>
                <p><strong>Graph Nodes:</strong> {demoResult.nodes_in_graph}</p>
                {demoResult.sample_features && (
                  <div>
                    <p><strong>Sample Features:</strong></p>
                    <ul className="ml-4 list-disc">
                      {demoResult.sample_features.map((feature, idx) => (
                        <li key={idx} className="text-blue-300">{feature}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <p className="text-green-400 font-medium">{demoResult.message}</p>
              </div>
            </div>
          )}
        </div>

        {/* Main Interface */}
        <div className="bg-slate-800 rounded-lg p-8 border border-slate-700">
          <h2 className="text-3xl font-semibold mb-6 text-purple-400">Generate Repository</h2>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Project Goal
              </label>
              <textarea
                value={projectGoal}
                onChange={(e) => setProjectGoal(e.target.value)}
                placeholder="e.g., Generate a machine learning toolkit with regression, classification, and clustering algorithms"
                className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg focus:border-purple-500 focus:outline-none text-white"
                rows={3}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Domain
              </label>
              <select
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg focus:border-purple-500 focus:outline-none text-white"
              >
                <option value="ml">Machine Learning</option>
                <option value="web">Web Development</option>
                <option value="data">Data Processing</option>
                <option value="general">General</option>
              </select>
            </div>

            <div className="flex space-x-4">
              <button
                onClick={handlePlanRepository}
                disabled={isPlanning || isGenerating}
                className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 px-6 py-3 rounded-lg font-medium transition-colors"
              >
                {isPlanning ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Planning with AI...
                  </span>
                ) : "📋 Plan Repository"}
              </button>
              
              <button
                onClick={handleGenerateRepository}
                disabled={isGenerating || isPlanning}
                className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 px-6 py-3 rounded-lg font-medium transition-colors"
              >
                {isGenerating ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </span>
                ) : "🏗️ Generate Repository"}
              </button>
            </div>

            {/* Speed optimization notice */}
            <div className="mt-4 p-3 bg-blue-900 border border-blue-600 rounded text-sm text-blue-200">
              💡 <strong>Real AI Integration:</strong> Planning now uses actual GPT-4o-mini for intelligent feature generation. 
              This takes 30-60 seconds for quality results vs instant mock responses.
            </div>
          </div>
        </div>

        {/* Live Job Progress */}
        {jobProgress && jobProgress.status === "running" && (
          <div className="mt-6 p-6 bg-slate-800 border border-yellow-600 rounded-lg">
            <h3 className="font-semibold text-yellow-400 mb-4">
              🔄 Live Generation Progress
            </h3>
            
            <div className="space-y-4">
              {/* Progress Bar */}
              <div className="w-full bg-gray-700 rounded-full h-3">
                <div 
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${jobProgress.progress}%` }}
                ></div>
              </div>
              
              {/* Progress Details */}
              <div className="flex justify-between text-sm">
                <span className="text-gray-300">{jobProgress.progress}% Complete</span>
                <span className="text-blue-300">{jobProgress.current_stage}</span>
              </div>
              
              {/* Stage Information */}
              <div className="bg-slate-700 p-3 rounded text-sm">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                  <span className="text-yellow-300 font-medium">Currently Processing:</span>
                </div>
                <p className="text-gray-300 ml-4">{jobProgress.current_stage}</p>
              </div>
              
              {/* Expected Timeline */}
              <div className="text-xs text-gray-400">
                <p>⏱️ AI-powered generation typically takes 2-5 minutes for quality results</p>
                <p>🧠 The system is making real LLM calls for intelligent feature planning</p>
              </div>
            </div>
          </div>
        )}

        {/* Results Section */}
        {error && (
          <div className="mt-6 p-4 bg-red-900 border border-red-600 rounded-lg">
            <h3 className="font-semibold text-red-400 mb-2">Error:</h3>
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {result && (
          <div className="mt-6 p-6 bg-slate-800 border border-green-600 rounded-lg">
            <h3 className="font-semibold text-green-400 mb-4">
              {result.type === 'plan' ? 'Planning Results' : 'Generation Started'}
            </h3>
            
            {result.type === 'plan' && (
              <div className="space-y-3 text-sm">
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-3 bg-slate-700 rounded">
                    <div className="text-2xl font-bold text-blue-400">
                      {result.data.metrics.total_features}
                    </div>
                    <div className="text-gray-300">Features</div>
                  </div>
                  <div className="text-center p-3 bg-slate-700 rounded">
                    <div className="text-2xl font-bold text-purple-400">
                      {result.data.metrics.total_nodes}
                    </div>
                    <div className="text-gray-300">Graph Nodes</div>
                  </div>
                  <div className="text-center p-3 bg-slate-700 rounded">
                    <div className="text-2xl font-bold text-green-400">
                      {result.data.metrics.total_edges}
                    </div>
                    <div className="text-gray-300">Connections</div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold text-blue-300 mb-2">Sample Feature Paths:</h4>
                  <div className="bg-slate-700 p-3 rounded text-xs font-mono">
                    {result.data.feature_paths.slice(0, 8).map((fp, idx) => (
                      <div key={idx} className="text-blue-300">
                        {fp.path} <span className="text-gray-400">({fp.source})</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
            
            {result.type === 'generate' && !jobProgress && (
              <div className="space-y-3">
                <p className="text-gray-300">
                  <strong>Job ID:</strong> <span className="font-mono text-blue-300">{result.jobId}</span>
                </p>
                <p className="text-gray-300">
                  Repository generation has started. This process involves:
                </p>
                <ul className="list-disc list-inside text-sm text-gray-300 ml-4 space-y-1">
                  <li>Stage A: AI plans repository structure using explore/exploit/missing features</li>
                  <li>Stage B: Designs file architecture and interfaces</li>
                  <li>Stage C: Generates actual code with test-driven development</li>
                </ul>
              </div>
            )}
            
            {result.type === 'generate_complete' && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-slate-700 rounded">
                    <div className="text-2xl font-bold text-green-400">
                      {result.data.result?.generated_files?.length || 0}
                    </div>
                    <div className="text-gray-300">Files Generated</div>
                  </div>
                  <div className="text-center p-3 bg-slate-700 rounded">
                    <div className="text-2xl font-bold text-blue-400">
                      {Math.round((result.data.result?.metrics?.success_rate || 0) * 100)}%
                    </div>
                    <div className="text-gray-300">Success Rate</div>
                  </div>
                </div>
                
                {result.data.result?.generated_files?.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-green-300 mb-2">Generated Files:</h4>
                    <div className="bg-slate-700 p-3 rounded text-xs font-mono max-h-32 overflow-y-auto">
                      {result.data.result.generated_files.map((file, idx) => (
                        <div key={idx} className="text-green-300">{file}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* System Info */}
        <div className="mt-12 text-center text-gray-400 text-sm">
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="p-3 bg-slate-800 rounded border border-slate-700">
              <div className="font-semibold text-blue-400">Stage A</div>
              <div>Proposal Construction</div>
              <div className="text-xs">Explore/Exploit/Missing</div>
            </div>
            <div className="p-3 bg-slate-800 rounded border border-slate-700">
              <div className="font-semibold text-purple-400">Stage B</div>
              <div>Implementation Design</div>
              <div className="text-xs">Files/Interfaces/Data Flow</div>
            </div>
            <div className="p-3 bg-slate-800 rounded border border-slate-700">
              <div className="font-semibold text-green-400">Stage C</div>
              <div>Code Generation</div>
              <div className="text-xs">Topological TDD</div>
            </div>
          </div>
          <p>ZeroRepo v1.0 - Graph-Driven Repository Generation System</p>
        </div>
      </div>
    </div>
  );
};

const Home = () => {
  const helloWorldApi = async () => {
    try {
      const response = await axios.get(`${API}/`);
      console.log(response.data.message);
    } catch (e) {
      console.error(e, `errored out requesting / api`);
    }
  };

  useEffect(() => {
    helloWorldApi();
  }, []);

  return <ZeroRepoInterface />;
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />}>
            <Route index element={<Home />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
