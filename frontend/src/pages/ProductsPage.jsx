import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Package, Check, X, Tag, Settings, Monitor } from 'lucide-react';
import api from '../utils/api';

const AVAILABLE_FEATURES = [
  { id: 'basic', name: 'Basis-Funktionen', description: 'Grundlegende Funktionen' },
  { id: 'export', name: 'Export', description: 'Datenexport-Funktionen' },
  { id: 'api_access', name: 'API-Zugang', description: 'Zugriff auf die API' },
  { id: 'premium', name: 'Premium', description: 'Premium-Funktionen' },
  { id: 'analytics', name: 'Analytics', description: 'Erweiterte Analysen' },
  { id: 'support', name: 'Priority Support', description: 'Prioritäts-Support' },
  { id: 'multi_user', name: 'Multi-User', description: 'Mehrere Benutzer' },
  { id: 'cloud_sync', name: 'Cloud-Sync', description: 'Cloud-Synchronisation' },
  { id: 'custom_branding', name: 'Custom Branding', description: 'Eigenes Branding' },
  { id: 'unlimited_storage', name: 'Unbegrenzter Speicher', description: 'Kein Speicherlimit' },
];

function ProductModal({ isOpen, onClose, product = null, onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    description: '',
    version: '1.0.0',
    available_features: [],
    default_max_devices: 1,
    default_license_type: 'standard',
    is_active: true
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name,
        slug: product.slug,
        description: product.description || '',
        version: product.version || '1.0.0',
        available_features: product.available_features || [],
        default_max_devices: product.default_max_devices || 1,
        default_license_type: product.default_license_type || 'standard',
        is_active: product.is_active
      });
    } else {
      setFormData({
        name: '',
        slug: '',
        description: '',
        version: '1.0.0',
        available_features: [],
        default_max_devices: 1,
        default_license_type: 'standard',
        is_active: true
      });
    }
    setError(null);
  }, [product, isOpen]);

  const generateSlug = (name) => {
    return name
      .toLowerCase()
      .replace(/[äöü]/g, (match) => ({ 'ä': 'ae', 'ö': 'oe', 'ü': 'ue' }[match]))
      .replace(/ß/g, 'ss')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  };

  const handleNameChange = (e) => {
    const name = e.target.value;
    setFormData(prev => ({
      ...prev,
      name,
      slug: !product ? generateSlug(name) : prev.slug
    }));
  };

  const toggleFeature = (featureId) => {
    setFormData(prev => ({
      ...prev,
      available_features: prev.available_features.includes(featureId)
        ? prev.available_features.filter(f => f !== featureId)
        : [...prev.available_features, featureId]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!formData.name.trim()) {
      setError('Name ist erforderlich');
      return;
    }

    if (!formData.slug.trim()) {
      setError('Slug ist erforderlich');
      return;
    }

    setLoading(true);
    try {
      if (product) {
        await api.put(`/products/${product.id}`, formData);
      } else {
        await api.post('/products', formData);
      }
      onSuccess();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Ein Fehler ist aufgetreten');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">
              {product ? 'Produkt bearbeiten' : 'Neues Produkt erstellen'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <X size={24} />
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Produktname *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={handleNameChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Meine Software"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Slug (URL-freundlich) *
                </label>
                <input
                  type="text"
                  value={formData.slug}
                  onChange={(e) => setFormData(prev => ({ ...prev, slug: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="meine-software"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Beschreibung
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                rows={2}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="Beschreibung des Produkts..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Version
                </label>
                <input
                  type="text"
                  value={formData.version}
                  onChange={(e) => setFormData(prev => ({ ...prev, version: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="1.0.0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Standard Max. Geräte
                </label>
                <input
                  type="number"
                  min="1"
                  value={formData.default_max_devices}
                  onChange={(e) => setFormData(prev => ({ ...prev, default_max_devices: parseInt(e.target.value) || 1 }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Standard Lizenztyp
                </label>
                <select
                  value={formData.default_license_type}
                  onChange={(e) => setFormData(prev => ({ ...prev, default_license_type: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="trial">Testversion</option>
                  <option value="standard">Standard</option>
                  <option value="professional">Professional</option>
                  <option value="enterprise">Enterprise</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Verfügbare Features
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {AVAILABLE_FEATURES.map((feature) => (
                  <button
                    key={feature.id}
                    type="button"
                    onClick={() => toggleFeature(feature.id)}
                    className={`flex items-center gap-2 p-2 rounded-md border text-sm text-left transition-colors ${
                      formData.available_features.includes(feature.id)
                        ? 'bg-primary-50 border-primary-300 text-primary-700'
                        : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <div className={`w-4 h-4 rounded flex items-center justify-center flex-shrink-0 ${
                      formData.available_features.includes(feature.id)
                        ? 'bg-primary-500 text-white'
                        : 'border border-gray-300'
                    }`}>
                      {formData.available_features.includes(feature.id) && (
                        <Check size={12} />
                      )}
                    </div>
                    <span className="truncate">{feature.name}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData(prev => ({ ...prev, is_active: e.target.checked }))}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <label htmlFor="is_active" className="text-sm text-gray-700">
                Produkt ist aktiv
              </label>
            </div>

            <div className="flex gap-3 pt-4 border-t">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Abbrechen
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
              >
                {loading ? 'Speichern...' : (product ? 'Aktualisieren' : 'Erstellen')}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

function DeleteConfirmModal({ isOpen, onClose, onConfirm, productName, loading }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Produkt löschen?
        </h3>
        <p className="text-gray-600 mb-6">
          Möchten Sie das Produkt <strong>"{productName}"</strong> wirklich löschen?
          Diese Aktion kann nicht rückgängig gemacht werden.
        </p>
        <p className="text-sm text-amber-600 bg-amber-50 p-3 rounded-md mb-4">
          Hinweis: Produkte mit zugewiesenen Lizenzen können nicht gelöscht werden.
        </p>
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Abbrechen
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
          >
            {loading ? 'Löschen...' : 'Löschen'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [deletingProduct, setDeletingProduct] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products');
      setProducts(response.data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Fehler beim Laden der Produkte');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleDelete = async () => {
    if (!deletingProduct) return;
    setDeleteLoading(true);
    try {
      await api.delete(`/products/${deletingProduct.id}`);
      setProducts(products.filter(p => p.id !== deletingProduct.id));
      setDeletingProduct(null);
    } catch (err) {
      setError(err.response?.data?.detail || 'Fehler beim Löschen');
    } finally {
      setDeleteLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Produkte</h1>
          <p className="text-gray-600 mt-1">Verwalten Sie Ihre Software-Produkte und deren Features</p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
        >
          <Plus size={20} />
          Neues Produkt
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-100 text-red-700 rounded-md flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="text-red-500 hover:text-red-700">
            <X size={20} />
          </button>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Package className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">Keine Produkte</h3>
          <p className="mt-2 text-gray-600">
            Erstellen Sie Ihr erstes Software-Produkt, um Lizenzen zuzuordnen.
          </p>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="mt-4 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
          >
            Produkt erstellen
          </button>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {products.map((product) => (
            <div
              key={product.id}
              className={`bg-white rounded-lg border shadow-sm overflow-hidden ${
                product.is_active ? 'border-gray-200' : 'border-gray-300 opacity-60'
              }`}
            >
              <div className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg ${
                      product.is_active ? 'bg-primary-100' : 'bg-gray-100'
                    }`}>
                      <Package className={
                        product.is_active ? 'text-primary-600' : 'text-gray-400'
                      } size={24} />
                    </div>
                    <div>
                      <h3 className="font-semibold text-gray-900">{product.name}</h3>
                      <p className="text-sm text-gray-500">{product.slug}</p>
                    </div>
                  </div>
                  {!product.is_active && (
                    <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                      Inaktiv
                    </span>
                  )}
                </div>

                {product.description && (
                  <p className="mt-3 text-sm text-gray-600 line-clamp-2">
                    {product.description}
                  </p>
                )}

                <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center gap-1">
                    <Tag size={14} />
                    <span>v{product.version || '1.0.0'}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Settings size={14} />
                    <span>{product.available_features?.length || 0} Features</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Monitor size={14} />
                    <span>{product.default_max_devices} Geräte</span>
                  </div>
                </div>

                {product.available_features && product.available_features.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1">
                    {product.available_features.slice(0, 4).map((feature) => (
                      <span
                        key={feature}
                        className="px-2 py-0.5 text-xs bg-primary-50 text-primary-700 rounded"
                      >
                        {feature}
                      </span>
                    ))}
                    {product.available_features.length > 4 && (
                      <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                        +{product.available_features.length - 4}
                      </span>
                    )}
                  </div>
                )}

                <div className="mt-4 pt-4 border-t flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    Standard: {product.default_license_type}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setEditingProduct(product)}
                      className="p-1.5 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded"
                      title="Bearbeiten"
                    >
                      <Edit2 size={16} />
                    </button>
                    <button
                      onClick={() => setDeletingProduct(product)}
                      className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                      title="Löschen"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <ProductModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={fetchProducts}
      />

      <ProductModal
        isOpen={!!editingProduct}
        onClose={() => setEditingProduct(null)}
        product={editingProduct}
        onSuccess={fetchProducts}
      />

      <DeleteConfirmModal
        isOpen={!!deletingProduct}
        onClose={() => setDeletingProduct(null)}
        onConfirm={handleDelete}
        productName={deletingProduct?.name}
        loading={deleteLoading}
      />
    </div>
  );
}
