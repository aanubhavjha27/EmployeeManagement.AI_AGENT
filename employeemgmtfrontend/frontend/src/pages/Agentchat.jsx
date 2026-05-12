import axios from 'axios'
import { ArrowRight, X } from 'lucide-react'
import React, { useState } from 'react'
import toast from 'react-hot-toast'
import { motion } from 'framer-motion'

const Agentchat = ({
  setshowbot,
  setsearchterm,
  setshowaddemployee,
  setemployees,
  setshowemployeedetail,
  setemployeeid
}) => {

  const [query, setquery] = useState('')
  const [response, setresponse] = useState('')
  const [loading, setloading] = useState(false)

  const handleenter = (e) => {
    if (e.key === 'Enter' && query.trim()) {
      submit()
    }
  }

  const submit = async () => {
    if (!query.trim()) return

    try {
      setloading(true)
      setresponse('')

      const res = await axios.post('http://localhost:8000/chat', {
        message: query
      })

      const data = res.data
      handleAction(data)

      setresponse(data.botmessage || data.message)
      setquery('')
    } catch (error) {
      toast.error('Failed to connect AI')
      setresponse('AI not reachable right now')
    } finally {
      setloading(false)
    }
  }

  const handleAction = async (data) => {
    switch (data.action) {

      case 'search':
      case 'filter_gender':
      case 'showall':
        if (data.employees?.length > 0) {
          setemployees(data.employees)
          setsearchterm('')
          toast.success(data.botmessage)
        } else {
          setemployees([])
          setsearchterm('')
          toast.error(data.botmessage)
        }
        break

      case 'add':
        if (data.success && data.employees?.length > 0) {
          const emp = data.employees[0]
          setemployees(prev => [emp, ...prev])
          toast.success(`Added ${emp.firstname}`)
        }
        break

      case 'delete':
        if (data.success && data.employeeid) {
          setemployees(prev => prev.filter(emp => emp.id !== data.employeeid))
          toast.success('Employee deleted')
        }
        break

      case 'update':
        if (data.success) {
          toast.success(data.botmessage)
          const res = await axios.get("http://localhost:8080/api/allemployees")
          setemployees(res.data)
        }
        break

      default:
        break
    }
  }

  return (
    <motion.div
      initial={{ y: '100%' }}
      animate={{ y: 0 }}
      exit={{ y: '100%' }}
      transition={{ duration: 0.3 }}
      className="fixed bottom-0 left-0 w-full z-50"
    >
      <div className="w-full max-w-3xl mx-auto bg-gradient-to-br from-slate-900 to-slate-800 text-white rounded-t-2xl shadow-2xl p-4">

        {/* Header */}
        <div className="flex items-center mb-3">
          <h2 className="font-semibold">AI Agent</h2>
          <X className="ml-auto cursor-pointer" onClick={() => setshowbot(false)} />
        </div>

        {/* Input */}
        <div className="flex items-center bg-white/10 border border-white/10 rounded-xl p-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setquery(e.target.value)}
            onKeyDown={handleenter}
            placeholder="Try: 'show all employees', 'delete john'"
            className="flex-1 bg-transparent outline-none text-sm"
          />

          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={submit}
            disabled={!query.trim()}
            className="ml-2 p-2 rounded-lg bg-indigo-500 hover:bg-indigo-600 disabled:opacity-40"
          >
            <ArrowRight size={18} />
          </motion.button>
        </div>

        {/* Response */}
        <div className="mt-4 bg-white/5 border border-white/10 rounded-xl p-3 min-h-[120px] text-sm">
          {loading ? 'Thinking...' : response || 'Ask something...'}
        </div>

      </div>
    </motion.div>
  )
}

export default Agentchat