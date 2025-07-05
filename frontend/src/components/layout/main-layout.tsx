import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Header } from './header'
import { Sidebar } from './sidebar'
import { cn } from '../../lib/utils'

interface MainLayoutProps {
  children: React.ReactNode
}

export function MainLayout({ children }: MainLayoutProps) {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <AnimatePresence>
        {isSidebarOpen && (
          <Sidebar isOpen={isSidebarOpen} onToggle={toggleSidebar} />
        )}
      </AnimatePresence>

      {/* Main content area */}
      <motion.div
        initial={{ marginLeft: 0 }}
        animate={{ marginLeft: isSidebarOpen ? 256 : 0 }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className="min-h-screen"
      >
        {/* Header */}
        <Header onMenuToggle={toggleSidebar} isSidebarOpen={isSidebarOpen} />

        {/* Page content */}
        <motion.main
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className={cn(
            'p-4 sm:p-6 lg:p-8',
            'transition-all duration-300 ease-in-out'
          )}
        >
          {children}
        </motion.main>
      </motion.div>

      {/* Overlay for mobile */}
      <AnimatePresence>
        {isSidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={toggleSidebar}
            className="fixed inset-0 z-30 bg-black bg-opacity-50 lg:hidden"
          />
        )}
      </AnimatePresence>
    </div>
  )
} 