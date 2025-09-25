# ZeroRepo Frontend

React-based frontend for the ZeroRepo graph-driven repository generation system.

## 🎨 Features

### Pages
- **Landing Page** (`/`) - Hero, features, demo, and research attribution
- **Generation Page** (`/generate`) - Full repository generation interface

### Components
- **Dark/Light Mode** - Seamless theme switching with localStorage persistence
- **Provider Selection** - Multi-provider LLM configuration
- **Live Progress** - Real-time generation tracking with file-level granularity
- **API Settings** - Secure localStorage-based API key management

## 🛠️ Technical Stack

### Core Technologies
- **React 19** - Latest React with concurrent features
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first styling with custom design system
- **Lucide Icons** - Professional iconography
- **Axios** - HTTP client for API communication

### Design System
- **Dark Mode** - Zinc-900 backgrounds with zinc-800 cards
- **Light Mode** - Clean whites with gray accents
- **Rounded Corners** - XL rounded corners (`rounded-3xl`)
- **Shadows** - Beautiful drop shadows (`shadow-2xl`)
- **Buttons** - Fully rounded pill-shaped buttons
- **Typography** - Professional hierarchy with proper contrast

## 🔧 Setup

### Installation
```bash
cd frontend
yarn install
```

### Development
```bash
yarn start
```

### Build
```bash
yarn build
```

## 🔑 API Key Management

### Security Model
- **Client-Side Storage** - All API keys stored in browser localStorage
- **Never Server-Side** - Keys never transmitted to ZeroRepo servers
- **Direct Provider Communication** - Keys sent directly to AI providers
- **Automatic Persistence** - Keys saved/loaded automatically

### Supported Providers
```javascript
// Stored in localStorage as 'zerorepo_api_keys'
{
  openai: "sk-...",
  anthropic: "sk-ant-...",
  google: "AI...",
  openrouter: "sk-or-...",
  github: "github_pat_..."
}
```

## 🎯 User Flow

### Landing Page
1. **Hero Section** - Research attribution and value proposition
2. **Preview Demo** - Visual file preview (no API calls)
3. **Real AI Demo** - Actual GPT-4o-mini showcase (~30 seconds)
4. **Features** - Comprehensive capability overview
5. **How It Works** - Three-stage process explanation

### Generation Page
1. **API Configuration** - Settings panel with provider selection
2. **Project Input** - Goal description and domain selection
3. **Provider/Model Selection** - Dynamic dropdown based on available keys
4. **Live Generation** - Real-time progress with file tracking
5. **Results Display** - Professional visualization of generated repositories

## 🎨 Design Guidelines

### Theme System
```javascript
const themeClasses = {
  bg: isDarkMode ? "bg-zinc-900" : "bg-white",
  cardBg: isDarkMode ? "bg-zinc-800" : "bg-white",
  text: isDarkMode ? "text-white" : "text-black",
  buttonPrimary: isDarkMode ? "bg-white text-black" : "bg-black text-white"
}
```

### Component Standards
- **Rounded Corners** - Use `rounded-3xl` for cards, `rounded-2xl` for inputs
- **Shadows** - Use `shadow-2xl` for primary elements, `shadow-xl` for secondary
- **Buttons** - Always `rounded-full` with hover scale effects
- **Icons** - Lucide icons with consistent sizing (h-4/5/6 w-4/5/6)
- **Spacing** - Use space-y-6/8 for sections, space-x-4 for inline elements

## 📱 Responsive Design

### Breakpoints
- **Mobile** - Single column layouts, stacked buttons
- **Tablet** - Two-column grids for forms
- **Desktop** - Full grid layouts with optimal spacing

### Accessibility
- **Keyboard Navigation** - Full keyboard support
- **Focus States** - Visible focus rings on all interactive elements
- **Color Contrast** - WCAG compliant contrast ratios
- **Screen Readers** - Proper ARIA labels and semantic HTML

## 🚀 Performance

### Optimization Features
- **Code Splitting** - Route-based splitting
- **Image Optimization** - Lazy loading and proper sizing
- **API Caching** - Model lists cached client-side
- **State Management** - Efficient React state updates

### Bundle Analysis
```bash
yarn build
npx webpack-bundle-analyzer build/static/js/*.js
```

## 🧪 Development

### Component Structure
```
src/
├── App.js                 # Main app with routing
├── components/
│   ├── LandingPage.js    # Landing page with hero and features
│   └── GenerationPage.js # Repository generation interface
├── hooks/                # Custom React hooks
└── lib/                  # Utility functions
```

### Adding New Providers
1. Update `/api/models` endpoint in backend
2. Add provider to dropdown options
3. Update localStorage key structure
4. Add provider-specific model handling

---

*Built with React 19, Tailwind CSS, and Lucide Icons*