import { useState, useEffect } from 'react'
import { useLicenseStore } from '../../store/licenseStore'
import { useAuthStore } from '../../store/authStore'
import { X, DollarSign, Info, Package, Check } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../../services/api'

export default function CreateLicenseModal({ onClose }) {
  const { createLicense, isLoading } = useLicenseStore()
  const { user } = useAuthStore()
  const [products, setProducts] = useState([])
  const [loadingProducts, setLoadingProducts] = useState(true)
  
  // Standard-Ablaufdatum: 1 Jahr ab heute
  const getDefaultExpiryDate = () => {
    const date = new Date()
    date.setFullYear(date.getFullYear() + 1)
    return date.toISOString().split('T')[0]
  }
  
  const [formData, setFormData] = useState({
    name: '',
    license_type: 'limited',
    max_devices: 1,
    trial_duration_days: 14,
    expires_at: getDefaultExpiryDate(),
    product_id: '',
    features: [],
  })
  
  // Revenue fields (admin only)
  const [trackRevenue, setTrackRevenue] = useState(false)
  const [revenueAmount, setRevenueAmount] = useState('')
  const [revenueNotes, setRevenueNotes] = useState('')
  
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await api.get('/products')
        // API returns { products: [...], total: n }
        const allProducts = response.data.products || []
        setProducts(allProducts.filter(p => p.is_active))
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
    const newLicenseType = product?.default_license_type || 'limited'
    const timeLimited = ['limited', 'standard', 'professional', 'enterprise']
    
    setFormData({
      ...formData,
      product_id: productId,
      max_devices: product?.default_max_devices || 1,
      license_type: newLicenseType,
      features: product?.available_features || [],
      // Setze Standard-Ablaufdatum wenn zeitlich begrenzter Typ
      expires_at: timeLimited.includes(newLicenseType) ? getDefaultExpiryDate() : formData.expires_at,
    })
  }
  
  const toggleFeature = (featureId) => {
    setFormData(prev => ({
      ...prev,
      features: prev.features.includes(featureId)
        ? prev.features.filter(f => f !== featureId)
        : [...prev.features, featureId]
    }))
  }
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Validation für zeitlich begrenzte Lizenzen
    const timeLimitedTypes = ['limited', 'standard', 'professional', 'enterprise']
    if (timeLimitedTypes.includes(formData.license_type) && !formData.expires_at) {
      toast.error('Bitte wählen Sie ein Ablaufdatum für die zeitlich begrenzte Lizenz')
      return
    }
    
    try {
      // Berechne die Anzahl der Tage bis zum Ablaufdatum
      let durationDays = null
      if (timeLimitedTypes.includes(formData.license_type) && formData.expires_at) {
        const today = new Date()
        today.setHours(0, 0, 0, 0)
        const expiry = new Date(formData.expires_at)
        expiry.setHours(0, 0, 0, 0)
        durationDays = Math.ceil((expiry - today) / (1000 * 60 * 60 * 24))
        if (durationDays < 1) durationDays = 1
      }
      
      const data = {
        ...formData,
        product_id: formData.product_id ? parseInt(formData.product_id) : null,
        max_devices: parseInt(formData.max_devices),
        trial_duration_days: formData.license_type === 'trial' 
          ? parseInt(formData.trial_duration_days) 
          : null,
        duration_days: durationDays,
        expires_at: null, // Backend berechnet das Datum aus duration_days
      }
      
      // Add revenue data if tracking is enabled
      if (trackRevenue && revenueAmount) {
        data.initial_revenue = {
          amount: parseFloat(revenueAmount),
          currency: 'EUR',
          notes: revenueNotes || null
        }
      }
      
      await createLicense(data)
      toast.success('Lizenz erfolgreich erstellt!')
      onClose()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Erstellen der Lizenz')
    }
  }
  
  // Calculate days from today for limited licenses
  const getDaysFromNow = () => {
    if (!formData.expires_at) return null
    const today = new Date()
    const expiry = new Date(formData.expires_at)
    const diffTime = expiry - today
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays > 0 ? diffDays : 0
  }
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700 sticky top-0 bg-white dark:bg-gray-800">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Neue Lizenz erstellen
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Product Selection */}
          {products.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                <Package className="w-4 h-4 inline mr-1" />
                Produkt
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
          )}
          
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Bezeichnung
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="input"
              placeholder="z.B. Kunde ABC - Pro Version"
            />
            <p className="mt-1 text-xs text-gray-500">
              Optional - hilft bei der Identifizierung
            </p>
          </div>
          
          {/* License Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Lizenztyp
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'unlimited', label: 'Unbegrenzt', desc: 'Läuft nie ab' },
                { value: 'limited', label: 'Zeitlich', desc: 'Festes Enddatum' },
                { value: 'trial', label: 'Testversion', desc: 'X Tage ab Aktivierung' },
              ].map(type => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => {
                    const timeLimited = ['limited', 'standard', 'professional', 'enterprise']
                    setFormData({ 
                      ...formData, 
                      license_type: type.value,
                      // Setze Standard-Ablaufdatum wenn zu zeitlich begrenzt gewechselt wird
                      expires_at: timeLimited.includes(type.value) && !formData.expires_at
                        ? getDefaultExpiryDate()
                        : formData.expires_at
                    })
                  }}
                  className={`p-3 rounded-lg border-2 transition-all text-left ${
                    formData.license_type === type.value
                      ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                      : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'
                  }`}
                >
                  <p className={`font-medium text-sm ${
                    formData.license_type === type.value 
                      ? 'text-primary-700 dark:text-primary-300' 
                      : 'text-gray-900 dark:text-white'
                  }`}>
                    {type.label}
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">{type.desc}</p>
                </button>
              ))}
            </div>
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
              <p className="mt-1 text-xs text-gray-500">
                Die Lizenz läuft X Tage nach der ersten Aktivierung ab
              </p>
            </div>
          )}
          
          {/* Expires At */}
          {['limited', 'standard', 'professional', 'enterprise'].includes(formData.license_type) && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Ablaufdatum
              </label>
              <input
                type="date"
                value={formData.expires_at}
                onChange={(e) => setFormData({ ...formData, expires_at: e.target.value })}
                className="input"
                required
                min={new Date().toISOString().split('T')[0]}
              />
              {getDaysFromNow() !== null && (
                <p className="mt-1 text-xs text-gray-500">
                  Gültig für {getDaysFromNow()} Tage ab heute
                </p>
              )}
            </div>
          )}
          
          {/* Max Devices */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Maximale Geräte
            </label>
            <div className="flex items-center space-x-3">
              <input
                type="number"
                min="0"
                max="1000"
                value={formData.max_devices}
                onChange={(e) => setFormData({ ...formData, max_devices: e.target.value })}
                className="input w-24"
              />
              <span className="text-sm text-gray-500">
                {parseInt(formData.max_devices) === 0 ? '= Unbegrenzte Geräte' : `Gerät${parseInt(formData.max_devices) !== 1 ? 'e' : ''}`}
              </span>
            </div>
          </div>
          
          {/* Features Selection */}
          {selectedProduct && selectedProduct.available_features && selectedProduct.available_features.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Features für diese Lizenz
              </label>
              <div className="grid grid-cols-2 gap-2">
                {selectedProduct.available_features.map((feature) => (
                  <button
                    key={feature}
                    type="button"
                    onClick={() => toggleFeature(feature)}
                    className={`flex items-center gap-2 p-2 rounded-md border text-sm text-left transition-colors ${
                      formData.features.includes(feature)
                        ? 'bg-primary-50 border-primary-300 text-primary-700 dark:bg-primary-900/30 dark:border-primary-600 dark:text-primary-300'
                        : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50 dark:bg-gray-700 dark:border-gray-600 dark:text-gray-300'
                    }`}
                  >
                    <div className={`w-4 h-4 rounded flex items-center justify-center flex-shrink-0 ${
                      formData.features.includes(feature)
                        ? 'bg-primary-500 text-white'
                        : 'border border-gray-300 dark:border-gray-500'
                    }`}>
                      {formData.features.includes(feature) && (
                        <Check size={12} />
                      )}
                    </div>
                    <span className="truncate">{feature}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
          
          {/* Revenue Tracking (Admin only) */}
          {user?.is_admin && (
            <div className="border-t border-gray-200 dark:border-gray-700 pt-5">
              <div className="flex items-center justify-between mb-3">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={trackRevenue}
                    onChange={(e) => setTrackRevenue(e.target.checked)}
                    className="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Einnahmen erfassen
                  </span>
                </label>
                <span className="text-xs text-gray-400 flex items-center">
                  <Info className="w-3 h-3 mr-1" />
                  Optional
                </span>
              </div>
              
              {trackRevenue && (
                <div className="space-y-3 pl-6 border-l-2 border-primary-200 dark:border-primary-800">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Betrag
                    </label>
                    <div className="relative">
                      <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                      <input
                        type="number"
                        value={revenueAmount}
                        onChange={(e) => setRevenueAmount(e.target.value)}
                        placeholder="0.00"
                        step="0.01"
                        min="0"
                        className="input pl-10"
                        required={trackRevenue}
                      />
                      <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-sm text-gray-400">
                        EUR
                      </span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Notizen
                    </label>
                    <textarea
                      value={revenueNotes}
                      onChange={(e) => setRevenueNotes(e.target.value)}
                      placeholder="z.B. Rechnung #12345, PayPal..."
                      rows={2}
                      className="input resize-none"
                    />
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Buttons */}
          <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
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
              {isLoading ? 'Wird erstellt...' : 'Lizenz erstellen'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
