import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from './client'
import type {
  Person,
  Company,
  Interaction,
  Topic,
  Event,
  Location,
  GraphData,
  CreatePersonRequest,
  UpdatePersonRequest,
  CreateInteractionRequest,
  NoteProcessingRequest,
  NoteProcessingResult,
  AgentSuggestion,
  NetworkStats,
  AdvancedNoteProcessingRequest
} from '../types/models'

// Query keys
export const queryKeys = {
  people: ['people'] as const,
  person: (id: string) => ['people', id] as const,
  companies: ['companies'] as const,
  company: (id: string) => ['companies', id] as const,
  interactions: ['interactions'] as const,
  interaction: (id: string) => ['interactions', id] as const,
  topics: ['topics'] as const,
  topic: (id: string) => ['topics', id] as const,
  events: ['events'] as const,
  event: (id: string) => ['events', id] as const,
  locations: ['locations'] as const,
  location: (id: string) => ['locations', id] as const,
  graph: ['graph'] as const,
  graphForPerson: (personId: string) => ['graph', 'person', personId] as const,
  stats: ['stats'] as const,
  suggestions: ['suggestions'] as const,
} as const

// People queries
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

export function usePerson(id: string) {
  return useQuery({
    queryKey: queryKeys.person(id),
    queryFn: async () => {
      const response = await api.getPerson(id)
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch person')
      }
      return response.data
    },
    enabled: !!id,
  })
}

// People mutations
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

export function useUpdatePerson() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ id, person }: { id: string; person: UpdatePersonRequest }) => {
      const response = await api.updatePerson(id, person)
      if (!response.success) {
        throw new Error(response.message || 'Failed to update person')
      }
      return response.data
    },
    onSuccess: (data, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.people })
      queryClient.invalidateQueries({ queryKey: queryKeys.person(id) })
    },
  })
}

export function useDeletePerson() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.deletePerson(id)
      if (!response.success) {
        throw new Error(response.message || 'Failed to delete person')
      }
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.people })
    },
  })
}

// Companies queries
export function useCompanies() {
  return useQuery({
    queryKey: queryKeys.companies,
    queryFn: async () => {
      const response = await api.getCompanies()
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch companies')
      }
      return response.data || []
    },
  })
}

export function useCompany(id: string) {
  return useQuery({
    queryKey: queryKeys.company(id),
    queryFn: async () => {
      const response = await api.getCompany(id)
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch company')
      }
      return response.data
    },
    enabled: !!id,
  })
}

// Companies mutations
export function useCreateCompany() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (company: Partial<Company>) => {
      const response = await api.createCompany(company)
      if (!response.success) {
        throw new Error(response.message || 'Failed to create company')
      }
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.companies })
    },
  })
}

export function useUpdateCompany() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ id, company }: { id: string; company: Partial<Company> }) => {
      const response = await api.updateCompany(id, company)
      if (!response.success) {
        throw new Error(response.message || 'Failed to update company')
      }
      return response.data
    },
    onSuccess: (data, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.companies })
      queryClient.invalidateQueries({ queryKey: queryKeys.company(id) })
    },
  })
}

export function useDeleteCompany() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.deleteCompany(id)
      if (!response.success) {
        throw new Error(response.message || 'Failed to delete company')
      }
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.companies })
    },
  })
}

// Interactions queries
export function useInteractions() {
  return useQuery({
    queryKey: queryKeys.interactions,
    queryFn: async () => {
      const response = await api.getInteractions()
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch interactions')
      }
      return response.data || []
    },
  })
}

export function useInteraction(id: string) {
  return useQuery({
    queryKey: queryKeys.interaction(id),
    queryFn: async () => {
      const response = await api.getInteraction(id)
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch interaction')
      }
      return response.data
    },
    enabled: !!id,
  })
}

// Interactions mutations
export function useCreateInteraction() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (interaction: CreateInteractionRequest) => {
      const response = await api.createInteraction(interaction)
      if (!response.success) {
        throw new Error(response.message || 'Failed to create interaction')
      }
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.interactions })
    },
  })
}

