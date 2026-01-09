import { useState, useEffect } from 'react'
import { Plus, Trash2, Edit2, Save, X, Loader2, Package, Settings } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../../utils/api'

export default function ProductFeatureManager({ productId, productName, onUpdate }) {
  const [features, setFeatures] = useState([])
  const [loading, setLoading] = useState(true)
  const [adding, setAdding] = useState(false)
  const [editing, setEditing] = useState(null)
  const [deleting, setDeleting] = useState(null)
  
  // New feature form
  const [newFeature, setNewFeature] = useState({ slug: '', name: '', description: '' })
  
  // Edit feature form
  const [editFeature, setEditFeature] = useState({ name: '', description: '' })

  useEffect(() => {
    fetchFeatures()
  }, [productId])

  const fetchFeatures = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/products/${productId}/features`)
      setFeatures(response.data.features || [])
    } catch (err) {
      console.error('Failed to load features', err)
      toast.error('Fehler beim Laden der Features')
    } finally {
      setLoading(false)
    }
  }

  const handleAddFeature = async (e) => {
    e.preventDefault()
    if (!newFeature.slug.trim() || !newFeature.name.trim()) {
      toast.error('Slug und Name sind erforderlich')
      return
    }
    
    try {
      setAdding(true)
      const response = await api.post(`/products/${productId}/features`, {
        slug: newFeature.slug.toLowerCase().replace(/\s+/g, '_'),
        name: newFeature.name,
        description: newFeature.description || null
      })
      setFeatures(response.data.features)
      setNewFeature({ slug: '', name: '', description: '' })
      toast.success('Feature hinzugefügt')
      if (onUpdate) onUpdate()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Hinzufügen')
    } finally {
      setAdding(false)
    }
  }

  const startEdit = (feature) => {
    setEditing(feature.slug)
    setEditFeature({ name: feature.name, description: feature.description || '' })
  }

  const handleUpdateFeature = async (slug) => {
    try {
      const response = await api.put(`/products/${productId}/features/${slug}`, {
        name: editFeature.name,
        description: editFeature.description || null
      })
      setFeatures(response.data.features)
      setEditing(null)
      toast.success('Feature aktualisiert')
      if (onUpdate) onUpdate()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Aktualisieren')
    }
  }

  const handleDeleteFeature = async (slug) => {
    if (!confirm(`Feature "${slug}" wirklich löschen?`)) return
    
    try {
      setDeleting(slug)
      await api.delete(`/products/${productId}/features/${slug}`)
      setFeatures(features.filter(f => f.slug !== slug))
      toast.success('Feature gelöscht')
      if (onUpdate) onUpdate()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Löschen')
    } finally {
      setDeleting(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3 pb-4 border-b border-gray-200 dark:border-gray-700">
        <div className="p-2 bg-primary-100 dark:bg-primary-900/30 rounded-lg">
          <Package className="w-5 h-5 text-primary-600 dark:text-primary-400" />
        </div>
        <div>
          <h3 className="font-semibold text-gray-900 dark:text-white">{productName}</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {features.length} Feature{features.length !== 1 && 's'} definiert
          </p>
        </div>
      </div>

      {/* Add New Feature Form */}
      <form onSubmit={handleAddFeature} className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg space-y-3">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Neues Feature hinzufügen
        </h4>
        
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Slug (ID)</label>
            <input
              type="text"
              value={newFeature.slug}
              onChange={(e) => setNewFeature({ ...newFeature, slug: e.target.value })}
              placeholder="z.B. data_api"
              className="input text-sm"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Name</label>
            <input
              type="text"
              value={newFeature.name}
              onChange={(e) => setNewFeature({ ...newFeature, name: e.target.value })}
              placeholder="z.B. API-Zugriff"
              className="input text-sm"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Beschreibung (optional)</label>
          <input
            type="text"
            value={newFeature.description}
            onChange={(e) => setNewFeature({ ...newFeature, description: e.target.value })}
            placeholder="Kurze Beschreibung des Features"
            className="input text-sm"
          />
        </div>
        
        <button
          type="submit"
          disabled={adding}
          className="btn btn-primary w-full text-sm"
        >
          {adding ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <>
              <Plus className="w-4 h-4 mr-1" />
              Feature hinzufügen
            </>
          )}
        </button>
      </form>

      {/* Features List */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
          <Settings className="w-4 h-4" />
          Verfügbare Features
        </h4>
        
        {features.length === 0 ? (
          <p className="text-sm text-gray-500 dark:text-gray-400 py-4 text-center">
            Noch keine Features definiert
          </p>
        ) : (
          <div className="space-y-2">
            {features.map((feature) => (
              <div
                key={feature.slug}
                className="p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg"
              >
                {editing === feature.slug ? (
                  // Edit Mode
                  <div className="space-y-2">
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="block text-xs text-gray-500 mb-1">Slug (nicht änderbar)</label>
                        <input
                          type="text"
                          value={feature.slug}
                          disabled
                          className="input text-sm bg-gray-100 dark:bg-gray-700"
                        />
                      </div>
                      <div>
                        <label className="block text-xs text-gray-500 mb-1">Name</label>
                        <input
                          type="text"
                          value={editFeature.name}
                          onChange={(e) => setEditFeature({ ...editFeature, name: e.target.value })}
                          className="input text-sm"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs text-gray-500 mb-1">Beschreibung</label>
                      <input
                        type="text"
                        value={editFeature.description}
                        onChange={(e) => setEditFeature({ ...editFeature, description: e.target.value })}
                        className="input text-sm"
                      />
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleUpdateFeature(feature.slug)}
                        className="btn btn-primary text-sm flex-1"
                      >
                        <Save className="w-4 h-4 mr-1" />
                        Speichern
                      </button>
                      <button
                        onClick={() => setEditing(null)}
                        className="btn btn-secondary text-sm"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ) : (
                  // View Mode
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900 dark:text-white">
                          {feature.name}
                        </span>
                        <span className="text-xs px-1.5 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 font-mono">
                          {feature.slug}
                        </span>
                      </div>
                      {feature.description && (
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {feature.description}
                        </p>
                      )}
                    </div>
                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => startEdit(feature)}
                        className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDeleteFeature(feature.slug)}
                        disabled={deleting === feature.slug}
                        className="p-1.5 text-gray-400 hover:text-red-500 rounded"
                      >
                        {deleting === feature.slug ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
