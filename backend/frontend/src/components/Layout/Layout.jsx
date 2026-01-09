import { Outlet } from 'react-router-dom'
import Navbar from './Navbar'
import Sidebar from './Sidebar'

export default function Layout() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 overflow-x-hidden">
      <Navbar />
      <div className="flex pt-16">
        <Sidebar />
        <main className="flex-1 p-6 ml-64 min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
