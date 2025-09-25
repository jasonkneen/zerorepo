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
  const [isDarkMode, setIsDarkMode] = useState(true);

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
        <div className="mb-12">
          <div className="border border-gray-200 rounded-lg p-6 bg-gray-50">
            <h2 className="text-xl font-semibold text-black mb-3">Quick Demo</h2>
            <p className="text-gray-600 mb-4">
              Test the ZeroRepo system with a machine learning example
            </p>
            
            <button
              onClick={handleQuickDemo}
              disabled={isGenerating}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400 transition-colors"
            >
              {isGenerating ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Running Real AI Demo...
                </>
              ) : "Run Quick Demo"}
            </button>

            {demoResult && (
              <div className="mt-4 p-4 border border-gray-200 rounded-lg bg-white">
                <h3 className="font-semibold text-black mb-3">Demo Results</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between py-1">
                    <span className="text-gray-600">Status</span>
                    <span className={`font-medium ${demoResult.success ? 'text-green-600' : 'text-red-600'}`}>
                      {demoResult.success ? "Success" : "Failed"}
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-1">
                    <span className="text-gray-600">Features Generated</span>
                    <span className="font-mono text-black">{demoResult.features_generated}</span>
                  </div>
                  <div className="flex items-center justify-between py-1">
                    <span className="text-gray-600">Graph Nodes</span>
                    <span className="font-mono text-black">{demoResult.nodes_in_graph}</span>
                  </div>
                  {demoResult.sample_features && demoResult.sample_features.length > 0 && (
                    <div className="mt-3">
                      <p className="text-gray-600 mb-2">Sample Features:</p>
                      <div className="bg-gray-50 p-3 rounded border text-xs font-mono space-y-1">
                        {demoResult.sample_features.slice(0, 5).map((feature, idx) => (
                          <div key={idx} className="text-gray-800">{feature}</div>
                        ))}
                      </div>
                    </div>
                  )}
                  <p className="mt-3 text-sm text-gray-700 font-medium">{demoResult.message}</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Main Interface */}
        <div className="border border-gray-200 rounded-lg p-6 bg-white">
          <h2 className="text-2xl font-semibold text-black mb-6">Generate Repository</h2>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Project Goal
              </label>
              <textarea
                value={projectGoal}
                onChange={(e) => setProjectGoal(e.target.value)}
                placeholder="e.g., Generate a machine learning toolkit with regression, classification, and clustering algorithms"
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-black focus:border-transparent text-black placeholder-gray-400 bg-white"
                rows={3}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Domain
              </label>
              <select
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-black focus:border-transparent text-black bg-white"
              >
                <option value="ml">Machine Learning</option>
                <option value="web">Web Development</option>
                <option value="data">Data Processing</option>
                <option value="general">General</option>
              </select>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={handlePlanRepository}
                disabled={isPlanning || isGenerating}
                className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:bg-gray-100 disabled:text-gray-400 transition-colors"
              >
                {isPlanning ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Planning with AI...
                  </>
                ) : "Plan Repository"}
              </button>
              
              <button
                onClick={handleGenerateRepository}
                disabled={isGenerating || isPlanning}
                className="flex-1 inline-flex items-center justify-center px-4 py-2 bg-black text-white rounded-md text-sm font-medium hover:bg-gray-800 disabled:bg-gray-300 disabled:text-gray-500 transition-colors"
              >
                {isGenerating ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </>
                ) : "Generate Repository"}
              </button>
            </div>

            {/* Performance notice */}
            <div className="p-3 bg-gray-50 border border-gray-200 rounded-md text-sm text-gray-600">
              <span className="font-medium">AI Integration:</span> Planning uses GPT-4o-mini for intelligent feature generation. 
              This takes 30-60 seconds for quality results.
            </div>
          </div>
        </div>

        {/* Live Job Progress */}
        {jobProgress && jobProgress.status === "running" && (
          <div className="mt-8 border border-gray-200 rounded-lg p-6 bg-white">
            <h3 className="text-lg font-semibold text-black mb-4">
              Generation Progress
            </h3>
            
            <div className="space-y-4">
              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-black h-2 rounded-full transition-all duration-500"
                  style={{ width: `${jobProgress.progress}%` }}
                ></div>
              </div>
              
              {/* Progress Details */}
              <div className="flex justify-between text-sm">
                <span className="text-gray-900 font-medium">{jobProgress.progress}% Complete</span>
                <span className="text-gray-600">{jobProgress.current_stage}</span>
              </div>
              
              {/* Stage Information */}
              <div className="bg-gray-50 border border-gray-200 p-4 rounded-md">
                <div className="flex items-center space-x-2 mb-2">
                  <div className="w-2 h-2 bg-black rounded-full animate-pulse"></div>
                  <span className="text-black font-medium">Currently Processing:</span>
                </div>
                <p className="text-gray-700 ml-4">{jobProgress.current_stage}</p>
              </div>
              
              {/* Expected Timeline */}
              <div className="text-xs text-gray-500 space-y-1">
                <p>⏱️ AI-powered generation typically takes 2-5 minutes for quality results</p>
                <p>🧠 The system is making real LLM calls for intelligent feature planning</p>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mt-8 p-4 bg-red-50 border border-red-200 rounded-lg">
            <h3 className="font-semibold text-red-800 mb-2">Error</h3>
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="mt-8 border border-gray-200 rounded-lg p-6 bg-white">
            <h3 className="text-lg font-semibold text-black mb-4">
              {result.type === 'plan' ? 'Planning Results' : 'Generation Started'}
            </h3>
            
            {result.type === 'plan' && (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-gray-50 border border-gray-200 rounded-md">
                    <div className="text-2xl font-bold text-black">
                      {result.data.metrics.total_features}
                    </div>
                    <div className="text-sm text-gray-600">Features</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 border border-gray-200 rounded-md">
                    <div className="text-2xl font-bold text-black">
                      {result.data.metrics.total_nodes}
                    </div>
                    <div className="text-sm text-gray-600">Graph Nodes</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 border border-gray-200 rounded-md">
                    <div className="text-2xl font-bold text-black">
                      {result.data.metrics.total_edges}
                    </div>
                    <div className="text-sm text-gray-600">Connections</div>
                  </div>
                </div>
                
                {result.data.feature_paths && result.data.feature_paths.length > 0 && (
                  <div>
                    <h4 className="font-medium text-black mb-3">Sample Feature Paths</h4>
                    <div className="bg-gray-50 border border-gray-200 p-4 rounded-md text-xs font-mono max-h-48 overflow-y-auto">
                      {result.data.feature_paths.slice(0, 12).map((fp, idx) => (
                        <div key={idx} className="flex justify-between py-1">
                          <span className="text-gray-900">{fp.path}</span>
                          <span className="text-gray-500">({fp.source})</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {result.type === 'generate' && !jobProgress && (
              <div className="space-y-4">
                <div className="p-4 bg-gray-50 border border-gray-200 rounded-md">
                  <p className="text-gray-700 mb-2">
                    <span className="font-medium">Job ID:</span> 
                    <span className="font-mono text-black ml-2">{result.jobId}</span>
                  </p>
                  <p className="text-gray-700 mb-3">
                    Repository generation has started. This process involves:
                  </p>
                  <div className="space-y-2 text-sm text-gray-600">
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border border-gray-300 rounded flex items-center justify-center text-xs">A</div>
                      <span>AI plans repository structure using explore/exploit/missing features</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border border-gray-300 rounded flex items-center justify-center text-xs">B</div>
                      <span>Designs file architecture and interfaces</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border border-gray-300 rounded flex items-center justify-center text-xs">C</div>
                      <span>Generates actual code with test-driven development</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {result.type === 'generate_complete' && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-gray-50 border border-gray-200 rounded-md">
                    <div className="text-2xl font-bold text-black">
                      {result.data.result?.generated_files?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">Files Generated</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 border border-gray-200 rounded-md">
                    <div className="text-2xl font-bold text-black">
                      {Math.round((result.data.result?.metrics?.success_rate || 0) * 100)}%
                    </div>
                    <div className="text-sm text-gray-600">Success Rate</div>
                  </div>
                </div>
                
                {result.data.result?.generated_files?.length > 0 && (
                  <div>
                    <h4 className="font-medium text-black mb-3">Generated Files</h4>
                    <div className="bg-gray-50 border border-gray-200 p-4 rounded-md text-xs font-mono max-h-32 overflow-y-auto">
                      {result.data.result.generated_files.map((file, idx) => (
                        <div key={idx} className="text-gray-800 py-1">{file}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Process Architecture */}
        <div className="mt-12 border-t border-gray-200 pt-8">
          <h3 className="text-lg font-medium text-black mb-6 text-center">Repository Generation Process</h3>
          <div className="grid grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-gray-100 border-2 border-gray-300 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-lg font-bold text-gray-700">A</span>
              </div>
              <h4 className="font-medium text-black mb-1">Proposal Construction</h4>
              <p className="text-sm text-gray-600">Explore/Exploit/Missing</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-gray-100 border-2 border-gray-300 rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-lg font-bold text-gray-700">B</span>
              </div>
              <h4 className="font-medium text-black mb-1">Implementation Design</h4>
              <p className="text-sm text-gray-600">Files/Interfaces/Data Flow</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-black rounded-lg flex items-center justify-center mx-auto mb-3">
                <span className="text-lg font-bold text-white">C</span>
              </div>
              <h4 className="font-medium text-black mb-1">Code Generation</h4>
              <p className="text-sm text-gray-600">Topological TDD</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-gray-500 text-sm border-t border-gray-200 pt-6">
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