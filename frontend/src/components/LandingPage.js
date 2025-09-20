import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  Zap, 
  Code, 
  GitBranch, 
  Cpu, 
  Sparkles, 
  ArrowRight, 
  CheckCircle, 
  Github,
  Twitter,
  Globe,
  Play,
  FileText,
  Database,
  Terminal
} from 'lucide-react';

const LandingPage = ({ isDarkMode, setIsDarkMode }) => {
  const [showPreview, setShowPreview] = useState(false);
  
  const themeClasses = {
    bg: isDarkMode ? "bg-zinc-900" : "bg-white",
    cardBg: isDarkMode ? "bg-zinc-800" : "bg-white",
    cardBorder: isDarkMode ? "border-zinc-700" : "border-gray-200",
    text: isDarkMode ? "text-white" : "text-black",
    textSecondary: isDarkMode ? "text-zinc-400" : "text-gray-600",
    textMuted: isDarkMode ? "text-zinc-500" : "text-gray-500",
    buttonPrimary: isDarkMode ? "bg-white text-black hover:bg-zinc-200" : "bg-black text-white hover:bg-gray-800",
    buttonSecondary: isDarkMode ? "bg-zinc-700 text-white hover:bg-zinc-600 border-zinc-600" : "bg-white text-gray-700 hover:bg-gray-50 border-gray-300",
    headerBorder: isDarkMode ? "border-zinc-800" : "border-gray-200",
    gradient: isDarkMode ? "from-zinc-800 to-zinc-900" : "from-gray-50 to-white"
  };

  const mockFiles = [
    { name: 'src/algorithms/regression.py', type: 'implementation', content: 'class LinearRegression:\\n    def fit(self, X, y):\\n        # Implementation here...' },
    { name: 'src/algorithms/classification.py', type: 'implementation', content: 'class LogisticRegression:\\n    def fit(self, X, y):\\n        # Implementation here...' },
    { name: 'tests/test_regression.py', type: 'test', content: 'import pytest\\ndef test_linear_regression():\\n    # Test cases here...' },
    { name: 'src/data/preprocessing.py', type: 'implementation', content: 'class StandardScaler:\\n    def transform(self, X):\\n        # Scaling logic...' },
    { name: 'src/evaluation/metrics.py', type: 'implementation', content: 'def accuracy_score(y_true, y_pred):\\n    # Accuracy calculation...' }
  ];

  const handlePreviewDemo = () => {
    setShowPreview(true);
    // Simulate file generation
    setTimeout(() => setShowPreview(false), 8000);
  };

  return (
    <div className={`min-h-screen ${themeClasses.bg} ${themeClasses.text} transition-colors duration-300`}>
      {/* Header */}
      <header className={`border-b ${themeClasses.headerBorder}`}>
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <GitBranch className="h-8 w-8" />
              <span className="text-2xl font-bold">ZeroRepo</span>
            </div>
            
            <div className="flex items-center space-x-4">
              <nav className="hidden md:flex space-x-6">
                <a href="#features" className={`${themeClasses.textSecondary} hover:${themeClasses.text} transition-colors`}>
                  Features
                </a>
                <a href="#how-it-works" className={`${themeClasses.textSecondary} hover:${themeClasses.text} transition-colors`}>
                  How it Works
                </a>
                <a href="#pricing" className={`${themeClasses.textSecondary} hover:${themeClasses.text} transition-colors`}>
                  Pricing
                </a>
              </nav>
              
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className={`rounded-full p-2 transition-all duration-300 ${
                  isDarkMode 
                    ? "bg-zinc-800 hover:bg-zinc-700 border border-zinc-600" 
                    : "bg-gray-100 hover:bg-gray-200 border border-gray-300"
                }`}
              >
                {isDarkMode ? (
                  <Sparkles className="h-4 w-4 text-yellow-400" />
                ) : (
                  <div className="h-4 w-4 rounded-full bg-gray-600"></div>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className={`py-20 bg-gradient-to-br ${themeClasses.gradient}`}>
        <div className="max-w-7xl mx-auto px-6">
          {/* Research Paper Attribution */}
          <div className="text-center mb-8">
            <div className={`inline-flex items-center px-6 py-3 ${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-full shadow-lg`}>
              <FileText className="h-4 w-4 mr-2 text-blue-500" />
              <span className={`text-sm ${themeClasses.textSecondary} mr-2`}>Based on the paper:</span>
              <a 
                href="https://arxiv.org/abs/2509.16198"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm font-medium text-blue-500 hover:text-blue-400 transition-colors underline"
              >
                Repository Planning Graphs for Agentic Software Development
              </a>
            </div>
          </div>

          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-6xl font-bold leading-tight mb-6">
                AI-Powered
                <span className="block bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
                  Repository Generation
                </span>
              </h1>
              <p className={`text-xl ${themeClasses.textSecondary} mb-8 leading-relaxed`}>
                ZeroRepo uses advanced graph-driven AI to plan, design, and generate complete software repositories. 
                From concept to code in minutes, not hours.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <button
                  onClick={handlePreviewDemo}
                  disabled={showPreview}
                  className={`
                    ${themeClasses.buttonSecondary} border
                    inline-flex items-center px-8 py-4 rounded-full text-lg font-semibold
                    shadow-2xl transition-all duration-300 transform hover:scale-105
                    disabled:opacity-50 disabled:transform-none
                  `}
                >
                  {showPreview ? (
                    <>
                      <Terminal className="animate-pulse mr-3 h-5 w-5" />
                      Generating Preview...
                    </>
                  ) : (
                    <>
                      <Play className="mr-3 h-5 w-5" />
                      Preview Demo
                    </>
                  )}
                </button>
                
                <Link
                  to="/generate"
                  className={`
                    ${themeClasses.buttonPrimary}
                    inline-flex items-center px-8 py-4 rounded-full text-lg font-semibold
                    shadow-2xl transition-all duration-300 transform hover:scale-105
                    text-center justify-center
                  `}
                >
                  <Zap className="mr-3 h-5 w-5" />
                  Try It Out
                </Link>
              </div>
              
              <div className="flex items-center space-x-6 text-sm">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className={themeClasses.textSecondary}>Real AI Integration</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className={themeClasses.textSecondary}>Test-Driven Development</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span className={themeClasses.textSecondary}>Multiple Domains</span>
                </div>
              </div>
            </div>
            
            {/* Preview Image/Demo */}
            <div className={`${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-3xl p-8 shadow-2xl`}>
              {showPreview ? (
                <div className="space-y-4">
                  <div className="flex items-center space-x-3 mb-6">
                    <Terminal className="h-6 w-6 text-blue-500" />
                    <span className="text-lg font-semibold">Repository Preview</span>
                  </div>
                  
                  {mockFiles.map((file, idx) => (
                    <div
                      key={file.name}
                      className={`
                        ${themeClasses.cardBg} ${themeClasses.cardBorder} border p-4 rounded-2xl
                        transition-all duration-500 transform
                        ${idx < Math.floor((Date.now() / 1000) % 10) ? 'opacity-100 translate-y-0' : 'opacity-50 translate-y-2'}
                      `}
                    >
                      <div className="flex items-center space-x-3 mb-2">
                        {file.type === 'test' ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <FileText className="h-4 w-4 text-blue-500" />
                        )}
                        <span className="font-mono text-sm">{file.name}</span>
                      </div>
                      <div className={`text-xs font-mono ${themeClasses.textMuted} bg-opacity-50 p-2 rounded overflow-hidden`}>
                        {file.content}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center space-y-6">
                  <div className="relative">
                    <div className={`w-full h-64 ${themeClasses.cardBorder} border-2 border-dashed rounded-2xl flex items-center justify-center`}>
                      <div className="text-center">
                        <Code className="h-16 w-16 mx-auto mb-4 text-gray-400" />
                        <p className={`${themeClasses.textSecondary} text-lg`}>
                          Your repository will appear here
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold">27</div>
                      <div className={`text-sm ${themeClasses.textSecondary}`}>Features</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">45</div>
                      <div className={`text-sm ${themeClasses.textSecondary}`}>Files</div>
                    </div>
                    <div>
                      <div className="text-2xl font-bold">98%</div>
                      <div className={`text-sm ${themeClasses.textSecondary}`}>Success Rate</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Powerful Features</h2>
            <p className={`text-xl ${themeClasses.textSecondary} max-w-3xl mx-auto`}>
              ZeroRepo combines cutting-edge AI with graph theory to generate production-ready repositories
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <FeatureCard
              icon={<GitBranch className="h-8 w-8 text-blue-500" />}
              title="Graph-Driven Planning"
              description="Uses Repository Planning Graphs (RPG) to model capabilities, dependencies, and data flows"
              themeClasses={themeClasses}
            />
            <FeatureCard
              icon={<Cpu className="h-8 w-8 text-purple-500" />}
              title="AI-Powered Generation"
              description="Leverages GPT-4, Claude, and Gemini for intelligent code generation and architecture design"
              themeClasses={themeClasses}
            />
            <FeatureCard
              icon={<CheckCircle className="h-8 w-8 text-green-500" />}
              title="Test-Driven Development"
              description="Generates comprehensive tests and iteratively improves code until all tests pass"
              themeClasses={themeClasses}
            />
            <FeatureCard
              icon={<Database className="h-8 w-8 text-orange-500" />}
              title="Multi-Domain Support"
              description="Supports ML, web development, data processing, and general software projects"
              themeClasses={themeClasses}
            />
            <FeatureCard
              icon={<Terminal className="h-8 w-8 text-red-500" />}
              title="CLI & API Access"
              description="Full CLI interface and REST API for integration into your development workflow"
              themeClasses={themeClasses}
            />
            <FeatureCard
              icon={<Sparkles className="h-8 w-8 text-yellow-500" />}
              title="Intelligent Features"
              description="Uses explore/exploit/missing strategies to ensure comprehensive feature coverage"
              themeClasses={themeClasses}
            />
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className={`py-20 bg-gradient-to-br ${themeClasses.gradient}`}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">How It Works</h2>
            <p className={`text-xl ${themeClasses.textSecondary} max-w-3xl mx-auto`}>
              Three-stage AI pipeline that transforms your idea into a complete repository
            </p>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8">
            <ProcessStep
              number="A"
              title="Proposal Construction"
              description="AI analyzes your goal and generates a comprehensive feature set using explore/exploit/missing strategies"
              icon={<Sparkles className="h-6 w-6" />}
              themeClasses={themeClasses}
            />
            <ProcessStep
              number="B"
              title="Implementation Design"
              description="Converts features into file structure, interfaces, and data flow architecture"
              icon={<Code className="h-6 w-6" />}
              themeClasses={themeClasses}
            />
            <ProcessStep
              number="C"
              title="Code Generation"
              description="Generates actual Python code with comprehensive tests using topological traversal"
              icon={<Terminal className="h-6 w-6" />}
              themeClasses={themeClasses}
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={`border-t ${themeClasses.headerBorder} py-12`}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <GitBranch className="h-6 w-6" />
                <span className="text-xl font-bold">ZeroRepo</span>
              </div>
              <p className={`${themeClasses.textSecondary} mb-4 max-w-md`}>
                Graph-driven repository generation powered by advanced AI. 
                Transform your ideas into production-ready code.
              </p>
              <div className="flex space-x-4">
                <a href="#" className={`${themeClasses.textSecondary} hover:${themeClasses.text} transition-colors`}>
                  <Github className="h-5 w-5" />
                </a>
                <a href="#" className={`${themeClasses.textSecondary} hover:${themeClasses.text} transition-colors`}>
                  <Twitter className="h-5 w-5" />
                </a>
                <a href="#" className={`${themeClasses.textSecondary} hover:${themeClasses.text} transition-colors`}>
                  <Globe className="h-5 w-5" />
                </a>
              </div>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Product</h3>
              <ul className="space-y-2">
                <li><a href="#" className={`${themeClasses.textSecondary} hover:${themeClasses.text} transition-colors text-sm`}>Features</a></li>
                <li><a href="#" className={`${themeClasses.textSecondary} hover:${themeClasses.text} transition-colors text-sm`}>Pricing</a></li>
                <li><a href="#" className={`${themeClasses.textSecondary} hover:${themeClasses.text} transition-colors text-sm`}>Documentation</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold mb-4">Company</h3>
              <ul className="space-y-2">
                <li><a href="#" className={`${themeClasses.textSecondary} hover:${themeClasses.text} transition-colors text-sm`}>About</a></li>
                <li><a href="#" className={`${themeClasses.textSecondary} hover:${themeClasses.text} transition-colors text-sm`}>Blog</a></li>
                <li><a href="#" className={`${themeClasses.textSecondary} hover:${themeClasses.text} transition-colors text-sm`}>Contact</a></li>
              </ul>
            </div>
          </div>
          
          <div className={`border-t ${themeClasses.headerBorder} mt-12 pt-8 text-center`}>
            <p className={`${themeClasses.textMuted} text-sm`}>
              © 2025 ZeroRepo. Built with the Emergent platform.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

const FeatureCard = ({ icon, title, description, themeClasses }) => (
  <div className={`${themeClasses.cardBg} ${themeClasses.cardBorder} border rounded-3xl p-6 shadow-2xl transition-all duration-300 hover:shadow-3xl hover:-translate-y-1`}>
    <div className="mb-4">{icon}</div>
    <h3 className="text-xl font-bold mb-3">{title}</h3>
    <p className={`${themeClasses.textSecondary}`}>{description}</p>
  </div>
);

const ProcessStep = ({ number, title, description, icon, themeClasses }) => (
  <div className="text-center">
    <div className={`w-20 h-20 ${themeClasses.buttonPrimary} rounded-full flex items-center justify-center mx-auto mb-6 shadow-2xl`}>
      <span className="text-2xl font-bold">{number}</span>
    </div>
    <h3 className="text-xl font-bold mb-4 flex items-center justify-center space-x-2">
      {icon}
      <span>{title}</span>
    </h3>
    <p className={`${themeClasses.textSecondary} text-lg`}>{description}</p>
  </div>
);

export default LandingPage;