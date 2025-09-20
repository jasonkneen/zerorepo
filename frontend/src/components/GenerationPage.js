import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { 
  ArrowLeft,
  Settings,
  GitBranch,
  Sparkles,
  Play,
  CheckCircle,
  AlertCircle,
  FileText,
  Terminal,
  Database,
  Clock,
  Zap,
  Code,
  Cpu
} from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001";
const API = `${BACKEND_URL.replace(/\/$/, "")}/api`;
const STORAGE_KEYS = 'zerorepo_api_keys';
const STORAGE_PREFS = 'zerorepo_provider_prefs';

const GenerationPage = ({ isDarkMode, setIsDarkMode }) => {
  const [projectGoal, setProjectGoal] = useState("");
  const [domain, setDomain] = useState("ml");
  const [selectedProvider, setSelectedProvider] = useState("openai");
  const [selectedModel, setSelectedModel] = useState("gpt-4o-mini");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPlanning, setIsPlanning] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [demoResult, setDemoResult] = useState(null);
  const [currentJob, setCurrentJob] = useState(null);
  const [jobProgress, setJobProgress] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [generatedFiles, setGeneratedFiles] = useState([]);
  const [availableModels, setAvailableModels] = useState({});
  const [apiKeys, setApiKeys] = useState({
    openai: "",
    anthropic: "",
    google: "",
    openrouter: "",
    github: ""
  });
  const [keysLoaded, setKeysLoaded] = useState(false);
  const [prefsLoaded, setPrefsLoaded] = useState(false);
  const [logs, setLogs] = useState([]);
  const [logsError, setLogsError] = useState(null);
  const [logsLoading, setLogsLoading] = useState(false);

  // Load saved provider/model preferences
  useEffect(() => {
    const savedPrefs = localStorage.getItem(STORAGE_PREFS);
    if (savedPrefs) {
      try {
        const parsed = JSON.parse(savedPrefs);
        if (parsed.provider) {
          setSelectedProvider(parsed.provider);
        }
        if (parsed.model) {
          setSelectedModel(parsed.model);
        }
        if (parsed.domain) {
          setDomain(parsed.domain);
        }
      } catch (err) {
        console.error("Failed to parse saved provider preferences:", err);
      }
    }
    setPrefsLoaded(true);
  }, []);

  // Load API keys from localStorage on component mount
  useEffect(() => {
    const savedKeys = localStorage.getItem(STORAGE_KEYS);
    if (savedKeys) {
      try {
        const parsedKeys = JSON.parse(savedKeys);
        setApiKeys(parsedKeys);
      } catch (err) {
        console.error("Failed to parse saved API keys:", err);
      }
    }
    setKeysLoaded(true);
  }, []);

  // Save API keys to localStorage whenever they change
  useEffect(() => {
    if (!keysLoaded) return;
    localStorage.setItem(STORAGE_KEYS, JSON.stringify(apiKeys));
  }, [apiKeys, keysLoaded]);

  // Persist provider/model/domain preferences
  useEffect(() => {
    if (!prefsLoaded) return;
    const prefs = {
      provider: selectedProvider,
      model: selectedModel,
      domain
    };
    localStorage.setItem(STORAGE_PREFS, JSON.stringify(prefs));
  }, [selectedProvider, selectedModel, domain, prefsLoaded]);

  // Load available models on component mount
  useEffect(() => {
    const loadModels = async () => {
      try {
        const response = await axios.get(`${API}/models`);
        setAvailableModels(response.data);
      } catch (err) {
        console.error("Failed to load models:", err);
      }
    };
    loadModels();
  }, []);

  const fetchLogs = useCallback(async (silent = false) => {
    try {
      if (!silent) {
        setLogsLoading(true);
      }
      const response = await axios.get(`${API}/logs?limit=200`);
      setLogs(response.data.lines || []);
      setLogsError(null);
    } catch (err) {
      setLogsError(err.response?.data?.detail || err.message || 'Failed to load logs');
    } finally {
      if (!silent) {
        setLogsLoading(false);
      }
    }
  }, [API]);

  useEffect(() => {
    if (!showSettings) {
      return undefined;
    }

    fetchLogs();
    const interval = setInterval(() => {
      fetchLogs(true);
    }, 5000);

    return () => clearInterval(interval);
  }, [showSettings, fetchLogs]);

  // Update available models when provider changes
  const getCurrentModels = () => {
    return availableModels[selectedProvider] || [];
  };

  // Update selected model when provider changes
  useEffect(() => {
    const models = getCurrentModels();
    if (models.length > 0 && !models.find(m => m.id === selectedModel)) {
      setSelectedModel(models[0].id);
    }
  }, [selectedProvider, availableModels]);

  // Check if current provider has API key
  const hasApiKey = (provider) => {
    return apiKeys[provider] && apiKeys[provider].trim().length > 0;
  };

  // Get effective API configuration for requests
  const getApiConfig = () => {
    if (hasApiKey(selectedProvider)) {
      return {
        provider: selectedProvider,
        model: selectedModel,
        api_key: apiKeys[selectedProvider]
      };
    } else {
      // No valid API key for selected provider
      return null;
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

  // Poll job status for live updates with file tracking
  useEffect(() => {
    if (currentJob && currentJob.status === "running") {
      const pollInterval = setInterval(async () => {
        try {
          const response = await axios.get(`${API}/zerorepo/jobs/${currentJob.id}`);
          const jobData = response.data;
          
          setJobProgress(jobData);
          
          // Simulate file generation for demo (in real implementation, this would come from the backend)
          if (jobData.progress > 25) {
            const mockFiles = [
              { name: 'src/algorithms/regression.py', status: 'completed', timestamp: new Date() },
              { name: 'src/algorithms/classification.py', status: 'in_progress', timestamp: new Date() },
              { name: 'tests/test_regression.py', status: 'completed', timestamp: new Date() },
              { name: 'src/data/preprocessing.py', status: 'pending', timestamp: null },
              { name: 'src/evaluation/metrics.py', status: 'pending', timestamp: null }
            ];
            setGeneratedFiles(mockFiles);
          }
          
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
      }, 2000); // Poll every 2 seconds for more responsiveness
      
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

    const apiConfig = getApiConfig();
    if (!apiConfig) {
      setError(`Please configure API key for ${selectedProvider} in settings`);
      return;
    }

    setIsPlanning(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API}/zerorepo/plan`, {
        project_goal: projectGoal,
        domain: domain,
        llm_provider: apiConfig.provider,
        llm_model: apiConfig.model,
        api_key: apiConfig.api_key,
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

    const apiConfig = getApiConfig();
    if (!apiConfig) {
      setError(`Please configure API key for ${selectedProvider} in settings`);
      return;
    }

    setIsGenerating(true);
    setError(null);
    setResult(null);
    setGeneratedFiles([]);

    try {
      const response = await axios.post(`${API}/zerorepo/generate`, {
        project_goal: projectGoal,
        domain: domain,
        llm_provider: apiConfig.provider,
        llm_model: apiConfig.model,
        api_key: apiConfig.api_key,
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

  return (
    <div className={`min-h-screen ${themeClasses.bg} ${themeClasses.text} transition-colors duration-300`}>
      {/* Header */}
      <header className={`border-b ${themeClasses.headerBorder}`}>
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link 
                to="/"
                className={`inline-flex items-center px-4 py-2 rounded-full ${themeClasses.buttonSecondary} border transition-all duration-300 hover:scale-105`}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Home
              </Link>
              <div className="flex items-center space-x-2">
                <GitBranch className="h-6 w-6" />
                <span className="text-xl font-bold">ZeroRepo</span>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowSettings(!showSettings)}
                className={`rounded-full p-3 transition-all duration-300 shadow-lg ${
                  isDarkMode 
                    ? "bg-zinc-800 hover:bg-zinc-700 border border-zinc-600" 
                    : "bg-gray-100 hover:bg-gray-200 border border-gray-300"
                }`}
              >
                <Settings className="h-5 w-5" />
              </button>
              
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className={`rounded-full p-3 transition-all duration-300 shadow-lg ${
                  isDarkMode 
                    ? "bg-zinc-800 hover:bg-zinc-700 border border-zinc-600" 
                    : "bg-gray-100 hover:bg-gray-200 border border-gray-300"
                }`}
              >
                {isDarkMode ? (
                  <Sparkles className="h-5 w-5 text-yellow-400" />
                ) : (
                  <div className="h-5 w-5 rounded-full bg-gray-600"></div>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-10">
        
        {/* Settings Panel */}
        {showSettings && (
          <div className={`mb-8 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-3xl p-8 shadow-2xl`}>
            <h3 className="text-xl font-bold mb-6 flex items-center">
              <Settings className="h-5 w-5 mr-2" />
              API Settings
            </h3>
            
            <div className="space-y-6">
              {/* OpenAI */}
              <div className="grid md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold mb-2">OpenAI API Key</label>
                  <input
                    type="password"
                    placeholder="sk-..."
                    value={apiKeys.openai}
                    onChange={(e) => setApiKeys(prev => ({...prev, openai: e.target.value}))}
                    className={`w-full p-3 border rounded-2xl ${themeClasses.input} ${themeClasses.inputFocus} focus:ring-2`}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Model</label>
                  <select
                    disabled={!apiKeys.openai}
                    className={`w-full p-3 border rounded-2xl ${themeClasses.input} ${themeClasses.inputFocus} focus:ring-2 disabled:opacity-50`}
                  >
                    {(availableModels.openai || []).map(model => (
                      <option key={model.id} value={model.id}>{model.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Anthropic */}
              <div className="grid md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold mb-2">Anthropic API Key</label>
                  <input
                    type="password"
                    placeholder="sk-ant-..."
                    value={apiKeys.anthropic}
                    onChange={(e) => setApiKeys(prev => ({...prev, anthropic: e.target.value}))}
                    className={`w-full p-3 border rounded-2xl ${themeClasses.input} ${themeClasses.inputFocus} focus:ring-2`}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Model</label>
                  <select
                    disabled={!apiKeys.anthropic}
                    className={`w-full p-3 border rounded-2xl ${themeClasses.input} ${themeClasses.inputFocus} focus:ring-2 disabled:opacity-50`}
                  >
                    {(availableModels.anthropic || []).map(model => (
                      <option key={model.id} value={model.id}>{model.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Google/Gemini */}
              <div className="grid md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold mb-2">Google/Gemini API Key</label>
                  <input
                    type="password"
                    placeholder="AI..."
                    value={apiKeys.google}
                    onChange={(e) => setApiKeys(prev => ({...prev, google: e.target.value}))}
                    className={`w-full p-3 border rounded-2xl ${themeClasses.input} ${themeClasses.inputFocus} focus:ring-2`}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Model</label>
                  <select
                    disabled={!apiKeys.google}
                    className={`w-full p-3 border rounded-2xl ${themeClasses.input} ${themeClasses.inputFocus} focus:ring-2 disabled:opacity-50`}
                  >
                    {(availableModels.google || []).map(model => (
                      <option key={model.id} value={model.id}>{model.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* OpenRouter */}
              <div className="grid md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold mb-2">OpenRouter API Key</label>
                  <input
                    type="password"
                    placeholder="YOUR_API_KEYor-..."
                    value={apiKeys.openrouter}
                    onChange={(e) => setApiKeys(prev => ({...prev, openrouter: e.target.value}))}
                    className={`w-full p-3 border rounded-2xl ${themeClasses.input} ${themeClasses.inputFocus} focus:ring-2`}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Model</label>
                  <select
                    disabled={!apiKeys.openrouter}
                    className={`w-full p-3 border rounded-2xl ${themeClasses.input} ${themeClasses.inputFocus} focus:ring-2 disabled:opacity-50`}
                  >
                    {(availableModels.openrouter || []).map(model => (
                      <option key={model.id} value={model.id}>{model.name}</option>
                    ))}
                  </select>
                </div>
              </div>
              {/* GitHub */}
              <div className="grid md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-semibold mb-2">GitHub API Key</label>
                  <input
                    type="password"
                    placeholder="github_pat_..."
                    value={apiKeys.github}
                    onChange={(e) => setApiKeys(prev => ({...prev, github: e.target.value}))}
                    className={`w-full p-3 border rounded-2xl ${themeClasses.input} ${themeClasses.inputFocus} focus:ring-2`}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold mb-2">Model</label>
                  <select
                    disabled={!apiKeys.github}
                    className={`w-full p-3 border rounded-2xl ${themeClasses.input} ${themeClasses.inputFocus} focus:ring-2 disabled:opacity-50`}
                  >
                    {(availableModels.github || []).map(model => (
                      <option key={model.id} value={model.id}>{model.name}</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Debug Logs */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-lg font-semibold">Debug Logs</h4>
                  <button
                    type="button"
                    onClick={() => fetchLogs(false)}
                    className={`text-sm px-3 py-1 rounded-full border ${themeClasses.buttonSecondary}`}
                  >
                    Refresh
                  </button>
                </div>
                {logsError && (
                  <div className={`p-3 rounded-xl border ${themeClasses.errorBg}`}>
                    <p className="text-sm">{logsError}</p>
                  </div>
                )}
                <div
                  className={`border rounded-2xl p-3 ${themeClasses.cardBg} ${themeClasses.cardBorder} max-h-64 overflow-y-auto font-mono text-xs leading-relaxed`}
                  style={{ whiteSpace: 'pre-wrap' }}
                >
                  {logsLoading && !logs.length ? (
                    <p>Loading logs...</p>
                  ) : logs.length ? (
                    logs.map((line, idx) => (
                      <div key={`${idx}-${line}`}>{line}</div>
                    ))
                  ) : (
                    <p>No log entries yet.</p>
                  )}
                </div>
              </div>
            </div>
            
            <div className={`mt-6 p-4 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl`}>
              <h4 className="font-semibold mb-2 flex items-center">
                <Database className="h-4 w-4 mr-2" />
                Storage & Security
              </h4>
              <p className={`text-sm ${themeClasses.textMuted} mb-2`}>
                🔒 All API keys are stored locally in your browser (localStorage). They are never sent to our servers.
              </p>
              <p className={`text-sm ${themeClasses.textMuted}`}>
                🌐 Keys are transmitted directly to the respective AI providers for processing.
              </p>
            </div>
            
            <div className="mt-6 flex justify-between items-center">
              <div className="space-y-1">
                <p className={`text-sm ${themeClasses.textMuted}`}>
                  API keys are required for production use. Get your keys from:
                </p>
                <div className="flex space-x-4 text-xs">
                  <a href="https://platform.openai.com/api-keys" target="_blank" className="text-blue-500 hover:underline">OpenAI</a>
                  <a href="https://console.anthropic.com/" target="_blank" className="text-blue-500 hover:underline">Anthropic</a>
                  <a href="https://aistudio.google.com/app/apikey" target="_blank" className="text-blue-500 hover:underline">Google</a>
                  <a href="https://openrouter.ai/keys" target="_blank" className="text-blue-500 hover:underline">OpenRouter</a>
                  <a href="https://github.com/marketplace/models" target="_blank" className="text-blue-500 hover:underline">GitHub</a>
                </div>
              </div>
              <button 
                onClick={() => setShowSettings(false)}
                className={`px-6 py-3 rounded-full ${themeClasses.buttonPrimary} shadow-lg hover:scale-105 transition-all duration-300`}
              >
                Close Settings
              </button>
            </div>
          </div>
        )}

        {/* Quick Demo Section */}
        <div className="mb-12">
          <div className={`${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-3xl p-8 shadow-2xl`}>
            <h2 className="text-2xl font-bold mb-4 flex items-center">
              <Play className="h-6 w-6 mr-3" />
              Quick Demo
            </h2>
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
                  <div className="animate-spin mr-3 h-5 w-5 border-2 border-current border-t-transparent rounded-full" />
                  Running AI Demo...
                </>
              ) : (
                <>
                  <Zap className="mr-3 h-5 w-5" />
                  Run Quick Demo
                </>
              )}
            </button>

            {demoResult && (
              <DemoResults demoResult={demoResult} themeClasses={themeClasses} />
            )}
          </div>
        </div>

        {/* Main Interface */}
        <div className={`${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-3xl p-8 shadow-2xl`}>
          <h2 className="text-3xl font-bold mb-8 flex items-center">
            <GitBranch className="h-8 w-8 mr-3" />
            Generate Repository
          </h2>
          
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

            <div className="grid md:grid-cols-2 gap-6">
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

              <div>
                <label className={`block text-sm font-semibold ${themeClasses.text} mb-3`}>
                  AI Provider
                </label>
                <select
                  value={selectedProvider}
                  onChange={(e) => setSelectedProvider(e.target.value)}
                  className={`
                    w-full p-4 border rounded-2xl shadow-lg transition-all duration-300
                    ${themeClasses.input} ${themeClasses.inputFocus} focus:ring-2 focus:ring-offset-2
                    ${isDarkMode ? "focus:ring-offset-zinc-900" : "focus:ring-offset-white"}
                  `}
                >
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="google">Google/Gemini</option>
                  <option value="openrouter">OpenRouter</option>
                  <option value="github">GitHub Models</option>
                </select>
              </div>
            </div>

            <div>
              <label className={`block text-sm font-semibold ${themeClasses.text} mb-3 flex items-center`}>
                <Cpu className="h-4 w-4 mr-2" />
                AI Model
                {!hasApiKey(selectedProvider) && (
                  <span className={`ml-2 text-xs ${themeClasses.errorText} font-semibold`}>
                    (Requires API key in settings ⚠️)
                  </span>
                )}
              </label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                disabled={!hasApiKey(selectedProvider)}
                className={`
                  w-full p-4 border rounded-2xl shadow-lg transition-all duration-300
                  ${themeClasses.input} ${themeClasses.inputFocus} focus:ring-2 focus:ring-offset-2
                  ${isDarkMode ? "focus:ring-offset-zinc-900" : "focus:ring-offset-white"}
                  disabled:opacity-50 disabled:cursor-not-allowed
                `}
              >
                {getCurrentModels().map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name} - {model.description}
                  </option>
                ))}
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
                  ${themeClasses.buttonSecondary} border
                `}
              >
                {isPlanning ? (
                  <>
                    <div className="animate-spin mr-3 h-5 w-5 border-2 border-current border-t-transparent rounded-full" />
                    Planning with AI...
                  </>
                ) : (
                  <>
                    <FileText className="mr-3 h-5 w-5" />
                    Plan Repository
                  </>
                )}
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
                    <div className="animate-spin mr-3 h-5 w-5 border-2 border-current border-t-transparent rounded-full" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Terminal className="mr-3 h-5 w-5" />
                    Generate Repository
                  </>
                )}
              </button>
            </div>

            {/* Performance notice */}
            <div className={`p-4 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl text-sm ${themeClasses.textSecondary} shadow-lg flex items-center`}>
              <Clock className="h-4 w-4 mr-2" />
              <span className="font-semibold">AI Integration:</span> 
              <span className="ml-1">Planning uses GPT-4o-mini for intelligent feature generation. This takes 30-60 seconds for quality results.</span>
            </div>
          </div>
        </div>

        {/* Enhanced Live Job Progress */}
        {jobProgress && jobProgress.status === "running" && (
          <LiveProgressTracker 
            jobProgress={jobProgress} 
            generatedFiles={generatedFiles}
            themeClasses={themeClasses} 
          />
        )}

        {/* Error Display */}
        {error && (
          <div className={`mt-8 p-6 rounded-3xl shadow-xl ${themeClasses.errorBg} border flex items-start`}>
            <AlertCircle className={`h-6 w-6 ${themeClasses.errorText} mr-3 mt-1`} />
            <div>
              <h3 className={`font-bold text-lg ${themeClasses.errorText} mb-2`}>Error</h3>
              <p className={themeClasses.errorText}>{error}</p>
            </div>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <ResultsDisplay result={result} themeClasses={themeClasses} />
        )}
      </div>
    </div>
  );
};

// Enhanced Live Progress Component
const LiveProgressTracker = ({ jobProgress, generatedFiles, themeClasses }) => (
  <div className={`mt-8 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-3xl p-8 shadow-2xl`}>
    <h3 className="text-2xl font-bold mb-6 flex items-center">
      <Terminal className="h-6 w-6 mr-3 text-blue-500" />
      Live Generation Progress
    </h3>
    
    <div className="space-y-6">
      {/* Enhanced Progress Bar */}
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-lg font-bold">{jobProgress.progress}% Complete</span>
          <span className={`${themeClasses.textSecondary} font-medium flex items-center`}>
            <Clock className="h-4 w-4 mr-1" />
            {jobProgress.current_stage}
          </span>
        </div>
        
        <div className={`w-full ${isDarkMode ? "bg-zinc-700" : "bg-gray-200"} rounded-full h-4 shadow-inner`}>
          <div 
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-4 rounded-full transition-all duration-1000 shadow-lg relative overflow-hidden"
            style={{ width: `${jobProgress.progress}%` }}
          >
            <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
          </div>
        </div>
      </div>
      
      {/* Current Stage */}
      <div className={`${themeClasses.cardBg} ${themeClasses.cardBorder} border p-6 rounded-2xl shadow-xl`}>
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-3 h-3 bg-blue-500 rounded-full animate-pulse shadow-lg"></div>
          <span className="font-bold text-lg">Currently Processing</span>
        </div>
        <p className={`${themeClasses.textSecondary} ml-6 text-lg`}>
          {jobProgress.current_stage}
        </p>
      </div>
      
      {/* File Generation Progress */}
      {generatedFiles.length > 0 && (
        <div className={`${themeClasses.cardBg} ${themeClasses.cardBorder} border p-6 rounded-2xl shadow-xl`}>
          <h4 className="font-bold text-lg mb-4 flex items-center">
            <FileText className="h-5 w-5 mr-2" />
            Files Being Generated
          </h4>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {generatedFiles.map((file, idx) => (
              <div key={idx} className={`flex items-center space-x-3 p-3 rounded-xl ${themeClasses.cardBg} border ${themeClasses.cardBorder}`}>
                {file.status === 'completed' && <CheckCircle className="h-5 w-5 text-green-500" />}
                {file.status === 'in_progress' && <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />}
                {file.status === 'pending' && <Clock className="h-5 w-5 text-gray-400" />}
                
                <div className="flex-1">
                  <div className="font-mono text-sm">{file.name}</div>
                  <div className={`text-xs ${themeClasses.textMuted} capitalize`}>{file.status}</div>
                </div>
                
                {file.timestamp && (
                  <div className={`text-xs ${themeClasses.textMuted}`}>
                    {file.timestamp.toLocaleTimeString()}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Timeline */}
      <div className={`text-sm ${themeClasses.textMuted} space-y-2 p-4 rounded-2xl ${themeClasses.cardBg} border ${themeClasses.cardBorder}`}>
        <div className="flex items-center space-x-2">
          <Clock className="h-4 w-4" />
          <span>AI-powered generation typically takes 3-8 minutes for quality results</span>
        </div>
        <div className="flex items-center space-x-2">
          <Cpu className="h-4 w-4" />
          <span>The system is making real LLM calls for intelligent code generation</span>
        </div>
      </div>
    </div>
  </div>
);

// Demo Results Component
const DemoResults = ({ demoResult, themeClasses }) => (
  <div className={`mt-6 p-6 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl shadow-xl`}>
    <h3 className="text-xl font-bold mb-4 flex items-center">
      <CheckCircle className="h-5 w-5 mr-2 text-green-500" />
      Demo Results
    </h3>
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
          <h4 className="font-semibold mb-3 flex items-center">
            <Code className="h-4 w-4 mr-2" />
            Sample Features
          </h4>
          <div className={`${themeClasses.cardBg} ${themeClasses.cardBorder} border p-4 rounded-2xl text-sm font-mono space-y-2 max-h-48 overflow-y-auto shadow-inner`}>
            {demoResult.sample_features.slice(0, 6).map((feature, idx) => (
              <div key={idx} className={`${themeClasses.textSecondary} py-1 flex items-center`}>
                <CheckCircle className="h-3 w-3 mr-2 text-green-500" />
                {feature}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  </div>
);

// Results Display Component
const ResultsDisplay = ({ result, themeClasses }) => (
  <div className={`mt-8 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-3xl p-8 shadow-2xl`}>
    <h3 className="text-xl font-bold mb-6">
      {result.type === 'plan' ? 'Planning Results' : 'Generation Started'}
    </h3>
    
    {result.type === 'plan' && (
      <div className="space-y-6">
        <div className="grid grid-cols-3 gap-6">
          <div className={`text-center p-6 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl shadow-xl`}>
            <Database className="h-8 w-8 mx-auto mb-2 text-blue-500" />
            <div className="text-3xl font-bold mb-2">{result.data.metrics.total_features}</div>
            <div className={`text-sm font-medium ${themeClasses.textSecondary}`}>Features</div>
          </div>
          <div className={`text-center p-6 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl shadow-xl`}>
            <GitBranch className="h-8 w-8 mx-auto mb-2 text-purple-500" />
            <div className="text-3xl font-bold mb-2">{result.data.metrics.total_nodes}</div>
            <div className={`text-sm font-medium ${themeClasses.textSecondary}`}>Graph Nodes</div>
          </div>
          <div className={`text-center p-6 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-2xl shadow-xl`}>
            <Code className="h-8 w-8 mx-auto mb-2 text-green-500" />
            <div className="text-3xl font-bold mb-2">{result.data.metrics.total_edges}</div>
            <div className={`text-sm font-medium ${themeClasses.textSecondary}`}>Connections</div>
          </div>
        </div>
        
        {result.data.feature_paths && result.data.feature_paths.length > 0 && (
          <div>
            <h4 className="font-semibold text-lg mb-4 flex items-center">
              <Sparkles className="h-5 w-5 mr-2" />
              Sample Feature Paths
            </h4>
            <div className={`${themeClasses.cardBg} ${themeClasses.cardBorder} border p-6 rounded-2xl text-sm font-mono max-h-64 overflow-y-auto shadow-inner space-y-2`}>
              {result.data.feature_paths.slice(0, 12).map((fp, idx) => (
                <div key={idx} className="flex justify-between py-1">
                  <span className={themeClasses.text}>{fp.path}</span>
                  <span className={`${themeClasses.textMuted} text-xs capitalize`}>({fp.source})</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )}
  </div>
);

export default GenerationPage;
