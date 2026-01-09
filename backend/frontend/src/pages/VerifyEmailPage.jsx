import { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { authApi } from '../services/api'
import { CheckCircle, XCircle, Loader } from 'lucide-react'

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState('loading') // loading, success, error
  const [message, setMessage] = useState('')
  
  useEffect(() => {
    const verifyEmail = async () => {
      const token = searchParams.get('token')
      
      if (!token) {
        setStatus('error')
        setMessage('Ungültiger Bestätigungslink. Kein Token vorhanden.')
        return
      }
      
      try {
        const response = await authApi.verifyEmail(token)
        setStatus('success')
        setMessage(response.data.message || 'E-Mail erfolgreich bestätigt!')
      } catch (err) {
        setStatus('error')
        setMessage(err.response?.data?.detail || 'Bestätigung fehlgeschlagen. Der Link ist möglicherweise abgelaufen.')
      }
    }
    
    verifyEmail()
  }, [searchParams])
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4">
      <div className="max-w-md w-full text-center">
        {status === 'loading' && (
          <>
            <div className="mx-auto w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
              <Loader className="w-8 h-8 text-primary-600 dark:text-primary-400 animate-spin" />
            </div>
            <h2 className="mt-6 text-2xl font-bold text-gray-900 dark:text-white">
              E-Mail wird bestätigt...
            </h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              Bitte warte, während wir deine E-Mail-Adresse bestätigen.
            </p>
          </>
        )}
        
        {status === 'success' && (
          <>
            <div className="mx-auto w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
              <CheckCircle className="w-8 h-8 text-green-600 dark:text-green-400" />
            </div>
            <h2 className="mt-6 text-2xl font-bold text-gray-900 dark:text-white">
              E-Mail bestätigt!
            </h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              {message}
            </p>
            <Link
              to="/login"
              className="mt-6 inline-block btn-primary"
            >
              Zur Anmeldung
            </Link>
          </>
        )}
        
        {status === 'error' && (
          <>
            <div className="mx-auto w-16 h-16 bg-red-100 dark:bg-red-900 rounded-full flex items-center justify-center">
              <XCircle className="w-8 h-8 text-red-600 dark:text-red-400" />
            </div>
            <h2 className="mt-6 text-2xl font-bold text-gray-900 dark:text-white">
              Bestätigung fehlgeschlagen
            </h2>
            <p className="mt-2 text-gray-600 dark:text-gray-400">
              {message}
            </p>
            <div className="mt-6 space-x-4">
              <Link
                to="/login"
                className="inline-block btn-secondary"
              >
                Anmelden
              </Link>
              <Link
                to="/register"
                className="inline-block btn-primary"
              >
                Erneut registrieren
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
