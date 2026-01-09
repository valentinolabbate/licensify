import { useState, useEffect } from 'react'
import { 
  DollarSign, 
  TrendingUp, 
  Calendar,
  FileText,
  ChevronLeft,
  ChevronRight,
  Trash2
} from 'lucide-react'
import { revenueApi } from '../services/api'
import toast from 'react-hot-toast'

export default function Revenue() {
  const [revenues, setRevenues] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(0)
  const [total, setTotal] = useState(0)
  const [totalAmount, setTotalAmount] = useState(0)
  const limit = 20

  useEffect(() => {
    loadData()
  }, [page])

  const loadData = async () => {
    try {
      setLoading(true)
      const [revenueRes, summaryRes] = await Promise.all([
        revenueApi.list({ skip: page * limit, limit }),
        revenueApi.getSummary()
      ])
      setRevenues(revenueRes.data.revenues)
      setTotal(revenueRes.data.total)
      setTotalAmount(revenueRes.data.total_amount)
      setSummary(summaryRes.data)
    } catch (error) {
      toast.error('Fehler beim Laden der Einnahmen')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Einnahme wirklich löschen?')) return
    
    try {
      await revenueApi.delete(id)
      toast.success('Einnahme gelöscht')
      loadData()
    } catch (error) {
      toast.error('Fehler beim Löschen')
    }
  }

  const formatCurrency = (amount, currency = 'EUR') => {
    return new Intl.NumberFormat('de-DE', {
      style: 'currency',
      currency: currency
    }).format(amount)
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleDateString('de-DE', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const totalPages = Math.ceil(total / limit)

  if (loading && !summary) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          Einnahmen
        </h1>
        <p className="text-gray-500 dark:text-gray-400">
          Übersicht über alle Lizenzeinnahmen
        </p>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Gesamteinnahmen</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatCurrency(summary.total_revenue)}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-xl flex items-center justify-center">
                <DollarSign className="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Diesen Monat</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatCurrency(summary.revenue_this_month)}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-xl flex items-center justify-center">
                <Calendar className="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Dieses Jahr</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatCurrency(summary.revenue_this_year)}
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500 dark:text-gray-400">Durchschnitt</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatCurrency(summary.average_transaction)}
                </p>
              </div>
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900 rounded-xl flex items-center justify-center">
                <FileText className="w-6 h-6 text-orange-600 dark:text-orange-400" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Monthly Chart */}
      {summary && summary.monthly_breakdown && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Monatliche Einnahmen
          </h2>
          <div className="flex items-end space-x-2 h-48">
            {summary.monthly_breakdown.map((month, index) => {
              const maxAmount = Math.max(...summary.monthly_breakdown.map(m => m.amount), 1)
              const height = (month.amount / maxAmount) * 100
              return (
                <div key={index} className="flex-1 flex flex-col items-center">
                  <div 
                    className="w-full bg-primary-500 rounded-t transition-all duration-300 hover:bg-primary-600"
                    style={{ height: `${Math.max(height, 2)}%` }}
                    title={`${month.month}: ${formatCurrency(month.amount)}`}
                  ></div>
                  <span className="text-xs text-gray-500 mt-2 transform -rotate-45 origin-top-left">
                    {month.month.slice(5)}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Payment Type Breakdown */}
      {summary && Object.keys(summary.by_payment_type).length > 0 && (
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Nach Zahlungsart
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(summary.by_payment_type).map(([type, amount]) => (
              <div key={type} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <span className="capitalize text-gray-700 dark:text-gray-300">
                  {type === 'initial' ? 'Erstlizenz' : type === 'extension' ? 'Verlängerung' : type === 'upgrade' ? 'Upgrade' : type}
                </span>
                <span className="font-semibold text-gray-900 dark:text-white">
                  {formatCurrency(amount)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Transactions Table */}
      <div className="card">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Transaktionen ({total})
          </h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Datum
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Lizenz
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Benutzer
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Typ
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Betrag
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Notizen
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                  Aktionen
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {revenues.map((revenue) => (
                <tr key={revenue.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {formatDate(revenue.created_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <p className="text-sm font-medium text-gray-900 dark:text-white">
                        {revenue.license_name || 'Unbenannt'}
                      </p>
                      <p className="text-xs text-gray-500 font-mono">
                        {revenue.license_key?.slice(0, 8)}...
                      </p>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {revenue.user_email || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`badge ${
                      revenue.payment_type === 'initial' ? 'badge-info' :
                      revenue.payment_type === 'extension' ? 'badge-success' :
                      'badge-warning'
                    }`}>
                      {revenue.payment_type === 'initial' ? 'Erstlizenz' :
                       revenue.payment_type === 'extension' ? 'Verlängerung' :
                       revenue.payment_type === 'upgrade' ? 'Upgrade' : revenue.payment_type}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-green-600 dark:text-green-400">
                    {formatCurrency(revenue.amount, revenue.currency)}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">
                    {revenue.notes || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <button
                      onClick={() => handleDelete(revenue.id)}
                      className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                      title="Löschen"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
              {revenues.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                    Keine Einnahmen vorhanden
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
            <p className="text-sm text-gray-500">
              Seite {page + 1} von {totalPages}
            </p>
            <div className="flex space-x-2">
              <button
                onClick={() => setPage(p => Math.max(0, p - 1))}
                disabled={page === 0}
                className="p-2 rounded-lg border border-gray-300 dark:border-gray-600 disabled:opacity-50"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
                className="p-2 rounded-lg border border-gray-300 dark:border-gray-600 disabled:opacity-50"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
