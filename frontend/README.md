# Network Journal Frontend

A React-based frontend for the Network Journal application, featuring a full-screen interactive network graph visualization with a ChatGPT-style overlay interface.

## 🏗️ Architecture Overview

The frontend is built as a modern React application using:
- **React 19** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **D3.js** for graph visualization
- **Framer Motion** for animations
- **TanStack Query** for data fetching
- **Shadcn/ui** for UI components

## 📦 Project Structure

```
frontend/
├── src/
│   ├── api/                 # API layer
│   │   ├── client.ts        # Axios-based API client
│   │   └── queries.ts       # TanStack Query hooks
│   ├── components/
│   │   ├── layout/          # Layout components
│   │   └── ui/              # Shadcn/ui components
│   ├── graph/               # Graph visualization
│   │   └── d3-graph-view.tsx # Main D3.js graph component
│   ├── lib/
│   │   └── utils.ts         # Utility functions
│   ├── pages/
│   │   └── dashboard.tsx    # Main dashboard page
│   ├── types/
│   │   └── models.ts        # TypeScript interfaces
│   ├── App.tsx              # Root component
│   ├── index.css            # Global styles
│   └── main.tsx             # Entry point
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## 🚀 Setup Instructions

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. **Clone and navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Create environment file:**
```bash
# Create .env.local (optional - defaults to localhost:8000)
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
```

4. **Start development server:**
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## 🎨 Design System

### Color Scheme
The application uses a dark theme with neon accents:

- **Background**: `#111827` (gray-900)
- **Overlay Backgrounds**: `rgba(31, 41, 55, 0.8)` with backdrop blur
- **Neon Colors**:
  - People: `#3b82f6` (blue-500)
  - Companies: `#22c55e` (green-500)
  - Topics: `#eab308` (yellow-500)
  - Events: `#a21caf` (purple-600)
  - Locations: `#ec4899` (pink-500)
  - Interactions: `#8b5cf6` (violet-500)

### Typography
- **Primary Font**: System font stack
- **Text Sizes**: Tailwind's responsive scale
- **Font Weights**: 400 (normal), 500 (medium), 600 (semibold), 700 (bold)

### Spacing
- **Container Padding**: 16px (mobile) → 24px (tablet) → 32px (desktop)
- **Component Spacing**: 4px, 8px, 12px, 16px, 24px, 32px
- **Border Radius**: 8px (default), 12px (large), 16px (xl)

## 🔧 Core Components

### 1. Dashboard (`src/pages/dashboard.tsx`)

The main full-screen dashboard with overlay controls.

**Key Features:**
- Full-screen D3.js graph visualization
- ChatGPT-style search bar at bottom
- Overlay menu system with animations
- Real-time stats display
- Responsive design

**State Management:**
```typescript
const [isMenuOpen, setIsMenuOpen] = useState(false)
const [isGraphOptionsOpen, setIsGraphOptionsOpen] = useState(false)
const [searchQuery, setSearchQuery] = useState('')
const [activeFilters, setActiveFilters] = useState({
  people: true,
  companies: true,
  topics: true,
  events: true,
  locations: true,
  interactions: true,
})
```

**Layout Structure:**
```tsx
<div className="w-full h-screen bg-gray-900 relative overflow-hidden">
  {/* Full-screen graph */}
  <div className="absolute inset-0">
    <D3GraphView />
  </div>
  
  {/* Overlay controls */}
  {/* Menu button (top-left) */}
  {/* Graph options button (top-left, below menu) */}
  {/* Add button (top-right) */}
  {/* Stats overlay (top-center) */}
  {/* Search bar (bottom-center) */}
</div>
```

### 2. D3GraphView (`src/graph/d3-graph-view.tsx`)

The core graph visualization component using D3.js.

**Key Features:**
- Custom bouncy spring physics
- Neon glow effects with drop shadows
- Particle system for drag interactions
- Zoom and pan controls
- Responsive canvas sizing

**Physics Configuration:**
```typescript
const simulation = d3.forceSimulation<D3Node>(nodes)
  .force('link', createBouncySpringForce())
  .force('charge', d3.forceManyBody().strength(-200))
  .force('collision', d3.forceCollide().radius(30))
  .force('gravity', createCircularGravityForce())
  .force('center', d3.forceCenter(width / 2, height / 2))
  .alphaDecay(0.015)
  .velocityDecay(0.2)
```

