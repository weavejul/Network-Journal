import React, { useEffect, useRef, useState, useCallback } from 'react'
import cytoscape from 'cytoscape'
import type { Core, ElementDefinition } from 'cytoscape'
import fcose from 'cytoscape-fcose'
import coseBilkent from 'cytoscape-cose-bilkent'
import dagre from 'cytoscape-dagre'
import klay from 'cytoscape-klay'
import euler from 'cytoscape-euler'
import layoutUtilities from 'cytoscape-layout-utilities'
import { useGraphData } from '../api/queries'
import { Card } from '../components/ui/card'
import { Checkbox } from '../components/ui/checkbox'
import type { GraphData, GraphNode, GraphEdge } from '../types/models'

// Register layouts
cytoscape.use(fcose)
cytoscape.use(coseBilkent)
cytoscape.use(dagre)
cytoscape.use(klay)
cytoscape.use(euler)
cytoscape.use(layoutUtilities)

const NODE_TYPES = [
  { type: 'person', label: 'People', color: 'bg-blue-500' },
  { type: 'company', label: 'Companies', color: 'bg-green-500' },
  { type: 'topic', label: 'Topics', color: 'bg-yellow-500' },
  { type: 'event', label: 'Events', color: 'bg-purple-500' },
  { type: 'location', label: 'Locations', color: 'bg-pink-500' },
  // Add more as needed
]

const OWNER_NAME = 'Alice'

function getNodeColor(type: string) {
  const found = NODE_TYPES.find(n => n.type === type)
  return found ? found.color : 'bg-gray-400'
}

