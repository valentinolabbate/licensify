import { useState, useEffect } from 'react'
import { useLicenseStore } from '../../store/licenseStore'
import { X, Check, Package, Euro } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../../services/api'

export default function CreateLicenseModal({ onClose }) {
  const { createLicense, isLoading } = useLicenseStore()
  const [products, setProducts] = useState([])
  const [loadingProducts, setLoadingProducts] = useState(true)
  
  const [formData, setFormData] = useState({
    name: '',
    license_type: 'limited',
    max_devices: 1,
    trial_duration_days: 14,
    expires_at: '',
    product_id: '',
    features: [],
    price: '',
    note: '',
    metadata: {},
  })
  
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get('/products')
        setProducts(response.data.filter(p => p.is_active))
      } catch (err) {
        console.error('Failed to load products', err)
      } finally {
        setLoadingProducts(false)
      }
    }
    fetchProducts()
  }, [])
  
  const selectedProduct = products.find(p => p.id === parseInt(formData.product_id))
  
  const handleProductChange = (e) => {
    const productId = e.target.value
    const product = products.find(p => p.id === parseInt(productId))
    
    // Extract feature slugs from available_features (can be string or object)
    const featureSlugs = (product?.available_features || []).map(f => 
      typeof f === 'object' ? f.slug : f
    )
    
    setFormData({
      ...formData,
      product_id: productId,
      max_devices: product?.default_max_devices || 1,
      license_type: product?.default_license_type || 'limited',
      features: featureSlugs,
    })
  }
  
  // Helper to get feature display info (supports both string and object formats)
  const getFeatureInfo = (feature) => {
    if (typeof feature === 'object') {
      return {
        slug: feature.slug,
        name: feature.name || feature.slug,
        description: feature.description
      }
    }
    return {
      slug: feature,
      name: feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      description: null
    }
  }
  
  const toggleFeature = (featureSlug) => {
    setFormData(prev => ({
      ...prev,
      features: prev.features.includes(featureSlug)
        ? prev.features.filter(f => f !== featureSlug)
        : [...prev.features, featureSlug]
    }))
  }
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      const data = {
        ...formData,
        product_id: formData.product_id ? parseInt(formData.product_id) : null,
        max_devices: parseInt(formData.max_devices),
        price: formData.price ? parseFloat(formData.price) : null,
        trial_duration_days: formData.license_type === 'trial' 
          ? parseInt(formData.trial_duration_days) 
          : null,
        expires_at: formData.license_type === 'limited' && formData.expires_at
          ? new Date(formData.expires_at).toISOString()
          : null,
      }
      
      await createLicense(data)
      toast.success('Lizenz erfolgreich erstellt!')
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Erstellen der Lizenz')
    }
  }
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Neue Lizenz erstellen
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Product Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              <Package className="w-4 h-4 inline mr-1" />
              Produkt (optional)
            </label>
            {loadingProducts ? (
              <div className="h-10 flex items-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
              </div>
            ) : (
              <select
                value={formData.product_id}
                onChange={handleProductChange}
                className="input"
              >
                <option value="">Kein Produkt zugewiesen</option>
                {products.map(product => (
                  <option key={product.id} value={product.id}>
                    {product.name} (v{product.version})
                  </option>
                ))}
              </select>
            )}
          </div>
          
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Name (optional)
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input"
              placeholder="Kunde ABC - Standard"
            />
          </div>
          
          {/* License Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Lizenztyp
            </label>
            <select
              value={formData.license_type}
              onChange={(e) => setFormData({ ...formData, license_type: e.target.value })}
              className="input"
            >
              <option value="unlimited">Unbegrenzt (Läuft nie ab)</option>
              <option value="trial">Testversion (Zeitbegrenzt)</option>
              <option value="limited">Begrenzt (Läuft ab an Datum)</option>
              <option value="standard">Standard</option>
              <option value="professional">Professional</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </div>
          
          {/* Trial Duration */}
          {formData.license_type === 'trial' && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Testdauer (Tage)
              </label>
              <input
                type="number"
                min="1"
                max="365"
                value={formData.trial_duration_days}
                onChange={(e) => setFormData({ ...formData, trial_duration_days: e.target.value })}
                className="input"
              />
            </div>
          )}
          
          {/* Expires At */}
          {(formData.license_type === 'limited' || formData.license_type === 'standard' || formData.license_type === 'professional' || formData.license_type === 'enterprise') && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Ablaufdatum
              </label>
              <input
                type="date"
                value={formData.expires_at}
                onChange={(e) => setFormData({ ...formData, expires_at: e.target.value })}
                className="input"
                min={new Date().toISOString().split('T')[0]}
              />
            </div>
          )}
          
          {/* Max Devices */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Max. Geräte
            </label>
            <input
              type="number"
              min="0"
              value={formData.max_devices}
              onChange={(e) => setFormData({ ...formData, max_devices: e.target.value })}
              className="input"
            />
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              0 = unbegrenzte Geräte
            </p>
          </div>
          
          {/* Features Selection */}
          {selectedProduct && selectedProduct.available_features && selectedProduct.available_features.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Features
              </label>
              <div className="space-y-2">
                {selectedProduct.available_features.map((feature) => {
                  const featureInfo = getFeatureInfo(feature)
                  return (
                    <button
                      key={featureInfo.slug}
                      type="button"
                      onClick={() => toggleFeature(featureInfo.slug)}
                      className={`flex items-start gap-3 p-3 w-full rounded-lg border text-sm text-left transition-colors ${
                        formData.features.includes(featureInfo.slug)
                          ? 'bg-primary-50 border-primary-300 dark:bg-primary-900/30 dark:border-primary-600'
                          : 'bg-white border-gray-200 hover:bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:hover:bg-gray-650'
                      }`}
                    >
                      <div className={`w-5 h-5 rounded flex items-center justify-center flex-shrink-0 mt-0.5 ${
                        formData.features.includes(featureInfo.slug)
                          ? 'bg-primary-500 text-white'
                          : 'border-2 border-gray-300 dark:border-gray-500'
                      }`}>
                        {formData.features.includes(featureInfo.slug) && (
                          <Check size={12} />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <span className={`font-medium block ${
                          formData.features.includes(featureInfo.slug)
                            ? 'text-primary-700 dark:text-primary-300'
                            : 'text-gray-700 dark:text-gray-300'
                        }`}>
                          {featureInfo.name}
                        </span>
                        {featureInfo.description && (
                          <span className="text-xs text-gray-500 dark:text-gray-400 block mt-0.5">
                            {featureInfo.description}
                          </span>
                        )}
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          )}
          
          {/* Price */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              <Euro className="w-4 h-4 inline mr-1" />
              Preis (optional)
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              className="input"
              placeholder="0.00"
            />
          </div>
          
          {/* Note */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Notiz (optional)
            </label>
            <textarea
              value={formData.note}
              onChange={(e) => setFormData({ ...formData, note: e.target.value })}
              className="input"
              rows={2}
              placeholder="Interne Notizen zur Lizenz..."
            />
          </div>
          
          {/* Buttons */}
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="btn-secondary"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary disabled:opacity-50"
            >
              {isLoading ? 'Erstellen...' : 'Lizenz erstellen'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
