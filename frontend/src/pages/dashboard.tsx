import { motion, AnimatePresence } from 'framer-motion'
import { useState, useRef } from 'react'
import { Card } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { useNetworkStats, usePeople, useInteractions, useAgentSuggestions, useGraphData, useDeletePerson, useDeleteCompany, useDeleteTopic, useDeleteEvent, useDeleteLocation, useDeleteInteraction } from '../api/queries'
import { useQueryClient } from '@tanstack/react-query'
import { processNoteWithAI, createEntitiesFromAI, processNoteWithAIAdvanced } from '../api/client'
import { api } from '../api/client'
import D3GraphView from '../graph/d3-graph-view'
import type { Person, Interaction, AgentSuggestion, AdvancedNoteProcessingRequest, AdvancedNoteProcessingResponse } from '../types/models'
import { AdvancedAIResults } from '../components/ui/advanced-ai-results'

// Icons (using simple text for now, can be replaced with proper icons)
const MenuIcon = () => <span className="text-2xl">☰</span>
const GraphIcon = () => <span className="text-2xl">🕸️</span>
const PlusIcon = () => <span className="text-2xl">+</span>
const SearchIcon = () => <span className="text-lg">🔍</span>
const AIIcon = () => <span className="text-lg">🤖</span>
const CloseIcon = () => <span className="text-lg">×</span>

