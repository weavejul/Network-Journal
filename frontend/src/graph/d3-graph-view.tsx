import React, { useEffect, useRef, useState, useCallback } from 'react'
import * as d3 from 'd3'
import { useGraphData } from '../api/queries'
import type { GraphData, GraphNode, GraphEdge } from '../types/models'

const NODE_TYPES = [
  { type: 'person', label: 'People', color: '#3b82f6', gradient: ['#000000', '#1a1a1a'] },
  { type: 'company', label: 'Companies', color: '#22c55e', gradient: ['#000000', '#1a1a1a'] },
  { type: 'topic', label: 'Topics', color: '#eab308', gradient: ['#000000', '#1a1a1a'] },
  { type: 'event', label: 'Events', color: '#a21caf', gradient: ['#000000', '#1a1a1a'] },
  { type: 'location', label: 'Locations', color: '#ec4899', gradient: ['#000000', '#1a1a1a'] },
  { type: 'interaction', label: 'Interactions', color: '#8b5cf6', gradient: ['#000000', '#1a1a1a'] },
]

const OWNER_NAME = 'Alice Johnson'

// Helper function to convert hex to RGB
function hexToRgb(hex: string) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : { r: 255, g: 255, b: 255 }
}

interface D3Node extends d3.SimulationNodeDatum {
  id: string
  label: string
  type: string
  properties: any
  isOwner: boolean
  originalX?: number
  originalY?: number
  velocity?: { x: number; y: number }
  pulse?: number
}

interface D3Link extends d3.SimulationLinkDatum<D3Node> {
  id: string
  source: string | D3Node
  target: string | D3Node
  type: string
  properties: any
}

interface Bounds {
  x: number
  y: number
  width: number
  height: number
  contains(x: number, y: number): boolean
  intersects(other: Bounds): boolean
}

// Spatial partitioning with Quadtree
class Quadtree {
  private bounds: Bounds
  private nodes: D3Node[] = []
  private children: Quadtree[] = []
  private maxNodes = 10
  private maxDepth = 8
  private depth: number

  constructor(bounds: Bounds, depth = 0) {
    this.bounds = bounds
    this.depth = depth
  }

  insert(node: D3Node): boolean {
    if (!this.bounds.contains(node.x!, node.y!)) {
      return false
    }

    if (this.nodes.length < this.maxNodes || this.depth >= this.maxDepth) {
      this.nodes.push(node)
      return true
    }

    if (this.children.length === 0) {
      this.subdivide()
    }

    for (const child of this.children) {
      if (child.insert(node)) {
        return true
      }
    }

    return false
  }

  query(bounds: Bounds): D3Node[] {
    const result: D3Node[] = []

    if (!this.bounds.intersects(bounds)) {
      return result
    }

    result.push(...this.nodes.filter(node => 
      bounds.contains(node.x!, node.y!)
    ))

    for (const child of this.children) {
      result.push(...child.query(bounds))
    }

    return result
  }

  clear() {
    this.nodes = []
    this.children = []
  }

  private subdivide() {
    const { x, y, width, height } = this.bounds
    const halfWidth = width / 2
    const halfHeight = height / 2

    this.children = [
      new Quadtree({ x, y, width: halfWidth, height: halfHeight, contains: this.bounds.contains, intersects: this.bounds.intersects }, this.depth + 1),
      new Quadtree({ x: x + halfWidth, y, width: halfWidth, height: halfHeight, contains: this.bounds.contains, intersects: this.bounds.intersects }, this.depth + 1),
      new Quadtree({ x, y: y + halfHeight, width: halfWidth, height: halfHeight, contains: this.bounds.contains, intersects: this.bounds.intersects }, this.depth + 1),
      new Quadtree({ x: x + halfWidth, y: y + halfHeight, width: halfWidth, height: halfHeight, contains: this.bounds.contains, intersects: this.bounds.intersects }, this.depth + 1)
    ]
  }
}

// Canvas-based renderer for better performance
class CanvasGraphRenderer {
  private canvas: HTMLCanvasElement
  private ctx: CanvasRenderingContext2D
  private nodeTextures: Map<string, ImageData> = new Map()
  private gradientCache: Map<string, CanvasGradient> = new Map()
  private glowTextures: Map<string, ImageData> = new Map()
  private resizeObserver!: ResizeObserver
  private nodes: D3Node[] = []
  private links: D3Link[] = []
  private transform: d3.ZoomTransform = d3.zoomIdentity
  private dragCallbacks: {
    onDragStart?: (event: MouseEvent, node: D3Node) => void
    onDrag?: (event: MouseEvent, node: D3Node) => void
    onDragEnd?: (event: MouseEvent, node: D3Node) => void
  } = {}
  private isDraggingNode: boolean = false
  private draggedNode: D3Node | null = null
  private onNodeClick?: (node: D3Node) => void
  private selectedNode: D3Node | null = null

  constructor(container: HTMLElement, onNodeClick?: (node: D3Node) => void) {
    this.canvas = document.createElement('canvas')
    this.ctx = this.canvas.getContext('2d')!
    this.onNodeClick = onNodeClick
    this.setupCanvas(container)
    this.preloadTextures()
    this.setupMouseEvents()
  }

