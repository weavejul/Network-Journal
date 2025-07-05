import { motion } from 'framer-motion'
import { cn } from '../../lib/utils'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
}

const navigationItems = [
  { name: 'Dashboard', href: '/', icon: '🏠' },
  { name: 'People', href: '/people', icon: '👥' },
  { name: 'Companies', href: '/companies', icon: '🏢' },
  { name: 'Topics', href: '/topics', icon: '🏷️' },
  { name: 'Events', href: '/events', icon: '📅' },
  { name: 'Locations', href: '/locations', icon: '📍' },
  { name: 'Interactions', href: '/interactions', icon: '💬' },
]

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  return (
    <motion.div
      initial={{ x: -300 }}
      animate={{ x: isOpen ? 0 : -300 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
      className={cn(
        'fixed left-0 top-0 z-40 h-screen w-64 bg-white shadow-lg border-r border-gray-200',
        'transform transition-transform duration-300 ease-in-out'
      )}
    >
      <div className="flex h-full flex-col">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="flex h-16 items-center justify-between border-b border-gray-200 px-6"
        >
          <h1 className="text-xl font-bold text-gray-900">Network Journal</h1>
          <button
            onClick={onToggle}
            className="rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </motion.div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-4 py-6">
          {navigationItems.map((item, index) => (
            <motion.a
              key={item.name}
              href={item.href}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 + index * 0.05 }}
              whileHover={{ x: 4 }}
              className={cn(
                'group flex items-center rounded-md px-3 py-2 text-sm font-medium text-gray-700',
                'hover:bg-blue-50 hover:text-blue-700 transition-colors duration-200'
              )}
            >
              <span className="mr-3 text-lg">{item.icon}</span>
              {item.name}
            </motion.a>
          ))}
        </nav>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="border-t border-gray-200 p-4"
        >
          <div className="text-xs text-gray-500">
            Network Journal v1.0
          </div>
        </motion.div>
      </div>
    </motion.div>
  )
} 