export function useUpdateInteraction() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ id, interaction }: { id: string; interaction: Partial<Interaction> }) => {
      const response = await api.updateInteraction(id, interaction)
      if (!response.success) {
        throw new Error(response.message || 'Failed to update interaction')
      }
      return response.data
    },
    onSuccess: (data, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.interactions })
      queryClient.invalidateQueries({ queryKey: queryKeys.interaction(id) })
    },
  })
}

export function useDeleteInteraction() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.deleteInteraction(id)
      if (!response.success) {
        throw new Error(response.message || 'Failed to delete interaction')
      }
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.interactions })
    },
  })
}

// Topics queries
export function useTopics() {
  return useQuery({
    queryKey: queryKeys.topics,
    queryFn: async () => {
      const response = await api.getTopics()
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch topics')
      }
      return response.data || []
    },
  })
}

export function useTopic(id: string) {
  return useQuery({
    queryKey: queryKeys.topic(id),
    queryFn: async () => {
      const response = await api.getTopic(id)
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch topic')
      }
      return response.data
    },
    enabled: !!id,
  })
}

// Topics mutations
export function useCreateTopic() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (topic: Partial<Topic>) => {
      const response = await api.createTopic(topic)
      if (!response.success) {
        throw new Error(response.message || 'Failed to create topic')
      }
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.topics })
    },
  })
}

export function useUpdateTopic() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ id, topic }: { id: string; topic: Partial<Topic> }) => {
      const response = await api.updateTopic(id, topic)
      if (!response.success) {
        throw new Error(response.message || 'Failed to update topic')
      }
      return response.data
    },
    onSuccess: (data, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.topics })
      queryClient.invalidateQueries({ queryKey: queryKeys.topic(id) })
    },
  })
}

export function useDeleteTopic() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.deleteTopic(id)
      if (!response.success) {
        throw new Error(response.message || 'Failed to delete topic')
      }
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.topics })
    },
  })
}

// Events queries
export function useEvents() {
  return useQuery({
    queryKey: queryKeys.events,
    queryFn: async () => {
      const response = await api.getEvents()
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch events')
      }
      return response.data || []
    },
  })
}

export function useEvent(id: string) {
  return useQuery({
    queryKey: queryKeys.event(id),
    queryFn: async () => {
      const response = await api.getEvent(id)
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch event')
      }
      return response.data
    },
    enabled: !!id,
  })
}

// Events mutations
export function useCreateEvent() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (event: Partial<Event>) => {
      const response = await api.createEvent(event)
      if (!response.success) {
        throw new Error(response.message || 'Failed to create event')
      }
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.events })
    },
  })
}

export function useUpdateEvent() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ id, event }: { id: string; event: Partial<Event> }) => {
      const response = await api.updateEvent(id, event)
      if (!response.success) {
        throw new Error(response.message || 'Failed to update event')
      }
      return response.data
    },
    onSuccess: (data, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.events })
      queryClient.invalidateQueries({ queryKey: queryKeys.event(id) })
    },
  })
}

export function useDeleteEvent() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.deleteEvent(id)
      if (!response.success) {
        throw new Error(response.message || 'Failed to delete event')
      }
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.events })
    },
  })
}

// Locations queries
export function useLocations() {
  return useQuery({
    queryKey: queryKeys.locations,
    queryFn: async () => {
      const response = await api.getLocations()
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch locations')
      }
      return response.data || []
    },
  })
}

export function useLocation(id: string) {
  return useQuery({
    queryKey: queryKeys.location(id),
    queryFn: async () => {
      const response = await api.getLocation(id)
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch location')
      }
      return response.data
    },
    enabled: !!id,
  })
}

// Locations mutations
export function useCreateLocation() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (location: Partial<Location>) => {
      const response = await api.createLocation(location)
      if (!response.success) {
        throw new Error(response.message || 'Failed to create location')
      }
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.locations })
    },
  })
}

export function useUpdateLocation() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async ({ id, location }: { id: string; location: Partial<Location> }) => {
      const response = await api.updateLocation(id, location)
      if (!response.success) {
        throw new Error(response.message || 'Failed to update location')
      }
      return response.data
    },
    onSuccess: (data, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.locations })
      queryClient.invalidateQueries({ queryKey: queryKeys.location(id) })
    },
  })
}

export function useDeleteLocation() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await api.deleteLocation(id)
      if (!response.success) {
        throw new Error(response.message || 'Failed to delete location')
      }
      return response
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.locations })
    },
  })
}