**Custom Forces:**
- **Bouncy Spring Force**: Enhanced spring with overshoot effects
- **Circular Gravity**: Pulls nodes toward center with distance-based strength
- **Pulse Effects**: Nodes scale when connected via springs

**Visual Effects:**
- **Iridescent Gradients**: Radial gradients for node fills
- **Neon Glows**: Drop shadows with color-matched RGB values
- **Particle System**: Trail effects during node dragging
- **Text Fitting**: Truncated labels with ellipsis

### 3. API Layer (`src/api/`)

**Client (`client.ts`):**
- Axios-based HTTP client
- Request/response interceptors for logging
- Error handling and timeout configuration
- Base URL: `http://localhost:8000/api/v1`

**Queries (`queries.ts`):**
- TanStack Query hooks for all API endpoints
- Optimistic updates and cache invalidation
- Error handling and loading states
- Query key management

**Key Hooks:**
```typescript
// Data fetching
usePeople()
useCompanies()
useInteractions()
useGraphData()
useNetworkStats()

// Mutations
useCreatePerson()
useUpdatePerson()
useDeletePerson()
// ... similar for other entities
```

### 4. UI Components (`src/components/ui/`)

**Button (`button.tsx`):**
- Variant-based styling (default, destructive, outline, secondary, ghost, link)
- Size variants (default, sm, lg, icon)
- Framer Motion hover/tap animations
- Radix UI Slot support

**Input (`input.tsx`):**
- Standard form input with focus animations
- Tailwind styling with focus states
- Framer Motion scale effect on focus

**Card (`card.tsx`):**
- Container component with header, content, and footer sections
- Consistent border radius and padding
- Dark theme compatible

## 🎯 Key Implementation Details

### 1. Full-Screen Layout

**Global CSS (`src/index.css`):**
```css
body {
  margin: 0;
  padding: 0;
  overflow: hidden;
}

html {
  margin: 0;
  padding: 0;
  height: 100%;
}

#root {
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
}
```

**App Structure (`src/App.tsx`):**
```tsx
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

### 2. Graph Physics

**Spring Force Implementation:**
```typescript
const createBouncySpringForce = () => {
  return (alpha: number) => {
    linksRef.current.forEach(link => {
      // Calculate distance between nodes
      const dx = target.x - source.x
      const dy = target.y - source.y
      const distance = Math.sqrt(dx * dx + dy * dy)
      const idealLength = 50
      
      if (distance > 0) {
        // Enhanced bouncy spring with overshoot
        const springStrength = 0.4 * alpha
        const overshoot = Math.sin(distance / idealLength * Math.PI) * 0.15
        const force = (distance - idealLength) * springStrength * (1 + overshoot)
        
        // Apply forces
        const fx = (dx / distance) * force
        const fy = (dy / distance) * force
        
        source.x += fx
        source.y += fy
        target.x -= fx
        target.y -= fy
      }
    })
  }
}
```

**Circular Gravity:**
```typescript
const createCircularGravityForce = () => {
  return (alpha: number) => {
    const centerX = 0
    const centerY = 0
    const gravityStrength = 0.8 * alpha
    
    nodesRef.current.forEach(node => {
      const dx = centerX - node.x
      const dy = centerY - node.y
      const distance = Math.sqrt(dx * dx + dy * dy)
      
      if (distance > 0) {
        const gravity = gravityStrength * (distance / 200)
        node.x += (dx / distance) * gravity
        node.y += (dy / distance) * gravity
      }
    })
  }
}
```

### 3. Visual Effects

**Neon Glow Generation:**
```typescript
function hexToRgb(hex: string) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : { r: 255, g: 255, b: 255 }
}

// Applied as CSS filter
.style('filter', (d) => {
  const nodeType = NODE_TYPES.find(t => t.type === d.type)
  if (nodeType) {
    const color = nodeType.color
    const rgb = hexToRgb(color)
    return `drop-shadow(0 0 12px rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.8)) drop-shadow(0 0 6px rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.6))`
  }
})
```

**Particle System:**
```typescript
interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  life: number
  maxLife: number
  color: string
}