  private setupCanvas(container: HTMLElement) {
    container.appendChild(this.canvas)
    this.canvas.style.position = 'absolute'
    this.canvas.style.top = '0'
    this.canvas.style.left = '0'
    this.canvas.style.width = '100%'
    this.canvas.style.height = '100%'
    
    const resizeObserver = new ResizeObserver(() => {
      this.canvas.width = container.clientWidth * window.devicePixelRatio
      this.canvas.height = container.clientHeight * window.devicePixelRatio
      this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio)
    })
    resizeObserver.observe(container)
    this.resizeObserver = resizeObserver
  }

  private setupMouseEvents() {
    let isDragging = false
    let draggedNode: D3Node | null = null
    let lastMousePos = { x: 0, y: 0 }
    let mouseDownTime = 0
    let hasMoved = false
    let clickThreshold = 5 // pixels
    let timeThreshold = 200 // milliseconds

    this.canvas.addEventListener('mousedown', (event) => {
      const mousePos = this.getMousePos(event)
      const node = this.getNodeAtPosition(mousePos.x, mousePos.y)
      
      if (node) {
        isDragging = true
        this.isDraggingNode = true
        this.draggedNode = node
        draggedNode = node
        lastMousePos = mousePos
        mouseDownTime = Date.now()
        hasMoved = false
        
        if (this.dragCallbacks.onDragStart) {
          this.dragCallbacks.onDragStart(event, node)
        }
      }
    })

    this.canvas.addEventListener('mousemove', (event) => {
      if (isDragging && draggedNode) {
        const mousePos = this.getMousePos(event)
        
        // Check if mouse has moved significantly
        const dx = mousePos.x - lastMousePos.x
        const dy = mousePos.y - lastMousePos.y
        const distance = Math.sqrt(dx * dx + dy * dy)
        
        if (distance > clickThreshold) {
          hasMoved = true
        }
        
        // Update node position directly to follow mouse
        if (draggedNode.x !== undefined) draggedNode.x = mousePos.x
        if (draggedNode.y !== undefined) draggedNode.y = mousePos.y
        
        if (this.dragCallbacks.onDrag) {
          this.dragCallbacks.onDrag(event, draggedNode)
        }
      }
    })

    this.canvas.addEventListener('mouseup', (event) => {
      if (isDragging && draggedNode) {
        const mouseUpTime = Date.now()
        const clickDuration = mouseUpTime - mouseDownTime
        
        // If it was a short click (less than timeThreshold) and didn't move much, treat as click
        if (clickDuration < timeThreshold && !hasMoved && this.onNodeClick) {
          this.onNodeClick(draggedNode)
        }
        
        if (this.dragCallbacks.onDragEnd) {
          this.dragCallbacks.onDragEnd(event, draggedNode)
        }
        isDragging = false
        this.isDraggingNode = false
        this.draggedNode = null
        draggedNode = null
      }
    })

    this.canvas.addEventListener('mouseleave', (event) => {
      if (isDragging && draggedNode) {
        if (this.dragCallbacks.onDragEnd) {
          this.dragCallbacks.onDragEnd(event, draggedNode)
        }
        isDragging = false
        this.isDraggingNode = false
        this.draggedNode = null
        draggedNode = null
      }
    })
  }

  getMousePos(event: MouseEvent) {
    const rect = this.canvas.getBoundingClientRect()
    const x = (event.clientX - rect.left - this.transform.x) / this.transform.k
    const y = (event.clientY - rect.top - this.transform.y) / this.transform.k
    return { x, y }
  }

  getNodeAtPosition(x: number, y: number): D3Node | null {
    // Check nodes in reverse order (top to bottom)
    for (let i = this.nodes.length - 1; i >= 0; i--) {
      const node = this.nodes[i]
      if (node.x === undefined || node.y === undefined) continue
      
      const radius = node.isOwner ? 35 : 25
      const scale = 1 + (node.pulse || 0) * 0.2
      const scaledRadius = radius * scale
      
      const dx = x - node.x
      const dy = y - node.y
      const distance = Math.sqrt(dx * dx + dy * dy)
      
      if (distance <= scaledRadius) {
        return node
      }
    }
    return null
  }

  setDragCallbacks(callbacks: {
    onDragStart?: (event: MouseEvent, node: D3Node) => void
    onDrag?: (event: MouseEvent, node: D3Node) => void
    onDragEnd?: (event: MouseEvent, node: D3Node) => void
  }) {
    this.dragCallbacks = callbacks
  }

  private preloadTextures() {
    NODE_TYPES.forEach(type => {
      // Create glow texture
      const glowTexture = this.createGlowTexture(type.color)
      this.glowTextures.set(type.type, glowTexture)
      
      // Create gradient
      const gradient = this.createNodeGradient(type)
      this.gradientCache.set(type.type, gradient)
    })
  }

  private createGlowTexture(color: string): ImageData {
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')!
    canvas.width = 128
    canvas.height = 128

    const rgb = hexToRgb(color)
    
    // Create radial gradient for glow
    const gradient = ctx.createRadialGradient(64, 64, 0, 64, 64, 64)
    gradient.addColorStop(0, `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.8)`)
    gradient.addColorStop(0.5, `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.4)`)
    gradient.addColorStop(1, `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0)`)

    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, 128, 128)

    return ctx.getImageData(0, 0, 128, 128)
  }

  private createNodeGradient(type: any): CanvasGradient {
    const gradient = this.ctx.createRadialGradient(0, 0, 0, 0, 0, 30)
    gradient.addColorStop(0, '#000000')
    gradient.addColorStop(0.5, '#1a1a1a')
    gradient.addColorStop(1, '#000000')
    return gradient
  }

  render(nodes: D3Node[], links: D3Link[], transform: d3.ZoomTransform, layoutOptions?: any, selectedNode?: any) {
    this.nodes = nodes
    this.links = links
    this.transform = transform
    // Only update internal selectedNode if a new one is provided
    if (selectedNode !== undefined) {
      this.selectedNode = selectedNode
    }
    
    console.log('🎨 Renderer: render called with selectedNode:', selectedNode?.id || 'null', 'internal selectedNode:', this.selectedNode?.id || 'null')
    
    const { width, height } = this.canvas
    this.ctx.clearRect(0, 0, width, height)
    
    // Apply zoom transform
    this.ctx.save()
    this.ctx.translate(transform.x, transform.y)
    this.ctx.scale(transform.k, transform.k)

    // Render links with configurable opacity
    this.renderLinks(links, nodes, layoutOptions?.linkOpacity || 0.6)
    
    // Render nodes with configurable settings
    this.renderNodes(nodes, layoutOptions)
    
    this.ctx.restore()
  }

  private renderLinks(links: D3Link[], nodes: D3Node[], opacity: number = 0.6) {
    this.ctx.strokeStyle = '#e2e8f0'
    this.ctx.lineWidth = 1.5
    this.ctx.globalAlpha = opacity

    links.forEach(link => {
      const source = typeof link.source === 'string' ? 
        nodes.find(n => n.id === link.source) : link.source
      const target = typeof link.target === 'string' ? 
        nodes.find(n => n.id === link.target) : link.target
      
      if (!source || !target || source.x === undefined || source.y === undefined || 
          target.x === undefined || target.y === undefined) return

      this.ctx.beginPath()
      this.ctx.moveTo(source.x, source.y)
      this.ctx.lineTo(target.x, target.y)
      this.ctx.stroke()
    })

    this.ctx.globalAlpha = 1
  }

  private renderNodes(nodes: D3Node[], layoutOptions?: any) {
    nodes.forEach(node => {
      if (node.x === undefined || node.y === undefined) return

      const nodeType = NODE_TYPES.find(t => t.type === node.type)
      if (!nodeType) return

      // Get node size based on layoutOptions
      const sizeMultiplier = layoutOptions?.nodeSize === 'small' ? 0.7 : 
                            layoutOptions?.nodeSize === 'large' ? 1.3 : 1.0
      
      const baseRadius = node.isOwner ? 35 : 25
      const radius = baseRadius * sizeMultiplier
      const scale = 1 + (node.pulse || 0) * 0.2
      
      // Determine node states
      const isDragged = this.draggedNode === node
      const isSelected = this.selectedNode && this.selectedNode.id === node.id
      
      // Debug logging for selection state
      if (isSelected) {
        console.log('⭐ Node is selected:', node.id, 'isDragged:', isDragged)
      }
      
      // Apply different scaling based on state
      const draggedScale = isDragged ? 1.2 : 1
      const selectedScale = isSelected ? 1.3 : 1
      const finalScale = scale * draggedScale * selectedScale
      const scaledRadius = radius * finalScale

      // Draw glow if enabled
      if (layoutOptions?.showGlows !== false) {
        const rgb = hexToRgb(nodeType.color)
        const glowRadius = radius + 20
        
        this.ctx.save()
        this.ctx.globalAlpha = 0.6
        
        // Create radial gradient for glow
        const glowGradient = this.ctx.createRadialGradient(
          node.x, node.y, 0,
          node.x, node.y, glowRadius
        )
        glowGradient.addColorStop(0, `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.8)`)
        glowGradient.addColorStop(0.5, `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.4)`)
        glowGradient.addColorStop(1, `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0)`)
        
        this.ctx.fillStyle = glowGradient
        this.ctx.beginPath()
        this.ctx.arc(node.x, node.y, glowRadius, 0, Math.PI * 2)
        this.ctx.fill()
        
        this.ctx.restore()
      }

      // Draw selection ring ONLY for selected nodes (info panel open)
      if (isSelected && !isDragged) {
        this.ctx.save()
        this.ctx.globalAlpha = 0.8
        
        // Create pulsing selection ring
        const ringRadius = radius + 15
        const ringGradient = this.ctx.createRadialGradient(
          node.x, node.y, 0,
          node.x, node.y, ringRadius
        )
        ringGradient.addColorStop(0, 'rgba(255, 255, 255, 0.8)')
        ringGradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.4)')
        ringGradient.addColorStop(1, 'rgba(255, 255, 255, 0)')
        
        this.ctx.fillStyle = ringGradient
        this.ctx.beginPath()
        this.ctx.arc(node.x, node.y, ringRadius, 0, Math.PI * 2)
        this.ctx.fill()
        
        this.ctx.restore()
      }

      // Draw drag highlight for dragged nodes
      if (isDragged) {
        this.ctx.save()
        this.ctx.globalAlpha = 0.6
        
        // Create drag highlight ring (different from selection ring)
        const dragRingRadius = radius + 12
        const dragRingGradient = this.ctx.createRadialGradient(
          node.x, node.y, 0,
          node.x, node.y, dragRingRadius
        )
        dragRingGradient.addColorStop(0, 'rgba(255, 255, 255, 0.6)')
        dragRingGradient.addColorStop(0.7, 'rgba(255, 255, 255, 0.3)')
        dragRingGradient.addColorStop(1, 'rgba(255, 255, 255, 0)')
        
        this.ctx.fillStyle = dragRingGradient
        this.ctx.beginPath()
        this.ctx.arc(node.x, node.y, dragRingRadius, 0, Math.PI * 2)
        this.ctx.fill()
        
        this.ctx.restore()
      }

      // Draw node
      this.ctx.save()
      this.ctx.translate(node.x, node.y)
      this.ctx.scale(finalScale, finalScale)

      // Get RGB values for stroke color
      const rgb = hexToRgb(nodeType.color)

      // Apply different styling based on state
      if (isDragged) {
        // Dragged node styling - brighter, more prominent
        const dragGradient = this.ctx.createRadialGradient(0, 0, 0, 0, 0, 30)
        dragGradient.addColorStop(0, '#666666')
        dragGradient.addColorStop(0.5, '#777777')
        dragGradient.addColorStop(1, '#555555')
        this.ctx.fillStyle = dragGradient
      } else if (isSelected) {
        // Selected node styling - lighter than normal but not as bright as dragged
        const lightGradient = this.ctx.createRadialGradient(0, 0, 0, 0, 0, 30)
        lightGradient.addColorStop(0, '#444444')
        lightGradient.addColorStop(0.5, '#555555')
        lightGradient.addColorStop(1, '#333333')
        this.ctx.fillStyle = lightGradient
      } else {
        // Normal node styling
        const gradient = this.gradientCache.get(node.type)
        if (gradient) {
          this.ctx.fillStyle = gradient
        } else {
          this.ctx.fillStyle = '#000000'
        }
      }
      
      this.ctx.beginPath()
      this.ctx.arc(0, 0, radius, 0, Math.PI * 2)
      this.ctx.fill()

      // Apply different stroke styling based on state
      if (isDragged) {
        // Dragged node stroke - very bright
        const brightRgb = {
          r: Math.min(255, rgb.r + 150),
          g: Math.min(255, rgb.g + 150),
          b: Math.min(255, rgb.b + 150)
        }
        this.ctx.strokeStyle = `rgb(${brightRgb.r}, ${brightRgb.g}, ${brightRgb.b})`
        this.ctx.lineWidth = node.isOwner ? 5 : 4
      } else if (isSelected) {
        // Selected node stroke - moderately bright
        const lightRgb = {
          r: Math.min(255, rgb.r + 100),
          g: Math.min(255, rgb.g + 100),
          b: Math.min(255, rgb.b + 100)
        }
        this.ctx.strokeStyle = `rgb(${lightRgb.r}, ${lightRgb.g}, ${lightRgb.b})`
        this.ctx.lineWidth = node.isOwner ? 4 : 3
      } else {
        // Normal node stroke
        this.ctx.strokeStyle = node.isOwner ? '#ffffff' : nodeType.color
        this.ctx.lineWidth = node.isOwner ? 4 : 3
      }
      this.ctx.stroke()

      this.ctx.restore()

      // Draw text if enabled
      if (layoutOptions?.showLabels !== false) {
        this.ctx.save()
        this.ctx.translate(node.x, node.y)
        this.ctx.scale(finalScale, finalScale)
        
        const maxLength = node.isOwner ? 10 : 8
        const text = node.label.length > maxLength ? 
          node.label.substring(0, maxLength) + '...' : node.label
        
        this.ctx.fillStyle = '#fff'
        this.ctx.font = `${node.isOwner ? '11px' : '9px'} sans-serif`
        this.ctx.textAlign = 'center'
        this.ctx.textBaseline = 'middle'
        
        // Text shadow
        this.ctx.shadowColor = 'rgba(0,0,0,0.5)'
        this.ctx.shadowBlur = 2
        this.ctx.shadowOffsetX = 1
        this.ctx.shadowOffsetY = 1
        
        this.ctx.fillText(text, 0, 0)
        this.ctx.restore()
      }
    })
  }

  destroy() {
    this.resizeObserver.disconnect()
    this.canvas.remove()
  }

  getCanvas() {
    return this.canvas
  }

  isDragging(): boolean {
    return this.isDraggingNode
  }

  setSelectedNode(node: D3Node | null) {
    console.log('🎯 Renderer: setSelectedNode called with:', node?.id || 'null')
    this.selectedNode = node
  }

  clearSelection() {
    console.log('🗑️ Renderer: clearSelection called')
    this.selectedNode = null
  }
}

