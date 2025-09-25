# ZeroRepo Frontend Components

React components for the ZeroRepo user interface.

## 🧩 Component Structure

### Pages
- **`LandingPage.js`** - Marketing page with hero, features, and demo
- **`GenerationPage.js`** - Repository generation interface

### Shared Components
- **Theme System** - Consistent dark/light mode theming
- **Icon Integration** - Lucide React icons throughout
- **Form Components** - Styled inputs, selects, and buttons

## 🎨 Design System

### Theme Classes
```javascript
const themeClasses = {
  bg: isDarkMode ? "bg-zinc-900" : "bg-white",
  cardBg: isDarkMode ? "bg-zinc-800" : "bg-white",
  cardBorder: isDarkMode ? "border-zinc-700" : "border-gray-200",
  text: isDarkMode ? "text-white" : "text-black",
  buttonPrimary: isDarkMode ? "bg-white text-black" : "bg-black text-white"
}
```

### Component Standards
- **Rounded Corners** - `rounded-3xl` for cards, `rounded-2xl` for inputs
- **Shadows** - `shadow-2xl` for elevation and depth
- **Buttons** - `rounded-full` pill-shaped with hover effects
- **Spacing** - Consistent `space-y-6/8` and `space-x-4`
- **Typography** - Professional hierarchy with proper contrast

## 🔧 Component Features

### LandingPage
- **Hero Section** - Research attribution and value proposition
- **Preview Demo** - Visual repository preview
- **Real AI Demo** - Actual AI showcase with results
- **Features Grid** - 6 feature cards with colored icons
- **Process Flow** - Three-stage explanation
- **Professional Footer** - Complete with social links

### GenerationPage  
- **API Configuration** - Settings panel with 5 providers
- **Provider Selection** - Dynamic model loading
- **Live Progress** - Real-time job tracking
- **Results Display** - Professional metrics visualization
- **Error Handling** - Comprehensive error states

## 🔑 State Management

### API Key Storage
```javascript
// localStorage-based security
const savedKeys = localStorage.getItem('zerorepo_api_keys');
const apiKeys = JSON.parse(savedKeys || '{}');

// Auto-save on changes
useEffect(() => {
  localStorage.setItem('zerorepo_api_keys', JSON.stringify(apiKeys));
}, [apiKeys]);
```

### Theme Persistence
- **Local Storage** - Theme preference saved
- **System Detection** - Respect system dark mode
- **Smooth Transitions** - Animated theme switching

## 🎯 User Experience

### Progressive Enhancement
1. **Landing Page** - Instant value proposition
2. **Preview Demo** - Visual preview (no API calls)
3. **Real Demo** - AI showcase (~30 seconds)
4. **Full Generation** - Complete repository creation

### Error States
- **API Key Missing** - Clear configuration guidance
- **Generation Errors** - Helpful error messages
- **Network Issues** - Graceful degradation
- **Loading States** - Professional spinners and progress

## 📱 Responsive Design

### Breakpoints
- **Mobile** - Single column, stacked elements
- **Tablet** - Two-column grids
- **Desktop** - Full grid layouts

### Accessibility
- **Keyboard Navigation** - Full keyboard support
- **Focus Management** - Visible focus indicators
- **Screen Readers** - Semantic HTML and ARIA labels
- **Color Contrast** - WCAG compliant ratios

---

*Professional React components for ZeroRepo interface*