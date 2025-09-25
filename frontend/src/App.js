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
        llm_model: "gpt-4o-mini",
        max_iterations: 2
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
        llm_model: "gpt-4o-mini",
        max_iterations: 3
      });

      setResult({
        type: 'generate',
        data: response.data,
        jobId: response.data.job_id
      });
      
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

  const themeClasses = {
    bg: isDarkMode ? "bg-zinc-900" : "bg-white",
    cardBg: isDarkMode ? "bg-zinc-800" : "bg-white",
    cardBorder: isDarkMode ? "border-zinc-700" : "border-gray-200",
    text: isDarkMode ? "text-white" : "text-black",
    textSecondary: isDarkMode ? "text-zinc-400" : "text-gray-600",
    textMuted: isDarkMode ? "text-zinc-500" : "text-gray-500",
    input: isDarkMode ? "bg-zinc-800 border-zinc-600 text-white placeholder-zinc-400" : "bg-white border-gray-300 text-black placeholder-gray-400",
    inputFocus: isDarkMode ? "focus:border-zinc-400 focus:ring-zinc-400" : "focus:border-black focus:ring-black",
    buttonPrimary: isDarkMode ? "bg-white text-black hover:bg-zinc-200" : "bg-black text-white hover:bg-gray-800",
    buttonSecondary: isDarkMode ? "bg-zinc-700 text-white hover:bg-zinc-600 border-zinc-600" : "bg-white text-gray-700 hover:bg-gray-50 border-gray-300",
    headerBorder: isDarkMode ? "border-zinc-800" : "border-gray-200",
    successText: isDarkMode ? "text-emerald-400" : "text-emerald-600",
    errorText: isDarkMode ? "text-red-400" : "text-red-600",
    errorBg: isDarkMode ? "bg-red-900/20 border-red-800" : "bg-red-50 border-red-200"
  };

  return (
    <div className={`min-h-screen ${themeClasses.bg} ${themeClasses.text} transition-colors duration-300`}>
      {/* Header */}
      <div className={`border-b ${themeClasses.headerBorder}`}>
        <div className="max-w-6xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div className="text-center flex-1">
              <h1 className="text-5xl font-bold tracking-tight mb-3">
                ZeroRepo
              </h1>
              <p className="text-xl font-medium mb-2">Graph-Driven Repository Generation</p>
              <p className={`text-sm ${themeClasses.textMuted}`}>
                AI-powered system that plans, designs, and generates complete software repositories
              </p>
            </div>
            
            {/* Dark Mode Toggle */}
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className={`rounded-full p-3 transition-all duration-300 shadow-lg ${
                isDarkMode 
                  ? "bg-zinc-800 hover:bg-zinc-700 border border-zinc-600" 
                  : "bg-gray-100 hover:bg-gray-200 border border-gray-300"
              }`}
            >
              {isDarkMode ? (
                <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-10">
        
        {/* Quick Demo Section */}
        <div className="mb-16">
          <div className={`${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-3xl p-8 shadow-2xl`}>
            <h2 className="text-2xl font-bold mb-4">Quick Demo</h2>
            <p className={`${themeClasses.textSecondary} mb-6 text-lg`}>
              Test the ZeroRepo system with a machine learning example
            </p>
            
            <button
              onClick={handleQuickDemo}
              disabled={isGenerating}
              className={`
                ${themeClasses.buttonPrimary}
                inline-flex items-center px-8 py-4 rounded-full text-lg font-semibold
                shadow-2xl transition-all duration-300 transform hover:scale-105 
                disabled:opacity-50 disabled:transform-none disabled:cursor-not-allowed
              `}
            >
              {isGenerating ? (
                <>
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Running AI Demo...
                </>
              ) : "🚀 Run Quick Demo"}
            </button>

            {demoResult && (
              <div className={`mt-6 p-6 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl shadow-xl`}>
                <h3 className="text-xl font-bold mb-4">Demo Results</h3>
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div className={`text-center p-4 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl shadow-lg`}>
                      <div className={`text-2xl font-bold ${demoResult.success ? themeClasses.successText : themeClasses.errorText}`}>
                        {demoResult.success ? "✓" : "✗"}
                      </div>
                      <div className={`text-sm ${themeClasses.textSecondary}`}>Status</div>
                    </div>
                    <div className={`text-center p-4 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl shadow-lg`}>
                      <div className="text-2xl font-bold">{demoResult.features_generated}</div>
                      <div className={`text-sm ${themeClasses.textSecondary}`}>Features</div>
                    </div>
                    <div className={`text-center p-4 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl shadow-lg`}>
                      <div className="text-2xl font-bold">{demoResult.nodes_in_graph}</div>
                      <div className={`text-sm ${themeClasses.textSecondary}`}>Nodes</div>
                    </div>
                  </div>
                  
                  {demoResult.sample_features && demoResult.sample_features.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-3">Sample Features</h4>
                      <div className={`${themeClasses.cardBg} ${themeClasses.cardBorder} border p-4 rounded-2xl text-sm font-mono space-y-2 max-h-48 overflow-y-auto shadow-inner`}>
                        {demoResult.sample_features.slice(0, 6).map((feature, idx) => (
                          <div key={idx} className={`${themeClasses.textSecondary} py-1`}>
                            {feature}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  <p className={`text-sm font-medium ${themeClasses.successText}`}>
                    {demoResult.message}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Main Interface */}
        <div className={`${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-3xl p-8 shadow-2xl`}>
          <h2 className="text-3xl font-bold mb-8">Generate Repository</h2>
          
          <div className="space-y-8">
            <div>
              <label className={`block text-sm font-semibold ${themeClasses.text} mb-3`}>
                Project Goal
              </label>
              <textarea
                value={projectGoal}
                onChange={(e) => setProjectGoal(e.target.value)}
                placeholder="e.g., Generate a machine learning toolkit with regression, classification, and clustering algorithms"
                className={`
                  w-full p-4 border rounded-2xl resize-none shadow-lg transition-all duration-300
                  ${themeClasses.input} ${themeClasses.inputFocus} focus:ring-2 focus:ring-offset-2
                  ${isDarkMode ? "focus:ring-offset-zinc-900" : "focus:ring-offset-white"}
                `}
                rows={4}
              />
            </div>

            <div>
              <label className={`block text-sm font-semibold ${themeClasses.text} mb-3`}>
                Domain
              </label>
              <select
                value={domain}
                onChange={(e) => setDomain(e.target.value)}
                className={`
                  w-full p-4 border rounded-2xl shadow-lg transition-all duration-300
                  ${themeClasses.input} ${themeClasses.inputFocus} focus:ring-2 focus:ring-offset-2
                  ${isDarkMode ? "focus:ring-offset-zinc-900" : "focus:ring-offset-white"}
                `}
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
                className={`
                  flex-1 inline-flex items-center justify-center px-8 py-4 rounded-full text-lg font-semibold
                  shadow-2xl transition-all duration-300 transform hover:scale-105
                  disabled:opacity-50 disabled:transform-none disabled:cursor-not-allowed
                  ${themeClasses.buttonSecondary}
                `}
              >
                {isPlanning ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Planning with AI...
                  </>
                ) : "📋 Plan Repository"}
              </button>
              
              <button
                onClick={handleGenerateRepository}
                disabled={isGenerating || isPlanning}
                className={`
                  flex-1 inline-flex items-center justify-center px-8 py-4 rounded-full text-lg font-semibold
                  shadow-2xl transition-all duration-300 transform hover:scale-105
                  disabled:opacity-50 disabled:transform-none disabled:cursor-not-allowed
                  ${themeClasses.buttonPrimary}
                `}
              >
                {isGenerating ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 714 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </>
                ) : "🏗️ Generate Repository"}
              </button>
            </div>

            {/* Performance notice */}
            <div className={`p-4 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl text-sm ${themeClasses.textSecondary} shadow-lg`}>
              <span className="font-semibold">AI Integration:</span> Planning uses GPT-4o-mini for intelligent feature generation. 
              This takes 30-60 seconds for quality results.
            </div>
          </div>
        </div>

        {/* Live Job Progress */}
        {jobProgress && jobProgress.status === "running" && (
          <div className={`mt-8 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-3xl p-8 shadow-2xl`}>
            <h3 className="text-xl font-bold mb-6">
              🔄 Live Generation Progress
            </h3>
            
            <div className="space-y-6">
              {/* Progress Bar */}
              <div className={`w-full ${isDarkMode ? "bg-zinc-700" : "bg-gray-200"} rounded-full h-4 shadow-inner`}>
                <div 
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-4 rounded-full transition-all duration-1000 shadow-lg"
                  style={{ width: `${jobProgress.progress}%` }}
                ></div>
              </div>
              
              {/* Progress Details */}
              <div className="flex justify-between">
                <span className="text-lg font-bold">{jobProgress.progress}% Complete</span>
                <span className={`${themeClasses.textSecondary} font-medium`}>
                  {jobProgress.current_stage}
                </span>
              </div>
              
              {/* Stage Information */}
              <div className={`${themeClasses.cardBg} ${themeClasses.cardBorder} border p-6 rounded-2xl shadow-xl`}>
                <div className="flex items-center space-x-3 mb-3">
                  <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse shadow-lg"></div>
                  <span className="font-semibold text-lg">Currently Processing</span>
                </div>
                <p className={`${themeClasses.textSecondary} ml-6 text-lg`}>
                  {jobProgress.current_stage}
                </p>
              </div>
              
              {/* Expected Timeline */}
              <div className={`text-sm ${themeClasses.textMuted} space-y-2 p-4 rounded-2xl ${themeClasses.cardBg} border ${themeClasses.cardBorder}`}>
                <p>⏱️ AI-powered generation typically takes 2-5 minutes for quality results</p>
                <p>🧠 The system is making real LLM calls for intelligent feature planning</p>
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className={`mt-8 p-6 rounded-3xl shadow-xl ${themeClasses.errorBg} border`}>
            <h3 className={`font-bold text-lg ${themeClasses.errorText} mb-3`}>Error</h3>
            <p className={themeClasses.errorText}>{error}</p>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className={`mt-8 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-3xl p-8 shadow-2xl`}>
            <h3 className="text-xl font-bold mb-6">
              {result.type === 'plan' ? 'Planning Results' : 'Generation Started'}
            </h3>
            
            {result.type === 'plan' && (
              <div className="space-y-6">
                <div className="grid grid-cols-3 gap-6">
                  <div className={`text-center p-6 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl shadow-xl`}>
                    <div className="text-3xl font-bold mb-2">
                      {result.data.metrics.total_features}
                    </div>
                    <div className={`text-sm font-medium ${themeClasses.textSecondary}`}>Features</div>
                  </div>
                  <div className={`text-center p-6 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl shadow-xl`}>
                    <div className="text-3xl font-bold mb-2">
                      {result.data.metrics.total_nodes}
                    </div>
                    <div className={`text-sm font-medium ${themeClasses.textSecondary}`}>Graph Nodes</div>
                  </div>
                  <div className={`text-center p-6 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl shadow-xl`}>
                    <div className="text-3xl font-bold mb-2">
                      {result.data.metrics.total_edges}
                    </div>
                    <div className={`text-sm font-medium ${themeClasses.textSecondary}`}>Connections</div>
                  </div>
                </div>
                
                {result.data.feature_paths && result.data.feature_paths.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-lg mb-4">Sample Feature Paths</h4>
                    <div className={`${themeClasses.cardBg} ${themeClasses.cardBorder} border p-6 rounded-2xl text-sm font-mono max-h-64 overflow-y-auto shadow-inner space-y-2`}>
                      {result.data.feature_paths.slice(0, 12).map((fp, idx) => (
                        <div key={idx} className="flex justify-between py-1">
                          <span className={themeClasses.text}>{fp.path}</span>
                          <span className={`${themeClasses.textMuted} text-xs`}>({fp.source})</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {result.type === 'generate' && !jobProgress && (
              <div className="space-y-4">
                <div className={`p-6 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl shadow-lg`}>
                  <p className={`${themeClasses.textSecondary} mb-3`}>
                    <span className="font-semibold">Job ID:</span> 
                    <span className="font-mono ml-2">{result.jobId}</span>
                  </p>
                  <p className={`${themeClasses.textSecondary} mb-4`}>
                    Repository generation has started. This process involves:
                  </p>
                  <div className="space-y-3">
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 ${themeClasses.cardBorder} border rounded-full flex items-center justify-center text-xs font-bold shadow-lg`}>A</div>
                      <span className={themeClasses.textSecondary}>AI plans repository structure using explore/exploit/missing features</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 ${themeClasses.cardBorder} border rounded-full flex items-center justify-center text-xs font-bold shadow-lg`}>B</div>
                      <span className={themeClasses.textSecondary}>Designs file architecture and interfaces</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 ${themeClasses.cardBorder} border rounded-full flex items-center justify-center text-xs font-bold shadow-lg`}>C</div>
                      <span className={themeClasses.textSecondary}>Generates actual code with test-driven development</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            {result.type === 'generate_complete' && (
              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-6">
                  <div className={`text-center p-6 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl shadow-xl`}>
                    <div className="text-3xl font-bold mb-2">
                      {result.data.result?.generated_files?.length || 0}
                    </div>
                    <div className={`text-sm font-medium ${themeClasses.textSecondary}`}>Files Generated</div>
                  </div>
                  <div className={`text-center p-6 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl shadow-xl`}>
                    <div className="text-3xl font-bold mb-2">
                      {Math.round((result.data.result?.metrics?.success_rate || 0) * 100)}%
                    </div>
                    <div className={`text-sm font-medium ${themeClasses.textSecondary}`}>Success Rate</div>
                  </div>
                </div>
                
                {result.data.result?.generated_files?.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-lg mb-4">Generated Files</h4>
                    <div className={`${themeClasses.cardBg} ${themeClasses.cardBorder} border p-6 rounded-2xl text-sm font-mono max-h-48 overflow-y-auto shadow-inner`}>
                      {result.data.result.generated_files.map((file, idx) => (
                        <div key={idx} className={`${themeClasses.textSecondary} py-1`}>{file}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Process Architecture */}
        <div className="mt-16">
          <h3 className="text-2xl font-bold text-center mb-8">Repository Generation Process</h3>
          <div className="grid grid-cols-3 gap-8">
            <div className="text-center">
              <div className={`w-16 h-16 ${themeClasses.cardBg} ${themeClasses.cardBorder} border-2 rounded-3xl flex items-center justify-center mx-auto mb-4 shadow-2xl`}>
                <span className="text-2xl font-bold">A</span>
              </div>
              <h4 className="font-bold text-lg mb-2">Proposal Construction</h4>
              <p className={`text-sm ${themeClasses.textSecondary}`}>Explore/Exploit/Missing</p>
            </div>
            <div className="text-center">
              <div className={`w-16 h-16 ${themeClasses.cardBg} ${themeClasses.cardBorder} border-2 rounded-3xl flex items-center justify-center mx-auto mb-4 shadow-2xl`}>
                <span className="text-2xl font-bold">B</span>
              </div>
              <h4 className="font-bold text-lg mb-2">Implementation Design</h4>
              <p className={`text-sm ${themeClasses.textSecondary}`}>Files/Interfaces/Data Flow</p>
            </div>
            <div className="text-center">
              <div className={`w-16 h-16 ${themeClasses.buttonPrimary} rounded-3xl flex items-center justify-center mx-auto mb-4 shadow-2xl`}>
                <span className="text-2xl font-bold">C</span>
              </div>
              <h4 className="font-bold text-lg mb-2">Code Generation</h4>
              <p className={`text-sm ${themeClasses.textSecondary}`}>Topological TDD</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className={`mt-16 text-center ${themeClasses.textMuted} text-sm border-t ${themeClasses.headerBorder} pt-8`}>
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