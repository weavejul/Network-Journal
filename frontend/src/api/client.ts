import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'
import type {
  APIResponse,
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
  AdvancedNoteProcessingRequest,
  AdvancedNoteProcessingResponse
} from '../types/models'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_PREFIX = '/api/v1'

class NetworkJournalAPI {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}${API_PREFIX}`,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor for logging
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('API Request Error:', error)
        return Promise.reject(error)
      }
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        return response
      },
      (error) => {
        console.error('API Response Error:', error.response?.data || error.message)
        return Promise.reject(error)
      }
    )
  }

  // Health check
  async healthCheck(): Promise<APIResponse> {
    const response = await this.client.get('/health')
    return response.data
  }

  // People endpoints
  async getPeople(): Promise<APIResponse<Person[]>> {
    const response = await this.client.get('/people/')
    return response.data
  }

  async getPerson(id: string): Promise<APIResponse<Person>> {
    const response = await this.client.get(`/people/${id}`)
    return response.data
  }

  async createPerson(person: CreatePersonRequest): Promise<APIResponse<Person>> {
    const response = await this.client.post('/people/', person)
    return response.data
  }

  async updatePerson(id: string, person: UpdatePersonRequest): Promise<APIResponse<Person>> {
    const response = await this.client.put(`/people/${id}`, person)
    return response.data
  }

  async deletePerson(id: string): Promise<APIResponse> {
    const response = await this.client.delete(`/people/${id}`)
    return response.data
  }

  // Companies endpoints
  async getCompanies(): Promise<APIResponse<Company[]>> {
    const response = await this.client.get('/companies/')
    return response.data
  }

  async getCompany(id: string): Promise<APIResponse<Company>> {
    const response = await this.client.get(`/companies/${id}`)
    return response.data
  }

  async createCompany(company: Partial<Company>): Promise<APIResponse<Company>> {
    const response = await this.client.post('/companies/', company)
    return response.data
  }

  async updateCompany(id: string, company: Partial<Company>): Promise<APIResponse<Company>> {
    const response = await this.client.put(`/companies/${id}`, company)
    return response.data
  }

  async deleteCompany(id: string): Promise<APIResponse> {
    const response = await this.client.delete(`/companies/${id}`)
    return response.data
  }

  // Interactions endpoints
  async getInteractions(): Promise<APIResponse<Interaction[]>> {
    const response = await this.client.get('/interactions/')
    return response.data
  }

  async getInteraction(id: string): Promise<APIResponse<Interaction>> {
    const response = await this.client.get(`/interactions/${id}`)
    return response.data
  }

  async createInteraction(interaction: CreateInteractionRequest): Promise<APIResponse<Interaction>> {
    const response = await this.client.post('/interactions/', interaction)
    return response.data
  }

  async updateInteraction(id: string, interaction: Partial<Interaction>): Promise<APIResponse<Interaction>> {
    const response = await this.client.put(`/interactions/${id}`, interaction)
    return response.data
  }

  async deleteInteraction(id: string): Promise<APIResponse> {
    const response = await this.client.delete(`/interactions/${id}`)
    return response.data
  }

  // Topics endpoints
  async getTopics(): Promise<APIResponse<Topic[]>> {
    const response = await this.client.get('/topics/')
    return response.data
  }

  async getTopic(id: string): Promise<APIResponse<Topic>> {
    const response = await this.client.get(`/topics/${id}`)
    return response.data
  }

  async createTopic(topic: Partial<Topic>): Promise<APIResponse<Topic>> {
    const response = await this.client.post('/topics/', topic)
    return response.data
  }

  async updateTopic(id: string, topic: Partial<Topic>): Promise<APIResponse<Topic>> {
    const response = await this.client.put(`/topics/${id}`, topic)
    return response.data
  }

  async deleteTopic(id: string): Promise<APIResponse> {
    const response = await this.client.delete(`/topics/${id}`)
    return response.data
  }

  // Events endpoints
  async getEvents(): Promise<APIResponse<Event[]>> {
    const response = await this.client.get('/events/')
    return response.data
  }

  async getEvent(id: string): Promise<APIResponse<Event>> {
    const response = await this.client.get(`/events/${id}`)
    return response.data
  }

  async createEvent(event: Partial<Event>): Promise<APIResponse<Event>> {
    const response = await this.client.post('/events/', event)
    return response.data
  }

  async updateEvent(id: string, event: Partial<Event>): Promise<APIResponse<Event>> {
    const response = await this.client.put(`/events/${id}`, event)
    return response.data
  }

  async deleteEvent(id: string): Promise<APIResponse> {
    const response = await this.client.delete(`/events/${id}`)
    return response.data
  }

  // Locations endpoints
  async getLocations(): Promise<APIResponse<Location[]>> {
    const response = await this.client.get('/locations/')
    return response.data
  }

  async getLocation(id: string): Promise<APIResponse<Location>> {
    const response = await this.client.get(`/locations/${id}`)
    return response.data
  }

  async createLocation(location: Partial<Location>): Promise<APIResponse<Location>> {
    const response = await this.client.post('/locations/', location)
    return response.data
  }

  async updateLocation(id: string, location: Partial<Location>): Promise<APIResponse<Location>> {
    const response = await this.client.put(`/locations/${id}`, location)
    return response.data
  }

  async deleteLocation(id: string): Promise<APIResponse> {
    const response = await this.client.delete(`/locations/${id}`)
    return response.data
  }

  // Graph endpoints
  async getGraphData(): Promise<APIResponse<GraphData>> {
    const response = await this.client.get('/graph/data')
    return response.data
  }

  async getGraphDataForPerson(personId: string): Promise<APIResponse<GraphData>> {
    const response = await this.client.get(`/graph/person/${personId}`)
    return response.data
  }

  // AI endpoints
  async processNoteAdvanced(request: AdvancedNoteProcessingRequest): Promise<APIResponse<AdvancedNoteProcessingResponse>> {
    const response = await this.client.post('/ai/process-note-advanced', request)
    return response.data
  }

  async processNote(request: NoteProcessingRequest): Promise<APIResponse<NoteProcessingResult>> {
    // Legacy endpoint - redirects to advanced processing
    const advancedRequest: AdvancedNoteProcessingRequest = {
      note_text: request.note_text,
      main_person_name: 'Alice', // Default main person
      auto_create_entities: false
    }
    const response = await this.client.post('/ai/process-note', advancedRequest)
    return response.data
  }

  async testAIExtraction(request: AdvancedNoteProcessingRequest): Promise<APIResponse<AdvancedNoteProcessingResponse>> {
    const response = await this.client.post('/ai/test-extraction', request)
    return response.data
  }

  async createEntitiesFromAI(request: AdvancedNoteProcessingRequest): Promise<APIResponse<any>> {
    const response = await this.client.post('/ai/create-entities', request)
    return response.data
  }

  async getDisambiguationSuggestions(entityName: string, entityType: string): Promise<APIResponse<any>> {
    const response = await this.client.get(`/ai/disambiguation/${entityName}?entity_type=${entityType}`)
    return response.data
  }

  async getAgentSuggestions(): Promise<APIResponse<AgentSuggestion[]>> {
    const response = await this.client.get('/ai/suggestions')
    return response.data
  }

  async acceptSuggestion(suggestionId: string): Promise<APIResponse> {
    const response = await this.client.post(`/ai/suggestions/${suggestionId}/accept`)
    return response.data
  }

  async rejectSuggestion(suggestionId: string): Promise<APIResponse> {
    const response = await this.client.post(`/ai/suggestions/${suggestionId}/reject`)
    return response.data
  }

  // Dashboard endpoints
  async getNetworkStats(): Promise<APIResponse<NetworkStats>> {
    const response = await this.client.get('/graph/stats')
    return response.data
  }
}

// Export singleton instance
export const api = new NetworkJournalAPI()
export default api

// AI Services
export const processNoteWithAIAdvanced = async (request: AdvancedNoteProcessingRequest): Promise<AdvancedNoteProcessingResponse> => {
  const response = await fetch(`${API_BASE_URL}${API_PREFIX}/ai/process-note-advanced`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`Advanced AI processing failed: ${response.statusText}`)
  }

  const result = await response.json()
  return result.data
}

export const processNoteWithAI = async (noteText: string): Promise<any> => {
  const request: AdvancedNoteProcessingRequest = {
    note_text: noteText,
    main_person_name: 'Alice',
    auto_create_entities: false
  }
  
  const response = await fetch(`${API_BASE_URL}${API_PREFIX}/ai/process-note`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`AI processing failed: ${response.statusText}`)
  }

  const result = await response.json()
  return result.data
}

export const testAIExtraction = async (request: AdvancedNoteProcessingRequest): Promise<AdvancedNoteProcessingResponse> => {
  const response = await fetch(`${API_BASE_URL}${API_PREFIX}/ai/test-extraction`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`AI extraction test failed: ${response.statusText}`)
  }

  const result = await response.json()
  return result.data
}

export const createEntitiesFromAI = async (request: AdvancedNoteProcessingRequest): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}${API_PREFIX}/ai/create-entities`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    throw new Error(`Entity creation failed: ${response.statusText}`)
  }

  const result = await response.json()
  return result.data
}

export const getDisambiguationSuggestions = async (entityName: string, entityType: string): Promise<any> => {
  const response = await fetch(`${API_BASE_URL}${API_PREFIX}/ai/disambiguation/${entityName}?entity_type=${entityType}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Disambiguation suggestions failed: ${response.statusText}`)
  }

  const result = await response.json()
  return result.data
} 