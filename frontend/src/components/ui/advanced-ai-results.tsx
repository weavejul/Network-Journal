import React from 'react'
import type { AdvancedNoteProcessingResponse, EntityResolution, ValidatedRelationship } from '../../types/models'

interface AdvancedAIResultsProps {
  results: AdvancedNoteProcessingResponse
  onApply: () => void
  onCancel: () => void
  isLoading?: boolean
}

export function AdvancedAIResults({ results, onApply, onCancel, isLoading = false }: AdvancedAIResultsProps) {
  const { analysis, resolved_entities, validated_relationships, created_entities, processing_confidence } = results

  const getEntityTypeColor = (entityType: string) => {
    switch (entityType) {
      case 'person': return 'bg-blue-100 text-blue-800'
      case 'company': return 'bg-green-100 text-green-800'
      case 'topic': return 'bg-purple-100 text-purple-800'
      case 'event': return 'bg-orange-100 text-orange-800'
      case 'location': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getActionColor = (action: string) => {
    switch (action) {
      case 'create_new': return 'bg-green-100 text-green-800'
      case 'use_existing': return 'bg-blue-100 text-blue-800'
      case 'ask_user': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* Processing Summary */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">AI Analysis Summary</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium">Confidence:</span>
            <span className={`ml-2 px-2 py-1 rounded text-xs ${
              processing_confidence > 0.8 ? 'bg-green-100 text-green-800' :
              processing_confidence > 0.6 ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              {(processing_confidence * 100).toFixed(1)}%
            </span>
          </div>
          <div>
            <span className="font-medium">Entities Found:</span>
            <span className="ml-2">{analysis.entities.length}</span>
          </div>
          <div>
            <span className="font-medium">Relationships:</span>
            <span className="ml-2">{analysis.relationships.length}</span>
          </div>
          <div>
            <span className="font-medium">Ambiguous Entities:</span>
            <span className="ml-2">{analysis.ambiguous_entities.length}</span>
          </div>
        </div>
      </div>

      {/* Entity Resolution */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Entity Resolution</h3>
        <div className="space-y-3">
          {Object.entries(resolved_entities).map(([entityName, resolution]) => (
            <div key={entityName} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="font-medium">{entityName}</span>
                  <span className={`px-2 py-1 rounded text-xs ${getEntityTypeColor(resolution.entity.entity_type)}`}>
                    {resolution.entity.entity_type}
                  </span>
                  <span className={`px-2 py-1 rounded text-xs ${getActionColor(resolution.action)}`}>
                    {resolution.action.replace('_', ' ')}
                  </span>
                </div>
                <span className="text-sm text-gray-500">
                  {(resolution.confidence * 100).toFixed(0)}% confidence
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-2">{resolution.entity.context}</p>
              {resolution.reasoning && (
                <p className="text-xs text-gray-500 italic">"{resolution.reasoning}"</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Relationships */}
      {validated_relationships.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Relationships</h3>
          <div className="space-y-2">
            {validated_relationships.map((rel, index) => (
              <div key={index} className="flex items-center space-x-2 text-sm">
                <span className="font-medium">{rel.from_entity}</span>
                <span className="text-gray-400">→</span>
                <span className="font-medium">{rel.to_entity}</span>
                <span className={`px-2 py-1 rounded text-xs bg-blue-100 text-blue-800`}>
                  {rel.relationship_type}
                </span>
                {rel.strength && (
                  <span className="text-xs text-gray-500">(strength: {rel.strength})</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Processing Notes */}
      {analysis.processing_notes.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Processing Notes</h3>
          <ul className="space-y-1">
            {analysis.processing_notes.map((note, index) => (
              <li key={index} className="text-sm text-gray-600">• {note}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end space-x-3">
        <button
          onClick={onCancel}
          disabled={isLoading}
          className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
        >
          Cancel
        </button>
        <button
          onClick={onApply}
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Applying...' : 'Apply to Network'}
        </button>
      </div>
    </div>
  )
} 