// Graph queries
export function useGraphData() {
  return useQuery({
    queryKey: queryKeys.graph,
    queryFn: async () => {
      const response = await api.getGraphData()
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch graph data')
      }
      return response.data
    },
  })
}

export function useGraphDataForPerson(personId: string) {
  return useQuery({
    queryKey: queryKeys.graphForPerson(personId),
    queryFn: async () => {
      const response = await api.getGraphDataForPerson(personId)
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch graph data for person')
      }
      return response.data
    },
    enabled: !!personId,
  })
}

// Stats queries
export function useNetworkStats() {
  return useQuery({
    queryKey: queryKeys.stats,
    queryFn: async () => {
      const response = await api.getNetworkStats()
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch network stats')
      }
      return response.data
    },
  })
}

// AI queries
export function useAgentSuggestions() {
  return useQuery({
    queryKey: queryKeys.suggestions,
    queryFn: async () => {
      const response = await api.getAgentSuggestions()
      if (!response.success) {
        throw new Error(response.message || 'Failed to fetch agent suggestions')
      }
      return response.data || []
    },
  })
}

// AI mutations
export function useProcessNoteAdvanced() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (request: AdvancedNoteProcessingRequest) => {
      const response = await api.processNoteAdvanced(request)
      if (!response.success) {
        throw new Error(response.message || 'Failed to process note with advanced AI')
      }
      return response.data
    },
    onSuccess: () => {
      // Invalidate relevant queries after processing a note
      queryClient.invalidateQueries({ queryKey: queryKeys.people })
      queryClient.invalidateQueries({ queryKey: queryKeys.companies })
      queryClient.invalidateQueries({ queryKey: queryKeys.topics })
      queryClient.invalidateQueries({ queryKey: queryKeys.events })
      queryClient.invalidateQueries({ queryKey: queryKeys.locations })
      queryClient.invalidateQueries({ queryKey: queryKeys.graph })
      queryClient.invalidateQueries({ queryKey: queryKeys.stats })
    },
  })
}

export function useProcessNote() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (request: NoteProcessingRequest) => {
      const response = await api.processNote(request)
      if (!response.success) {
        throw new Error(response.message || 'Failed to process note')
      }
      return response.data
    },
    onSuccess: () => {
      // Invalidate relevant queries after processing a note
      queryClient.invalidateQueries({ queryKey: queryKeys.people })
      queryClient.invalidateQueries({ queryKey: queryKeys.companies })
      queryClient.invalidateQueries({ queryKey: queryKeys.topics })
      queryClient.invalidateQueries({ queryKey: queryKeys.graph })
    },
  })
}

export function useTestAIExtraction() {
  return useMutation({
    mutationFn: async (request: AdvancedNoteProcessingRequest) => {
      const response = await api.testAIExtraction(request)
      if (!response.success) {
        throw new Error(response.message || 'Failed to test AI extraction')
      }
      return response.data
    },
  })
}

export function useCreateEntitiesFromAI() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: async (request: AdvancedNoteProcessingRequest) => {
      const response = await api.createEntitiesFromAI(request)
      if (!response.success) {
        throw new Error(response.message || 'Failed to create entities from AI')
      }
      return response.data
    },
    onSuccess: () => {
      // Invalidate all relevant queries after creating entities
      queryClient.invalidateQueries({ queryKey: queryKeys.people })
      queryClient.invalidateQueries({ queryKey: queryKeys.companies })
      queryClient.invalidateQueries({ queryKey: queryKeys.topics })
      queryClient.invalidateQueries({ queryKey: queryKeys.events })
      queryClient.invalidateQueries({ queryKey: queryKeys.locations })
      queryClient.invalidateQueries({ queryKey: queryKeys.graph })
      queryClient.invalidateQueries({ queryKey: queryKeys.stats })
    },
  })
}

export function useGetDisambiguationSuggestions(entityName: string, entityType: string) {
  return useQuery({
    queryKey: ['disambiguation', entityName, entityType],
    queryFn: async () => {
      const response = await api.getDisambiguationSuggestions(entityName, entityType)
      if (!response.success) {
        throw new Error(response.message || 'Failed to get disambiguation suggestions')
      }
      return response.data
    },
    enabled: false, // Only run when explicitly called
  })
} 