export function Dashboard() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isGraphOptionsOpen, setIsGraphOptionsOpen] = useState(false)
  const [isLayoutOptionsOpen, setIsLayoutOptionsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedNode, setSelectedNode] = useState<any>(null)
  const [aiInputText, setAIInputText] = useState('')
  const [aiResults, setAIResults] = useState<AdvancedNoteProcessingResponse | null>(null)
  const [isAIInputOpen, setIsAIInputOpen] = useState(false)
  const [isProcessingAI, setIsProcessingAI] = useState(false)
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false)
  const [isDeletingNode, setIsDeletingNode] = useState(false)
  const [activeFilters, setActiveFilters] = useState({
    people: true,
    companies: true,
    topics: true,
    events: true,
    locations: true,
    interactions: true,
  })
  const [layoutOptions, setLayoutOptions] = useState({
    algorithm: 'force-directed', // force-directed, circular, hierarchical, radial
    showLabels: true,
    showGlows: true,
    nodeSize: 'normal', // small, normal, large
    linkOpacity: 0.6,
    animationSpeed: 'normal', // slow, normal, fast
    gravityStrength: 'normal', // weak, normal, strong
    springStrength: 'normal', // loose, normal, tight
  })

  const graphRef = useRef<{ clearSelection: () => void } | null>(null)

  const { data: stats } = useNetworkStats()
  const { data: people } = usePeople()
  const { data: interactions } = useInteractions()
  const { data: suggestions } = useAgentSuggestions()
  const { data: graphData } = useGraphData()

  // Delete mutations
  const deletePersonMutation = useDeletePerson()
  const deleteCompanyMutation = useDeleteCompany()
  const deleteTopicMutation = useDeleteTopic()
  const deleteEventMutation = useDeleteEvent()
  const deleteLocationMutation = useDeleteLocation()
  const deleteInteractionMutation = useDeleteInteraction()
  
  const queryClient = useQueryClient()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement search functionality
    console.log('Searching for:', searchQuery)
  }

  const toggleFilter = (filter: string) => {
    setActiveFilters(prev => ({
      ...prev,
      [filter]: !prev[filter as keyof typeof prev]
    }))
  }

  const updateLayoutOption = (option: string, value: any) => {
    setLayoutOptions(prev => ({
      ...prev,
      [option]: value
    }))
  }

  const handleNodeClick = (node: any) => {
    console.log('🖱️ Dashboard: Node clicked:', node.id)
    setSelectedNode(node)
  }

  const handleDragStart = (event: MouseEvent, node: any) => {
    console.log('🖱️ Dashboard: Drag started for node:', node.id)
    // Clear selection when dragging starts
    setSelectedNode(null)
  }

  const closeNodeDetails = () => {
    console.log('❌ Dashboard: Closing node details')
    setSelectedNode(null)
    // Clear the selection in the graph renderer
    if (graphRef.current) {
      graphRef.current.clearSelection()
    }
  }

  const resetGraphView = () => {
    // This will be called when the panel closes to reset the view
    if (selectedNode) {
      // The view will automatically reset when selectedNode becomes null
    }
  }

  const openMenu = (menuType: 'main' | 'graph' | 'layout') => {
    // Close other menus first
    if (menuType === 'main') {
      setIsGraphOptionsOpen(false)
      setIsLayoutOptionsOpen(false)
      setIsMenuOpen(!isMenuOpen)
    } else if (menuType === 'graph') {
      setIsMenuOpen(false)
      setIsLayoutOptionsOpen(false)
      setIsGraphOptionsOpen(!isGraphOptionsOpen)
    } else {
      setIsMenuOpen(false)
      setIsGraphOptionsOpen(false)
      setIsLayoutOptionsOpen(!isLayoutOptionsOpen)
    }
  }

  const closeAllMenus = () => {
    setIsMenuOpen(false)
    setIsGraphOptionsOpen(false)
    setIsLayoutOptionsOpen(false)
  }

  // Get connections for the selected node
  const getNodeConnections = (nodeId: string) => {
    if (!graphData?.edges) return []
    
    return graphData.edges.filter(edge => 
      edge.source === nodeId || edge.target === nodeId
    ).map(edge => {
      const connectedNodeId = edge.source === nodeId ? edge.target : edge.source
      const connectedNode = graphData.nodes.find(n => n.id === connectedNodeId)
      return {
        ...edge,
        connectedNode
      }
    })
  }

  const openAIInput = () => {
    setIsAIInputOpen(true)
    setAIInputText('')
    setAIResults(null)
  }

  const closeAIInput = () => {
    setIsAIInputOpen(false)
    setAIInputText('')
    setAIResults(null)
  }

  const processAIInput = async () => {
    if (!aiInputText.trim()) return
    
    setIsProcessingAI(true)
    try {
      console.log('Processing AI input with advanced system:', aiInputText)
      
      // Use the new advanced AI processing
      const request: AdvancedNoteProcessingRequest = {
        note_text: aiInputText,
        main_person_name: 'Alice', // This should be configurable
        auto_create_entities: false // We'll handle creation manually for now
      }
      
      const result = await processNoteWithAIAdvanced(request)
      setAIResults(result)
      
    } catch (error) {
      console.error('Error processing AI input:', error)
      // TODO: Show error message to user
      alert('Error processing your input. Please try again.')
    } finally {
      setIsProcessingAI(false)
    }
  }

  const applyAIResults = async () => {
    if (!aiResults) return
    
    setIsProcessingAI(true)
    try {
      console.log('Applying advanced AI results:', aiResults)
      
      // Create entities using the advanced system
      const request: AdvancedNoteProcessingRequest = {
        note_text: aiInputText,
        main_person_name: 'Alice',
        auto_create_entities: true
      }
      
      const createdEntities = await createEntitiesFromAI(request)
      console.log('Created entities with advanced system:', createdEntities)
      
      // Invalidate graph data to refresh the visualization
      queryClient.invalidateQueries({ queryKey: ['graph'] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
      
      // Close the modal
      closeAIInput()
      
    } catch (error) {
      console.error('Error applying AI results:', error)
      // TODO: Show error message to user
      alert('Error applying AI results. Please try again.')
    } finally {
      setIsProcessingAI(false)
    }
  }

  const openDeleteModal = () => {
    setIsDeleteModalOpen(true)
  }

  const closeDeleteModal = () => {
    setIsDeleteModalOpen(false)
  }

  const deleteNode = async () => {
    if (!selectedNode) return
    
    setIsDeletingNode(true)
    try {
      console.log('Deleting node:', selectedNode.id, selectedNode.type)
      
      // Call the appropriate delete mutation based on node type
      let result
      switch (selectedNode.type) {
        case 'person':
          result = await deletePersonMutation.mutateAsync(selectedNode.id)
          break
        case 'company':
          result = await deleteCompanyMutation.mutateAsync(selectedNode.id)
          break
        case 'topic':
          result = await deleteTopicMutation.mutateAsync(selectedNode.id)
          break
        case 'event':
          result = await deleteEventMutation.mutateAsync(selectedNode.id)
          break
        case 'location':
          result = await deleteLocationMutation.mutateAsync(selectedNode.id)
          break
        case 'interaction':
          result = await deleteInteractionMutation.mutateAsync(selectedNode.id)
          break
        default:
          throw new Error(`Unknown node type: ${selectedNode.type}`)
      }
      
      console.log(`Successfully deleted ${selectedNode.type}:`, selectedNode.id)
      
      // Invalidate graph data to refresh the visualization
      queryClient.invalidateQueries({ queryKey: ['graph'] })
      queryClient.invalidateQueries({ queryKey: ['stats'] })
      
      // Close the delete modal and node details
      closeDeleteModal()
      closeNodeDetails()
      
    } catch (error) {
      console.error('Error deleting node:', error)
      alert(`Error deleting ${selectedNode.type}. Please try again.`)
    } finally {
      setIsDeletingNode(false)
    }
  }

  return (
    <div className="w-full h-screen bg-gray-900 relative overflow-hidden">
      {/* Full-screen graph */}
      <div className="absolute inset-0">
        <D3GraphView 
          activeFilters={activeFilters} 
          layoutOptions={layoutOptions}
          onNodeClick={handleNodeClick}
          onDragStart={handleDragStart}
          selectedNode={selectedNode}
          ref={graphRef}
        />
      </div>

      {/* Top left menu button */}
      <div className="absolute top-4 left-4 z-10">
        <Button
          onClick={() => openMenu('main')}
          className="w-12 h-12 rounded-full bg-gray-800/80 backdrop-blur-sm border border-gray-600 hover:bg-gray-700/80 transition-all"
        >
          <MenuIcon />
        </Button>

        {/* Menu dropdown */}
        <AnimatePresence>
          {isMenuOpen && (
            <motion.div
              initial={{ opacity: 0, x: -10, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: -10, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="absolute top-0 left-16 bg-gray-800/90 backdrop-blur-md rounded-lg border border-gray-600 shadow-xl min-w-48"
            >
              <div className="p-2">
                <div className="px-3 py-2 text-sm font-medium text-gray-300 border-b border-gray-600 mb-2">
                  Network Journal
                </div>
                <div className="space-y-1">
                  <button className="w-full text-left px-3 py-2 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors">
                    👥 People ({people?.length || 0})
                  </button>
                  <button className="w-full text-left px-3 py-2 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors">
                    🏢 Companies
                  </button>
                  <button className="w-full text-left px-3 py-2 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors">
                    📝 Notes
                  </button>
                  <button className="w-full text-left px-3 py-2 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors">
                    🔔 Notifications ({suggestions?.length || 0})
                  </button>
                  <div className="border-t border-gray-600 my-2"></div>
                  <button className="w-full text-left px-3 py-2 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors">
                    ⚙️ Settings
                  </button>
                  <button className="w-full text-left px-3 py-2 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors">
                    📊 Analytics
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Graph options button */}
      <div className="absolute top-20 left-4 z-10">
        <Button
          onClick={() => openMenu('graph')}
          className="w-12 h-12 rounded-full bg-gray-800/80 backdrop-blur-sm border border-gray-600 hover:bg-gray-700/80 transition-all"
        >
          <GraphIcon />
        </Button>

        {/* Graph options dropdown */}
        <AnimatePresence>
          {isGraphOptionsOpen && (
            <motion.div
              initial={{ opacity: 0, x: -10, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: -10, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="absolute top-0 left-16 bg-gray-800/90 backdrop-blur-md rounded-lg border border-gray-600 shadow-xl min-w-48"
            >
              <div className="p-2">
                <div className="px-3 py-2 text-sm font-medium text-gray-300 border-b border-gray-600 mb-2">
                  Graph Options
                </div>
                <div className="space-y-1">
                  {Object.entries(activeFilters).map(([key, value]) => (
                    <label key={key} className="flex items-center px-3 py-2 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors cursor-pointer">
                      <input
                        type="checkbox"
                        checked={value}
                        onChange={(e) => {
                          e.stopPropagation()
                          toggleFilter(key)
                        }}
                        onClick={(e) => e.stopPropagation()}
                        className="mr-2"
                      />
                      {key.charAt(0).toUpperCase() + key.slice(1)}
                    </label>
                  ))}
                  <div className="border-t border-gray-600 my-2"></div>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation()
                      openMenu('layout')
                    }}
                    className="w-full text-left px-3 py-2 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors"
                  >
                    🎨 Layout Options
                  </button>
                  <button className="w-full text-left px-3 py-2 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors">
                    🔄 Reset View
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Layout options dropdown - replaces graph menu */}
        <AnimatePresence>
          {isLayoutOptionsOpen && (
            <motion.div
              initial={{ opacity: 0, x: -10, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: -10, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="absolute top-0 left-16 bg-gray-800/90 backdrop-blur-md rounded-lg border border-gray-600 shadow-xl w-64 max-h-96 overflow-y-auto"
            >
              <div className="p-3">
                <div className="flex items-center justify-between px-3 py-2 text-sm font-medium text-gray-300 border-b border-gray-600 mb-3">
                  <span>Layout Options</span>
                  <button 
                    onClick={() => openMenu('graph')}
                    className="text-gray-400 hover:text-white transition-colors"
                  >
                    ← Back
                  </button>
                </div>
                
                {/* Layout Algorithm */}
                <div className="mb-3">
                  <div className="px-3 py-1 text-xs font-medium text-gray-400 uppercase tracking-wide">
                    Layout Algorithm
                  </div>
                  <div className="space-y-1 mt-1">
                    {[
                      { value: 'force-directed', label: 'Force-Directed', desc: 'Organic clustering' },
                      { value: 'circular', label: 'Circular', desc: 'Even spacing' },
                      { value: 'hierarchical', label: 'Hierarchical', desc: 'Tree-like structure' },
                      { value: 'radial', label: 'Radial', desc: 'Center-outward' }
                    ].map(option => (
                      <label key={option.value} className="flex items-center px-3 py-1.5 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors cursor-pointer">
                        <input
                          type="radio"
                          name="algorithm"
                          value={option.value}
                          checked={layoutOptions.algorithm === option.value}
                          onChange={(e) => {
                            e.stopPropagation()
                            updateLayoutOption('algorithm', e.target.value)
                          }}
                          onClick={(e) => e.stopPropagation()}
                          className="mr-2"
                        />
                        <div>
                          <div className="font-medium">{option.label}</div>
                          <div className="text-xs text-gray-400">{option.desc}</div>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Visual Options */}
                <div className="mb-3">
                  <div className="px-3 py-1 text-xs font-medium text-gray-400 uppercase tracking-wide">
                    Visual Options
                  </div>
                  <div className="space-y-1 mt-1">
                    <label className="flex items-center px-3 py-1.5 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors cursor-pointer">
                      <input
                        type="checkbox"
                        checked={layoutOptions.showLabels}
                        onChange={(e) => {
                          e.stopPropagation()
                          updateLayoutOption('showLabels', e.target.checked)
                        }}
                        onClick={(e) => e.stopPropagation()}
                        className="mr-2"
                      />
                      Show Node Labels
                    </label>
                    <label className="flex items-center px-3 py-1.5 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors cursor-pointer">
                      <input
                        type="checkbox"
                        checked={layoutOptions.showGlows}
                        onChange={(e) => {
                          e.stopPropagation()
                          updateLayoutOption('showGlows', e.target.checked)
                        }}
                        onClick={(e) => e.stopPropagation()}
                        className="mr-2"
                      />
                      Show Glow Effects
                    </label>
                  </div>
                </div>

                {/* Node Size */}
                <div className="mb-3">
                  <div className="px-3 py-1 text-xs font-medium text-gray-400 uppercase tracking-wide">
                    Node Size
                  </div>
                  <div className="space-y-1 mt-1">
                    {[
                      { value: 'small', label: 'Small' },
                      { value: 'normal', label: 'Normal' },
                      { value: 'large', label: 'Large' }
                    ].map(option => (
                      <label key={option.value} className="flex items-center px-3 py-1.5 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors cursor-pointer">
                        <input
                          type="radio"
                          name="nodeSize"
                          value={option.value}
                          checked={layoutOptions.nodeSize === option.value}
                          onChange={(e) => {
                            e.stopPropagation()
                            updateLayoutOption('nodeSize', e.target.value)
                          }}
                          onClick={(e) => e.stopPropagation()}
                          className="mr-2"
                        />
                        {option.label}
                      </label>
                    ))}
                  </div>
                </div>

                {/* Physics Settings */}
                <div className="mb-3">
                  <div className="px-3 py-1 text-xs font-medium text-gray-400 uppercase tracking-wide">
                    Physics Settings
                  </div>
                  <div className="space-y-2 mt-1">
                    <div>
                      <div className="px-3 py-1 text-sm text-gray-300">Gravity Strength</div>
                      <div className="space-y-1">
                        {[
                          { value: 'weak', label: 'Weak' },
                          { value: 'normal', label: 'Normal' },
                          { value: 'strong', label: 'Strong' }
                        ].map(option => (
                          <label key={option.value} className="flex items-center px-3 py-1 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors cursor-pointer">
                            <input
                              type="radio"
                              name="gravityStrength"
                              value={option.value}
                              checked={layoutOptions.gravityStrength === option.value}
                              onChange={(e) => {
                                e.stopPropagation()
                                updateLayoutOption('gravityStrength', e.target.value)
                              }}
                              onClick={(e) => e.stopPropagation()}
                              className="mr-2"
                            />
                            {option.label}
                          </label>
                        ))}
                      </div>
                    </div>
                    <div>
                      <div className="px-3 py-1 text-sm text-gray-300">Spring Strength</div>
                      <div className="space-y-1">
                        {[
                          { value: 'loose', label: 'Loose' },
                          { value: 'normal', label: 'Normal' },
                          { value: 'tight', label: 'Tight' }
                        ].map(option => (
                          <label key={option.value} className="flex items-center px-3 py-1 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors cursor-pointer">
                            <input
                              type="radio"
                              name="springStrength"
                              value={option.value}
                              checked={layoutOptions.springStrength === option.value}
                              onChange={(e) => {
                                e.stopPropagation()
                                updateLayoutOption('springStrength', e.target.value)
                              }}
                              onClick={(e) => e.stopPropagation()}
                              className="mr-2"
                            />
                            {option.label}
                          </label>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Animation Speed */}
                <div className="mb-3">
                  <div className="px-3 py-1 text-xs font-medium text-gray-400 uppercase tracking-wide">
                    Animation Speed
                  </div>
                  <div className="space-y-1 mt-1">
                    {[
                      { value: 'slow', label: 'Slow' },
                      { value: 'normal', label: 'Normal' },
                      { value: 'fast', label: 'Fast' }
                    ].map(option => (
                      <label key={option.value} className="flex items-center px-3 py-1.5 text-sm text-gray-200 hover:bg-gray-700/50 rounded transition-colors cursor-pointer">
                        <input
                          type="radio"
                          name="animationSpeed"
                          value={option.value}
                          checked={layoutOptions.animationSpeed === option.value}
                          onChange={(e) => {
                            e.stopPropagation()
                            updateLayoutOption('animationSpeed', e.target.value)
                          }}
                          onClick={(e) => e.stopPropagation()}
                          className="mr-2"
                        />
                        {option.label}
                      </label>
                    ))}
                  </div>
                </div>

                {/* Link Opacity Slider */}
                <div className="mb-3">
                  <div className="px-3 py-1 text-xs font-medium text-gray-400 uppercase tracking-wide">
                    Link Opacity
                  </div>
                  <div className="px-3 py-2">
                    <input
                      type="range"
                      min="0.1"
                      max="1"
                      step="0.1"
                      value={layoutOptions.linkOpacity}
                      onChange={(e) => {
                        e.stopPropagation()
                        updateLayoutOption('linkOpacity', parseFloat(e.target.value))
                      }}
                      onClick={(e) => e.stopPropagation()}
                      className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                    />
                    <div className="text-xs text-gray-400 mt-1">
                      {Math.round(layoutOptions.linkOpacity * 100)}%
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Top right add button - moves left when details panel is open */}
      <div className={`absolute top-4 z-10 transition-all duration-300 ${selectedNode ? 'right-[420px]' : 'right-4'}`}>
        <Button
          onClick={openAIInput}
          className="w-12 h-12 rounded-full bg-blue-600/80 backdrop-blur-sm border border-blue-500 hover:bg-blue-500/80 transition-all"
        >
          <PlusIcon />
        </Button>
      </div>

      {/* Node Details Panel */}
      <AnimatePresence>
        {selectedNode && (
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="absolute top-0 right-0 w-96 h-full bg-gray-800/95 backdrop-blur-md border-l border-gray-600 shadow-2xl z-20"
          >
            <div className="h-full flex flex-col">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-600">
                <h2 className="text-xl font-bold text-white">Node Details</h2>
                <button
                  onClick={closeNodeDetails}
                  className="text-gray-400 hover:text-white transition-colors text-2xl w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-700"
                >
                  ×
                </button>
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto p-6 space-y-8">
                {/* Node Type and Basic Info */}
                <div className="bg-gray-700/30 rounded-xl p-6">
                  <div className="flex items-center space-x-4 mb-4">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                      selectedNode.type === 'person' ? 'bg-blue-500' :
                      selectedNode.type === 'company' ? 'bg-green-500' :
                      selectedNode.type === 'topic' ? 'bg-yellow-500' :
                      selectedNode.type === 'event' ? 'bg-purple-500' :
                      selectedNode.type === 'location' ? 'bg-pink-500' :
                      'bg-indigo-500'
                    }`}>
                      <span className="text-white text-xs font-bold">
                        {selectedNode.type.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-white">{selectedNode.label}</h3>
                      <div className="text-sm text-gray-300 capitalize">
                        {selectedNode.type} {selectedNode.isOwner && '• You'}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Node Properties */}
                {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 && (
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
                      <span className="w-1 h-6 bg-blue-500 rounded-full mr-3"></span>
                      Properties
                    </h4>
                    <div className="bg-gray-700/30 rounded-xl p-4 space-y-3">
                      {Object.entries(selectedNode.properties).map(([key, value]) => (
                        <div key={key} className="flex justify-between items-center py-2 border-b border-gray-600/30 last:border-b-0">
                          <span className="text-gray-300 capitalize font-medium">
                            {key.replace(/_/g, ' ')}
                          </span>
                          <span className="text-white text-right max-w-xs break-words">
                            {String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Connections */}
                <div>
                  <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
                    <span className="w-1 h-6 bg-green-500 rounded-full mr-3"></span>
                    Connections ({getNodeConnections(selectedNode.id).length})
                  </h4>
                  <div className="space-y-3">
                    {getNodeConnections(selectedNode.id).length > 0 ? (
                      getNodeConnections(selectedNode.id).map((connection, index) => (
                        <div key={index} className="bg-gray-700/30 rounded-xl p-4 hover:bg-gray-700/50 transition-colors">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center space-x-3">
                              <div className={`w-4 h-4 rounded-full ${
                                connection.connectedNode?.type === 'person' ? 'bg-blue-500' :
                                connection.connectedNode?.type === 'company' ? 'bg-green-500' :
                                connection.connectedNode?.type === 'topic' ? 'bg-yellow-500' :
                                connection.connectedNode?.type === 'event' ? 'bg-purple-500' :
                                connection.connectedNode?.type === 'location' ? 'bg-pink-500' :
                                'bg-indigo-500'
                              }`}></div>
                              <span className="text-white font-semibold">
                                {connection.connectedNode?.label || 'Unknown Node'}
                              </span>
                            </div>
                            <span className="text-xs text-gray-400 capitalize bg-gray-600/50 px-2 py-1 rounded-full">
                              {connection.type}
                            </span>
                          </div>
                          {connection.properties && Object.keys(connection.properties).length > 0 && (
                            <div className="text-xs text-gray-400 space-y-1">
                              {Object.entries(connection.properties).map(([key, value]) => (
                                <div key={key} className="flex justify-between">
                                  <span className="capitalize">{key.replace(/_/g, ' ')}:</span>
                                  <span className="text-gray-300">{String(value)}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))
                    ) : (
                      <div className="bg-gray-700/30 rounded-xl p-6 text-center">
                        <div className="text-gray-400 text-sm">No connections found</div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div>
                  <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
                    <span className="w-1 h-6 bg-purple-500 rounded-full mr-3"></span>
                    Actions
                  </h4>
                  <div className="space-y-3">
                    <button className="w-full px-4 py-3 text-sm bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition-colors font-medium">
                      ✏️ Edit {selectedNode.type}
                    </button>
                    <button className="w-full px-4 py-3 text-sm bg-gray-600 hover:bg-gray-500 text-white rounded-xl transition-colors font-medium">
                      📊 View History
                    </button>
                    <button className="w-full px-4 py-3 text-sm bg-gray-600 hover:bg-gray-500 text-white rounded-xl transition-colors font-medium">
                      ➕ Add Connection
                    </button>
                    <div className="border-t border-gray-600 my-3"></div>
                    <button 
                      onClick={openDeleteModal}
                      className="w-full px-4 py-3 text-sm bg-red-600 hover:bg-red-500 text-white rounded-xl transition-colors font-medium"
                    >
                      🗑️ Delete {selectedNode.type}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Stats overlay - top center */}
      <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10">
        <div className="bg-gray-800/80 backdrop-blur-sm rounded-lg border border-gray-600 px-4 py-2 flex items-center space-x-6">
          <div className="text-center">
            <div className="text-lg font-bold text-white">{stats?.total_people || 0}</div>
            <div className="text-xs text-gray-300">People</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-white">{stats?.total_companies || 0}</div>
            <div className="text-xs text-gray-300">Companies</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-white">{stats?.total_interactions || 0}</div>
            <div className="text-xs text-gray-300">Interactions</div>
          </div>
        </div>
      </div>

      {/* Bottom search bar - ChatGPT style */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-10 w-full max-w-2xl px-4">
        <form onSubmit={handleSearch} className="relative">
          <div className="relative">
            <Input
              type="text"
              placeholder="Ask about your network... (e.g., 'Who knows about AI?', 'Show me people at Google')"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-gray-800/90 backdrop-blur-md border border-gray-600 text-white placeholder-gray-400 pr-12 py-3 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              type="submit"
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-gray-400 hover:text-white transition-colors"
            >
              <SearchIcon />
            </button>
          </div>
        </form>
        
        {/* Quick suggestions */}
        <div className="flex justify-center mt-3 space-x-2">
          {['Who knows about AI?', 'Show me people at Google', 'Recent interactions', 'Network insights'].map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => setSearchQuery(suggestion)}
              className="px-3 py-1 text-xs bg-gray-800/60 backdrop-blur-sm border border-gray-600 text-gray-300 rounded-full hover:bg-gray-700/60 transition-colors"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>

      {/* AI Input Modal */}
      <AnimatePresence>
        {isAIInputOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-700 flex-shrink-0">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <AIIcon />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">AI Network Assistant</h2>
                    <p className="text-sm text-gray-400">Tell me about someone or something to add to your network</p>
                  </div>
                </div>
                <button
                  onClick={closeAIInput}
                  className="text-gray-400 hover:text-white transition-colors w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-800"
                >
                  <CloseIcon />
                </button>
              </div>

              {/* Content - Scrollable */}
              <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
                {/* Input Area - Fixed height when no results */}
                {!aiResults && (
                  <div className="flex-1 p-6 overflow-hidden">
                    <div className="h-full flex flex-col">
                      {/* Instructions */}
                      <div className="mb-4 p-4 bg-gray-800/50 rounded-xl border border-gray-700 flex-shrink-0">
                        <h3 className="text-sm font-semibold text-white mb-2">💡 Examples of what you can tell me:</h3>
                        <div className="text-xs text-gray-300 space-y-1">
                          <p>• "Met Sarah at the AI conference. She's a product manager at Google, really into machine learning and hiking."</p>
                          <p>• "John Doe works at Microsoft as a senior engineer, really into cloud computing."</p>
                          <p>• "Had lunch with Alice in San Francisco. She's starting a new company focused on sustainable tech."</p>
                        </div>
                      </div>

                      {/* Input */}
                      <div className="flex-1 flex flex-col min-h-0">
                        <textarea
                          value={aiInputText}
                          onChange={(e) => setAIInputText(e.target.value)}
                          placeholder="Tell me about someone or something to add to your network..."
                          className="flex-1 bg-gray-800 border border-gray-600 rounded-xl p-4 text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          disabled={isProcessingAI}
                        />
                        
                        {/* Submit Button */}
                        <div className="mt-4 flex justify-end flex-shrink-0">
                          <Button
                            onClick={processAIInput}
                            disabled={!aiInputText.trim() || isProcessingAI}
                            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-3 rounded-xl font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            {isProcessingAI ? (
                              <div className="flex items-center space-x-2">
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                <span>Processing...</span>
                              </div>
                            ) : (
                              <div className="flex items-center space-x-2">
                                <AIIcon />
                                <span>Analyze & Add</span>
                              </div>
                            )}
                          </Button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Results Area - Scrollable */}
                {aiResults && (
                  <div className="flex-1 flex flex-col min-h-0">
                    {/* Results Header */}
                    <div className="border-b border-gray-700 p-6 bg-gray-800/30 flex-shrink-0">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-white">Advanced AI Analysis</h3>
                        <div className="flex items-center space-x-2">
                          <div className={`w-2 h-2 rounded-full ${
                            aiResults.processing_confidence > 0.8 ? 'bg-green-500' : 
                            aiResults.processing_confidence > 0.6 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}></div>
                          <span className="text-sm text-gray-400">
                            {(aiResults.processing_confidence * 100).toFixed(0)}% confidence
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Scrollable Results Content */}
                    <div className="flex-1 overflow-y-auto p-6">
                      <AdvancedAIResults
                        results={aiResults}
                        onApply={applyAIResults}
                        onCancel={() => setAIResults(null)}
                        isLoading={isProcessingAI}
                      />
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Delete Confirmation Modal */}
      <AnimatePresence>
        {isDeleteModalOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-gray-900 border border-gray-700 rounded-2xl shadow-2xl w-full max-w-md"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-700">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-red-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-lg">🗑️</span>
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-white">Delete {selectedNode?.type}</h2>
                    <p className="text-sm text-gray-400">This action cannot be undone</p>
                  </div>
                </div>
                <button
                  onClick={closeDeleteModal}
                  className="text-gray-400 hover:text-white transition-colors w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-800"
                >
                  <CloseIcon />
                </button>
              </div>

              {/* Content */}
              <div className="p-6">
                <div className="mb-6">
                  <p className="text-gray-300 mb-4">
                    Are you sure you want to delete <span className="text-white font-semibold">{selectedNode?.label}</span>?
                  </p>
                  <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
                    <div className="flex items-start space-x-3">
                      <span className="text-red-400 text-lg">⚠️</span>
                      <div className="text-sm text-red-300">
                        <p className="font-semibold mb-1">This will also delete:</p>
                        <ul className="list-disc list-inside space-y-1">
                          <li>All connections to this {selectedNode?.type}</li>
                          <li>Any relationships involving this {selectedNode?.type}</li>
                          <li>All associated data and history</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex justify-end space-x-3">
                  <Button
                    onClick={closeDeleteModal}
                    disabled={isDeletingNode}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-xl transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={deleteNode}
                    disabled={isDeletingNode}
                    className="px-6 py-2 bg-red-600 hover:bg-red-500 text-white rounded-xl font-medium transition-all disabled:opacity-50"
                  >
                    {isDeletingNode ? (
                      <div className="flex items-center space-x-2">
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        <span>Deleting...</span>
                      </div>
                    ) : (
                      'Delete Permanently'
                    )}
                  </Button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Click outside to close dropdowns */}
      {(isMenuOpen || isGraphOptionsOpen || isLayoutOptionsOpen) && (
        <div
          className="absolute inset-0 z-5"
          onClick={closeAllMenus}
        />
      )}
    </div>
  )
}

export default Dashboard 