export const D3GraphView = React.forwardRef<{ clearSelection: () => void }, {
  activeFilters?: {
    people: boolean
    companies: boolean
    topics: boolean
    events: boolean
    locations: boolean
    interactions: boolean
  }
  layoutOptions?: {
    algorithm: string
    showLabels: boolean
    showGlows: boolean
    nodeSize: string
    linkOpacity: number
    animationSpeed: string
    gravityStrength: string
    springStrength: string
  }
  onNodeClick?: (node: any) => void
  onDragStart?: (event: MouseEvent, node: any) => void
  selectedNode?: any
}>(({ 
  activeFilters = {
    people: true,
    companies: true,
    topics: true,
    events: true,
    locations: true,
    interactions: true,
  },
  layoutOptions = {
    algorithm: 'force-directed',
    showLabels: true,
    showGlows: true,
    nodeSize: 'normal',
    linkOpacity: 0.6,
    animationSpeed: 'normal',
    gravityStrength: 'normal',
    springStrength: 'normal',
  },
  onNodeClick,
  onDragStart,
  selectedNode
}, ref) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const { data, isLoading, error } = useGraphData()
  
  // D3 simulation refs
  const simulationRef = useRef<d3.Simulation<D3Node, D3Link> | null>(null)
  const nodesRef = useRef<D3Node[]>([])
  const linksRef = useRef<D3Link[]>([])
  const zoomRef = useRef<d3.ZoomBehavior<HTMLCanvasElement, unknown> | null>(null)
  const rendererRef = useRef<CanvasGraphRenderer | null>(null)
  const quadtreeRef = useRef<Quadtree | null>(null)

  // Expose clearSelection method to parent component
  const clearSelection = useCallback(() => {
    if (rendererRef.current) {
      rendererRef.current.clearSelection()
    }
  }, [])

  // Expose methods to parent component
  React.useImperativeHandle(ref, () => ({
    clearSelection
  }), [clearSelection])

  // Transform API data to D3 format with filtering
  const makeD3Data = useCallback((graph: GraphData | undefined) => {
    if (!graph) return { nodes: [], links: [] }
    
    // Filter nodes based on active filters
    const filteredNodes = graph.nodes.filter(node => {
      const nodeType = node.type.toLowerCase()
      switch (nodeType) {
        case 'person':
          return activeFilters.people
        case 'company':
          return activeFilters.companies
        case 'topic':
          return activeFilters.topics
        case 'event':
          return activeFilters.events
        case 'location':
          return activeFilters.locations
        case 'interaction':
          return activeFilters.interactions
        default:
          return true
      }
    })
    
    // Create a set of visible node IDs for link filtering
    const visibleNodeIds = new Set(filteredNodes.map(n => n.id))
    
    // Filter links to only include those between visible nodes
    const filteredLinks = graph.edges.filter(edge => 
      visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target)
    )
    
    // Convert to D3 format
    const d3Nodes: D3Node[] = filteredNodes.map(n => ({
      id: n.id,
      label: n.label,
      type: n.type,
      properties: n.properties,
      isOwner: n.label === OWNER_NAME,
      pulse: 0,
    }))
    
    // Create a map for quick node lookup
    const nodeMap = new Map(d3Nodes.map(n => [n.id, n]))
    
    const d3Links: D3Link[] = filteredLinks.map(l => ({
      id: l.id,
      source: nodeMap.get(l.source)!, // Convert to actual node object
      target: nodeMap.get(l.target)!, // Convert to actual node object
      type: l.type,
      properties: l.properties,
    }))
    
    // Debug logging
    console.log('D3 Graph Data:', { 
      nodes: d3Nodes.length, 
      links: d3Links.length,
      filters: activeFilters
    })
    
    return { nodes: d3Nodes, links: d3Links }
  }, [activeFilters])

  // Optimized bouncy spring force with spatial partitioning
  const createBouncySpringForce = () => {
    return (alpha: number) => {
      // Get spring strength multiplier based on layoutOptions
      const springMultiplier = layoutOptions.springStrength === 'loose' ? 0.6 : 
                              layoutOptions.springStrength === 'tight' ? 1.4 : 1.0
      
      linksRef.current.forEach(link => {
        const source = typeof link.source === 'string' ? 
          nodesRef.current.find(n => n.id === link.source) : link.source
        const target = typeof link.target === 'string' ? 
          nodesRef.current.find(n => n.id === link.target) : link.target
        
        if (!source || !target) return
        
        const dx = (target.x || 0) - (source.x || 0)
        const dy = (target.y || 0) - (source.y || 0)
        const distance = Math.sqrt(dx * dx + dy * dy)
        const idealLength = 50 // Much shorter for tighter clustering
        
        if (distance > 0) {
          // Enhanced bouncy spring force with configurable strength
          const springStrength = 0.4 * alpha * springMultiplier
          const overshoot = Math.sin(distance / idealLength * Math.PI) * 0.15
          const force = (distance - idealLength) * springStrength * (1 + overshoot)
          
          const fx = (dx / distance) * force
          const fy = (dy / distance) * force
          
          if (source.x !== undefined) source.x += fx
          if (source.y !== undefined) source.y += fy
          if (target.x !== undefined) target.x -= fx
          if (target.y !== undefined) target.y -= fy

          // Add pulse effect to connected nodes
          if (source.pulse !== undefined) source.pulse = Math.min(source.pulse + 0.1, 1)
          if (target.pulse !== undefined) target.pulse = Math.min(target.pulse + 0.1, 1)
        }
      })
    }
  }

  // Optimized circular gravity force
  const createCircularGravityForce = () => {
    return (alpha: number) => {
      const centerX = 0
      const centerY = 0
      
      // Get gravity strength multiplier based on layoutOptions
      const gravityMultiplier = layoutOptions.gravityStrength === 'weak' ? 0.5 : 
                               layoutOptions.gravityStrength === 'strong' ? 1.5 : 1.0
      
      const gravityStrength = 0.8 * alpha * gravityMultiplier
      
      nodesRef.current.forEach(node => {
        if (node.x === undefined || node.y === undefined) return
        
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

  // Optimized collision detection with spatial partitioning
  const createOptimizedCollisionForce = () => {
    return (alpha: number) => {
      if (!quadtreeRef.current) return
      
      const collisionRadius = 30
      quadtreeRef.current.clear()
      
      // Rebuild quadtree
      nodesRef.current.forEach(node => {
        if (node.x !== undefined && node.y !== undefined) {
          quadtreeRef.current!.insert(node)
        }
      })
      
      // Check collisions using spatial partitioning
      nodesRef.current.forEach(node => {
        if (node.x === undefined || node.y === undefined) return
        
        const bounds: Bounds = {
          x: node.x - collisionRadius,
          y: node.y - collisionRadius,
          width: collisionRadius * 2,
          height: collisionRadius * 2,
          contains: function(x: number, y: number) {
            return x >= this.x && x <= this.x + this.width && 
                   y >= this.y && y <= this.y + this.height
          },
          intersects: function(other: Bounds) {
            return !(this.x + this.width < other.x || 
                     other.x + other.width < this.x || 
                     this.y + this.height < other.y || 
                     other.y + other.height < this.y)
          }
        }
        
        const nearbyNodes = quadtreeRef.current!.query(bounds)
        resolveCollisions(node, nearbyNodes, alpha)
      })
    }
  }

  // Edge repulsion force to prevent edge overlap
  const createEdgeRepulsionForce = () => {
    return (alpha: number) => {
      const repulsionStrength = 0.3 * alpha
      const repulsionDistance = 20 // Minimum distance between edges
      
      // Check each pair of edges
      for (let i = 0; i < linksRef.current.length; i++) {
        for (let j = i + 1; j < linksRef.current.length; j++) {
          const edge1 = linksRef.current[i]
          const edge2 = linksRef.current[j]
          
          const source1 = typeof edge1.source === 'string' ? 
            nodesRef.current.find(n => n.id === edge1.source) : edge1.source
          const target1 = typeof edge1.target === 'string' ? 
            nodesRef.current.find(n => n.id === edge1.target) : edge1.target
          const source2 = typeof edge2.source === 'string' ? 
            nodesRef.current.find(n => n.id === edge2.source) : edge2.source
          const target2 = typeof edge2.target === 'string' ? 
            nodesRef.current.find(n => n.id === edge2.target) : edge2.target
          
          if (!source1 || !target1 || !source2 || !target2 ||
              source1.x === undefined || source1.y === undefined ||
              target1.x === undefined || target1.y === undefined ||
              source2.x === undefined || source2.y === undefined ||
              target2.x === undefined || target2.y === undefined) continue
          
          // Calculate the closest points between the two line segments
          const closestPoints = getClosestPointsBetweenLines(
            source1.x, source1.y, target1.x, target1.y,
            source2.x, source2.y, target2.x, target2.y
          )
          
          const distance = Math.sqrt(
            Math.pow(closestPoints.x1 - closestPoints.x2, 2) + 
            Math.pow(closestPoints.y1 - closestPoints.y2, 2)
          )
          
          if (distance < repulsionDistance && distance > 0) {
            // Calculate repulsion force
            const force = (repulsionDistance - distance) * repulsionStrength
            const dx = (closestPoints.x2 - closestPoints.x1) / distance
            const dy = (closestPoints.y2 - closestPoints.y1) / distance
            
            // Apply force to move edges apart
            // Move the closest points on each edge away from each other
            const moveDistance = force * 0.5
            
            // For edge1, move the closest point
            const edge1Ratio = getPointRatioOnLine(
              closestPoints.x1, closestPoints.y1,
              source1.x, source1.y, target1.x, target1.y
            )
            if (edge1Ratio >= 0 && edge1Ratio <= 1) {
              source1.x -= dx * moveDistance * (1 - edge1Ratio)
              source1.y -= dy * moveDistance * (1 - edge1Ratio)
              target1.x -= dx * moveDistance * edge1Ratio
              target1.y -= dy * moveDistance * edge1Ratio
            }
            
            // For edge2, move the closest point
            const edge2Ratio = getPointRatioOnLine(
              closestPoints.x2, closestPoints.y2,
              source2.x, source2.y, target2.x, target2.y
            )
            if (edge2Ratio >= 0 && edge2Ratio <= 1) {
              source2.x += dx * moveDistance * (1 - edge2Ratio)
              source2.y += dy * moveDistance * (1 - edge2Ratio)
              target2.x += dx * moveDistance * edge2Ratio
              target2.y += dy * moveDistance * edge2Ratio
            }
          }
        }
      }
    }
  }

  // Helper function to find closest points between two line segments
  const getClosestPointsBetweenLines = (
    x1: number, y1: number, x2: number, y2: number,
    x3: number, y3: number, x4: number, y4: number
  ) => {
    const ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) /
               ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
    const ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) /
               ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
    
    // Clamp to line segments
    const uaClamped = Math.max(0, Math.min(1, ua))
    const ubClamped = Math.max(0, Math.min(1, ub))
    
    return {
      x1: x1 + uaClamped * (x2 - x1),
      y1: y1 + uaClamped * (y2 - y1),
      x2: x3 + ubClamped * (x4 - x3),
      y2: y3 + ubClamped * (y4 - y3)
    }
  }

  // Helper function to get the ratio of a point along a line
  const getPointRatioOnLine = (
    px: number, py: number,
    x1: number, y1: number, x2: number, y2: number
  ) => {
    const dx = x2 - x1
    const dy = y2 - y1
    const length = Math.sqrt(dx * dx + dy * dy)
    
    if (length === 0) return 0
    
    const dot = (px - x1) * dx + (py - y1) * dy
    return dot / (length * length)
  }

  // Resolve collisions between nodes
  const resolveCollisions = (node: D3Node, nearbyNodes: D3Node[], alpha: number) => {
    const collisionRadius = 30
    
    nearbyNodes.forEach(other => {
      if (other === node || other.x === undefined || other.y === undefined || 
          node.x === undefined || node.y === undefined) return
      
      const dx = other.x - node.x
      const dy = other.y - node.y
      const distance = Math.sqrt(dx * dx + dy * dy)
      
      if (distance < collisionRadius && distance > 0) {
        const force = (collisionRadius - distance) * 0.1 * alpha
        const fx = (dx / distance) * force
        const fy = (dy / distance) * force
        
        node.x -= fx
        node.y -= fy
        other.x += fx
        other.y += fy
      }
    })
  }

  // Initialize D3 visualization
  useEffect(() => {
    if (!containerRef.current || !data) return

    const { nodes, links } = makeD3Data(data)
    nodesRef.current = nodes
    linksRef.current = links

    // Clean up previous simulation
    if (simulationRef.current) {
      simulationRef.current.stop()
    }

    // Create canvas renderer
    const renderer = new CanvasGraphRenderer(containerRef.current, onNodeClick)
    rendererRef.current = renderer

    // Set up drag callbacks
    renderer.setDragCallbacks({
      onDragStart: (event, node) => {
        // Call the external onDragStart callback if provided
        if (onDragStart) {
          onDragStart(event, node)
        }
        if (simulationRef.current) {
          simulationRef.current.alphaTarget(0.3).restart()
        }
        // Set fixed position to lock the node
        node.fx = node.x
        node.fy = node.y
      },
      onDrag: (event, node) => {
        // Update the fixed position to follow mouse
        if (node.x !== undefined && node.y !== undefined) {
          node.fx = node.x
          node.fy = node.y
        }
        // Force a simulation tick to update connected nodes
        if (simulationRef.current) {
          simulationRef.current.tick()
        }
      },
      onDragEnd: (event, node) => {
        if (simulationRef.current) {
          simulationRef.current.alphaTarget(0)
        }
        // Release the fixed position so physics can take over
        node.fx = null
        node.fy = null
        if (simulationRef.current) {
          simulationRef.current.alpha(0.3).restart()
        }
      }
    })

    // Initialize quadtree
    const bounds: Bounds = {
      x: -1000, y: -1000, width: 2000, height: 2000,
      contains: function(x: number, y: number) {
        return x >= this.x && x <= this.x + this.width && 
               y >= this.y && y <= this.y + this.height
      },
      intersects: function(other: Bounds) {
        return !(this.x + this.width < other.x || 
                 other.x + other.width < this.x || 
                 this.y + this.height < other.y || 
                 other.y + other.height < this.y)
      }
    }
    quadtreeRef.current = new Quadtree(bounds)

    const width = containerRef.current.clientWidth
    const height = containerRef.current.clientHeight

    // Create zoom behavior for canvas
    const zoom = d3.zoom<HTMLCanvasElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        // Only apply zoom if we're not dragging a node
        if (!renderer.isDragging()) {
          renderer.render(nodes, links, event.transform, layoutOptions)
        }
      })
      .filter((event) => {
        // Only prevent zoom/pan when actually clicking on nodes (mousedown)
        // Allow zooming when hovering over nodes
        if (event.type === 'mousedown') {
          const mousePos = renderer.getMousePos(event)
          const node = renderer.getNodeAtPosition(mousePos.x, mousePos.y)
          return !node // Only allow zoom/pan when not clicking on a node
        }
        return true // Allow all other events (wheel zoom, etc.)
      })
    
    zoomRef.current = zoom
    d3.select(renderer.getCanvas()).call(zoom)

    // Create simulation based on layout algorithm
    let simulation: d3.Simulation<D3Node, D3Link>
    
    switch (layoutOptions.algorithm) {
      case 'circular':
        simulation = createCircularLayout(nodes, links, width, height)
        break
      case 'hierarchical':
        simulation = createHierarchicalLayout(nodes, links, width, height)
        break
      case 'radial':
        simulation = createRadialLayout(nodes, links, width, height)
        break
      default: // force-directed
        simulation = createForceDirectedLayout(nodes, links, width, height)
        break
    }

    simulationRef.current = simulation

    // Position Alice at center for all layouts
    const aliceNode = nodes.find(n => n.isOwner)
    if (aliceNode) {
      aliceNode.x = width / 2
      aliceNode.y = height / 2
      if (layoutOptions.algorithm === 'force-directed') {
        aliceNode.fx = width / 2
        aliceNode.fy = height / 2
      }
    }

    // Update positions on simulation tick
    simulation.on('tick', () => {
      // Update pulse effects
      nodes.forEach(node => {
        if (node.pulse !== undefined) {
          node.pulse = Math.max(0, node.pulse - 0.02)
        }
      })

      // Render frame
      const transform = d3.zoomTransform(renderer.getCanvas())
      renderer.render(nodes, links, transform, layoutOptions)
    })

    // Initial render
    renderer.render(nodes, links, d3.zoomIdentity, layoutOptions)

    return () => {
      simulation.stop()
      renderer.destroy()
    }
  }, [data, makeD3Data])

  // Handle layout changes separately
  useEffect(() => {
    if (!simulationRef.current || !nodesRef.current || !linksRef.current || !containerRef.current) return

    const nodes = nodesRef.current
    const links = linksRef.current
    const width = containerRef.current.clientWidth
    const height = containerRef.current.clientHeight

    // Stop current simulation
    simulationRef.current.stop()

    // Create new simulation based on layout algorithm
    let simulation: d3.Simulation<D3Node, D3Link>
    
    switch (layoutOptions.algorithm) {
      case 'circular':
        simulation = createCircularLayout(nodes, links, width, height)
        break
      case 'hierarchical':
        simulation = createHierarchicalLayout(nodes, links, width, height)
        break
      case 'radial':
        simulation = createRadialLayout(nodes, links, width, height)
        break
      default: // force-directed
        simulation = createForceDirectedLayout(nodes, links, width, height)
        break
    }

    simulationRef.current = simulation

    // Position Alice at center for all layouts
    const aliceNode = nodes.find(n => n.isOwner)
    if (aliceNode) {
      aliceNode.x = width / 2
      aliceNode.y = height / 2
      if (layoutOptions.algorithm === 'force-directed') {
      aliceNode.fx = width / 2
      aliceNode.fy = height / 2
      }
    }

    // Update positions on simulation tick
    simulation.on('tick', () => {
      // Update pulse effects
      nodes.forEach(node => {
        if (node.pulse !== undefined) {
          node.pulse = Math.max(0, node.pulse - 0.02)
        }
      })

      // Render frame
      if (rendererRef.current) {
        const transform = d3.zoomTransform(rendererRef.current.getCanvas())
        rendererRef.current.render(nodes, links, transform, layoutOptions)
      }
    })

    // Initial render
    if (rendererRef.current) {
      rendererRef.current.render(nodes, links, d3.zoomIdentity, layoutOptions)
    }
  }, [layoutOptions.algorithm])

  // Update selected node without resetting simulation
  useEffect(() => {
    if (rendererRef.current) {
      rendererRef.current.setSelectedNode(selectedNode)
    }

    // Center viewport on selected node
    if (selectedNode && zoomRef.current && containerRef.current) {
      const canvas = rendererRef.current?.getCanvas()
      if (canvas && selectedNode.x !== undefined && selectedNode.y !== undefined) {
        const width = containerRef.current.clientWidth
        const height = containerRef.current.clientHeight
        
        // Calculate the transform to center the node
        // We want the node to be at the center of the viewport
        const targetScale = 1.5
        
        // Calculate the translation needed to center the node
        // The formula is: translate = center_of_viewport - (node_position * scale)
        const targetX = width / 2 - selectedNode.x * targetScale
        const targetY = height / 2 - selectedNode.y * targetScale
        
        const transform = d3.zoomIdentity
          .translate(targetX, targetY)
          .scale(targetScale)
        
        // Smoothly transition to the new view
        d3.select(canvas)
          .transition()
          .duration(800)
          .ease(d3.easeCubicOut)
          .call(zoomRef.current.transform, transform)
      }
    } else if (!selectedNode && zoomRef.current && containerRef.current) {
      // Reset to default view when no node is selected
      const canvas = rendererRef.current?.getCanvas()
      if (canvas) {
        // Smoothly transition back to default view
        d3.select(canvas)
          .transition()
          .duration(600)
          .ease(d3.easeCubicOut)
          .call(zoomRef.current.transform, d3.zoomIdentity)
      }
    }
  }, [selectedNode])

  // Sync renderer's internal selectedNode state with external prop
  useEffect(() => {
    console.log('🔍 D3GraphView: selectedNode prop changed:', selectedNode?.id || 'null')
    if (rendererRef.current) {
      rendererRef.current.setSelectedNode(selectedNode)
    }
  }, [selectedNode])

  // Create force-directed layout (original)
  const createForceDirectedLayout = (nodes: D3Node[], links: D3Link[], width: number, height: number) => {
    return d3.forceSimulation<D3Node>(nodes)
      .force('link', createBouncySpringForce())
      .force('charge', d3.forceManyBody().strength(-200))
      .force('collision', createOptimizedCollisionForce())
      .force('edgeRepulsion', createEdgeRepulsionForce())
      .force('gravity', createCircularGravityForce())
      .force('center', d3.forceCenter(width / 2, height / 2))
      .alphaDecay(0.015)
      .velocityDecay(0.2)
  }

  // Create circular layout
  const createCircularLayout = (nodes: D3Node[], links: D3Link[], width: number, height: number) => {
    // Position nodes in a circle
    const centerX = width / 2
    const centerY = height / 2
    const radius = Math.min(width, height) * 0.3
    
    nodes.forEach((node, i) => {
      const angle = (i / nodes.length) * 2 * Math.PI
      node.x = centerX + radius * Math.cos(angle)
      node.y = centerY + radius * Math.sin(angle)
      // Fix positions for circular layout
      node.fx = node.x
      node.fy = node.y
    })

    return d3.forceSimulation<D3Node>(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-50))
      .force('collision', d3.forceCollide().radius(30))
      .alphaDecay(0.02)
      .velocityDecay(0.3)
  }

  // Create hierarchical layout
  const createHierarchicalLayout = (nodes: D3Node[], links: D3Link[], width: number, height: number) => {
    // Find Alice (owner) as root
    const aliceNode = nodes.find(n => n.isOwner)
    if (!aliceNode) return createForceDirectedLayout(nodes, links, width, height)

    // Create a simple tree structure based on connections
    const nodeMap = new Map(nodes.map(n => [n.id, n]))
    const visited = new Set<string>()
    const queue: { node: D3Node; level: number; angle: number }[] = []
    
    // Start with Alice at the top
    aliceNode.x = width / 2
    aliceNode.y = 100
    // Don't fix Alice position completely - allow slight movement
    aliceNode.fx = aliceNode.x
    aliceNode.fy = aliceNode.y
    visited.add(aliceNode.id)
    queue.push({ node: aliceNode, level: 0, angle: 0 })

    // BFS to position connected nodes
    while (queue.length > 0) {
      const { node, level, angle } = queue.shift()!
      const connectedNodes = links
        .filter(l => (l.source as D3Node).id === node.id || (l.target as D3Node).id === node.id)
        .map(l => (l.source as D3Node).id === node.id ? l.target as D3Node : l.source as D3Node)
        .filter(n => !visited.has(n.id))

      if (connectedNodes.length > 0) {
        const levelHeight = 120
        const levelY = 100 + (level + 1) * levelHeight
        const spacing = Math.min(300, width / (connectedNodes.length + 1))
        
        connectedNodes.forEach((connectedNode, i) => {
          const nodeAngle = angle + (i - (connectedNodes.length - 1) / 2) * spacing / 100
          connectedNode.x = width / 2 + nodeAngle * 50
          connectedNode.y = levelY
          // Don't fix positions completely - allow movement within constraints
          connectedNode.fx = null
          connectedNode.fy = null
          visited.add(connectedNode.id)
          queue.push({ node: connectedNode, level: level + 1, angle: nodeAngle })
        })
      }
    }

    // Position remaining unconnected nodes randomly
      nodes.forEach(node => {
      if (!visited.has(node.id)) {
        node.x = Math.random() * width
        node.y = Math.random() * height
        node.fx = null
        node.fy = null
      }
    })

    return d3.forceSimulation<D3Node>(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(80))
      .force('charge', d3.forceManyBody().strength(-100))
      .force('collision', d3.forceCollide().radius(25))
      .force('x', d3.forceX().x((d: any) => {
        // Keep nodes roughly in their level positions
        if (d.isOwner) return width / 2
        return d.x || width / 2
      }).strength(0.3))
      .force('y', d3.forceY().y((d: any) => {
        // Keep nodes roughly in their level positions
        if (d.isOwner) return 100
        return d.y || height / 2
      }).strength(0.3))
      .alphaDecay(0.01)
      .velocityDecay(0.5)
  }

  // Create radial layout
  const createRadialLayout = (nodes: D3Node[], links: D3Link[], width: number, height: number) => {
    // Find Alice (owner) as center
    const aliceNode = nodes.find(n => n.isOwner)
    if (!aliceNode) return createForceDirectedLayout(nodes, links, width, height)

    const centerX = width / 2
    const centerY = height / 2
    
    // Position Alice at center
    aliceNode.x = centerX
    aliceNode.y = centerY
    // Keep Alice fixed at center
    aliceNode.fx = centerX
    aliceNode.fy = centerY

    // Position other nodes in concentric circles
    const otherNodes = nodes.filter(n => !n.isOwner)
    const maxRadius = Math.min(width, height) * 0.4
    const circles = 3 // Number of concentric circles
    
    otherNodes.forEach((node, i) => {
      const circleIndex = Math.floor(i / Math.ceil(otherNodes.length / circles))
      const radius = (circleIndex + 1) * (maxRadius / circles)
      const angle = (i / Math.ceil(otherNodes.length / circles)) * 2 * Math.PI
      
      node.x = centerX + radius * Math.cos(angle)
      node.y = centerY + radius * Math.sin(angle)
      // Don't fix positions completely - allow movement within radial constraints
      node.fx = null
      node.fy = null
    })

    return d3.forceSimulation<D3Node>(nodes)
      .force('link', d3.forceLink(links).id((d: any) => d.id).distance(60))
      .force('charge', d3.forceManyBody().strength(-80))
      .force('collision', d3.forceCollide().radius(20))
      .force('radial', (alpha: number) => {
        // Custom radial force to keep nodes in their assigned circles
        otherNodes.forEach((node, i) => {
          if (node.x === undefined || node.y === undefined) return
          
          const circleIndex = Math.floor(i / Math.ceil(otherNodes.length / circles))
          const targetRadius = (circleIndex + 1) * (maxRadius / circles)
          
          const dx = node.x - centerX
          const dy = node.y - centerY
          const currentRadius = Math.sqrt(dx * dx + dy * dy)
          
          if (currentRadius > 0) {
            const radiusDiff = targetRadius - currentRadius
            const force = radiusDiff * 0.1 * alpha
            
            node.x += (dx / currentRadius) * force
            node.y += (dy / currentRadius) * force
          }
        })
      })
      .alphaDecay(0.02)
      .velocityDecay(0.4)
  }

  // Drag functions (now handled by canvas renderer)
  const dragstarted = (event: any, d: D3Node) => {
    // Handled by canvas renderer
  }

  const dragged = (event: any, d: D3Node) => {
    // Handled by canvas renderer
  }

  const dragended = (event: any, d: D3Node) => {
    // Handled by canvas renderer
  }

  return (
    <div className="w-full h-full relative">
      <div ref={containerRef} className="w-full h-full" />
      {isLoading && <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80 z-10">
        <span className="text-gray-300">Loading network...</span>
      </div>}
      {error && <div className="absolute bottom-4 left-4 text-red-400 bg-red-900/80 px-3 py-2 rounded">Error loading graph: {String(error)}</div>}
    </div>
  )
})

export default D3GraphView 