export function GraphView() {
  const cyRef = useRef<Core | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [filters, setFilters] = useState<Record<string, boolean>>(() => Object.fromEntries(NODE_TYPES.map(n => [n.type, true])))
  const { data, isLoading, error } = useGraphData()
  const [layoutName, setLayoutName] = useState<'fcose' | 'cose-bilkent'>('fcose')

  // Transform API data to Cytoscape elements
  const makeElements = useCallback((graph: GraphData | undefined, filters: Record<string, boolean>): ElementDefinition[] => {
    if (!graph) return []
    // Only include nodes of enabled types
    const nodes = graph.nodes.filter(n => filters[n.type])
    const nodeIds = new Set(nodes.map(n => n.id))
    // Only include edges where both source and target are visible
    const edges = graph.edges.filter(e => nodeIds.has(e.source) && nodeIds.has(e.target))
    return [
      ...nodes.map(n => ({
        data: {
          id: n.id,
          label: n.label,
          type: n.type,
          ...n.properties,
        },
        classes: n.label === OWNER_NAME ? 'owner-node' : n.type + '-node',
      })),
      ...edges.map(e => ({
        data: {
          id: e.id,
          source: e.source,
          target: e.target,
          type: e.type,
          ...e.properties,
        },
        classes: e.type + '-edge',
      })),
    ]
  }, [])

  // Store original positions for snap-back
  const originalPositions = useRef<Map<string, { x: number; y: number }>>(new Map())

  // Custom bouncy animation function
  function animateWithBounce(node: any, targetPos: { x: number; y: number }, duration: number = 800) {
    const startPos = node.position()
    const startTime = Date.now()
    
    function animate() {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      
      // Create a bouncy effect by overshooting and bouncing back
      const bounceProgress = 1 - Math.pow(1 - progress, 3) // Cubic ease-out
      const overshoot = Math.sin(progress * Math.PI * 2) * 0.1 * (1 - progress) // Overshoot effect
      
      const currentX = startPos.x + (targetPos.x - startPos.x) * (bounceProgress + overshoot)
      const currentY = startPos.y + (targetPos.y - startPos.y) * (bounceProgress + overshoot)
      
      node.position({ x: currentX, y: currentY })
      
      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }
    
    requestAnimationFrame(animate)
  }

  // Cytoscape stylesheet - using any[] since Stylesheet type isn't exported
  const cyStyles: any[] = [
    {
      selector: 'node',
      style: {
        'background-color': '#64748b', // fallback
        'label': 'data(label)',
        'color': '#fff',
        'text-valign': 'center',
        'text-halign': 'center',
        'font-size': 14,
        'width': 40,
        'height': 40,
        'transition-property': 'background-color, width, height',
        'transition-duration': '300ms',
        'z-index': 10,
        'border-width': 2,
        'border-color': '#fff',
        'text-outline-width': 2,
        'text-outline-color': '#64748b',
      },
    },
    ...NODE_TYPES.map(n => ({
      selector: `node.${n.type}-node`,
      style: {
        'background-color': getTailwindColor(n.color),
        'text-outline-color': getTailwindColor(n.color),
      },
    })),
    {
      selector: 'node.owner-node',
      style: {
        'background-color': '#f59e42',
        'border-color': '#fbbf24',
        'border-width': 4,
        'width': 60,
        'height': 60,
        'font-size': 18,
        'z-index': 20,
        'text-outline-color': '#f59e42',
      },
    },
    {
      selector: 'edge',
      style: {
        'width': 2,
        'line-color': '#cbd5e1',
        'target-arrow-color': '#cbd5e1',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'transition-property': 'line-color, width',
        'transition-duration': '300ms',
      },
    },
    {
      selector: ':selected',
      style: {
        'border-color': '#fbbf24',
        'border-width': 6,
        'line-color': '#fbbf24',
        'target-arrow-color': '#fbbf24',
      },
    },
    {
      selector: '.connected',
      style: {
        'background-color': '#fef3c7',
        'border-color': '#f59e0b',
        'border-width': 3,
        'z-index': 15,
      },
    },
    {
      selector: '.selected-edge',
      style: {
        'line-color': '#f59e0b',
        'width': 4,
        'target-arrow-color': '#f59e0b',
        'z-index': 15,
      },
    },
  ]

  // Helper to convert Tailwind color to hex
  function getTailwindColor(tw: string): string {
    switch (tw) {
      case 'bg-blue-500': return '#3b82f6'
      case 'bg-green-500': return '#22c55e'
      case 'bg-yellow-500': return '#eab308'
      case 'bg-purple-500': return '#a21caf'
      case 'bg-pink-500': return '#ec4899'
      default: return '#64748b'
    }
  }

  // Initialize Cytoscape
  useEffect(() => {
    if (!containerRef.current) return
    if (cyRef.current) {
      cyRef.current.destroy()
      cyRef.current = null
    }
    
    const cy = cytoscape({
      container: containerRef.current,
      elements: makeElements(data, filters),
      style: cyStyles,
      layout: {
        name: layoutName,
        animate: true,
        randomize: false,
        fit: true,
        nodeDimensionsIncludeLabels: true,
        // Circular physics with stronger center gravity
        gravity: 1.2, // Much stronger gravity towards center
        nodeRepulsion: 15000, // Higher repulsion for more bounce
        idealEdgeLength: 60, // Shorter edges for tighter circular layout
        edgeElasticity: 0.9, // Very elastic edges (rubbery)
        nestingFactor: 0.5, // Less nesting for more spread
        gravityRangeCompound: 3.0, // Much stronger compound gravity
        gravityCompound: 2.0, // More compound gravity
        initialEnergyOnIncremental: 0.1, // Very low initial energy for more movement
        // Circular layout parameters
        center: { x: 0, y: 0 }, // Center gravity point
        gravityRange: 2000, // Large gravity range for circular effect
        // Force circular arrangement
        nodeRepulsionRange: 200, // Nodes repel each other more strongly
        nodeRepulsionRangeMax: 400, // Maximum repulsion range
      } as any,
      wheelSensitivity: 0.2,
      minZoom: 0.1,
      maxZoom: 2,
      motionBlur: true,
      textureOnViewport: true,
      pixelRatio: 'auto',
    })
    cyRef.current = cy

    // Center on Alice
    const aliceNode = cy.nodes().filter(n => n.data('label') === OWNER_NAME)
    if (aliceNode.length > 0) {
      // Position Alice at the center
      aliceNode.position({ x: 0, y: 0 })
      cy.center(aliceNode)
      aliceNode.select()
    }

    // Event handlers for dynamic updates
    let layoutTimeout: NodeJS.Timeout | null = null

    // Store original positions after initial layout
    cy.on('layoutstop', () => {
      cy.nodes().forEach(node => {
        const pos = node.position()
        originalPositions.current.set(node.id(), { x: pos.x, y: pos.y })
      })
    })

    // Dynamic physics restart when nodes are dragged
    cy.on('dragfreeon', 'node', () => {
      // Clear any existing timeout
      if (layoutTimeout) {
        clearTimeout(layoutTimeout)
      }
      
      // Restart full physics layout for maximum bounciness
      layoutTimeout = setTimeout(() => {
        cy.layout({
          name: layoutName,
          animate: true,
          fit: false, // Don't fit to viewport when restarting
          nodeDimensionsIncludeLabels: true,
          // Circular physics with stronger center gravity
          gravity: 1.2, // Much stronger gravity towards center
          nodeRepulsion: 15000, // Higher repulsion for more bounce
          idealEdgeLength: 60, // Shorter edges for tighter circular layout
          edgeElasticity: 0.9, // Very elastic edges (rubbery)
          nestingFactor: 0.5, // Less nesting for more spread
          gravityRangeCompound: 3.0, // Much stronger compound gravity
          gravityCompound: 2.0, // More compound gravity
          initialEnergyOnIncremental: 0.1, // Very low initial energy for more movement
          // Circular layout parameters
          center: { x: 0, y: 0 }, // Center gravity point
          gravityRange: 2000, // Large gravity range for circular effect
          // Force circular arrangement
          nodeRepulsionRange: 200, // Nodes repel each other more strongly
          nodeRepulsionRangeMax: 400, // Maximum repulsion range
        } as any).run()
      }, 50) // Shorter delay for more responsive feel
    })

    // Node selection highlighting
    cy.on('select', 'node', (event) => {
      const node = event.target
      // Highlight connected nodes
      const connected = node.neighborhood().nodes()
      connected.addClass('connected')
      // Highlight edges
      node.connectedEdges().addClass('selected-edge')
    })

    cy.on('unselect', 'node', () => {
      // Remove highlighting
      cy.nodes().removeClass('connected')
      cy.edges().removeClass('selected-edge')
    })

    // Handle data changes (filters, new data)
    cy.on('add remove data', () => {
      // Clear any existing timeout
      if (layoutTimeout) {
        clearTimeout(layoutTimeout)
      }
      
      cy.layout({
        name: layoutName,
        animate: true,
        fit: true,
        nodeDimensionsIncludeLabels: true,
        // Circular physics with stronger center gravity
        gravity: 1.2, // Much stronger gravity towards center
        nodeRepulsion: 15000, // Higher repulsion for more bounce
        idealEdgeLength: 60, // Shorter edges for tighter circular layout
        edgeElasticity: 0.9, // Very elastic edges (rubbery)
        nestingFactor: 0.5, // Less nesting for more spread
        gravityRangeCompound: 3.0, // Much stronger compound gravity
        gravityCompound: 2.0, // More compound gravity
        initialEnergyOnIncremental: 0.1, // Very low initial energy for more movement
        // Circular layout parameters
        center: { x: 0, y: 0 }, // Center gravity point
        gravityRange: 2000, // Large gravity range for circular effect
        // Force circular arrangement
        nodeRepulsionRange: 200, // Nodes repel each other more strongly
        nodeRepulsionRangeMax: 400, // Maximum repulsion range
      } as any).run()
    })

    // Responsive resize
    const handleResize = () => cy.resize()
    window.addEventListener('resize', handleResize)
    
    return () => {
      window.removeEventListener('resize', handleResize)
      if (layoutTimeout) {
        clearTimeout(layoutTimeout)
      }
      cy.destroy()
    }
    // eslint-disable-next-line
  }, [containerRef, data, filters, layoutName])

  // Handle filter changes
  function handleFilterChange(type: string) {
    setFilters(f => ({ ...f, [type]: !f[type] }))
  }

  // Layout switcher (optional)
  function handleLayoutChange(e: React.ChangeEvent<HTMLSelectElement>) {
    setLayoutName(e.target.value as 'fcose' | 'cose-bilkent')
  }

  // Reset layout function
  function resetLayout() {
    if (cyRef.current) {
      cyRef.current.layout({
        name: layoutName,
        animate: true,
        fit: true,
        nodeDimensionsIncludeLabels: true,
        // Circular physics with stronger center gravity
        gravity: 1.2, // Much stronger gravity towards center
        nodeRepulsion: 15000, // Higher repulsion for more bounce
        idealEdgeLength: 60, // Shorter edges for tighter circular layout
        edgeElasticity: 0.9, // Very elastic edges (rubbery)
        nestingFactor: 0.5, // Less nesting for more spread
        gravityRangeCompound: 3.0, // Much stronger compound gravity
        gravityCompound: 2.0, // More compound gravity
        initialEnergyOnIncremental: 0.1, // Very low initial energy for more movement
        // Circular layout parameters
        center: { x: 0, y: 0 }, // Center gravity point
        gravityRange: 2000, // Large gravity range for circular effect
        // Force circular arrangement
        nodeRepulsionRange: 200, // Nodes repel each other more strongly
        nodeRepulsionRangeMax: 400, // Maximum repulsion range
      } as any).run()
    }
  }

  return (
    <Card className="p-4 w-full h-[600px] flex flex-col">
      <div className="flex items-center gap-4 mb-4">
        <span className="font-semibold text-foreground">Show:</span>
        {NODE_TYPES.map(n => (
          <label key={n.type} className="flex items-center gap-1 text-sm">
            <Checkbox checked={filters[n.type]} onCheckedChange={() => handleFilterChange(n.type)} />
            <span className={`capitalize ${n.color} text-white px-2 py-1 rounded`}>{n.label}</span>
          </label>
        ))}
        <span className="ml-auto flex items-center gap-2">
          <select value={layoutName} onChange={handleLayoutChange} className="border rounded px-2 py-1 bg-background text-foreground">
            <option value="fcose">fCoSE (Physics)</option>
            <option value="cose-bilkent">COSE-Bilkent</option>
          </select>
          <button 
            onClick={resetLayout}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors text-sm"
          >
            Reset Layout
          </button>
        </span>
      </div>
      <div ref={containerRef} className="flex-1 w-full h-full rounded-lg border border-muted-foreground/20 bg-muted" />
      {isLoading && <div className="absolute inset-0 flex items-center justify-center bg-background/80 z-10"><span className="text-muted-foreground">Loading network...</span></div>}
      {error && <div className="text-red-500 mt-2">Error loading graph: {String(error)}</div>}
    </Card>
  )
}

export default GraphView 