const createParticles = (x: number, y: number, color: string) => {
  for (let i = 0; i < 8; i++) {
    const angle = (Math.PI * 2 * i) / 8
    const speed = 2 + Math.random() * 3
    particlesRef.current.push({
      x, y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 1,
      maxLife: 30 + Math.random() * 20,
      color,
    })
  }
}
```

### 4. Animation System

**Framer Motion Integration:**
```typescript
// Dropdown animations
<motion.div
  initial={{ opacity: 0, y: -10, scale: 0.95 }}
  animate={{ opacity: 1, y: 0, scale: 1 }}
  exit={{ opacity: 0, y: -10, scale: 0.95 }}
  transition={{ duration: 0.2 }}
>
  {/* Dropdown content */}
</motion.div>

// Button hover effects
<motion.div
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.98 }}
  transition={{ type: 'spring', stiffness: 400, damping: 17 }}
>
  <Button />
</motion.div>
```

### 5. Data Flow

**Query Structure:**
```typescript
// Query keys for cache management
export const queryKeys = {
  people: ['people'] as const,
  person: (id: string) => ['people', id] as const,
  companies: ['companies'] as const,
  // ... etc
}

// Example query hook
export function usePeople() {
  return useQuery({
    queryKey: queryKeys.people,
    queryFn: async () => {
      const response = await api.getPeople()
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch people')
      }
      return response.data || []
    },
  })
}
```

**Mutation with Cache Updates:**
```typescript
export function useCreatePerson() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (person: CreatePersonRequest) => {
      const response = await api.createPerson(person)
      if (!response.success) {
        throw new Error(response.message || 'Failed to create person')
      }
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.people })
    },
  })
}
```

## 🎮 User Interactions

### 1. Graph Interactions
- **Drag**: Click and drag nodes to reposition
- **Zoom**: Mouse wheel to zoom in/out
- **Pan**: Click and drag empty space to pan
- **Particles**: Visual feedback during dragging

### 2. Menu System
- **Menu Button**: Top-left hamburger menu
- **Graph Options**: Web icon below menu button
- **Add Button**: Blue plus button top-right
- **Click Outside**: Closes dropdowns

### 3. Search Interface
- **Search Bar**: Bottom-center ChatGPT-style input
- **Quick Suggestions**: Clickable chips below search
- **Form Submission**: Enter key or search button

## 🔧 Configuration

### Environment Variables
```bash
VITE_API_BASE_URL=http://localhost:8000  # Backend API URL
```

### Build Configuration
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```

### Tailwind Configuration
```javascript
// tailwind.config.js
export default {
  darkMode: ["class"],
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // CSS custom properties for theming
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        // ... etc
      },
      keyframes: {
        "accordion-down": { /* ... */ },
        "accordion-up": { /* ... */ },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

## 🚀 Performance Considerations

### Current Optimizations
- **React Query**: Efficient caching and background updates
- **Framer Motion**: Hardware-accelerated animations
- **D3.js**: Efficient DOM manipulation
- **Tailwind**: Purged CSS for minimal bundle size

### Known Limitations
- **Graph Performance**: D3.js DOM manipulation becomes expensive with 500+ nodes
- **Particle System**: Creates/destroys DOM elements every frame
- **Drop Shadows**: CSS filters are expensive for many elements

## 🐛 Troubleshooting

### Common Issues

1. **Graph not rendering:**
   - Check browser console for D3.js errors
   - Verify API is returning graph data
   - Ensure container has proper dimensions

2. **Performance issues:**
   - Reduce number of nodes/edges
   - Disable particle effects
   - Simplify visual effects

3. **API connection errors:**
   - Verify backend is running on port 8000
   - Check CORS configuration
   - Review network tab for failed requests

### Debug Tools
- **React Query DevTools**: Available in development
- **Browser DevTools**: Network, Console, Performance tabs
- **D3.js Debugging**: Console logs for graph data and physics

## 📝 Development Notes

### Code Style
- **TypeScript**: Strict mode enabled
- **ESLint**: React hooks and TypeScript rules
- **Prettier**: Automatic code formatting
- **Conventions**: Functional components, hooks, descriptive naming

### Testing Strategy
- **Unit Tests**: Component testing with React Testing Library
- **Integration Tests**: API integration testing
- **Performance Tests**: Graph rendering with large datasets

### Deployment
- **Build**: `npm run build`
- **Preview**: `npm run preview`
- **Static Hosting**: Compatible with Vercel, Netlify, etc.

This frontend implementation provides a modern, performant, and visually appealing interface for the Network Journal application, with a focus on user experience and maintainable code architecture.
