// Enums matching backend types
export enum RelationshipType {
  COLLEAGUE = "colleague",
  FRIEND = "friend",
  FAMILY = "family",
  ACQUAINTANCE = "acquaintance",
  MENTOR = "mentor",
  MENTEE = "mentee"
}

export enum InteractionChannel {
  EMAIL = "email",
  CALL = "call",
  IN_PERSON = "in_person",
  VIDEO_CALL = "video_call",
  TEXT = "text",
  SOCIAL_MEDIA = "social_media"
}

export enum EventType {
  CONFERENCE = "conference",
  MEETUP = "meetup",
  PARTY = "party",
  MEETING = "meeting",
  LUNCH = "lunch",
  DINNER = "dinner"
}

export enum ContactStatus {
  ACTIVE = "active",
  NEEDS_FOLLOW_UP = "needs_follow_up",
  INACTIVE = "inactive"
}

export enum DataSource {
  USER_NOTE = "user_note",
  AGENT_SUGGESTION = "agent_suggestion",
  MANUAL_ENTRY = "manual_entry"
}

// Core entity interfaces
export interface Person {
  id?: string
  name: string
  email?: string
  phone?: string
  linkedin_url?: string
  last_contacted_date?: string
  birthday?: string
  source_of_contact?: string
  status: ContactStatus
  notes?: string
  created_at?: string
  updated_at?: string
  data_source: DataSource
}

export interface Company {
  id?: string
  name: string
  industry?: string
  website?: string
  created_at?: string
  updated_at?: string
}

export interface Topic {
  id?: string
  name: string
  created_at?: string
}

export interface Location {
  id?: string
  city: string
  state?: string
  country?: string
  created_at?: string
}

export interface Event {
  id?: string
  name: string
  date: string
  type: EventType
  location_id?: string
  created_at?: string
}

export interface Interaction {
  id?: string
  date: string
  channel: InteractionChannel
  summary?: string
  created_at?: string
  data_source: DataSource
}

// Relationship interfaces
export interface PersonRelationship {
  from_person_id: string
  to_person_id: string
  strength: number // 1-5 scale
  type: RelationshipType
  created_at?: string
}

export interface EmploymentRelationship {
  person_id: string
  company_id: string
  role: string
  start_date: string
  end_date?: string // null if current
  created_at?: string
}

// Graph visualization interfaces
export interface GraphNode {
  id: string
  label: string
  type: string // 'person', 'company', 'topic', etc.
  properties: Record<string, any>
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  type: string // relationship type
  properties: Record<string, any>
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

// AI processing interfaces
export interface AdvancedNoteProcessingRequest {
  note_text: string
  main_person_name?: string
  main_person_id?: string
  auto_create_entities?: boolean
}

export interface EntityMention {
  name: string
  entity_type: string // 'person', 'company', 'topic', 'event', 'location'
  confidence: number
  context: string
  properties: Record<string, any>
}

export interface RelationshipMention {
  from_entity: string
  to_entity: string
  relationship_type: string
  strength?: number
  context: string
  properties: Record<string, any>
}

export interface NoteAnalysis {
  entities: EntityMention[]
  relationships: RelationshipMention[]
  main_person_context?: string
  ambiguous_entities: string[]
  suggested_actions: string[]
  confidence_score: number
  processing_notes: string[]
}

export interface EntityResolution {
  action: 'create_new' | 'use_existing' | 'ask_user'
  entity: EntityMention
  existing_id?: string
  confidence: number
  reasoning?: string
}

export interface ValidatedRelationship {
  from_entity: string
  to_entity: string
  from_id: string
  to_id: string
  relationship_type: string
  strength?: number
  properties: Record<string, any>
  context: string
}

export interface CreatedEntity {
  name: string
  id: string
  action: 'created' | 'used_existing'
}

export interface CreatedEntities {
  people: CreatedEntity[]
  companies: CreatedEntity[]
  topics: CreatedEntity[]
  events: CreatedEntity[]
  locations: CreatedEntity[]
  relationships: Array<{
    from: string
    to: string
    type: string
    action: string
  }>
}

export interface AdvancedNoteProcessingResponse {
  analysis: NoteAnalysis
  resolved_entities: Record<string, EntityResolution>
  validated_relationships: ValidatedRelationship[]
  created_entities: CreatedEntities
  main_person_id?: string
  processing_confidence: number
}

// Legacy interfaces for backward compatibility
export interface NoteProcessingRequest {
  note_text: string
  person_id?: string
}

export interface NoteProcessingResult {
  person_name?: string
  company?: string
  role?: string
  topics_of_interest: string[]
  events_mentioned: string[]
  location?: string
  confidence: number
}

export interface AgentSuggestion {
  id?: string
  person_id: string
  suggestion_type: string
  suggested_data: Record<string, any>
  source_url?: string
  source_description: string
  confidence: number
  status: string // 'pending_review', 'accepted', 'rejected'
  created_at?: string
}

// API response interfaces
export interface APIResponse<T = any> {
  success: boolean
  data?: T
  message?: string
}

export interface PaginatedResponse<T = any> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// Form interfaces for creating/updating entities
export interface CreatePersonRequest {
  name: string
  email?: string
  phone?: string
  linkedin_url?: string
  source_of_contact?: string
  notes?: string
}

export interface UpdatePersonRequest extends Partial<CreatePersonRequest> {
  status?: ContactStatus
}

export interface CreateInteractionRequest {
  date: string
  channel: InteractionChannel
  summary?: string
}

// Dashboard statistics
export interface NetworkStats {
  total_people: number
  total_companies: number
  total_interactions: number
  recent_interactions: number // last 30 days
  people_needing_followup: number
  pending_suggestions: number
} 